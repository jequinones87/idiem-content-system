"""Mandatory policy tests A–F from docs/04_ACCEPTANCE_CRITERIA.md."""

import re

from idiem.brief import build_brief
from idiem.cells import CellRules
from idiem.factsheet import build_fact_sheet

TRANSPORTE = "INFRA CRÍTICA TRANSPORTE"
LAB = "LAB MINERO DIGITAL"
MINERA = "INFRA OPERACIÓN MINERA"


# --- Test A — Transporte ------------------------------------------------------
def test_A_transporte_is_content_gap(kb):
    sheet = build_fact_sheet(kb, TRANSPORTE, topic="post técnico Metro")
    assert sheet.is_content_gap
    assert sheet.knowledge_ids == []
    assert sheet.allowed_facts == []
    assert any("Metro/EFE" in g or "activos" in g.lower() for g in sheet.content_gaps)


def test_A_transporte_brief_status_content_gap(kb):
    brief = build_brief(kb, TRANSPORTE, topic="post técnico Metro")
    assert brief["status"] == "CONTENT_GAP"
    assert brief["draft_copy"]["body"] == ""  # no technical draft
    assert brief["knowledge_ids"] == []


# --- Test B — Modelamiento preventivo (NAME_ONLY_DO_NOT_EXPAND) ---------------
def test_B_name_only_may_be_named_not_expanded(kb):
    sheet = build_fact_sheet(kb, MINERA, topic="Modelamiento preventivo")
    name_only_ids = {
        it.knowledge_id
        for it in kb.items_in_cell(MINERA)
        if it.generation_policy == "NAME_ONLY_DO_NOT_EXPAND"
        and it.knowledge_id in sheet.knowledge_ids
    }
    assert name_only_ids, "el topic debe recuperar al menos un item NAME_ONLY"

    for kid in name_only_ids:
        # A mandatory caveat forbids expansion.
        assert any(
            kid in m and "NAME_ONLY" in m for m in sheet.mandatory_matices
        ), f"falta caveat NAME_ONLY para {kid}"
        # Allowed facts for this id are naming-only (contain 'mencionar'),
        # never a verified-evidence expansion.
        facts = [f for f in sheet.allowed_facts if f.startswith(f"[{kid}]")]
        assert facts
        assert all("mencionar por nombre" in f for f in facts), facts


# --- Test C — Triaxial (USE_TECHNICAL_CORE_BLOCK_CLAIMS) ----------------------
def test_C_triaxial_core_allowed_claims_blocked(kb):
    sheet = build_fact_sheet(kb, LAB, topic="Triaxial")
    block_ids = {
        it.knowledge_id
        for it in kb.items_in_cell(LAB)
        if it.generation_policy == "USE_TECHNICAL_CORE_BLOCK_CLAIMS"
        and it.knowledge_id in sheet.knowledge_ids
    }
    assert block_ids, "Triaxial debe recuperar items BLOCK_CLAIMS"
    # Technical/lab description allowed when supported.
    assert sheet.allowed_facts
    # Rankings/superlatives explicitly blocked.
    assert sheet.blocked_claims
    blob = " ".join(sheet.blocked_claims).lower()
    assert "ranking" in blob or "superlativ" in blob or "exclusiv" in blob


def test_C_no_world_claim_leaks_into_allowed_facts(kb):
    sheet = build_fact_sheet(kb, LAB, topic="Triaxial")
    forbidden = re.compile(r"único en el mundo|el más grande del mundo|world[- ]?class ranking", re.I)
    assert not any(forbidden.search(f) for f in sheet.allowed_facts)


# --- Test D — Mining boundary (no cross-cell leakage) ------------------------
def test_D_lab_brief_never_leaks_operacion_minera(kb):
    sheet = build_fact_sheet(kb, LAB, topic="BIM monitoreo de activos")
    assert all(not kid.startswith("KB-IOM") for kid in sheet.knowledge_ids)


def test_D_digital_does_not_pull_items_into_lab(kb):
    # GR-10: 'digital' is not a technical entry requirement for LAB.
    assert kb.cell_rules.get("digital_does_not_determine_lab") is True


def test_D_operacion_minera_holds_integrity_engineering(kb):
    # When the service is integrity/engineering/continuity it lives in IOM,
    # retrievable there — and must not appear in a LAB brief.
    iom_ids = {it.knowledge_id for it in kb.items_in_cell(MINERA)}
    lab_ids = {it.knowledge_id for it in kb.items_in_cell(LAB)}
    assert iom_ids.isdisjoint(lab_ids)


# --- Test E — excluded evidence (hard block) ---------------------------------
def test_E_excluded_relations_never_used(kb):
    excluded = set(kb.excluded_relation_ids)
    used = set()
    for cell in kb.cells():
        sheet = build_fact_sheet(kb, cell)
        used.update(sheet.relation_ids)
    assert excluded, "debe haber relaciones excluidas en la biblioteca"
    assert used.isdisjoint(excluded), "una relación excluida se filtró como evidencia"


def test_E_excluded_absent_from_briefs(kb):
    excluded = set(kb.excluded_relation_ids)
    for cell in kb.cells():
        brief = build_brief(kb, cell)
        assert set(brief["traceability"]["relation_ids"]).isdisjoint(excluded)


# --- Test F — source traceability --------------------------------------------
def test_F_every_allowed_fact_cites_a_knowledge_id(kb):
    sheet = build_fact_sheet(kb, "INFRA PÚBLICA RESILIENTE")
    tag = re.compile(r"^\[(KB-[A-Z]{3}-\d{3})\]")
    for fact in sheet.allowed_facts:
        m = tag.match(fact)
        assert m, f"fact sin cita de knowledge_id: {fact!r}"
        assert m.group(1) in kb.item_by_id


def test_F_draft_brief_exposes_supporting_ids(kb):
    brief = build_brief(kb, "INFRA OPERACIÓN MINERA")
    assert brief["status"] == "DRAFT"
    assert brief["knowledge_ids"]
    assert brief["traceability"]["relation_ids"]
    assert brief["traceability"]["document_ids"]
