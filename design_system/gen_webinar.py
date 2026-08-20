"""Generate design_system/plantilla_03_webinar.html from the webinar brief,
matching the agency reference layout (photo top + red kicker + gancho; gray panel
with Webinar title, relator, and red date/time card). Data-driven from the brief."""
import base64, json, sys, datetime
sys.path.insert(0, "/home/user/idiem-content-system/src")
from idiem.webinar import build_webinar_plan, load_brief
from idiem.loader import CONFIG_DIR

ROOT = "/home/user/idiem-content-system"
AST = f"{ROOT}/design_system/assets"

def uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()

LOGO = uri(f"{AST}/logo_idiem_oficial.svg", "image/svg+xml")
ESLOGAN = uri(f"{AST}/eslogan_idiem_3_blanco.svg", "image/svg+xml")
IC_CAL = uri(f"{AST}/icon_calendar.png", "image/png")
IC_CLK = uri(f"{AST}/icon_clock.png", "image/png")

RELATOR_PHOTO = {  # relator_id -> local portrait
    "EXP-12": f"{AST}/expositor_paula_araneda.jpg",
    "EXP-01": f"{AST}/expositor_juan_guzman.jpg",
}
DIAS = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
MESES = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto",
         "septiembre","octubre","noviembre","diciembre"]

def fecha_txt(iso):
    try:
        d = datetime.date.fromisoformat(iso)
        return DIAS[d.weekday()], f"{d.day} de {MESES[d.month-1]}"
    except Exception:
        return "", iso

def initials(name):
    parts = [p for p in name.split() if p]
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()

def card(sesion):
    tema = sesion["tema"] or "Webinar"
    gancho = sesion["gancho"] or sesion["titulo"]
    titulo = sesion["titulo"]
    dia, fecha = fecha_txt(sesion["fecha"])
    hora = (sesion["hora"] or "").strip()
    hora_txt = f"{hora} hrs." if hora else ""
    # thematic photo
    foto = sesion.get("foto_tema") or ""
    photo_uri = uri(f"{AST}/{foto}", "image/jpeg") if foto else ""
    # relator
    nombre = sesion["relator_nombre"] or ""
    cargo = sesion["relator_cargo"] or ""
    rid = sesion["relator_id"]
    if rid in RELATOR_PHOTO:
        relator_media = f'<img src="{uri(RELATOR_PHOTO[rid],"image/jpeg")}" alt="{nombre}">'
    else:
        relator_media = f'<div class="avatar">{initials(nombre)}</div>'
    photo_style = f'background-image:url({photo_uri})' if photo_uri else 'background:#4a4d4e'
    return f"""
    <div class="wcard">
      <div class="photo" style="{photo_style}"></div>
      <div class="photo-grad"></div>
      <img class="eslogan" src="{ESLOGAN}" alt="Elige bien. Elige idiem.">
      <div class="logo125">
        <img class="lg" src="{LOGO}" alt="idiem">
        <span class="bar"></span>
        <span class="an"><b>125</b><i class="dot"></i><em>años</em></span>
      </div>
      <div class="photo-copy">
        <span class="kicker">{tema}</span>
        <div class="gancho fit" data-max="6.4" data-min="3.4">{gancho}</div>
      </div>
      <div class="panel">
        <span class="pill">Webinar:</span>
        <div class="wtitle fit" data-max="4.2" data-min="2.5">{titulo}</div>
        <div class="hr"></div>
        <span class="pill mini">Relator</span>
        <div class="prow">
          <div class="relator">
            <div class="disc">{relator_media}</div>
            <div class="rinfo"><div class="rname">{nombre.upper()}</div><div class="rcargo">{cargo}</div></div>
          </div>
          <div class="datecard">
            <div class="drow"><img src="{IC_CAL}" alt=""><span>{dia}<br>{fecha}</span></div>
            <div class="dhr"></div>
            <div class="drow"><img src="{IC_CLK}" alt=""><span>{hora_txt}</span></div>
          </div>
        </div>
      </div>
    </div>"""

plan = build_webinar_plan(load_brief(CONFIG_DIR / "webinar" / "example_brief.json"))
static_card = card(plan["sesiones"][0])
ciclo_cards = "\n".join(card(s) for s in plan["sesiones"])

HTML = f"""<title>Plantilla Webinar</title>
<meta name="description" content="Paso 3 del Design System IDIEM: la plantilla de Webinar (insumo externo) con el layout oficial de la agencia — foto temática + bloque rojo + gancho, y panel gris con relator y tarjeta de fecha. Estático para un webinar; se agregan slides para un ciclo.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap">
<style>
  :root{{--red:#e1261d;--gray-blue:#666d72;--gray-light:#efefef;--gray-dark:#2f3030;
    --ink:#22262a;--paper:#f6f6f4;--card:#fff;--line:rgba(47,48,48,.12);--muted:#6a7075;
    --shadow:0 24px 60px -28px rgba(47,48,48,.45);--mono:"Montserrat",system-ui,sans-serif;}}
  @media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--ink:#eef0f0;--paper:#17191a;--card:#202324;--gray-light:#2a2d2e;--line:rgba(239,239,239,.12);--muted:#9aa1a5;--shadow:0 26px 70px -30px rgba(0,0,0,.75);}}}}
  :root[data-theme="dark"]{{--ink:#eef0f0;--paper:#17191a;--card:#202324;--gray-light:#2a2d2e;--line:rgba(239,239,239,.12);--muted:#9aa1a5;--shadow:0 26px 70px -30px rgba(0,0,0,.75);}}
  *{{box-sizing:border-box}} html{{-webkit-text-size-adjust:100%}}
  body{{margin:0;font-family:var(--mono);background:var(--paper);color:var(--ink);line-height:1.55;padding:clamp(20px,4vw,64px) clamp(16px,4vw,64px) 80px}}
  .wrap{{max-width:1200px;margin:0 auto}}
  .eyebrow{{display:inline-flex;align-items:center;gap:.6em;font-size:.72rem;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--red);margin:0 0 14px}}
  .eyebrow .dot{{width:.5em;height:.5em;border-radius:50%;background:var(--red)}}
  h1.title{{font-size:clamp(1.9rem,4.6vw,3rem);font-weight:800;letter-spacing:-.02em;line-height:1.05;margin:0 0 .5rem;text-wrap:balance}} h1.title b{{color:var(--red)}}
  .lede{{font-size:clamp(1rem,1.7vw,1.16rem);color:var(--muted);max-width:64ch;margin:0 0 1.4rem}}
  .meta{{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 22px;font-size:.78rem}}
  .chip{{display:inline-flex;align-items:center;gap:.5em;padding:6px 12px;border:1px solid var(--line);border-radius:100px;background:var(--card);color:var(--ink);font-weight:500}} .chip b{{color:var(--red);font-weight:700}}
  h2.sec{{font-size:.8rem;font-weight:800;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);margin:34px 0 14px;display:flex;align-items:center;gap:10px}}
  h2.sec::before{{content:"";width:22px;height:3px;background:var(--red);border-radius:2px}}

  /* ===== webinar card ===== */
  .wcard{{container-type:inline-size;position:relative;width:min(560px,86vw);aspect-ratio:1/1;overflow:hidden;border-radius:10px;box-shadow:var(--shadow);background:var(--gray-dark);color:#fff;isolation:isolate;user-select:none}}
  .photo{{position:absolute;left:0;top:0;width:100%;height:48cqw;z-index:0;background-size:cover;background-position:50% 46%}}
  .photo-grad{{position:absolute;left:0;top:0;width:100%;height:48cqw;z-index:1;background:linear-gradient(0deg,rgba(0,0,0,.62) 0%,rgba(0,0,0,.05) 34%,rgba(0,0,0,.28) 100%)}}
  .eslogan{{position:absolute;z-index:3;top:4.4cqw;left:4.8cqw;width:30cqw;height:auto;filter:drop-shadow(0 1px 8px rgba(0,0,0,.5))}}
  .logo125{{position:absolute;z-index:3;top:4.6cqw;right:4.8cqw;display:flex;align-items:center;gap:2.4cqw;filter:drop-shadow(0 1px 8px rgba(0,0,0,.5))}}
  .logo125 .lg{{width:15cqw;height:auto;display:block}}
  .logo125 .bar{{width:.34cqw;height:7.4cqw;background:#fff;opacity:.9;border-radius:2px}}
  .logo125 .an{{display:flex;flex-direction:column;line-height:1;color:#fff}}
  .logo125 .an b{{font-size:5.4cqw;font-weight:800;letter-spacing:-.02em;position:relative}}
  .logo125 .an .dot{{position:absolute;right:-1.9cqw;top:.2cqw;width:1.5cqw;height:1.5cqw;border-radius:50%;background:var(--red)}}
  .logo125 .an em{{font-style:normal;font-size:2.1cqw;font-weight:600;letter-spacing:.02em;margin-top:.3cqw}}
  .photo-copy{{position:absolute;z-index:3;left:4.8cqw;right:6cqw;top:46cqw;transform:translateY(-100%);display:flex;flex-direction:column;align-items:flex-start;gap:2.4cqw}}
  .kicker{{background:var(--red);color:#fff;font-weight:800;font-size:4.4cqw;letter-spacing:-.005em;padding:1.3cqw 2.4cqw;border-radius:.4cqw}}
  .gancho{{font-weight:800;line-height:1.04;letter-spacing:-.015em;text-shadow:0 2px 14px rgba(0,0,0,.5);max-width:78cqw;max-height:20cqw;overflow:hidden}}

  .panel{{position:absolute;left:0;top:48cqw;width:100%;height:52cqw;z-index:2;background:var(--gray-dark);padding:4.2cqw 5cqw 4.2cqw}}
  .pill{{display:inline-block;background:var(--gray-blue);color:#fff;font-weight:700;font-size:2.7cqw;letter-spacing:.02em;padding:1cqw 2.6cqw;border-radius:.7cqw}}
  .pill.mini{{font-size:2.5cqw;padding:.8cqw 2.4cqw}}
  .wtitle{{font-weight:800;line-height:1.08;letter-spacing:-.01em;color:#fff;margin-top:2cqw;max-width:90cqw;max-height:11cqw;overflow:hidden}}
  .hr{{height:1px;background:rgba(255,255,255,.22);margin:2.6cqw 0 2.2cqw;width:70cqw}}
  .prow{{display:flex;align-items:center;justify-content:space-between;gap:3cqw;margin-top:2.4cqw}}
  .relator{{display:flex;align-items:center;gap:3cqw;min-width:0}}
  .relator .disc{{position:relative;width:16cqw;height:16cqw;flex:none;border-radius:50%;background:#fff;padding:.7cqw}}
  .relator .disc img{{width:100%;height:100%;object-fit:cover;object-position:50% 20%;border-radius:50%;display:block}}
  .relator .disc .avatar{{width:100%;height:100%;border-radius:50%;background:var(--red);display:flex;align-items:center;justify-content:center;font-size:6.5cqw;font-weight:800;color:#fff}}
  .relator .rname{{font-size:3cqw;font-weight:800;letter-spacing:.01em;white-space:nowrap}}
  .relator .rcargo{{font-size:2.2cqw;font-weight:500;color:rgba(255,255,255,.82);line-height:1.22;margin-top:.5cqw;max-width:30cqw}}
  .datecard{{flex:none;background:var(--red);border-radius:2.2cqw;padding:2.6cqw 3cqw;display:flex;flex-direction:column;gap:1.6cqw;min-width:30cqw}}
  .datecard .drow{{display:flex;align-items:center;gap:2.4cqw}}
  .datecard .drow img{{width:4.6cqw;height:4.6cqw;object-fit:contain;flex:none}}
  .datecard .drow span{{font-size:2.9cqw;font-weight:700;color:#fff;line-height:1.12}}
  .datecard .dhr{{height:1px;background:rgba(255,255,255,.4);margin:0 .5cqw}}

  .cap{{font-size:.8rem;color:var(--muted);margin:8px 0 0}}
  .stage{{display:flex;justify-content:flex-start}}
  .strip{{display:flex;gap:18px;overflow-x:auto;padding:6px 2px 18px;scroll-snap-type:x mandatory}}
  .strip .wcard{{flex:0 0 auto;width:min(460px,80vw);scroll-snap-align:center}}
  .grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px}}
  @media (max-width:820px){{.grid{{grid-template-columns:1fr}}}}
  .p{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:clamp(16px,2.2vw,22px)}}
  .p h3{{margin:0 0 8px;font-size:.72rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:var(--red)}}
  .p p{{margin:0 0 8px;font-size:.9rem;color:var(--muted)}} .p p b{{color:var(--ink);font-weight:600}}
  .p code{{font-family:var(--mono);font-weight:600;background:var(--gray-light);padding:1px 6px;border-radius:5px;font-size:.84em}}
  .foot{{margin-top:30px;padding-top:18px;border-top:1px solid var(--line);font-size:.8rem;color:var(--muted);display:flex;flex-wrap:wrap;gap:6px 18px}}
  .foot code{{font-family:var(--mono);font-weight:600;background:var(--gray-light);padding:1px 6px;border-radius:5px}}
</style>

<div class="wrap">
  <p class="eyebrow"><span class="dot"></span>IDIEM · Design System · Paso 3 · v2</p>
  <h1 class="title">Plantilla 03 — <b>Webinar</b></h1>
  <p class="lede">Layout oficial de la agencia: <strong>foto temática</strong> arriba (con eslogan, logo 125 años, bloque rojo del tema y título-gancho) y <strong>panel gris</strong> abajo (título del webinar, relator y tarjeta roja de fecha/hora). <strong>Insumo externo</strong>, no ocupa los 12 del mes. Con una sesión es estático; para un <strong>ciclo</strong> se agregan slides con el mismo diseño y <strong>cambia la foto superior</strong> por tema.</p>
  <div class="meta">
    <span class="chip">Insumo <b>externo</b></span>
    <span class="chip">No ocupa los <b>12</b> del mes</span>
    <span class="chip">Texto <b>auto-ajustable</b></span>
    <span class="chip">Foto temática cambia por sesión</span>
  </div>

  <h2 class="sec">Modo estático · un webinar</h2>
  <div class="stage">{static_card}</div>
  <p class="cap">Reproducción del layout de referencia, generado desde el brief (sesión 1). El título se ajusta solo si es largo.</p>

  <h2 class="sec">Modo carrusel · ciclo (cambia la foto superior por tema)</h2>
  <div class="strip">{ciclo_cards}</div>
  <p class="cap">↔ Un slide por webinar, mismo diseño; la foto de la mitad superior cambia según el tema de cada sesión.</p>

  <div class="grid">
    <div class="p"><h3>El brief</h3><p>Campos por sesión: <b>tema</b> (bloque rojo), <b>gancho</b> (título grande), <b>foto_tema</b> (foto superior), <b>título</b> del webinar, fecha/hora, modalidad, plataforma, <b>URL de sesión</b> e <b>inscripción</b>, y relator.</p><p><code>config/webinar/webinar_brief.schema.json</code></p></div>
    <div class="p"><h3>Reglas &amp; grounding</h3><p><b>1 sesión → estático · 2+ → carrusel.</b> Relator y foto desde <code>config/expositor_library/expositores.csv</code>. Si no hay foto temática en la librería, se genera con <b>Muapi</b> (profesional, sin texto).</p><p>Logística = dato libre; claim técnico en el temario sigue las reglas de la librería.</p></div>
  </div>
  <div class="foot">
    <span>Brief: <code>config/webinar/example_brief.json</code></span>
    <span>Motor: <code>src/idiem/webinar.py</code></span>
    <span>Relator real: <code>EXP-12</code> · Paula Araneda</span>
  </div>
</div>

<script>
  function fit(el){{
    const max=parseFloat(el.dataset.max), min=parseFloat(el.dataset.min);
    let fs=max; el.style.fontSize=fs+'cqw';
    let g=0;
    while((el.scrollHeight>el.clientHeight+1) && fs>min && g<60){{ fs-=0.2; el.style.fontSize=fs+'cqw'; g++; }}
  }}
  function fitAll(){{ document.querySelectorAll('.fit').forEach(fit); }}
  if(document.fonts && document.fonts.ready){{ document.fonts.ready.then(fitAll); }}
  window.addEventListener('load', fitAll);
  window.addEventListener('resize', ()=>{{ clearTimeout(window.__ft); window.__ft=setTimeout(fitAll,120); }});
</script>
"""

out = f"{ROOT}/design_system/plantilla_03_webinar.html"
open(out, "w").write(HTML)
print("wrote", out, len(HTML), "bytes")
