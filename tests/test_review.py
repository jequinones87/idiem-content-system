"""Monthly Content Ops review (compose + render)."""

from idiem.brief import validate_brief
from idiem.review import (
    compose_month,
    render_review_html,
    set_post_copy,
    to_standalone_html,
)


def test_compose_matches_plan_slots(kb):
    review = compose_month(kb, "2026-09", target_count=12)
    total = review.draft_count + review.gap_count
    assert total == 12
    assert len(review.posts) == review.draft_count
    assert len(review.gaps) == review.gap_count


def test_each_post_is_anchored_and_schema_valid(kb):
    review = compose_month(kb, "2026-09", target_count=12)
    for post in review.posts:
        # anchored: the slot's knowledge_id is the main item in the brief
        assert post.knowledge_id in post.brief["knowledge_ids"]
        assert post.status == "DRAFT"
        validate_brief(post.brief)


def test_no_cross_cell_leak_in_posts(kb):
    review = compose_month(kb, "2026-09", target_count=12)
    for post in review.posts:
        assert post.brief["cell"] == post.cell
        # Enrichment stays within the same cell AND the anchor's service.
        anchor = kb.item_by_id[post.knowledge_id]
        for kid in post.brief["knowledge_ids"]:
            item = kb.item_by_id[kid]
            assert item.cell == post.cell
            assert item.service == anchor.service


def test_transporte_only_appears_as_gap(kb):
    review = compose_month(kb, "2026-09", target_count=12)
    assert all(p.cell != "INFRA CRÍTICA TRANSPORTE" for p in review.posts)
    assert any(g.cell == "INFRA CRÍTICA TRANSPORTE" for g in review.gaps)


def test_render_contains_month_anchors_and_governance(kb):
    review = compose_month(kb, "2026-09", target_count=12)
    htmlc = render_review_html(review)
    assert "2026-09" in htmlc
    assert "<title>" in htmlc
    for post in review.posts:
        assert f'id="{post.content_id}"' in htmlc
    # If any composed post carries blocked claims, the view must surface them.
    if any(p.brief.get("blocked_claims") for p in review.posts):
        assert "Claims bloqueados" in htmlc


def test_standalone_wrap_is_well_formed(kb):
    review = compose_month(kb, "2026-09", target_count=6)
    doc = to_standalone_html(render_review_html(review))
    assert doc.startswith("<!doctype html>")
    assert "<head>" in doc and "</head>" in doc
    assert "<body>" in doc


def test_set_post_copy_ingests_publishable_copy(kb):
    review = compose_month(kb, "2026-09", target_count=12)
    post = review.posts[0]
    good = {
        "hook": "Respaldo técnico para infraestructura.",
        "body": "Contenido acotado a la evidencia disponible.",
        "cta": "Conversemos.",
    }
    updated = set_post_copy(review, post.content_id, good)
    assert updated.brief["draft_copy"] == good
    assert updated.brief["status"] == "DRAFT"
