"""Milestone 1 — canonical data loader.

Loads the read-only 2A.2 package under ``data/`` into typed, indexed objects.
Never writes to ``data/``. Generated state belongs in ``output/``.
"""

from __future__ import annotations

import json
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Optional

from .models import (
    AuxiliaryEvidence,
    CellDefinition,
    ExcludedRelation,
    GenerationRule,
    KnowledgeItem,
    KnowledgeSource,
    ReserveRelation,
    SourceDocument,
)

# Repo layout: <root>/src/idiem/loader.py  ->  root is parents[2]
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
CONFIG_DIR = REPO_ROOT / "config"
SCHEMA_DIR = REPO_ROOT / "schemas"

PRODUCTION_BASE = "04_base_produccion_IDIEM_2A2.json"
EDITORIAL_RULES = "05_reglas_editoriales_generacion_IDIEM_2A2.json"
CLOSURE_VALIDATION = "06_validacion_cierre_biblioteca_2A2.json"
CELL_RULES = "cell_rules.json"
EDITORIAL_STYLE = "editorial_style.json"
SUBTHEMES = "subthemes.json"
EVIDENCE_EXTENSION = "ext_2A3/evidence_2A3.json"


def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s or "")


def load_editorial_style() -> dict:
    """Load the external, configurable editorial style guide (config/)."""
    with (CONFIG_DIR / EDITORIAL_STYLE).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_subthemes() -> dict:
    """Load the external, configurable subtheme axis (Fase D). Empty if absent."""
    path = CONFIG_DIR / SUBTHEMES
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _tuple(value) -> tuple:
    if value is None:
        return tuple()
    if isinstance(value, (list, tuple)):
        return tuple(value)
    return (value,)


class KnowledgeBase:
    """In-memory, indexed view of the canonical production base."""

    def __init__(
        self,
        *,
        metadata: dict,
        cell_definitions: list[CellDefinition],
        generation_rules: list[GenerationRule],
        knowledge_items: list[KnowledgeItem],
        knowledge_sources: list[KnowledgeSource],
        auxiliary_evidence: list[AuxiliaryEvidence],
        reserve: list[ReserveRelation],
        excluded: list[ExcludedRelation],
        source_documents: list[SourceDocument],
        editorial_rules: dict,
        cell_rules: dict,
        closure: dict,
        extension: Optional[dict] = None,
    ) -> None:
        self.metadata = metadata
        self.cell_definitions = cell_definitions
        self.generation_rules = generation_rules
        self.knowledge_items = knowledge_items
        self.knowledge_sources = knowledge_sources
        self.auxiliary_evidence = auxiliary_evidence
        self.reserve = reserve
        self.excluded = excluded
        self.source_documents = source_documents
        self.editorial_rules = editorial_rules
        self.cell_rules = cell_rules
        self.closure = closure

        # --- indexes ---------------------------------------------------------
        self.item_by_id: dict[str, KnowledgeItem] = {
            it.knowledge_id: it for it in knowledge_items
        }
        self.cell_def_by_name: dict[str, CellDefinition] = {
            c.cell: c for c in cell_definitions
        }
        self.aux_by_id: dict[str, AuxiliaryEvidence] = {
            a.auxiliary_id: a for a in auxiliary_evidence
        }
        self.doc_by_id: dict[str, SourceDocument] = {
            d.document_id: d for d in source_documents
        }
        self.excluded_relation_ids: frozenset[str] = frozenset(
            e.relation_id for e in excluded
        )
        self.reserve_relation_ids: frozenset[str] = frozenset(
            r.relation_id for r in reserve
        )

        self._sources_by_item: dict[str, list[KnowledgeSource]] = {}
        for s in knowledge_sources:
            self._sources_by_item.setdefault(s.knowledge_id, []).append(s)

        self._items_by_cell: dict[str, list[KnowledgeItem]] = {}
        for it in knowledge_items:
            self._items_by_cell.setdefault(it.cell, []).append(it)

        self._aux_by_cell: dict[str, list[AuxiliaryEvidence]] = {}
        for a in auxiliary_evidence:
            self._aux_by_cell.setdefault(a.cell, []).append(a)

        # --- 2A.3 evidence extension (additive; never mutates 2A.2) -----------
        self.extension = extension or {}
        doc_by_filename = {
            _nfc(d.file_name): d.document_id for d in source_documents
        }
        self._enrichment_by_service: dict[tuple[str, str], list[dict]] = defaultdict(list)
        self._blocked_source_by_service: dict[tuple[str, str], list[dict]] = defaultdict(list)
        self._enrichment_by_id: dict[str, dict] = {}
        for rec in self.extension.get("enrichment", []):
            rec = {**rec, "document_id": doc_by_filename.get(_nfc(rec.get("file_name", "")))}
            self._enrichment_by_service[(rec["cell"], rec["service"])].append(rec)
            self._enrichment_by_id[rec["enrichment_id"]] = rec
        for rec in self.extension.get("blocked_source", []):
            self._blocked_source_by_service[(rec["cell"], rec["service"])].append(rec)

        # --- 2A.3 audited policy overrides (additive; never mutates 2A.2) ------
        # A change of generation_policy on a 2A.2 knowledge_id, authorized by the
        # source of truth (e.g. NAME_ONLY -> technical core). Indexed by id.
        self._policy_override_by_id: dict[str, dict] = {}
        for rec in self.extension.get("policy_overrides", []):
            rec = {**rec, "document_id": doc_by_filename.get(_nfc(rec.get("file_name", "")))}
            self._policy_override_by_id[rec["knowledge_id"]] = rec

    def enrichment_for(self, cell: str, service: str) -> list[dict]:
        return list(self._enrichment_by_service.get((cell, service), []))

    def enrichment_by_id(self, enrichment_id: str) -> Optional[dict]:
        return self._enrichment_by_id.get(enrichment_id)

    def blocked_source_for(self, cell: str, service: str) -> list[dict]:
        return list(self._blocked_source_by_service.get((cell, service), []))

    def policy_override_for(self, knowledge_id: str) -> Optional[dict]:
        return self._policy_override_by_id.get(knowledge_id)

    # --- convenience accessors ----------------------------------------------
    def cells(self) -> list[str]:
        return [c.cell for c in self.cell_definitions]

    def items_in_cell(self, cell: str) -> list[KnowledgeItem]:
        return list(self._items_by_cell.get(cell, []))

    def auxiliary_in_cell(self, cell: str) -> list[AuxiliaryEvidence]:
        return list(self._aux_by_cell.get(cell, []))

    def sources_for(self, knowledge_id: str) -> list[KnowledgeSource]:
        return list(self._sources_by_item.get(knowledge_id, []))

    def technical_relation_ids(self) -> set[str]:
        rels: set[str] = set()
        for it in self.knowledge_items:
            rels.update(it.source_relation_ids)
        return rels

    def auxiliary_relation_ids(self) -> set[str]:
        return {a.relation_id for a in self.auxiliary_evidence}


def _parse_cell_definition(d: dict) -> CellDefinition:
    return CellDefinition(
        cell=d["cell"],
        definition=d["definition"],
        rules=_tuple(d.get("rules")),
        communication_reference_2026=d.get("communication_reference_2026", ""),
        active_knowledge_items=int(d.get("active_knowledge_items", 0)),
        auxiliary_items=int(d.get("auxiliary_items", 0)),
    )


def _parse_item(d: dict) -> KnowledgeItem:
    return KnowledgeItem(
        knowledge_id=d["knowledge_id"],
        cell=d["cell"],
        service=d["service"],
        capability=d.get("capability"),
        application=d.get("application"),
        generation_policy=d["generation_policy"],
        usage_instruction=d.get("usage_instruction", ""),
        taxonomy_statuses=_tuple(d.get("taxonomy_statuses")),
        notes=_tuple(d.get("notes")),
        source_relation_ids=_tuple(d.get("source_relation_ids")),
        document_ids=_tuple(d.get("document_ids")),
        retrieval_key=d.get("retrieval_key", ""),
    )


def _parse_source(d: dict) -> KnowledgeSource:
    return KnowledgeSource(
        knowledge_id=d["knowledge_id"],
        relation_id=d["relation_id"],
        document_id=d.get("document_id", ""),
        file_name=d.get("file_name", ""),
        page=str(d.get("page", "")),
        section=d.get("section"),
        verified_evidence=d.get("verified_evidence", ""),
        audit_result=d.get("audit_result"),
        audit_use_status=d.get("audit_use_status"),
        document_group=d.get("document_group"),
        independent_source=d.get("independent_source"),
    )


def _parse_aux(d: dict) -> AuxiliaryEvidence:
    return AuxiliaryEvidence(
        auxiliary_id=d["auxiliary_id"],
        cell=d["cell"],
        type=d.get("type", ""),
        production_policy=d["production_policy"],
        usage_instruction=d.get("usage_instruction", ""),
        relation_id=d["relation_id"],
        document_id=d.get("document_id", ""),
        source_service=d.get("source_service"),
        source_capability=d.get("source_capability"),
        source_application=d.get("source_application"),
        note=d.get("note"),
        verified_evidence=d.get("verified_evidence", ""),
    )


def _parse_reserve(d: dict) -> ReserveRelation:
    return ReserveRelation(
        relation_id=d["relation_id"],
        production_policy=d["production_policy"],
        usage_instruction=d.get("usage_instruction", ""),
        document_id=d.get("document_id"),
        verified_evidence=d.get("verified_evidence", ""),
    )


def _parse_excluded(d: dict) -> ExcludedRelation:
    return ExcludedRelation(
        relation_id=d["relation_id"],
        production_policy=d["production_policy"],
        document_id=d.get("document_id"),
        audit_reason=d.get("audit_reason", ""),
        verified_evidence=d.get("verified_evidence", ""),
    )


def _parse_document(d: dict) -> SourceDocument:
    return SourceDocument(
        document_id=d["document_id"],
        file_name=d.get("file_name", ""),
        relation_ids=_tuple(d.get("relation_ids")),
        relation_count=int(d.get("relation_count", 0)),
        cells_2A2=_tuple(d.get("cells_2A2")),
    )


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_knowledge_base(data_dir: Optional[Path] = None) -> KnowledgeBase:
    """Load the full canonical package into an indexed :class:`KnowledgeBase`."""
    data_dir = Path(data_dir) if data_dir else DATA_DIR

    base = _load_json(data_dir / PRODUCTION_BASE)
    editorial = _load_json(data_dir / EDITORIAL_RULES)
    closure = _load_json(data_dir / CLOSURE_VALIDATION)
    cell_rules = _load_json(CONFIG_DIR / CELL_RULES)

    ext_path = data_dir / EVIDENCE_EXTENSION
    extension = _load_json(ext_path) if ext_path.exists() else {}

    return KnowledgeBase(
        metadata=base["metadata"],
        cell_definitions=[_parse_cell_definition(x) for x in base["cell_definitions"]],
        generation_rules=[
            GenerationRule(rule_id=r["rule_id"], rule=r["rule"])
            for r in base["generation_rules"]
        ],
        knowledge_items=[_parse_item(x) for x in base["knowledge_items"]],
        knowledge_sources=[_parse_source(x) for x in base["knowledge_sources"]],
        auxiliary_evidence=[_parse_aux(x) for x in base["auxiliary_evidence"]],
        reserve=[_parse_reserve(x) for x in base["reserve_outside_prioritized_cells"]],
        excluded=[_parse_excluded(x) for x in base["excluded_relations"]],
        source_documents=[_parse_document(x) for x in base["source_documents"]],
        editorial_rules=editorial,
        cell_rules=cell_rules,
        closure=closure,
        extension=extension,
    )
