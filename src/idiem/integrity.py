"""Milestone 1 — integrity and closure checks.

Reproduces the known 2A.2 closure totals and fails closed on missing/duplicate
IDs or invalid policy enums. Every check logs a reason (CLAUDE.md: "Log reasons
for every blocked or gap state").
"""

from __future__ import annotations

from dataclasses import dataclass

from . import policies
from .loader import KnowledgeBase

# Expected closure totals — docs/04_ACCEPTANCE_CRITERIA.md (library integrity).
EXPECTED_TOTALS = {
    "source_relations_total": 292,
    "assigned_to_cells": 137,
    "technical_source_relations": 102,
    "auxiliary_relations": 35,
    "reserve": 150,
    "excluded": 5,
    "active_knowledge_items": 116,
    "source_documents": 29,
}

# Expected active knowledge items per cell — docs/04_ACCEPTANCE_CRITERIA.md.
EXPECTED_CELL_ITEMS = {
    "INFRA PÚBLICA RESILIENTE": 24,
    "INFRA HOSPITALARIA Y ASISTENCIAL": 6,
    "INFRA CRÍTICA TRANSPORTE": 0,
    "INFRA OPERACIÓN MINERA": 65,
    "LAB MINERO DIGITAL": 21,
}


@dataclass
class CheckResult:
    check_id: str
    passed: bool
    reason: str
    detail: object = None

    def __bool__(self) -> bool:  # pragma: no cover - trivial
        return self.passed


class IntegrityError(Exception):
    """Raised when a hard integrity invariant is violated (fail closed)."""


def run_all_checks(kb: KnowledgeBase) -> list[CheckResult]:
    """Run every integrity check and return per-check results (does not raise)."""
    checks: list[CheckResult] = []
    tech_rels = kb.technical_relation_ids()
    aux_rels = kb.auxiliary_relation_ids()
    reserve_rels = set(kb.reserve_relation_ids)
    excluded_rels = set(kb.excluded_relation_ids)

    def add(cid: str, passed: bool, reason: str, detail=None) -> None:
        checks.append(CheckResult(cid, passed, reason, detail))

    # IC-01 active knowledge items count
    n_items = len(kb.knowledge_items)
    add(
        "IC-01",
        n_items == EXPECTED_TOTALS["active_knowledge_items"],
        f"active_knowledge_items={n_items} (esperado {EXPECTED_TOTALS['active_knowledge_items']})",
        n_items,
    )

    # IC-02 knowledge_id uniqueness
    ids = [it.knowledge_id for it in kb.knowledge_items]
    dup = sorted({x for x in ids if ids.count(x) > 1})
    add("IC-02", not dup, f"knowledge_id duplicados: {dup or 'ninguno'}", dup)

    # IC-03 technical source relations
    add(
        "IC-03",
        len(tech_rels) == EXPECTED_TOTALS["technical_source_relations"],
        f"technical_source_relations={len(tech_rels)} (esperado 102)",
        len(tech_rels),
    )

    # IC-04 auxiliary relations
    add(
        "IC-04",
        len(aux_rels) == EXPECTED_TOTALS["auxiliary_relations"],
        f"auxiliary_relations={len(aux_rels)} (esperado 35)",
        len(aux_rels),
    )

    # IC-05 reserve
    add(
        "IC-05",
        len(reserve_rels) == EXPECTED_TOTALS["reserve"],
        f"reserve={len(reserve_rels)} (esperado 150)",
        len(reserve_rels),
    )

    # IC-06 excluded
    add(
        "IC-06",
        len(excluded_rels) == EXPECTED_TOTALS["excluded"],
        f"excluded={len(excluded_rels)} (esperado 5)",
        len(excluded_rels),
    )

    # IC-07 source documents
    add(
        "IC-07",
        len(kb.source_documents) == EXPECTED_TOTALS["source_documents"],
        f"source_documents={len(kb.source_documents)} (esperado 29)",
        len(kb.source_documents),
    )

    # IC-08 assigned to cells = technical + auxiliary
    assigned = len(tech_rels) + len(aux_rels)
    add(
        "IC-08",
        assigned == EXPECTED_TOTALS["assigned_to_cells"],
        f"assigned_to_cells={assigned} (esperado 137)",
        assigned,
    )

    # IC-09 total relations = technical + auxiliary + reserve + excluded
    total = len(tech_rels) + len(aux_rels) + len(reserve_rels) + len(excluded_rels)
    add(
        "IC-09",
        total == EXPECTED_TOTALS["source_relations_total"],
        f"source_relations_total={total} (esperado 292)",
        total,
    )

    # IC-10 partition: no overlap across technical / auxiliary / reserve / excluded
    overlaps = {
        "tech∩aux": tech_rels & aux_rels,
        "tech∩reserve": tech_rels & reserve_rels,
        "tech∩excluded": tech_rels & excluded_rels,
        "aux∩reserve": aux_rels & reserve_rels,
        "aux∩excluded": aux_rels & excluded_rels,
        "reserve∩excluded": reserve_rels & excluded_rels,
    }
    bad = {k: sorted(v) for k, v in overlaps.items() if v}
    add("IC-10", not bad, f"solapamientos de particion: {bad or 'ninguno'}", bad)

    # IC-11 per-cell active knowledge item counts
    cell_bad = {}
    for cell, expected in EXPECTED_CELL_ITEMS.items():
        got = len(kb.items_in_cell(cell))
        if got != expected:
            cell_bad[cell] = {"got": got, "expected": expected}
    add(
        "IC-11",
        not cell_bad,
        f"conteo por celda: {cell_bad or 'todos correctos'}",
        cell_bad,
    )

    # IC-12 generation_policy enum validity (fail closed on unknown policy)
    invalid_pol = sorted(
        {
            it.knowledge_id
            for it in kb.knowledge_items
            if not policies.is_valid_generation_policy(it.generation_policy)
        }
    )
    add(
        "IC-12",
        not invalid_pol,
        f"generation_policy invalida en: {invalid_pol or 'ninguno'}",
        invalid_pol,
    )

    # IC-13 auxiliary production_policy enum validity
    invalid_aux = sorted(
        {
            a.auxiliary_id
            for a in kb.auxiliary_evidence
            if a.production_policy not in policies.AUXILIARY_POLICIES
        }
    )
    add(
        "IC-13",
        not invalid_aux,
        f"production_policy auxiliar invalida en: {invalid_aux or 'ninguno'}",
        invalid_aux,
    )

    # IC-14 source coverage: every item source_relation_id resolves to a
    # knowledge_source row for that item, and item cell exists.
    known_cells = set(kb.cell_def_by_name)
    missing_cell = sorted(
        {it.knowledge_id for it in kb.knowledge_items if it.cell not in known_cells}
    )
    add(
        "IC-14",
        not missing_cell,
        f"items con celda desconocida: {missing_cell or 'ninguno'}",
        missing_cell,
    )

    # IC-15 excluded relations never appear as technical or auxiliary evidence
    leaked = sorted((tech_rels | aux_rels) & excluded_rels)
    add(
        "IC-15",
        not leaked,
        f"relaciones excluidas usadas como evidencia: {leaked or 'ninguna'}",
        leaked,
    )

    return checks


def assert_integrity(kb: KnowledgeBase) -> list[CheckResult]:
    """Run all checks; raise :class:`IntegrityError` if any fails (fail closed)."""
    results = run_all_checks(kb)
    failed = [r for r in results if not r.passed]
    if failed:
        lines = "\n".join(f"  [{r.check_id}] {r.reason}" for r in failed)
        raise IntegrityError(f"Fallaron {len(failed)} checks de integridad:\n{lines}")
    return results
