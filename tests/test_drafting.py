"""Milestone 6 — drafting adapter."""

import pytest

from idiem.brief import build_brief, validate_brief
from idiem.drafting import (
    DeterministicDrafter,
    apply_draft,
    assert_no_fact_leakage,
)


def test_draft_keeps_status_draft_and_schema_valid(kb):
    brief = build_brief(kb, "INFRA PÚBLICA RESILIENTE")
    drafted = apply_draft(brief)
    assert drafted["status"] == "DRAFT"
    validate_brief(drafted)
    assert drafted["draft_copy"]["hook"]
    assert drafted["draft_copy"]["body"]


def test_draft_adds_no_new_facts(kb):
    brief = build_brief(kb, "INFRA OPERACIÓN MINERA")
    drafted = apply_draft(brief)
    # Body prose is derived only from allowed_facts + matices (tags stripped).
    from idiem.drafting import _strip_tag

    allowed = {_strip_tag(f) for f in brief["allowed_facts"]}
    matices = {_strip_tag(m) for m in brief["mandatory_matices"]}
    for line in drafted["draft_copy"]["body"].split("\n"):
        clean = line.lstrip("•– ").strip()
        if not clean or clean in {"Notas de uso (respetar):"}:
            continue
        assert clean in allowed or clean in matices, clean


def test_draft_preserves_traceability(kb):
    brief = build_brief(kb, "LAB MINERO DIGITAL")
    drafted = apply_draft(brief)
    assert drafted["traceability"] == brief["traceability"]
    assert drafted["knowledge_ids"] == brief["knowledge_ids"]


def test_content_gap_brief_has_empty_draft(kb):
    brief = build_brief(kb, "INFRA CRÍTICA TRANSPORTE", topic="Metro")
    drafted = apply_draft(brief)
    assert drafted["status"] == "CONTENT_GAP"
    assert drafted["draft_copy"] == {"hook": "", "body": "", "cta": ""}


def test_fact_leakage_guard_rejects_foreign_id(kb):
    brief = build_brief(kb, "INFRA OPERACIÓN MINERA")
    bad_draft = {"hook": "KB-ZZZ-999 nuevo servicio", "body": "", "cta": ""}
    with pytest.raises(ValueError):
        assert_no_fact_leakage(brief, bad_draft)


def test_drafter_is_pluggable_via_protocol(kb):
    brief = build_brief(kb, "INFRA PÚBLICA RESILIENTE")
    assert DeterministicDrafter().draft(brief)["hook"]
