"""Milestone 2 — deterministic retrieval."""

from idiem.retrieval import RetrievalEngine, RetrievalQuery


def test_retrieve_by_cell_stays_in_cell(kb):
    engine = RetrievalEngine(kb)
    hits = engine.retrieve_by_cell("INFRA OPERACIÓN MINERA")
    assert len(hits) == 65
    assert all(h.item.cell == "INFRA OPERACIÓN MINERA" for h in hits)


def test_retrieve_returns_traceability_and_policy(kb):
    engine = RetrievalEngine(kb)
    hits = engine.retrieve_by_cell("INFRA PÚBLICA RESILIENTE")
    h = hits[0]
    assert h.policy == h.item.generation_policy
    assert h.relation_ids, "debe exponer relation_ids"
    assert h.document_ids, "debe exponer document_ids"


def test_filter_by_policy(kb):
    engine = RetrievalEngine(kb)
    hits = engine.retrieve(
        RetrievalQuery(cell="LAB MINERO DIGITAL", policy="USE_TECHNICAL_CORE_BLOCK_CLAIMS")
    )
    assert hits
    assert all(h.policy == "USE_TECHNICAL_CORE_BLOCK_CLAIMS" for h in hits)


def test_keyword_is_accent_insensitive(kb):
    engine = RetrievalEngine(kb)
    hits = engine.retrieve(RetrievalQuery(cell="LAB MINERO DIGITAL", keyword="triaxial"))
    assert hits
    assert all(h.item.cell == "LAB MINERO DIGITAL" for h in hits)


def test_compatible_auxiliary_is_same_cell_and_usable(kb):
    engine = RetrievalEngine(kb)
    hits = engine.retrieve_by_cell("INFRA PÚBLICA RESILIENTE")
    for h in hits:
        for aux in h.compatible_auxiliary:
            assert aux.cell == "INFRA PÚBLICA RESILIENTE"
            assert aux.production_policy != "DO_NOT_USE_AS_FACT"


def test_transporte_cell_returns_no_items(kb):
    engine = RetrievalEngine(kb)
    assert engine.retrieve_by_cell("INFRA CRÍTICA TRANSPORTE") == []
