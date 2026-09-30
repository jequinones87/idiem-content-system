"""Content coverage — ¿dónde se queda el sistema sin temas frescos?

Responde, por célula: cuántos knowledge_items quedan disponibles que NO estén en
cooldown (usados en la ventana reciente del archivo). Sirve para decidir qué célula
necesita nuevas PPT/brochures/entrevistas ANTES de planificar el próximo mes.

No inventa contenido ni relaja CONTENT_GAP: una célula restringida sin ítems técnicos
activos (p.ej. INFRA CRÍTICA TRANSPORTE) se reporta como CONTENT_GAP.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict

from .cells import CellRules
from .loader import KnowledgeBase, load_knowledge_base
from .editorial_novelty import load_diversity_config, load_history


@dataclass
class CellCoverage:
    cell: str
    total_items: int
    on_cooldown: int
    fresh: int
    status: str

    def to_dict(self) -> dict:
        return asdict(self)


def _status(fresh: int, is_gap: bool, cfg: dict) -> str:
    if is_gap:
        return "CONTENT_GAP"
    cov = cfg.get("coverage", {"low_max": 4, "medium_max": 15})
    if fresh <= 0:
        return "CONTENT_GAP"
    if fresh <= cov["low_max"]:
        return "LOW"
    if fresh <= cov["medium_max"]:
        return "MEDIUM"
    return "OK"


def coverage(kb: KnowledgeBase, month: str | None = None,
             config: dict | None = None) -> list[CellCoverage]:
    """Cobertura editorial por célula para el mes que se va a planificar."""
    cfg = config or load_diversity_config()
    rules = CellRules(kb)
    window = cfg["cooldown"]["knowledge_id_months"]
    recent_kids: set[str] = set()
    if month:
        recent_kids = {h.get("knowledge_id") for h in load_history(month, window) if h.get("knowledge_id")}

    out: list[CellCoverage] = []
    for cell in rules.known_cells():
        items = kb.items_in_cell(cell)
        kids = {it.knowledge_id for it in items}
        on_cd = len(kids & recent_kids)
        fresh = len(kids - recent_kids)
        is_gap = rules.technical_gap(cell).is_gap
        out.append(CellCoverage(cell=cell, total_items=len(items),
                                on_cooldown=on_cd, fresh=fresh,
                                status=_status(fresh, is_gap, cfg)))
    return out


def coverage_report(kb: KnowledgeBase | None = None, month: str | None = None) -> str:
    kb = kb or load_knowledge_base()
    rows = coverage(kb, month)
    header = "Reporte de cobertura editorial" + (f" — planificando {month}" if month else "")
    L = [header, "", f"{'CÉLULA':34} {'ITEMS':>6} {'COOLDOWN':>9} {'FRESH':>6}  STATUS", "-" * 72]
    for r in sorted(rows, key=lambda x: x.fresh):
        L.append(f"{r.cell:34} {r.total_items:6d} {r.on_cooldown:9d} {r.fresh:6d}  {r.status}")
    L.append("")
    L.append("STATUS: OK (>medium_max) · MEDIUM · LOW (<=low_max) · CONTENT_GAP (0 o célula restringida).")
    return "\n".join(L)


def _cli() -> int:  # pragma: no cover
    import argparse

    ap = argparse.ArgumentParser(description="Reporte de cobertura editorial por célula.")
    ap.add_argument("--month", default=None, help="Mes a planificar (YYYY-MM); aplica cooldown reciente.")
    args = ap.parse_args()
    print(coverage_report(month=args.month))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_cli())
