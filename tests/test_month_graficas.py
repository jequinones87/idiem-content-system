"""Cobertura de la capa visual mensual (state/plans/<mes>_graficas.json).

Cada post del plan aprobado debe tener pieza, foto existente y traza de origen;
los posts con flag VERIFY en los copies deben llevar su aviso en la pieza; ningún
texto de pieza puede llevar siglas de célula ni superlativos.
"""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PLANS = ROOT / "state" / "plans"
MONTHS = sorted(p.name.split("_")[0] for p in PLANS.glob("*_graficas.json"))
SIGLAS = re.compile(r"\b(IOM|IPR|IHA|LMD|ICT)\b")
SUPERLATIVOS = re.compile(r"\b(l[ií]der(es)?|el mejor|los mejores|n[uú]mero uno|#1|el [uú]nico)\b", re.I)


def _load(month):
    g = json.loads((PLANS / f"{month}_graficas.json").read_text("utf-8"))
    plan = json.loads((PLANS / f"{month}_asignacion.json").read_text("utf-8"))
    copies = json.loads((PLANS / f"{month}_copies.json").read_text("utf-8"))
    return g, plan, copies


def _texts(post):
    out = [post.get("svc", ""), post.get("msg", ""), post.get("base", "")]
    c = post.get("carousel") or {}
    if c:
        out += [c["portada"]["kicker"], c["portada"]["title"], c["cierre"]["bajada"]]
        for sl in c["intermedias"]:
            out += [sl["title"], sl["body"]]
    s = post.get("special") or {}
    out += [s.get("kicker", ""), s.get("title", ""), s.get("sub", "")]
    return " ".join(out)


@pytest.mark.parametrize("month", MONTHS)
def test_every_planned_post_has_a_piece_and_photo(month):
    g, plan, copies = _load(month)
    keys = {str(p["seq"]) for p in plan["posts"]} | ({"E"} if "E" in copies["copies"] else set())
    assert keys <= set(g["posts"]), f"posts sin pieza: {keys - set(g['posts'])}"
    for k in keys:
        ph = g["posts"][k]["photo"]
        assert (ROOT / g["photo_dir"] / ph["file"]).exists(), f"{k}: falta {ph['file']}"
        assert ph["source"] in {"library", "stock"}
        assert ph.get("drive") if ph["source"] == "library" else ph.get("id")


@pytest.mark.parametrize("month", MONTHS)
def test_carousel_format_matches_plan(month):
    g, plan, _ = _load(month)
    for p in plan["posts"]:
        is_car = "carousel" in g["posts"][str(p["seq"])]
        assert is_car == (p["format"] == "CAROUSEL"), f"post {p['seq']}: formato no coincide"


@pytest.mark.parametrize("month", MONTHS)
def test_piece_text_has_no_cell_codes_nor_superlatives(month):
    g, _, _ = _load(month)
    for k, post in g["posts"].items():
        t = _texts(post)
        assert not SIGLAS.search(t), f"{k}: siglas de célula en la pieza"
        assert not SUPERLATIVOS.search(t), f"{k}: superlativo en la pieza"


@pytest.mark.parametrize("month", MONTHS)
def test_verify_posts_are_flagged_on_the_piece(month):
    g, _, copies = _load(month)
    for item in copies.get("verify_before_publish", []):
        k = re.match(r"#(\d+)", item).group(1)
        assert g["posts"][k].get("flag", "").startswith("VERIFY"), f"post {k} sin aviso VERIFY"
