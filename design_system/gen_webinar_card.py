"""Emit a single 1080x1080 webinar card (Plantilla 03) ready to rasterize.

Reuses the official webinar layout (foto temática arriba + kicker rojo + gancho;
panel gris con "Webinar:" + título + relator + tarjeta roja de fecha/hora) from
`gen_webinar.py`, but wraps ONE session in an `.export` 1080x1080 container so
`render_bundle.cjs` can screenshot it to PNG. Data-driven from a brief.

Uso:
  PYTHONPATH=src python3 design_system/gen_webinar_card.py \
      config/webinar/acero_estructural_brief.json 0 > /tmp/.../webinar_card.html
"""
from __future__ import annotations

import base64
import datetime
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AST = ROOT / "design_system" / "assets"
sys.path.insert(0, str(ROOT / "src"))
from idiem.webinar import build_webinar_plan, load_brief  # noqa: E402

RELATOR_PHOTO = {
    "EXP-12": AST / "expositor_paula_araneda.jpg",
    "EXP-01": AST / "expositor_juan_guzman.jpg",
    "EXP-08": AST / "expositor_david_silva.jpg",
}

# Encuadre de la foto temática (portrait/landscape) por archivo: background-position
FOTO_POS = {
    "webinar_tema_acero_estructural.jpg": "50% 64%",
}

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


def uri(path: Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


LOGO = uri(AST / "logo_idiem_oficial.svg", "image/svg+xml")
ESLOGAN = uri(AST / "eslogan_idiem_3_blanco.svg", "image/svg+xml")
IC_CAL = uri(AST / "icon_calendar.png", "image/png")
IC_CLK = uri(AST / "icon_clock.png", "image/png")


def fecha_txt(iso: str) -> tuple[str, str]:
    try:
        d = datetime.date.fromisoformat(iso)
        return DIAS[d.weekday()], f"{d.day} de {MESES[d.month - 1]}"
    except Exception:
        return "", iso


def initials(name: str) -> str:
    parts = [p for p in name.split() if p]
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()


def card(sesion: dict) -> str:
    tema = sesion["tema"] or "Webinar"
    gancho = sesion["gancho"] or sesion["titulo"]
    titulo = sesion["titulo"]
    dia, fecha = fecha_txt(sesion["fecha"])
    hora = (sesion["hora"] or "").strip()
    hora_txt = f"{hora} hrs." if hora else ""
    foto = sesion.get("foto_tema") or ""
    photo_uri = uri(AST / foto, "image/jpeg") if foto else ""
    pos = FOTO_POS.get(foto, "50% 46%")
    nombre = sesion["relator_nombre"] or ""
    cargo = sesion["relator_cargo"] or ""
    rid = sesion["relator_id"]
    if rid in RELATOR_PHOTO:
        relator_media = f'<img src="{uri(RELATOR_PHOTO[rid], "image/jpeg")}" alt="{nombre}">'
    else:
        relator_media = f'<div class="avatar">{initials(nombre)}</div>'
    photo_style = (f'background-image:url({photo_uri});background-position:{pos}'
                   if photo_uri else 'background:#4a4d4e')
    return f"""
    <div class="wcard">
      <div class="photo" style="{photo_style}"></div>
      <div class="photo-grad"></div>
      <img class="eslogan" src="{ESLOGAN}" alt="Elige bien. Elige idiem.">
      <img class="logo" src="{LOGO}" alt="idiem">
      <div class="photo-copy">
        <span class="kicker">{tema}</span>
        <div class="gancho fit" data-max="6.0" data-min="3.2">{gancho}</div>
      </div>
      <div class="panel">
        <span class="pill">Webinar:</span>
        <div class="wtitle fit" data-max="3.9" data-min="2.4">{titulo}</div>
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


CSS = r"""
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#fff}
body{font-family:"Montserrat",system-ui,sans-serif}
.export{width:1080px;height:1080px;overflow:hidden;position:relative}
:root{--red:#e1261d;--gray-blue:#666d72;--gray-dark:#2f3030}
.wcard{container-type:inline-size;position:relative;width:1080px;height:1080px;overflow:hidden;
  background:var(--gray-dark);color:#fff;isolation:isolate;user-select:none}
.photo{position:absolute;left:0;top:0;width:100%;height:46cqw;z-index:0;background-size:cover;background-position:50% 46%}
.photo-grad{position:absolute;left:0;top:0;width:100%;height:46cqw;z-index:1;
  background:linear-gradient(0deg,rgba(0,0,0,.62) 0%,rgba(0,0,0,.05) 34%,rgba(0,0,0,.28) 100%)}
.eslogan{position:absolute;z-index:3;top:4.4cqw;left:4.8cqw;width:30cqw;height:auto;filter:drop-shadow(0 1px 8px rgba(0,0,0,.5))}
.logo{position:absolute;z-index:3;top:5cqw;right:5cqw;width:19cqw;height:auto;display:block;filter:drop-shadow(0 1px 8px rgba(0,0,0,.5))}
.photo-copy{position:absolute;z-index:3;left:4.8cqw;right:6cqw;top:44cqw;transform:translateY(-100%);
  display:flex;flex-direction:column;align-items:flex-start;gap:2.4cqw}
.kicker{background:var(--red);color:#fff;font-weight:800;font-size:4.4cqw;letter-spacing:-.005em;padding:1.3cqw 2.4cqw;border-radius:.4cqw}
.gancho{font-weight:800;line-height:1.04;letter-spacing:-.015em;text-shadow:0 2px 14px rgba(0,0,0,.5);max-width:78cqw;max-height:20cqw;overflow:hidden}
.panel{position:absolute;left:0;top:46cqw;width:100%;height:54cqw;z-index:2;background:var(--gray-dark);padding:4cqw 5cqw 5.6cqw}
.pill{display:inline-block;background:var(--gray-blue);color:#fff;font-weight:700;font-size:2.7cqw;letter-spacing:.02em;padding:1cqw 2.6cqw;border-radius:.7cqw}
.pill.mini{font-size:2.5cqw;padding:.8cqw 2.4cqw}
.wtitle{font-weight:800;line-height:1.08;letter-spacing:-.01em;color:#fff;margin-top:1.8cqw;max-width:90cqw;max-height:12cqw;overflow:hidden}
.hr{height:1px;background:rgba(255,255,255,.22);margin:2.2cqw 0 1.8cqw;width:70cqw}
.prow{display:flex;align-items:center;justify-content:space-between;gap:3cqw;margin-top:2cqw}
.relator{display:flex;align-items:center;gap:3cqw;min-width:0}
.relator .disc{position:relative;width:15.5cqw;height:15.5cqw;flex:none;border-radius:50%;background:#fff;padding:.7cqw}
.relator .disc img{width:100%;height:100%;object-fit:cover;object-position:50% 18%;border-radius:50%;display:block}
.relator .disc .avatar{width:100%;height:100%;border-radius:50%;background:var(--red);display:flex;align-items:center;justify-content:center;font-size:6.5cqw;font-weight:800;color:#fff}
.relator .rname{font-size:3.1cqw;font-weight:800;letter-spacing:.01em;white-space:nowrap}
.relator .rcargo{font-size:2.15cqw;font-weight:500;color:rgba(255,255,255,.82);line-height:1.22;margin-top:.5cqw;max-width:34cqw}
.datecard{flex:none;background:var(--red);border-radius:2cqw;padding:2.3cqw 2.8cqw;display:flex;flex-direction:column;gap:1.3cqw;min-width:29cqw}
.datecard .drow{display:flex;align-items:center;gap:2.4cqw}
.datecard .drow img{width:4.2cqw;height:4.2cqw;object-fit:contain;flex:none}
.datecard .drow span{font-size:2.85cqw;font-weight:700;color:#fff;line-height:1.12}
.datecard .dhr{height:1px;background:rgba(255,255,255,.4);margin:0 .5cqw}
"""

FIT_JS = r"""
function fit(el){
  var max=parseFloat(el.dataset.max), min=parseFloat(el.dataset.min);
  var fs=max; el.style.fontSize=fs+'cqw'; var g=0;
  while((el.scrollHeight>el.clientHeight+1) && fs>min && g<80){ fs-=0.15; el.style.fontSize=fs+'cqw'; g++; }
}
function fitAll(){ document.querySelectorAll('.fit').forEach(fit); }
document.addEventListener('DOMContentLoaded', fitAll);
if(document.fonts && document.fonts.ready){ document.fonts.ready.then(fitAll); }
window.addEventListener('load', function(){ fitAll(); setTimeout(fitAll,120); });
"""


def main() -> None:
    brief_path = sys.argv[1] if len(sys.argv) > 1 else str(
        ROOT / "config" / "webinar" / "acero_estructural_brief.json")
    idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    plan = build_webinar_plan(load_brief(brief_path))
    html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>Webinar IDIEM</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap">
<style>{CSS}</style></head>
<body><div class="export">{card(plan["sesiones"][idx])}</div>
<script>{FIT_JS}</script></body></html>"""
    sys.stdout.write(html)


if __name__ == "__main__":
    main()
