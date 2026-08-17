"""Typed models for the canonical IDIEM 2A.2 knowledge package.

Dataclasses mirror the JSON shapes documented in ``docs/02_DATA_CONTRACT.md``.
They are read-only value objects; nothing here mutates ``data/``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class CellDefinition:
    cell: str
    definition: str
    rules: tuple[str, ...]
    communication_reference_2026: str
    active_knowledge_items: int
    auxiliary_items: int


@dataclass(frozen=True)
class GenerationRule:
    rule_id: str
    rule: str


@dataclass(frozen=True)
class KnowledgeItem:
    knowledge_id: str
    cell: str
    service: str
    capability: Optional[str]
    application: Optional[str]
    generation_policy: str
    usage_instruction: str
    taxonomy_statuses: tuple[str, ...]
    notes: tuple[str, ...]
    source_relation_ids: tuple[str, ...]
    document_ids: tuple[str, ...]
    retrieval_key: str


@dataclass(frozen=True)
class KnowledgeSource:
    """A (knowledge_id, relation_id) evidence row with verified evidence text."""

    knowledge_id: str
    relation_id: str
    document_id: str
    file_name: str
    page: str
    section: Optional[str]
    verified_evidence: str
    audit_result: Optional[str]
    audit_use_status: Optional[str]
    document_group: Optional[str]
    independent_source: Optional[str]


@dataclass(frozen=True)
class AuxiliaryEvidence:
    auxiliary_id: str
    cell: str
    type: str
    production_policy: str
    usage_instruction: str
    relation_id: str
    document_id: str
    source_service: Optional[str]
    source_capability: Optional[str]
    source_application: Optional[str]
    note: Optional[str]
    verified_evidence: str


@dataclass(frozen=True)
class ReserveRelation:
    relation_id: str
    production_policy: str
    usage_instruction: str
    document_id: Optional[str]
    verified_evidence: str


@dataclass(frozen=True)
class ExcludedRelation:
    relation_id: str
    production_policy: str
    document_id: Optional[str]
    audit_reason: str
    verified_evidence: str


@dataclass(frozen=True)
class SourceDocument:
    document_id: str
    file_name: str
    relation_ids: tuple[str, ...]
    relation_count: int
    cells_2A2: tuple[str, ...] = field(default_factory=tuple)
