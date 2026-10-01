"""Milestone 2 — deterministic retrieval layer (no LLM).

Filters knowledge items by cell/service/capability/application/policy/document/
relation/keyword and returns, for each hit, the item plus its source
traceability, policy, and *same-cell* compatible auxiliary evidence (GR-01/GR-05).
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field

from . import policies
from .loader import KnowledgeBase
from .models import AuxiliaryEvidence, KnowledgeItem, KnowledgeSource


def _norm(text: str) -> str:
    """Casefold + strip accents for accent-insensitive keyword matching."""
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return stripped.casefold()


@dataclass
class RetrievalHit:
    item: KnowledgeItem
    sources: list[KnowledgeSource]
    compatible_auxiliary: list[AuxiliaryEvidence] = field(default_factory=list)

    @property
    def policy(self) -> str:
        return self.item.generation_policy

    @property
    def relation_ids(self) -> list[str]:
        return list(self.item.source_relation_ids)

    @property
    def document_ids(self) -> list[str]:
        return list(self.item.document_ids)


@dataclass
class RetrievalQuery:
    cell: str | None = None
    service: str | None = None
    capability: str | None = None
    application: str | None = None
    policy: str | None = None
    document_id: str | None = None
    relation_id: str | None = None
    keyword: str | None = None


def _keyword_haystack(item: KnowledgeItem, sources: list[KnowledgeSource]) -> str:
    parts = [
        item.retrieval_key,
        item.service,
        item.capability or "",
        item.application or "",
    ]
    parts.extend(s.verified_evidence for s in sources)
    return _norm(" • ".join(parts))


class RetrievalEngine:
    """Deterministic filtering over the loaded knowledge base."""

    def __init__(self, kb: KnowledgeBase) -> None:
        self.kb = kb

    def _compatible_auxiliary(self, cell: str) -> list[AuxiliaryEvidence]:
        """Same-cell auxiliary evidence whose own policy permits use (GR-05)."""
        return [
            a
            for a in self.kb.auxiliary_in_cell(cell)
            if policies.auxiliary_is_usable(a.production_policy)
        ]

    def retrieve(self, query: RetrievalQuery) -> list[RetrievalHit]:
        # Start from the cell partition (GR-01) when a cell is given.
        if query.cell is not None:
            candidates = self.kb.items_in_cell(query.cell)
        else:
            candidates = list(self.kb.knowledge_items)

        kw = _norm(query.keyword) if query.keyword else None
        hits: list[RetrievalHit] = []

        for item in candidates:
            if query.service and _norm(query.service) not in _norm(item.service):
                continue
            if query.capability and _norm(query.capability) not in _norm(
                item.capability or ""
            ):
                continue
            if query.application and _norm(query.application) not in _norm(
                item.application or ""
            ):
                continue
            if query.policy and item.generation_policy != query.policy:
                continue
            if query.document_id and query.document_id not in item.document_ids:
                continue
            if query.relation_id and query.relation_id not in item.source_relation_ids:
                continue

            sources = self.kb.sources_for(item.knowledge_id)

            if kw and kw not in _keyword_haystack(item, sources):
                continue

            hits.append(
                RetrievalHit(
                    item=item,
                    sources=sources,
                    compatible_auxiliary=self._compatible_auxiliary(item.cell),
                )
            )

        return hits

    def retrieve_by_cell(self, cell: str) -> list[RetrievalHit]:
        return self.retrieve(RetrievalQuery(cell=cell))
