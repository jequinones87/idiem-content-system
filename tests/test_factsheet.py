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


def test_factsheet_anchored_to_main_knowledge_id(kb):
    item = kb.items_in_cell("INFRA OPERACIÓN MINERA")[0]
    sheet = build_fact_sheet(
        kb, "INFRA OPERACIÓN MINERA", main_knowledge_id=item.knowledge_id
    )
    assert not sheet.is_content_gap
    assert sheet.knowledge_ids == [item.knowledge_id]


def test_factsheet_enrich_same_service(kb):
    # Pick a service with more than one item in a cell.
    from collections import Counter

    cell = "INFRA OPERACIÓN MINERA"
    svc_counts = Counter(it.service for it in kb.items_in_cell(cell))
    svc = next(s for s, n in svc_counts.items() if n > 1)
    anchor = next(it for it in kb.items_in_cell(cell) if it.service == svc)

    base = build_fact_sheet(kb, cell, main_knowledge_id=anchor.knowledge_id)
    enriched = build_fact_sheet(
        kb, cell, main_knowledge_id=anchor.knowledge_id, enrich_same_service=True
    )
    # Enrichment adds same-service siblings and more grounded facts.
    assert len(enriched.knowledge_ids) > len(base.knowledge_ids)
    assert anchor.knowledge_id in enriched.knowledge_ids
    for kid in enriched.knowledge_ids:
        item = kb.item_by_id[kid]
        assert item.cell == cell        # never crosses cells
        assert item.service == svc      # same service only


def test_factsheet_anchor_from_wrong_cell_is_gap(kb):
    lab_item = kb.items_in_cell("LAB MINERO DIGITAL")[0]
    sheet = build_fact_sheet(
        kb, "INFRA OPERACIÓN MINERA", main_knowledge_id=lab_item.knowledge_id
    )
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
