"""Milestone 6 — drafting adapter.

Generates hook/body/CTA *only after* a brief is factual and policy-compliant.
It never adds an IDIEM fact that is not already in the fact sheet, keeps the
status ``DRAFT`` and retains traceability (docs/03 M6).

The drafter sits behind :class:`DraftingAdapter` so a future LLM-based drafter
can plug in — but any such drafter must remain bounded to the brief's
``allowed_facts``. The default :class:`DeterministicDrafter` is bounded *by
construction*: it only recombines strings already present in the brief.
"""

from __future__ import annotations

import copy
import re
from typing import Protocol, runtime_checkable

from .brief import validate_brief

_KB_TOKEN = re.compile(r"KB-[A-Z]{3}-\d{3}")


@runtime_checkable
class DraftingAdapter(Protocol):
    def draft(self, brief: dict) -> dict:  # pragma: no cover
        """Return a ``draft_copy`` dict {hook, body, cta} for the brief."""
        ...


def _strip_tag(fact: str) -> str:
    """Remove a leading ``[KB-...]`` / ``[AUX-...]`` / ``[celda]`` tag for prose."""
    return re.sub(r"^\[[^\]]+\]\s*", "", fact).strip()


class DeterministicDrafter:
    """Fact-bounded, no-LLM drafter. Recombines only brief-supplied strings."""

    def draft(self, brief: dict) -> dict:
        if brief.get("status") == "CONTENT_GAP" or not brief.get("allowed_facts"):
            return {"hook": "", "body": "", "cta": ""}

        angle = brief.get("editorial_angle", "")
        facts = [_strip_tag(f) for f in brief["allowed_facts"]]
        matices = [_strip_tag(m) for m in brief.get("mandatory_matices", [])]

        # Hook: the editorial angle (a comms positioning reference, not an IDIEM
        # factual claim). Falls back to the first fact if no angle.
        hook = angle or facts[0]

        body_lines = [f"• {f}" for f in facts]
        if matices:
            body_lines.append("")
            body_lines.append("Notas de uso (respetar):")
            body_lines.extend(f"– {m}" for m in matices)
        body = "\n".join(body_lines)

        cta = "Conversemos sobre cómo el respaldo técnico de IDIEM aplica a tu proyecto."
        return {"hook": hook, "body": body, "cta": cta}


def assert_no_fact_leakage(brief: dict, draft: dict) -> None:
    """Fail closed if the draft references a knowledge_id outside the fact sheet."""
    allowed = set(brief.get("knowledge_ids", []))
    text = " ".join(draft.get(k, "") for k in ("hook", "body", "cta"))
    for token in _KB_TOKEN.findall(text):
        if token not in allowed:
            raise ValueError(
                f"Drafting introdujo un knowledge_id fuera del fact sheet: {token}"
            )


def apply_draft(brief: dict, drafter: DraftingAdapter | None = None) -> dict:
    """Return a copy of ``brief`` with ``draft_copy`` filled by ``drafter``.

    Preserves status (DRAFT stays DRAFT), keeps traceability, re-validates the
    schema and records the drafting step in QA notes. Human approval still
    pending (rule 10).
    """
    drafter = drafter or DeterministicDrafter()
    out = copy.deepcopy(brief)
    draft = drafter.draft(out)
    assert_no_fact_leakage(out, draft)
    out["draft_copy"] = draft
    note = "M6 drafting: copy generado desde allowed_facts (sin hechos nuevos)."
    if note not in out["qa"]["notes"]:
        out["qa"]["notes"].append(note)
    validate_brief(out)
    return out
