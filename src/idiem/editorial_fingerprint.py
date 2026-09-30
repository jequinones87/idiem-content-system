"""Editorial fingerprint — huella editorial estructurada de una pieza.

La diversidad NO puede medirse sólo por ``knowledge_id`` / célula / servicio /
subtema: dos piezas con distinto ``knowledge_id`` pueden ser editorialmente casi
idénticas (mismo pain, mismo hook, mismo arquetipo, mismo CTA). Este módulo
resume cada pieza en una huella con dimensiones normalizadas (enums), determinista
y auditable, que alimenta archivado, novelty, QA y reporting.

DESCRIBE lo que la pieza ES; NO autoriza contenido. La gobernanza factual
(allowed_facts, CONTENT_GAP, claims bloqueados, trazabilidad) sigue mandando: p.ej.
que una pieza se clasifique como ``case_or_experience`` no autoriza inventar un
caso — esa restricción la aplican el planner/drafting/QA factual, no esta huella.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field, asdict
from typing import Optional

# --- taxonomías normalizadas (enums) -----------------------------------------
HOOK_TYPES = (
    "risk", "question", "insight", "statistic", "misconception",
    "explanation", "consequence", "opportunity", "checklist", "case",
)
CTA_TYPES = (
    "contact", "learn_more", "self_assessment", "question",
    "conversation", "visit_service", "save_reference", "no_cta",
)
ARCHETYPES = (
    "problem_solution", "technical_insight", "explainer", "case_or_experience",
    "method_or_evidence", "sector_question", "checklist", "institutional_or_occasion",
)
VISUAL_THEMES = (
    "people", "laboratory", "field", "infrastructure",
    "equipment", "detail", "aerial", "graphic",
)
PAIN_CATEGORIES = (
    "risk_of_failure", "delays", "cost_overrun", "compliance_gap",
    "reliability", "safety", "quality_assurance", "decision_uncertainty",
    "continuity", "sustainability", "other",
)

_EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF←-⇿⬀-⯿️]"
)
_HASHTAG_RE = re.compile(r"#\w+")
_TAG_RE = re.compile(r"<[^>]+>")
_WORD_RE = re.compile(r"[0-9a-záéíóúñü]+", re.IGNORECASE)
_STOPWORDS = frozenset("""
a al algo ante antes bajo cada como con contra de del desde donde dos el en entre era eres es esa ese eso esta este esto ha hasta hay la las le les lo los mas más me mi mis muy no nos o os para pero poco por porque que qué se sea segun según ser si sí sin so sobre su sus te tu tus un una uno unos unas y ya
tu tus nuestro nuestra nuestros nuestras idiem
""".split())


def _strip_accents(s: str) -> str:
    d = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in d if not unicodedata.combining(c))


def clean_text(s: str) -> str:
    """Lowercased text without emojis, hashtags, HTML tags or accents."""
    s = _TAG_RE.sub(" ", s or "")
    s = _EMOJI_RE.sub(" ", s)
    s = _HASHTAG_RE.sub(" ", s)
    return _strip_accents(s).casefold()


def tokens(s: str, *, drop_stop: bool = True) -> set[str]:
    """Content-token set for similarity (accent-insensitive, stopwords out)."""
    out = {m.group(0) for m in _WORD_RE.finditer(clean_text(s))}
    if drop_stop:
        out = {t for t in out if t not in _STOPWORDS and len(t) > 2}
    return out


def _has(text: str, *needles: str) -> bool:
    t = clean_text(text)
    return any(_strip_accents(n).casefold() in t for n in needles)


def _first_sentence(s: str, limit: int = 160) -> str:
    body = re.split(r"(?<=[.!?…])\s", (s or "").strip(), maxsplit=1)[0]
    return body[:limit].strip()


# --- clasificadores deterministas --------------------------------------------
def classify_hook_type(hook: str) -> str:
    t = clean_text(hook)
    if not t.strip():
        return "explanation"
    is_question = "?" in (hook or "")
    if _has(hook, "checklist", "3 claves", "pasos para", "que revisar", "clave para", "puntos clave"):
        return "checklist"
    if _has(hook, "no siempre", "no basta con", "no solo", "muchas veces el problema", "el problema no esta", "mito"):
        return "misconception"
    if re.search(r"\b\d{2,}\b|\d+\s?%|millones|mil ", t):
        return "statistic"
    if _has(hook, "falla", "riesgo", "colaps", "detener", "detencion", "peligro", "grieta", "fisura", "no detectad", "incidente", "corrosion"):
        return "risk"
    if _has(hook, "puede postergar", "puede comprometer", "impacto", "sobrecosto", "atraso", "consecuencia", "termina en", "deriva en"):
        return "consequence"
    if _has(hook, "oportunidad", "innovar", "mejorar", "optimizar", "potenciar", "avanzar"):
        return "opportunity"
    if _has(hook, "caso", "proyecto", "experiencia", "cuando trabajamos", "en el proyecto"):
        return "case"
    if is_question:
        return "question"
    if _has(hook, "que es", "como funciona", "en que consiste", "sabias que", "consiste en"):
        return "explanation"
    return "insight"


def classify_cta_type(cta: str) -> str:
    t = clean_text(cta)
    if not t.strip():
        return "no_cta"
    has_link = "idiem.cl" in t or "http" in t
    is_question = "?" in (cta or "")
    if _has(cta, "guarda", "guardalo", "guardala", "referencia para", "ten a mano"):
        return "save_reference"
    if _has(cta, "evalua", "autoevalua", "revisa si", "revisa tu", "chequea", "esta tu obra", "esta tu proyecto"):
        return "self_assessment"
    if is_question and not _has(cta, "conversemos", "contactanos", "contacto"):
        return "question"
    if _has(cta, "contactanos", "contacto", "escribenos", "cotiza", "solicita"):
        return "contact"
    if _has(cta, "conversemos", "hablemos"):
        return "conversation"
    if _has(cta, "conoce nuestros servicios", "conoce el servicio", "conoce este servicio", "alcance de este servicio", "conoce el alcance", "visita"):
        return "visit_service"
    if _has(cta, "conoce mas", "descubre", "mas informacion", "lee ", "revisa como", "conoce como"):
        return "learn_more"
    if is_question:
        return "question"
    return "contact" if has_link else "no_cta"


def classify_pain_category(hook: str, body: str = "") -> str:
    text = f"{hook}\n{body}"
    if _has(text, "atraso", "plazo", "retraso", "programacion", "cronograma"):
        return "delays"
    if _has(text, "sobrecosto", "costo", "economic", "presupuesto"):
        return "cost_overrun"
    if _has(text, "falla", "colaps", "grieta", "fisura", "corrosion", "rotura", "deterioro"):
        return "risk_of_failure"
    if _has(text, "norma", "cumplimiento", "normativ", "brecha", "regulacion", "fiscaliz"):
        return "compliance_gap"
    if _has(text, "continuidad", "detencion", "operacion", "disponibilidad"):
        return "continuity"
    if _has(text, "confiabilidad", "vida util", "vida remanente", "integridad"):
        return "reliability"
    if _has(text, "seguridad", "riesgo para las personas", "incendio", "proteccion"):
        return "safety"
    if _has(text, "calidad", "ensayo", "control", "certific", "trazabilidad"):
        return "quality_assurance"
    if _has(text, "decidir", "decision", "evidencia para", "priorizar"):
        return "decision_uncertainty"
    if _has(text, "sustentab", "huella", "energ", "carbono", "ambient"):
        return "sustainability"
    return "other"


def classify_archetype(rec: "PostRecord") -> str:
    if not rec.knowledge_id and not rec.evidence_ids:
        return "institutional_or_occasion"
    if _has(rec.editorial_angle or "", "saludo", "efemeride", "dia del", "dia mundial", "institucional"):
        return "institutional_or_occasion"
    fmt = (rec.format or "").upper()
    hook = rec.hook
    body = rec.body
    if "?" in (hook or "") and _has(hook, "sector", "industria", "mineria", "obras", "hospital", "sabias"):
        return "sector_question"
    if fmt in {"CARRUSEL", "CAROUSEL"} and _has(body, "etapa", "paso", "1.", "2.", "3.", "checklist"):
        return "checklist"
    if _has(hook, "checklist", "pasos", "3 claves", "que revisar"):
        return "checklist"
    if _has(body, "caso", "proyecto ", "cliente", "experiencia en", "aplicado en el proyecto") and rec.evidence_ids:
        return "case_or_experience"
    if _has(body, "ensayo", "evidencia", "metodolog", "trazabilidad", "control de calidad", "certificacion"):
        return "method_or_evidence"
    if _has(hook, "que es", "como funciona", "en que consiste", "consiste en", "sabias que"):
        return "explainer"
    if _has(body, "norma", "metodo", "disciplina", "modelacion", "elementos finitos", "monitoreo") and "?" not in (hook or ""):
        return "technical_insight"
    return "problem_solution"


_VISUAL_KEYWORDS = (
    ("laboratory", ("laborator", "ensayo", "planta_acero", "triaxial", "muestra", "probeta")),
    ("equipment", ("equipo_tri", "equipo_", "maquina", "grua", "instrumento", "sensor", "escaner", "dron", "lidar")),
    ("graphic", ("bim", "modelad", "render", "grafic", "esquema", "3d", "diagrama")),
    ("aerial", ("aerea", "aerial", "drone", "vista_aerea", "cenital")),
    ("people", ("trabajador", "profesional", "persona", "geologo", "equipo_humano", "ingeniero", "operario")),
    ("infrastructure", ("estructura", "vigas", "acero", "hormigon", "puente", "edificio", "domo", "tunel", "andamio", "obra")),
    ("field", ("terreno", "sondaje", "faena", "mina", "campo", "geolog", "relave")),
    ("detail", ("detalle", "close", "macro", "primer_plano")),
)


def classify_visual_theme(photo_id: Optional[str], detalle: str = "") -> Optional[str]:
    if not photo_id and not detalle:
        return None
    hay = f"{photo_id or ''} {detalle or ''}"
    for theme, kws in _VISUAL_KEYWORDS:
        if _has(hay, *kws):
            return theme
    return None


# --- record + fingerprint ----------------------------------------------------
@dataclass
class PostRecord:
    """Vista normalizada de una pieza para huella (desde archive u otro origen)."""

    content_id: str = ""
    cell: Optional[str] = None
    service: str = ""
    subtheme: str = ""
    editorial_angle: str = ""
    knowledge_id: Optional[str] = None
    evidence_ids: tuple[str, ...] = ()
    format: str = "STATIC"
    hook: str = ""
    body: str = ""
    cta: str = ""
    primary_claim_seed: str = ""   # e.g. graphic svc+msg
    photo_id: Optional[str] = None
    photo_detalle: str = ""


def _subtheme_name(v) -> str:
    if isinstance(v, dict):
        return str(v.get("nombre") or v.get("name") or "")
    return str(v or "")


def record_from_archive_post(p: dict) -> PostRecord:
    copy = p.get("copy") or {}
    graphic = p.get("graphic") or {}
    photo = p.get("photo") or {}
    seed = " · ".join(x for x in (graphic.get("svc", ""), _TAG_RE.sub(" ", graphic.get("msg", "")),
                                  graphic.get("title", "")) if x)
    return PostRecord(
        content_id=p.get("content_id", ""),
        cell=p.get("cell"),
        service=str(p.get("service") or graphic.get("svc") or ""),
        subtheme=_subtheme_name(p.get("subtheme")),
        editorial_angle=p.get("editorial_angle", ""),
        knowledge_id=p.get("knowledge_id"),
        evidence_ids=tuple(p.get("evidence_ids") or []),
        format=p.get("format", "STATIC"),
        hook=copy.get("hook", ""),
        body=copy.get("body", ""),
        cta=copy.get("cta", ""),
        primary_claim_seed=seed,
        photo_id=(photo.get("photo_id") or photo.get("stock_id")),
        photo_detalle=photo.get("detalle", ""),
    )


@dataclass
class EditorialFingerprint:
    content_id: str
    service: str
    subtheme: str
    primary_claim: str
    pain_point: str
    pain_category: str
    angle: str
    hook_type: str
    editorial_archetype: str
    cta_type: str
    format: str
    evidence_ids: list[str]
    knowledge_id: Optional[str]
    photo_id: Optional[str]
    visual_theme: Optional[str]

    def to_dict(self) -> dict:
        return asdict(self)


def _primary_claim(rec: PostRecord) -> str:
    if rec.primary_claim_seed.strip():
        return re.sub(r"\s+", " ", _TAG_RE.sub(" ", rec.primary_claim_seed)).strip()
    for marker in ("en #idiem", "en idiem", "desde #idiem", "desde idiem"):
        idx = clean_text(rec.body).find(marker)
        if idx >= 0:
            return _first_sentence(rec.body[idx:], 160)
    return _first_sentence(rec.body, 160)


def fingerprint_record(rec: PostRecord) -> EditorialFingerprint:
    return EditorialFingerprint(
        content_id=rec.content_id,
        service=rec.service,
        subtheme=rec.subtheme,
        primary_claim=_primary_claim(rec),
        pain_point=_first_sentence(_EMOJI_RE.sub("", rec.hook), 140).strip(),
        pain_category=classify_pain_category(rec.hook, rec.body),
        angle=rec.editorial_angle,
        hook_type=classify_hook_type(rec.hook),
        editorial_archetype=classify_archetype(rec),
        cta_type=classify_cta_type(rec.cta),
        format=(rec.format or "STATIC"),
        evidence_ids=list(rec.evidence_ids),
        knowledge_id=rec.knowledge_id,
        photo_id=rec.photo_id,
        visual_theme=classify_visual_theme(rec.photo_id, rec.photo_detalle),
    )


def fingerprint_archive_post(p: dict) -> EditorialFingerprint:
    return fingerprint_record(record_from_archive_post(p))
