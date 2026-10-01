"""Photo Library — deterministic photo selection for a post's graphic.

Reads ``config/photo_library/photo_manifest.csv`` (the human-curated library) and
picks the best REAL photo for a post by matching célula + subtema + disciplina +
entorno, in decreasing strictness. When nothing suitable exists, it returns a
Muapi generation spec instead of forcing an unrelated photo — fail closed on the
image, never misrepresent a project. A generated photo is always tagged as such
and never presented as a real record of an IDIEM project.

This lives behind an interface (CLAUDE.md: "keep future visual/assets integration
behind an interface"). The engine only DECIDES which photo/prompt to use; the
actual Muapi generation happens out-of-band at artifact-build time, exactly like
the graphic_brief is a reference and the final graphic is produced in the artifact.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass

from .loader import CONFIG_DIR

MANIFEST = CONFIG_DIR / "photo_library" / "photo_manifest.csv"

# A photo "corresponds" to a post only if it shares the célula AND either the
# subtema, or both disciplina and entorno. Below that we do not force a photo.
_MIN_CORRESPOND_SCORE = 6


@dataclass(frozen=True)
class Photo:
    id: str
    archivo: str
    concepto: str
    celulas: tuple[str, ...]
    subtemas: tuple[str, ...]
    disciplina: str
    entorno: str
    orientacion: str
    tipo: str
    derechos: str
    personas: str
    consentimiento: str
    fuente: str
    notas: str


def _split(v: str | None) -> tuple[str, ...]:
    return tuple(x.strip() for x in (v or "").split(";") if x.strip())


def load_photos(path=None) -> list[Photo]:
    path = path or MANIFEST
    if not path.exists():
        return []
    out: list[Photo] = []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            out.append(
                Photo(
                    id=(row.get("id") or "").strip(),
                    archivo=(row.get("archivo") or "").strip(),
                    concepto=(row.get("concepto") or "").strip(),
                    celulas=_split(row.get("celulas")),
                    subtemas=_split(row.get("subtemas")),
                    disciplina=(row.get("disciplina") or "").strip(),
                    entorno=(row.get("entorno") or "").strip(),
                    orientacion=(row.get("orientacion") or "").strip(),
                    tipo=(row.get("tipo") or "").strip(),
                    derechos=(row.get("derechos") or "").strip(),
                    personas=(row.get("personas") or "").strip(),
                    consentimiento=(row.get("consentimiento") or "").strip(),
                    fuente=(row.get("fuente") or "").strip(),
                    notas=(row.get("notas") or "").strip(),
                )
            )
    return out


def _score(
    photo: Photo,
    *,
    cell: str,
    subtema: str,
    disciplina: str,
    entorno: str,
    orientacion: str | None,
) -> int:
    """Higher is better. Returns -1 when the célula does not match (hard filter)."""
    if cell not in photo.celulas:
        return -1
    s = 0
    if subtema and subtema in photo.subtemas:
        s += 4
    if disciplina and disciplina == photo.disciplina:
        s += 2
    if entorno and entorno == photo.entorno:
        s += 2
    if orientacion and photo.orientacion and orientacion == photo.orientacion:
        s += 1
    # Prefer owned photos and images without consent risk (fewer identifiable people).
    if photo.derechos == "propia":
        s += 1
    if photo.personas == "no":
        s += 1
    return s


def build_muapi_prompt(
    *, cell: str, subtema: str, disciplina: str, entorno: str
) -> str:
    """A deterministic, safe prompt for a professional, photorealistic image.

    Describes the scene by disciplina/entorno/subtema only — never a specific
    project, client, result or superlative. No text, no logos, no invented people.
    """
    entorno_txt = {
        "mina": "faena minera real",
        "obra": "obra de construcción real",
        "terreno": "trabajo técnico en terreno",
        "laboratorio": "laboratorio técnico",
        "faena": "faena industrial",
        "oficina": "oficina de ingeniería",
    }.get(entorno, entorno or "contexto técnico")
    tema = subtema or disciplina or "ingeniería"
    return (
        f"Fotografía profesional y fotorrealista de {entorno_txt}, "
        f"que ilustra el servicio de {tema} en el ámbito de {cell.lower()}. "
        "Personas con equipo de protección en acción o estructura/equipamiento "
        "técnico real, luz natural o técnica, encuadre limpio y nítido, "
        "estética documental de ingeniería. "
        "Sin texto, sin logos, sin marcas de agua, sin rostros reconocibles "
        "inventados, sin estética de banco de imágenes genérico."
    )


def decide_photo(
    *,
    cell: str,
    subtema: str = "",
    disciplina: str = "",
    entorno: str = "",
    orientacion: str | None = None,
    exclude_ids: set[str] | None = None,
    photos: list[Photo] | None = None,
) -> dict:
    """Pick a real library photo, or fall back to a Muapi generation spec.

    Returns a dict with ``source`` = ``"library"`` | ``"muapi"``:
      - library:  {source, photo_id, archivo, fuente, orientacion, derechos, score}
      - muapi:    {source:"muapi", origin:"muapi_generada", prompt, requisitos, reason}
    """
    photos = photos if photos is not None else load_photos()
    exclude_ids = exclude_ids or set()

    ranked = sorted(
        (
            (
                _score(
                    p,
                    cell=cell,
                    subtema=subtema,
                    disciplina=disciplina,
                    entorno=entorno,
                    orientacion=orientacion,
                ),
                p,
            )
            for p in photos
            if p.id not in exclude_ids
        ),
        key=lambda t: (t[0], t[1].id),
        reverse=True,
    )

    if ranked and ranked[0][0] >= _MIN_CORRESPOND_SCORE:
        score, p = ranked[0]
        return {
            "source": "library",
            "photo_id": p.id,
            "archivo": p.archivo,
            "fuente": p.fuente,
            "orientacion": p.orientacion,
            "derechos": p.derechos,
            "personas": p.personas,
            "score": score,
        }

    # Nothing corresponds -> generate, tagged as such, never a real record.
    return {
        "source": "muapi",
        "origin": "muapi_generada",
        "prompt": build_muapi_prompt(
            cell=cell, subtema=subtema, disciplina=disciplina, entorno=entorno
        ),
        "requisitos": [
            "profesional y fotorrealista",
            "coherente con el servicio/célula del post",
            "sin texto, logos ni marcas de agua",
            "sin personas identificables inventadas",
        ],
        "reason": "sin foto adecuada en el manifest para este post",
    }
