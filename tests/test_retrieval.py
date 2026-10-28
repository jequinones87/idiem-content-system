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


def test_contracting_mechanism_auxiliary_is_blocked_by_config(kb):
    # MKT 28-10-2026: Ley 21.094 no se aborda en RRSS (config/cell_rules.json)
    from idiem.factsheet import build_fact_sheet

    engine = RetrievalEngine(kb)
    cell = "INFRA PÚBLICA RESILIENTE"
    assert all(a.type != "MECANISMO_CONTRATACION" for a in engine._compatible_auxiliary(cell))
    blocked = {a.auxiliary_id for a, _ in engine._blocked_auxiliary(cell)}
    assert {"AUX-010", "AUX-016"} <= blocked
    sheet = build_fact_sheet(kb, cell)
    assert not blocked & set(sheet.auxiliary_ids)
    assert any(b.startswith("[AUX-010] Bloqueado por config") for b in sheet.blocked_claims)
