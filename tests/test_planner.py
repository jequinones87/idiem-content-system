"""Milestone 5 — monthly planner."""

from idiem.planner import MonthlyPlanner, _largest_remainder


def _no_subs(kb):
    p = MonthlyPlanner(kb)
    p.config = {**p.config, "substitutions": {}}
    return p


def test_largest_remainder_sums_to_target():
    weights = {"A": 6, "B": 6, "C": 8, "D": 6, "E": 8}
    alloc = _largest_remainder(weights, 12)
    assert sum(alloc.values()) == 12
    assert all(v >= 0 for v in alloc.values())


def test_plan_hits_target_slot_count(kb):
    plan = MonthlyPlanner(kb).build_plan(month="2026-09", target_count=12)
    assert len(plan.slots) == 12


def test_transporte_substituted_by_default(kb):
    # Default config substitutes Transporte's quota into Salud/Pública.
    plan = MonthlyPlanner(kb).build_plan(month="2026-09", target_count=12)
    assert len(plan.slots) == 12
    assert all(s.cell != "INFRA CRÍTICA TRANSPORTE" for s in plan.slots)
    assert all(s.status == "DRAFT" for s in plan.slots)  # fallbacks have coverage


def test_transporte_gap_without_substitution(kb):
    plan = _no_subs(kb).build_plan(month="2026-09", target_count=12)
    transporte = [s for s in plan.slots if s.cell == "INFRA CRÍTICA TRANSPORTE"]
    assert transporte, "sin sustitución, Transporte recibe cuota por peso"
    assert all(s.status == "CONTENT_GAP" for s in transporte)
    assert plan.gaps


def test_no_consecutive_same_knowledge_id(kb):
    plan = MonthlyPlanner(kb).build_plan(month="2026-09", target_count=12)
    draft = [s for s in plan.slots if s.status == "DRAFT"]
    for a, b in zip(draft, draft[1:]):
        if a.knowledge_id and b.knowledge_id:
            assert a.knowledge_id != b.knowledge_id


def test_does_not_exceed_factual_coverage(kb):
    # With a huge target, DRAFT slots per cell never exceed that cell's coverage.
    plan = MonthlyPlanner(kb).build_plan(month="2026-09", target_count=200)
    from collections import Counter

    draft_per_cell = Counter(
        s.cell for s in plan.slots if s.status == "DRAFT"
    )
    for cell, n in draft_per_cell.items():
        assert n <= len(kb.items_in_cell(cell)), cell
    # No knowledge_id is reused across DRAFT slots (coverage-bounded).
    kids = [s.knowledge_id for s in plan.slots if s.status == "DRAFT"]
    assert len(kids) == len(set(kids))


def test_does_not_borrow_across_cells_without_config(kb):
    # Without substitution config, an unfillable cell must NOT borrow from others.
    plan = _no_subs(kb).build_plan(
        month="2026-09",
        target_count=5,
        weights={"INFRA CRÍTICA TRANSPORTE": 1},
    )
    assert all(s.status == "CONTENT_GAP" for s in plan.slots)
    assert all(s.cell == "INFRA CRÍTICA TRANSPORTE" for s in plan.slots)


def test_substitution_reassigns_transporte_quota(kb):
    # Configured substitution moves Transporte's quota to the fallback cells.
    plan = MonthlyPlanner(kb).build_plan(
        month="2026-09",
        target_count=5,
        weights={"INFRA CRÍTICA TRANSPORTE": 1},
    )
    assert all(s.cell != "INFRA CRÍTICA TRANSPORTE" for s in plan.slots)
    fallback = {"INFRA HOSPITALARIA Y ASISTENCIAL", "INFRA PÚBLICA RESILIENTE"}
    assert all(s.cell in fallback for s in plan.slots if s.status == "DRAFT")


def test_recent_history_excludes_ids(kb):
    plan = MonthlyPlanner(kb)
    first = plan.build_plan(month="2026-09", target_count=6)
    used = [s.knowledge_id for s in first.slots if s.knowledge_id]
    second = plan.build_plan(
        month="2026-10", target_count=6, recent_history=used
    )
    reused = {s.knowledge_id for s in second.slots if s.knowledge_id} & set(used)
    assert not reused


def test_allow_rebalance_config_fills_from_surplus(kb):
    planner = MonthlyPlanner(kb)
    planner.config = dict(planner.config)
    planner.config["allow_rebalance"] = True
    plan = planner.build_plan(
        month="2026-09",
        target_count=6,
        weights={"INFRA CRÍTICA TRANSPORTE": 5, "INFRA OPERACIÓN MINERA": 1},
    )
    # With rebalance on, surplus mining coverage absorbs unmet Transporte quota.
    draft = [s for s in plan.slots if s.status == "DRAFT"]
    assert draft, "el rebalance debe producir algunos DRAFT desde cobertura disponible"
    assert all(s.cell != "INFRA CRÍTICA TRANSPORTE" for s in draft)
