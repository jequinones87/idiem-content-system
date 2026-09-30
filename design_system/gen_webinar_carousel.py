"""Emit the webinar carousel slides (post tipo carrusel) as 1080x1080 `.export`
cards ready for render_bundle.cjs. Reuses the banner + tokens from
gen_webinar_card.py so the whole serie comparte el mismo banner y estilo.

Slides:
  car1  portada  — banner + "Webinar:" + tema + fecha (invita a deslizar)
  car2  contexto — por qué es relevante (escenario NCh203 / cadena global)
  car3  temario  — qué abordaremos (5 puntos del brief)
  car4  cierre   — relator + fecha + CTA de inscripción

Uso:
  PYTHONPATH=src python3 design_system/gen_webinar_carousel.py \
      config/webinar/acero_estructural_brief.json car2 > slide.html
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "design_system"))

from gen_webinar_card import (  # noqa: E402
    AST, CSS, ESLOGAN, FIT_JS, IC_CAL, IC_CLK, LOGO, FOTO_POS,
    RELATOR_PHOTO, build_webinar_plan, fecha_txt, load_brief, uri,
)

CONTENT_CSS = r"""
.cs{container-type:inline-size;position:relative;width:1080px;height:1080px;overflow:hidden;
  background:radial-gradient(120% 120% at 80% 8%, #34393b 0%, #262b2d 55%, #191d1f 100%);
  color:#fff;isolation:isolate;font-family:"Montserrat",system-ui,sans-serif;user-select:none}
.cs .eslogan{position:absolute;z-index:3;top:6cqw;left:6cqw;width:29cqw;height:auto}
.cs .logo{position:absolute;z-index:3;top:6.4cqw;right:6cqw;width:18cqw;height:auto;display:block}
.cs-body-wrap{position:absolute;inset:0;z-index:2;display:flex;flex-direction:column;justify-content:center;
  padding:20cqw 8cqw 12cqw}
.cs-body-wrap.top{justify-content:flex-start;padding:13cqw 8cqw 10cqw}
.cs-kicker{display:inline-block;align-self:flex-start;background:var(--red);color:#fff;font-weight:800;
  font-size:3.1cqw;letter-spacing:.02em;padding:1.1cqw 2.6cqw;border-radius:.5cqw;margin-bottom:4cqw}
.cs-title{font-weight:800;font-size:6.2cqw;line-height:1.08;letter-spacing:-.015em;max-width:84cqw;
  text-wrap:balance;margin-bottom:5cqw}
.cs-body-wrap.top .cs-title{margin-bottom:4cqw}
.cs-lead{font-size:3.5cqw;font-weight:500;line-height:1.42;color:rgba(255,255,255,.9);max-width:80cqw}
.cs-list{display:flex;flex-direction:column;gap:2.6cqw;margin-top:1cqw}
.cs-item{display:flex;gap:2.8cqw;align-items:flex-start}
.cs-num{flex:none;width:6cqw;height:6cqw;border-radius:50%;background:var(--red);color:#fff;
  font-weight:800;font-size:3cqw;display:flex;align-items:center;justify-content:center;margin-top:.2cqw}
.cs-itext{font-size:2.95cqw;font-weight:500;line-height:1.3;color:rgba(255,255,255,.94);max-width:76cqw}
.cs-foot{position:absolute;z-index:3;left:8cqw;bottom:7cqw;font-size:2.9cqw;font-weight:700;color:#fff;
  display:flex;align-items:center;gap:2cqw}
.cs-foot .rule{width:9cqw;height:.55cqw;background:var(--red);border-radius:2px}

/* portada / cierre reusan .wcard del banner; extras: */
.ppanel{flex-direction:column;align-items:flex-start;justify-content:center;gap:3cqw;padding:0 6cqw}
.pp-lead{font-size:4.9cqw;font-weight:800;line-height:1.08;letter-spacing:-.01em;color:#fff;max-width:86cqw}
.pp-red{color:var(--red)}
.pp-date{font-size:3.2cqw;font-weight:600;color:rgba(255,255,255,.9)}
.pp-swipe{align-self:flex-end;font-size:3cqw;font-weight:800;color:var(--red);letter-spacing:.02em}
.cierre-cta{flex:none;width:38cqw;display:flex;flex-direction:column;align-items:center;gap:2.6cqw}
.cta-pill{white-space:nowrap;background:var(--red);color:#fff;font-weight:800;font-size:3.5cqw;padding:2cqw 5cqw;border-radius:100px}
.cta-note{font-size:2.7cqw;font-weight:600;color:rgba(255,255,255,.86);text-align:center;line-height:1.35}
"""

RELEVANCIA = (
    "El abastecimiento de acero y la fabricación de estructuras hoy involucran "
    "cadenas de suministro globales, nuevos modelos de contratación y múltiples "
    "actores responsables del cumplimiento normativo. Asegurar la conformidad con "
    "la NCh203 va mucho más allá de contar con certificados de materiales.")


def _head(title: str, extra: str = "") -> str:
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{title}</title>'
            '<link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:ital,'
            'wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap">'
            f'<style>{CSS}{CONTENT_CSS}{extra}</style></head><body>')


def _wrap(inner: str, title: str) -> str:
    return _head(title) + f'<div class="export">{inner}</div><script>{FIT_JS}</script></body></html>'


def _banner(foto: str, pill: str, titulo: str) -> str:
    photo_uri = uri(AST / foto, "image/jpeg") if foto else ""
    pos = FOTO_POS.get(foto, "50% 50%")
    style = f'background-image:url({photo_uri});background-position:{pos}' if photo_uri else 'background:#4a4d4e'
    return (f'<div class="photo" style="{style}"></div><div class="photo-grad"></div>'
            f'<img class="eslogan" src="{ESLOGAN}" alt="Elige bien. Elige idiem.">'
            f'<img class="logo" src="{LOGO}" alt="idiem">'
            f'<div class="banner-copy"><span class="wpill">{pill}</span>'
            f'<div class="wtitle fit" data-max="6.2" data-min="3.8">{titulo}</div></div>')


def portada(s: dict) -> str:
    dia, fecha = fecha_txt(s["fecha"])
    hora = (s["hora"] or "").strip()
    inner = (f'<div class="wcard">{_banner(s.get("foto_tema", ""), "Webinar:", s["titulo"])}'
             f'<div class="panel ppanel">'
             f'<div class="pp-lead"><span class="pp-red">NCh203:</span> cómo asegurar la calidad del acero cuando la cadena de suministro es global</div>'
             f'<div class="pp-date">🗓️ {dia} {fecha} · {hora} hrs · Online</div>'
             f'<div class="pp-swipe">Desliza →</div>'
             f'</div></div>')
    return _wrap(inner, "Webinar · portada")


def content(kicker: str, title: str, body_html: str, align: str = "center",
            show_foot: bool = True) -> str:
    top = " top" if align == "top" else ""
    foot = ('<div class="cs-foot"><span class="rule"></span>idiem.cl</div>'
            if show_foot else "")
    inner = (f'<div class="cs">'
             f'<img class="eslogan" src="{ESLOGAN}" alt="Elige bien. Elige idiem.">'
             f'<img class="logo" src="{LOGO}" alt="idiem">'
             f'<div class="cs-body-wrap{top}"><span class="cs-kicker">{kicker}</span>'
             f'<div class="cs-title fit" data-max="6.2" data-min="3.6">{title}</div>'
             f'{body_html}</div>'
             f'{foot}</div>')
    return _wrap(inner, "Webinar · slide")


def temario_list(puntos: list[str]) -> str:
    items = "".join(
        f'<div class="cs-item"><div class="cs-num">{i}</div>'
        f'<div class="cs-itext">{p}</div></div>'
        for i, p in enumerate(puntos, 1))
    return f'<div class="cs-list">{items}</div>'


def cierre(s: dict) -> str:
    dia, fecha = fecha_txt(s["fecha"])
    hora = (s["hora"] or "").strip()
    nombre = s["relator_nombre"] or ""
    cargo = s["relator_cargo"] or ""
    cred = s.get("relator_credenciales") or ""
    rid = s["relator_id"]
    media = (f'<img src="{uri(RELATOR_PHOTO[rid], "image/jpeg")}" alt="{nombre}">'
             if rid in RELATOR_PHOTO else f'<div class="avatar">{nombre[:1]}</div>')
    inner = (f'<div class="wcard">{_banner(s.get("foto_tema", ""), "Inscripción abierta", s["titulo"])}'
             f'<div class="panel">'
             f'<div class="relator-block">'
             f'<div class="disc">{media}</div>'
             f'<div class="cred"><div class="cname">{nombre}</div>'
             f'<div class="cline">{cred}</div><div class="cline">{cargo}</div></div>'
             f'</div>'
             f'<div class="cierre-cta">'
             f'<div class="cta-pill">📩 Inscríbete</div>'
             f'<div class="cta-note">{dia} {fecha}<br>{hora} hrs<br>Link en la descripción</div>'
             f'</div>'
             f'</div></div>')
    return _wrap(inner, "Webinar · cierre")


def main() -> None:
    brief_path = sys.argv[1]
    slide = sys.argv[2] if len(sys.argv) > 2 else "car1"
    plan = build_webinar_plan(load_brief(brief_path))
    s = plan["sesiones"][0]
    if slide == "car1":
        out = portada(s)
    elif slide == "car2":
        out = content("El escenario cambió",
                      "La calidad del acero ya no se resuelve solo con un certificado.",
                      f'<div class="cs-lead">{RELEVANCIA}</div>')
    elif slide == "car3":
        out = content("En el webinar", "Qué abordaremos", temario_list(s.get("temario", [])),
                      align="top", show_foot=False)
    elif slide == "car4":
        out = cierre(s)
    else:
        raise SystemExit(f"slide desconocido: {slide}")
    sys.stdout.write(out)


if __name__ == "__main__":
    main()
