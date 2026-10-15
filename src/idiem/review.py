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
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from .brief import build_brief
from .drafting import DraftingAdapter, apply_draft, ingest_draft
from .graphic import build_graphic_brief
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
    sources: list[dict] = field(default_factory=list)
    subtheme: str = ""
    graphic_brief: dict = field(default_factory=dict)


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


_EXT_TAG = re.compile(r"\[(EXT-\d+)\]")
_OVR_TAG = re.compile(r"\[(OVR-[A-Za-z0-9\-]+)\]")


def _collect_sources(kb: KnowledgeBase, brief: dict) -> list[dict]:
    """Exact source text behind a post, matching the facts actually used.

    Derives evidence rows from (1) each knowledge item's canonical sources,
    (2) the 2A.3 enrichment records referenced by ``[EXT-####]`` tags present in
    the post's facts, and (3) any audited ``[OVR-...]`` policy override. Reading
    the tags off the brief keeps the "Ver fuente" popup consistent with the
    month-level de-dup: only enrichment actually surfaced in this post is shown.
    Returns records {label, file, page, text} for veracity checks.
    """
    sources: list[dict] = []
    for kid in brief.get("knowledge_ids", []):
        for s in kb.sources_for(kid):
            sources.append(
                {"label": kid, "file": s.file_name, "page": s.page, "text": s.verified_evidence}
            )

    # Scan the fact/claim/matiz lines this post actually carries for 2A.3 tags.
    lines = (
        list(brief.get("allowed_facts", []))
        + list(brief.get("blocked_claims", []))
        + list(brief.get("mandatory_matices", []))
    )
    blob = "\n".join(lines)

    seen_ext: set[str] = set()
    for eid in _EXT_TAG.findall(blob):
        if eid in seen_ext:
            continue
        seen_ext.add(eid)
        rec = kb.enrichment_by_id(eid)
        if rec:
            sources.append(
                {
                    "label": eid,
                    "file": rec.get("file_name", ""),
                    "page": rec.get("page", ""),
                    "text": rec.get("verified_evidence", ""),
                }
            )

    seen_ovr: set[str] = set()
    for oid in _OVR_TAG.findall(blob):
        if oid in seen_ovr:
            continue
        seen_ovr.add(oid)
        for kid in brief.get("knowledge_ids", []):
            ov = kb.policy_override_for(kid)
            if ov and ov.get("override_id") == oid:
                text = ov.get("rationale", "")
                if ov.get("allowed_facts"):
                    text = ov["allowed_facts"][0]
                sources.append(
                    {
                        "label": oid,
                        "file": ov.get("file_name", ""),
                        "page": ov.get("page", ""),
                        "text": text,
                    }
                )
                break
    return sources


def compose_month(
    kb: KnowledgeBase,
    month: str,
    *,
    target_count: int | None = None,
    drafter: DraftingAdapter | None = None,
    recent_history: list[str] | None = None,
) -> MonthReview:
    """Compose a month: plan -> per-slot anchored brief + draft + graphic brief.

    ``recent_history`` (from the published ledger) excludes recently-used items
    so content rotates month to month.
    """
    planner = MonthlyPlanner(kb)
    plan = planner.build_plan(
        month=month, target_count=target_count, recent_history=recent_history
    )

    # Month-level de-dup: a 2A.3 enrichment record (e.g. the ISO/HSEC line)
    # surfaces at most once across the whole month, so posts stop repeating the
    # same credential/attribute (Fase B). Accumulated across slots in order.
    used_enrichment_ids: set[str] = set()

    posts: list[PostReview] = []
    gaps: list[GapReview] = []
    for slot in plan.slots:
        if slot.status == "DRAFT" and slot.knowledge_id:
            brief = build_brief(
                kb,
                slot.cell,
                main_knowledge_id=slot.knowledge_id,
                enrich_same_service=True,
                used_enrichment_ids=used_enrichment_ids,
            )
            brief["content_id"] = slot.content_id  # canonical post id from the plan
            drafted = apply_draft(brief, drafter)
            subtheme = planner._tema_of(kb.item_by_id[slot.knowledge_id])
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
                    sources=_collect_sources(kb, drafted),
                    subtheme=subtheme,
                    graphic_brief=build_graphic_brief(drafted, subtheme),
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
    """Replace a post's draft with validated publishable copy (agent-assisted).

    Re-validates against allowed_facts / blocked terms and regenerates the
    graphic brief so the visual headline stays in sync with the edited copy.
    """
    for post in review.posts:
        if post.content_id == content_id:
            post.brief = ingest_draft(post.brief, copy_dict)
            post.graphic_brief = build_graphic_brief(post.brief, post.subtheme)
            return post
    raise KeyError(f"content_id no encontrado en la review: {content_id}")


def replace_post(
    kb: KnowledgeBase,
    review: MonthReview,
    content_id: str,
    *,
    drafter: DraftingAdapter | None = None,
) -> PostReview:
    """Reject one post and swap in the next best candidate of the same cell.

    The "Cambiar post" action: excludes the rejected item AND every item already
    used in the month, then takes the cell's next diversified candidate. Keeps
    policy/traceability intact. Raises if the cell has no alternative left.
    """
    target = next((p for p in review.posts if p.content_id == content_id), None)
    if target is None:
        raise KeyError(f"content_id no encontrado en la review: {content_id}")

    used = {p.knowledge_id for p in review.posts}  # includes the rejected one
    planner = MonthlyPlanner(kb)
    candidates = planner._candidates(target.cell, used)
    if not candidates:
        raise ValueError(
            f"Sin alternativa disponible en la célula '{target.cell}' para reemplazar."
        )
    new_item = candidates[0]

    brief = build_brief(
        kb, target.cell, main_knowledge_id=new_item.knowledge_id,
        enrich_same_service=True,
    )
    brief["content_id"] = target.content_id  # keep the slot's canonical id
    drafted = apply_draft(brief, drafter)
    subtheme = planner._tema_of(new_item)

    updated = PostReview(
        seq=target.seq,
        content_id=target.content_id,
        cell=target.cell,
        knowledge_id=new_item.knowledge_id,
        content_type=drafted["content_type"],
        status=drafted["status"],
        editorial_angle=target.editorial_angle,
        brief=drafted,
        sources=_collect_sources(kb, drafted),
        subtheme=subtheme,
        graphic_brief=build_graphic_brief(drafted, subtheme),
    )
    review.posts[review.posts.index(target)] = updated
    return updated


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
.gbrief{background:var(--bg);border:1px solid var(--line);border-left:3px solid var(--warn);
  border-radius:8px;padding:12px 14px;margin:12px 0}
.gbtag{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.gbtag b{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.gbhead{font-weight:650;font-size:14px;color:var(--ink)}
.gbpts{margin:6px 0 0;padding-left:18px}
.gbpts li{font-size:13px;margin:2px 0;color:var(--muted)}
.gbphoto{margin-top:8px;font-size:12px;color:var(--muted)}
.sec{margin-top:12px}
.sec b{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
details.sec>summary{font-size:11px;text-transform:uppercase;letter-spacing:.06em;
  color:var(--muted);font-weight:600;cursor:pointer;list-style:none;
  display:flex;align-items:center;gap:8px;padding:3px 0}
details.sec>summary::-webkit-details-marker{display:none}
details.sec>summary::before{content:"\25B8";font-size:10px;transition:transform .15s;color:var(--muted)}
details.sec[open]>summary::before{transform:rotate(90deg)}
details.sec>summary:hover{color:var(--ink)}
details.sec .count{background:var(--chip);border:1px solid var(--line);border-radius:999px;
  padding:0 8px;font-size:10.5px;color:var(--muted);font-weight:600;letter-spacing:0}
details.sec[open]>summary{margin-bottom:2px}
ul{margin:6px 0 0;padding-left:18px}
li{font-size:13.5px;margin:3px 0}
.blocked li{color:var(--gap)}
.warns li{color:var(--warn)}
.overflow{overflow-x:auto}
.gapcard{border-left:4px solid var(--gap)}
.gapcard h3{color:var(--ink)}
.srcbtn{cursor:pointer;font:inherit;font-size:13px;font-weight:600;
  color:var(--accent);background:var(--chip);border:1px solid var(--line);
  border-radius:8px;padding:7px 12px}
.srcbtn:hover{border-color:var(--accent)}
.srcbtn:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.srcdlg{border:1px solid var(--line);border-radius:12px;padding:0;max-width:640px;
  width:calc(100% - 32px);background:var(--panel);color:var(--ink)}
.srcdlg::backdrop{background:rgba(0,0,0,.45)}
.dlghead{display:flex;justify-content:space-between;align-items:center;gap:12px;
  padding:14px 16px;border-bottom:1px solid var(--line)}
.dlgclose{cursor:pointer;font:inherit;border:none;background:transparent;
  color:var(--muted);font-size:16px}
.dlgbody{padding:8px 16px 4px;max-height:60vh;overflow-y:auto}
.srcrow{padding:12px 0;border-bottom:1px solid var(--line)}
.srcrow:last-child{border-bottom:none}
.srcmeta{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:6px}
.srcfile{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;color:var(--muted)}
.srctext{font-size:14px;line-height:1.5}
.dlgcta{margin:12px 16px 16px;cursor:pointer;font:inherit;font-weight:600;
  color:var(--accent-ink);background:var(--accent);border:none;border-radius:8px;padding:8px 16px}
"""


def _chips(label: str, items: list[str], cls: str = "") -> str:
    """Collapsible (<details>) section with a count, collapsed by default so a
    post card stays compact until the reviewer expands it."""
    if not items:
        return ""
    lis = "".join(f"<li>{html.escape(str(x))}</li>" for x in items)
    return (
        f'<details class="sec {cls}"><summary>{html.escape(label)}'
        f'<span class="count">{len(items)}</span></summary><ul>{lis}</ul></details>'
    )


def _graphic_block(post: PostReview) -> str:
    """Render the graphic brief next to the copy (reviewed together)."""
    g = post.graphic_brief
    if not g:
        return ""
    fmt = html.escape(str(g.get("recommended_format", "STATIC")))
    if g.get("recommended_format") == "STATIC" and g.get("carousel_viable"):
        fmt += " · carrusel posible"
    headline = html.escape(str(g.get("visual_headline", "")))
    pts = "".join(f"<li>{html.escape(str(p))}</li>" for p in g.get("key_points", []))
    pq = g.get("photo_query")
    if pq:
        photo = (
            f'📷 Foto sugerida · {html.escape(str(pq.get("disciplina","")))} · '
            f'{html.escape(str(pq.get("entorno","")))} · {html.escape(str(pq.get("orientacion","")))}'
        )
    else:
        photo = "🎨 Gráfica template (sin foto)"
    return (
        f'<div class="gbrief">'
        f'<div class="gbtag"><b>Gráfica</b><span class="tag">{fmt}</span></div>'
        f'<div class="gbhead">{headline}</div>'
        f"<ul class=\"gbpts\">{pts}</ul>"
        f'<div class="gbphoto">{photo}</div>'
        f"</div>"
    )


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
    graphic = _graphic_block(post)
    facts = _chips("Hechos permitidos", b.get("allowed_facts", []))
    blocked = _chips("Claims bloqueados", b.get("blocked_claims", []), "blocked")
    matices = _chips("Matices obligatorios", b.get("mandatory_matices", []), "warns")

    dlg_id = f"src-{post.content_id}"
    source_btn = (
        f'<div class="sec"><button class="srcbtn" type="button" '
        f"onclick=\"document.getElementById('{html.escape(dlg_id)}').showModal()\">"
        f"🔎 Ver fuente ({len(post.sources)})</button></div>"
    )
    rows = ""
    for s in post.sources:
        rows += (
            f'<div class="srcrow"><div class="srcmeta">'
            f'<span class="tag">{html.escape(str(s.get("label","")))}</span>'
            f'<span class="srcfile">{html.escape(str(s.get("file","")))} · p.{html.escape(str(s.get("page","")))}</span>'
            f'</div><div class="srctext">{html.escape(str(s.get("text","")))}</div></div>'
        )
    dialog = (
        f'<dialog id="{html.escape(dlg_id)}" class="srcdlg">'
        f'<form method="dialog"><div class="dlghead">'
        f"<b>Fuente exacta · {html.escape(post.content_id)}</b>"
        f'<button class="dlgclose" value="close">✕</button></div></form>'
        f'<div class="dlgbody">{rows or "<em>Sin fuentes.</em>"}</div>'
        f'<form method="dialog"><button class="dlgcta">Cerrar</button></form>'
        f"</dialog>"
    )
    return (
        f'<div class="card" id="{html.escape(post.content_id)}">'
        f"<h3>#{post.seq:02d} · {html.escape(post.content_id)}</h3>"
        f'<div class="meta">{meta}</div>'
        f"{copy_html}{graphic}{facts}{blocked}{matices}{source_btn}{dialog}"
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
