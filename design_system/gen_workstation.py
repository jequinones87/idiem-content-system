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
}

# Fotos Adobe Stock licenciadas (tier libre) para los posts sin foto de librería
# adecuada (antes marcados Muapi). Descargadas, comprimidas a 1080px y usadas
# localmente; foto real y trazable, sin depender de un CDN externo.
STOCK_SUB = {
    1:  {"id": "212862972",  "detalle": "acuerdo · ejecutivos"},
    7:  {"id": "204006589",  "detalle": "sonómetro en terreno"},
    8:  {"id": "1614411840", "detalle": "fusión de tubería HDPE"},
    9:  {"id": "85465544",   "detalle": "hospital moderno"},
    12: {"id": "340172893",  "detalle": "END por ultrasonido en soldadura"},
}

PAGE = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap">
<style>{style}{carcss}</style>
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
    # Estático: pieza Servicios (círculo rojo).
    return [G.canvas(seq, cshort, photo_uri, finish)]


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
            html = PAGE.format(style=style, carcss=CAR.CAROUSEL_CSS, canvas=canvas_html)
            hp = posts_dir / f"p{seq:02d}_s{idx}.html"
            pp = posts_dir / f"p{seq:02d}_s{idx}.png"
            hp.write_text(html, encoding="utf-8")
            manifest.append({"html": str(hp), "png": str(pp)})
            pngs.append(str(pp))
        structure.append({"seq": seq, "cid": post.content_id, "pngs": pngs})

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
        post = posts[cid]
        uris = [jpeg_uri(p) for p in st["pngs"]]
        cards.append(render_card(seq, post, uris))

    html = ARTIFACT.replace("__CARDS__", "\n".join(cards))
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

    return f'''<article class="post" data-seq="{seq}" data-cid="{G.esc(post.content_id)}" data-car="{"1" if is_car else "0"}">
  <script type="application/json" class="slides-data">{slides_json}</script>
  <div class="graphic">
    <div class="gwrap">
      <img class="main" src="{uris[0]}" data-idx="0" alt="Post {seq:02d}">
      <span class="fmtbadge">{fmt_label}</span>
      <span class="zoomhint">clic para ampliar</span>
    </div>
    {strip}
  </div>
  <div class="controls">
    <div class="chead"><span class="seq">{seq:02d}</span><span class="badge">{cshort}</span>
      <span class="badge ghost">{G.esc(fmt)}</span><span class="sub">{G.esc(subname)}</span></div>

    <label class="lab">Texto del post <span class="hint">— editable, se guarda en tu navegador</span></label>
    <textarea class="copy" data-cid="{G.esc(post.content_id)}" spellcheck="false">{G.esc(full_copy)}</textarea>

    <label class="lab">Cambios en la imagen / gráfica</label>
    <textarea class="imgnote" data-cid="{G.esc(post.content_id)}" spellcheck="false"
      placeholder="Ej.: cambiar la foto por una de faena real; achicar el titular; usar otra lámina de cierre…"></textarea>

    <div class="btns">
      <button class="btn regen" type="button">🔄 Solicitar regeneración</button>
      <button class="btn ghost png" type="button">Descargar PNG</button>
      <button class="btn ghost pdf" type="button">Descargar PDF</button>
      <button class="btn ghost copybtn" type="button">Copiar texto</button>
    </div>

    <div class="trace">
      <div class="tr"><span class="k">Ancla</span><span class="v"><code>{G.esc(post.content_id)}</code></span></div>
      <div class="tr"><span class="k">Evidencia</span><span class="v">{ev_codes}</span></div>
      <div class="tr"><span class="k">Foto</span><span class="v">{foto}</span></div>
    </div>
  </div>
</article>'''


ARTIFACT = r'''<title>Workstation Septiembre IDIEM</title>
<meta name="description" content="Plataforma de desarrollo de los 12 posts de septiembre de IDIEM: gráfica por post, texto editable, notas de imagen con regeneración, descarga PNG/PDF y revisión de carruseles.">
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
  <h1>Septiembre — <b>desarrollo de los 12 posts</b></h1>
  <p class="lede">Por cada post: la gráfica arriba (clic para ampliar; los carruseles se revisan lámina por lámina), y abajo el <strong>texto editable</strong>, un recuadro para <strong>cambios de imagen</strong> con su botón de regeneración, y descargas <strong>PNG/PDF</strong>. Tus ediciones se guardan en este navegador. Para que Claude aplique las regeneraciones, usa <strong>Exportar cambios</strong> y envíale el archivo.</p>
  <div class="bar">
    <input class="idfield" id="revName" type="text" placeholder="Tu nombre" autocomplete="name" spellcheck="false">
    <input class="idfield" id="revRole" type="text" placeholder="Especialidad / área (opcional)" spellcheck="false">
    <button class="xbtn export" type="button">⬇ Descargar mis cambios (JSON)</button>
    <span class="savehint">Pon tu nombre, comenta los posts y descarga tu JSON para enviarlo. Todo se guarda en este navegador.</span>
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
  var KEY='idiem_ws_sep2026_v1';
  var store={};
  try{store=JSON.parse(localStorage.getItem(KEY)||'{}')||{};}catch(e){store={};}
  function persist(){try{localStorage.setItem(KEY,JSON.stringify(store));}catch(e){}}
  function rec(cid){return (store[cid]=store[cid]||{});}

  function toast(msg){var t=document.getElementById('toast');t.textContent=msg;t.classList.add('on');
    clearTimeout(t._t);t._t=setTimeout(function(){t.classList.remove('on');},1900);}
  function autosize(t){t.style.height='auto';t.style.height=(t.scrollHeight+2)+'px';}

  // ---- per-post wiring ----
  document.querySelectorAll('.post').forEach(function(post){
    var cid=post.getAttribute('data-cid');
    var slides=[];
    try{slides=JSON.parse(post.querySelector('.slides-data').textContent)||[];}catch(e){}
    var r=store[cid]||{};

    var copy=post.querySelector('textarea.copy');
    if(typeof r.copy==='string')copy.value=r.copy;
    autosize(copy);
    copy.addEventListener('input',function(){rec(cid).copy=copy.value;persist();autosize(copy);});

    var note=post.querySelector('textarea.imgnote');
    if(typeof r.note==='string')note.value=r.note;
    autosize(note);
    note.addEventListener('input',function(){rec(cid).note=note.value;persist();autosize(note);});

    var regen=post.querySelector('.btn.regen');
    function paintRegen(){var on=!!(store[cid]&&store[cid].regen);
      regen.classList.toggle('on',on);post.classList.toggle('flag',on);
      regen.textContent=on?'✓ Regeneración solicitada':'🔄 Solicitar regeneración';}
    paintRegen();
    regen.addEventListener('click',function(){var cur=!!(store[cid]&&store[cid].regen);
      rec(cid).regen=!cur;persist();paintRegen();
      toast(!cur?'Marcado. Exporta los cambios para que Claude regenere.':'Marca quitada.');});

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
  var revName=document.getElementById('revName'), revRole=document.getElementById('revRole');
  var rv=store._reviewer||{};
  if(rv.name)revName.value=rv.name; if(rv.role)revRole.value=rv.role;
  function saveRev(){store._reviewer={name:revName.value.trim(),role:revRole.value.trim()};persist();}
  revName.addEventListener('input',saveRev); revRole.addEventListener('input',saveRev);
  function slug(s){return (s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'')
    .replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,40)||'revisor';}

  // ---- export changes ----
  document.querySelector('.xbtn.export').addEventListener('click',async function(){
    var name=revName.value.trim();
    if(!name){toast('Pon tu nombre antes de descargar');revName.focus();return;}
    var out={reviewer:{name:name,role:revRole.value.trim()||null},
      month:'2026-09',exported_at:new Date().toISOString(),posts:[]};
    document.querySelectorAll('.post').forEach(function(post){
      var cid=post.getAttribute('data-cid'),r=store[cid]||{};
      if(r.copy||r.note||r.regen){
        out.posts.push({content_id:cid,seq:post.getAttribute('data-seq'),
          copy:r.copy||null,image_note:r.note||null,regenerate:!!r.regen});
      }
    });
    if(!out.posts.length){toast('No hay cambios que exportar todavía');return;}
    var json=JSON.stringify(out,null,2);
    var fname='idiem_cambios_sep2026__'+slug(name)+'.json';
    // 1) capacidad downloads (dentro del artefacto claude.ai)
    var dl=await downloads();
    if(dl){try{await dl.save({filename:fname,data:json});toast('Cambios descargados');return;}
      catch(e){if(e&&e.code==='declined'){toast('Descarga cancelada');return;}}}
    // 2) descarga por navegador (archivo HTML abierto fuera de claude.ai)
    try{
      var blob=new Blob([json],{type:'application/json'});
      var url=URL.createObjectURL(blob);
      var a=document.createElement('a');a.href=url;a.download=fname;
      document.body.appendChild(a);a.click();
      setTimeout(function(){document.body.removeChild(a);URL.revokeObjectURL(url);},1500);
      toast('Cambios descargados');return;
    }catch(e){}
    // 3) último recurso: mostrar el JSON para copiar y pegar en un correo
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
})();
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
