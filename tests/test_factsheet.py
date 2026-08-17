"""Milestone 3 — fact sheet engine."""

from idiem.factsheet import build_fact_sheet


def test_factsheet_generated_for_populated_cell(kb):
    sheet = build_fact_sheet(kb, "INFRA PÚBLICA RESILIENTE")
    assert not sheet.is_content_gap
    assert sheet.knowledge_ids
    assert sheet.allowed_facts
    assert sheet.relation_ids
    assert sheet.document_ids


def test_factsheet_logs_reasons(kb):
    # CLAUDE.md: log reasons for every blocked/gap state.
    sheet = build_fact_sheet(kb, "INFRA CRÍTICA TRANSPORTE")
    assert sheet.log
    assert any("CONTENT_GAP" in line for line in sheet.log)


def test_topic_without_match_is_gap_not_borrowed(kb):
    sheet = build_fact_sheet(kb, "INFRA HOSPITALARIA Y ASISTENCIAL", topic="zzz-no-existe-xyz")
    assert sheet.is_content_gap
    assert sheet.knowledge_ids == []


def test_factsheet_only_same_cell_ids(kb):
    for cell, prefix in [
        ("INFRA PÚBLICA RESILIENTE", "KB-IPR"),
        ("INFRA OPERACIÓN MINERA", "KB-IOM"),
        ("LAB MINERO DIGITAL", "KB-LMD"),
        ("INFRA HOSPITALARIA Y ASISTENCIAL", "KB-IHA"),
    ]:
        sheet = build_fact_sheet(kb, cell)
        assert all(k.startswith(prefix) for k in sheet.knowledge_ids), cell
