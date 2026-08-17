"""Milestone 3 — fact sheet engine.

Turns a cell (+ optional topic/goal/audience) into a policy-compliant fact
sheet: selected knowledge IDs, allowed facts, mandatory caveats, blocked
claims, content gaps and full source traceability. Generated *before* any copy.

Every fact traces to a knowledge_id and its source relation/document IDs. No
IDIEM fact is invented: allowed facts are the verified-evidence strings already
present in the canonical package, gated by each item's generation_policy.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import policies
from .cells import CellRules
from .loader import KnowledgeBase
from .retrieval import RetrievalEngine, RetrievalHit, RetrievalQuery


@dataclass
class FactSheet:
    cell: str
    topic: str | None
    goal: str | None
    audience: str | None
    is_content_gap: bool
    knowledge_ids: list[str] = field(default_factory=list)
    auxiliary_ids: list[str] = field(default_factory=list)
    allowed_facts: list[str] = field(default_factory=list)
    mandatory_matices: list[str] = field(default_factory=list)
    blocked_claims: list[str] = field(default_factory=list)
    content_gaps: list[str] = field(default_factory=list)
    relation_ids: list[str] = field(default_factory=list)
    document_ids: list[str] = field(default_factory=list)
    log: list[str] = field(default_factory=list)


def _dedupe(seq: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _facts_from_hit(hit: RetrievalHit, sheet: FactSheet) -> None:
    """Derive allowed facts / caveats / blocked claims for one item by policy."""
    item = hit.item
    kid = item.knowledge_id
    policy = item.generation_policy

    if policies.is_name_only(policy):
        # GR-03: may be named, never expanded or equated to another service.
        label = item.capability or item.service
        sheet.allowed_facts.append(
            f"[{kid}] IDIEM cuenta con «{label}» (mencionar por nombre)."
        )
        sheet.mandatory_matices.append(
            f"[{kid}] NAME_ONLY_DO_NOT_EXPAND: no explicar, no describir método/entregable, "
            f"no equiparar «{label}» a otro servicio."
        )
        sheet.log.append(f"{kid}: NAME_ONLY -> solo mención, sin expansión.")
        return

    # Expandable policies: state the verified evidence (technical core).
    for src in hit.sources:
        if src.verified_evidence:
            sheet.allowed_facts.append(f"[{kid}] {src.verified_evidence}")

    if policies.requires_matiz(policy):
        sheet.mandatory_matices.append(
            f"[{kid}] USE_WITH_MATIZ: {item.usage_instruction}"
        )
        sheet.log.append(f"{kid}: USE_WITH_MATIZ -> matiz obligatorio agregado.")

    if policies.blocks_claims(policy):
        # GR-04: technical core allowed, attached rankings/superlatives blocked.
        for tmpl in policies.BLOCKED_CLAIM_TEMPLATES:
            sheet.blocked_claims.append(f"[{kid}] {tmpl}")
        sheet.log.append(f"{kid}: BLOCK_CLAIMS -> rankings/superlativos bloqueados.")


def build_fact_sheet(
    kb: KnowledgeBase,
    cell: str,
    *,
    topic: str | None = None,
    goal: str | None = None,
    audience: str | None = None,
) -> FactSheet:
    engine = RetrievalEngine(kb)
    rules = CellRules(kb)

    sheet = FactSheet(
        cell=cell,
        topic=topic,
        goal=goal,
        audience=audience,
        is_content_gap=False,
    )

    # 1) Cell-level content gap (e.g. Transporte -> Metro/EFE only, 0 items).
    gap = rules.technical_gap(cell)
    if gap.is_gap:
        sheet.is_content_gap = True
        sheet.content_gaps.append(gap.reason or f"Sin evidencia técnica activa en {cell}.")
        sheet.log.append(f"CONTENT_GAP en {cell}: {gap.reason}")
        return sheet

    # 2) Retrieve same-cell items (optionally narrowed by topic keyword).
    query = RetrievalQuery(cell=cell, keyword=topic)
    hits = engine.retrieve(query)

    if not hits:
        # The cell has evidence, but nothing matched the requested topic.
        sheet.is_content_gap = True
        sheet.content_gaps.append(
            f"La célula '{cell}' tiene evidencia activa, pero ningún knowledge_item "
            f"coincide con el tema solicitado ('{topic}'). No se rellena con otra célula."
        )
        sheet.log.append(f"CONTENT_GAP temático en {cell} para topic='{topic}'.")
        return sheet

    # 3) Derive facts per item, respecting policy.
    priority = rules.priority_note(cell)
    if priority:
        sheet.mandatory_matices.append(f"[celda] {priority}")

    for hit in hits:
        sheet.knowledge_ids.append(hit.item.knowledge_id)
        sheet.relation_ids.extend(hit.item.source_relation_ids)
        sheet.document_ids.extend(hit.item.document_ids)
        _facts_from_hit(hit, sheet)

    # 4) Compatible auxiliary evidence (same cell, usable policy). GR-05.
    for aux in engine._compatible_auxiliary(cell):
        sheet.auxiliary_ids.append(aux.auxiliary_id)
        sheet.relation_ids.append(aux.relation_id)
        sheet.document_ids.append(aux.document_id)
        if policies.auxiliary_needs_validity_check(aux.production_policy):
            sheet.mandatory_matices.append(
                f"[{aux.auxiliary_id}] Verificar vigencia antes de publicar "
                f"({aux.production_policy}, GR-13)."
            )

    # 5) Normalize.
    sheet.knowledge_ids = _dedupe(sheet.knowledge_ids)
    sheet.auxiliary_ids = _dedupe(sheet.auxiliary_ids)
    sheet.allowed_facts = _dedupe(sheet.allowed_facts)
    sheet.mandatory_matices = _dedupe(sheet.mandatory_matices)
    sheet.blocked_claims = _dedupe(sheet.blocked_claims)
    sheet.relation_ids = _dedupe(sheet.relation_ids)
    sheet.document_ids = _dedupe(sheet.document_ids)
    return sheet
