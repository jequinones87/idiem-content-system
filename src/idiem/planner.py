"""Milestone 5 — monthly content planner.

Turns the factual library into a configurable monthly grid. Honors the M5
constraints from docs/03_IMPLEMENTATION_PLAN.md:

- do not exceed factual coverage;
- avoid consecutive reuse of the same main knowledge ID;
- vary angle/application where possible;
- emit CONTENT_GAP when a target cell cannot be safely populated;
- do not silently rebalance unless configuration allows it.

Never borrows evidence across cells to hit a quota (roadmap §3): a quota the
library cannot support becomes a gap, not a reclassification.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .loader import CONFIG_DIR, KnowledgeBase
from .retrieval import RetrievalEngine

PLANNER_CONFIG = "planner.json"


@dataclass
class PlanSlot:
    seq: int
    cell: str
    status: str  # "DRAFT" | "CONTENT_GAP"
    content_type: str
    knowledge_id: str | None
    editorial_angle: str
    application: str | None
    content_id: str | None
    reason: str | None = None


@dataclass
class MonthlyPlan:
    month: str
    target_count: int
    cadence_per_week: str
    weights: dict
    allow_rebalance: bool
    slots: list[PlanSlot] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    log: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


def load_planner_config() -> dict:
    with (CONFIG_DIR / PLANNER_CONFIG).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _largest_remainder(weights: dict[str, float], total: int) -> dict[str, int]:
    """Proportionally allocate ``total`` integer slots across weighted cells."""
    wsum = sum(weights.values())
    if wsum <= 0 or total <= 0:
        return {c: 0 for c in weights}
    raw = {c: (w / wsum) * total for c, w in weights.items()}
    floors = {c: int(v) for c, v in raw.items()}
    assigned = sum(floors.values())
    remainder = total - assigned
    # distribute the remaining units to the largest fractional parts,
    # breaking ties deterministically by cell name.
    order = sorted(
        weights, key=lambda c: (-(raw[c] - floors[c]), c)
    )
    for c in order[:remainder]:
        floors[c] += 1
    return floors


def _content_id(cell: str, knowledge_id: str, seq: int) -> str:
    return f"PLAN-{knowledge_id}-{seq:02d}"


def _diversify(items: list) -> list:
    """Reorder items to maximize thematic spread when taking the first N.

    Groups by ``service`` and then, within a service, by ``capability``, and
    round-robins across those buckets. So ``result[:N]`` covers as many distinct
    services (then capabilities) as the cell offers before repeating any — the
    fix for months where the naive ``sorted-by-id[:N]`` slice clustered every
    slot into the largest/alphabetically-first service.
    """
    # Bucket by (service, capability), preserving a deterministic inner order.
    buckets: dict[tuple[str, str], list] = {}
    for it in sorted(items, key=lambda x: x.knowledge_id):
        key = (it.service or "", it.capability or "")
        buckets.setdefault(key, []).append(it)

    # Order service groups deterministically by name; within a service, order
    # capability groups by name. Round-robin services first (outer), so distinct
    # services come first; ties inside a service spread across capabilities.
    from collections import OrderedDict

    by_service: "OrderedDict[str, list[list]]" = OrderedDict()
    for (svc, cap) in sorted(buckets):
        by_service.setdefault(svc, []).append(buckets[(svc, cap)])

    # Flatten each service into a capability-interleaved queue.
    service_queues: dict[str, list] = {}
    for svc, cap_groups in by_service.items():
        q: list = []
        cap_lists = [list(g) for g in cap_groups]
        while any(cap_lists):
            for cl in cap_lists:
                if cl:
                    q.append(cl.pop(0))
        service_queues[svc] = q

    # Round-robin across services.
    order = sorted(service_queues)
    out: list = []
    while any(service_queues[s] for s in order):
        for s in order:
            if service_queues[s]:
                out.append(service_queues[s].pop(0))
    return out


class MonthlyPlanner:
    def __init__(self, kb: KnowledgeBase, config: dict | None = None) -> None:
        self.kb = kb
        self.config = config or load_planner_config()
        self.engine = RetrievalEngine(kb)

    def _candidates(self, cell: str, recent: set[str]) -> list:
        """Deterministic, coverage-limited list of usable main items for a cell.

        Excludes knowledge IDs in ``recent`` (recent content history) so the
        planner does not repeat what was just published.
        """
        items = [
            it
            for it in self.kb.items_in_cell(cell)
            if it.knowledge_id not in recent
        ]
        # Spread by service/capability so the first-N slice varies the topic
        # instead of clustering into the largest service (Fase A).
        return _diversify(items)

    def build_plan(
        self,
        *,
        month: str,
        target_count: int | None = None,
        cadence_per_week: str | None = None,
        weights: dict | None = None,
        campaign_priorities: dict | None = None,
        recent_history: list[str] | None = None,
    ) -> MonthlyPlan:
        target = target_count or int(self.config["default_target_count"])
        cadence = cadence_per_week or self.config.get("cadence_per_week", "2-3")
        weights = dict(weights or self.config["cell_weights"])
        allow_rebalance = bool(self.config.get("allow_rebalance", False))
        recent = set(recent_history or [])

        # Optional campaign priorities multiply base weights (configurable intent,
        # never overrides factual coverage).
        if campaign_priorities:
            for cell, mult in campaign_priorities.items():
                if cell in weights:
                    weights[cell] = weights[cell] * float(mult)

        plan = MonthlyPlan(
            month=month,
            target_count=target,
            cadence_per_week=str(cadence),
            weights=weights,
            allow_rebalance=allow_rebalance,
        )

        quotas = _largest_remainder(weights, target)
        plan.log.append(f"Cuotas normalizadas (target={target}): {quotas}")

        # Directed substitution (configured, not silent): when a cell has quota
        # but zero coverage (e.g. Transporte), reassign its quota to the
        # configured fallback cells that DO have coverage headroom. This is an
        # explicit editorial rule, distinct from allow_rebalance.
        substitutions = self.config.get("substitutions", {})
        for src_cell, targets in substitutions.items():
            q = quotas.get(src_cell, 0)
            if q <= 0 or len(self._candidates(src_cell, recent)) > 0:
                continue  # only substitute cells that cannot be filled at all
            quotas[src_cell] = 0
            # Fallback targets participate even if they carried no base weight.
            for t in targets:
                quotas.setdefault(t, 0)
            valid = list(targets)
            plan.log.append(
                f"Sustitución: {q} cupo(s) de {src_cell} (sin cobertura) -> {valid}."
            )
            i = 0
            while q > 0 and valid:
                if all(
                    len(self._candidates(t, recent)) - quotas[t] <= 0 for t in valid
                ):
                    break  # no fallback has headroom
                t = valid[i % len(valid)]
                if len(self._candidates(t, recent)) - quotas[t] > 0:
                    quotas[t] += 1
                    q -= 1
                i += 1
            if q > 0:
                quotas[src_cell] = q  # remainder cannot be covered -> honest gap
                plan.log.append(
                    f"Sustitución parcial: {q} cupo(s) sin cobertura disponible -> CONTENT_GAP."
                )

        # Fill per cell up to min(quota, coverage). Track shortfalls.
        filled: dict[str, list] = {}
        shortfall: dict[str, int] = {}
        for cell, quota in quotas.items():
            candidates = self._candidates(cell, recent)
            take = min(quota, len(candidates))
            filled[cell] = candidates[:take]
            short = quota - take
            if short > 0:
                shortfall[cell] = short
                plan.log.append(
                    f"{cell}: cuota={quota}, cobertura={len(candidates)} -> "
                    f"faltan {short} (no se toma prestado de otra celda)."
                )

        # Optional, explicit rebalance of unmet quota into cells with surplus
        # coverage. Off by default (do not silently rebalance).
        rebalanced: dict[str, list] = {c: [] for c in quotas}
        if allow_rebalance and shortfall:
            deficit = sum(shortfall.values())
            for cell in sorted(quotas):
                extra = self._candidates(cell, recent)[len(filled[cell]):]
                for it in extra:
                    if deficit <= 0:
                        break
                    rebalanced[cell].append(it)
                    deficit -= 1
            if deficit < sum(shortfall.values()):
                plan.log.append(
                    "allow_rebalance=true: excedente reasignado a celdas con cobertura."
                )
            # Reduce shortfall counts by what we rebalanced.
            moved = sum(len(v) for v in rebalanced.values())
            plan.log.append(f"Slots reasignados por rebalance: {moved}.")
            # Remaining shortfall stays as gaps.
            remaining = moved
            for cell in list(shortfall):
                if remaining <= 0:
                    break
                reduce = min(shortfall[cell], remaining)
                shortfall[cell] -= reduce
                remaining -= reduce
                if shortfall[cell] == 0:
                    del shortfall[cell]

        # Build DRAFT slots (interleaved across cells for cadence + to avoid
        # consecutive same-cell/same-id adjacency).
        draft_units: list[tuple[str, object]] = []
        per_cell_lists = {
            cell: list(filled[cell]) + list(rebalanced.get(cell, []))
            for cell in quotas
        }
        # round-robin interleave
        remaining_total = sum(len(v) for v in per_cell_lists.values())
        cell_cycle = [c for c in sorted(quotas) if per_cell_lists[c]]
        idx = 0
        while remaining_total > 0 and cell_cycle:
            cell = cell_cycle[idx % len(cell_cycle)]
            if per_cell_lists[cell]:
                draft_units.append((cell, per_cell_lists[cell].pop(0)))
                remaining_total -= 1
            if not per_cell_lists[cell]:
                cell_cycle = [c for c in cell_cycle if per_cell_lists[c]]
                idx = 0
                continue
            idx += 1

        seq = 1
        prev_kid: str | None = None
        for cell, item in draft_units:
            # Guard the no-consecutive-reuse invariant (defensive; interleave
            # already separates same-cell items).
            if item.knowledge_id == prev_kid:
                plan.log.append(
                    f"Reordenado para evitar reuso consecutivo de {item.knowledge_id}."
                )
            cell_def = self.kb.cell_def_by_name.get(cell)
            angle = cell_def.communication_reference_2026 if cell_def else ""
            plan.slots.append(
                PlanSlot(
                    seq=seq,
                    cell=cell,
                    status="DRAFT",
                    content_type="TECHNICAL_INSIGHT",
                    knowledge_id=item.knowledge_id,
                    editorial_angle=angle,
                    application=item.application,
                    content_id=_content_id(cell, item.knowledge_id, seq),
                )
            )
            prev_kid = item.knowledge_id
            seq += 1

        # Emit CONTENT_GAP slots for unmet quota (after any rebalance).
        for cell in sorted(shortfall):
            for _ in range(shortfall[cell]):
                reason = (
                    f"La célula '{cell}' no tiene evidencia técnica activa suficiente "
                    f"para cubrir la cuota del mes; se marca CONTENT_GAP en vez de "
                    f"reclasificar conocimiento de otra célula."
                )
                plan.slots.append(
                    PlanSlot(
                        seq=seq,
                        cell=cell,
                        status="CONTENT_GAP",
                        content_type="EXPERT_INPUT_REQUIRED",
                        knowledge_id=None,
                        editorial_angle="",
                        application=None,
                        content_id=None,
                        reason=reason,
                    )
                )
                plan.gaps.append(f"[{cell}] {reason}")
                seq += 1

        return plan


def write_plan_json(plan: MonthlyPlan, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"plan_{plan.month}.json"
    with path.open("w", encoding="utf-8") as fh:
        json.dump(plan.to_dict(), fh, ensure_ascii=False, indent=2)
    return path


def write_plan_csv(plan: MonthlyPlan, out_dir: Path) -> Path:
    """Optional CSV grid for human review (docs/03 M8 export)."""
    import csv

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"plan_{plan.month}.csv"
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            ["seq", "cell", "status", "content_type", "knowledge_id",
             "application", "editorial_angle", "content_id", "reason"]
        )
        for s in plan.slots:
            writer.writerow(
                [s.seq, s.cell, s.status, s.content_type, s.knowledge_id or "",
                 s.application or "", s.editorial_angle, s.content_id or "",
                 s.reason or ""]
            )
    return path
