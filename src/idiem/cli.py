"""Minimal local demo CLI for the IDIEM content system.

The ``demo`` command runs the first working demo required by the handoff:
  1. retrieve technical knowledge by cell;
  2. return a CONTENT_GAP for a technical Transporte request;
  3. generate a structured fact sheet;
  4. generate one schema-valid DRAFT content brief with full traceability.

Usage:
    python -m idiem.cli integrity
    python -m idiem.cli retrieve "INFRA OPERACIÓN MINERA"
    python -m idiem.cli factsheet "LAB MINERO DIGITAL" --topic Triaxial
    python -m idiem.cli brief "INFRA PÚBLICA RESILIENTE"
    python -m idiem.cli demo
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from .brief import build_brief, write_brief
from .cells import CellRules
from .factsheet import build_fact_sheet
from .integrity import assert_integrity, run_all_checks
from .loader import REPO_ROOT, load_knowledge_base
from .retrieval import RetrievalEngine

OUTPUT_DIR = REPO_ROOT / "output"
TRANSPORTE = "INFRA CRÍTICA TRANSPORTE"


def _p(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def cmd_integrity(_args) -> int:
    kb = load_knowledge_base()
    results = run_all_checks(kb)
    for r in results:
        flag = "PASS" if r.passed else "FAIL"
        print(f"[{flag}] {r.check_id}: {r.reason}")
    failed = [r for r in results if not r.passed]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks PASS")
    return 1 if failed else 0


def cmd_retrieve(args) -> int:
    kb = load_knowledge_base()
    hits = RetrievalEngine(kb).retrieve_by_cell(args.cell)
    print(f"Célula: {args.cell} — {len(hits)} knowledge_items")
    for h in hits[: args.limit]:
        print(
            f"  {h.item.knowledge_id} | {h.policy} | {h.item.service}"
            f" | {h.item.capability or '-'}"
        )
    return 0


def cmd_factsheet(args) -> int:
    kb = load_knowledge_base()
    sheet = build_fact_sheet(kb, args.cell, topic=args.topic)
    _p(asdict(sheet))
    return 0


def cmd_brief(args) -> int:
    kb = load_knowledge_base()
    brief = build_brief(kb, args.cell, topic=args.topic, content_type=args.content_type)
    _p(brief)
    if args.write:
        path = write_brief(brief, OUTPUT_DIR)
        print(f"\nEscrito: {path}", file=sys.stderr)
    return 0


def cmd_demo(_args) -> int:
    kb = load_knowledge_base()

    print("=" * 70)
    print("IDIEM Content System — primer demo funcional")
    print("=" * 70)

    print("\n[0] Integridad de la biblioteca (fail closed)")
    assert_integrity(kb)
    print("    OK — la biblioteca reproduce el cierre 2A.2.")

    print("\n[1] Retrieval técnico por célula")
    engine = RetrievalEngine(kb)
    for cell in kb.cells():
        n = len(engine.retrieve_by_cell(cell))
        print(f"    {cell}: {n} knowledge_items")

    print(f"\n[2] Solicitud técnica de Transporte -> CONTENT_GAP")
    rules = CellRules(kb)
    gap = rules.technical_gap(TRANSPORTE)
    print(f"    is_gap={gap.is_gap}")
    print(f"    reason={gap.reason}")

    print("\n[3] Fact sheet estructurado (LAB MINERO DIGITAL / Triaxial)")
    sheet = build_fact_sheet(kb, "LAB MINERO DIGITAL", topic="Triaxial")
    print(f"    knowledge_ids: {sheet.knowledge_ids}")
    print(f"    allowed_facts: {len(sheet.allowed_facts)} | "
          f"blocked_claims: {len(sheet.blocked_claims)} | "
          f"matices: {len(sheet.mandatory_matices)}")

    print("\n[4] Brief DRAFT schema-valid con trazabilidad (INFRA PÚBLICA RESILIENTE)")
    brief = build_brief(kb, "INFRA PÚBLICA RESILIENTE")
    path = write_brief(brief, OUTPUT_DIR)
    print(f"    content_id: {brief['content_id']}")
    print(f"    status: {brief['status']}")
    print(f"    knowledge_ids: {len(brief['knowledge_ids'])} | "
          f"relation_ids: {len(brief['traceability']['relation_ids'])} | "
          f"document_ids: {len(brief['traceability']['document_ids'])}")
    print(f"    escrito en: {path}")

    print("\n[+] Brief CONTENT_GAP para Transporte (schema-valid)")
    gap_brief = build_brief(kb, TRANSPORTE, topic="Metro L7 estructural")
    print(f"    status: {gap_brief['status']} | content_gaps: {gap_brief['content_gaps']}")

    print("\nDemo OK.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="idiem", description="IDIEM content system CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("integrity", help="Run integrity checks").set_defaults(func=cmd_integrity)
    sub.add_parser("demo", help="Run the first working demo").set_defaults(func=cmd_demo)

    p_ret = sub.add_parser("retrieve", help="Retrieve items by cell")
    p_ret.add_argument("cell")
    p_ret.add_argument("--limit", type=int, default=100)
    p_ret.set_defaults(func=cmd_retrieve)

    p_fs = sub.add_parser("factsheet", help="Build a fact sheet")
    p_fs.add_argument("cell")
    p_fs.add_argument("--topic", default=None)
    p_fs.set_defaults(func=cmd_factsheet)

    p_br = sub.add_parser("brief", help="Build a schema-valid brief")
    p_br.add_argument("cell")
    p_br.add_argument("--topic", default=None)
    p_br.add_argument("--content-type", dest="content_type", default="TECHNICAL_INSIGHT")
    p_br.add_argument("--write", action="store_true")
    p_br.set_defaults(func=cmd_brief)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
