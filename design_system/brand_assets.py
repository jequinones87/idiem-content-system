"""Recursos oficiales de marca (eslogan, logo, anillo del círculo) como data URIs.

Reemplaza los archivos de bootstrap `_slogan/_logo/_ring.txt` que vivían en el
scratchpad de sesión: ahora se derivan siempre de los SVG versionados en
`design_system/assets/`, así cualquier generador puede re-emitir piezas.
"""
from __future__ import annotations

import base64
import re
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets"


def _svg_uri(name: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode((ASSETS / name).read_bytes()).decode()


def _ring_path() -> str:
    svg = (ASSETS / "circulo_geometrico.svg").read_text(encoding="utf-8")
    m = re.search(r'<path[^>]*\sd="([^"]+)"', svg, re.S)
    if not m:
        raise ValueError("circulo_geometrico.svg sin path d")
    return " ".join(m.group(1).split())


SLOGAN = _svg_uri("eslogan_idiem_3_blanco.svg")
LOGO = _svg_uri("logo_idiem_oficial.svg")
RING = _ring_path()  # path d del anillo, viewBox 0 0 850 850
