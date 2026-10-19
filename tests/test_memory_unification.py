"""Integración de ramas (19-10-2026): memoria única, longitud y evidencia de noviembre."""

import json
import sys
from pathlib import Path

from idiem.ledger import build_ledger_from_archive, load_ledger
from idiem.loader import load_editorial_style

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "design_system"))

from archive_month_plan import evidence_from_fact_check  # noqa: E402


def test_length_rule_is_identical_in_both_configs():
    style = load_editorial_style()["length"]
    div = json.loads((REPO / "config" / "editorial_diversity.json").read_text(encoding="utf-8"))["length"]
    for k in ("unit", "max_chars", "target_chars_min", "target_chars_max"):
        assert style[k] == div[k], k


def test_engine_limits_mirror_mkt_limits():
    cfg = json.loads((REPO / "config" / "editorial_diversity.json").read_text(encoding="utf-8"))
    lim, d = cfg["limits_per_month"], cfg["diversity"]
    assert d["min_distinct_archetypes"] == lim["min_distinct_archetypes"]
    assert d["max_same_archetype"] == lim["max_posts_per_archetype"]
    assert d["max_same_cta_type"] == lim["max_posts_per_cta_type"]
    assert d["max_same_hook_type"] == lim["max_posts_per_hook_type"]
    assert cfg["history_window_months"] == cfg["recency"]["compare_against_months"]


def test_single_monthly_memory():
    assert not (REPO / "state" / "consolidated").exists() or \
        not list((REPO / "state" / "consolidated").glob("*.json"))
    for m in ("2026-09", "2026-10", "2026-11"):
        assert (REPO / "content" / "archive" / f"{m}.json").exists()


def test_ledger_is_derived_from_archive():
    assert load_ledger().to_dict() == build_ledger_from_archive().to_dict()


def test_november_status_recorded():
    a = json.loads((REPO / "content" / "archive" / "2026-11.json").read_text(encoding="utf-8"))
    st = {p["seq"]: p["status"] for p in a["posts"]}
    assert st[4] == "PUBLICADO"
    assert all(v == "PROGRAMADO" for k, v in st.items() if k != 4)
    assert len(st) == 12


def test_evidence_parser_expands_and_excludes_replaced():
    assert evidence_from_fact_check("KB-IOM-001/002 literal + EXT-0010/0011") == \
        ["KB-IOM-001", "KB-IOM-002", "EXT-0010", "EXT-0011"]
    # #9 nov: KB-IOM-019 quedó bloqueado por MKT; no puede entrar como evidencia
    assert "KB-IOM-019" not in evidence_from_fact_check(
        "KB-IOM-016 + EXT-0006 literal. Reemplaza a KB-IOM-019 (MKT: sin certeza del servicio).")


def test_blocked_productivity_items_never_in_archive_evidence():
    for m in ("2026-11",):
        a = json.loads((REPO / "content" / "archive" / f"{m}.json").read_text(encoding="utf-8"))
        for p in a["posts"]:
            assert not {"KB-IOM-019", "KB-IOM-020"} & set(p["evidence_ids"]), p["content_id"]
