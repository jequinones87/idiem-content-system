"""Cell-rule engine backed by the external, configurable ``config/cell_rules.json``.

CLAUDE.md rule 11: cell rules must stay external/configurable so the team can
adjust definitions without code rewrites. This module reads that config and the
canonical cell definitions; it holds no hard-coded cell policy of its own.
"""

from __future__ import annotations

from dataclasses import dataclass

from .loader import KnowledgeBase


@dataclass
class GapDecision:
    is_gap: bool
    reason: str | None = None


class CellRules:
    def __init__(self, kb: KnowledgeBase) -> None:
        self.kb = kb
        self.config = kb.cell_rules
        self._restricted = self.config.get("restricted_cells", {})
        self._priority = self.config.get("priority_overrides", [])

    def known_cells(self) -> list[str]:
        return list(self.config.get("cells", self.kb.cells()))

    def is_restricted(self, cell: str) -> bool:
        return cell in self._restricted

    def technical_gap(self, cell: str) -> GapDecision:
        """Decide whether a *technical* request for ``cell`` is a CONTENT_GAP.

        Driven by config + live library counts, never hard-coded. A restricted
        cell (e.g. Transporte -> Metro/EFE only) with zero active technical
        items yields CONTENT_GAP (Test A).
        """
        active = len(self.kb.items_in_cell(cell))
        if active > 0:
            return GapDecision(is_gap=False)

        rule = self._restricted.get(cell)
        if rule is not None:
            reason = rule.get(
                "gap_reason",
                f"Sin knowledge_items tecnicos activos para la celda restringida {cell}.",
            )
            return GapDecision(is_gap=True, reason=reason)

        # No active items and not a documented restriction: still a gap, but
        # flagged generically (fail closed).
        return GapDecision(
            is_gap=True,
            reason=f"La celda '{cell}' no tiene knowledge_items tecnicos activos en la biblioteca actual.",
        )

    def priority_note(self, cell: str) -> str | None:
        """Return a human-readable priority note if ``cell`` participates in one."""
        for rule in self._priority:
            if rule.get("prefer") == cell or rule.get("over") == cell:
                return (
                    f"{rule.get('prefer')} tiene prioridad sobre {rule.get('over')} "
                    f"cuando el proyecto es '{rule.get('when_project_is')}' "
                    f"({rule.get('source_rule')})."
                )
        return None
