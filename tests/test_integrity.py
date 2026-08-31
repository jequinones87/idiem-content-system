"""Milestone 1 — integrity and closure reproduction.

Acceptance: reproduces the known closure totals; fails on missing/duplicate IDs
or invalid policy.
"""

import copy

import pytest

from idiem import integrity
from idiem.integrity import (
    EXPECTED_CELL_ITEMS,
    EXPECTED_TOTALS,
    IntegrityError,
    assert_integrity,
    run_all_checks,
)


def test_all_integrity_checks_pass(kb):
    results = run_all_checks(kb)
    failed = [r for r in results if not r.passed]
    assert not failed, "\n".join(f"{r.check_id}: {r.reason}" for r in failed)


def test_reproduces_closure_totals(kb):
    tech = kb.technical_relation_ids()
    aux = kb.auxiliary_relation_ids()
    assert len(kb.knowledge_items) == EXPECTED_TOTALS["active_knowledge_items"]
    assert len(tech) == EXPECTED_TOTALS["technical_source_relations"]
    assert len(aux) == EXPECTED_TOTALS["auxiliary_relations"]
    assert len(kb.reserve_relation_ids) == EXPECTED_TOTALS["reserve"]
    assert len(kb.excluded_relation_ids) == EXPECTED_TOTALS["excluded"]
    assert len(kb.source_documents) == EXPECTED_TOTALS["source_documents"]
    assert len(tech) + len(aux) == EXPECTED_TOTALS["assigned_to_cells"]
    total = len(tech) + len(aux) + len(kb.reserve_relation_ids) + len(kb.excluded_relation_ids)
    assert total == EXPECTED_TOTALS["source_relations_total"]


def test_per_cell_item_counts(kb):
    for cell, expected in EXPECTED_CELL_ITEMS.items():
        assert len(kb.items_in_cell(cell)) == expected, cell


def test_matches_canonical_closure_summary(kb):
    """Our computed totals agree with data/06 closure summary."""
    summary = kb.closure["summary"]
    assert len(kb.knowledge_items) == summary["knowledge_items"]
    assert len(kb.technical_relation_ids()) == summary["technical_source_relations"]
    assert len(kb.auxiliary_relation_ids()) == summary["auxiliary_relations"]
    assert len(kb.reserve_relation_ids) == summary["reserve_outside_cells"]
    assert len(kb.excluded_relation_ids) == summary["excluded_relations"]


def test_fails_closed_on_duplicate_id(kb):
    corrupt = copy.copy(kb)
    corrupt.knowledge_items = list(kb.knowledge_items) + [kb.knowledge_items[0]]
    results = {r.check_id: r for r in run_all_checks(corrupt)}
    assert not results["IC-02"].passed  # uniqueness must fail


def test_fails_closed_on_invalid_policy(kb):
    from dataclasses import replace

    corrupt = copy.copy(kb)
    bad = replace(kb.knowledge_items[0], generation_policy="TOTALLY_MADE_UP")
    corrupt.knowledge_items = [bad] + list(kb.knowledge_items[1:])
    results = {r.check_id: r for r in run_all_checks(corrupt)}
    assert not results["IC-12"].passed


def test_assert_integrity_raises_on_corruption(kb):
    from dataclasses import replace

    corrupt = copy.copy(kb)
    bad = replace(kb.knowledge_items[0], generation_policy="NOPE")
    corrupt.knowledge_items = [bad] + list(kb.knowledge_items[1:])
    with pytest.raises(IntegrityError):
        assert_integrity(corrupt)
