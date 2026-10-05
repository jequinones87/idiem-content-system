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


def test_deepened_enrichment_resolves_documents(kb):
    # Fase E: the deepened 2A.3 curation (EXT-0110+) loads and each record
    # resolves its source document, and attaches to a real (cell, service).
    new_ids = [f"EXT-0{n}" for n in range(110, 123)]
    seen = 0
    for eid in new_ids:
        rec = kb.enrichment_by_id(eid)
        if rec is None:
            continue
        seen += 1
        assert rec.get("document_id"), f"{eid} sin document_id resuelto"
        assert kb.enrichment_for(rec["cell"], rec["service"]), f"{eid} servicio inexistente"
    assert seen >= 10, f"esperaba >=10 registros nuevos, vi {seen}"


def test_incendios_service_now_has_evidence(kb):
    # Fase E filled a previously-empty service.
    recs = kb.enrichment_for("INFRA PÚBLICA RESILIENTE", "Ingeniería contra incendios")
    assert recs, "Ingeniería contra incendios debe tener evidencia 2A.3"
