"""Milestone 6 — drafting adapter."""

import pytest

from idiem.brief import build_brief, validate_brief
from idiem.drafting import (
    DeterministicDrafter,
    LLMDrafter,
    apply_draft,
    assert_no_blocked_claim_terms,
    assert_no_fact_leakage,
    build_drafting_request,
    forbidden_terms,
    ingest_draft,
    render_drafting_prompt,
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


# --- Publish-intended copy path (agent- or LLM-drafted) ----------------------
def test_forbidden_terms_include_blocked_claim_quotes(kb):
    brief = build_brief(kb, "LAB MINERO DIGITAL", topic="Triaxial")
    terms = forbidden_terms(brief)
    # Superlatives surfaced by the Triaxial BLOCK_CLAIMS items must be forbidden.
    assert "único" in terms
    assert any("más grande del mundo" in t for t in terms)


def test_drafting_request_is_bounded(kb):
    brief = build_brief(kb, "LAB MINERO DIGITAL", topic="Triaxial")
    req = build_drafting_request(brief)
    assert req.allowed_facts
    assert req.forbidden_terms
    assert "JSON" in render_drafting_prompt(req)


def test_ingest_rejects_blocked_term_copy(kb):
    brief = build_brief(kb, "LAB MINERO DIGITAL", topic="Triaxial")
    bad = {
        "hook": "El único equipo del mundo",
        "body": "IDIEM tiene el equipo más grande del mundo.",
        "cta": "Hablemos.",
    }
    with pytest.raises(ValueError):
        ingest_draft(brief, bad)


def test_ingest_accepts_clean_copy_and_keeps_draft(kb):
    brief = build_brief(kb, "LAB MINERO DIGITAL", topic="Triaxial")
    good = {
        "hook": "Ensayos de gran escala para geotecnia minera.",
        "body": (
            "IDIEM cuenta con un equipo Triaxial Gigante para ensayar suelos de "
            "gran tamaño, desarrollado con ingeniería propia, aplicado en gran "
            "minería, presas de tierra, energía e infraestructura."
        ),
        "cta": "Conversemos sobre tu proyecto.",
    }
    out = ingest_draft(brief, good)
    assert out["status"] == "DRAFT"
    assert out["draft_copy"] == good
    assert out["traceability"] == brief["traceability"]
    validate_brief(out)


def test_llm_drafter_output_is_validated(kb):
    brief = build_brief(kb, "LAB MINERO DIGITAL", topic="Triaxial")

    def fake_complete(_prompt: str) -> str:
        # Simulates a compliant model response.
        return (
            '{"hook": "Geotecnia de gran escala.", '
            '"body": "Equipo Triaxial Gigante para partículas de gran tamaño, '
            'con ingeniería propia.", "cta": "Hablemos."}'
        )

    draft = LLMDrafter(fake_complete).draft(brief)
    assert draft["hook"]
    assert_no_blocked_claim_terms(brief, draft)


def test_llm_drafter_rejects_leaky_response(kb):
    brief = build_brief(kb, "LAB MINERO DIGITAL", topic="Triaxial")

    def leaky(_prompt: str) -> str:
        return '{"hook": "único en el mundo", "body": "x", "cta": "y"}'

    with pytest.raises(ValueError):
        LLMDrafter(leaky).draft(brief)
