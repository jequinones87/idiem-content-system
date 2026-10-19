"""Archivo mensual consolidado (memoria única) — índices derivados.

``content/archive/AAAA-MM.json`` es la memoria ÚNICA de lo publicado/programado
(copies definitivos). Este módulo calcula, desde la lista de piezas, todo lo que se
deriva de ella: huella editorial por pieza, índice de dedup e índice de huellas.
Lo usan ``design_system/archive_month.py`` (sep/oct) y
``design_system/archive_month_plan.py`` (desde nov, desde ``state/plans/``).
"""

from __future__ import annotations

import datetime as _dt
from collections import Counter

from .editorial_fingerprint import fingerprint_archive_post


def build_month_archive(month: str, posts: list[dict], *, published: bool,
                        extra: dict | None = None) -> dict:
    posts = sorted(posts, key=lambda p: p["seq"])
    for p in posts:
        p["editorial_fingerprint"] = fingerprint_archive_post(p).to_dict()

    kids = [p["knowledge_id"] for p in posts if p.get("knowledge_id")]
    subs = sorted({p["subtheme"] for p in posts if p.get("subtheme")})
    cells = dict(Counter(p["cell_short"] for p in posts if p.get("cell_short")))
    fps = [p["editorial_fingerprint"] for p in posts]
    archive = {
        "month": month,
        "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "published": bool(published),
        "count": len(posts),
        "dedup_index": {
            "knowledge_ids": sorted(set(kids)),
            "subthemes": subs,
            "cells": cells,
            "angles": [{"seq": p["seq"], "cell": p.get("cell_short"), "subtheme": p.get("subtheme"),
                        "angle": p.get("editorial_angle", "")} for p in posts],
        },
        "fingerprint_index": {
            "archetypes": dict(Counter(f["editorial_archetype"] for f in fps)),
            "cta_types": dict(Counter(f["cta_type"] for f in fps)),
            "hook_types": dict(Counter(f["hook_type"] for f in fps)),
            "pain_categories": dict(Counter(f["pain_category"] for f in fps)),
            "visual_themes": dict(Counter(f["visual_theme"] for f in fps if f["visual_theme"])),
        },
        "posts": posts,
    }
    if extra:
        archive.update(extra)
    return archive


def to_markdown(a: dict) -> str:
    L = [f"# Archivo de contenidos — {a['month']}", ""]
    L.append(f"> Generado {a['generated_at']} · {a['count']} piezas · "
             f"publicado: {'sí' if a['published'] else a.get('publication_note', 'no registrado')}.")
    L.append("> Memoria de lo publicado: úsalo como CONTEXTO al armar el mes siguiente, "
             "para ACTUALIZAR hechos y para NO REPETIR temas/ángulos.")
    L.append("")
    di = a["dedup_index"]
    L.append("## Índice para no repetir (dedup)")
    L.append(f"- **Células usadas:** " + ", ".join(f"{k}×{v}" for k, v in sorted(di["cells"].items())))
    L.append(f"- **knowledge_ids usados:** " + ", ".join(f"`{k}`" for k in di["knowledge_ids"]))
    L.append("- **Subtemas usados:**")
    for s in di["subthemes"]:
        L.append(f"  - {s}")
    L.append("")
    L.append("## Piezas")
    for p in a["posts"]:
        L.append("")
        L.append(f"### {p['seq']:02d} · {p.get('cell_short') or ''} · {p.get('subtheme') or p['content_id']}")
        meta = [f"`{p['content_id']}`", p["format"]]
        if p["knowledge_id"]:
            meta.append(f"knowledge_id `{p['knowledge_id']}`")
        if p["evidence_ids"]:
            meta.append("evidencia " + ", ".join(f"`{e}`" for e in p["evidence_ids"]))
        L.append(" · ".join(meta))
        ph = p["photo"]
        L.append(f"- **Foto:** {ph.get('source')} "
                 + (f"`{ph.get('photo_id') or ph.get('stock_id','')}`" if ph.get('photo_id') or ph.get('stock_id') else "")
                 + (f" — {ph['detalle']}" if ph.get('detalle') else ""))
        if p.get("status"):
            L.append(f"- **Estado:** {p['status']}")
        fp = p.get("editorial_fingerprint") or {}
        L.append(f"- **Huella:** {fp.get('editorial_archetype')} · hook {fp.get('hook_type')} · "
                 f"CTA {fp.get('cta_type')}" + (" (asignada)" if fp.get("assigned_fields") else " (heurística)"))
        L.append(f"- **Ángulo:** {p.get('editorial_angle', '')}")
        L.append(f"- **Copy ({p['copy']['chars']} car.):**")
        L.append("")
        L.append("```")
        L.append(p["copy"]["full"])
        L.append("```")
    L.append("")
    return "\n".join(L)
