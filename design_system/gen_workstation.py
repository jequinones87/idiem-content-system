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
import tempfile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import gen_month_grid as G          # noqa: E402
import carousel as CAR              # noqa: E402
from bundle_month import grid_style, resolve_photo  # noqa: E402

BUILD_DEFAULT = Path(tempfile.gettempdir()) / "idiem_ws_build"

# Sustitución liviana: el pick top del motor pesa 8.3 MB (no descargable por el
# conector). Se usa su hermana de librería, misma célula/subtema, versión ~1080px.
# seq -> foto de librería incrustada. Vacío al iniciar el mes: las piezas parten
# con campo de marca sólido y Kike pide las fotos (Drive) en la workstation.
PHOTO_SUB = {}

# Fotos Adobe Stock licenciadas (tier libre) para los posts sin foto de librería
# adecuada (antes marcados Muapi). Descargadas, comprimidas a 1080px y usadas
# localmente; foto real y trazable, sin depender de un CDN externo.
# Fotos Adobe Stock licenciadas. Sin stock este mes.
STOCK_SUB = {}

# Sello de certificación Green Hospital (propia de IDIEM), overlay esquina inf-der del post 5.
GH_SEAL = ("data:image/png;base64," +
           base64.b64encode((ROOT / "assets" / "green_hospital_logo.png").read_bytes()).decode())

# seq -> historial de cambios que YO (Claude) apliqué y republiqué, más reciente
# primero. Alimenta el chip de estado "publicado · fecha" y el bloque "Historial"
# de cada post. Espeja la bitácora de docs/09_EDITORIAL_MEMORY.md.
# seq -> historial de cambios aplicados y republicados (más reciente primero).
# Octubre parte sin historial; se irá poblando a medida que se apliquen rondas.
APPLIED_LOG = {}

NEW_POSTS = set()  # chip "nuevo" (no usado en la tarjeta actual)

# Estado "sembrado" en el ws-state embebido. En un mes nuevo va en False: el tablero
# arranca limpio (nada aprobado/subido) y la DB del artefacto es la fuente de verdad
# del estado compartido. Sólo se pone en True para "congelar" un mes ya cerrado como
# fallback offline (fue el caso de septiembre 2026).
SEED_ALL_DONE = False


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
# Posts institucionales que NO trazan a knowledge_id (saludos). Octubre no lleva:
# las 3 efemérides (Arquitectura, RRD, Geólogo) están DENTRO de los 12 y trazan a 2A.2.
SPECIAL = []

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
    return [G.canvas(seq, cshort, photo_uri, finish, corner_logo=None, side="left")]


def emit(month: str, build: Path) -> None:
    build.mkdir(parents=True, exist_ok=True)
    posts_dir = build / "slides"
    posts_dir.mkdir(exist_ok=True)
    kb = G.load_knowledge_base()
    review = G.compose_current(kb)

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
    review = G.compose_current(kb)
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

    html = ARTIFACT.replace("__CARDS__", "\n".join(cards))
    if SEED_ALL_DONE:
        seed = {st["cid"]: {"approved": True, "approvedAt": None,
                            "posted": True, "postedAt": None}
                for st in structure}
        html = html.replace(
            '<script id="ws-state" type="application/json">{}</script>',
            '<script id="ws-state" type="application/json">'
            + json.dumps(seed, ensure_ascii=False) + '</script>')
    out_path.write_text(html, encoding="utf-8")
    print(f"build: {out_path} ({out_path.stat().st_size//1024} KB, {len(structure)} posts, "
          f"seed={'all-done' if SEED_ALL_DONE else 'empty'})")


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

    return f'''<article class="post" data-seq="{seq}" data-cid="{G.esc(post.content_id)}" data-car="{"1" if is_car else "0"}" data-status="publicado" data-edited-at="" data-edited-by="" data-caltitle="{G.esc(f"Post {seq:02d} · {subname}" if subname else f"Post {seq:02d}")}">
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
    return f'''<article class="post special" data-seq="{seq}" data-cid="{G.esc(s["content_id"])}" data-car="0" data-status="publicado" data-edited-at="" data-edited-by="" data-caltitle="{G.esc(f'Post {seq:02d} · {s["subtheme"]}')}">
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


ARTIFACT = r'''<title>Workstation Octubre IDIEM</title>
<meta name="description" content="Plataforma de desarrollo de los 12 posts de octubre de IDIEM: gráfica por post, texto editable, notas de imagen con regeneración, descarga PNG/PDF y revisión de carruseles.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap">
<style>
:root{
  --red:#e1261d;--gray-blue:#666d72;--gray-dark:#2f3030;--gray-light:#efefef;
  --ink:#22262a;--paper:#f2f2ef;--card:#ffffff;--line:rgba(47,48,48,.13);
  --muted:#6a7075;--shadow:0 20px 50px -26px rgba(47,48,48,.42);--mono:"Montserrat",system-ui,sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --ink:#eef0f0;--paper:#141617;--card:#1d2021;--gray-light:#282b2c;
  --line:rgba(239,239,239,.14);--muted:#9aa1a5;--shadow:0 24px 64px -30px rgba(0,0,0,.78);
}}
:root[data-theme="dark"]{
  --ink:#eef0f0;--paper:#141617;--card:#1d2021;--gray-light:#282b2c;
  --line:rgba(239,239,239,.14);--muted:#9aa1a5;--shadow:0 24px 64px -30px rgba(0,0,0,.78);
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:var(--mono);background:var(--paper);color:var(--ink);line-height:1.5;
  padding:clamp(18px,3.5vw,52px) clamp(14px,3.5vw,44px) 90px}
.wrap{max-width:1180px;margin:0 auto}
.eyebrow{display:inline-flex;align-items:center;gap:.6em;font-size:.72rem;font-weight:700;
  letter-spacing:.22em;text-transform:uppercase;color:var(--red);margin:0 0 12px}
.eyebrow .dot{width:.5em;height:.5em;border-radius:50%;background:var(--red)}
h1{font-size:clamp(1.8rem,4vw,2.7rem);font-weight:800;letter-spacing:-.02em;line-height:1.04;margin:0 0 .4rem}
h1 b{color:var(--red)}
.lede{font-size:clamp(1rem,1.6vw,1.13rem);color:var(--muted);max-width:74ch;margin:0 0 18px}
.bar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:0 0 26px}
.bar .savehint{font-size:.76rem;color:var(--muted)}
.syncstate{font-family:inherit;font-size:.74rem;font-weight:700;color:var(--muted);border:1px solid var(--line);border-radius:100px;padding:6px 12px;display:inline-flex;align-items:center;gap:.4em;white-space:nowrap}
.syncstate[data-mode="sync"]{color:#15803d;border-color:rgba(21,128,61,.4);background:rgba(21,128,61,.08)}
.syncstate[data-mode="local"]{color:#c6780a;border-color:rgba(198,120,10,.4);background:rgba(198,120,10,.08)}
.xbtn{font-family:inherit;font-size:.8rem;font-weight:700;color:#fff;background:var(--gray-dark);border:0;
  padding:8px 16px;border-radius:100px;cursor:pointer}
.xbtn.on{background:var(--red)}
.idfield{font-family:inherit;font-size:.82rem;color:var(--ink);background:var(--card);border:1px solid var(--line);
  border-radius:100px;padding:8px 14px;min-width:150px}
.idfield:focus{outline:2px solid var(--red);outline-offset:1px}

.grid{display:grid;grid-template-columns:1fr;gap:24px}
@media(min-width:900px){.grid{grid-template-columns:1fr 1fr}}
.post{background:var(--card);border:1px solid var(--line);border-radius:16px;overflow:hidden;box-shadow:var(--shadow);display:flex;flex-direction:column}
.post.flag{outline:2px solid var(--red);outline-offset:-2px}
.graphic{padding:16px 16px 0}
.gwrap{position:relative;border-radius:10px;overflow:hidden;cursor:zoom-in;box-shadow:0 8px 22px -12px rgba(0,0,0,.5)}
.gwrap .main{display:block;width:100%;aspect-ratio:1/1;object-fit:cover}
.fmtbadge{position:absolute;top:10px;left:10px;font-size:.66rem;font-weight:800;letter-spacing:.08em;color:#fff;background:rgba(0,0,0,.55);padding:4px 10px;border-radius:100px;backdrop-filter:blur(3px)}
.zoomhint{position:absolute;bottom:10px;right:10px;font-size:.64rem;font-weight:700;color:#fff;background:rgba(0,0,0,.5);padding:4px 9px;border-radius:100px;opacity:0;transition:opacity .15s}
.gwrap:hover .zoomhint{opacity:1}
.modbadge{position:absolute;top:10px;right:10px;font-size:.6rem;font-weight:800;letter-spacing:.03em;color:#fff;background:rgba(0,0,0,.5);padding:4px 9px;border-radius:100px;backdrop-filter:blur(3px)}
.modbadge.on{background:rgba(225,38,29,.92)}
.modbadge.new{background:rgba(21,128,61,.95)}
/* estado por post */
.statuschip{position:absolute;top:10px;right:10px;font-size:.6rem;font-weight:800;letter-spacing:.03em;color:#fff;background:rgba(0,0,0,.55);padding:4px 9px;border-radius:100px;backdrop-filter:blur(3px);max-width:70%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.statuschip.pub{background:rgba(45,50,52,.82)}
.statuschip.pend{background:rgba(198,120,10,.95)}
.statuschip.ready{background:rgba(225,38,29,.95)}
/* badges de estado de publicación (esquina inf-izq, apilados) */
.botleft{position:absolute;bottom:10px;left:10px;display:flex;flex-direction:column;gap:6px;align-items:flex-start}
.ap-badge{font-size:.62rem;font-weight:800;letter-spacing:.03em;color:#fff;background:rgba(21,128,61,.95);padding:4px 10px;border-radius:100px;backdrop-filter:blur(3px);display:inline-flex;align-items:center;gap:.35em}
.cal-badge{font-size:.62rem;font-weight:800;letter-spacing:.03em;color:#fff;background:rgba(124,58,237,.95);padding:4px 10px;border-radius:100px;backdrop-filter:blur(3px);display:inline-flex;align-items:center;gap:.35em}
.li-badge{font-size:.62rem;font-weight:800;letter-spacing:.03em;color:#fff;background:rgba(10,102,194,.95);padding:4px 10px;border-radius:100px;backdrop-filter:blur(3px);display:inline-flex;align-items:center;gap:.35em}
/* estado "aprobado para publicar" (independiente) */
.post.approved{outline:2px solid rgba(21,128,61,.55);outline-offset:-2px}
.btn.approve{background:transparent;color:#15803d;border-color:rgba(21,128,61,.5);font-weight:800}
.btn.approve.on{background:#15803d;color:#fff;border-color:#15803d}
/* estado de publicación en LinkedIn (gana el borde si además está subido) */
.post.posted{outline:2px solid rgba(10,102,194,.55);outline-offset:-2px}
.btn.linkedin{background:transparent;color:#0a66c2;border-color:rgba(10,102,194,.5);font-weight:800}
.btn.linkedin.on{background:#0a66c2;color:#fff;border-color:#0a66c2}
/* fecha de publicación + Google Calendar */
.calrow{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:2px}
.caldate,.caltime{font-family:inherit;font-size:.8rem;color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:100px;padding:6px 12px}
.caldate:focus,.caltime:focus{outline:2px solid var(--red);outline-offset:1px}
.btn.cal{background:transparent;color:#7c3aed;border-color:rgba(124,58,237,.5);font-weight:800;text-decoration:none;display:inline-flex;align-items:center;gap:.35em}
.btn.cal:hover{background:rgba(124,58,237,.10)}
.btn.cal.off{opacity:.45;pointer-events:none}
.calclear{font-family:inherit;font-size:.64rem;font-weight:700;letter-spacing:0;text-transform:none;color:#7c3aed;background:transparent;border:0;cursor:pointer;padding:0;margin-left:auto}
.libox{display:inline-flex;align-items:center;gap:.4em;font-size:.8rem;color:var(--muted)}
.libox b{font-size:1rem;font-weight:800;color:#0a66c2}
.litoggle{font-family:inherit;font-size:.74rem;font-weight:700;color:var(--muted);background:transparent;border:1px solid var(--line);border-radius:100px;padding:5px 12px;cursor:pointer}
.litoggle.on{color:#fff;background:#0a66c2;border-color:#0a66c2}
/* tablero */
.dash{display:flex;flex-wrap:wrap;align-items:center;gap:10px 16px;margin:0 0 22px;padding:12px 14px;border:1px solid var(--line);border-radius:12px;background:var(--card)}
.counts{display:flex;flex-wrap:wrap;gap:8px 14px;font-size:.8rem;color:var(--muted)}
.ct{display:inline-flex;align-items:center;gap:.4em}
.ct b{font-size:1rem;font-weight:800;color:var(--ink)}
.ct.pend b{color:#c6780a}.ct.ready b{color:var(--red)}.ct.appr b{color:#15803d}.ct.sched b{color:#7c3aed}
.filters{display:flex;flex-wrap:wrap;gap:6px;margin-left:auto}
.fchip{font-family:inherit;font-size:.74rem;font-weight:700;color:var(--muted);background:transparent;border:1px solid var(--line);border-radius:100px;padding:5px 12px;cursor:pointer}
.fchip.on{color:#fff;background:var(--gray-dark);border-color:var(--gray-dark)}
.jumpnext{font-family:inherit;font-size:.74rem;font-weight:700;color:var(--red);background:transparent;border:0;cursor:pointer;padding:5px 4px}
.post.hide{display:none}
/* controles de estado */
.lab{display:flex;align-items:center;gap:8px}
.revert{font-family:inherit;font-size:.64rem;font-weight:700;letter-spacing:0;text-transform:none;color:var(--red);background:transparent;border:0;cursor:pointer;padding:0;margin-left:auto}
.editline{font-size:.72rem;color:var(--muted);min-height:1em;line-height:1.4}
.editline .who{font-weight:700;color:var(--ink)}
.btn.ready.on{background:#15803d;border-color:#15803d;color:#fff}
.hist{margin-top:6px;border-top:1px dashed var(--line);padding-top:8px}
.hist summary{font-size:.68rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);cursor:pointer}
.histlist{list-style:none;margin:8px 0 0;padding:0;display:flex;flex-direction:column;gap:5px}
.histlist li{display:grid;grid-template-columns:74px 1fr;gap:10px;font-size:.75rem}
.histlist .hd{font-weight:800;color:var(--red)}
.histlist .hs{color:var(--ink)}
.tpub{color:var(--gray-blue)}.tpend{color:#c6780a}.tready{color:var(--red)}
.xbtn.ghost{background:transparent;color:var(--ink);border:1px solid var(--line)}
.strip{display:flex;gap:6px;padding:10px 0 0;overflow-x:auto}
.thumb{height:52px;width:52px;object-fit:cover;border-radius:6px;cursor:pointer;border:2px solid transparent;flex:none;opacity:.7}
.thumb.on{border-color:var(--red);opacity:1}

.controls{padding:14px 18px 18px;display:flex;flex-direction:column;gap:10px}
.chead{display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.seq{font-size:1.1rem;font-weight:800;color:var(--red)}
.badge{font-size:.66rem;font-weight:800;letter-spacing:.1em;color:#fff;background:var(--gray-dark);padding:3px 9px;border-radius:100px}
.badge.ghost{background:transparent;color:var(--muted);border:1px solid var(--line)}
.sub{font-size:.82rem;font-weight:600;color:var(--muted)}
.lab{font-size:.66rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-top:4px}
.lab .hint{font-weight:600;letter-spacing:0;text-transform:none;color:var(--muted);opacity:.8}
.cc{margin-left:auto;font-size:.64rem;font-weight:800;letter-spacing:0;text-transform:none;color:var(--muted);white-space:nowrap}
.cc.warn{color:#c6780a}
.cc.over{color:var(--red)}
textarea{font-family:inherit;width:100%;resize:vertical;border:1px solid var(--line);border-radius:10px;
  background:var(--gray-light);color:var(--ink);padding:10px 12px;font-size:.86rem;line-height:1.55}
textarea:focus{outline:2px solid var(--red);outline-offset:1px;background:var(--card)}
textarea.copy{min-height:150px}
textarea.imgnote{min-height:62px}
.btns{display:flex;flex-wrap:wrap;gap:8px;margin-top:2px}
.btn{font-family:inherit;font-size:.76rem;font-weight:700;border-radius:100px;padding:7px 14px;cursor:pointer;border:1px solid var(--line);background:var(--card);color:var(--ink)}
.btn.regen{background:var(--red);color:#fff;border-color:var(--red)}
.btn.regen.on{background:var(--gray-blue);border-color:var(--gray-blue)}
.btn.ghost{background:transparent}
.btn:disabled{opacity:.5;cursor:default}
.trace{display:flex;flex-direction:column;gap:6px;border-top:1px solid var(--line);padding-top:10px;margin-top:4px}
.tr{display:grid;grid-template-columns:74px 1fr;gap:10px;font-size:.77rem}
.tr .k{font-size:.62rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);padding-top:2px}
.tr .v{min-width:0;word-break:break-word}
.tr a{color:var(--red);font-weight:600}
code{font-family:inherit;font-weight:700;background:var(--gray-light);padding:1px 6px;border-radius:5px;font-size:.9em}
.muprompt{color:var(--muted);font-size:.72rem;font-style:italic}

/* lightbox */
.lb{position:fixed;inset:0;background:rgba(6,8,9,.92);display:none;z-index:50;align-items:center;justify-content:center;flex-direction:column;gap:14px;padding:24px}
.lb.on{display:flex}
.lb img{max-width:min(90vw,860px);max-height:78vh;border-radius:8px;box-shadow:0 30px 80px -30px rgba(0,0,0,.8)}
.lb .lbbar{display:flex;align-items:center;gap:18px;color:#fff;font-size:.85rem;font-weight:700}
.lb .nav{font-family:inherit;font-size:1rem;font-weight:800;color:#fff;background:rgba(255,255,255,.14);border:0;width:44px;height:44px;border-radius:50%;cursor:pointer}
.lb .nav:disabled{opacity:.3;cursor:default}
.lb .close{position:absolute;top:18px;right:22px;font-size:1.4rem;color:#fff;background:none;border:0;cursor:pointer}
.lb .count{min-width:60px;text-align:center}
.foot{margin-top:32px;padding-top:18px;border-top:1px solid var(--line);font-size:.78rem;color:var(--muted);display:flex;flex-wrap:wrap;gap:6px 18px}
.toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:var(--gray-dark);color:#fff;
  padding:10px 18px;border-radius:100px;font-size:.82rem;font-weight:600;opacity:0;transition:opacity .2s;z-index:60;pointer-events:none}
.toast.on{opacity:1}
</style>

<div class="wrap">
  <p class="eyebrow"><span class="dot"></span>IDIEM · Design System · Workstation</p>
  <h1>Octubre — <b>12 posts</b></h1>
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
    <span>Motor: <code>compose_current(2026-10)</code> · copy validado con <code>ingest_draft</code>.</span>
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

<script>
(function(){
  var KEY='idiem_ws_oct2026_v7';
  function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
  function readJSON(s){try{return JSON.parse(s||'{}')||{};}catch(e){return {};}}
  function mergeState(base,over){var out={},k;for(k in base)out[k]=base[k];
    for(k in over){var a=out[k],b=over[k];if(!a){out[k]=b;continue;}
      var ta=a&&a.editedAt?Date.parse(a.editedAt):0,tb=b&&b.editedAt?Date.parse(b.editedAt):0;
      out[k]=(tb>=ta)?b:a;}return out;}
  // Estado COMPARTIDO embebido (viaja entre dispositivos al "Guardar y compartir")
  // fusionado con el borrador LOCAL de este navegador (gana el más reciente por post).
  var _embed=readJSON((document.getElementById('ws-state')||{}).textContent);
  var _local=readJSON(localStorage.getItem(KEY));
  var store=mergeState(_embed,_local);
  function persistLocal(){try{localStorage.setItem(KEY,JSON.stringify(store));}catch(e){}}
  // ---- estado compartido en vivo (capacidad db del artefacto) ----
  // La DB es la fuente de verdad cuando está disponible; localStorage queda como
  // caché offline. persist() guarda local y agenda un push a la DB de los docs
  // que cambiaron. Un onSnapshot repinta en vivo lo que cambie cualquier equipo.
  var db=null, dbShadow={}, pushTimer=null;
  function isPostKey(k){return k && k.charAt(0)!=='_';}
  function schedulePush(){if(!db)return;clearTimeout(pushTimer);pushTimer=setTimeout(pushNow,400);}
  function pushNow(){if(!db)return;
    Object.keys(store).forEach(function(cid){
      if(!isPostKey(cid))return;
      var body=JSON.stringify(store[cid]||{});
      if(body!==dbShadow[cid]){dbShadow[cid]=body;
        try{db.doc('posts/'+cid).set(store[cid]||{}).catch(function(){});}catch(e){}}
    });}
  function persist(){persistLocal();schedulePush();}
  function rec(cid){return (store[cid]=store[cid]||{});}
  function syncIndicator(mode){var el=document.getElementById('syncState');if(!el)return;
    el.setAttribute('data-mode',mode);
    el.textContent = mode==='sync'?'🟢 Sincronizado con el equipo'
      : mode==='local'?'🟡 Sin conexión · cambios locales' : 'Conectando…';}

  function toast(msg){var t=document.getElementById('toast');t.textContent=msg;t.classList.add('on');
    clearTimeout(t._t);t._t=setTimeout(function(){t.classList.remove('on');},1900);}
  function autosize(t){t.style.height='auto';t.style.height=(t.scrollHeight+2)+'px';}

  // ---- helpers de estado ----
  var revName=document.getElementById('revName');
  function currentUser(){return (revName&&revName.value.trim())||'';}
  function fmtWhen(iso){if(!iso)return '';var d=new Date(iso);if(isNaN(d))return '';
    var D=('0'+d.getDate()).slice(-2),M=('0'+(d.getMonth()+1)).slice(-2);
    var hh=('0'+d.getHours()).slice(-2),mm=('0'+d.getMinutes()).slice(-2);
    var today=new Date();var same=d.toDateString()===today.toDateString();
    return (same?'hoy':D+'-'+M)+' '+hh+':'+mm;}

  function computeStatus(copyEl,noteEl,r){
    var edited=(copyEl.value!==copyEl.defaultValue)||(noteEl.value.trim()!=='')||!!r.regen;
    if(!edited)return 'publicado';
    return r.ready?'listo':'pendiente';
  }

  // ---- per-post wiring ----
  document.querySelectorAll('.post').forEach(function(post){
    var cid=post.getAttribute('data-cid');
    var slides=[];
    try{slides=JSON.parse(post.querySelector('.slides-data').textContent)||[];}catch(e){}
    var r=store[cid]||{};

    var copy=post.querySelector('textarea.copy');
    var note=post.querySelector('textarea.imgnote');
    var cc=post.querySelector('[data-cc]');
    var chip=post.querySelector('.statuschip');
    var applied=chip?(chip.getAttribute('data-applied')||''):'';
    var editline=post.querySelector('.editline');
    var ready=post.querySelector('.btn.ready');
    var regen=post.querySelector('.btn.regen');
    var revs=post.querySelectorAll('.revert');

    if(typeof r.copy==='string')copy.value=r.copy;
    if(typeof r.note==='string')note.value=r.note;
    autosize(copy);autosize(note);

    function refresh(){
      // contador de caracteres (regla MKT: máx 900; .length cuenta unidades UTF-16)
      if(cc){var nch=copy.value.length;cc.textContent=nch+' / 900';
        cc.classList.toggle('warn',nch>860&&nch<=900);cc.classList.toggle('over',nch>900);}
      var st=computeStatus(copy,note,store[cid]||{});
      post.setAttribute('data-status',st);
      post.classList.toggle('flag',st!=='publicado');
      // chip
      if(chip){chip.className='statuschip '+(st==='publicado'?'pub':st==='listo'?'ready':'pend');
        var when=fmtWhen((store[cid]||{}).editedAt);
        chip.textContent = st==='publicado' ? (applied?('publicado · '+applied):'sin cambios')
          : st==='listo' ? ('✓ listo'+(when?' · '+when:'')) : ('✎ pendiente'+(when?' · '+when:''));}
      // editline + revert
      var rr=store[cid]||{};
      var parts=[];
      if(copy.value!==copy.defaultValue)parts.push('el texto');
      if(note.value.trim()!=='')parts.push('una nota de imagen');
      if(rr.regen)parts.push('regeneración');
      if(editline){
        if(parts.length){var by=rr.editedBy?(' · por <span class="who">'+esc(rr.editedBy)+'</span>'):'';
          editline.innerHTML='Editaste '+parts.join(', ')+' · '+(fmtWhen(rr.editedAt)||'sin fecha')+by;}
        else editline.textContent='Sin cambios respecto a lo publicado.';
      }
      revs.forEach(function(b){var f=b.getAttribute('data-field');
        b.hidden = f==='copy' ? (copy.value===copy.defaultValue) : (note.value.trim()==='');});
      // ready button
      if(ready){var on=!!rr.ready && st!=='publicado';
        ready.classList.toggle('on',on);
        ready.textContent=on?'✓ Listo (quitar marca)':'✓ Marcar listo para aplicar';
        ready.disabled = (st==='publicado');}
      // el evento de Calendar incluye el copy: refrescar su enlace si cambió
      if(typeof paintCal==='function')paintCal();
    }
    function stamp(){var rc=rec(cid);rc.editedAt=new Date().toISOString();rc.editedBy=currentUser();}

    copy.addEventListener('input',function(){rec(cid).copy=copy.value;stamp();persist();autosize(copy);refresh();updateDash();});
    note.addEventListener('input',function(){rec(cid).note=note.value;stamp();persist();autosize(note);refresh();updateDash();});

    function paintRegen(){var on=!!(store[cid]&&store[cid].regen);
      regen.classList.toggle('on',on);
      regen.textContent=on?'✓ Regeneración solicitada':'🔄 Solicitar regeneración';}
    regen.addEventListener('click',function(){var cur=!!(store[cid]&&store[cid].regen);
      rec(cid).regen=!cur;stamp();persist();paintRegen();refresh();updateDash();
      toast(!cur?'Marcado para regenerar la imagen.':'Marca quitada.');});

    ready.addEventListener('click',function(){var rc=rec(cid);rc.ready=!rc.ready;persist();refresh();updateDash();
      toast(rc.ready?'Marcado como listo para aplicar.':'Marca de "listo" quitada.');});

    // ---- estado "subido a LinkedIn" (independiente del estado de contenido) ----
    var liBtn=post.querySelector('.btn.linkedin');
    var liBadge=post.querySelector('.li-badge');
    function paintLinked(){var r2=store[cid]||{};var on=!!r2.posted;
      post.classList.toggle('posted',on);
      if(liBtn){liBtn.classList.toggle('on',on);
        liBtn.textContent=on?('✓ Subido a LinkedIn'+(r2.postedAt?(' · '+fmtWhen(r2.postedAt)):'')):'🔗 Marcar subido a LinkedIn';}
      if(liBadge)liBadge.hidden=!on;}
    paintLinked();
    if(liBtn)liBtn.addEventListener('click',function(){var rc=rec(cid);rc.posted=!rc.posted;
      rc.postedAt=rc.posted?new Date().toISOString():null;persist();paintLinked();updateDash();
      toast(rc.posted?'Marcado como subido a LinkedIn.':'Marca de LinkedIn quitada.');});

    // ---- estado "aprobado para publicar" (independiente: revisado → aprobado → subido) ----
    var apBtn=post.querySelector('.btn.approve');
    var apBadge=post.querySelector('.ap-badge');
    function paintApproved(){var r2=store[cid]||{};var on=!!r2.approved;
      post.classList.toggle('approved',on);
      if(apBtn){apBtn.classList.toggle('on',on);
        apBtn.textContent=on?('✓ Aprobado'+(r2.approvedAt?(' · '+fmtWhen(r2.approvedAt)):'')):'✅ Aprobar para publicar';}
      if(apBadge)apBadge.hidden=!on;}
    paintApproved();
    if(apBtn)apBtn.addEventListener('click',function(){var rc=rec(cid);rc.approved=!rc.approved;
      rc.approvedAt=rc.approved?new Date().toISOString():null;persist();paintApproved();updateDash();
      toast(rc.approved?'Aprobado para publicar.':'Aprobación quitada.');});

    // ---- fecha de publicación + Google Calendar (independiente) ----
    // El artifact corre en un iframe sandbox y no puede llamar la API de Calendar;
    // el botón es un enlace "TEMPLATE" que abre Google Calendar con el evento pre-llenado.
    var calDate=post.querySelector('.caldate');
    var calTime=post.querySelector('.caltime');
    var calBtn=post.querySelector('.btn.cal');
    var calBadge=post.querySelector('.cal-badge');
    var calClear=post.querySelector('.calclear');
    var calTitle=post.getAttribute('data-caltitle')||('Post '+post.getAttribute('data-seq'));
    var WS_URL='https://claude.ai/code/artifact/f9016145-d797-4a02-867e-1e478de62a6b';
    if(calDate&&typeof r.scheduledFor==='string')calDate.value=r.scheduledFor;
    if(calTime&&typeof r.scheduledTime==='string'&&r.scheduledTime)calTime.value=r.scheduledTime;
    function pad2(x){return ('0'+x).slice(-2);}
    function fmtDM(iso){var p=(iso||'').split('-');return p.length===3?(p[2]+'-'+p[1]):'';}
    function calURL(){
      var d=calDate?calDate.value:''; if(!d)return null;
      var t=(calTime&&calTime.value)||'09:00';
      var hh=parseInt(t.split(':')[0],10); if(isNaN(hh))hh=9;
      var mm=parseInt(t.split(':')[1],10); if(isNaN(mm))mm=0;
      var ymd=d.replace(/-/g,'');
      var start=ymd+'T'+pad2(hh)+pad2(mm)+'00';
      var em=mm+30, eh=hh; if(em>=60){em-=60; eh=(hh+1)%24;}
      var end=ymd+'T'+pad2(eh)+pad2(em)+'00';
      var title='📢 Publicar en LinkedIn — '+calTitle;
      var details=(copy.value||'')+'\n\n— Verifica la publicación y marca "subido a LinkedIn" en la workstation:\n'+WS_URL;
      return 'https://calendar.google.com/calendar/render?action=TEMPLATE'
        +'&text='+encodeURIComponent(title)
        +'&dates='+start+'/'+end
        +'&ctz=America/Santiago'
        +'&details='+encodeURIComponent(details);
    }
    function paintCal(){
      if(!calBtn)return;
      var d=calDate?calDate.value:'';
      var url=calURL();
      if(url){calBtn.setAttribute('href',url);calBtn.classList.remove('off');}
      else{calBtn.removeAttribute('href');calBtn.classList.add('off');}
      if(calBadge){if(d){calBadge.hidden=false;calBadge.textContent='📅 '+fmtDM(d);}else calBadge.hidden=true;}
      if(calClear)calClear.hidden=!d;
      post.classList.toggle('scheduled',!!d);
    }
    function saveCal(){var rc=rec(cid);var d=(calDate&&calDate.value)||'';
      if(d){rc.scheduledFor=d;rc.scheduledTime=(calTime&&calTime.value)||'09:00';}
      else{delete rc.scheduledFor;delete rc.scheduledTime;}
      persist();paintCal();updateDash();}
    if(calDate)calDate.addEventListener('change',function(){saveCal();
      toast(calDate.value?('Agendado para el '+fmtDM(calDate.value)+' · abre el botón para crear el evento'):'Fecha quitada.');});
    if(calTime)calTime.addEventListener('change',saveCal);
    if(calClear)calClear.addEventListener('click',function(){if(calDate)calDate.value='';if(calTime)calTime.value='09:00';saveCal();toast('Fecha quitada.');});

    revs.forEach(function(b){b.addEventListener('click',function(){
      var f=b.getAttribute('data-field');
      if(f==='copy'){copy.value=copy.defaultValue;rec(cid).copy=copy.defaultValue;autosize(copy);}
      else{note.value='';rec(cid).note='';autosize(note);}
      var rc=store[cid]||{};
      if(copy.value===copy.defaultValue&&note.value.trim()===''&&!rc.regen){rc.ready=false;}
      persist();refresh();updateDash();toast('Volviste a lo publicado.');});});

    // selected slide index for PNG download / main preview
    var curIdx=0;
    var main=post.querySelector('.main');
    post.querySelectorAll('.thumb').forEach(function(th){
      th.addEventListener('click',function(){
        curIdx=parseInt(th.getAttribute('data-idx'),10)||0;
        main.src=slides[curIdx];
        post.querySelectorAll('.thumb').forEach(function(x){x.classList.remove('on');});
        th.classList.add('on');
      });
    });

    post.querySelector('.gwrap').addEventListener('click',function(){openLB(slides,curIdx);});

    post.querySelector('.btn.copybtn').addEventListener('click',function(){
      var txt=copy.value;
      if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(txt).then(function(){toast('Texto copiado');},function(){toast('Texto copiado');});}
      else{var ta=document.createElement('textarea');ta.value=txt;document.body.appendChild(ta);ta.select();try{document.execCommand('copy');}catch(e){}document.body.removeChild(ta);toast('Texto copiado');}
    });

    post.querySelector('.btn.png').addEventListener('click',function(){downloadPNG(post,slides,curIdx);});
    post.querySelector('.btn.pdf').addEventListener('click',function(){downloadPDF(post,slides);});

    // Reaplica el estado (store[cid]) a los controles + repinta. Lo llama el
    // onSnapshot de la DB para reflejar en vivo lo que cambie otro equipo.
    // No pisa un campo de texto que se está editando (activeElement).
    function applyState(){
      var rr=store[cid]||{};
      if(document.activeElement!==copy){
        copy.value=(typeof rr.copy==='string')?rr.copy:copy.defaultValue;autosize(copy);}
      if(document.activeElement!==note){
        note.value=(typeof rr.note==='string')?rr.note:'';autosize(note);}
      if(calDate&&document.activeElement!==calDate)calDate.value=rr.scheduledFor||'';
      if(calTime&&document.activeElement!==calTime)calTime.value=rr.scheduledTime||'09:00';
      paintRegen();paintApproved();paintLinked();paintCal();refresh();
    }
    applyState();
    post._apply=applyState;
  });

  // ---- lightbox ----
  var lb=document.getElementById('lb'),lbImg=document.getElementById('lbImg'),
      lbPrev=document.getElementById('lbPrev'),lbNext=document.getElementById('lbNext'),
      lbCount=document.getElementById('lbCount'),lbClose=document.getElementById('lbClose');
  var lbSlides=[],lbIdx=0;
  function paintLB(){lbImg.src=lbSlides[lbIdx];lbCount.textContent=(lbIdx+1)+' / '+lbSlides.length;
    lbPrev.disabled=lbIdx<=0;lbNext.disabled=lbIdx>=lbSlides.length-1;
    lbPrev.style.visibility=lbNext.style.visibility=lbSlides.length>1?'visible':'hidden';}
  function openLB(slides,idx){lbSlides=slides;lbIdx=idx||0;paintLB();lb.classList.add('on');}
  function closeLB(){lb.classList.remove('on');
    var box=document.getElementById('exportBox');
    if(box){box.remove();lbImg.style.display='';lb.querySelector('.lbbar').style.display='';}}
  lbPrev.addEventListener('click',function(){if(lbIdx>0){lbIdx--;paintLB();}});
  lbNext.addEventListener('click',function(){if(lbIdx<lbSlides.length-1){lbIdx++;paintLB();}});
  lbClose.addEventListener('click',closeLB);
  lb.addEventListener('click',function(e){if(e.target===lb)closeLB();});
  document.addEventListener('keydown',function(e){if(!lb.classList.contains('on'))return;
    if(e.key==='Escape')closeLB();if(e.key==='ArrowLeft')lbPrev.click();if(e.key==='ArrowRight')lbNext.click();});

  // ---- downloads capability ----
  var _dl=null,_dlTried=false;
  async function downloads(){if(_dlTried)return _dl;_dlTried=true;
    try{_dl=(window.claude&&claude.use)?await claude.use('downloads'):null;}catch(e){_dl=null;}return _dl;}

  function dataURItoBytes(uri){var b64=uri.split(',')[1];var bin=atob(b64);
    var n=bin.length,u=new Uint8Array(n);for(var i=0;i<n;i++)u[i]=bin.charCodeAt(i);return u;}

  async function downloadPNG(post,slides,idx){
    var dl=await downloads();
    var seq=post.getAttribute('data-seq');
    if(!dl){toast('Descarga no disponible en esta vista');return;}
    try{
      var bytes=dataURItoBytes(slides[idx]);         // JPEG bytes
      // re-encode to PNG via canvas for a true .png
      var img=new Image();img.src=slides[idx];await img.decode();
      var cv=document.createElement('canvas');cv.width=img.naturalWidth;cv.height=img.naturalHeight;
      cv.getContext('2d').drawImage(img,0,0);
      var blob=await new Promise(function(res){cv.toBlob(res,'image/png');});
      await dl.save({filename:'idiem_sep_post'+seq+(slides.length>1?('_lam'+(idx+1)):'')+'.png',data:blob});
      toast('PNG guardado');
    }catch(e){toast(errMsg(e));}
  }

  async function downloadPDF(post,slides){
    var dl=await downloads();
    var seq=post.getAttribute('data-seq');
    if(!dl){toast('Descarga no disponible en esta vista');return;}
    try{
      var pages=slides.map(function(u){return dataURItoBytes(u);});
      var pdf=buildImagePDF(pages,1080,1080);
      await dl.save({filename:'idiem_sep_post'+seq+'.pdf',data:pdf});
      toast('PDF guardado');
    }catch(e){
      if(e&&e.code==='extension_not_enabled'){toast('PDF no habilitado aquí — descarga PNG por lámina');}
      else{toast(errMsg(e));}
    }
  }

  function errMsg(e){var c=e&&e.code;
    if(c==='declined')return 'Descarga cancelada';
    if(c==='too_large')return 'Archivo muy grande';
    if(c==='rate_limited')return 'Espera un momento y reintenta';
    return 'No se pudo descargar';}

  // ---- minimal image PDF (JPEG pages, DCTDecode) ----
  function buildImagePDF(jpegs,w,h){
    var enc=new TextEncoder();
    var chunks=[],offset=0,offsets=[];
    function put(x){var b=(typeof x==='string')?enc.encode(x):x;chunks.push(b);offset+=b.length;}
    function obj(n){offsets[n]=offset;}
    put('%PDF-1.4\n%\xE2\xE3\xCF\xD3\n');
    var N=jpegs.length;
    // object numbering: 1 catalog, 2 pages, then per page: pageObj, imgObj, contentObj
    var pageIds=[],total=2+N*3;
    obj(1);put('1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n');
    var kids='';for(var i=0;i<N;i++){kids+=(3+i*3)+' 0 R ';}
    obj(2);put('2 0 obj\n<< /Type /Pages /Count '+N+' /Kids ['+kids+'] >>\nendobj\n');
    for(var p=0;p<N;p++){
      var pageId=3+p*3,imgId=pageId+1,contId=pageId+2;
      obj(pageId);
      put(pageId+' 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 '+w+' '+h+'] '+
          '/Resources << /XObject << /Im0 '+imgId+' 0 R >> >> /Contents '+contId+' 0 R >>\nendobj\n');
      obj(imgId);
      put(imgId+' 0 obj\n<< /Type /XObject /Subtype /Image /Width '+w+' /Height '+h+
          ' /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length '+jpegs[p].length+' >>\nstream\n');
      put(jpegs[p]);put('\nendstream\nendobj\n');
      var cs='q '+w+' 0 0 '+h+' 0 0 cm /Im0 Do Q\n';
      obj(contId);
      put(contId+' 0 obj\n<< /Length '+enc.encode(cs).length+' >>\nstream\n'+cs+'endstream\nendobj\n');
    }
    var xrefPos=offset;
    var count=total+1;
    put('xref\n0 '+count+'\n0000000000 65535 f \n');
    for(var k=1;k<count;k++){var o=offsets[k]||0;put(('0000000000'+o).slice(-10)+' 00000 n \n');}
    put('trailer\n<< /Size '+count+' /Root 1 0 R >>\nstartxref\n'+xrefPos+'\n%%EOF');
    return new Blob(chunks,{type:'application/pdf'});
  }

  // ---- reviewer identity ----
  var revRole=document.getElementById('revRole');
  var rv=store._reviewer||{};
  if(rv.name&&revName)revName.value=rv.name; if(rv.role&&revRole)revRole.value=rv.role;
  function saveRev(){store._reviewer={name:revName.value.trim(),role:revRole.value.trim(),editedAt:new Date().toISOString()};persist();}
  if(revName)revName.addEventListener('input',saveRev); if(revRole)revRole.addEventListener('input',saveRev);
  function slug(s){return (s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'')
    .replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,40)||'revisor';}

  // ---- resumen + filtros (dashboard) ----
  function setTxt(id,v){var e=document.getElementById(id);if(e)e.textContent=v;}
  var curFilter='todos', hidePosted=false;
  function applyFilter(){document.querySelectorAll('.post').forEach(function(p){
    var st=p.getAttribute('data-status')||'publicado';
    var byStatus=curFilter==='todos'||st===curFilter;
    var byLinked=!hidePosted||!p.classList.contains('posted');
    p.classList.toggle('hide', !(byStatus&&byLinked));});}
  function updateDash(){var c={pendiente:0,listo:0,publicado:0},linked=0,approved=0,scheduled=0,total=0;
    document.querySelectorAll('.post').forEach(function(p){var s=p.getAttribute('data-status')||'publicado';
      if(c[s]==null)c[s]=0;c[s]++;total++;if(p.classList.contains('posted'))linked++;
      if(p.classList.contains('approved'))approved++;
      if(p.classList.contains('scheduled'))scheduled++;});
    setTxt('nPend',c.pendiente);setTxt('nReady',c.listo);setTxt('nPub',c.publicado);
    setTxt('nApproved',approved);setTxt('nApTotal',total);
    setTxt('nSched',scheduled);setTxt('nSchTotal',total);
    setTxt('nLinked',linked);setTxt('nTotal',total);applyFilter();}
  var liToggle=document.getElementById('liToggle');
  if(liToggle)liToggle.addEventListener('click',function(){hidePosted=!hidePosted;
    this.classList.toggle('on',hidePosted);
    this.textContent=hidePosted?'Mostrar todos':'Ocultar los ya subidos';applyFilter();});
  var filters=document.getElementById('filters');
  if(filters)filters.addEventListener('click',function(e){var b=e.target.closest('.fchip');if(!b)return;
    curFilter=b.getAttribute('data-f');
    this.querySelectorAll('.fchip').forEach(function(x){x.classList.toggle('on',x===b);});applyFilter();});
  var jn=document.getElementById('jumpNext');
  if(jn)jn.addEventListener('click',function(){
    var t=document.querySelector('.post[data-status="pendiente"]')||document.querySelector('.post[data-status="listo"]');
    if(t)t.scrollIntoView({behavior:'smooth',block:'start'});else toast('No hay posts pendientes.');});

  // "Guardar y compartir" quedó obsoleto: el estado se sincroniza en vivo por la
  // DB del artefacto (ver más abajo). Se eliminó saveCloud/buildCleanHTML/artifactCap.

  // ---- respaldo opcional: descargar JSON ----
  var expBtn=document.querySelector('.xbtn.export');
  if(expBtn)expBtn.addEventListener('click',async function(){
    var out={reviewer:{name:(revName?revName.value.trim():'')||null,role:(revRole?revRole.value.trim():'')||null},
      month:'2026-10',exported_at:new Date().toISOString(),posts:[]};
    document.querySelectorAll('.post').forEach(function(post){
      var stt=post.getAttribute('data-status');if(stt==='publicado')return;
      var cid=post.getAttribute('data-cid'),r=store[cid]||{},ce=post.querySelector('textarea.copy');
      out.posts.push({content_id:cid,seq:post.getAttribute('data-seq'),status:stt,
        copy:(ce&&ce.value!==ce.defaultValue)?ce.value:null,
        image_note:(r.note&&r.note.trim())?r.note:null,regenerate:!!r.regen,ready:!!r.ready,
        edited_by:r.editedBy||null,edited_at:r.editedAt||null});
    });
    if(!out.posts.length){toast('No hay cambios que respaldar todavía');return;}
    var json=JSON.stringify(out,null,2);
    var fname='idiem_cambios_oct2026__'+slug(out.reviewer.name||'revisor')+'.json';
    var dl=await downloads();
    if(dl){try{await dl.save({filename:fname,data:json});toast('Respaldo descargado');return;}
      catch(e){if(e&&e.code==='declined'){toast('Descarga cancelada');return;}}}
    try{var blob=new Blob([json],{type:'application/json'});var url=URL.createObjectURL(blob);
      var a=document.createElement('a');a.href=url;a.download=fname;document.body.appendChild(a);a.click();
      setTimeout(function(){document.body.removeChild(a);URL.revokeObjectURL(url);},1500);
      toast('Respaldo descargado');return;}catch(e){}
    var w=document.getElementById('lb');var box=document.createElement('div');
    box.id='exportBox';box.style.cssText='display:flex;flex-direction:column;gap:10px;align-items:center';
    var pre=document.createElement('textarea');pre.readOnly=true;pre.value=json;
    pre.style.cssText='width:min(90vw,720px);height:54vh;font-family:monospace;font-size:12px;padding:10px;border-radius:8px';
    var cp=document.createElement('button');cp.textContent='Copiar JSON';cp.className='xbtn';
    cp.onclick=function(){pre.select();try{document.execCommand('copy');}catch(e){}toast('JSON copiado');};
    box.appendChild(pre);box.appendChild(cp);
    lbImg.style.display='none';w.querySelector('.lbbar').style.display='none';
    w.insertBefore(box,w.querySelector('.close').nextSibling);w.classList.add('on');
  });

  updateDash();

  // ---- conexión a la DB del artefacto (estado compartido en vivo) ----
  function applyAll(){document.querySelectorAll('.post').forEach(function(p){
    if(p._apply)p._apply();});updateDash();}
  (async function(){
    try{db=(window.claude&&claude.use)?await claude.use('db'):null;}catch(e){db=null;}
    if(!db){syncIndicator('local');return;}   // sin DB: modo local (localStorage)
    syncIndicator('sync');
    try{
      db.collection('posts').onSnapshot(function(snap){
        var changed=false;
        snap.docChanges().forEach(function(ch){
          var cid=ch.doc.id;
          var body=ch.type==='removed'?'{}':JSON.stringify(ch.doc.data()||{});
          if(body===dbShadow[cid])return;              // eco de nuestra propia escritura
          dbShadow[cid]=body;
          store[cid]=ch.type==='removed'?{}:Object.assign({},ch.doc.data()||{});
          changed=true;
        });
        if(changed){persistLocal();applyAll();}
        syncIndicator('sync');
      },function(err){syncIndicator('local');});
    }catch(e){syncIndicator('local');}
  })();
})();
</script>'''


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", default="2026-10")
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
