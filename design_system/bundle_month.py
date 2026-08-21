"""Bundle mensual descargable — HTML + 12 PNG 1080x1080 + copy.txt.

Produce un paquete por mes, listo para publicar, sin servidor:

  idiem_<mes>/
    README.txt
    grilla_<mes>.html            (la grilla de revisión, copy editable)
    posts/NN_CEL_slug.png        (12 gráficas 1080x1080)
    copy/copy_<mes>.txt          (los 12 copies juntos)
    copy/NN_CEL.txt              (un copy por post, listo para pegar)

Reutiliza la capa visual y el copy de `gen_month_grid` (misma fuente de verdad).
Cada gráfica embebe la foto de `assets/month/pNN.(jpg|jpeg|png)` si existe; si no,
usa el campo de marca sólido. Así, al dejar una foto nueva con ese nombre y volver
a correr, la gráfica queda con foto — sin tocar código.

Uso:
  1) PYTHONPATH=src python3 design_system/bundle_month.py --emit   # genera HTML + copy + manifest
  2) node design_system/render_bundle.cjs <build_dir>/manifest.json # rasteriza PNG
  (el runner de sesión encadena ambos y comprime el zip)
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import gen_month_grid as G  # noqa: E402  (misma fuente de datos/visual)

MONTH_LABEL = {"2026-09": "septiembre_2026"}


def resolve_photo(seq: int):
    """Cualquier assets/month/pNN.(jpg|jpeg|png) -> data URI. Extensible."""
    for ext in ("jpg", "jpeg", "png"):
        f = G.MONTH / f"p{seq:02d}.{ext}"
        if f.exists():
            b = f.read_bytes()
            import base64
            mime = "png" if ext == "png" else "jpeg"
            return f"data:image/{mime};base64,{base64.b64encode(b).decode()}"
    return None


def slug(text: str) -> str:
    t = (text or "").lower()
    t = (t.replace("á", "a").replace("é", "e").replace("í", "i")
          .replace("ó", "o").replace("ú", "u").replace("ñ", "n"))
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:40] or "post"


def grid_style() -> str:
    m = re.search(r"<style>(.*?)</style>", G.TEMPLATE, re.S)
    return m.group(1) if m else ""


PAGE = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap">
<style>{style}</style>
<style>
  html,body{{margin:0;padding:0;background:#0a0c0d}}
  .export{{width:1080px;height:1080px;position:relative;overflow:hidden}}
  .export .canvas{{width:1080px !important;height:1080px !important;border-radius:0 !important;box-shadow:none !important}}
</style></head>
<body><div class="export">{canvas}</div></body></html>"""


def emit(month: str, build_root: Path) -> Path:
    label = MONTH_LABEL.get(month, month.replace("-", "_"))
    out = build_root / f"idiem_{label}"
    posts_dir = out / "posts"
    copy_dir = out / "copy"
    for d in (posts_dir, copy_dir):
        d.mkdir(parents=True, exist_ok=True)

    kb = G.load_knowledge_base()
    review = G.compose_month(kb, month, target_count=12)
    for cid, c in G.COPY.items():
        G.set_post_copy(review, cid, c)

    style = grid_style()
    manifest = []
    all_copy = []

    for seq, post in enumerate(review.posts, 1):
        cell = post.cell
        cshort = G.CELL_SHORT.get(cell, cell[:3].upper())
        gb = post.graphic_brief or {}
        ps = gb.get("photo_selection") or {}
        photo_uri = resolve_photo(seq)
        finish = "photo" if photo_uri else G.finish_tag(seq, ps)[0]

        gsvc = G.GRAPHIC[seq]["svc"]
        base = f"{seq:02d}_{cshort}_{slug(gsvc)}"

        # --- gráfica standalone 1080x1080 ---
        canvas_html = G.canvas(seq, cshort, photo_uri, finish)
        html = PAGE.format(style=style, canvas=canvas_html)
        html_path = posts_dir / f"{base}.html"
        html_path.write_text(html, encoding="utf-8")
        manifest.append({"html": str(html_path), "png": str(posts_dir / f"{base}.png")})

        # --- copy por post ---
        c = G.COPY[post.content_id]
        body = f"{c['hook']}\n\n{c['body']}\n\n{c['cta']}"
        (copy_dir / f"{base}.txt").write_text(body + "\n", encoding="utf-8")
        subname = post.subtheme.get("nombre") if isinstance(post.subtheme, dict) else ""
        all_copy.append(
            f"{'='*70}\nPOST {seq:02d} · {cshort} · {subname}\n"
            f"Ancla: {post.content_id}  ·  Foto: {finish}\n{'='*70}\n\n{body}\n")

    (copy_dir / f"copy_{label}.txt").write_text("\n\n".join(all_copy), encoding="utf-8")

    # grilla de revisión (si ya fue generada por gen_month_grid)
    grid_src = ROOT / "plantilla_grilla_mes.html"
    if grid_src.exists():
        shutil.copy(grid_src, out / f"grilla_{label}.html")

    embedded = sum(1 for seq in range(1, 13) if resolve_photo(seq))
    (out / "README.txt").write_text(README.format(
        label=label, embedded=embedded, faltan=12 - embedded), encoding="utf-8")

    (build_root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"emit: {out} · {len(manifest)} posts · {embedded} con foto embebida")
    return out


README = """IDIEM · Bundle mensual — {label}
===================================================================

Contenido
-------------------------------------------------------------------
  posts/    12 gráficas terminadas a 1080x1080 px (PNG), formato
            Servicios (Plantilla 01). Listas para publicar.
  copy/     copy_{label}.txt  -> los 12 copies juntos.
            NN_CEL.txt        -> un copy por post, listo para pegar
                                 (hook + cuerpo + CTA, con # y emojis).
  grilla_{label}.html          Vista de revisión (copy editable) para
                                 abrir en el navegador.

Estado de las fotos
-------------------------------------------------------------------
  Con foto embebida en el PNG: {embedded} de 12.
  Sin foto (campo de marca sólido): {faltan}.

  Para completar las que faltan, deja el archivo de imagen en
  design_system/assets/month/ con el nombre pNN.jpg (o .png), donde
  NN es el número de post (p07.jpg, p08.jpg, ...), y vuelve a generar
  el bundle. La gráfica tomará esa foto automáticamente.

  - Fotos Muapi generadas: descárgalas desde su URL (en la grilla,
    "ver imagen generada") y guárdalas como pNN.jpg.
  - Fotos de librería pesadas (>4 MB): sube una versión liviana a la
    carpeta de Drive y se incrusta al regenerar.

Reglas (no negociables)
-------------------------------------------------------------------
  Cada post traza a su knowledge_id (2A.2 = fuente de verdad).
  Sin superlativos (GR-04). NAME_ONLY donde aplica.
  Los webinars son un agregado aparte: NO ocupan estos 12 espacios.
"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", default="2026-09")
    ap.add_argument("--build", default=None, help="directorio de build")
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args()
    build_root = Path(args.build) if args.build else (
        Path("/tmp/claude-0/-home-user-idiem-content-system/"
             "1c5b178b-f8ee-5946-beb8-9cf3fffd70df/scratchpad/bundle"))
    build_root.mkdir(parents=True, exist_ok=True)
    emit(args.month, build_root)
