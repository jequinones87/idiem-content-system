"""Monthly Content Ops review.

Composes a month into one reviewable package: the plan grid, and per DRAFT slot
a concrete post (brief anchored to the slot's main knowledge_id + draft copy),
plus the CONTENT_GAP slots as gap cards. Renders a neutral, theme-aware,
self-contained HTML review (internal ops tool — deliberately NOT an IDIEM-brand
piece; visual identity waits for the Design System handoff).

Everything stays DRAFT until human approval. The rendered copy is bounded to the
fact sheet: the deterministic skeleton by default, or publishable copy ingested
per post via :func:`set_post_copy`.
"""

from __future__ import annotations

import html
import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from .brief import build_brief
from .drafting import DraftingAdapter, apply_draft, ingest_draft
from .loader import KnowledgeBase
from .planner import MonthlyPlanner, write_plan_csv, write_plan_json


@dataclass
class PostReview:
    seq: int
    content_id: str
    cell: str
    knowledge_id: str
    content_type: str
    status: str
    editorial_angle: str
    brief: dict


@dataclass
class GapReview:
    seq: int
    cell: str
    reason: str


@dataclass
class MonthReview:
    month: str
    target_count: int
    draft_count: int
    gap_count: int
    quotas: dict
    posts: list[PostReview] = field(default_factory=list)
    gaps: list[GapReview] = field(default_factory=list)
    plan: dict = field(default_factory=dict)


def compose_month(
    kb: KnowledgeBase,
    month: str,
    *,
    target_count: int | None = None,
    drafter: DraftingAdapter | None = None,
) -> MonthReview:
    """Compose a month: plan -> per-slot anchored brief + draft, and gap cards."""
    plan = MonthlyPlanner(kb).build_plan(month=month, target_count=target_count)

    posts: list[PostReview] = []
    gaps: list[GapReview] = []
    for slot in plan.slots:
        if slot.status == "DRAFT" and slot.knowledge_id:
            brief = build_brief(
                kb,
                slot.cell,
                main_knowledge_id=slot.knowledge_id,
                enrich_same_service=True,
            )
            brief["content_id"] = slot.content_id  # canonical post id from the plan
            drafted = apply_draft(brief, drafter)
            posts.append(
                PostReview(
                    seq=slot.seq,
                    content_id=slot.content_id,
                    cell=slot.cell,
                    knowledge_id=slot.knowledge_id,
                    content_type=drafted["content_type"],
                    status=drafted["status"],
                    editorial_angle=slot.editorial_angle,
                    brief=drafted,
                )
            )
        else:
            gaps.append(
                GapReview(seq=slot.seq, cell=slot.cell, reason=slot.reason or "")
            )

    quotas = dict(Counter(s.cell for s in plan.slots))
    return MonthReview(
        month=month,
        target_count=plan.target_count,
        draft_count=len(posts),
        gap_count=len(gaps),
        quotas=quotas,
        posts=posts,
        gaps=gaps,
        plan=plan.to_dict(),
    )


def set_post_copy(review: MonthReview, content_id: str, copy_dict: dict) -> PostReview:
    """Replace a post's draft with validated publishable copy (agent-assisted)."""
    for post in review.posts:
        if post.content_id == content_id:
            post.brief = ingest_draft(post.brief, copy_dict)
            return post
    raise KeyError(f"content_id no encontrado en la review: {content_id}")


# ---------------------------------------------------------------------------
# Rendering (neutral, theme-aware, self-contained — Artifact-ready body content)
# ---------------------------------------------------------------------------

_CSS = """
:root{
  --bg:#f6f7f9; --panel:#ffffff; --ink:#191c21; --muted:#5a6472;
  --line:#e3e6ec; --accent:#2f6f8f; --accent-ink:#ffffff;
  --gap:#9a3b2f; --warn:#a6791f; --chip:#eef1f5;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#14161a; --panel:#1c2027; --ink:#e8eaed; --muted:#98a2b2;
    --line:#2a2f39; --accent:#5aa6c7; --accent-ink:#0c1013;
    --gap:#e0958a; --warn:#d8b163; --chip:#242a33;
  }
}
:root[data-theme="dark"]{
  --bg:#14161a; --panel:#1c2027; --ink:#e8eaed; --muted:#98a2b2;
  --line:#2a2f39; --accent:#5aa6c7; --accent-ink:#0c1013;
  --gap:#e0958a; --warn:#d8b163; --chip:#242a33;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  line-height:1.55;padding:32px 20px;font-variant-numeric:tabular-nums}
.wrap{max-width:820px;margin:0 auto}
.banner{background:var(--chip);border:1px solid var(--line);border-radius:8px;
  padding:10px 14px;font-size:12.5px;color:var(--muted);margin-bottom:20px}
h1{font-size:23px;margin:0 0 4px;letter-spacing:-0.01em;text-wrap:balance}
h2{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);
  margin:26px 0 12px;font-weight:600}
.sub{color:var(--muted);font-size:14px;margin-bottom:18px}
.counts{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px}
.pill{background:var(--panel);border:1px solid var(--line);border-radius:999px;
  padding:4px 12px;font-size:12.5px;color:var(--muted)}
.pill b{color:var(--ink);font-weight:600}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;
  padding:16px 18px;margin-bottom:12px}
.card h3{margin:0 0 10px;font-size:13px;color:var(--muted);font-weight:600;
  font-family:ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.02em}
.meta{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;align-items:center}
.tag{background:var(--chip);border-radius:6px;padding:2px 9px;font-size:11.5px;
  color:var(--muted);letter-spacing:.02em}
.tag.status{color:var(--accent-ink);background:var(--accent);font-weight:600}
.tag.gap{color:var(--accent-ink);background:var(--gap);font-weight:600}
.tag.warn{color:var(--accent-ink);background:var(--warn);font-weight:600}
.copy{background:var(--bg);border:1px solid var(--line);border-left:3px solid var(--accent);
  border-radius:8px;padding:14px 16px;margin:12px 0}
.copy .hook{font-weight:650;font-size:15px}
.copy .body{white-space:pre-wrap;margin:9px 0;max-width:62ch}
.copy .cta{color:var(--accent);font-weight:600}
.sec{margin-top:12px}
.sec b{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
ul{margin:6px 0 0;padding-left:18px}
li{font-size:13.5px;margin:3px 0}
.blocked li{color:var(--gap)}
.warns li{color:var(--warn)}
.trace{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;
  color:var(--muted);margin-top:4px}
.overflow{overflow-x:auto}
.gapcard{border-left:4px solid var(--gap)}
.gapcard h3{color:var(--ink)}
"""


def _chips(label: str, items: list[str], cls: str = "") -> str:
    if not items:
        return ""
    lis = "".join(f"<li>{html.escape(str(x))}</li>" for x in items)
    return f'<div class="sec {cls}"><b>{html.escape(label)}</b><ul>{lis}</ul></div>'


def _post_card(post: PostReview) -> str:
    b = post.brief
    copy = b.get("draft_copy", {})
    gov = ""
    if b.get("blocked_claims"):
        gov += '<span class="tag gap">claims bloqueados</span>'
    if any("NAME_ONLY" in m for m in b.get("mandatory_matices", [])):
        gov += '<span class="tag warn">solo nombrar</span>'
    meta = (
        f'<span class="tag status">{html.escape(post.status)}</span>'
        f'<span class="tag">{html.escape(post.cell)}</span>'
        f'<span class="tag">{html.escape(post.content_type)}</span>'
        f'<span class="tag">{html.escape(post.knowledge_id)}</span>'
        f"{gov}"
    )
    copy_html = (
        f'<div class="copy">'
        f'<div class="hook">{html.escape(copy.get("hook",""))}</div>'
        f'<div class="body">{html.escape(copy.get("body",""))}</div>'
        f'<div class="cta">{html.escape(copy.get("cta",""))}</div>'
        f"</div>"
    )
    facts = _chips("Hechos permitidos", b.get("allowed_facts", []))
    blocked = _chips("Claims bloqueados", b.get("blocked_claims", []), "blocked")
    matices = _chips("Matices obligatorios", b.get("mandatory_matices", []), "warns")
    tr = b.get("traceability", {})
    trace = (
        f'<div class="sec"><b>Trazabilidad</b>'
        f'<div class="trace overflow">relations: {html.escape(", ".join(tr.get("relation_ids", [])))}<br>'
        f'documents: {html.escape(", ".join(tr.get("document_ids", [])))}</div></div>'
    )
    return (
        f'<div class="card" id="{html.escape(post.content_id)}">'
        f"<h3>#{post.seq:02d} · {html.escape(post.content_id)}</h3>"
        f'<div class="meta">{meta}</div>'
        f"{copy_html}{facts}{blocked}{matices}{trace}"
        f"</div>"
    )


def _gap_card(gap: GapReview) -> str:
    return (
        f'<div class="card gapcard">'
        f"<h3>#{gap.seq:02d} · {html.escape(gap.cell)}</h3>"
        f'<div class="meta"><span class="tag gap">CONTENT_GAP</span></div>'
        f"<div>{html.escape(gap.reason)}</div></div>"
    )


def render_review_html(review: MonthReview) -> str:
    """Render the review as self-contained body content (Artifact-ready)."""
    counts = (
        f'<span class="pill">Target <b>{review.target_count}</b></span>'
        f'<span class="pill">DRAFT <b>{review.draft_count}</b></span>'
        f'<span class="pill">CONTENT_GAP <b>{review.gap_count}</b></span>'
    )
    quotas = "".join(
        f'<span class="pill">{html.escape(cell)} <b>{n}</b></span>'
        for cell, n in sorted(review.quotas.items())
    )
    posts = "".join(_post_card(p) for p in review.posts)
    gaps = "".join(_gap_card(g) for g in review.gaps)
    gaps_section = f"<h2>Content gaps · {review.gap_count}</h2>{gaps}" if gaps else ""
    return (
        f"<title>Grilla editorial {html.escape(review.month)}</title>"
        f"<style>{_CSS}</style>"
        f'<div class="wrap">'
        f'<div class="banner">Uso interno — herramienta de operación, no es pieza de marca. '
        f"Todo permanece DRAFT hasta aprobación humana. La identidad visual IDIEM llega "
        f"en el handoff del Design System.</div>"
        f"<h1>Plan de contenido · {html.escape(review.month)}</h1>"
        f'<div class="sub">Revisión editorial con trazabilidad a la biblioteca 2A.2. '
        f"Cada post traza a su knowledge_id, hechos permitidos, claims bloqueados y fuentes.</div>"
        f'<div class="counts">{counts}</div>'
        f'<div class="counts">{quotas}</div>'
        f"<h2>Posts · {review.draft_count}</h2>"
        f"{posts}{gaps_section}"
        f"</div>"
    )


def to_standalone_html(content: str) -> str:
    """Wrap Artifact-ready body content into a full standalone HTML document.

    ``content`` carries the <title> and <style>; those belong in <head>, while
    the visible markup is emitted into <body>. Split on the closing </style> tag.
    """
    marker = "</style>"
    if marker in content:
        head, body = content.split(marker, 1)
        head = head + marker
    else:
        head, body = "", content
    return (
        "<!doctype html>\n<html lang='es'>\n<head>\n<meta charset='utf-8'>\n"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>\n"
        f"{head}\n</head>\n<body>\n{body}\n</body>\n</html>"
    )


def write_review(review: MonthReview, out_dir: Path) -> dict[str, Path]:
    """Write the review HTML (standalone) plus the plan JSON/CSV to ``out_dir``."""
    out_dir.mkdir(parents=True, exist_ok=True)
    content = render_review_html(review)

    # Standalone document for local viewing / repo.
    html_path = out_dir / f"review_{review.month}.html"
    with html_path.open("w", encoding="utf-8") as fh:
        fh.write(to_standalone_html(content))

    # Artifact-ready body content (no <html>/<head>/<body> wrappers).
    body_path = out_dir / f"review_{review.month}.artifact.html"
    with body_path.open("w", encoding="utf-8") as fh:
        fh.write(content)

    from .planner import MonthlyPlan, PlanSlot  # local import to rebuild for exports

    # Rebuild a MonthlyPlan view for the CSV/JSON exporters from stored dict.
    plan_dict = review.plan
    plan = MonthlyPlan(
        month=plan_dict["month"],
        target_count=plan_dict["target_count"],
        cadence_per_week=plan_dict["cadence_per_week"],
        weights=plan_dict["weights"],
        allow_rebalance=plan_dict["allow_rebalance"],
        slots=[PlanSlot(**s) for s in plan_dict["slots"]],
        gaps=list(plan_dict["gaps"]),
        log=list(plan_dict["log"]),
    )
    csv_path = write_plan_csv(plan, out_dir)
    json_path = write_plan_json(plan, out_dir)
    return {"html": html_path, "artifact": body_path, "csv": csv_path, "json": json_path}
