"""Recalcula huellas e índices de un archivo mensual ya congelado.

No toca copies, fotos ni estados: solo vuelve a derivar ``editorial_fingerprint``,
``dedup_index`` y ``fingerprint_index`` (p.ej. tras ajustar ``heuristic_taxonomy_map``
en ``config/editorial_diversity.json``). Respeta la ``assignment`` de cada pieza.

  PYTHONPATH=src python3 design_system/archive_refresh.py --month 2026-10
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from idiem.archive import build_month_archive, to_markdown  # noqa: E402

_DERIVED = {"month", "generated_at", "published", "count", "dedup_index", "fingerprint_index", "posts"}


def refresh(path: Path) -> dict:
    old = json.loads(path.read_text(encoding="utf-8"))
    extra = {k: v for k, v in old.items() if k not in _DERIVED}
    return build_month_archive(old["month"], old["posts"], published=old["published"], extra=extra)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", action="append", required=True)
    ap.add_argument("--dir", default=str(REPO / "content" / "archive"))
    args = ap.parse_args()
    for m in args.month:
        path = Path(args.dir) / f"{m}.json"
        a = refresh(path)
        path.write_text(json.dumps(a, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        path.with_suffix(".md").write_text(to_markdown(a), encoding="utf-8")
        print(f"refresh: {path} ({a['count']} piezas)")
