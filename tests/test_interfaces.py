"""Future-handoff interfaces (roadmap FASE D–I): contracts + fail-closed.

These verify the interfaces are *prepared* but not implemented, and that the
asset query is a pure metadata transformation that selects nothing.
"""

import pytest

from idiem.brief import build_brief
from idiem.interfaces import (
    ASSET_ROLE_ILLUSTRATIVE,
    ASSET_ROLE_PROJECT_EVIDENCE,
    AssetQuery,
    NotImplementedDesignSystem,
    NotImplementedPublisher,
    NotImplementedVisualProvider,
    build_asset_query,
)


def test_design_system_is_not_implemented(kb):
    with pytest.raises(NotImplementedError):
        NotImplementedDesignSystem().tokens("STATIC")


def test_visual_provider_is_not_implemented(kb):
    with pytest.raises(NotImplementedError):
        NotImplementedVisualProvider().resolve_assets(AssetQuery(cell="X"))


def test_publisher_is_not_implemented(kb):
    with pytest.raises(NotImplementedError):
        NotImplementedPublisher().publish({})


def test_asset_query_from_technical_brief_is_illustrative(kb):
    brief = build_brief(kb, "INFRA PÚBLICA RESILIENTE")
    q = build_asset_query(brief)
    assert q.cell == "INFRA PÚBLICA RESILIENTE"
    assert q.desired_role == ASSET_ROLE_ILLUSTRATIVE
    # A non-evidence piece must not demand evidence-linked imagery.
    assert q.require_relation_ids == tuple()


def test_asset_query_for_project_evidence_requires_relation_ids(kb):
    brief = build_brief(
        kb, "INFRA OPERACIÓN MINERA", content_type="PROJECT_EVIDENCE"
    )
    q = build_asset_query(brief)
    assert q.desired_role == ASSET_ROLE_PROJECT_EVIDENCE
    # Evidence imagery is keyed by the brief's own relation_ids (never invented).
    assert set(q.require_relation_ids) == set(brief["traceability"]["relation_ids"])


def test_asset_query_selects_nothing(kb):
    # build_asset_query returns metadata only; it has no assets to select.
    brief = build_brief(kb, "LAB MINERO DIGITAL")
    q = build_asset_query(brief)
    assert not hasattr(q, "assets")
