"""Graphic brief derivation + guardrails."""

from idiem.graphic import build_graphic_brief
from idiem.review import compose_month


def test_graphic_brief_fields_and_no_forbidden(kb):
    review = compose_month(kb, "2026-09", target_count=12)
    for post in review.posts:
        g = post.graphic_brief
        assert set(g) >= {"visual_headline", "key_points", "recommended_format",
                          "needs_photo", "photo_query", "evidence_ids"}
        assert g["recommended_format"] in {"STATIC", "CAROUSEL"}
        text = (g["visual_headline"] + " " + " ".join(g["key_points"])).lower()
        # No blocked superlative reaches the graphic.
        for term in ("único", "líder mundial", "el más grande", "primero del mundo"):
            assert term not in text


def test_graphic_brief_sanitizes_forbidden_source_fact(kb):
    # LMD geotecnia/rocas carries "único…" inside a source fact; the graphic
    # must drop it, not crash.
    from idiem.review import replace_post
    review = compose_month(kb, "2026-09", target_count=12)
    # Build directly for a rocas post via a fresh brief.
    from idiem.brief import build_brief
    brief = build_brief(kb, "LAB MINERO DIGITAL", main_knowledge_id="KB-LMD-004",
                        enrich_same_service=True)
    g = build_graphic_brief(brief, "Geotecnia y rocas")
    joined = (g["visual_headline"] + " " + " ".join(g["key_points"])).lower()
    assert "único" not in joined
