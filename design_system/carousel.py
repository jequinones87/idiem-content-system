"""Carrusel — láminas con FOTO DE FONDO (diseño Plantilla 02), no campo plano.

Estructura acordada (static/carrusel/webinar):
  - Portada  : foto de fondo + kicker + gancho (una palabra en rojo) + eslogan + logo.
  - Intermedias (01/02/03): MISMA foto oscurecida + número rojo + ícono + título con
    palabra resaltada (caja roja) + bajada.
  - Cierre   : campo gris de marca + eslogan + bajada + logo + idiem.cl.

Sin siglas de célula en la pieza (manejo interno). Todo el contenido traza al copy
validado del post.
"""
from __future__ import annotations

import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

CAROUSEL_POSTS = {2, 8}


def _icon(name: str) -> str:
    b = (ASSETS / f"icon_{name}.png").read_bytes()
    return f"data:image/png;base64,{base64.b64encode(b).decode()}"


# Contenido por post. `title` admite <span class="c2rb">palabra</span> (caja roja);
# la portada usa <span class="c2rt">palabra</span> (texto rojo).
SLIDES = {
    2: {
        "portada": {"kicker": "PERITAJES · OPERACIÓN MINERA",
                    "title": 'Entender qué <span class="c2rt">ocurrió</span>.'},
        "intermedias": [
            {"icon": "location", "title": 'Peritaje de <span class="c2rb">incendios</span>',
             "body": "Reconstrucción técnica del evento en la operación minera."},
            {"icon": "magnifier", "title": 'Fallas <span class="c2rb">estructurales</span>',
             "body": "Peritajes de fallas estructurales y mecánicas: determinamos qué ocurrió y por qué."},
            {"icon": "shield", "title": 'Brechas y <span class="c2rb">estándares</span>',
             "body": "Identificamos, cuantificamos y evaluamos condiciones subestándar según control de fatalidad."},
        ],
        "cierre": {"bajada": "Evidencia técnica que explica lo ocurrido y sustenta decisiones."},
    },
    8: {
        "portada": {"kicker": "CONTROL DE CALIDAD · HDPE",
                    "title": 'Uniones <span class="c2rt">confiables</span>.'},
        "intermedias": [
            {"icon": "magnifier", "title": 'Ensayos <span class="c2rb">no destructivos</span>',
             "body": "Verifican especificaciones y detectan defectos en la unión soldada."},
            {"icon": "location", "title": 'Ensayos <span class="c2rb">mecánicos</span>',
             "body": "Evalúan las propiedades de la unión soldada HDPE."},
            {"icon": "shield", "title": 'Respaldo <span class="c2rb">documental</span>',
             "body": "Asesoría experta en la documentación técnica de fabricación."},
        ],
        "cierre": {"bajada": "Control técnico que respalda la confiabilidad de las líneas HDPE."},
    },
}


def portada_html(photo_uri: str, sl: dict, logo: str, slogan: str) -> str:
    return f'''<div class="canvas c2slide" data-finish="carousel">
  <div class="c2photo" style="background-image:url('{photo_uri}')"></div>
  <div class="c2grad"></div>
  <img class="c2slogan" src="{slogan}" alt="Elige bien. Elige idiem.">
  <img class="c2logo" src="{logo}" alt="Logo IDIEM">
  <div class="c2eyebrow">{sl["kicker"]}</div>
  <div class="c2ptitle">{sl["title"]}</div>
</div>'''


def intermedia_html(photo_uri: str, num: str, sl: dict, logo: str) -> str:
    return f'''<div class="canvas c2slide" data-finish="carousel">
  <div class="c2photo" style="background-image:url('{photo_uri}')"></div>
  <div class="c2veil"></div>
  <img class="c2logo" src="{logo}" alt="Logo IDIEM">
  <div class="c2num">{num}</div>
  <img class="c2ic" src="{_icon(sl["icon"])}" alt="">
  <div class="c2rule"></div>
  <div class="c2mtitle">{sl["title"]}</div>
  <div class="c2mbody">{sl["body"]}</div>
</div>'''


def cierre_html(sl: dict, logo: str, slogan: str) -> str:
    return f'''<div class="canvas c2slide c2cierre" data-finish="carousel">
  <div class="c2cwrap">
    <img class="c2ceslogan" src="{slogan}" alt="Elige bien. Elige idiem.">
    <div class="c2cdiv"></div>
    <div class="c2cbajada">{sl["bajada"]}</div>
    <img class="c2clogo" src="{logo}" alt="Logo IDIEM">
    <div class="c2curl">idiem.cl</div>
  </div>
</div>'''


def build_slides(seq: int, photo_uri: str, logo: str, slogan: str) -> list[str]:
    """Portada + 3 intermedias + cierre para un post de carrusel."""
    data = SLIDES[seq]
    out = [portada_html(photo_uri, data["portada"], logo, slogan)]
    for i, sl in enumerate(data["intermedias"], start=1):
        out.append(intermedia_html(photo_uri, f"0{i}", sl, logo))
    out.append(cierre_html(data["cierre"], logo, slogan))
    return out


# CSS namespaced c2* (no choca con el canvas Servicios). Basado en Plantilla 02.
CAROUSEL_CSS = r'''
.c2slide{color:#fff;background:var(--gray-dark)}
.c2photo{position:absolute;inset:0;z-index:0;background-size:cover;background-position:50% 42%}
.c2grad{position:absolute;inset:0;z-index:1;background:linear-gradient(0deg,rgba(0,0,0,.82) 4%,rgba(0,0,0,.15) 46%,rgba(0,0,0,.38) 100%)}
.c2veil{position:absolute;inset:0;z-index:1;background:linear-gradient(180deg,rgba(20,21,22,.72),rgba(20,21,22,.86))}
.c2slogan{position:absolute;z-index:3;top:5.4cqw;left:5.6cqw;width:34cqw;height:auto;display:block;filter:drop-shadow(0 1px 10px rgba(0,0,0,.4))}
.c2logo{position:absolute;z-index:3;top:5.6cqw;right:5.6cqw;width:19cqw;height:auto;display:block;filter:drop-shadow(0 1px 10px rgba(0,0,0,.4))}
.c2eyebrow{position:absolute;z-index:3;left:5.6cqw;bottom:26cqw;font-size:2.5cqw;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:#fff;opacity:.95}
.c2ptitle{position:absolute;z-index:3;left:5.6cqw;right:8cqw;bottom:7cqw;font-size:7.6cqw;font-weight:800;line-height:1.02;letter-spacing:-.02em;text-shadow:0 2px 18px rgba(0,0,0,.5)}
.c2ptitle .c2rt{color:var(--red)}
.c2num{position:absolute;z-index:3;top:5.6cqw;left:5.6cqw;font-size:3.2cqw;font-weight:800;color:var(--red);letter-spacing:.04em}
.c2ic{position:absolute;z-index:3;top:17cqw;left:5.6cqw;width:20cqw;height:20cqw;object-fit:contain}
.c2rule{position:absolute;z-index:3;left:5.6cqw;top:40cqw;width:11cqw;height:.7cqw;background:var(--red);border-radius:2px}
.c2mtitle{position:absolute;z-index:3;left:5.6cqw;right:7cqw;top:44cqw;font-size:6.4cqw;font-weight:800;line-height:1.06;letter-spacing:-.01em}
.c2rb{display:inline;background:var(--red);color:#fff;padding:.02em .22em;border-radius:.06em;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.c2mbody{position:absolute;z-index:3;left:5.6cqw;right:9cqw;bottom:8cqw;font-size:3.5cqw;font-weight:500;line-height:1.32;color:rgba(255,255,255,.94)}
.c2cierre{background:radial-gradient(120% 120% at 78% 10%, #34393b 0%, #23292b 60%, #191d1f 100%)}
.c2cwrap{position:absolute;inset:0;z-index:3;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:12cqw 9cqw;gap:5cqw}
.c2ceslogan{width:56cqw;height:auto;display:block}
.c2cdiv{width:14cqw;height:.6cqw;background:var(--red);border-radius:2px}
.c2cbajada{font-size:3.6cqw;font-weight:500;line-height:1.34;color:rgba(255,255,255,.92);max-width:74cqw}
.c2clogo{width:30cqw;height:auto;display:block;margin-top:1cqw}
.c2curl{font-size:3cqw;font-weight:700;letter-spacing:.04em;color:#fff}
'''
