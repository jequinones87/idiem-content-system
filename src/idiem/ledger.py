"""Published-content ledger — the monthly memory.

Records which knowledge_ids were used each month so the planner can rotate
content: an item that was published recently is put on cooldown and excluded
from the next months' proposals. The ledger lives in ``state/`` (versioned,
auditable) and is never under ``data/``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .loader import REPO_ROOT

STATE_DIR = REPO_ROOT / "state"
LEDGER_FILE = STATE_DIR / "published_ledger.json"
DEFAULT_COOLDOWN_MONTHS = 3


@dataclass
class Ledger:
    """month -> list of {content_id, cell, knowledge_id} actually published."""

    months: dict[str, list[dict]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"months": self.months}


def load_ledger(path: Path | None = None) -> Ledger:
    p = path or LEDGER_FILE
    if not p.exists():
        return Ledger()
    with p.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return Ledger(months=dict(data.get("months", {})))


def save_ledger(ledger: Ledger, path: Path | None = None) -> Path:
    p = path or LEDGER_FILE
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        json.dump(ledger.to_dict(), fh, ensure_ascii=False, indent=2)
    return p


def _previous_months(month: str, n: int) -> list[str]:
    """The ``n`` YYYY-MM strings immediately before ``month``."""
    year, mon = (int(x) for x in month.split("-"))
    out: list[str] = []
    for _ in range(n):
        mon -= 1
        if mon == 0:
            mon = 12
            year -= 1
        out.append(f"{year:04d}-{mon:02d}")
    return out


def recent_knowledge_ids(
    ledger: Ledger, month: str, cooldown_months: int = DEFAULT_COOLDOWN_MONTHS
) -> list[str]:
    """knowledge_ids used in the ``cooldown_months`` months before ``month``.

    These are excluded from ``month``'s plan so content rotates instead of
    repeating. When the library is exhausted the planner falls back to a
    CONTENT_GAP rather than reusing on cooldown.
    """
    recent: list[str] = []
    for m in _previous_months(month, cooldown_months):
        for entry in ledger.months.get(m, []):
            kid = entry.get("knowledge_id")
            if kid:
                recent.append(kid)
    return recent


def record_month(ledger: Ledger, month: str, posts: list[dict]) -> Ledger:
    """Record a month's published posts (idempotent per month)."""
    ledger.months[month] = [
        {
            "content_id": p.get("content_id"),
            "cell": p.get("cell"),
            "knowledge_id": p.get("knowledge_id"),
        }
        for p in posts
    ]
    return ledger
