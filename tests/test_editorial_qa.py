"""Editorial QA — diversidad por pieza y por mes + regresión de octubre."""

from idiem.editorial_qa import (
    FAIL,
    PASS,
    WARNING,
    check_month,
    check_piece,
    load_posts,
    monthly_editorial_report,
)


def _post(cid, *, chars=700, arch="problem_impact_capability", cta="commercial_contact", hook="insight",
          pcat="other", subtheme="", photo_id=None, visual=None):
    return {
        "content_id": cid,
        "copy": {"hook": "h", "body": "b", "cta": "c", "chars": chars},
        "editorial_fingerprint": {
            "content_id": cid, "service": subtheme or cid, "subtheme": subtheme or cid,
            "primary_claim": f"claim {cid}", "pain_point": f"pain {cid}",
            "pain_category": pcat, "hook_type": hook, "editorial_archetype": arch,
            "cta_type": cta, "photo_id": photo_id, "visual_theme": visual,
            "knowledge_id": cid,
        },
    }


def _diverse_month(n=12):
    archs = ["problem_impact_capability", "data_implication", "technical_question", "evidence_learning",
             "process_result", "project_challenge"]
    ctas = ["commercial_contact", "deep_dive", "download", "technical_conversation", "knowledge", "service_discovery"]
    hooks = ["risk", "question", "insight", "data_point", "technical_claim", "contrast"]
    return [
        _post(f"P{i:02d}", arch=archs[i % len(archs)], cta=ctas[i % len(ctas)],
              hook=hooks[i % len(hooks)], pcat=["risk_of_failure", "delays", "quality_assurance",
              "compliance_gap", "safety", "continuity"][i % 6], subtheme=f"sub{i}")
        for i in range(n)
    ]


# --- por pieza ---------------------------------------------------------------
def test_check_piece_flags_over_limit():
    # tope flexible (MKT 19-10-2026): sobre 900 se marca, sin bloquear
    findings = check_piece(_post("X", chars=950))
    assert any(f.level == WARNING and f.code == "char_over_reference" for f in findings)


def test_every_copy_under_character_limit_october():
    posts = load_posts("2026-10")
    assert posts, "octubre debe estar archivado"
    for p in posts:
        for f in check_piece(p):
            assert f.code != "char_limit", f"{p['content_id']} excede el tope"


# --- por mes: mes diverso pasa ----------------------------------------------
def test_diverse_month_passes():
    report = check_month("SYN", posts=_diverse_month())
    codes = {f.code for f in report.findings}
    assert "cta_concentration" not in codes
    assert "archetype_concentration" not in codes
    assert report.status in {PASS, WARNING}  # sin FAIL


def test_cta_type_not_overused():
    # Mes con CTA concentrado -> WARNING; mes balanceado -> sin hallazgo de CTA.
    concentrated = [_post(f"P{i}", cta="commercial_contact", arch=["problem_impact_capability", "technical_question"][i % 2],
                          subtheme=f"s{i}") for i in range(8)]
    r = check_month("SYN", posts=concentrated)
    assert any(f.code == "cta_concentration" for f in r.findings)
    assert not any(f.code == "cta_concentration" for f in check_month("SYN", posts=_diverse_month()).findings)


def test_month_has_minimum_archetype_diversity():
    poor = [_post(f"P{i}", arch="problem_impact_capability", cta=["commercial_contact", "deep_dive"][i % 2],
                  subtheme=f"s{i}") for i in range(12)]
    r = check_month("SYN", posts=poor)
    assert any(f.code == "archetype_diversity_low" for f in r.findings)
    assert not any(f.code == "archetype_diversity_low" for f in check_month("SYN", posts=_diverse_month()).findings)


def test_visual_reuse_is_detected_when_photo_metadata_exists():
    posts = _diverse_month(6)
    posts[0]["editorial_fingerprint"]["photo_id"] = "generica_estructura_acero_low"
    posts[1]["editorial_fingerprint"]["photo_id"] = "generica_estructura_acero_low"
    r = check_month("SYN", posts=posts)
    assert any(f.code == "photo_reuse" for f in r.findings)


# --- regresión octubre -------------------------------------------------------
def test_october_regression_detects_concentration():
    r = check_month("2026-10")
    assert r.status == WARNING
    codes = {f.code for f in r.findings}
    assert "cta_concentration" in codes         # contact x10
    assert "archetype_concentration" in codes    # problem_solution x5
    # Con los límites MKT (mín. 6 arquetipos) y sin contar los institucionales,
    # octubre SÍ queda bajo en diversidad de arquetipos (hallazgo de la auditoría).
    assert "archetype_diversity_low" in codes
    # el reporte legible se genera sin error
    assert "Reporte editorial — 2026-10" in monthly_editorial_report("2026-10")


def test_recent_knowledge_id_not_reused_in_october():
    from idiem.editorial_novelty import load_history, load_month_fingerprints
    # None = piezas institucionales (saludos / hitos) que no trazan a knowledge_id;
    # no son knowledge_ids, así que quedan fuera del chequeo de frescura.
    hist_kids = {h.get("knowledge_id") for h in load_history("2026-10")} - {None}
    oct_kids = {f.get("knowledge_id") for f in load_month_fingerprints("2026-10")} - {None}
    assert hist_kids and oct_kids
    assert hist_kids.isdisjoint(oct_kids)  # frescura: octubre no reusa knowledge_ids recientes


# --- noviembre (asignación MKT previa a redactar) -----------------------------
def test_november_archive_respects_mkt_limits():
    r = check_month("2026-11")
    codes = {f.code for f in r.findings}
    # la tabla de asignación cumplió los límites aprobados por MKT
    assert not codes & {"archetype_concentration", "cta_concentration", "hook_concentration",
                        "archetype_diversity_low", "consecutive_repeat"}
    # #4: copy final de MKT sobre el tope, registrado como excepción aprobada (no FAIL)
    over = [f for f in r.findings if f.code.startswith("char_")]
    assert over and all(f.level == WARNING for f in over)


def test_length_over_reference_warns_and_records_reason():
    from idiem.editorial_qa import check_piece
    post = _post("X", chars=1000)
    # MKT 19-10-2026: el tope de 900 es referencia flexible -> aviso, no bloqueo
    fs = check_piece(post)
    assert any(f.level == WARNING and f.code == "char_over_reference" for f in fs)
    assert not any(f.level == FAIL for f in fs)
    # con un config de tope duro, vuelve a bloquear (regla configurable)
    from idiem.loader import load_editorial_style
    hard = load_editorial_style()
    hard["length"] = dict(hard["length"], max_is_hard=True)
    assert any(f.level == FAIL and f.code == "char_limit" for f in check_piece(post, style=hard))
    post["length_override"] = "aprobado por MKT"
    fs = check_piece(post)
    assert any(f.level == WARNING and f.code == "char_limit_override" for f in fs)
    assert not any(f.level == FAIL and f.code == "char_limit" for f in fs)
