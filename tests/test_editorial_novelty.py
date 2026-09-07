"""Editorial novelty engine — historial, similitud y detección de repetición."""

from idiem.editorial_novelty import (
    editorial_history_summary,
    jaccard,
    load_history,
    load_month_fingerprints,
    near_duplicates,
    novelty_band,
    novelty_score,
    pairwise_near_duplicates,
    previous_months,
    select_diverse,
)


def _fp(cid, *, claim="", pain="", hook="insight", arch="problem_solution",
        cta="contact", pcat="other", kid=None, subtheme="", visual=None):
    return {
        "content_id": cid, "knowledge_id": kid or cid, "subtheme": subtheme or cid,
        "primary_claim": claim, "pain_point": pain, "pain_category": pcat,
        "hook_type": hook, "editorial_archetype": arch, "cta_type": cta,
        "visual_theme": visual,
    }


def test_jaccard():
    assert jaccard(set(), set()) == 0.0
    assert jaccard({"a", "b"}, {"a", "b"}) == 1.0
    assert jaccard({"a", "b"}, {"a", "c"}) == 1 / 3


def test_previous_months_wraps_year():
    assert previous_months("2026-01", 2) == ["2025-12", "2025-11"]


def test_load_history_reads_previous_month():
    hist = load_history("2026-10", window_months=3)
    assert len(hist) >= 12  # incluye septiembre archivado
    assert all("hook_type" in f for f in hist)


def test_history_summary_has_required_keys():
    hist = load_month_fingerprints("2026-09")
    s = editorial_history_summary(hist)
    for key in ("recent_subthemes", "recent_claims", "recent_pain_points",
                "recent_hooks", "recent_hook_types", "recent_archetypes",
                "recent_cta_types", "recent_phrases_to_avoid"):
        assert key in s
    assert "conversation" in s["recent_cta_types"]  # septiembre concentró conversation


def test_novelty_penalizes_repetition():
    history = [_fp("H", hook="risk", arch="problem_solution", cta="contact",
                   pcat="risk_of_failure", kid="KB-1", subtheme="fallas")]
    repeat = _fp("C1", hook="risk", arch="problem_solution", cta="contact",
                 pcat="risk_of_failure", kid="KB-1", subtheme="fallas")
    fresh = _fp("C2", hook="opportunity", arch="explainer", cta="no_cta",
                pcat="sustainability", kid="KB-9", subtheme="sostenibilidad")
    s_repeat, reasons = novelty_score(repeat, history)
    s_fresh, _ = novelty_score(fresh, history)
    assert s_fresh > s_repeat
    assert reasons  # explica por qué penaliza
    assert novelty_band(1.0) == "high" and novelty_band(0.1) == "low"


def test_structural_equivalence_detected_even_with_different_words():
    # Principio final: mismo pain+hook+arquetipo+CTA => editorialmente cercano.
    a = _fp("A", claim="Una falla no detectada detiene la operación",
            pain="Una falla no detectada puede detener la operación",
            hook="risk", arch="problem_solution", cta="contact", pcat="risk_of_failure")
    b = _fp("B", claim="Un deterioro no identificado compromete la continuidad",
            pain="Un deterioro no identificado compromete la continuidad",
            hook="risk", arch="problem_solution", cta="contact", pcat="risk_of_failure")
    c = _fp("C", claim="Detectar anomalías a tiempo reduce riesgos",
            pain="Detectar anomalías a tiempo permite reducir riesgos",
            hook="risk", arch="problem_solution", cta="contact", pcat="risk_of_failure")
    pairs = pairwise_near_duplicates([a, b, c])
    assert len(pairs) == 3  # A-B, A-C, B-C
    assert all(p["shared_structure"] for p in pairs)


def test_near_duplicate_claims_are_detected():
    a = _fp("A", claim="control de calidad del hormigón en faena minera", subtheme="hormigon")
    b = _fp("B", claim="control de calidad de hormigon en la faena minera", subtheme="hormigon")
    hits = near_duplicates(a, [b])
    assert hits and any("claim" in r for r in hits[0]["reasons"])


def test_near_duplicate_hooks_are_detected():
    a = _fp("A", pain="una falla no detectada puede detener la operación minera",
            hook="risk", arch="explainer", cta="learn_more", pcat="risk_of_failure")
    b = _fp("B", pain="una falla no detectada puede detener la faena minera",
            hook="question", arch="checklist", cta="no_cta", pcat="delays")
    hits = near_duplicates(a, [b])
    assert hits and any("pain" in r for r in hits[0]["reasons"])


def test_select_diverse_prefers_novel_and_respects_k():
    history = [_fp("H", hook="risk", arch="problem_solution", cta="contact",
                   pcat="risk_of_failure", kid="KB-1", subtheme="fallas")]
    cands = [
        _fp("dup", hook="risk", arch="problem_solution", cta="contact",
            pcat="risk_of_failure", kid="KB-1", subtheme="fallas"),
        _fp("nov1", hook="opportunity", arch="explainer", cta="no_cta",
            pcat="sustainability", kid="KB-9", subtheme="sostenibilidad"),
        _fp("nov2", hook="statistic", arch="checklist", cta="self_assessment",
            pcat="quality_assurance", kid="KB-8", subtheme="ensayos"),
    ]
    chosen = select_diverse(cands, 2, history)
    ids = {c["content_id"] for c in chosen}
    assert len(chosen) == 2
    assert "dup" not in ids  # el duplicado del historial queda fuera
    # nunca inventa: pide más de los disponibles -> devuelve los que hay
    assert len(select_diverse(cands, 10, history)) == 3


def test_editorial_history_is_added_to_drafting_request(kb):
    from idiem.brief import build_brief
    from idiem.drafting import build_drafting_request, render_drafting_prompt

    brief = build_brief(kb, "INFRA OPERACIÓN MINERA")
    req = build_drafting_request(brief, month="2026-10")
    assert req.editorial_history, "el request debe traer el historial editorial reciente"
    assert "recent_cta_types" in req.editorial_history
    assert "editorial_history" in render_drafting_prompt(req)
    # backward compatible: sin month no se carga historial
    assert build_drafting_request(brief).editorial_history == {}
