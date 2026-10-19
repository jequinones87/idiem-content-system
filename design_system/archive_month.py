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
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent / "src"))

import gen_month_grid as G      # noqa: E402  (COPY, GRAPHIC, CELL_SHORT)
import gen_workstation as W     # noqa: E402  (PHOTO_SUB, STOCK_SUB, SPECIAL, APPLIED_LOG)
import carousel as CAR          # noqa: E402  (CAROUSEL_POSTS)
from idiem.archive import build_month_archive, to_markdown  # noqa: E402


def _full_copy(c: dict) -> str:
    return f'{c["hook"]}\n\n{c["body"]}\n\n{c["cta"]}'


def _strip_tags(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


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
        c = G.COPY[post.knowledge_id]
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

    # posts institucionales / adicionales: no trazan a knowledge_id de 2A.2. Pueden ser
    # saludos de una lámina o carruseles (fuentes oficiales aportadas por MKT).
    for s in W.SPECIAL:
        c = s["copy"]
        full = _full_copy(c)
        is_car = s["seq"] in CAR.CAROUSEL_POSTS
        if is_car:
            sl = CAR.SLIDES.get(s["seq"], {})
            port = sl.get("portada", {})
            graphic = {"svc": port.get("kicker", s.get("subtheme", "")),
                       "title": _strip_tags(port.get("title", "")),
                       "msg": ""}
        else:
            graphic = {"kicker": s.get("kicker", ""), "title": s.get("title", ""),
                       "sub": s.get("sub", "")}
        photo = s.get("photo") or {"source": "sin_foto",
                                   "detalle": s.get("photo_note", "sin foto por ahora")}
        posts.append({
            "seq": s["seq"],
            "content_id": s["content_id"],
            "cell": None,
            "cell_short": s.get("cshort", ""),
            "subtheme": s.get("subtheme", ""),
            "editorial_angle": s.get("editorial_angle", "post institucional (no traza a knowledge_id)"),
            "format": "CARRUSEL" if is_car else s.get("fmt", "SALUDO"),
            "knowledge_id": None,
            "evidence_ids": [],
            "graphic": graphic,
            "photo": photo,
            "copy": {"hook": c["hook"], "body": c["body"], "cta": c["cta"],
                     "full": full, "chars": len(full)},
            "posted": True if published_all else None,
        })

    return build_month_archive(month, posts, published=published_all)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", default=G.MONTH_ID,
                    help="etiqueta del mes a archivar (por defecto, el mes activo del sistema)")
    ap.add_argument("--published-all", action="store_true",
                    help="marca todas las piezas como publicadas (estado del mes cerrado)")
    ap.add_argument("--out-dir", default=str(ROOT.parent / "content" / "archive"))
    ap.add_argument("--force", action="store_true",
                    help="sobrescribe un archivo ya congelado (pierde ediciones manuales)")
    args = ap.parse_args()

    out = Path(args.out_dir)
    if (out / f"{args.month}.json").exists() and not args.force:
        # Fail closed: el archivo congelado es la memoria ÚNICA (p.ej. octubre lleva el copy
        # definitivo de la workstation, que los generadores no reproducen al 100%).
        sys.exit(f"{out}/{args.month}.json ya existe; usa design_system/archive_refresh.py para "
                 "recalcular huellas, o --force para regenerarlo desde los generadores.")
    archive = build_archive(args.month, args.published_all)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{args.month}.json").write_text(
        json.dumps(archive, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / f"{args.month}.md").write_text(to_markdown(archive), encoding="utf-8")
    print(f"archive: {args.month} -> {out}/{args.month}.json + .md "
          f"({archive['count']} piezas, {len(archive['dedup_index']['knowledge_ids'])} knowledge_ids)")
