"""Webinar track — an ADD-ON to the 12 monthly posts, not part of them.

Webinar pieces are external input (event logistics: title, date, speaker, URLs),
so they do not come from the 2A.2 evidence library, do not consume a monthly slot,
and never touch the cooldown ledger or the cell rotation. A structured brief (with
repeatable sessions) feeds a template that renders a STATIC piece for a single
webinar or a CAROUSEL for a cycle of several.

Grounding note (CLAUDE.md rules 2–3): event logistics are free input, but any
technical claim about IDIEM in a session's `temario` still passes the library rules
at copy time (NAME_ONLY, no superlatives). This module only structures the brief and
resolves speakers; it does not fabricate claims.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass

from .loader import CONFIG_DIR

EXPOSITORES = CONFIG_DIR / "expositor_library" / "expositores.csv"
WEBINAR_DIR = CONFIG_DIR / "webinar"
SCHEMA = WEBINAR_DIR / "webinar_brief.schema.json"


@dataclass(frozen=True)
class Expositor:
    id: str
    nombre: str
    cargo: str
    carpeta_id: str
    carpeta_url: str
    foto_principal_id: str
    notas: str


def load_expositores(path=None) -> dict[str, Expositor]:
    path = path or EXPOSITORES
    out: dict[str, Expositor] = {}
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            e = Expositor(
                id=(row.get("id") or "").strip(),
                nombre=(row.get("nombre") or "").strip(),
                cargo=(row.get("cargo") or "").strip(),
                carpeta_id=(row.get("carpeta_id") or "").strip(),
                carpeta_url=(row.get("carpeta_url") or "").strip(),
                foto_principal_id=(row.get("foto_principal_id") or "").strip(),
                notas=(row.get("notas") or "").strip(),
            )
            if e.id:
                out[e.id] = e
    return out


def load_brief(path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_brief(brief: dict) -> None:
    """Validate against the JSON schema. Raises jsonschema.ValidationError on failure."""
    import jsonschema

    with SCHEMA.open("r", encoding="utf-8") as fh:
        schema = json.load(fh)
    jsonschema.validate(brief, schema)


def resolve_mode(brief: dict) -> str:
    """STATIC for a single session, CAROUSEL for a cycle — unless forced."""
    modo = (brief.get("modo") or "auto").lower()
    n = len(brief.get("sesiones", []))
    if modo == "static":
        return "STATIC"
    if modo == "carousel":
        return "CAROUSEL"
    return "CAROUSEL" if n >= 2 else "STATIC"


def resolve_session(session: dict, brief: dict, expositores: dict[str, Expositor]) -> dict:
    """Merge a session with its expositor record and cycle-level fallbacks."""
    exp = expositores.get(session.get("relator_id", ""))
    relator_nombre = session.get("relator_nombre") or (exp.nombre if exp else "")
    relator_cargo = session.get("relator_cargo") or (exp.cargo if exp else "")
    return {
        "titulo": session.get("titulo", ""),
        "fecha": session.get("fecha", ""),
        "hora": session.get("hora", ""),
        "modalidad": session.get("modalidad", "Online"),
        "plataforma": session.get("plataforma", ""),
        "url_sesion": session.get("url_sesion", ""),
        # per-session inscription URL falls back to the cycle-level one
        "url_inscripcion": session.get("url_inscripcion") or brief.get("inscripcion_url", ""),
        "relator_id": session.get("relator_id", ""),
        "relator_nombre": relator_nombre,
        "relator_cargo": relator_cargo,
        "relator_foto_id": exp.foto_principal_id if exp else "",
        "relator_carpeta_url": exp.carpeta_url if exp else "",
        "temario": list(session.get("temario", [])),
    }


def build_webinar_plan(brief: dict, expositores: dict[str, Expositor] | None = None) -> dict:
    """Resolve a validated brief into a render plan: mode + resolved sessions."""
    expositores = expositores if expositores is not None else load_expositores()
    sesiones = [resolve_session(s, brief, expositores) for s in brief.get("sesiones", [])]
    return {
        "ciclo": brief.get("ciclo", ""),
        "mode": resolve_mode(brief),
        "inscripcion_url": brief.get("inscripcion_url", ""),
        "sesiones": sesiones,
        "content_type": "WEBINAR",
        "track": "eventos",
        "consume_monthly_slot": False,
        "uses_ledger": False,
    }
