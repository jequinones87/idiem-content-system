"""Performance scaffold — andamiaje para asociar métricas a ``content_id``.

Estructura PREPARADA para un futuro feedback loop (LinkedIn/Metricool). Hoy solo:
schema + loader + validación. La performance NUNCA es fuente factual y NO altera
automáticamente el sistema editorial; su uso futuro será señal de PRIORIZACIÓN, no
de contenido. Ver docs/11_EDITORIAL_DIVERSITY.md.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Optional

from .loader import REPO_ROOT

PERFORMANCE_FILE = REPO_ROOT / "content" / "performance.csv"

_INT_FIELDS = ("impressions", "engagements", "clicks", "comments", "shares", "leads")


@dataclass
class PerformanceRow:
    content_id: str
    date: str = ""
    cell: str = ""
    service: str = ""
    subtheme: str = ""
    archetype: str = ""
    hook_type: str = ""
    cta_type: str = ""
    format: str = ""
    impressions: int = 0
    engagements: int = 0
    clicks: int = 0
    comments: int = 0
    shares: int = 0
    leads: int = 0


PERFORMANCE_FIELDS = tuple(f.name for f in fields(PerformanceRow))


def _to_int(v: str) -> int:
    v = (v or "").strip()
    return int(v) if v.lstrip("-").isdigit() else 0


def load_performance(path: Path | None = None) -> list[PerformanceRow]:
    """Lee content/performance.csv (vacío salvo header por ahora)."""
    p = path or PERFORMANCE_FILE
    if not p.exists():
        return []
    rows: list[PerformanceRow] = []
    with p.open("r", encoding="utf-8", newline="") as fh:
        for rec in csv.DictReader(fh):
            data = {k: rec.get(k, "") for k in PERFORMANCE_FIELDS}
            for k in _INT_FIELDS:
                data[k] = _to_int(data[k])
            if data["content_id"]:
                rows.append(PerformanceRow(**data))
    return rows


def performance_by_content_id(rows: list[PerformanceRow] | None = None) -> dict[str, PerformanceRow]:
    rows = rows if rows is not None else load_performance()
    return {r.content_id: r for r in rows}
