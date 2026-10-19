"""Montserrat oficial incrustada (data URIs) para TODA pieza renderizada.

Google Fonts no carga en el entorno de render: con un <link> el navegador cae en una
fuente de reemplazo (hallazgo 14-10-2026). Desde diciembre 2026 (decisión MKT 19-10-2026)
las piezas nuevas se generan con estos archivos: pesos 400-800, subconjunto latin
(incluye tildes, ñ, ¿ ¡). Origen: @fontsource/montserrat 5.0.8 · licencia SIL OFL 1.1
(assets/fonts/OFL.txt).
"""
from __future__ import annotations

import base64
import re
from pathlib import Path

FONTS = Path(__file__).resolve().parent / "assets" / "fonts"
WEIGHTS = (400, 500, 600, 700, 800)


def _face(weight: int) -> str:
    b = base64.b64encode((FONTS / f"montserrat-{weight}.woff2").read_bytes()).decode()
    return (f'@font-face{{font-family:"Montserrat";font-weight:{weight};font-style:normal;'
            f'font-display:block;src:url(data:font/woff2;base64,{b}) format("woff2")}}')


FONT_CSS = "".join(_face(w) for w in WEIGHTS)
# Para plantillas que pasan por str.format (llaves escapadas).
FONT_CSS_FMT = FONT_CSS.replace("{", "{{").replace("}", "}}")

_GOOGLE = re.compile(r'<link[^>]+fonts\.(?:googleapis|gstatic)\.com[^>]*>\s*')


def embed(html: str) -> str:
    """Reemplaza los <link> de Google Fonts por Montserrat incrustada."""
    if not _GOOGLE.search(html):
        return html
    first = True

    def sub(_m):
        nonlocal first
        out, first = (f"<style>{FONT_CSS}</style>" if first else ""), False
        return out
    return _GOOGLE.sub(sub, html)
