"""Banner 16:9 (1920x1080) del webinar para el evento de LinkedIn.

Mismos datos y recursos que el post 1 de la serie (gen_webinar_card.py, variante
"inv"): imagen fija de la serie + "Webinar:" + tema, relator con foto circular y
credenciales, y tarjeta roja con día/fecha/hora. Data-driven desde el brief.

Diagramación pensada para la portada de evento: foto a la izquierda con el título,
panel gris a la derecha con relator y fecha; todo el texto dentro de un margen de
seguridad (LinkedIn puede recortar los bordes en algunas vistas).

Uso:
  PYTHONPATH=src python3 design_system/gen_webinar_event_banner.py \
      config/webinar/acero_estructural_brief.json > banner.html
  (rasterizar con render_bundle.cjs → recorta el elemento .export de 1920x1080)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "design_system"))

import base64  # noqa: E402

from gen_webinar_card import (  # noqa: E402
    AST, ESLOGAN, FOTO_POS, IC_CAL, IC_CLK, LOGO, RELATOR_PHOTO,
    build_webinar_plan, fecha_txt, load_brief, uri,
)

# Montserrat oficial incrustada (Google Fonts no carga en el entorno de render: sin esto
# el navegador usa una fuente de reemplazo). Archivos de la skill video-carrusel-idiem.
from brand_fonts import FONT_CSS  # noqa: E402  (Montserrat 400-800 incrustada)

CSS = r"""
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#0a0c0d}
body{font-family:"Montserrat",system-ui,sans-serif}
:root{--red:#e1261d;--gray-dark:#2f3030}
.export{width:1920px;height:1080px;overflow:hidden;position:relative;background:var(--gray-dark);color:#fff}
.photo{position:absolute;left:0;top:0;width:1180px;height:1080px;background-size:cover}
.grad{position:absolute;left:0;top:0;width:1180px;height:1080px;
  background:linear-gradient(0deg,rgba(0,0,0,.86) 0%,rgba(0,0,0,.18) 48%,rgba(0,0,0,.42) 100%),
             linear-gradient(90deg,rgba(0,0,0,0) 70%,rgba(47,48,48,.9) 100%)}
.eslogan{position:absolute;top:84px;left:96px;width:430px;height:auto;filter:drop-shadow(0 1px 8px rgba(0,0,0,.5))}
.copy{position:absolute;left:96px;right:860px;bottom:120px;display:flex;flex-direction:column;align-items:flex-start;gap:30px}
.pill{background:var(--red);color:#fff;font-weight:700;font-size:58px;padding:14px 34px;border-radius:7px}
.title{font-weight:700;font-size:76px;line-height:1.05;letter-spacing:-.012em;text-shadow:0 2px 18px rgba(0,0,0,.55)}
.online{font-size:30px;font-weight:700;color:rgba(255,255,255,.9)}
.panel{position:absolute;left:1180px;top:0;width:740px;height:1080px;background:var(--gray-dark);
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:44px;padding:270px 80px 50px}
.logo{position:absolute;top:84px;right:96px;width:230px;height:auto}
.rel{display:flex;flex-direction:column;align-items:center;text-align:center;gap:22px}
.disc{width:270px;height:270px;border-radius:50%;background:#fff;padding:9px;box-shadow:0 10px 30px -12px rgba(0,0,0,.55)}
.disc img{width:100%;height:100%;object-fit:cover;object-position:50% 22%;border-radius:50%;display:block}
.cname{font-size:42px;font-weight:700}
.cline{font-size:24px;font-weight:400;color:rgba(255,255,255,.86);line-height:1.35}
.datecard{background:var(--red);border-radius:22px;padding:30px 44px;display:flex;flex-direction:column;gap:20px;min-width:440px}
.drow{display:flex;align-items:center;gap:22px}
.drow img{width:50px;height:50px}
.drow span{font-size:32px;font-weight:700;line-height:1.15;white-space:nowrap}
.hr{height:1px;background:rgba(255,255,255,.45)}
"""


def banner(s: dict) -> str:
    dia, fecha = fecha_txt(s["fecha"])
    hora = (s["hora"] or "").strip()
    foto = s.get("foto_tema") or ""
    pos = FOTO_POS.get(foto, "50% 50%")
    nombre = s["relator_nombre"] or ""
    cargo = s["relator_cargo"] or ""
    cred = s.get("relator_credenciales") or ""
    media = (f'<img src="{uri(RELATOR_PHOTO[s["relator_id"]], "image/jpeg")}" alt="{nombre}">'
             if s["relator_id"] in RELATOR_PHOTO else "")
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Banner evento webinar</title>
<style>{FONT_CSS}{CSS}</style></head><body><div class="export">
  <div class="photo" style="background-image:url({uri(AST / foto, 'image/jpeg')});background-position:{pos}"></div>
  <div class="grad"></div>
  <img class="eslogan" src="{ESLOGAN}" alt="Elige bien. Elige idiem.">
  <div class="copy">
    <span class="pill">Webinar:</span>
    <div class="title">{s["titulo"]}</div>
    <div class="online">Online</div>
  </div>
  <div class="panel">
    <img class="logo" src="{LOGO}" alt="idiem">
    <div class="rel">
      <div class="disc">{media}</div>
      <div class="cname">{nombre}</div>
      <div><div class="cline">{cred}</div><div class="cline">{cargo}</div></div>
    </div>
    <div class="datecard">
      <div class="drow"><img src="{IC_CAL}" alt=""><span>{dia}<br>{fecha}</span></div>
      <div class="hr"></div>
      <div class="drow"><img src="{IC_CLK}" alt=""><span>{hora} hrs.</span></div>
    </div>
  </div>
</div></body></html>"""


if __name__ == "__main__":
    plan = build_webinar_plan(load_brief(sys.argv[1]))
    sys.stdout.write(banner(plan["sesiones"][0]))
