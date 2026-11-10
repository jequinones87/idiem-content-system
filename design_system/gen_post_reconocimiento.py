"""Post estático 1080x1080 de reconocimiento a una persona del equipo IDIEM.

Pieza institucional (como los saludos): no traza a knowledge_id; los datos del
reconocimiento vienen de la fuente pública indicada en el JSON de entrada.
Diagramación: panel gris oscuro a la izquierda con el mensaje, retrato a la derecha,
anillo de marca tenue en la esquina inferior izquierda y eslogan abajo. Montserrat incrustada (Google Fonts no
carga en el entorno de render).

Uso:
  python3 design_system/gen_post_reconocimiento.py config/especiales/<pieza>.json > pieza.html
  (rasterizar con render_bundle.cjs → recorta .export 1080x1080)
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from brand_assets import LOGO, RING, SLOGAN  # noqa: E402

from brand_fonts import FONT_CSS  # noqa: E402  (Montserrat 400-800 incrustada)

CSS = r"""
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#0a0c0d}
body{font-family:"Montserrat",system-ui,sans-serif}
:root{--red:#e1261d;--gray-dark:#2f3030}
.export{width:1080px;height:1080px;overflow:hidden;position:relative;background:var(--gray-dark);color:#fff}
.photo{position:absolute;right:0;top:0;width:540px;height:1080px;background-size:cover}
.fade{position:absolute;right:0;top:0;width:540px;height:1080px;
  background:linear-gradient(90deg,rgba(47,48,48,1) 0%,rgba(47,48,48,0) 22%),
             linear-gradient(0deg,rgba(47,48,48,.55) 0%,rgba(47,48,48,0) 26%)}
.ring{position:absolute;left:-330px;bottom:-360px;width:760px;height:760px;opacity:.16}
.ring path{fill:var(--red)}
.logo{position:absolute;top:70px;left:72px;width:190px;height:auto}
.copy{position:absolute;left:72px;width:520px;top:236px;display:flex;flex-direction:column;gap:22px}
.kick{font-size:24px;font-weight:700;letter-spacing:.18em;text-transform:uppercase}
.rule{width:120px;height:7px;background:var(--red);border-radius:2px}
.big{white-space:nowrap;font-size:132px;font-weight:700;line-height:.9;letter-spacing:-.03em;color:#fff}
.sub{font-size:28px;font-weight:600;line-height:1.25;color:rgba(255,255,255,.9)}
.sub b{color:var(--red);font-weight:700}
.lead{font-size:38px;font-weight:700;line-height:1.12;letter-spacing:-.01em;text-wrap:balance}
.who{margin-top:14px;display:flex;flex-direction:column;gap:6px}
.name{font-size:36px;font-weight:700}
.role{font-size:26px;font-weight:400;color:rgba(255,255,255,.88)}
.lists{margin-top:6px;font-size:21px;line-height:1.45;color:rgba(255,255,255,.8)}
.lists b{color:#fff}
.src{margin-top:4px;font-size:18px;font-weight:400;color:rgba(255,255,255,.7)}
.slogan{position:absolute;left:72px;bottom:66px;width:300px;height:auto}
/* layout "espejo" (MKT 10-11-2026, seminario NCh430): retrato a la izquierda, panel a la derecha */
.espejo .photo,.espejo .fade{left:0;right:auto;width:470px}
.espejo .fade{background:linear-gradient(270deg,rgba(47,48,48,1) 0%,rgba(47,48,48,0) 22%),
             linear-gradient(0deg,rgba(47,48,48,.55) 0%,rgba(47,48,48,0) 26%)}
.espejo .ring{left:auto;right:-330px}
.espejo .logo,.espejo .slogan{left:530px}
.espejo .copy{left:530px;width:490px;top:210px;gap:20px}
.espejo .lead{font-size:32px}
.espejo .role{font-size:24px;line-height:1.3}
.espejo .src{font-size:17px}
/* bloque de fecha (opcional): cuadro rojo con día y mes + detalle a la derecha */
.date{display:flex;align-items:center;gap:22px}
.date .box{background:var(--red);border-radius:6px;padding:12px 18px 10px;text-align:center;line-height:1}
.date .d{font-size:64px;font-weight:800;letter-spacing:-.02em}
.date .m{font-size:22px;font-weight:700;letter-spacing:.16em;margin-top:4px}
.date .t{font-size:24px;font-weight:600;line-height:1.35;color:rgba(255,255,255,.92)}
"""


def render(d: dict) -> str:
    foto = (ROOT.parent / d["foto"]).read_bytes()
    uri = "data:image/jpeg;base64," + base64.b64encode(foto).decode()
    lists = "<br>".join(d["listas"])
    # `cifra_size` (opcional): baja el cuerpo de la cifra cuando el texto es largo y entraría en la foto.
    big_style = f' style="font-size:{d["cifra_size"]}"' if d.get("cifra_size") else ""
    # Sin `cifra` (vacía) no hay dato grande: todo el texto queda al mismo tamaño (pedido MKT 03-11-2026).
    big = f'<div class="big"{big_style}>{d["cifra"]}</div>' if d.get("cifra") else ""
    # `sub` (opcional): línea de contexto bajo la barra roja, antes de la cifra/bajada (p. ej. bloque de un congreso).
    sub = f'<div class="sub">{d["sub"]}</div>' if d.get("sub") else ""
    # `fecha_box` (opcional): {"dia","mes","detalle"} → cuadro rojo con la fecha del evento.
    fb = d.get("fecha_box")
    date = (f'<div class="date"><div class="box"><div class="d">{fb["dia"]}</div><div class="m">{fb["mes"]}</div></div>'
            f'<div class="t">{fb["detalle"]}</div></div>') if fb else ""
    # `layout` (opcional): "espejo" = retrato a la izquierda y panel a la derecha. Por defecto, retrato a la derecha.
    layout = " espejo" if d.get("layout") == "espejo" else ""
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{d["titulo"]}</title>
<style>{FONT_CSS}{CSS}</style></head><body><div class="export{layout}">
  <div class="photo" style="background-image:url({uri});background-position:{d.get("foto_pos", "50% 0%")}"></div>
  <div class="fade"></div>
  <svg class="ring" viewBox="0 0 850 850" aria-hidden="true"><path d="{RING}"/></svg>
  <img class="logo" src="{LOGO}" alt="idiem">
  <div class="copy">
    <div class="kick">{d["kicker"]}</div>
    <div class="rule"></div>
    {sub}
    {big}
    <div class="lead">{d["lead"]}</div>
    {date}
    <div class="who"><div class="name">{d["nombre"]}</div><div class="role">{d["cargo"]}</div></div>
    {f'<div class="lists">{lists}</div>' if lists else ""}
    <div class="src">{d["fuente_txt"]}</div>
  </div>
  <img class="slogan" src="{SLOGAN}" alt="Elige bien. Elige idiem.">
</div></body></html>"""


if __name__ == "__main__":
    sys.stdout.write(render(json.loads(Path(sys.argv[1]).read_text("utf-8"))))
