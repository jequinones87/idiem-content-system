"""Workstation del ciclo de webinar (Acero estructural) — MISMA LÍNEA que la
workstation mensual de octubre: reusa el frontend/backend compartido
(design_system/workstation_shared/workstation_ui.{css,js}) con sync en vivo por
la capacidad `db`, estados publicado/pendiente/listo, aprobar, subido a LinkedIn,
agendar en Google Calendar, notas de imagen + regeneración, PNG/PDF, historial,
traza y lightbox. Solo cambian los datos (5 piezas del webinar) y la config
(WSCFG: key, wsUrl, export).

Uso:
  python3 design_system/gen_webinar_workstation.py > /tmp/.../webinar_ws.html
Requiere los PNG renderizados en SLIDES (inv, live, car1..car4).
"""
from __future__ import annotations

import base64
import io
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "design_system" / "workstation_shared"
SLIDES = Path("/tmp/claude-0/-home-user-idiem-content-system/"
              "1c5b178b-f8ee-5946-beb8-9cf3fffd70df/scratchpad/wslides")

WS_URL = "https://claude.ai/artifact/9VHLEeZ2WYm2pUwyhb4FkA"
FORM = ("https://docs.google.com/forms/d/e/1FAIpQLSdIHQss1ajlR2E1cQAU7EPPUZlaVJ5OGU4h8"
        "T6kh_b76fDHCQ/viewform?usp=pp_url&entry.1892003034=LinkedIn")
ZOOM = "https://us02web.zoom.us/j/84226077802?pwd=basVXzx7rE41rnjqLR0z1oGa4vCzW3.1"
APPLIED = "30-09-2026"


def jpeg_uri(name: str, q: int = 86) -> str:
    im = Image.open(SLIDES / f"{name}.png").convert("RGB")
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


COPY = {
 1: (
  "🏗️ El acero estructural de un proyecto minero o industrial hoy puede provenir de casi "
  "cualquier parte del mundo. Asegurar su calidad conforme a la NCh203 ya no se resuelve "
  "solo con un certificado de materiales.\n\n"
  "Cadenas de suministro globales, nuevos modelos de contratación y múltiples actores hacen "
  "que mantener la trazabilidad y verificar el cumplimiento normativo sea cada vez más "
  "desafiante. 📋\n\n"
  "En #IDIEM —laboratorio de ensayos, organismo certificador y centro de investigación "
  "aplicada— hemos participado durante años en el control y la certificación de acero "
  "estructural para proyectos mineros e industriales. Te invitamos a este webinar para "
  "compartir aprendizajes y buenas prácticas. ✅\n\n"
  "🎙️ David Silva, Jefe División Aceros Control de IDIEM\n"
  "🗓️ Miércoles 14 de octubre · 09:30 hrs (Chile) · Online\n\n"
  f"📩 Inscríbete aquí 👉 {FORM}\n\n"
  "#IDIEM #AceroEstructural #NCh203 #Minería #Industria #AseguramientoDeCalidad #Certificación"),

 2: (
  "🔎 ¿Por qué volver a mirar la NCh203? Porque el escenario del acero estructural cambió.\n\n"
  "El abastecimiento y la fabricación de estructuras hoy involucran cadenas de suministro "
  "globales y múltiples actores. Asegurar la conformidad va mucho más allá de un certificado "
  "de materiales: exige trazabilidad y evidencia técnica a lo largo de todo el proyecto. 📋\n\n"
  "Desliza para ver por qué es relevante y qué abordaremos en el webinar 👉\n\n"
  "En #IDIEM —laboratorio de ensayos, organismo certificador y centro de investigación "
  "aplicada— compartiremos los aprendizajes de años controlando y certificando acero "
  "estructural para proyectos mineros e industriales.\n\n"
  "🎙️ David Silva, Jefe División Aceros Control de IDIEM\n"
  "🗓️ Miércoles 14 de octubre · 09:30 hrs (Chile) · Online\n\n"
  f"📩 Inscríbete aquí 👉 {FORM}\n\n"
  "#IDIEM #AceroEstructural #NCh203 #Minería #Industria #AseguramientoDeCalidad"),

 3: (
  "🧩 Un certificado de materiales no basta. La conformidad con la NCh203 se juega en la "
  "trazabilidad y en la evidencia técnica que respalda el cumplimiento a lo largo del "
  "proyecto.\n\n"
  "¿Dónde aparecen las principales brechas? En la trazabilidad entre el origen del acero, la "
  "fabricación de la estructura y la recepción en obra, con múltiples actores involucrados. 🔍\n\n"
  "En este webinar, David Silva —Jefe División Aceros Control de IDIEM— compartirá los "
  "aprendizajes de años en control y certificación de acero estructural, y buenas prácticas "
  "para cerrar esas brechas, independiente del origen del acero o del lugar de fabricación. ✅\n\n"
  "🗓️ Miércoles 14 de octubre · 09:30 hrs (Chile) · Online\n\n"
  f"📩 Inscríbete aquí 👉 {FORM}\n\n"
  "#IDIEM #AceroEstructural #NCh203 #Minería #Industria #Trazabilidad #Certificación"),

 4: (
  "⏰ Mañana: webinar «Acero estructural en proyectos mineros e industriales».\n\n"
  "Si participas en la especificación, suministro, fabricación, inspección o recepción de "
  "estructuras de acero, esta conversación es para ti. Hablaremos de qué ha cambiado en la "
  "aplicación de la NCh203, las brechas más recurrentes en trazabilidad y el rol del "
  "laboratorio y la certificación en el aseguramiento de calidad. 🧱\n\n"
  "🎙️ David Silva, Jefe División Aceros Control de IDIEM\n"
  "🗓️ Miércoles 14 de octubre · 09:30 hrs (Chile) · Online\n\n"
  f"Aún estás a tiempo de inscribirte 📩 👉 {FORM}\n\n"
  "#IDIEM #AceroEstructural #NCh203 #Minería #Industria #AseguramientoDeCalidad"),

 5: (
  "🔴 ¡Hoy es el día! Webinar «Acero estructural en proyectos mineros e industriales».\n\n"
  "Hoy conversamos sobre los aprendizajes y desafíos del aseguramiento de calidad del acero "
  "estructural conforme a la NCh203, junto a David Silva, Jefe División Aceros Control de "
  "IDIEM. 🧱\n\n"
  "🕘 Hoy, 09:30 hrs (Chile)\n"
  f"🎥 Ingresa por Zoom 👉 {ZOOM}\n\n"
  "¡Te esperamos! ✅\n\n"
  "#IDIEM #AceroEstructural #NCh203 #Minería #Industria #Webinar"),
}

# seq -> (fecha_label, objetivo, tipo, [slides], link(nombre,url), sched(date,time), imagen_traza, historial[(fecha,txt)])
POSTS = {
 1: {"fecha": "1 oct", "obj": "Apertura de inscripciones", "tipo": "STATIC", "slides": ["inv"],
     "sched": ("2026-10-01", "09:00"),
     "imagen": "Banner de serie (provisto por MKT) · relator David Silva",
     "hist": [(APPLIED, "Pieza creada para la serie del webinar del 14-oct (relator David Silva)."),
              (APPLIED, "Banner fijo de la serie (imagen provista por MKT) + logo/eslogan."),
              (APPLIED, "Layout: foto de David ampliada + credenciales; íconos de fecha en blanco.")]},
 2: {"fecha": "5 oct", "obj": "Relevancia + temática", "tipo": "CARRUSEL", "slides": ["car1", "car2", "car3", "car4"],
     "sched": ("2026-10-05", "09:00"),
     "imagen": "Banner + láminas de contenido (portada · contexto NCh203 · temario · cierre)",
     "hist": [(APPLIED, "Carrusel de 4 láminas creado para la serie del webinar."),
              (APPLIED, "Contexto NCh203 (cadena de suministro global) + temario de 5 puntos."),
              (APPLIED, "Cierre con relator y CTA de inscripción.")]},
 3: {"fecha": "8 oct", "obj": "Recordatorio · trazabilidad", "tipo": "STATIC", "slides": ["inv"],
     "sched": ("2026-10-08", "09:00"),
     "imagen": "Banner de serie (provisto por MKT) · relator David Silva",
     "hist": [(APPLIED, "Recordatorio: misma gráfica de invitación, copy con foco en trazabilidad/brechas.")]},
 4: {"fecha": "13 oct", "obj": "Víspera del evento", "tipo": "STATIC", "slides": ["inv"],
     "sched": ("2026-10-13", "09:00"),
     "imagen": "Banner de serie (provisto por MKT) · relator David Silva",
     "hist": [(APPLIED, "Víspera: misma gráfica de invitación, copy '⏰ mañana' + últimas inscripciones.")]},
 5: {"fecha": "14 oct", "obj": "Día del evento · ingreso", "tipo": "STATIC", "slides": ["live"],
     "sched": ("2026-10-14", "08:00"),
     "imagen": "Banner · variante día del evento (ingreso por Zoom)",
     "hist": [(APPLIED, "Variante 'día del evento': '🔴 ¡Webinar hoy!' + tarjeta 'Ingresa por Zoom'."),
              (APPLIED, "El link de Zoom va SOLO en este post; posts 1–4 llevan el formulario.")]},
}

# data URIs (una vez por gráfica usada)
_USED = sorted({g for p in POSTS.values() for g in p["slides"]})
IMG = {g: jpeg_uri(g) for g in _USED}


def cid_of(seq: int) -> str:
    return f"WEB-ACERO-{seq:02d}"


def card(seq: int) -> str:
    p = POSTS[seq]
    cid = cid_of(seq)
    slides = [IMG[g] for g in p["slides"]]
    slides_json = json.dumps(slides)
    main = slides[0]
    car = 1 if p["tipo"] == "CARRUSEL" else 0
    link_name, link_url = ("Formulario de inscripción", FORM) if seq != 5 else ("Link de Zoom (solo hoy)", ZOOM)

    strip = ""
    if car:
        thumbs = "".join(
            f'<img class="thumb{" on" if i == 0 else ""}" data-idx="{i}" src="{u}" alt="lámina {i+1}">'
            for i, u in enumerate(slides))
        strip = f'<div class="strip">{thumbs}</div>'

    hist = p["hist"]
    hist_items = "".join(
        f'<li><span class="hd">{esc(d)}</span><span class="hs">{esc(t)}</span></li>' for d, t in hist)

    return f'''<article class="post" data-seq="{seq}" data-cid="{cid}" data-car="{car}" data-status="publicado" data-edited-at="" data-edited-by="" data-caltitle="Webinar Acero · Post {seq} ({esc(p['fecha'])})">
  <script type="application/json" class="slides-data">{slides_json}</script>
  <div class="graphic">
    <div class="gwrap">
      <img class="main" src="{main}" data-idx="0" alt="Post {seq}">
      <span class="fmtbadge">{p['tipo']}</span>
      <span class="statuschip pub" data-applied="{APPLIED}">publicado · {APPLIED}</span>
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
    <div class="chead"><span class="seq">{seq:02d}</span><span class="badge">WEBINAR</span>
      <span class="badge ghost">{p['tipo']}</span><span class="sub">{esc(p['fecha'])} · {esc(p['obj'])}</span></div>

    <label class="lab">Texto del post <span class="hint">— editable, se guarda en tu navegador</span>
      <span class="cc" data-cc>0 / 900</span>
      <button class="revert" type="button" data-field="copy" hidden>↺ volver a lo publicado</button></label>
    <textarea class="copy" data-cid="{cid}" spellcheck="false">{esc(COPY[seq])}</textarea>

    <label class="lab">Cambios en la imagen / gráfica
      <button class="revert" type="button" data-field="note" hidden>↺ limpiar</button></label>
    <textarea class="imgnote" data-cid="{cid}" spellcheck="false"
      placeholder="Ej.: cambiar el encuadre del banner; achicar el titular; otra lámina de cierre…"></textarea>

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
      <div class="tr"><span class="k">Ancla</span><span class="v"><code>{cid}</code> · webinar (insumo externo)</span></div>
      <div class="tr"><span class="k">Fuente</span><span class="v">Brief · <code>config/webinar/acero_estructural_brief.json</code> · logística de evento (dato libre)</span></div>
      <div class="tr"><span class="k">Imagen</span><span class="v">{esc(p['imagen'])}</span></div>
    </div>
    <details class="hist"><summary>Historial de cambios aplicados ({len(hist)})</summary><ul class="histlist">{hist_items}</ul></details>
  </div>
</article>'''


def build() -> str:
    css = (SHARED / "workstation_ui.css").read_text()
    js = (SHARED / "workstation_ui.js").read_text()
    cards = "\n".join(card(s) for s in sorted(POSTS))

    # estado inicial embebido: agenda pre-cargada con las fechas de campaña
    init = {}
    for s in sorted(POSTS):
        d, t = POSTS[s]["sched"]
        init[cid_of(s)] = {"scheduledFor": d, "scheduledTime": t}
    state_json = json.dumps(init, ensure_ascii=False)

    cfg = {"key": "idiem_ws_webinar_acero_v1", "wsUrl": WS_URL,
           "exportMonth": "webinar-acero-2026", "exportTag": "webinar_acero", "ccMax": 1300}
    cfg_json = json.dumps(cfg, ensure_ascii=False)

    return f'''<title>Workstation Webinar Acero · IDIEM</title>
<meta name="description" content="Serie de 5 posts del webinar de acero estructural (NCh203, 14-oct): gráfica por post, texto editable, notas de imagen, agenda en Google Calendar, aprobación y estado en LinkedIn, con sincronización en vivo con el equipo.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap">
<style>
[hidden]{{display:none!important}}
{css}
</style>

<div class="wrap">
  <p class="eyebrow"><span class="dot"></span>IDIEM · Design System · Workstation · Webinar</p>
  <h1>Webinar Acero estructural — <b>5 posts</b></h1>
  <p class="lede">Serie de difusión del webinar del <strong>14 de octubre</strong> (relator David Silva). Cada post muestra su <strong>estado</strong> en la esquina de la gráfica. Abajo tienes el texto editable, notas de imagen, el <strong>historial</strong> y <strong>↺ volver a lo publicado</strong>. Todo se <strong>sincroniza en vivo con el equipo</strong>: aprueba (<strong>✅ Aprobado para publicar</strong>), agenda la fecha, y marca <strong>🔗 subido a LinkedIn</strong> (flujo: <b class="tpub">revisado → aprobado → agendado → subido</b>). No necesitas guardar: se guarda solo. <em>Insumo externo del webinar: no traza a knowledge_id; el link de Zoom va solo en el post del día del evento.</em></p>
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
{cards}
  </div>

  <div class="foot">
    <span>Serie del webinar · misma línea que la workstation mensual (frontend/backend compartido).</span>
    <span>Inscripción: Google Forms · Zoom solo en el post del día del evento.</span>
  </div>
</div>

<script id="ws-state" type="application/json">{state_json}</script>
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

<script>window.WSCFG={cfg_json};</script>
<script>
{js}
</script>'''


if __name__ == "__main__":
    import sys
    sys.stdout.write(build())
