"""Integridad del banco de fuentes expertas y temas (config/topic_bank/expert_sources.json)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = json.loads((ROOT / "config" / "topic_bank" / "expert_sources.json").read_text("utf-8"))
CLASSES = {"SAFE", "VERIFY", "INTERNAL", "DO_NOT_PUBLISH"}
KINDS = {"concept", "normative", "third_party_stat", "idiem_capability", "public_incident",
         "project_data", "internal_reference"}
CELLS = {"INFRA PÚBLICA RESILIENTE", "INFRA HOSPITALARIA Y ASISTENCIAL", "INFRA CRÍTICA TRANSPORTE",
         "INFRA OPERACIÓN MINERA", "LAB MINERO DIGITAL"}


def _ids(key):
    return [x["id"] for x in BANK[key]]


def test_ids_unique():
    for key in ("sources", "claims", "topics"):
        ids = _ids(key)
        assert len(ids) == len(set(ids)), f"ids duplicados en {key}"


def test_sources_have_trace():
    for s in BANK["sources"]:
        assert re.fullmatch(r"SRC-\d{3}", s["id"])
        assert s["drive"].startswith("https://"), s["id"]
        assert set(s["cells"]) <= CELLS, s["id"]


def test_claims_classified_and_linked():
    src = set(_ids("sources"))
    for c in BANK["claims"]:
        assert c["class"] in CLASSES and c["kind"] in KINDS, c["id"]
        assert set(c["sources"]) <= src, c["id"]
        # fail closed: capacidades IDIEM nuevas, incidentes con nombre y datos de proyecto nunca SAFE
        if c["kind"] in {"public_incident", "project_data", "internal_reference"}:
            assert c["class"] != "SAFE", f"{c['id']} no puede ser SAFE"
        if c["kind"] == "idiem_capability" and c["class"] == "SAFE":
            assert c.get("validated_by"), f"{c['id']}: capacidad SAFE sin validación de MKT"
        if c["kind"] == "third_party_stat":
            assert c.get("cite"), f"{c['id']} sin fuente citada"


def test_topics_reference_existing_claims_and_kb():
    claims = set(_ids("claims"))
    kb_ids = set(re.findall(r"KB-[A-Z]{3}-\d{3}",
                            (ROOT / "data" / "04_conocimiento_activo_IDIEM_2A2.csv").read_text("utf-8-sig")))
    for t in BANK["topics"]:
        assert t["cell"] in CELLS, t["id"]
        assert t["claims"] and set(t["claims"]) <= claims, t["id"]
        assert set(t.get("related_kb", [])) <= kb_ids, t["id"]


def test_discarded_topics_and_blocked_claims_fail_closed():
    blocked = {c["id"] for c in BANK["claims"] if c["class"] == "DO_NOT_PUBLISH"}
    for c in BANK["claims"]:
        if c["class"] == "DO_NOT_PUBLISH":
            assert c.get("blocked_reason"), c["id"]
    for t in BANK["topics"]:
        assert t["status"] in {"CANDIDATE", "DISCARDED", "USED"}, t["id"]
        if t["status"] == "DISCARDED":
            assert t.get("discarded_reason"), t["id"]
        else:
            # un tema vigente nunca se apoya en una afirmación bloqueada
            assert not set(t["claims"]) & blocked, t["id"]


def test_aito_is_not_publishable():
    # MKT 19-10-2026: el tema de asesoría a la inspección de obras (AITO) no se publica
    claims = {c["id"]: c for c in BANK["claims"]}
    assert claims["SRC-004#C05"]["class"] == "DO_NOT_PUBLISH"
    assert claims["SRC-004#C07"]["class"] == "DO_NOT_PUBLISH"
    assert {t["id"]: t for t in BANK["topics"]}["TOP-002"]["status"] == "DISCARDED"
