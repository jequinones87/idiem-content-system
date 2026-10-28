"""Carrusel extra noviembre 2026 · post B (19-nov) · Gestión del riesgo aluvional en 5 etapas.

Post adicional a la grilla (contingencia de lluvias y aluviones, oct-2026). Traza a las
fuentes SRC-008#C01–C02 (oferta integral IDIEM, validada por MKT 28-10-2026) en
config/topic_bank/expert_sources.json; en 2A.2 el servicio solo existe como reserva
(R0001/R0002), así que no hay knowledge_id. Sin proyectos con nombre (MKT 28-10-2026).

Pedido MKT: muy visual y con poco texto. Por eso las intermedias muestran la foto con
degradado inferior (no el velo completo de la Plantilla 02), ícono grande en círculo rojo,
título con caja roja, una bajada corta y un indicador de avance de 5 etapas.
Fotos: carpeta de Drive de MKT (fotos de la presentación SRC-007), recortadas a 1080.

Uso:
  python3 design_system/gen_extra_aluviones.py <carpeta_salida>
  node design_system/render_bundle.cjs <carpeta_salida>/manifest.json
"""
from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from brand_assets import LOGO, SLOGAN  # noqa: E402
from brand_fonts import FONT_CSS  # noqa: E402

ICONS = ROOT.parent / ".claude" / "skills" / "video-carrusel-idiem" / "assets" / "icons"
PHOTOS = ROOT / "assets" / "month_2026-11"

COVER = {"photo": "extra_contension2.jpg", "pos": "50% 40%",
         "kicker": "GESTIÓN DEL RIESGO ALUVIONAL",
         "title": '¿Qué quebrada <span class="rt">intervenir</span> primero?'}
STAGES = [
    {"photo": "extra_aluvion_jpg.jpg", "pos": "50% 50%", "icon": "search",
     "title": '<span class="rb">Diagnóstico</span>',
     "body": "Catastro de infraestructura y viviendas para identificar los sectores expuestos."},
    {"photo": "extra_contension3.jpg", "pos": "50% 70%", "icon": "ruler",
     "title": 'Estudios de <span class="rb">terreno</span>',
     "body": "Hidrología, geología, geomorfología, topografía, mecánica de suelos, geotecnia y geofísica."},
    {"photo": "extra_aluvion_png.jpg", "pos": "40% 55%", "icon": "activity",
     "title": '<span class="rb">Modelación</span> numérica',
     "body": "Crecidas y aluviones modelados bajo escenarios de cambio climático."},
    {"photo": "extra_aluvion_jpg.jpg", "pos": "60% 35%", "icon": "map-pin",
     "title": 'Zonificación de la <span class="rb">amenaza</span>',
     "body": "Mapas para planificar el territorio y coordinar la respuesta ante emergencias."},
    {"photo": "extra_contension2.jpg", "pos": "50% 45%", "icon": "shield-check",
     "title": 'Obras de <span class="rb">mitigación</span>',
     "body": "Alternativas, presupuestos, evaluación económica y términos de referencia."},
]
CLOSE = "Estudiar, priorizar, diseñar y validar: un socio técnico para todo el ciclo del riesgo aluvional."

CSS = r"""
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#0a0c0d}
body{font-family:"Montserrat",system-ui,sans-serif}
:root{--red:#e1261d;--gray-dark:#2f3030}
.export{width:1080px;height:1080px;overflow:hidden;position:relative;background:var(--gray-dark);color:#fff}
.ph{position:absolute;inset:0;background-size:cover}
.gcov{position:absolute;inset:0;background:linear-gradient(0deg,rgba(0,0,0,.86) 6%,rgba(0,0,0,.2) 50%,rgba(0,0,0,.42) 100%)}
.gst{position:absolute;inset:0;background:linear-gradient(0deg,rgba(18,20,21,.94) 30%,rgba(18,20,21,.45) 62%,rgba(18,20,21,.4) 84%,rgba(18,20,21,.72) 100%)}
.slogan{position:absolute;top:58px;left:60px;width:367px}
.logo{position:absolute;top:60px;right:60px;width:205px}
.kick{position:absolute;left:60px;bottom:300px;font-size:27px;font-weight:700;letter-spacing:.16em}
.ptitle{position:absolute;left:60px;right:90px;bottom:76px;font-size:88px;font-weight:800;line-height:1.02;letter-spacing:-.02em;text-shadow:0 2px 18px rgba(0,0,0,.5)}
.rt{color:var(--red)}
.num{position:absolute;top:62px;left:60px;font-size:34px;font-weight:800;color:#fff;letter-spacing:.04em;background:var(--red);padding:6px 16px;border-radius:6px}
.num small{font-size:22px;color:rgba(255,255,255,.85);font-weight:700}
.ic{position:absolute;left:60px;top:430px;width:150px;height:150px;border-radius:50%;background:var(--red);display:flex;align-items:center;justify-content:center;box-shadow:0 6px 28px rgba(0,0,0,.35)}
.ic svg{width:78px;height:78px;color:#fff;stroke-width:1.8}
.mtitle{position:absolute;left:60px;right:70px;top:620px;font-size:70px;font-weight:800;line-height:1.08;letter-spacing:-.01em}
.rb{background:var(--red);padding:.02em .2em;border-radius:.06em;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.mbody{position:absolute;left:60px;right:110px;top:800px;font-size:37px;font-weight:500;line-height:1.3;color:rgba(255,255,255,.94)}
.prog{position:absolute;left:60px;right:60px;bottom:58px;display:flex;gap:12px}
.prog i{flex:1;height:8px;border-radius:4px;background:rgba(255,255,255,.28)}
.prog i.on{background:var(--red)}
.prog i.done{background:rgba(255,255,255,.7)}
.close{background:radial-gradient(120% 120% at 78% 10%,#34393b 0%,#23292b 60%,#191d1f 100%)}
.cwrap{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:120px 100px;gap:52px}
.cslogan{width:600px}
.cdiv{width:150px;height:7px;background:var(--red);border-radius:2px}
.cbody{font-size:40px;font-weight:600;line-height:1.32;color:rgba(255,255,255,.94);max-width:820px}
.clogo{width:320px}
.curl{font-size:32px;font-weight:700;letter-spacing:.04em}
"""


def _uri(name: str) -> str:
    return "data:image/jpeg;base64," + base64.b64encode((PHOTOS / name).read_bytes()).decode()


def _icon(name: str) -> str:
    svg = (ICONS / f"{name}.svg").read_text("utf-8")
    return re.sub(r'class="[^"]*"', "", svg)


def _page(title: str, inner: str, cls: str = "") -> str:
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{title}</title>'
            f'<style>{FONT_CSS}{CSS}</style></head><body><div class="export {cls}">{inner}</div></body></html>')


def slides() -> list[str]:
    out = [_page("Portada", f'''<div class="ph" style="background-image:url({_uri(COVER["photo"])});background-position:{COVER["pos"]}"></div>
<div class="gcov"></div><img class="slogan" src="{SLOGAN}" alt="Elige bien. Elige idiem."><img class="logo" src="{LOGO}" alt="idiem">
<div class="kick">{COVER["kicker"]}</div><div class="ptitle">{COVER["title"]}</div>''')]
    n = len(STAGES)
    for i, st in enumerate(STAGES, start=1):
        prog = "".join(f'<i class="{"on" if k == i else "done" if k < i else ""}"></i>' for k in range(1, n + 1))
        out.append(_page(f"Etapa {i}", f'''<div class="ph" style="background-image:url({_uri(st["photo"])});background-position:{st["pos"]}"></div>
<div class="gst"></div><img class="logo" src="{LOGO}" alt="idiem"><div class="num">0{i} <small>/ 0{n}</small></div>
<div class="ic">{_icon(st["icon"])}</div><div class="mtitle">{st["title"]}</div><div class="mbody">{st["body"]}</div>
<div class="prog">{prog}</div>'''))
    out.append(_page("Cierre", f'''<div class="cwrap"><img class="cslogan" src="{SLOGAN}" alt="Elige bien. Elige idiem.">
<div class="cdiv"></div><div class="cbody">{CLOSE}</div><img class="clogo" src="{LOGO}" alt="idiem"><div class="curl">idiem.cl</div></div>''', "close"))
    return out


if __name__ == "__main__":
    dest = Path(sys.argv[1]).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    manifest = []
    for k, html in enumerate(slides(), start=1):
        h = dest / f"B_lamina_{k:02d}.html"
        h.write_text(html, "utf-8")
        manifest.append({"html": str(h), "png": str(dest / f"B_lamina_{k:02d}.png")})
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=1), "utf-8")
    print(f"{len(manifest)} láminas → {dest}")
