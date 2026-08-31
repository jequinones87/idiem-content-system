"""Editorial style guide wiring into the drafting contract."""

from idiem.brief import build_brief
from idiem.drafting import (
    build_drafting_request,
    recommended_hashtags,
    render_drafting_prompt,
)
from idiem.loader import load_editorial_style


def test_style_guide_loads_with_required_keys():
    style = load_editorial_style()
    for key in ("voice", "structure", "length", "emoji", "hashtags"):
        assert key in style
    assert style["length"]["target_words_min"] >= 1
    assert "#IDIEM" in style["hashtags"]["always"]


def test_recommended_hashtags_per_cell():
    style = load_editorial_style()
    tags = recommended_hashtags("LAB MINERO DIGITAL", style)
    assert tags[0] == "#IDIEM"
    assert any("Ensayos" in t or "Minería" in t for t in tags)
    assert len(tags) <= style["hashtags"]["closing_block"]["max"]


def test_drafting_request_carries_style_and_hashtags(kb):
    brief = build_brief(kb, "INFRA OPERACIÓN MINERA")
    req = build_drafting_request(brief)
    assert req.style, "el encargo debe incluir la guía de estilo"
    assert "#IDIEM" in req.recommended_hashtags
    prompt = render_drafting_prompt(req)
    assert "hashtags" in prompt.lower()
    assert "110" in prompt or "length" in prompt.lower()


def test_drafting_request_accepts_injected_style(kb):
    brief = build_brief(kb, "LAB MINERO DIGITAL")
    custom = {
        "hashtags": {
            "always": ["#IDIEM"],
            "closing_block": {"min": 2, "max": 3},
            "vocabulary_by_cell": {"LAB MINERO DIGITAL": ["#Ensayos", "#Calidad"]},
        }
    }
    req = build_drafting_request(brief, style=custom)
    assert req.recommended_hashtags == ["#IDIEM", "#Ensayos", "#Calidad"]


def test_pain_point_only_for_public_organism_cells(kb):
    from idiem.brief import build_brief
    from idiem.drafting import build_drafting_request, pain_point_for
    from idiem.loader import load_editorial_style

    style = load_editorial_style()
    # Public-organism cells carry the "atraso de obras" pain point.
    for cell in ("INFRA PÚBLICA RESILIENTE", "INFRA HOSPITALARIA Y ASISTENCIAL"):
        assert "atraso" in pain_point_for(cell, style).lower()
    # Mining / lab cells have no configured pain point.
    assert pain_point_for("INFRA OPERACIÓN MINERA", style) == ""
    assert pain_point_for("LAB MINERO DIGITAL", style) == ""
    # The drafting request surfaces it for a public post.
    brief = build_brief(
        kb, "INFRA PÚBLICA RESILIENTE",
        main_knowledge_id="KB-IPR-001", enrich_same_service=True,
    )
    assert "atraso" in build_drafting_request(brief).pain_point.lower()
