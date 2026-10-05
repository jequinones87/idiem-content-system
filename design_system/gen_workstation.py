"""Workstation mensual — el artefacto como plataforma para desarrollar los posts.

Por cada post: la gráfica final (nítida, 1080px) arriba, y abajo los controles:
un solo recuadro de texto editable, un recuadro de notas de imagen + botón de
regeneración, y botones de descarga PNG/PDF. Las gráficas son clickeables
(lightbox) y los carruseles se revisan lámina por lámina.

Pipeline (3 pasos, encadenados por el runner):
  1) --emit   : escribe una HTML standalone por lámina + manifest.json + structure.json
  2) node render_bundle.cjs <build>/manifest.json  -> PNG 1080x1080 por lámina
  3) --build  : lee los PNG, los embebe (JPEG) y arma el artefacto con la UI + capacidades

Capacidades declaradas al publicar: {downloads:true} (PNG/PDF reales). La
regeneración de imagen NO puede llamar a Muapi desde el artefacto (no es conector
claude.ai): el botón guarda la nota y el usuario exporta los cambios para que
Claude regenere y republique.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import gen_month_grid as G          # noqa: E402
import carousel as CAR              # noqa: E402
from bundle_month import grid_style, resolve_photo  # noqa: E402

BUILD_DEFAULT = Path("/tmp/claude-0/-home-user-idiem-content-system/"
                     "1c5b178b-f8ee-5946-beb8-9cf3fffd70df/scratchpad/ws")

# Sustitución liviana: el pick top del motor pesa 8.3 MB (no descargable por el
# conector). Se usa su hermana de librería, misma célula/subtema, versión ~1080px.
PHOTO_SUB = {
    6:  {"photo_id": "PHO-0044", "orig": "PHO-0061",
         "fuente": "https://drive.google.com/file/d/1TMjf-mU8rJ-Ds-O2d1sP0ce9MHISjLUS/view",
         "detalle": "vigas de acero · casco IDIEM"},
    10: {"photo_id": "PHO-0013", "orig": "PHO-0040",
         "fuente": "https://drive.google.com/file/d/14Ad1dRP_Dfipr-C88kGtBVJL24KDdMOS/view",
         "detalle": "domo minero · dron"},
    3:  {"photo_id": "PHO-0085", "orig": "PHO-0091",
         "fuente": "https://drive.google.com/file/d/1xUlYXbYXjL1VpIvy_EewpWXAOSQtEWhQ/view",
         "detalle": "casco IDIEM · tablet · revisión", "reason": "foto original pixelada (329px)"},
    11: {"photo_id": "PHO-0095", "orig": "PHO-0004",
         "fuente": "https://drive.google.com/file/d/13ZKXpQ0kMFr0j7TVW7Jl8CIrL3DGOanJ/view",
         "detalle": "edificio en construcción (Costanera)", "reason": "cambio pedido"},
    1:  {"photo_id": "PHO-0058", "orig": "Adobe Stock #212862972",
         "fuente": "https://drive.google.com/file/d/1KnC9RDEQUNZMxWX28rphzN2EGLz1ZNOl/view",
         "detalle": "ejecutivo con laptop · planos", "reason": "cambio pedido: foto de librería"},
    7:  {"photo_id": "equipo_acustica_FA-1", "orig": "Adobe Stock #204006589",
         "fuente": "https://drive.google.com/file/d/19uVCrI97li6szs65HJaT8FdOTe3lZZpK/view",
         "detalle": "equipo de acústica en terreno (foto propia)", "reason": "cambio pedido: foto propia de faena"},
    8:  {"photo_id": "Tuberia_HDPE_END_ACERO4", "orig": "Adobe Stock #1614411840",
         "fuente": "https://drive.google.com/file/d/1sHwdzCXyJeneC35woSwz8DkT8qKH3fXp/view",
         "detalle": "END en tubería HDPE (foto propia)", "reason": "cambio pedido: foto propia de faena"},
    9:  {"photo_id": "generica_ejecutivos_casco_construccion", "orig": "Adobe Stock #212862972",
         "fuente": "https://drive.google.com/file/d/1_eczAWE2nzda5yfFx_jV23xorWODv8cG/view",
         "detalle": "ejecutivos con casco · apretón de manos en obra", "reason": "cambio pedido: foto de librería"},
}

# Fotos Adobe Stock licenciadas (tier libre) para los posts sin foto de librería
# adecuada (antes marcados Muapi). Descargadas, comprimidas a 1080px y usadas
# localmente; foto real y trazable, sin depender de un CDN externo.
STOCK_SUB = {
    12: {"id": "340172893",  "detalle": "END por ultrasonido en soldadura"},
}

# Sello de certificación Green Hospital (propia de IDIEM), overlay esquina inf-der del post 5.
GH_SEAL = ("data:image/png;base64," +
           base64.b64encode((ROOT / "assets" / "green_hospital_logo.png").read_bytes()).decode())

# seq -> historial de cambios que YO (Claude) apliqué y republiqué, más reciente
# primero. Alimenta el chip de estado "publicado · fecha" y el bloque "Historial"
# de cada post. Espeja la bitácora de docs/09_EDITORIAL_MEMORY.md.
APPLIED_LOG = {
    1:  [{"date": "2026-08-28", "summary": "Copy reescrito (MKT) + foto laptop/planos"},
         {"date": "2026-08-24", "summary": "Foto de acuerdo/ejecutivos (previa)"}],
    2:  [{"date": "2026-08-28", "summary": "Carrusel reformulado: causa-origen, estructural/mecánico, estudio de riesgo"},
         {"date": "2026-08-28", "summary": "Copy reescrito + orden de láminas (incendios → fallas)"}],
    3:  [{"date": "2026-08-24", "summary": "Foto casco + tablet (se corrigió la pixelada)"}],
    5:  [{"date": "2026-08-28", "summary": "Sello Green Hospital 50% más grande, detrás del círculo"},
         {"date": "2026-08-28", "summary": "Sello Green Hospital más grande (¼ del lienzo), detrás del círculo"},
         {"date": "2026-08-28", "summary": "Copy (sin Salud sin Daño, ISO 50001) + sello Green Hospital"}],
    6:  [{"date": "2026-08-21", "summary": "Foto vigas de acero / casco IDIEM"}],
    7:  [{"date": "2026-08-28", "summary": "Círculo movido a la derecha (se ve el equipo de acústica)"},
         {"date": "2026-08-28", "summary": "Copy (estudio de impacto, D.D. 14/24) + foto propia de acústica"}],
    8:  [{"date": "2026-08-28", "summary": "Foto propia de faena (tubería HDPE)"}],
    9:  [{"date": "2026-08-28", "summary": "Reencuadre para que el círculo no tape la cara"},
         {"date": "2026-08-28", "summary": "Foto → ejecutivos con casco, apretón de manos en obra (librería)"},
         {"date": "2026-08-28", "summary": "Foto de acuerdo / apretón de manos"}],
    10: [{"date": "2026-08-21", "summary": "Foto domo minero / dron"}],
    11: [{"date": "2026-08-24", "summary": "Foto edificio en construcción (Costanera)"}],
    12: [{"date": "2026-08-28", "summary": "Título de gráfica → “Detectar antes de fallar”"},
         {"date": "2026-08-28", "summary": "Gráfica: soldaduras inspeccionadas por muestreo"}],
    13: [{"date": "2026-08-28", "summary": "Foto → bandera chilena + camión minero (librería)"},
         {"date": "2026-08-28", "summary": "Creación — saludo Fiestas Patrias"}],
}
NEW_POSTS = {13}  # posts creados nuevos (chip "nuevo")


def _fmt_date(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{d}-{m}-{y}"


def status_chip(seq: int) -> str:
    """Chip de estado inicial (lo actualiza el JS según el trabajo del revisor)."""
    log = APPLIED_LOG.get(seq) or []
    last = _fmt_date(log[0]["date"]) if log else ""
    label = f"publicado · {last}" if last else "sin cambios"
    return (f'<span class="statuschip pub" data-applied="{last}">{label}</span>')


def history_html(seq: int) -> str:
    log = APPLIED_LOG.get(seq) or []
    if not log:
        return ""
    items = "".join(
        f'<li><span class="hd">{_fmt_date(e["date"])}</span>'
        f'<span class="hs">{G.esc(e["summary"])}</span></li>'
        for e in log)
    return (f'<details class="hist"><summary>Historial de cambios aplicados '
            f'({len(log)})</summary><ul class="histlist">{items}</ul></details>')

# Posts institucionales que NO vienen del motor (no trazan a knowledge_id). Se
# arman aparte y se anexan después de los 12. Foto de fondo (estilo Plantilla 02).
SPECIAL = [{
    "seq": 13,
    "content_id": "SALUDO-FIESTAS-PATRIAS-2026-09",
    "cshort": "SALUDO",
    "subtheme": "Fiestas Patrias · institucional",
    "fmt": "SALUDO",
    "photo": "p13.jpg",
    "kicker": "FELICES FIESTAS PATRIAS",
    "title": 'Presentes en la<br>historia de <span class="fpred">Chile</span>.',
    "sub": "Aportamos ciencia e ingeniería al desarrollo de la infraestructura del país.",
    "copy": {
        "hook": "🇨🇱 Este 18 de septiembre celebramos a Chile y a las personas que lo construyen cada día.",
        "body": ("A lo largo de nuestra historia, en IDIEM hemos acompañado el desarrollo de la "
                 "infraestructura del país: aportando ciencia, ensayos e ingeniería al servicio de obras "
                 "que sostienen la vida de las personas.\n\n"
                 "Caminos, hospitales, edificios y faenas que ayudamos a hacer más seguros y confiables "
                 "también son parte de la historia de Chile. 🏗️"),
        "cta": "¡Felices Fiestas Patrias! 🇨🇱\n\n#IDIEM #FiestasPatrias #Chile #Ingeniería #Infraestructura",
    },
    "trace": ("Saludo institucional — pieza conmemorativa que <strong>no traza a un knowledge_id</strong>. "
              "Mensaje general, sin afirmaciones específicas de proyectos, fechas ni cifras."),
}]
SPECIAL_BY_CID = {s["content_id"]: s for s in SPECIAL}

FIESTAS_CSS = r'''
.fpslide{color:#fff;background:var(--gray-dark)}
.fpphoto{position:absolute;inset:0;z-index:0;background-size:cover;background-position:50% 40%}
.fpveil{position:absolute;inset:0;z-index:1;background:linear-gradient(0deg,rgba(9,11,12,.88) 6%,rgba(9,11,12,.28) 48%,rgba(9,11,12,.52) 100%)}
.fpwrap{position:absolute;z-index:3;left:6cqw;right:6cqw;bottom:8.5cqw;display:flex;flex-direction:column;gap:2.6cqw}
.fpkick{font-size:2.5cqw;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:#fff;opacity:.96}
.fprule{width:12cqw;height:.7cqw;background:var(--red);border-radius:2px}
.fptitle{font-size:6.8cqw;font-weight:800;line-height:1.03;letter-spacing:-.02em;text-shadow:0 2px 18px rgba(0,0,0,.55)}
.fptitle .fpred{color:var(--red)}
.fpsub{font-size:3.1cqw;font-weight:500;line-height:1.34;color:rgba(255,255,255,.93);max-width:80cqw}
'''


def fiestas_html(photo_uri: str | None, s: dict) -> str:
    photo = photo_uri or ""
    return f'''<div class="canvas fpslide" data-finish="photo">
  <div class="fpphoto" style="background-image:url('{photo}')"></div>
  <div class="fpveil"></div>
  <img class="c2slogan" src="{G.SLOGAN}" alt="Elige bien. Elige idiem.">
  <img class="c2logo" src="{G.LOGO}" alt="Logo IDIEM">
  <div class="fpwrap">
    <div class="fpkick">{s["kicker"]}</div>
    <div class="fprule"></div>
    <div class="fptitle">{s["title"]}</div>
    <div class="fpsub">{G.esc(s["sub"])}</div>
  </div>
</div>'''


def mod_badge(seq: int) -> str:
    """Chip mínimo esquina sup-der: si el post fue modificado y cuándo."""
    if seq in NEW_POSTS:
        return '<span class="modbadge new">★ nuevo</span>'
    d = MODIFIED.get(seq)
    if d:
        y, m, day = d.split("-")
        return f'<span class="modbadge on">✎ {day}-{m}-{y}</span>'
    return '<span class="modbadge">sin cambios</span>'


PAGE = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap">
<style>{style}{carcss}{fpcss}</style>
<style>
  html,body{{margin:0;padding:0;background:#0a0c0d}}
  .export{{width:1080px;height:1080px;position:relative;overflow:hidden}}
  .export .canvas{{width:1080px !important;height:1080px !important;border-radius:0 !important;box-shadow:none !important}}
</style></head>
<body><div class="export">{canvas}</div></body></html>"""


def post_slides(seq: int, post) -> list[str]:
    cshort = G.CELL_SHORT.get(post.cell, post.cell[:3].upper())
    ps = (post.graphic_brief or {}).get("photo_selection") or {}
    photo_uri = resolve_photo(seq)
    finish = "photo" if photo_uri else G.finish_tag(seq, ps)[0]
    if seq in CAR.CAROUSEL_POSTS:
        # Carrusel: portada + intermedias + cierre, todo con foto de fondo (Plantilla 02).
        return CAR.build_slides(seq, photo_uri, G.LOGO, G.SLOGAN)
    # Estático: pieza Servicios (círculo rojo). Post 5 lleva sello Green Hospital;
    # post 7 mueve el círculo a la derecha para dejar ver el equipo de acústica.
    corner = GH_SEAL if seq == 5 else None
    side = "right" if seq == 7 else "left"
    return [G.canvas(seq, cshort, photo_uri, finish, corner_logo=corner, side=side)]


def emit(month: str, build: Path) -> None:
    build.mkdir(parents=True, exist_ok=True)
    posts_dir = build / "slides"
    posts_dir.mkdir(exist_ok=True)
    kb = G.load_knowledge_base()
    review = G.compose_month(kb, month, target_count=12)
    for cid, c in G.COPY.items():
        G.set_post_copy(review, cid, c)

    style = grid_style()
    manifest, structure = [], []
    for seq, post in enumerate(review.posts, 1):
        slides = post_slides(seq, post)
        pngs = []
        for idx, canvas_html in enumerate(slides):
            html = PAGE.format(style=style, carcss=CAR.CAROUSEL_CSS, fpcss=FIESTAS_CSS, canvas=canvas_html)
            hp = posts_dir / f"p{seq:02d}_s{idx}.html"
            pp = posts_dir / f"p{seq:02d}_s{idx}.png"
            hp.write_text(html, encoding="utf-8")
            manifest.append({"html": str(hp), "png": str(pp)})
            pngs.append(str(pp))
        structure.append({"seq": seq, "cid": post.content_id, "pngs": pngs})

    # Posts institucionales (no del motor): se anexan después de los 12.
    for s in SPECIAL:
        seq = s["seq"]
        photo_uri = resolve_photo(seq)
        html = PAGE.format(style=style, carcss=CAR.CAROUSEL_CSS, fpcss=FIESTAS_CSS,
                           canvas=fiestas_html(photo_uri, s))
        hp = posts_dir / f"p{seq:02d}_s0.html"
        pp = posts_dir / f"p{seq:02d}_s0.png"
        hp.write_text(html, encoding="utf-8")
        manifest.append({"html": str(hp), "png": str(pp)})
        structure.append({"seq": seq, "cid": s["content_id"], "pngs": [str(pp)]})

    (build / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), "utf-8")
    (build / "structure.json").write_text(json.dumps(structure, ensure_ascii=False), "utf-8")
    print(f"emit: {len(structure)} posts, {len(manifest)} láminas -> {build}")


def jpeg_uri(png_path: str, q: int = 86) -> str:
    from PIL import Image
    im = Image.open(png_path).convert("RGB")
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def build(month: str, build_dir: Path, out_path: Path) -> None:
    kb = G.load_knowledge_base()
    review = G.compose_month(kb, month, target_count=12)
    for cid, c in G.COPY.items():
        G.set_post_copy(review, cid, c)
    posts = {p.content_id: p for p in review.posts}
    structure = json.loads((build_dir / "structure.json").read_text("utf-8"))

    cards = []
    for st in structure:
        seq, cid = st["seq"], st["cid"]
        uris = [jpeg_uri(p) for p in st["pngs"]]
        if cid in SPECIAL_BY_CID:
            cards.append(render_special_card(SPECIAL_BY_CID[cid], uris))
        else:
            cards.append(render_card(seq, posts[cid], uris))

    page = ARTIFACT.replace("__CARDS__", "\n".join(cards))
    css = (ROOT / "workstation_shared" / "workstation_ui.css").read_text(encoding="utf-8")
    js = (ROOT / "workstation_shared" / "workstation_ui.js").read_text(encoding="utf-8")
    cfg = json.dumps({"key": "idiem_ws_sep2026_v5",
                      "wsUrl": "https://claude.ai/code/artifact/f9016145-d797-4a02-867e-1e478de62a6b",
                      "exportMonth": "2026-09", "exportTag": "sep2026", "ccMax": 900}, ensure_ascii=False)
    html = page.replace("__CSS__", css).replace("__JS__", js).replace("__CFG__", cfg)
    out_path.write_text(html, encoding="utf-8")
    print(f"build: {out_path} ({out_path.stat().st_size//1024} KB, {len(structure)} posts)")


def render_card(seq: int, post, uris: list[str]) -> str:
    cshort = G.CELL_SHORT.get(post.cell, post.cell[:3].upper())
    sub = post.subtheme if isinstance(post.subtheme, dict) else {}
    subname = sub.get("nombre", "") if isinstance(sub, dict) else ""
    gb = post.graphic_brief or {}
    ps = gb.get("photo_selection") or {}
    fmt = gb.get("recommended_format") or "STATIC"
    is_car = seq in CAR.CAROUSEL_POSTS
    n = len(uris)
    fmt_label = f"CARRUSEL · {n} láminas" if is_car else "STATIC"

    c = G.COPY[post.content_id]
    full_copy = f"{c['hook']}\n\n{c['body']}\n\n{c['cta']}"

    ev = gb.get("evidence_ids") or []
    ev_codes = " · ".join(f"<code>{G.esc(e)}</code>" for e in ev[:4]) or f"<code>{G.esc(post.knowledge_id)}</code>"

    src = ps.get("source")
    if seq in PHOTO_SUB:
        s = PHOTO_SUB[seq]
        reason = s.get("reason", "original 8.3 MB, no descargable por el conector")
        foto = (f'Librería · <code>{s["photo_id"]}</code> ({G.esc(s["detalle"])}) · '
                f'<a href="{G.esc(s["fuente"])}" target="_blank" rel="noopener">ver en Drive</a>'
                f'<br><span class="muprompt">reemplaza a <code>{s["orig"]}</code> '
                f'({G.esc(reason)})</span>')
    elif seq in STOCK_SUB:
        s = STOCK_SUB[seq]
        foto = (f'Adobe Stock · <code>#{s["id"]}</code> ({G.esc(s["detalle"])}) · licencia libre'
                f'<br><span class="muprompt">foto licenciada e incrustada (reemplaza el placeholder Muapi)</span>')
    elif src == "library":
        foto = f'Librería · <code>{G.esc(ps.get("photo_id",""))}</code> · <a href="{G.esc(ps.get("fuente",""))}" target="_blank" rel="noopener">ver en Drive</a>'
    elif src == "muapi":
        foto = 'Muapi (generada) — pendiente de incrustar (deja <code>assets/month/p%02d.jpg</code>)' % seq
    else:
        foto = 'Sin foto por diseño (<code>needs_photo=false</code>)'

    # tira de láminas (solo carrusel)
    strip = ""
    if is_car:
        thumbs = "".join(
            f'<img class="thumb{" on" if i==0 else ""}" src="{u}" data-idx="{i}" alt="lámina {i+1}">'
            for i, u in enumerate(uris))
        strip = f'<div class="strip">{thumbs}</div>'

    # data de láminas para JS (idx -> uri en orden)
    slides_json = G.esc(json.dumps(uris))

    return f'''<article class="post" data-seq="{seq}" data-cid="{G.esc(post.content_id)}" data-car="{"1" if is_car else "0"}" data-status="publicado" data-edited-at="" data-edited-by="" data-caltitle="Post {seq:02d}">
  <script type="application/json" class="slides-data">{slides_json}</script>
  <div class="graphic">
    <div class="gwrap">
      <img class="main" src="{uris[0]}" data-idx="0" alt="Post {seq:02d}">
      <span class="fmtbadge">{fmt_label}</span>
      {status_chip(seq)}
      <div class="botleft">
        <span class="ap-badge" hidden>✅ Aprobado</span>
        <span class="cal-badge" hidden>📅</span>
        <span class="li-badge" hidden>🔗 En LinkedIn</span>
      </div>
      <span class="zoomhint">clic para ampliar</span>
    </div>
    {strip}
  </div>
  <div class="controls">
    <div class="chead"><span class="seq">{seq:02d}</span><span class="badge">{cshort}</span>
      <span class="badge ghost">{G.esc(fmt)}</span><span class="sub">{G.esc(subname)}</span></div>

    <label class="lab">Texto del post <span class="hint">— editable, se guarda en tu navegador</span>
      <span class="cc" data-cc>0 / 900</span>
      <button class="revert" type="button" data-field="copy" hidden>↺ volver a lo publicado</button></label>
    <textarea class="copy" data-cid="{G.esc(post.content_id)}" spellcheck="false">{G.esc(full_copy)}</textarea>

    <label class="lab">Cambios en la imagen / gráfica
      <button class="revert" type="button" data-field="note" hidden>↺ limpiar</button></label>
    <textarea class="imgnote" data-cid="{G.esc(post.content_id)}" spellcheck="false"
      placeholder="Ej.: cambiar la foto por una de faena real; achicar el titular; usar otra lámina de cierre…"></textarea>

    <div class="editline"></div>

    <div class="btns">
      <button class="btn ready" type="button">✓ Marcar listo para aplicar</button>
      <button class="btn approve" type="button">✅ Aprobar para publicar</button>
      <button class="btn linkedin" type="button">🔗 Marcar subido a LinkedIn</button>
      <button class="btn regen" type="button">🔄 Solicitar regeneración</button>
      <button class="btn ghost png" type="button">Descargar PNG</button>
      <button class="btn ghost pdf" type="button">Descargar PDF</button>
      <button class="btn ghost copybtn" type="button">Copiar texto</button>
    </div>

    <label class="lab">Fecha de publicación <span class="hint">— agéndala en tu Google Calendar</span>
      <button class="calclear" type="button" hidden>↺ quitar fecha</button></label>
    <div class="calrow">
      <input type="date" class="caldate" aria-label="Fecha de publicación">
      <input type="time" class="caltime" value="09:00" aria-label="Hora de publicación">
      <a class="btn cal off" target="_blank" rel="noopener">📅 Agendar en Google Calendar</a>
    </div>

    <div class="trace">
      <div class="tr"><span class="k">Ancla</span><span class="v"><code>{G.esc(post.content_id)}</code></span></div>
      <div class="tr"><span class="k">Evidencia</span><span class="v">{ev_codes}</span></div>
      <div class="tr"><span class="k">Foto</span><span class="v">{foto}</span></div>
    </div>
    {history_html(seq)}
  </div>
</article>'''


def render_special_card(s: dict, uris: list[str]) -> str:
    seq = s["seq"]
    c = s["copy"]
    full_copy = f"{c['hook']}\n\n{c['body']}\n\n{c['cta']}"
    slides_json = G.esc(json.dumps(uris))
    foto = ('Librería · <code>generica_bandera_chile_mineria</code> (bandera chilena + camión minero) · '
            '<a href="https://drive.google.com/file/d/18Vlym9diMd7rcuAbaWvFMapzAF491biH/view" target="_blank" rel="noopener">ver en Drive</a>'
            '<br><span class="muprompt">pieza conmemorativa de Fiestas Patrias (reemplaza a La Moneda)</span>')
    return f'''<article class="post special" data-seq="{seq}" data-cid="{G.esc(s["content_id"])}" data-car="0" data-status="publicado" data-edited-at="" data-edited-by="" data-caltitle="Post {seq:02d}">
  <script type="application/json" class="slides-data">{slides_json}</script>
  <div class="graphic">
    <div class="gwrap">
      <img class="main" src="{uris[0]}" data-idx="0" alt="Post {seq:02d}">
      <span class="fmtbadge">SALUDO · FIESTAS PATRIAS</span>
      {status_chip(seq)}
      <div class="botleft">
        <span class="ap-badge" hidden>✅ Aprobado</span>
        <span class="cal-badge" hidden>📅</span>
        <span class="li-badge" hidden>🔗 En LinkedIn</span>
      </div>
      <span class="zoomhint">clic para ampliar</span>
    </div>
  </div>
  <div class="controls">
    <div class="chead"><span class="seq">{seq:02d}</span><span class="badge">{G.esc(s["cshort"])}</span>
      <span class="badge ghost">{G.esc(s["fmt"])}</span><span class="sub">{G.esc(s["subtheme"])}</span></div>

    <label class="lab">Texto del post <span class="hint">— editable, se guarda en tu navegador</span>
      <span class="cc" data-cc>0 / 900</span>
      <button class="revert" type="button" data-field="copy" hidden>↺ volver a lo publicado</button></label>
    <textarea class="copy" data-cid="{G.esc(s["content_id"])}" spellcheck="false">{G.esc(full_copy)}</textarea>

    <label class="lab">Cambios en la imagen / gráfica
      <button class="revert" type="button" data-field="note" hidden>↺ limpiar</button></label>
    <textarea class="imgnote" data-cid="{G.esc(s["content_id"])}" spellcheck="false"
      placeholder="Ej.: cambiar la foto; ajustar el saludo…"></textarea>

    <div class="editline"></div>

    <div class="btns">
      <button class="btn ready" type="button">✓ Marcar listo para aplicar</button>
      <button class="btn approve" type="button">✅ Aprobar para publicar</button>
      <button class="btn linkedin" type="button">🔗 Marcar subido a LinkedIn</button>
      <button class="btn regen" type="button">🔄 Solicitar regeneración</button>
      <button class="btn ghost png" type="button">Descargar PNG</button>
      <button class="btn ghost pdf" type="button">Descargar PDF</button>
      <button class="btn ghost copybtn" type="button">Copiar texto</button>
    </div>

    <label class="lab">Fecha de publicación <span class="hint">— agéndala en tu Google Calendar</span>
      <button class="calclear" type="button" hidden>↺ quitar fecha</button></label>
    <div class="calrow">
      <input type="date" class="caldate" aria-label="Fecha de publicación">
      <input type="time" class="caltime" value="09:00" aria-label="Hora de publicación">
      <a class="btn cal off" target="_blank" rel="noopener">📅 Agendar en Google Calendar</a>
    </div>

    <div class="trace">
      <div class="tr"><span class="k">Ancla</span><span class="v"><code>{G.esc(s["content_id"])}</code></span></div>
      <div class="tr"><span class="k">Nota</span><span class="v">{s["trace"]}</span></div>
      <div class="tr"><span class="k">Foto</span><span class="v">{foto}</span></div>
    </div>
    {history_html(seq)}
  </div>
</article>'''


ARTIFACT = r'''<title>Workstation Septiembre IDIEM</title>
<meta name="description" content="Plataforma de desarrollo de los 12 posts de septiembre de IDIEM: gráfica por post, texto editable, notas de imagen con regeneración, descarga PNG/PDF y revisión de carruseles.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap">
<style>
[hidden]{display:none!important}
__CSS__
</style>

<div class="wrap">
  <p class="eyebrow"><span class="dot"></span>IDIEM · Design System · Workstation</p>
  <h1>Septiembre — <b>12 posts + saludo Fiestas Patrias</b></h1>
  <p class="lede">Cada post muestra su <strong>estado</strong> en la esquina de la gráfica: <b class="tpub">publicado</b> (lo que ya apliqué), <b class="tpend">pendiente</b> (lo editaste, aún sin aplicar) o <b class="tready">listo para aplicar</b> (lo marcaste tú). Abajo tienes el texto editable, notas de imagen, el <strong>historial</strong> de lo aplicado, y <strong>↺ volver a lo publicado</strong>. Todo lo que marcas se <strong>sincroniza en vivo con el equipo</strong>: aprueba (<strong>✅ Aprobado para publicar</strong>), agenda la fecha, y marca <strong>🔗 subido a LinkedIn</strong> una vez publicado (flujo: <b class="tpub">revisado → aprobado → agendado → subido</b>). No necesitas guardar: se guarda solo.</p>
  <div class="bar">
    <input class="idfield" id="revName" type="text" placeholder="Tu nombre" autocomplete="name" spellcheck="false">
    <input class="idfield" id="revRole" type="text" placeholder="Especialidad / área (opcional)" spellcheck="false">
    <span class="syncstate" id="syncState" data-mode="init">Conectando…</span>
    <button class="xbtn ghost export" type="button">Descargar respaldo (JSON)</button>
    <span class="savehint" id="savehint">Tus cambios se guardan y comparten con el equipo automáticamente.</span>
  </div>
  <div class="dash">
    <div class="counts">
      <span class="ct pend"><b id="nPend">0</b> pendientes</span>
      <span class="ct ready"><b id="nReady">0</b> listos para aplicar</span>
      <span class="ct pub"><b id="nPub">0</b> publicados</span>
      <span class="ct appr">✅ <b id="nApproved">0</b>/<span id="nApTotal">0</span> aprobados</span>
      <span class="ct sched">📅 <b id="nSched">0</b>/<span id="nSchTotal">0</span> agendados</span>
      <span class="libox">🔗 <b id="nLinked">0</b>/<span id="nTotal">0</span> subidos a LinkedIn</span>
    </div>
    <div class="filters" id="filters">
      <button class="fchip on" type="button" data-f="todos">Todos</button>
      <button class="fchip" type="button" data-f="pendiente">Pendientes</button>
      <button class="fchip" type="button" data-f="listo">Listos</button>
      <button class="fchip" type="button" data-f="publicado">Publicados</button>
    </div>
    <button class="litoggle" type="button" id="liToggle">Ocultar los ya subidos</button>
    <button class="jumpnext" type="button" id="jumpNext">Ir al siguiente pendiente ↓</button>
  </div>

  <div class="grid">
__CARDS__
  </div>

  <div class="foot">
    <span>Motor: <code>compose_month(2026-09)</code> · copy validado con <code>ingest_draft</code>.</span>
    <span>2A.2 = fuente de verdad · GR-04 sin superlativos · NAME_ONLY.</span>
    <span>Regeneración de imagen: la aplica Claude (Muapi/librería) al recibir el export.</span>
  </div>
</div>

<script id="ws-state" type="application/json">{}</script>
<div class="lb" id="lb">
  <button class="close" id="lbClose" aria-label="cerrar">✕</button>
  <img id="lbImg" alt="">
  <div class="lbbar">
    <button class="nav" id="lbPrev" aria-label="anterior">‹</button>
    <span class="count" id="lbCount"></span>
    <button class="nav" id="lbNext" aria-label="siguiente">›</button>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>window.WSCFG=__CFG__;</script>
<script>
__JS__
</script>'''


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", default="2026-09")
    ap.add_argument("--build", default=str(BUILD_DEFAULT))
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--assemble", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "plantilla_workstation_mes.html"))
    args = ap.parse_args()
    bd = Path(args.build)
    if args.emit:
        emit(args.month, bd)
    if args.assemble:
        build(args.month, bd, Path(args.out))
