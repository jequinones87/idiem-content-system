"""Archivador de contenidos mensuales — memoria de lo publicado.

Congela el contenido de un mes (copys, fotos, trazas, plan y estado) en un
registro versionado que sirve para los meses siguientes:
  1) CONTEXTO: qué se publicó y con qué evidencia/fotos.
  2) ACTUALIZACIÓN: base para corregir hechos si cambian.
  3) NO REPETIR: índice de dedup (knowledge_ids, subtemas, ángulos, células)
     para que el mes nuevo rote temas y no repita posts del mes anterior.

Fuente: los propios generadores (compose_month + COPY + PHOTO_SUB/STOCK_SUB +
SPECIAL), así el archivo es reproducible y auditable. El estado de publicación
vive en la DB del artefacto; se anota a nivel de mes con --published-all (o se
deja como "no registrado").

Uso:
  PYTHONPATH=src python3 design_system/archive_month.py --month 2026-09 \
      --published-all --out-dir content/archive
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent / "src"))

import gen_month_grid as G      # noqa: E402  (COPY, GRAPHIC, CELL_SHORT)
import gen_workstation as W     # noqa: E402  (PHOTO_SUB, STOCK_SUB, SPECIAL, APPLIED_LOG)
import carousel as CAR          # noqa: E402  (CAROUSEL_POSTS)


def _full_copy(c: dict) -> str:
    return f'{c["hook"]}\n\n{c["body"]}\n\n{c["cta"]}'


def _photo(seq: int, ps: dict) -> dict:
    """Traza de la foto usada, espejando la lógica de la workstation."""
    if seq in W.PHOTO_SUB:
        s = W.PHOTO_SUB[seq]
        return {"source": "libreria_idiem", "photo_id": s["photo_id"],
                "fuente": s.get("fuente", ""), "detalle": s.get("detalle", ""),
                "reemplaza_a": s.get("orig", ""), "motivo": s.get("reason", "")}
    if seq in W.STOCK_SUB:
        s = W.STOCK_SUB[seq]
        return {"source": "adobe_stock", "stock_id": s["id"], "detalle": s.get("detalle", "")}
    src = (ps or {}).get("source")
    if src == "library":
        return {"source": "libreria_idiem", "photo_id": ps.get("photo_id", ""),
                "fuente": ps.get("fuente", "")}
    if src == "muapi":
        return {"source": "muapi_generada"}
    return {"source": "sin_foto", "detalle": "campo de marca sólido (needs_photo=false)"}


def build_archive(month: str, published_all: bool) -> dict:
    kb = G.load_knowledge_base()
    # Usa la composición curada del mes activo (misma fuente que la workstation),
    # de modo que el archivo refleje exactamente lo publicado (picks + copy + fotos).
    review = G.compose_current(kb)

    posts = []
    for seq, post in enumerate(review.posts, 1):
        c = G.COPY[post.content_id]
        full = _full_copy(c)
        gb = post.graphic_brief or {}
        ps = gb.get("photo_selection") or {}
        graphic = G.GRAPHIC.get(seq, {})
        posts.append({
            "seq": seq,
            "content_id": post.content_id,
            "cell": post.cell,
            "cell_short": G.CELL_SHORT.get(post.cell, post.cell[:3].upper()),
            "subtheme": post.subtheme,
            "editorial_angle": post.editorial_angle,
            "format": "CARRUSEL" if seq in CAR.CAROUSEL_POSTS else (gb.get("recommended_format") or "STATIC"),
            "knowledge_id": post.knowledge_id,
            "evidence_ids": gb.get("evidence_ids") or [],
            "graphic": {"svc": graphic.get("svc", ""), "msg": graphic.get("msg", ""),
                        "baseline": graphic.get("base", "")},
            "photo": _photo(seq, ps),
            "copy": {"hook": c["hook"], "body": c["body"], "cta": c["cta"],
                     "full": full, "chars": len(full)},
            "posted": True if published_all else None,
        })

    # posts institucionales (saludos): no trazan a knowledge_id
    for s in W.SPECIAL:
        c = s["copy"]
        full = _full_copy(c)
        posts.append({
            "seq": s["seq"],
            "content_id": s["content_id"],
            "cell": None,
            "cell_short": s.get("cshort", ""),
            "subtheme": s.get("subtheme", ""),
            "editorial_angle": "saludo institucional (no traza a knowledge_id)",
            "format": s.get("fmt", "SALUDO"),
            "knowledge_id": None,
            "evidence_ids": [],
            "graphic": {"kicker": s.get("kicker", ""), "title": s.get("title", ""),
                        "sub": s.get("sub", "")},
            "photo": {"source": "libreria_idiem", "photo_id": "generica_bandera_chile_mineria"},
            "copy": {"hook": c["hook"], "body": c["body"], "cta": c["cta"],
                     "full": full, "chars": len(full)},
            "posted": True if published_all else None,
        })

    posts.sort(key=lambda p: p["seq"])

    # índice de dedup para el mes siguiente
    kids = [p["knowledge_id"] for p in posts if p["knowledge_id"]]
    subs = sorted({p["subtheme"] for p in posts if p["subtheme"]})
    cells: dict = {}
    for p in posts:
        if p["cell_short"]:
            cells[p["cell_short"]] = cells.get(p["cell_short"], 0) + 1

    return {
        "month": month,
        "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "published": bool(published_all),
        "count": len(posts),
        "dedup_index": {
            "knowledge_ids": sorted(set(kids)),
            "subthemes": subs,
            "cells": cells,
            "angles": [{"seq": p["seq"], "cell": p["cell_short"], "subtheme": p["subtheme"],
                        "angle": p["editorial_angle"]} for p in posts],
        },
        "posts": posts,
    }


def to_markdown(a: dict) -> str:
    L = [f"# Archivo de contenidos — {a['month']}", ""]
    L.append(f"> Generado {a['generated_at']} · {a['count']} piezas · "
             f"publicado: {'sí' if a['published'] else 'no registrado'}.")
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
        L.append(f"### {p['seq']:02d} · {p['cell_short']} · {p['subtheme'] or p['content_id']}")
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
        L.append(f"- **Ángulo:** {p['editorial_angle']}")
        L.append(f"- **Copy ({p['copy']['chars']} car.):**")
        L.append("")
        L.append("```")
        L.append(p["copy"]["full"])
        L.append("```")
    L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", default=G.MONTH_ID,
                    help="etiqueta del mes a archivar (por defecto, el mes activo del sistema)")
    ap.add_argument("--published-all", action="store_true",
                    help="marca todas las piezas como publicadas (estado del mes cerrado)")
    ap.add_argument("--out-dir", default=str(ROOT.parent / "content" / "archive"))
    args = ap.parse_args()

    archive = build_archive(args.month, args.published_all)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{args.month}.json").write_text(
        json.dumps(archive, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / f"{args.month}.md").write_text(to_markdown(archive), encoding="utf-8")
    print(f"archive: {args.month} -> {out}/{args.month}.json + .md "
          f"({archive['count']} piezas, {len(archive['dedup_index']['knowledge_ids'])} knowledge_ids)")
