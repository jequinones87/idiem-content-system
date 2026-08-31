"""Milestone 4 — brief generator and schema validation."""

import pytest
from jsonschema import ValidationError

from idiem.brief import build_brief, is_valid_brief, validate_brief


def test_brief_is_schema_valid_for_every_cell(kb):
    for cell in kb.cells():
        brief = build_brief(kb, cell)
        validate_brief(brief)  # raises if invalid


def test_draft_brief_has_expected_shape(kb):
    brief = build_brief(kb, "INFRA PÚBLICA RESILIENTE")
    assert brief["status"] == "DRAFT"
    assert brief["cell"] == "INFRA PÚBLICA RESILIENTE"
    assert brief["recommended_format"] in {"STATIC", "CAROUSEL"}
    assert brief["qa"]["human_approval"] is False  # stays DRAFT until approval


def test_content_gap_brief_is_schema_valid(kb):
    brief = build_brief(kb, "INFRA CRÍTICA TRANSPORTE", topic="Metro estructural")
    assert brief["status"] == "CONTENT_GAP"
    assert brief["expert_input_required"] is True
    validate_brief(brief)


def test_visual_brief_contract_present(kb):
    brief = build_brief(kb, "LAB MINERO DIGITAL")
    vb = brief["visual_brief"]
    assert set(vb) == {"main_message", "supporting_points", "evidence_to_visualize"}


def test_invalid_brief_is_rejected(kb):
    brief = build_brief(kb, "INFRA OPERACIÓN MINERA")
    brief["status"] = "PUBLISHED_NOW"  # not in enum
    assert not is_valid_brief(brief)
    with pytest.raises(ValidationError):
        validate_brief(brief)


def test_invalid_content_type_raises(kb):
    with pytest.raises(ValueError):
        build_brief(kb, "INFRA OPERACIÓN MINERA", content_type="BOGUS")


def test_draft_copy_only_contains_allowed_facts(kb):
    brief = build_brief(kb, "INFRA PÚBLICA RESILIENTE")
    # Body is built strictly from allowed_facts (no invented IDIEM facts).
    body = brief["draft_copy"]["body"]
    for line in filter(None, body.split("\n")):
        assert line in brief["allowed_facts"]
