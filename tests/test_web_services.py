"""Registro de servicios de www.idiem.cl (config/topic_bank/web_services.json) y su extractor."""
import json
import re
from pathlib import Path

from idiem.web_services import build_registry, parse_detail, parse_index

ROOT = Path(__file__).resolve().parents[1]
REG = json.loads((ROOT / "config" / "topic_bank" / "web_services.json").read_text("utf-8"))
SERVICES = REG["services"]


# --- integridad del registro ------------------------------------------------------------


def test_ids_and_paths_unique():
    ids = [s["id"] for s in SERVICES]
    paths = [s["path"] for s in SERVICES]
    assert len(ids) == len(set(ids))
    assert len(paths) == len(set(paths))
    assert all(re.fullmatch(r"WEB-\d{3}", i) for i in ids)


def test_all_verify_and_validation_explicit():
    # Decisión MKT 19-10-2026: todo servicio web entra como VERIFY; nada usable sin validated_by.
    for s in SERVICES:
        assert s["class"] == "VERIFY", s["id"]
        if "validated_on" in s:
            assert s.get("validated_by"), f"{s['id']}: fecha de validación sin responsable"


def test_hierarchy_consistent():
    by_id = {s["id"]: s for s in SERVICES}
    parent_level = {"area": "categoria", "servicio": "area"}
    for s in SERVICES:
        assert s["url"] == "https://www.idiem.cl" + s["path"]
        if s["level"] == "categoria":
            assert s["parent_id"] is None
        else:
            parent = by_id[s["parent_id"]]
            assert parent["level"] == parent_level[s["level"]], s["id"]
            assert s["path"].startswith(parent["path"] + "/"), s["id"]


def test_traceable_text():
    for s in SERVICES:
        assert s["title"] and s["description"], s["id"]
        if s["level"] == "servicio":
            assert s["offerings"], f"{s['id']}: servicio sin prestaciones"


def test_duplicates_point_to_first_with_same_text():
    by_id = {s["id"]: s for s in SERVICES}
    for s in SERVICES:
        if "same_text_as" in s:
            first = by_id[s["same_text_as"]]
            assert first["content_hash"] == s["content_hash"] and "same_text_as" not in first


def test_known_promo_claims_flagged():
    # Superlativos del sitio que no pasan al copy (voz de marca, regla 6).
    flagged = {f.lower() for s in SERVICES for f in s["promo_flags"]}
    assert "único" in flagged and "mejor" in flagged


# --- extractor --------------------------------------------------------------------------

DETAIL = """<aside><ul><li><a href="/servicios/a/b/otro">Otro</a></li></ul></aside>
<div class="col-lg-9"><form><h4>Estudios de impacto en costo</h4>
<div><p>Análisis técnico   de costos.</p></div>
<label class="mdc-label"> Revisión de presupuestos </label>
<script>no()</script></form>
<p><span>help_outline</span> ¿Tienes dudas con lo que necesitas?</p><h4>Partners</h4><p>pie</p></div>"""

INDEX = """<h3>Ensayos de laboratorio</h3><p>Pruebas de materiales.</p><p>Ver más</p><p>oculto</p>
<a href="/servicios/ensayos-de-laboratorio">Ver especialidades</a>"""


def test_parse_detail_extracts_main_column_only():
    d = parse_detail(DETAIL)
    assert d == {"title": "Estudios de impacto en costo",
                 "description": ["Análisis técnico de costos."],
                 "offerings": ["Revisión de presupuestos"]}


def test_parse_detail_fails_closed_without_content():
    try:
        parse_detail("<div><h4>Sin columna</h4></div>")
    except ValueError:
        return
    raise AssertionError("debió fallar")


def test_parse_index_binds_category_by_link():
    assert parse_index(INDEX) == {"/servicios/ensayos-de-laboratorio": {
        "title": "Ensayos de laboratorio", "description": ["Pruebas de materiales."]}}


def _item(path, desc, level="categoria", parent=None):
    return {"path": path, "level": level, "parent": parent, "title": "T", "description": [desc],
            "offerings": []}


def test_recrawl_keeps_ids_and_resets_validation_on_change():
    first = build_registry([_item("/servicios/a", "x"), _item("/servicios/b", "y")], today="2026-10-19")
    for s in first["services"]:
        s["validated_by"], s["validated_on"] = "MKT", "2026-10-20"
    again = build_registry([_item("/servicios/c", "z"), _item("/servicios/b", "y"),
                            _item("/servicios/a", "x cambiado")], previous=first)
    by_path = {s["path"]: s for s in again["services"]}
    assert by_path["/servicios/a"]["id"] == "WEB-001" and by_path["/servicios/b"]["id"] == "WEB-002"
    assert by_path["/servicios/c"]["id"] == "WEB-003"
    assert "validated_by" not in by_path["/servicios/a"]  # texto cambió → vuelve a VERIFY sin validar
    assert by_path["/servicios/b"]["validated_by"] == "MKT"
