"""Sales Intelligence v2 — capa complementaria: retrieval contextual + guardrails.

Cubre los requisitos de integración (CLAUDE_CODE_TASK §9):
- una PPT no cambia la clasificación oficial;
- Operación Minera != Laboratorio Minero Digital;
- Transporte solo recupera Metro/EFE (y conserva su regla oficial);
- VERIFY activa validación;
- DO_NOT_PUBLISH no llega al copy final;
- el retrieval no carga fichas irrelevantes.
"""

import pytest

from idiem.cells import CellRules
from idiem.sales_intelligence import (
    SAFE,
    VERIFY,
    DO_NOT_PUBLISH,
    SalesIntelligence,
    load_sales_intelligence,
)

OM = "INFRA OPERACIÓN MINERA"
LMD = "LAB MINERO DIGITAL"
TRANSPORTE = "INFRA CRÍTICA TRANSPORTE"
HOSPITAL = "INFRA HOSPITALARIA Y ASISTENCIAL"
PUBLICA = "INFRA PÚBLICA RESILIENTE"


@pytest.fixture()
def si():
    # fresh instance per test so parsed-cell scoping is observable
    return load_sales_intelligence()


# --- 1. una PPT no cambia la clasificación oficial ---------------------------
def test_sales_intelligence_never_classifies(si, kb):
    # La capa NO expone clasificación de ningún tipo.
    for attr in ("classify", "classify_cell", "route", "assign_cell"):
        assert not hasattr(si, attr), f"SI no debe exponer {attr!r}"

    # Las células oficiales las gobierna cell_rules.json / CellRules, no la PPT.
    rules = CellRules(kb)
    official = set(rules.known_cells())
    assert official == {
        "INFRA PÚBLICA RESILIENTE",
        "INFRA HOSPITALARIA Y ASISTENCIAL",
        "INFRA CRÍTICA TRANSPORTE",
        "INFRA OPERACIÓN MINERA",
        "LAB MINERO DIGITAL",
    }
    # Toda célula con cobertura SI es una célula oficial (no inventa células nuevas).
    assert set(si.official_cells()).issubset(official)

    # for_cell recibe una célula oficial ya resuelta; una desconocida => [] (fail closed).
    assert si.for_cell("CELDA_INEXISTENTE") == []


# --- 2. Operación Minera != Laboratorio Minero Digital -----------------------
def test_operacion_minera_separate_from_laboratorio(si):
    om = si.for_cell(OM)
    lab = si.for_cell(LMD)
    assert om and lab
    assert all(f.cell == OM for f in om)
    assert all(f.cell == LMD for f in lab)
    # Ninguna ficha se cruza entre células.
    om_paths = {str(f.path) for f in om}
    lab_paths = {str(f.path) for f in lab}
    assert om_paths.isdisjoint(lab_paths)
    assert not any("laboratorio" in str(f.path).lower() for f in om)

    # Un ángulo distintivo de LMD (triaxial) no aparece en el material SAFE de OM.
    om_text = " ".join(si.context_for(OM).safe_content_angles()).lower()
    lab_text = " ".join(si.context_for(LMD).safe_content_angles()).lower()
    assert "triaxial" in lab_text
    assert "triaxial" not in om_text


# --- 3. Transporte solo Metro/EFE y conserva su regla oficial ----------------
def test_transporte_only_metro_efe(si, kb):
    tr = si.for_cell(TRANSPORTE)
    assert {f.segment for f in tr} == {"metro", "efe"}
    assert si.for_cell(TRANSPORTE, segment="metro") and all(
        f.segment == "metro" for f in si.for_cell(TRANSPORTE, segment="metro")
    )
    # La PPT NO habilita capacidad técnica: la célula sigue siendo CONTENT_GAP técnico.
    gap = CellRules(kb).technical_gap(TRANSPORTE)
    assert gap.is_gap is True


# --- 4. VERIFY activa validación --------------------------------------------
def test_verify_activates_validation(si):
    ctx = si.context_for(OM)
    # Proof points de OM están marcados VERIFY.
    verify = [e for f in ctx.fichas for e in f.verify_elements()]
    assert verify, "OM debe tener elementos VERIFY"
    for e in verify:
        assert e.needs_validation is True
        assert e.publishable_without_validation is False
    assert ctx.verify_flags(), "verify_flags debe exponer los pendientes de validación"

    # Un elemento SAFE (pain points) sí es publicable sin validación.
    safe = [e for f in ctx.fichas for e in f.safe_elements()
            if "pain" in e.title.lower()]
    assert safe and safe[0].publishable_without_validation is True
    assert safe[0].needs_validation is False


def test_compound_state_fails_closed(si):
    # "Commercial packaging — VERIFY / INTERNAL" debe resolver al estado más
    # restrictivo para publicar (VERIFY), nunca ascender silenciosamente a SAFE.
    ctx = si.context_for(OM)
    pack = [e for f in ctx.fichas for e in f.elements
            if "commercial packaging" in e.title.lower()]
    assert pack
    assert pack[0].effective_state == VERIFY
    assert pack[0].publishable_without_validation is False


# --- 5. DO_NOT_PUBLISH nunca llega al copy final -----------------------------
def test_do_not_publish_excluded_from_output(si):
    ctx = si.context_for(LMD)
    excluded = ctx.excluded_items()
    assert excluded, "LMD tiene una sección DO_NOT_PUBLISH"

    # Nada DO_NOT_PUBLISH aparece en el material afirmable (SAFE) del enrichment.
    enr = ctx.to_drafting_enrichment()
    safe_blob = " ".join(
        enr["pain_points"] + enr["business_needs"]
        + enr["value_propositions"] + enr["content_angles"]
    ).lower()
    for phrase in excluded:
        assert phrase.lower() not in safe_blob

    # El guardrail bloquea una frase DO_NOT_PUBLISH en copy final.
    with pytest.raises(ValueError):
        si.assert_publishable("IDIEM, laboratorio líder en Chile.")


def test_guardrail_blocks_causal_terms_but_not_valid_words(si):
    with pytest.raises(ValueError):
        si.assert_publishable("Este servicio garantiza cero fallas.")
    # "aseguramiento" (propuesta de valor válida) NO debe gatillar el guardrail
    # de "asegura" (límite de palabra).
    si.assert_publishable("Aseguramiento técnico independiente para la obra.")


# --- 6. el retrieval no carga fichas irrelevantes ----------------------------
def test_retrieval_loads_only_requested_cell(si):
    assert si.parsed_cells == set()
    fichas = si.for_cell(HOSPITAL)
    assert len(fichas) == 1
    assert fichas[0].segment == "salud_publica"
    # Solo se parseó la célula pedida; ninguna otra.
    assert si.parsed_cells == {HOSPITAL}
    # Una célula sin cobertura no rompe ni arrastra otras fichas.
    assert si.for_cell("OTRA_CELDA") == []
    assert si.parsed_cells == {HOSPITAL}


# --- precedencia declarada ---------------------------------------------------
def test_precedence_order(si):
    assert si.precedence == [
        "official_cell_rules",
        "editorial_rules",
        "validated_services_and_brochures",
        "sales_intelligence",
        "cases_and_evidence",
        "external_sources",
    ]
    # Sales Intelligence por debajo de reglas oficiales, editoriales y servicios.
    assert si.precedence.index("sales_intelligence") == 3


# --- trazabilidad ------------------------------------------------------------
def test_traceability_records_source(si):
    ctx = si.context_for(TRANSPORTE, segment="metro")
    trace = ctx.trace()
    assert trace["cell"] == TRANSPORTE
    assert trace["segment"] == "metro"
    assert trace["fichas"], "debe registrar la ficha consultada"
    f0 = trace["fichas"][0]
    assert f0["segment"] == "metro"
    assert "Metro" in f0["source_ppt"]  # PPT de origen registrado
    assert f0["drive_id"]               # trazabilidad a la fuente
