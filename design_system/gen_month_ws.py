"""Workstation mensual data-driven (desde noviembre 2026).

MISMA LÍNEA que septiembre/octubre/webinar: reusa el frontend/backend compartido
(design_system/workstation_shared/workstation_ui.{css,js}), con sync en vivo (`db`),
estados, aprobar, LinkedIn, Google Calendar, notas de imagen, PNG/PDF, historial,
traza y lightbox. Las piezas usan las plantillas oficiales (Plantilla 01 Servicios,
Plantilla 02 carrusel con foto de fondo, pieza conmemorativa con foto).

Todo sale de archivos externos del mes (nada hardcodeado por post):
  state/plans/<mes>_asignacion.json  -> fecha, KB, formato, arquetipo/hook/CTA, pain point
  state/plans/<mes>_copies.json      -> copy DRAFT por post + fact_check
  state/plans/<mes>_graficas.json    -> capa visual (titulares, láminas, foto + traza)

Pipeline:
  1) --emit     : HTML standalone por lámina + manifest.json + structure.json
  2) node design_system/render_bundle.cjs <build>/manifest.json   -> PNG 1080x1080
  3) --assemble : embebe los PNG (JPEG) y arma la workstation

Uso:
  PYTHONPATH=src python3 design_system/gen_month_ws.py --month 2026-11 --emit
  node design_system/render_bundle.cjs <build>/manifest.json
  PYTHONPATH=src python3 design_system/gen_month_ws.py --month 2026-11 --assemble --out <html>
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
sys.path.insert(0, str(ROOT))
import gen_month_grid as G          # noqa: E402  (CSS Plantilla 01 + esc)
import carousel as CAR              # noqa: E402  (CSS Plantilla 02)
import gen_workstation as GW        # noqa: E402  (CSS pieza conmemorativa + PAGE)
from bundle_month import grid_style  # noqa: E402
from brand_assets import LOGO, RING, SLOGAN  # noqa: E402

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]
CELL_SHORT = G.CELL_SHORT
ARQ_LABEL = {
    "problem_impact_capability": "problema → impacto → capacidad",
    "risk_prevention": "prevención de riesgo",
    "technical_question": "pregunta técnica",
    "data_implication": "dato → implicancia",
    "process_result": "proceso → resultado",
    "project_challenge": "desafío de proyecto",
    "evidence_learning": "evidencia → aprendizaje",
    "capability_application": "capacidad aplicada",
}


def load(month: str) -> dict:
    p = REPO / "state" / "plans"
    plan = json.loads((p / f"{month}_asignacion.json").read_text("utf-8"))
    copies = json.loads((p / f"{month}_copies.json").read_text("utf-8"))
    gfx = json.loads((p / f"{month}_graficas.json").read_text("utf-8"))
    return {"plan": plan, "copies": copies, "gfx": gfx}


def items(month: str) -> list[dict]:
    """Posts + efeméride ordenados por fecha de publicación."""
    d = load(month)
    out = []
    for p in d["plan"]["posts"]:
        k = str(p["seq"])
        out.append({"key": k, "seq": p["seq"], "date": p["date"], "plan": p,
                    "copy": d["copies"]["copies"][k], "gfx": d["gfx"]["posts"][k],
                    "fact": d["copies"].get("fact_check", {}).get(k, ""),
                    "cid": f"PLAN-{p['knowledge_id']}-{p['seq']:02d}"})
    extras = d["plan"].get("extra") or []
    ex = (extras[0] if isinstance(extras, list) and extras else extras) or {}
    if "E" in d["copies"]["copies"]:
        out.append({"key": "E", "seq": 0, "date": ex.get("date", f"{month}-26"), "plan": ex,
                    "copy": d["copies"]["copies"]["E"], "gfx": d["gfx"]["posts"]["E"],
                    "fact": d["copies"].get("fact_check", {}).get("E", ""),
                    "cid": f"EFEM-{month}"})
    out.sort(key=lambda x: (x["date"], x["seq"]))
    return out


def photo_uri(month: str, gfx: dict) -> str:
    d = REPO / json.loads((REPO / "state" / "plans" / f"{month}_graficas.json").read_text("utf-8"))["photo_dir"]
    f = d / gfx["photo"]["file"]
    return "data:image/jpeg;base64," + base64.b64encode(f.read_bytes()).decode()


def _icon(name: str) -> str:
    b = (ROOT / "assets" / f"icon_{name}.png").read_bytes()
    return f"data:image/png;base64,{base64.b64encode(b).decode()}"


# ---- piezas ---------------------------------------------------------------
def static_canvas(g: dict, uri: str) -> str:
    pos = g["photo"].get("pos", "50% 45%")
    side = " circ-right" if g.get("side") == "right" else ""
    return f'''<div class="canvas{side}" data-finish="photo">
  <div class="photo" style="background-image:url('{uri}');background-position:{pos}"></div>
  <div class="legibility"></div>
  <img class="slogan" src="{SLOGAN}" alt="Elige bien. Elige idiem.">
  <img class="logo" src="{LOGO}" alt="Logo IDIEM">
  <div class="circle-wrap">
    <svg viewBox="0 0 850 850" aria-hidden="true"><path class="ring" d="{RING}"/></svg>
    <div class="circle-msg">
      <div class="svc">{G.esc(g["svc"])}</div>
      <div class="msg">{g["msg"]}</div>
    </div>
  </div>
  <div class="baseline">{g["base"]}</div>
</div>'''


def carousel_slides(g: dict, uri: str) -> list[str]:
    pos = g["photo"].get("pos", "50% 42%")
    c = g["carousel"]
    bg = f"background-image:url('{uri}');background-position:{pos}"
    pt = c["portada"]
    out = [f'''<div class="canvas c2slide" data-finish="carousel">
  <div class="c2photo" style="{bg}"></div><div class="c2grad"></div>
  <img class="c2slogan" src="{SLOGAN}" alt="Elige bien. Elige idiem.">
  <img class="c2logo" src="{LOGO}" alt="Logo IDIEM">
  <div class="c2eyebrow">{pt["kicker"]}</div>
  <div class="c2ptitle">{pt["title"]}</div>
</div>''']
    for i, sl in enumerate(c["intermedias"], 1):
        out.append(f'''<div class="canvas c2slide" data-finish="carousel">
  <div class="c2photo" style="{bg}"></div><div class="c2veil"></div>
  <img class="c2logo" src="{LOGO}" alt="Logo IDIEM">
  <div class="c2num">0{i}</div>
  <img class="c2ic" src="{_icon(sl["icon"])}" alt="">
  <div class="c2rule"></div>
  <div class="c2mtitle">{sl["title"]}</div>
  <div class="c2mbody">{G.esc(sl["body"])}</div>
</div>''')
    out.append(CAR.cierre_html(c["cierre"], LOGO, SLOGAN))
    return out


def special_canvas(g: dict, uri: str) -> str:
    s = g["special"]
    pos = g["photo"].get("pos", "50% 40%")
    return f'''<div class="canvas fpslide" data-finish="photo">
  <div class="fpphoto" style="background-image:url('{uri}');background-position:{pos}"></div>
  <div class="fpveil"></div>
  <img class="c2slogan" src="{SLOGAN}" alt="Elige bien. Elige idiem.">
  <img class="c2logo" src="{LOGO}" alt="Logo IDIEM">
  <div class="fpwrap">
    <div class="fpkick">{s["kicker"]}</div>
    <div class="fprule"></div>
    <div class="fptitle">{s["title"]}</div>
    <div class="fpsub">{G.esc(s["sub"])}</div>
  </div>
</div>'''


EXTRA_CSS = r'''
.fpkick{letter-spacing:.14em}
'''


def emit(month: str, build: Path) -> None:
    sl = build / "slides"
    sl.mkdir(parents=True, exist_ok=True)
    style = grid_style()
    manifest, structure = [], []
    for it in items(month):
        g = it["gfx"]
        uri = photo_uri(month, g)
        if "carousel" in g:
            canv = carousel_slides(g, uri)
        elif "special" in g:
            canv = [special_canvas(g, uri)]
        else:
            canv = [static_canvas(g, uri)]
        pngs = []
        for idx, c in enumerate(canv):
            html = GW.PAGE.format(style=style + EXTRA_CSS, carcss=CAR.CAROUSEL_CSS,
                                  fpcss=GW.FIESTAS_CSS, canvas=c)
            hp, pp = sl / f"p{it['key']}_s{idx}.html", sl / f"p{it['key']}_s{idx}.png"
            hp.write_text(html, encoding="utf-8")
            manifest.append({"html": str(hp), "png": str(pp)})
            pngs.append(str(pp))
        structure.append({"key": it["key"], "pngs": pngs})
    (build / "manifest.json").write_text(json.dumps(manifest), "utf-8")
    (build / "structure.json").write_text(json.dumps(structure), "utf-8")
    print(f"emit: {len(structure)} piezas, {len(manifest)} láminas -> {build}")


# ---- workstation ----------------------------------------------------------
def jpeg_uri(png: str, q: int = 86) -> str:
    from PIL import Image
    im = Image.open(png).convert("RGB")
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def _fecha(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{int(d)} {MESES[int(m) - 1][:3]}"


def card(it: dict, uris: list[str], applied: str) -> str:
    p, g, cid = it["plan"], it["gfx"], it["cid"]
    is_car = "carousel" in g
    is_special = "special" in g
    ph = g["photo"]
    if ph["source"] == "stock":
        foto = (f'Adobe Stock · <code>#{G.esc(ph["id"])}</code> ({G.esc(ph["detalle"])}) · licencia libre'
                f'<br><span class="muprompt">sin foto propia de transporte descargable en la librería</span>')
    else:
        foto = (f'Librería · <code>{G.esc(ph["id"])}</code> ({G.esc(ph["detalle"])}) · '
                f'<a href="{G.esc(ph["drive"])}" target="_blank" rel="noopener">ver en Drive</a>')

    if is_special:
        badge, fmt_label, sub = "EFEMÉRIDE", "EFEMÉRIDE · INSTITUCIONAL", f'{_fecha(it["date"])} · Día Mundial del Transporte Sostenible'
        trace = (f'<div class="tr"><span class="k">Ancla</span><span class="v"><code>{cid}</code></span></div>'
                 f'<div class="tr"><span class="k">Nota</span><span class="v">{g["trace"]}</span></div>')
    else:
        badge = CELL_SHORT.get(p["cell"], p["cell"][:3])
        fmt_label = f"CARRUSEL · {len(uris)} láminas" if is_car else "STATIC"
        sub = f'{_fecha(it["date"])} · {p["theme"]}'
        arq = (f'{G.esc(ARQ_LABEL.get(p["archetype"], p["archetype"]))} · hook <code>{p["hook_type"]}</code>'
               f' · CTA <code>{p["cta_type"]}</code>')
        trace = (f'<div class="tr"><span class="k">Ancla</span><span class="v"><code>{cid}</code></span></div>'
                 f'<div class="tr"><span class="k">Evidencia</span><span class="v">{G.esc(it["fact"])}</span></div>'
                 f'<div class="tr"><span class="k">Diversidad</span><span class="v">{arq}<br>'
                 f'<span class="muprompt">pain point: {G.esc(p["pain_point"])}</span></span></div>')
    flag = g.get("flag")
    if flag:
        trace += (f'<div class="tr"><span class="k">Verificar</span><span class="v">'
                  f'<span class="pending">⚠ {G.esc(flag)}</span></span></div>')
    trace += f'<div class="tr"><span class="k">Foto</span><span class="v">{foto}</span></div>'

    strip = ""
    if is_car:
        thumbs = "".join(f'<img class="thumb{" on" if i == 0 else ""}" src="{u}" data-idx="{i}" alt="lámina {i+1}">'
                         for i, u in enumerate(uris))
        strip = f'<div class="strip">{thumbs}</div>'
    # historial: cambios aplicados (graficas.json "hist", más reciente primero) + creación
    log = list(g.get("hist", [])) + [{"date": g.get("created", applied),
                                      "summary": "Pieza y copy DRAFT creados según la tabla de asignación v3 aprobada por MKT."}]
    items_html = "".join(f'<li><span class="hd">{G.esc(e["date"])}</span><span class="hs">{G.esc(e["summary"])}</span></li>'
                         for e in log)
    hist = (f'<details class="hist"><summary>Historial de cambios aplicados ({len(log)})</summary>'
            f'<ul class="histlist">{items_html}</ul></details>')
    title = f"Nov · Post {it['key']} ({_fecha(it['date'])})" if not is_special else f"Nov · Efeméride ({_fecha(it['date'])})"
    label = f"{int(it['key']):02d}" if it["key"].isdigit() else "★"
    return f'''<article class="post{" special" if is_special else ""}" data-seq="{it['key']}" data-cid="{cid}" data-car="{1 if is_car else 0}" data-status="publicado" data-edited-at="" data-edited-by="" data-caltitle="{G.esc(title)}">
  <script type="application/json" class="slides-data">{G.esc(json.dumps(uris))}</script>
  <div class="graphic">
    <div class="gwrap">
      <img class="main" src="{uris[0]}" data-idx="0" alt="Post {label}">
      <span class="fmtbadge">{fmt_label}</span>
      <span class="statuschip pub" data-applied="{applied}">publicado · {applied}</span>
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
    <div class="chead"><span class="seq">{label}</span><span class="badge">{G.esc(badge)}</span>
      <span class="badge ghost">DRAFT</span><span class="sub">{G.esc(sub)}</span></div>

    <label class="lab">Texto del post <span class="hint">— editable, se guarda en tu navegador</span>
      <span class="cc" data-cc>0 / 900</span>
      <button class="revert" type="button" data-field="copy" hidden>↺ volver a lo publicado</button></label>
    <textarea class="copy" data-cid="{cid}" spellcheck="false">{G.esc(it["copy"])}</textarea>

    <label class="lab">Cambios en la imagen / gráfica
      <button class="revert" type="button" data-field="note" hidden>↺ limpiar</button></label>
    <textarea class="imgnote" data-cid="{cid}" spellcheck="false"
      placeholder="Ej.: cambiar la foto por otra de la librería; achicar el titular; mover el círculo…"></textarea>

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

    <div class="trace">{trace}</div>
    {hist}
  </div>
</article>'''


def assemble(month: str, build: Path, out: Path, ws_url: str, applied: str) -> None:
    its = {it["key"]: it for it in items(month)}
    structure = json.loads((build / "structure.json").read_text("utf-8"))
    cards = [card(its[st["key"]], [jpeg_uri(p) for p in st["pngs"]], applied) for st in structure]
    init = {its[st["key"]]["cid"]: {"scheduledFor": its[st["key"]]["date"], "scheduledTime": "09:00"}
            for st in structure}
    y, m = month.split("-")
    mes = MESES[int(m) - 1]
    n_posts = sum(1 for k in its if k.isdigit())
    cfg = {"key": f"idiem_ws_{mes[:3]}{y}_v1", "wsUrl": ws_url, "exportMonth": month,
           "exportTag": f"{mes[:3]}{y}", "ccMax": 900}
    css = (ROOT / "workstation_shared" / "workstation_ui.css").read_text("utf-8")
    js = (ROOT / "workstation_shared" / "workstation_ui.js").read_text("utf-8")
    extra = " + efeméride" if "E" in its else ""
    html = (ARTIFACT.replace("__MES__", mes.capitalize()).replace("__MESL__", mes)
            .replace("__N__", str(n_posts)).replace("__EXTRA__", extra).replace("__MONTH__", month)
            .replace("__CARDS__", "\n".join(cards)).replace("__STATE__", json.dumps(init))
            .replace("__CSS__", css).replace("__JS__", js).replace("__CFG__", json.dumps(cfg)))
    out.write_text(html, encoding="utf-8")
    print(f"assemble: {out} ({out.stat().st_size // 1024} KB, {len(structure)} piezas)")


ARTIFACT = r'''<title>Workstation __MES__ IDIEM</title>
<meta name="description" content="Los __N__ posts de __MESL__ de IDIEM__EXTRA__: gráfica por post, copy DRAFT editable, traza de evidencia y diversidad, agenda, aprobación y estado en LinkedIn con sincronización en vivo.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap">
<style>
[hidden]{display:none!important}
__CSS__
.trace .pending{color:#c77a0a;font-weight:600}
</style>

<div class="wrap">
  <p class="eyebrow"><span class="dot"></span>IDIEM · Design System · Workstation</p>
  <h1>__MES__ — <b>__N__ posts__EXTRA__</b></h1>
  <p class="lede">Primer mes con la <strong>estrategia editorial y control de sesgos</strong>: cada post tiene asignados arquetipo, hook, CTA y pain point (ver <em>Diversidad</em> en la traza). Todos los textos están en <strong>DRAFT</strong> hasta tu aprobación. Cada post muestra su <strong>estado</strong> en la esquina de la gráfica; abajo tienes el texto editable, notas de imagen, el <strong>historial</strong> y <strong>↺ volver a lo publicado</strong>. Todo se <strong>sincroniza en vivo con el equipo</strong>: aprueba (<strong>✅ Aprobado para publicar</strong>), agenda la fecha (ya viene precargada según la grilla) y marca <strong>🔗 subido a LinkedIn</strong> (flujo: <b class="tpub">revisado → aprobado → agendado → subido</b>). Los posts con <strong>⚠ Verificar</strong> requieren validación antes de publicar.</p>
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
    <span>Plan: <code>state/plans/__MONTH___asignacion.json</code> (v3, aprobado MKT) · copies <code>__MONTH___copies.json</code> · gráficas <code>__MONTH___graficas.json</code>.</span>
    <span>2A.2 = fuente de verdad · GR-04 sin superlativos · ≤ 900 caracteres · diversidad según <code>editorial_diversity.json</code>.</span>
    <span>Regeneración de imagen: la aplica Claude al recibir el export.</span>
  </div>
</div>

<script id="ws-state" type="application/json">__STATE__</script>
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
    ap.add_argument("--month", required=True)
    ap.add_argument("--build", required=True)
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--assemble", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--ws-url", default="")
    ap.add_argument("--applied", default="")
    a = ap.parse_args()
    if a.emit:
        emit(a.month, Path(a.build))
    if a.assemble:
        assemble(a.month, Path(a.build), Path(a.out), a.ws_url, a.applied)
