"""Photo Library: real-photo selection vs Muapi fallback, and graphic wiring."""

from idiem.photo_library import Photo, decide_photo, load_photos, build_muapi_prompt


def _demo_photos() -> list[Photo]:
    return [
        Photo(
            id="PHO-9001", archivo="mina_estructura.jpg", concepto="estructura",
            celulas=("INFRA OPERACIÓN MINERA",), subtemas=("Monitoreo e integridad estructural",),
            disciplina="estructuras", entorno="mina", orientacion="H",
            tipo="propia_idiem", derechos="propia", personas="no", consentimiento="na",
            fuente="drive://x", notas="",
        ),
        Photo(
            id="PHO-9002", archivo="obra_hormigon.jpg", concepto="hormigon",
            celulas=("INFRA PÚBLICA RESILIENTE",), subtemas=("Ensayos de especialidades",),
            disciplina="hormigon", entorno="obra", orientacion="H",
            tipo="stock", derechos="licencia_vigente", personas="no", consentimiento="na",
            fuente="drive://y", notas="",
        ),
    ]


def test_manifest_loads_and_is_nonempty():
    photos = load_photos()
    assert len(photos) >= 40
    assert all(p.id and p.celulas for p in photos)


def test_selects_real_photo_when_it_corresponds():
    d = decide_photo(
        cell="INFRA OPERACIÓN MINERA",
        subtema="Monitoreo e integridad estructural",
        disciplina="estructuras",
        entorno="mina",
        photos=_demo_photos(),
    )
    assert d["source"] == "library"
    assert d["photo_id"] == "PHO-9001"
    assert d["score"] >= 6


def test_falls_back_to_muapi_when_nothing_corresponds():
    d = decide_photo(
        cell="INFRA CRÍTICA TRANSPORTE",  # no photo for this cell in demo set
        subtema="Vías férreas",
        disciplina="ferrocarril",
        entorno="terreno",
        photos=_demo_photos(),
    )
    assert d["source"] == "muapi"
    assert d["origin"] == "muapi_generada"
    assert "prompt" in d and d["prompt"]
    # Muapi prompt never carries text/logos or invents specifics
    low = d["prompt"].lower()
    assert "sin texto" in low and "sin logos" in low


def test_muapi_prompt_is_generic_not_specific():
    p = build_muapi_prompt(
        cell="LAB MINERO DIGITAL", subtema="Control de calidad HDPE",
        disciplina="soldadura", entorno="faena",
    )
    assert "hdpe" in p.lower()
    # no superlatives / project attribution
    for bad in ("primer", "líder", "mejor", "único"):
        assert bad not in p.lower()


def test_cell_is_a_hard_filter():
    # Right disciplina/entorno but wrong cell -> must not be chosen from library
    d = decide_photo(
        cell="INFRA HOSPITALARIA Y ASISTENCIAL",
        subtema="Monitoreo e integridad estructural",
        disciplina="estructuras",
        entorno="mina",
        photos=_demo_photos(),
    )
    assert d["source"] == "muapi"


def test_exclude_ids_avoids_repeats():
    photos = _demo_photos()
    d = decide_photo(
        cell="INFRA OPERACIÓN MINERA",
        subtema="Monitoreo e integridad estructural",
        disciplina="estructuras",
        entorno="mina",
        exclude_ids={"PHO-9001"},
        photos=photos,
    )
    # only matching cell photo excluded -> fall back
    assert d["source"] == "muapi"
