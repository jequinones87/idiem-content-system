"""Carrusel — láminas adicionales para los posts de formato CAROUSEL.

Un carrusel = lámina 1 (la gráfica Servicios, idéntica a la del grid) + láminas
intermedias (ícono + palabra clave roja + texto) + lámina de cierre (CTA).
Todo el contenido traza al copy ya validado del post (sin claims nuevos).

Se renderiza a PNG 1080x1080 por lámina; el PDF del post junta todas las láminas.
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


# Láminas intermedias + cierre por post (la lámina 1 es la gráfica Servicios).
SLIDES = {
    2: [
        {"tipo": "int", "icon": "magnifier", "kw": "Fallas",
         "title": "Peritajes de fallas estructurales y mecánicas",
         "body": "Determinamos qué ocurrió y por qué, con método técnico."},
        {"tipo": "int", "icon": "shield", "kw": "Incendios",
         "title": "Peritajes de incendios en la operación minera",
         "body": "Reconstrucción técnica del evento sobre evidencia física."},
        {"tipo": "int", "icon": "location", "kw": "Brechas",
         "title": "Identificamos, cuantificamos y evaluamos condiciones subestándar",
         "body": "Conforme a estándares de seguridad y control de fatalidad."},
        {"tipo": "cierre", "line": "Evidencia técnica que explica lo ocurrido<br>y sustenta decisiones.",
         "cta": "Conversemos en idiem.cl"},
    ],
    8: [
        {"tipo": "int", "icon": "magnifier", "kw": "END",
         "title": "Ensayos no destructivos de las uniones soldadas",
         "body": "Verifican especificaciones y detectan defectos."},
        {"tipo": "int", "icon": "shield", "kw": "Mecánicos",
         "title": "Ensayos mecánicos de las uniones",
         "body": "Evalúan las propiedades de la unión soldada HDPE."},
        {"tipo": "int", "icon": "location", "kw": "Respaldo",
         "title": "Asesoría experta en la documentación técnica",
         "body": "Asociada a la fabricación de las uniones."},
        {"tipo": "cierre", "line": "Control técnico que respalda la<br>confiabilidad de las líneas HDPE.",
         "cta": "Conversemos en idiem.cl"},
    ],
}


def intermediate_html(sl: dict, n: int, total: int, logo: str) -> str:
    icon = _icon(sl["icon"])
    return f'''<div class="canvas cslide int" data-finish="carousel">
  <div class="csfield"></div>
  <img class="logo" src="{logo}" alt="Logo IDIEM">
  <div class="cbody">
    <img class="cicon" src="{icon}" alt="">
    <div class="ckw">{sl["kw"]}</div>
    <div class="ctitle">{sl["title"]}</div>
    <div class="ctext">{sl["body"]}</div>
  </div>
  <div class="cfoot"><span class="csite">idiem.cl</span><span class="cnum">{n} / {total}</span></div>
</div>'''


def cierre_html(sl: dict, n: int, total: int, logo: str, slogan: str) -> str:
    return f'''<div class="canvas cslide cierre" data-finish="carousel">
  <div class="csfield red"></div>
  <img class="slogan" src="{slogan}" alt="Elige bien. Elige idiem.">
  <img class="logo" src="{logo}" alt="Logo IDIEM">
  <div class="cbody center">
    <div class="cline">{sl["line"]}</div>
    <div class="ccta">{sl["cta"]}</div>
  </div>
  <div class="cfoot"><span class="csite">idiem.cl</span><span class="cnum">{n} / {total}</span></div>
</div>'''


# CSS de las láminas de carrusel (se inyecta junto al CSS de canvas Servicios).
CAROUSEL_CSS = r'''
.cslide{color:#fff}
.csfield{position:absolute;inset:0;z-index:0;
  background:radial-gradient(120% 120% at 80% 8%, #34393b 0%, #23292b 58%, #191d1f 100%)}
.csfield.red{background:radial-gradient(120% 130% at 50% 0%, #e1261d 0%, #c11f18 60%, #a51a14 100%)}
.cslide .logo{position:absolute;z-index:3;top:5cqw;right:5.4cqw;width:19cqw;height:auto;filter:drop-shadow(0 1px 10px rgba(0,0,0,.4))}
.cslide .slogan{position:absolute;z-index:3;top:5.4cqw;left:5.4cqw;width:33cqw;height:auto;filter:drop-shadow(0 1px 10px rgba(0,0,0,.35))}
.cbody{position:absolute;z-index:2;left:8cqw;right:8cqw;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:3cqw}
.cbody.center{align-items:center;text-align:center;gap:4cqw}
.cicon{width:15cqw;height:15cqw;object-fit:contain;margin-bottom:1cqw}
.ckw{display:inline-block;align-self:flex-start;font-size:3.4cqw;font-weight:800;letter-spacing:.02em;color:#ff5a4f;text-transform:uppercase}
.ctitle{font-size:6.4cqw;font-weight:800;line-height:1.08;letter-spacing:-.01em;max-width:80cqw;text-wrap:balance}
.ctext{font-size:3.5cqw;font-weight:500;line-height:1.3;color:rgba(255,255,255,.9);max-width:74cqw}
.cline{font-size:7cqw;font-weight:800;line-height:1.12;letter-spacing:-.01em;max-width:82cqw;text-wrap:balance}
.ccta{font-size:3.8cqw;font-weight:700;background:rgba(0,0,0,.16);border:2px solid rgba(255,255,255,.55);border-radius:100px;padding:2cqw 5cqw}
.cfoot{position:absolute;z-index:3;left:5.4cqw;right:5.4cqw;bottom:5cqw;display:flex;justify-content:space-between;align-items:center;font-size:2.6cqw;font-weight:700;color:rgba(255,255,255,.92)}
.cnum{opacity:.8}
'''
