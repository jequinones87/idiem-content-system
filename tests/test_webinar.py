"""Webinar track: brief validation, static/carousel mode, expositor resolution,
repeatable sessions, and URL fallbacks. Webinar pieces never consume a monthly slot."""

import json

import pytest

from idiem.webinar import (
    EXPOSITORES,
    build_webinar_plan,
    load_brief,
    load_expositores,
    resolve_mode,
    validate_brief,
    WEBINAR_DIR,
)


def _brief(n_sessions: int, modo: str = "auto") -> dict:
    return {
        "ciclo": "Ciclo demo",
        "modo": modo,
        "inscripcion_url": "https://idiem.cl/insc",
        "sesiones": [
            {
                "titulo": f"Sesión {i+1}",
                "fecha": "2026-09-25",
                "hora": "16:00",
                "relator_id": "EXP-01",
                "url_sesion": "https://zoom.us/x",
                "temario": ["a", "b"],
            }
            for i in range(n_sessions)
        ],
    }


def test_expositor_library_loads():
    exps = load_expositores()
    assert len(exps) >= 12
    assert "EXP-01" in exps and exps["EXP-01"].nombre
    # every expositor references a Drive folder
    assert all(e.carpeta_id for e in exps.values())


def test_example_brief_is_schema_valid():
    brief = load_brief(WEBINAR_DIR / "example_brief.json")
    validate_brief(brief)  # raises on failure


def test_mode_single_session_is_static():
    assert resolve_mode(_brief(1)) == "STATIC"


def test_mode_cycle_is_carousel():
    assert resolve_mode(_brief(3)) == "CAROUSEL"


def test_mode_can_be_forced():
    assert resolve_mode(_brief(1, modo="carousel")) == "CAROUSEL"
    assert resolve_mode(_brief(3, modo="static")) == "STATIC"


def test_repeatable_sessions_are_all_resolved():
    plan = build_webinar_plan(_brief(3))
    assert len(plan["sesiones"]) == 3
    assert plan["mode"] == "CAROUSEL"


def test_session_inscription_url_falls_back_to_cycle():
    brief = _brief(1)
    brief["inscripcion_url"] = "https://idiem.cl/global"
    # session has no url_inscripcion -> uses cycle-level
    plan = build_webinar_plan(brief)
    assert plan["sesiones"][0]["url_inscripcion"] == "https://idiem.cl/global"


def test_relator_resolved_from_library():
    plan = build_webinar_plan(_brief(1))
    s = plan["sesiones"][0]
    assert s["relator_nombre"]  # pulled from EXP-01
    assert s["relator_foto_id"]  # library has a principal photo id for EXP-01


def test_webinar_never_consumes_monthly_slot():
    plan = build_webinar_plan(_brief(1))
    assert plan["content_type"] == "WEBINAR"
    assert plan["consume_monthly_slot"] is False
    assert plan["uses_ledger"] is False


def test_brief_requires_at_least_one_session():
    with pytest.raises(Exception):
        validate_brief({"sesiones": []})
