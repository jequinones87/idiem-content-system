"""Graphic brief — the structured design spec derived from an approved post.

The graphic is a COMPLEMENT to the caption, not a copy of it: it carries a short
visual headline (a claim), a few key points, a format (static/carousel), and —
when a photo fits — a photo query for the Image Library. Everything is bounded to
the post's approved copy and allowed facts, and inherits the same blocked terms,
so a superlative can never reach the graphic either.

The visual language (palette, templates) is NOT decided here — that arrives with
the Design System handoff. This only produces the brief that feeds it.
"""

from __future__ import annotations

import json
import re
from collections import Counter

from .drafting import forbidden_terms
from .loader import CONFIG_DIR

_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF←-⇿⬀-⯿️]"
)
_HASHTAG = re.compile(r"#\w+")


def _load_concept_dict() -> dict:
    p = CONFIG_DIR / "photo_library" / "concept_dictionary.json"
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _load_graphic_rules() -> dict:
    p = CONFIG_DIR / "graphic_rules.json"
    if not p.exists():
        return {
            "carousel_suggest_points": 7,
            "carousel_viable_points": 4,
            "photo_entornos": ["mina", "obra", "terreno", "laboratorio", "faena"],
        }
    with p.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _subtheme_photo_hint(concept_dict: dict) -> dict[str, tuple[str, str]]:
    """subtema -> (disciplina, entorno), inferred from the concept dictionary."""
    acc: dict[str, list[tuple[str, str]]] = {}
    for c in concept_dict.get("concepts", {}).values():
        for st in c.get("subtemas", []):
            acc.setdefault(st, []).append((c.get("disciplina", ""), c.get("entorno", "")))
    hint: dict[str, tuple[str, str]] = {}
    for st, pairs in acc.items():
        disc = Counter(d for d, _ in pairs).most_common(1)[0][0]
        ent = Counter(e for _, e in pairs).most_common(1)[0][0]
        hint[st] = (disc, ent)
    return hint


def _clean(text: str) -> str:
    text = _HASHTAG.sub("", text)
    text = _EMOJI.sub("", text)
    return re.sub(r"\s+", " ", text).strip(" ·—-:.,¿?¡!").strip()


def _has_forbidden(text: str, forbidden: list[str]) -> bool:
    low = text.lower()
    return any(t and t in low for t in forbidden)


def _visual_headline(brief: dict, forbidden: list[str]) -> str:
    """A short claim for the graphic, from the approved hook (bounded).

    Falls back to the editorial angle, and blanks out if the only source carries
    a forbidden term — the graphic never shows a superlative.
    """
    copy = brief.get("draft_copy", {})
    for src in (copy.get("hook"), brief.get("editorial_angle")):
        src = _clean(src or "")
        if not src:
            continue
        first = re.split(r"(?<=[.?!])\s+", src)[0]
        if _has_forbidden(first, forbidden):
            continue
        words = first.split()
        return " ".join(words[:12]) + ("…" if len(words) > 12 else "")
    return ""


def _distinct_points(brief: dict, forbidden: list[str]) -> list[str]:
    """Distinct short visual labels from the allowed facts: strips tags, skips
    forbidden terms, and de-duplicates near-identical facts (e.g. the repeated
    'sector Salud') by their leading words, so the count reflects real variety."""
    pts = brief.get("allowed_facts", [])
    out: list[str] = []
    seen: set[str] = set()
    for p in pts:
        p = re.sub(r"^\[[^\]]+\]\s*", "", str(p))  # strip leading [TAG]
        p = _clean(p)
        if not p or _has_forbidden(p, forbidden):
            continue
        sig = " ".join(p.lower().split()[:5])  # near-duplicate signature
        if sig in seen:
            continue
        seen.add(sig)
        words = p.split()
        out.append(" ".join(words[:9]) + ("…" if len(words) > 9 else ""))
    return out


def build_graphic_brief(brief: dict, subtheme: str, *, concept_dict: dict | None = None) -> dict:
    """Derive the graphic brief for one approved post. Fails closed on any
    forbidden term reaching the visual text."""
    concept_dict = concept_dict if concept_dict is not None else _load_concept_dict()
    hints = _subtheme_photo_hint(concept_dict)
    rules = _load_graphic_rules()
    forbidden = forbidden_terms(brief)

    distinct = _distinct_points(brief, forbidden)
    n = len(distinct)
    # Static/carousel is ultimately an editorial call; the engine only suggests.
    # Default STATIC, suggest CAROUSEL for clearly list/process posts, and flag
    # "carousel viable" when there is enough distinct material to build one.
    suggest = int(rules.get("carousel_suggest_points", 7))
    viable = int(rules.get("carousel_viable_points", 4))
    fmt = "CAROUSEL" if n >= suggest else "STATIC"
    carousel_viable = n >= viable

    disciplina, entorno = hints.get(subtheme, ("", ""))
    needs_photo = entorno in set(rules.get("photo_entornos", []))
    photo_query = (
        {"disciplina": disciplina, "entorno": entorno, "orientacion": "C"}
        if needs_photo
        else None
    )

    gb = {
        "content_id": brief.get("content_id"),
        "subtheme": subtheme,
        "visual_headline": _visual_headline(brief, forbidden),
        "key_points": distinct[:5],
        "recommended_format": fmt,
        "carousel_viable": carousel_viable,
        "needs_photo": needs_photo,
        "photo_query": photo_query,
        "evidence_ids": list(brief.get("knowledge_ids", [])),
    }

    # Safety net: after sanitizing, no blocked/forbidden term may remain.
    visual_text = " ".join([gb["visual_headline"], *gb["key_points"]]).lower()
    for term in forbidden:
        if term and term in visual_text:
            raise ValueError(
                f"El graphic_brief contiene un término bloqueado (GR-04): {term!r}"
            )
    return gb
