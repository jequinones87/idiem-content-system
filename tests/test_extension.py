"""2A.3 evidence extension — additive, validated, non-mutating."""

from idiem import policies
from idiem.factsheet import build_fact_sheet
from idiem.integrity import EXPECTED_TOTALS


def test_extension_loads(kb):
    total = sum(len(v) for v in kb._enrichment_by_service.values())
    assert total > 0, "la extensión 2A.3 debe cargar registros"


def test_every_enrichment_attaches_to_real_service(kb):
    real = {(it.cell, it.service) for it in kb.knowledge_items}
    for key in kb._enrichment_by_service:
        assert key in real, f"enrichment con (cell,service) inexistente: {key}"


def test_every_enrichment_resolves_document(kb):
    for recs in kb._enrichment_by_service.values():
        for r in recs:
            assert r.get("document_id"), f"file_name sin document_id: {r.get('file_name')}"


def test_enrichment_policies_valid(kb):
    for recs in kb._enrichment_by_service.values():
        for r in recs:
            assert policies.is_valid_generation_policy(r["generation_policy"])


def test_extension_does_not_change_2A2_counts(kb):
    # The additive layer must not alter the canonical closure totals.
    assert len(kb.knowledge_items) == EXPECTED_TOTALS["active_knowledge_items"]
    assert len(kb.technical_relation_ids()) == EXPECTED_TOTALS["technical_source_relations"]


def test_enrichment_deepens_fact_sheet(kb):
    cell = "INFRA OPERACIÓN MINERA"
    anchor = next(
        it for it in kb.items_in_cell(cell) if it.service == "Servicios a operación minera"
    )
    base = build_fact_sheet(kb, cell, main_knowledge_id=anchor.knowledge_id)
    enriched = build_fact_sheet(
        kb, cell, main_knowledge_id=anchor.knowledge_id, enrich_same_service=True
    )
    assert len(enriched.allowed_facts) > len(base.allowed_facts)
    assert any(f.startswith("[EXT-") for f in enriched.allowed_facts)


def test_enrichment_blocks_source_superlatives(kb):
    # Rocas/geotecnia enrichment must surface blocked superlatives.
    cell = "LAB MINERO DIGITAL"
    anchor = next(
        it for it in kb.items_in_cell(cell) if it.service == "Laboratorio de rocas"
    )
    sheet = build_fact_sheet(
        kb, cell, main_knowledge_id=anchor.knowledge_id, enrich_same_service=True
    )
    blob = " ".join(sheet.blocked_claims).lower()
    assert "no afirmar" in blob or "ranking" in blob or "superlativ" in blob
