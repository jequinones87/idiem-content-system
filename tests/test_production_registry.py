"""Las piezas producidas siguen los métodos vigentes (docs/14_PLAYBOOK_PRODUCCION.md).

Fallan si alguien (persona o Claude) entrega un juego de posts sin workstation registrado,
arma un carrusel fuera de la Plantilla 02 o deja un video sin su archivo, y si los IDs del
banco de fuentes se repiten.
"""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REG = json.loads((ROOT / "config" / "production_registry.json").read_text("utf-8"))
PLANS = ROOT / "state" / "plans"
GRAFICAS = sorted(PLANS.glob("*_graficas.json"))
URL = re.compile(r"^https://claude\.ai/(code/)?artifact/[A-Za-z0-9-]+$")


def _sets():
    return [p.name.removesuffix("_graficas.json") for p in GRAFICAS]


def test_registry_entries_are_valid():
    ids = [w["id"] for w in REG["workstations"]]
    assert len(ids) == len(set(ids))
    for w in REG["workstations"]:
        assert URL.match(w["url"]), w["id"]
        assert w["status"], w["id"]


@pytest.mark.parametrize("prefix", _sets())
def test_every_plan_set_has_a_workstation(prefix):
    data = {w["data"] for w in REG["workstations"]}
    assert prefix in data, (f"state/plans/{prefix}_* no tiene workstation registrado en "
                            "config/production_registry.json (todo juego de posts se entrega en un workstation)")
    for part in ("asignacion", "copies"):
        assert (PLANS / f"{prefix}_{part}.json").exists(), f"falta {prefix}_{part}.json"


@pytest.mark.parametrize("path", GRAFICAS, ids=lambda p: p.name)
def test_pieces_follow_current_templates(path):
    g = json.loads(path.read_text("utf-8"))
    photo_dir = ROOT / g["photo_dir"]
    keys = REG["methods"]["carousel"]["data_keys"]
    for k, p in g["posts"].items():
        assert (photo_dir / p["photo"]["file"]).exists(), f"{path.name}#{k}: falta la foto"
        if "carousel" in p:
            c = p["carousel"]
            assert set(c) == {"portada", "intermedias", "cierre"}, f"{path.name}#{k}: carrusel fuera de la Plantilla 02"
            assert set(keys["portada"]) <= set(c["portada"]), f"{path.name}#{k}: portada incompleta"
            assert set(keys["cierre"]) <= set(c["cierre"]), f"{path.name}#{k}: cierre incompleto"
            assert c["intermedias"], f"{path.name}#{k}: sin intermedias"
            for sl in c["intermedias"]:
                assert set(keys["intermedias"]) <= set(sl), f"{path.name}#{k}: intermedia incompleta"
                assert (ROOT / "design_system" / "assets" / f"icon_{sl['icon']}.png").exists(), \
                    f"{path.name}#{k}: ícono icon_{sl['icon']}.png no existe"
                assert 'class="c2rb"' in sl["title"], f"{path.name}#{k}: título sin caja roja (Plantilla 02)"
        elif "special" not in p:
            assert {"svc", "msg", "base"} <= set(p), f"{path.name}#{k}: estático fuera de la Plantilla 01"
        if "video" in p:
            v = p["video"]
            assert (photo_dir / v["file"]).exists(), f"{path.name}#{k}: falta el MP4 {v['file']}"
            assert v.get("published", "").startswith("media/"), f"{path.name}#{k}: video sin ruta publicada"
            assert v.get("music"), f"{path.name}#{k}: video sin nota de música"


def test_topic_bank_ids_are_sequential_without_gaps():
    bank = json.loads((ROOT / "config" / "topic_bank" / "expert_sources.json").read_text("utf-8"))
    for key, prefix in (("sources", "SRC"), ("topics", "TOP")):
        nums = sorted(int(x["id"].split("-")[1]) for x in bank[key])
        assert nums == list(range(1, len(nums) + 1)), f"IDs {prefix} con huecos o duplicados: {nums}"
