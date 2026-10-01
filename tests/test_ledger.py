"""Published-content ledger (monthly memory / cooldown)."""

from idiem.ledger import (
    Ledger,
    load_ledger,
    recent_knowledge_ids,
    record_month,
    save_ledger,
)


def test_previous_months_cooldown_window():
    led = Ledger()
    record_month(led, "2026-08", [{"content_id": "a", "cell": "X", "knowledge_id": "KB-1"}])
    record_month(led, "2026-09", [{"content_id": "b", "cell": "X", "knowledge_id": "KB-2"}])
    recent = set(recent_knowledge_ids(led, "2026-10", cooldown_months=3))
    assert recent == {"KB-1", "KB-2"}
    # Year rollover works.
    recent_jan = set(recent_knowledge_ids(led, "2026-10", cooldown_months=1))
    assert recent_jan == {"KB-2"}  # only September is within 1-month cooldown


def test_ledger_roundtrip(tmp_path):
    led = Ledger()
    record_month(led, "2026-09", [{"content_id": "b", "cell": "X", "knowledge_id": "KB-2"}])
    p = save_ledger(led, tmp_path / "ledger.json")
    back = load_ledger(p)
    assert back.months["2026-09"][0]["knowledge_id"] == "KB-2"


def test_month_rotation_excludes_recent(kb):
    from idiem.review import compose_month

    sep = compose_month(kb, "2026-09", target_count=12)
    led = Ledger()
    record_month(
        led, "2026-09",
        [{"content_id": p.content_id, "cell": p.cell, "knowledge_id": p.knowledge_id} for p in sep.posts],
    )
    recent = recent_knowledge_ids(led, "2026-10")
    oct_ = compose_month(kb, "2026-10", target_count=12, recent_history=recent)
    sep_ids = {p.knowledge_id for p in sep.posts}
    oct_ids = {p.knowledge_id for p in oct_.posts}
    assert sep_ids.isdisjoint(oct_ids), "octubre no debe repetir ítems de septiembre"
