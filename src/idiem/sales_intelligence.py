"""Sales Intelligence — capa complementaria de conocimiento comercial (v2).

Deriva de las PPT de venta por célula/segmento. Es una fuente **complementaria**
(autoridad 4 de 6, ver ``manifest.json`` y ``config/cell_rules.json``): enriquece la
ideación/redacción con dolores, necesidades, propuestas de valor, capacidades,
ángulos y casos, pero **jamás** clasifica un servicio ni redefine una célula.

Precedencia (de mayor a menor autoridad):
  1. reglas oficiales de células y clasificación
  2. reglas editoriales
  3. servicios/brochures validados
  4. Sales Intelligence  (esta capa)
  5. casos/evidencias
  6. fuentes externas

Diseño:
- La célula se resuelve SIEMPRE con las reglas oficiales (``cells.py`` /
  ``cell_rules.json``) ANTES de consultar esta capa. Por eso este módulo NO expone
  ninguna función de clasificación: ``for_cell`` recibe una célula oficial ya resuelta.
- Retrieval contextual y perezoso: solo se parsea la(s) ficha(s) de la célula pedida
  (Transporte → Metro/EFE; el resto una ficha), nunca las seis en cada generación.
- Estados de publicación por elemento (SAFE / VERIFY / INTERNAL / DO_NOT_PUBLISH),
  con semántica *fail closed*: un estado desconocido nunca es SAFE.
- Guardrails de seguridad editorial (CONTENT_RULES.md): términos de garantía causal,
  placeholders y frases DO_NOT_PUBLISH nunca llegan al copy final.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .loader import CONFIG_DIR, REPO_ROOT

# --- estados de publicación --------------------------------------------------
SAFE = "SAFE"
VERIFY = "VERIFY"
INTERNAL = "INTERNAL"
DO_NOT_PUBLISH = "DO_NOT_PUBLISH"

PUBLISH_STATES = (SAFE, VERIFY, INTERNAL, DO_NOT_PUBLISH)

# Restrictividad para publicar como hecho público (0 = más restrictivo).
# Un elemento compuesto (p.ej. "SAFE / VERIFY") toma el estado MÁS restrictivo:
# fail closed → nunca se convierte silenciosamente en hecho.
_RESTRICTIVENESS = {DO_NOT_PUBLISH: 0, VERIFY: 1, INTERNAL: 2, SAFE: 3}

# Patrón editorial recomendado por esta capa (no se fuerza si el formato pide otro).
SI_CONTENT_PATTERN = "problema/necesidad → impacto → capacidad IDIEM → evidencia/caso → CTA"

# Guardrails (CONTENT_RULES.md §4 y §7). Lenguaje de garantía causal a evitar salvo
# validación explícita. Se comparan con límites de palabra para no chocar con
# términos válidos (p.ej. "aseguramiento").
_CAUSAL_GUARANTEE_TERMS = (
    "garantiza", "garantizar", "garantizado", "garantizada",
    "elimina", "eliminar",
    "evita", "evitar",
    "asegura", "asegurar",
    "impide", "impedir",
)
_PLACEHOLDER_MARKERS = ("agregar una imagen", "xxxx", "xxxxxx")

_STATE_RE = re.compile(r"\b(SAFE|VERIFY|INTERNAL|DO_NOT_PUBLISH)\b")
_BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
# Secciones que son metadata/provenance, no material editorial:
_META_TITLES = {"source"}


_QUOTE_CHARS = "\"'“”„«»‘’‹›"


def _norm(text: str) -> str:
    """Casefold + strip accents + drop quote characters (fichas quote DO_NOT_PUBLISH
    phrases, so literal matching must ignore surrounding quotes)."""
    if not text:
        return ""
    d = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in d if not unicodedata.combining(c) and c not in _QUOTE_CHARS)
    return stripped.casefold()


def _squash(text: str) -> str:
    """Normalize + drop all punctuation to spaces + collapse — for robust phrase
    matching (fichas carry trailing periods/quotes on DO_NOT_PUBLISH items)."""
    return re.sub(r"\s+", " ", re.sub(r"[^0-9a-z]+", " ", _norm(text))).strip()


def _clean_item(line: str) -> str:
    """Strip bullet/number markers and markdown bold/emphasis from a list line."""
    line = _BULLET_RE.sub("", line.strip())
    line = line.replace("**", "").replace("`", "")
    return line.strip()


def _effective_state(states: tuple[str, ...]) -> str:
    """Fail-closed effective state: the most restrictive present; default INTERNAL."""
    if not states:
        return INTERNAL
    return min(states, key=lambda s: _RESTRICTIVENESS.get(s, 0))


@dataclass(frozen=True)
class SIElement:
    """One labeled section of a ficha (heading + its items + publish state)."""

    ficha_cell: str          # official cell name
    ficha_segment: str
    title: str               # heading text, state tokens removed
    states: tuple[str, ...]  # all state tokens found (or inherited)
    items: tuple[str, ...]

    @property
    def effective_state(self) -> str:
        return _effective_state(self.states)

    @property
    def publishable_without_validation(self) -> bool:
        return self.effective_state == SAFE

    @property
    def needs_validation(self) -> bool:
        return self.effective_state == VERIFY

    @property
    def is_internal(self) -> bool:
        return self.effective_state == INTERNAL

    @property
    def is_excluded(self) -> bool:
        return self.effective_state == DO_NOT_PUBLISH


@dataclass
class SIFicha:
    cell: str                # official cell name
    segment: str
    source_title: str        # PPT de origen
    drive_id: str
    path: Path
    elements: list[SIElement] = field(default_factory=list)

    def _by_state(self, predicate) -> list[SIElement]:
        return [e for e in self.elements if predicate(e)]

    def safe_elements(self) -> list[SIElement]:
        return self._by_state(lambda e: e.publishable_without_validation)

    def verify_elements(self) -> list[SIElement]:
        return self._by_state(lambda e: e.needs_validation)

    def excluded_elements(self) -> list[SIElement]:
        return self._by_state(lambda e: e.is_excluded)

    def items_where(self, *, title_contains: str, only_safe: bool = True) -> list[str]:
        key = _norm(title_contains)
        out: list[str] = []
        for e in self.elements:
            if only_safe and not e.publishable_without_validation:
                continue
            if key in _norm(e.title):
                out.extend(e.items)
        return out

    def trace(self) -> dict:
        return {
            "cell": self.cell,
            "segment": self.segment,
            "ficha": str(self.path.relative_to(REPO_ROOT)) if self.path.is_absolute() else str(self.path),
            "source_ppt": self.source_title,
            "drive_id": self.drive_id,
        }


@dataclass(frozen=True)
class SICase:
    case_id: str
    cell: str          # official cell name
    segment: Optional[str]
    client: str
    asset: Optional[str]
    themes: tuple[str, ...]
    publication_status: str

    @property
    def is_excluded(self) -> bool:
        return self.publication_status == DO_NOT_PUBLISH

    @property
    def needs_validation(self) -> bool:
        # Los casos son proof points potenciales: por defecto requieren validación
        # de difusión/alcance/vigencia (CONTENT_RULES §5) salvo que sean SAFE.
        return self.publication_status != SAFE and not self.is_excluded


@dataclass
class SIContext:
    """Material de ideación para UNA célula (opcionalmente un segmento)."""

    cell: str
    segment: Optional[str]
    fichas: list[SIFicha]
    cases: list[SICase]

    def _collect(self, title_contains: str) -> list[str]:
        out: list[str] = []
        for f in self.fichas:
            out.extend(f.items_where(title_contains=title_contains, only_safe=True))
        return out

    def safe_pain_points(self) -> list[str]:
        # "pain" o "dolor", y "necesidad"/"need" como necesidades de negocio afines.
        return self._collect("pain") + self._collect("dolor")

    def safe_business_needs(self) -> list[str]:
        return self._collect("need") + self._collect("necesidad")

    def safe_value_propositions(self) -> list[str]:
        return self._collect("value") + self._collect("propuesta")

    def safe_content_angles(self) -> list[str]:
        return self._collect("angle") + self._collect("ángulo") + self._collect("angulo")

    def verify_flags(self) -> list[dict]:
        """Elementos VERIFY (con su título y items) que exigen validación humana."""
        flags: list[dict] = []
        for f in self.fichas:
            for e in f.verify_elements():
                flags.append({
                    "cell": f.cell, "segment": f.segment,
                    "section": e.title, "items": list(e.items),
                    "source_ppt": f.source_title,
                })
        return flags

    def excluded_items(self) -> list[str]:
        out: list[str] = []
        for f in self.fichas:
            for e in f.excluded_elements():
                out.extend(e.items)
        return out

    def to_drafting_enrichment(self) -> dict:
        """Material listo para alimentar al redactor (solo SAFE como afirmable).

        VERIFY se entrega aparte, como pendientes de validación (no como hechos).
        DO_NOT_PUBLISH queda fuera. Incluye trazabilidad interna.
        """
        return {
            "content_pattern": SI_CONTENT_PATTERN,
            "pain_points": self.safe_pain_points(),
            "business_needs": self.safe_business_needs(),
            "value_propositions": self.safe_value_propositions(),
            "content_angles": self.safe_content_angles(),
            "verify_flags": self.verify_flags(),
            "cases": [
                {"case_id": c.case_id, "client": c.client, "asset": c.asset,
                 "themes": list(c.themes), "publication_status": c.publication_status,
                 "needs_validation": c.needs_validation}
                for c in self.cases if not c.is_excluded
            ],
            "trace": self.trace(),
        }

    def trace(self) -> dict:
        return {
            "cell": self.cell,
            "segment": self.segment,
            "fichas": [f.trace() for f in self.fichas],
            "verify_sections_used": [
                {"segment": fl["segment"], "section": fl["section"]}
                for fl in self.verify_flags()
            ],
        }


def _parse_ficha_markdown(text: str, *, cell: str, segment: str,
                          source_title: str, drive_id: str, path: Path) -> SIFicha:
    """Parse a ficha .md into labeled :class:`SIElement` sections.

    Headings (``##``/``###``) carry publish-state tokens; ``###`` inherit the parent
    ``##`` states when none of their own are present. List/paragraph lines become items.
    """
    elements: list[SIElement] = []
    parent_states: tuple[str, ...] = ()
    cur_title: Optional[str] = None
    cur_states: tuple[str, ...] = ()
    cur_items: list[str] = []

    def flush() -> None:
        nonlocal cur_title, cur_items, cur_states
        if cur_title is not None and _norm(cur_title) not in _META_TITLES:
            elements.append(SIElement(
                ficha_cell=cell, ficha_segment=segment,
                title=cur_title, states=cur_states, items=tuple(cur_items),
            ))
        cur_title, cur_items, cur_states = None, [], ()

    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("# "):
            continue  # document title
        m2 = line.startswith("## ")
        m3 = line.startswith("### ")
        if m2 or m3:
            flush()
            head = line[3:] if m2 else line[4:]
            found = tuple(_STATE_RE.findall(head))
            title = _STATE_RE.sub("", head)
            title = title.replace("—", " ").replace("/", " ").strip(" -–—:")
            title = re.sub(r"\s{2,}", " ", title).strip()
            if m2:
                parent_states = found
                cur_states = found
            else:
                cur_states = found or parent_states
            cur_title = title
            continue
        if cur_title is None:
            continue
        content = _clean_item(line)
        if content:
            cur_items.append(content)
    flush()
    return SIFicha(cell=cell, segment=segment, source_title=source_title,
                   drive_id=drive_id, path=path, elements=elements)


class SalesIntelligence:
    """Lazy, cell-scoped view over the Sales Intelligence package.

    No expone clasificación: recibe células oficiales ya resueltas.
    """

    def __init__(self, root: Path, cell_map: dict, manifest: dict,
                 cases_raw: list[dict]) -> None:
        self.root = root
        self.manifest = manifest
        self.cell_map = dict(cell_map)  # SI-internal cell -> official cell
        self.precedence = list(manifest.get("precedence", []))

        # index manifest sources by OFFICIAL cell (fail closed if unmapped)
        self._sources_by_cell: dict[str, list[dict]] = {}
        for src in manifest.get("sources", []):
            official = self.cell_map.get(src.get("cell"))
            if not official:
                continue
            self._sources_by_cell.setdefault(official, []).append(src)

        # cases by OFFICIAL cell
        self._cases_by_cell: dict[str, list[SICase]] = {}
        for c in cases_raw:
            official = self.cell_map.get(c.get("cell"))
            if not official:
                continue
            self._cases_by_cell.setdefault(official, []).append(SICase(
                case_id=c["case_id"], cell=official, segment=c.get("segment"),
                client=c.get("client", ""), asset=c.get("asset"),
                themes=tuple(c.get("themes", [])),
                publication_status=c.get("publication_status", VERIFY),
            ))

        self._parsed: dict[str, list[SIFicha]] = {}  # cache; also = "already parsed"

    # -- introspection ------------------------------------------------------
    def official_cells(self) -> list[str]:
        """Official cells that HAVE Sales Intelligence coverage."""
        return sorted(self._sources_by_cell.keys())

    def segments_for(self, cell: str) -> list[str]:
        return [s.get("segment", "") for s in self._sources_by_cell.get(cell, [])]

    @property
    def parsed_cells(self) -> set[str]:
        """Cells whose fichas have actually been parsed (retrieval scoping proof)."""
        return set(self._parsed.keys())

    # -- retrieval (cell already resolved by official rules) ----------------
    def for_cell(self, cell: str, segment: str | None = None) -> list[SIFicha]:
        """Parse+return ONLY the fichas of ``cell`` (optionally one ``segment``).

        Fail closed: a cell without coverage returns ``[]`` (never raises, never
        loads another cell's fichas). Parsing is lazy and cached per cell.
        """
        if cell not in self._sources_by_cell:
            return []  # fail closed: no coverage → nothing loaded, nothing cached
        if cell not in self._parsed:
            fichas: list[SIFicha] = []
            for src in self._sources_by_cell.get(cell, []):
                path = self.root / src["knowledge_file"]
                if not path.exists():
                    continue
                fichas.append(_parse_ficha_markdown(
                    path.read_text(encoding="utf-8"),
                    cell=cell, segment=src.get("segment", ""),
                    source_title=src.get("source_title", ""),
                    drive_id=src.get("drive_id", ""), path=path,
                ))
            self._parsed[cell] = fichas
        result = self._parsed[cell]
        if segment is not None:
            result = [f for f in result if f.segment == segment]
        return list(result)

    def cases_for(self, cell: str, segment: str | None = None) -> list[SICase]:
        cases = self._cases_by_cell.get(cell, [])
        if segment is not None:
            cases = [c for c in cases if c.segment == segment]
        return list(cases)

    def context_for(self, cell: str, segment: str | None = None) -> SIContext:
        return SIContext(
            cell=cell, segment=segment,
            fichas=self.for_cell(cell, segment),
            cases=self.cases_for(cell, segment),
        )

    # -- guardrails ---------------------------------------------------------
    def excluded_phrases(self) -> list[str]:
        """DO_NOT_PUBLISH literal items across ALL fichas (forces a full parse)."""
        phrases: list[str] = []
        for cell in self._sources_by_cell:
            for f in self.for_cell(cell):
                for e in f.excluded_elements():
                    phrases.extend(e.items)
        return phrases

    def forbidden_public_terms(self) -> list[str]:
        """Placeholder markers that must never reach final public copy."""
        return list(_PLACEHOLDER_MARKERS)

    def causal_guarantee_warnings(self, text: str) -> list[str]:
        """ADVISORY (no bloquea): verbos de garantía causal presentes en el texto
        (CONTENT_RULES §4). El verbo por sí solo no es prohibido —"evita sobrecostos"
        es legítimo—; se reportan para que un humano suavice sobre-promesas. La
        aprobación humana (regla 10) es el filtro final, no un keyword duro."""
        low = _norm(text)
        return [t for t in _CAUSAL_GUARANTEE_TERMS
                if re.search(r"\b" + re.escape(_norm(t)) + r"\b", low)]

    def assert_publishable(self, text: str, *, check_excluded: bool = True) -> None:
        """Fail closed SOLO ante lo que nunca debe publicarse sin ambigüedad: un
        placeholder o una frase ``DO_NOT_PUBLISH`` de las fichas. Los verbos de
        garantía causal NO se bloquean aquí (ver ``causal_guarantee_warnings``): un
        bloqueo por palabra suelta produce falsos positivos sobre copy legítimo ya
        aprobado por humanos."""
        low = _norm(text)
        for ph in _PLACEHOLDER_MARKERS:
            if ph in low:
                raise ValueError(f"Sales Intelligence: placeholder en copy: {ph!r}")
        if check_excluded:
            squashed = _squash(text)
            for phrase in self.excluded_phrases():
                p = _squash(phrase)
                if len(p) >= 6 and p in squashed:
                    raise ValueError(f"Sales Intelligence: frase DO_NOT_PUBLISH en copy: {phrase!r}")


def _load_cell_map() -> tuple[dict, Path]:
    with (CONFIG_DIR / "cell_rules.json").open("r", encoding="utf-8") as fh:
        cfg = json.load(fh)
    si = cfg.get("sales_intelligence", {})
    root = REPO_ROOT / si.get("root", "knowledge/sales_intelligence")
    return si.get("cell_map", {}), root


def load_sales_intelligence(root: Path | None = None) -> SalesIntelligence:
    """Load the Sales Intelligence layer (manifest + cases). Fichas parse lazily."""
    cell_map, cfg_root = _load_cell_map()
    root = Path(root) if root else cfg_root
    with (root / "manifest.json").open("r", encoding="utf-8") as fh:
        manifest = json.load(fh)
    cases_path = root / "cases" / "cases.json"
    cases_raw = json.loads(cases_path.read_text(encoding="utf-8")) if cases_path.exists() else []
    return SalesIntelligence(root=root, cell_map=cell_map, manifest=manifest, cases_raw=cases_raw)


def _demo(cell: str, segment: str | None = None) -> None:  # pragma: no cover
    si = load_sales_intelligence()
    ctx = si.context_for(cell, segment)
    print(json.dumps(ctx.to_drafting_enrichment(), ensure_ascii=False, indent=2))


if __name__ == "__main__":  # pragma: no cover
    import argparse

    ap = argparse.ArgumentParser(description="Demo: contexto Sales Intelligence por célula.")
    ap.add_argument("--cell", required=True, help="Nombre oficial de la célula.")
    ap.add_argument("--segment", default=None, help="Segmento opcional (metro/efe/...).")
    args = ap.parse_args()
    _demo(args.cell, args.segment)
