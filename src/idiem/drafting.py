"""Milestone 6 — drafting adapter.

Generates hook/body/CTA *only after* a brief is factual and policy-compliant.
It never adds an IDIEM fact that is not already in the fact sheet, keeps the
status ``DRAFT`` and retains traceability (docs/03 M6).

Two drafting paths, same guardrails:

- :class:`DeterministicDrafter` — no credentials. Recombines the brief's own
  strings into a fact skeleton (an internal working artifact for a human/LLM to
  rewrite). Bounded by construction.
- Publish-intended copy — :class:`LLMDrafter` (credential-agnostic, takes a
  ``complete`` callable) for automated runs, or :func:`ingest_draft` for
  agent-assisted drafting written in-session on the user's subscription (no API
  key). Both enforce :func:`assert_no_fact_leakage` (no foreign knowledge_id)
  and :func:`assert_no_blocked_claim_terms` (no rankings/superlatives, GR-04),
  keep status ``DRAFT`` and retain traceability.

Any drafter must remain bounded to the brief's ``allowed_facts``; the bounded
spec is produced by :func:`build_drafting_request`.
"""

from __future__ import annotations

import copy
import json
import re
from dataclasses import asdict, dataclass, field
from typing import Callable, Protocol, runtime_checkable

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


# ---------------------------------------------------------------------------
# Bounded drafting request + publish-intended copy path (agent- or LLM-drafted)
# ---------------------------------------------------------------------------

# Base superlatives/rankings that are never publishable as IDIEM claims (GR-04),
# even when they appear inside source verified_evidence.
_BASE_FORBIDDEN_TERMS = (
    "único", "unico", "única", "unica",
    "el más grande del mundo", "el mas grande del mundo",
    "el mayor del mundo", "líder mundial", "lider mundial",
    "el mejor del mundo", "primero del mundo", "world ranking",
    "tercero más grande a nivel mundial", "tercero mas grande a nivel mundial",
    "uno de los tres", "el más grande de", "el mas grande de",
)

_QUOTED = re.compile(r"['\"“”«»]([^'\"“”«»]{2,60})['\"“”«»]")

DRAFTING_INSTRUCTIONS = (
    "Redacta un post de LinkedIn en voz institucional IDIEM (español) siguiendo la "
    "guía editorial (campo 'style'). FORMA: estructura hook → problema → solución "
    "IDIEM con detalle técnico → impacto → CTA; longitud objetivo del estilo "
    "(~110-170 palabras, 4-5 párrafos); emojis presentes y temáticos (1-4 por párrafo según pertinencia); termina con un "
    "bloque de hashtags (usa 'recommended_hashtags', 4-6, incluyendo #IDIEM) y marca "
    "1-3 términos clave como hashtag inline. "
    "REGLAS FACTUALES ESTRICTAS: (1) usa ÚNICAMENTE la información de allowed_facts; "
    "no agregues servicios, cifras, clientes, proyectos ni resultados que no estén "
    "ahí. (2) Respeta cada nota en mandatory_matices. (3) NUNCA publiques los "
    "blocked_claims ni forbidden_terms (rankings, superlativos, exclusividades, "
    "primacías mundiales), aunque aparezcan en la evidencia. (4) No expandas términos "
    "marcados como 'mencionar por nombre'. (5) Si la evidencia no alcanza la longitud "
    "objetivo, escribe un post más corto y honesto; no rellenes. (6) Devuelve SOLO un "
    "JSON válido: {\"hook\": str, \"body\": str, \"cta\": str} (el body incluye el "
    "bloque de hashtags al final)."
)


@dataclass
class DraftingRequest:
    """The bounded spec any drafter (agent or LLM) must obey for one brief."""

    content_id: str
    cell: str
    editorial_angle: str
    content_type: str
    recommended_format: str
    knowledge_ids: list[str]
    allowed_facts: list[str]
    mandatory_matices: list[str]
    blocked_claims: list[str]
    forbidden_terms: list[str]
    recommended_hashtags: list[str] = field(default_factory=list)
    style: dict = field(default_factory=dict)
    instructions: str = DRAFTING_INSTRUCTIONS

    def to_dict(self) -> dict:
        return asdict(self)


def forbidden_terms(brief: dict) -> list[str]:
    """Terms that must not appear in publish-intended copy for this brief.

    Base superlatives plus any single-quoted phrase surfaced inside the brief's
    blocked_claims (e.g. 'único', 'el más grande del mundo').
    """
    terms = {t.lower() for t in _BASE_FORBIDDEN_TERMS}
    for claim in brief.get("blocked_claims", []):
        for m in _QUOTED.findall(claim):
            terms.add(m.strip().lower())
    return sorted(terms)


def recommended_hashtags(cell: str, style: dict) -> list[str]:
    """Closing-block hashtags for a cell: always-tags + the cell's vocabulary."""
    tags = list(style.get("hashtags", {}).get("always", []))
    vocab = style.get("hashtags", {}).get("vocabulary_by_cell", {}).get(cell, [])
    for t in vocab:
        if t not in tags:
            tags.append(t)
    cap = style.get("hashtags", {}).get("closing_block", {}).get("max", 6)
    return tags[:cap]


def build_drafting_request(brief: dict, *, style: dict | None = None) -> DraftingRequest:
    """Derive the bounded drafting spec (incl. editorial style) from a brief."""
    if style is None:
        from .loader import load_editorial_style

        style = load_editorial_style()
    cell = brief.get("cell", "")
    return DraftingRequest(
        content_id=brief.get("content_id", ""),
        cell=cell,
        editorial_angle=brief.get("editorial_angle", ""),
        content_type=brief.get("content_type", ""),
        recommended_format=brief.get("recommended_format", "STATIC"),
        knowledge_ids=list(brief.get("knowledge_ids", [])),
        allowed_facts=[_strip_tag(f) for f in brief.get("allowed_facts", [])],
        mandatory_matices=[_strip_tag(m) for m in brief.get("mandatory_matices", [])],
        blocked_claims=[_strip_tag(c) for c in brief.get("blocked_claims", [])],
        forbidden_terms=forbidden_terms(brief),
        recommended_hashtags=recommended_hashtags(cell, style),
        style=style,
    )


def render_drafting_prompt(req: DraftingRequest) -> str:
    """Render the bounded request as a text prompt for an LLM drafter."""
    payload = req.to_dict()
    return (
        f"{req.instructions}\n\n"
        f"ENCARGO (JSON de entrada):\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n"
    )


def assert_no_blocked_claim_terms(brief: dict, draft: dict) -> None:
    """Fail closed if publish-intended copy contains a blocked/forbidden term."""
    text = " ".join(draft.get(k, "") for k in ("hook", "body", "cta")).lower()
    for term in forbidden_terms(brief):
        if term and term in text:
            raise ValueError(
                f"El copy contiene un término bloqueado (GR-04): {term!r}"
            )


def _parse_copy(raw: str) -> dict:
    """Parse an LLM response into {hook, body, cta}. Fails closed on bad output."""
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        data = json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"Respuesta de drafting no es JSON válido: {exc}") from exc
    missing = {"hook", "body", "cta"} - set(data)
    if missing:
        raise ValueError(f"Faltan campos en el copy: {sorted(missing)}")
    return {k: str(data[k]) for k in ("hook", "body", "cta")}


class LLMDrafter:
    """Credential-agnostic LLM drafter.

    Takes a ``complete`` callable (str prompt -> str response). In automated mode
    pass an Anthropic client wrapper; in agent-assisted mode the copy is produced
    in-session and fed through :func:`ingest_draft` instead. Either way the output
    is validated against fact leakage and blocked terms before use.
    """

    def __init__(self, complete: Callable[[str], str]) -> None:
        self._complete = complete

    def draft(self, brief: dict) -> dict:
        if brief.get("status") == "CONTENT_GAP" or not brief.get("allowed_facts"):
            return {"hook": "", "body": "", "cta": ""}
        req = build_drafting_request(brief)
        raw = self._complete(render_drafting_prompt(req))
        draft = _parse_copy(raw)
        assert_no_fact_leakage(brief, draft)
        assert_no_blocked_claim_terms(brief, draft)
        return draft


def ingest_draft(brief: dict, copy_dict: dict) -> dict:
    """Validate externally-authored publish copy and write it into the brief.

    Used for agent-assisted drafting (copy written in-session on the user's
    subscription, no API key). Enforces both guards, keeps status DRAFT and
    re-validates the schema.
    """
    clean = {k: str(copy_dict.get(k, "")) for k in ("hook", "body", "cta")}
    assert_no_fact_leakage(brief, clean)
    assert_no_blocked_claim_terms(brief, clean)
    out = copy.deepcopy(brief)
    out["draft_copy"] = clean
    note = "M6 drafting: copy publicable ingerido y validado (sin fugas ni claims bloqueados)."
    if note not in out["qa"]["notes"]:
        out["qa"]["notes"].append(note)
    validate_brief(out)
    return out


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
