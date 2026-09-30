"""Editorial fingerprint — clasificadores deterministas + huella por pieza."""

import json
from pathlib import Path

from idiem.editorial_fingerprint import (
    ARCHETYPES,
    CTA_TYPES,
    HOOK_TYPES,
    PAIN_CATEGORIES,
    VISUAL_THEMES,
    PostRecord,
    classify_archetype,
    classify_cta_type,
    classify_hook_type,
    classify_visual_theme,
    fingerprint_archive_post,
    fingerprint_record,
)

ARCHIVE = Path(__file__).resolve().parents[1] / "content" / "archive" / "2026-09.json"


def test_hook_type_classifier():
    assert classify_hook_type("¿Tu obra está cumpliendo el programa?") == "question"
    assert classify_hook_type("Una falla no detectada puede detener la operación.") == "risk"
    assert classify_hook_type("El 85% de las obras enfrenta este problema.") == "statistic"
    assert classify_hook_type("No basta con inspeccionar una vez.") == "misconception"
    assert classify_hook_type("3 claves para revisar tu estructura.") == "checklist"


def test_cta_type_classifier():
    assert classify_cta_type("") == "no_cta"
    assert classify_cta_type("Contáctanos y conversemos sobre tu caso.") == "contact"
    assert classify_cta_type("Conversemos en https://idiem.cl 👉") == "conversation"
    assert classify_cta_type("¿Está tu obra cumpliendo la norma?") in {"question", "self_assessment"}
    assert classify_cta_type("Conoce nuestros servicios en https://idiem.cl") == "visit_service"
    assert classify_cta_type("Evalúa el estado de tu activo hoy.") == "self_assessment"


def test_archetype_institutional_when_no_knowledge():
    rec = PostRecord(content_id="X", knowledge_id=None, evidence_ids=(),
                     editorial_angle="saludo institucional", hook="Feliz día.", cta="")
    assert classify_archetype(rec) == "institutional_or_occasion"


def test_archetype_problem_solution_default():
    rec = PostRecord(content_id="X", knowledge_id="KB-IOM-001", evidence_ids=("KB-IOM-001",),
                     hook="Un riesgo puede detener la faena.",
                     body="En IDIEM apoyamos con inspección.", cta="Conversemos.")
    assert classify_archetype(rec) in ARCHETYPES
    assert classify_archetype(rec) == "problem_solution"


def test_visual_theme_from_photo_id():
    assert classify_visual_theme("planta_aceros") == "laboratory"
    assert classify_visual_theme("generica_estructura_acero_low") == "infrastructure"
    assert classify_visual_theme("generico_modelado_estructura") == "graphic"
    assert classify_visual_theme(None) is None


def test_primary_claim_prefers_graphic_seed():
    rec = PostRecord(content_id="X", knowledge_id="KB", evidence_ids=("KB",),
                     primary_claim_seed="Cumplimiento normativo · Cerrar las brechas.",
                     body="Texto largo del cuerpo.", hook="h", cta="c")
    fp = fingerprint_record(rec)
    assert "brechas" in fp.primary_claim.lower()


def test_fingerprint_all_enums_valid_on_real_archive():
    posts = json.loads(ARCHIVE.read_text(encoding="utf-8"))["posts"]
    for p in posts:
        fp = fingerprint_archive_post(p)
        assert fp.hook_type in HOOK_TYPES
        assert fp.cta_type in CTA_TYPES
        assert fp.editorial_archetype in ARCHETYPES
        assert fp.pain_category in PAIN_CATEGORIES
        assert fp.visual_theme is None or fp.visual_theme in VISUAL_THEMES
        assert fp.content_id
        # la huella es serializable (para archivado)
        d = fp.to_dict()
        assert set(d) >= {"hook_type", "cta_type", "editorial_archetype", "primary_claim"}


def test_fingerprint_detects_cta_concentration_in_september():
    # Regresión: septiembre concentra el CTA "conversation" (problema real).
    posts = json.loads(ARCHIVE.read_text(encoding="utf-8"))["posts"]
    ctas = [fingerprint_archive_post(p).cta_type for p in posts]
    assert ctas.count("conversation") >= 6
