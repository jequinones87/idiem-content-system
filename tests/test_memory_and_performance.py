"""Memoria unificada (ledger derivado del archivo) + andamiaje de performance."""

from idiem.ledger import build_ledger_from_archive, recent_knowledge_ids
from idiem.performance import (
    PERFORMANCE_FIELDS,
    PerformanceRow,
    load_performance,
    performance_by_content_id,
)


def test_ledger_derived_from_archive():
    ledger = build_ledger_from_archive()
    assert "2026-09" in ledger.months
    assert "2026-10" in ledger.months
    assert all(e.get("knowledge_id") for e in ledger.months["2026-10"])
    # el cooldown se calcula desde el ledger derivado (mismo cálculo que el planner)
    recent = recent_knowledge_ids(ledger, "2026-11", cooldown_months=3)
    assert any(k.startswith("KB-") for k in recent)


def test_performance_schema_and_empty_load():
    for req in ("content_id", "impressions", "cta_type", "archetype", "leads"):
        assert req in PERFORMANCE_FIELDS
    # Hoy el archivo trae solo header -> sin filas.
    assert load_performance() == []
    assert performance_by_content_id([]) == {}


def test_performance_parses_rows(tmp_path):
    p = tmp_path / "perf.csv"
    p.write_text(
        "content_id,date,cell,service,subtheme,archetype,hook_type,cta_type,format,"
        "impressions,engagements,clicks,comments,shares,leads\n"
        "PLAN-X,2026-10-01,IOM,Confiabilidad,fallas,problem_solution,risk,contact,STATIC,"
        "1000,80,12,3,5,1\n",
        encoding="utf-8",
    )
    rows = load_performance(p)
    assert len(rows) == 1 and isinstance(rows[0], PerformanceRow)
    assert rows[0].impressions == 1000 and rows[0].leads == 1
    assert performance_by_content_id(rows)["PLAN-X"].cta_type == "contact"
