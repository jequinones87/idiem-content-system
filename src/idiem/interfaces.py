"""Placeholder interfaces for later handoffs (design/assets and publishing).

CLAUDE.md rule 12: do not implement publishing or design automation in the first
milestone. Rule: keep future visual/assets integration behind an interface.
These are typed contracts only — deliberately not implemented.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class VisualAssetProvider(Protocol):
    """Future design/asset layer. Selects/renders visuals from a visual_brief.

    Not implemented in this milestone. A real provider will consume the
    ``visual_brief`` block of a content brief and return asset references.
    """

    def resolve_assets(self, visual_brief: dict) -> list[dict]:  # pragma: no cover
        ...


@runtime_checkable
class Publisher(Protocol):
    """Future publishing layer (e.g. Metricool / n8n). Not implemented here."""

    def publish(self, brief: dict) -> dict:  # pragma: no cover
        ...


class NotImplementedVisualProvider:
    """Explicit fail-closed placeholder for the design/assets layer."""

    def resolve_assets(self, visual_brief: dict) -> list[dict]:
        raise NotImplementedError(
            "El layer de diseño/assets se entrega en un handoff posterior "
            "(CLAUDE.md regla 12)."
        )


class NotImplementedPublisher:
    """Explicit fail-closed placeholder for the publishing layer."""

    def publish(self, brief: dict) -> dict:
        raise NotImplementedError(
            "La publicación no se implementa en el primer milestone "
            "(CLAUDE.md regla 12)."
        )
