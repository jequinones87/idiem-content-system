"""Placeholder interfaces for future handoffs (FASE D–I of the roadmap).

CLAUDE.md rule 12 + 08_PROJECT_ROADMAP: build the factual/editorial engine now
and leave *interfaces* ready for design, assets and integrations — without
inventing or implementing those layers before their specific handoffs.

Everything here is a typed contract or fail-closed placeholder. There are NO
visual decisions (colors, fonts, templates), NO real image classification and
NO publishing logic in this module — those arrive with FASE D/E/F/H handoffs.

Domain separation (roadmap §11): Knowledge / Editorial / Planner produce the
approved brief; Visual / Assets / Integrations only *consume* approved output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Protocol, runtime_checkable

# =============================================================================
# FASE E — Image Library (contract only). Roadmap §6.
# =============================================================================

# asset_role distinguishes decoration from evidence. This distinction is a
# factual-integrity rule, not a visual one: an illustrative image must never be
# presented as proof that IDIEM executed a project (roadmap §6, principio crítico).
ASSET_ROLE_ILLUSTRATIVE = "illustrative"
ASSET_ROLE_PROJECT_EVIDENCE = "project_evidence"
ASSET_ROLES = frozenset({ASSET_ROLE_ILLUSTRATIVE, ASSET_ROLE_PROJECT_EVIDENCE})


@dataclass(frozen=True)
class ImageAsset:
    """Recommended image-library contract (roadmap §6). Not populated here.

    A future handoff delivers the real catalog. ``project_evidence`` assets must
    carry ``relation_ids`` linking them to verified relations; ``illustrative``
    assets may accompany content but prove nothing about IDIEM's involvement.
    """

    image_id: str
    file: str
    cells: tuple[str, ...] = field(default_factory=tuple)
    topics: tuple[str, ...] = field(default_factory=tuple)
    asset_type: str = "photography"
    asset_role: str = ASSET_ROLE_ILLUSTRATIVE
    orientation: str = "horizontal"
    people: bool = False
    project_identified: bool = False
    project_name: Optional[str] = None
    relation_ids: tuple[str, ...] = field(default_factory=tuple)
    approved_for_use: bool = False
    usage_notes: str = ""


@dataclass(frozen=True)
class AssetQuery:
    """A request for assets derived from an approved brief's ``visual_brief``.

    This is metadata only — it describes *what* imagery a piece would need. It
    performs no selection. Building the query never touches real files.
    """

    cell: str
    topics: tuple[str, ...] = field(default_factory=tuple)
    orientation: str = "horizontal"
    # If evidence-backed imagery is required, restrict to project_evidence assets
    # whose relation_ids intersect these. Empty => illustrative is acceptable.
    require_relation_ids: tuple[str, ...] = field(default_factory=tuple)
    desired_role: str = ASSET_ROLE_ILLUSTRATIVE


def build_asset_query(brief: dict) -> AssetQuery:
    """Derive an :class:`AssetQuery` from a content brief's visual brief.

    Pure metadata transformation; selects nothing. When the brief cites concrete
    project evidence, the query asks for evidence-backed imagery keyed by the
    brief's own relation_ids (never invents a project link).
    """
    relation_ids = tuple(brief.get("traceability", {}).get("relation_ids", []))
    is_project = brief.get("content_type") == "PROJECT_EVIDENCE"
    topics = tuple(
        t for t in [brief.get("core_problem_or_question")] if t
    )
    return AssetQuery(
        cell=brief.get("cell", ""),
        topics=topics,
        require_relation_ids=relation_ids if is_project else tuple(),
        desired_role=(
            ASSET_ROLE_PROJECT_EVIDENCE if is_project else ASSET_ROLE_ILLUSTRATIVE
        ),
    )


# =============================================================================
# FASE D — Design System (interface only). Roadmap §5.
# =============================================================================


@runtime_checkable
class DesignSystemProvider(Protocol):
    """Future design-system layer (tokens/typography/colors/grids/templates).

    Claude Code must NOT define any of these itself (roadmap §5/§12). A real
    provider, delivered by handoff, returns visual tokens keyed by format.
    """

    def tokens(self, fmt: str) -> dict:  # pragma: no cover
        ...

    def template_for(self, fmt: str, brief: dict) -> dict:  # pragma: no cover
        ...


# =============================================================================
# FASE E/F — Visual asset resolution + production (interface only).
# =============================================================================


@runtime_checkable
class VisualAssetProvider(Protocol):
    """Future assets layer. Resolves an :class:`AssetQuery` to catalog assets."""

    def resolve_assets(self, query: AssetQuery) -> list[ImageAsset]:  # pragma: no cover
        ...


# =============================================================================
# FASE H/I — Publishing / integrations (interface only). Roadmap §9/§10.
# =============================================================================


@runtime_checkable
class Publisher(Protocol):
    """Future publishing layer (Metricool / n8n). Consumes APPROVED briefs only.

    Roadmap §9: integrations consume approved output; they must never query the
    factual library to create content on their own.
    """

    def publish(self, approved_brief: dict) -> dict:  # pragma: no cover
        ...


# --- Explicit fail-closed placeholders --------------------------------------


class NotImplementedDesignSystem:
    def tokens(self, fmt: str) -> dict:
        raise NotImplementedError(
            "El Design System IDIEM llega en un handoff posterior (FASE D). "
            "No se definen colores/tipografías/templates aquí (roadmap §5/§12)."
        )

    def template_for(self, fmt: str, brief: dict) -> dict:
        raise NotImplementedError("Templates gráficos: handoff FASE D.")


class NotImplementedVisualProvider:
    def resolve_assets(self, query: AssetQuery) -> list[ImageAsset]:
        raise NotImplementedError(
            "La biblioteca de imágenes llega en un handoff posterior (FASE E). "
            "No se selecciona ni clasifica fotografía real aquí (roadmap §6/§12)."
        )


class NotImplementedPublisher:
    def publish(self, approved_brief: dict) -> dict:
        raise NotImplementedError(
            "La publicación/integración no se implementa en este milestone "
            "(FASE H/I, roadmap §9/§10; CLAUDE.md regla 12)."
        )
