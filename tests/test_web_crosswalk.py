"""Cruce WEB-* vs 2A.2 (config/topic_bank/web_crosswalk.json): consistencia y precedencia de 2A.2."""
import copy
import json

import pytest

from idiem.loader import load_knowledge_base
from idiem.web_crosswalk import CROSSWALK, DOC, REGISTRY, cells_2a2, render, validate

CW = json.loads(CROSSWALK.read_text("utf-8"))
REG = json.loads(REGISTRY.read_text("utf-8"))
BY_ID = {e["web_id"]: e for e in CW["entries"]}


@pytest.fixture(scope="module")
def kb():
    return load_knowledge_base()


def test_crosswalk_valid_and_complete(kb):
    assert validate(CW, REG, kb) == []


def test_doc_is_up_to_date(kb):
    assert DOC.read_text("utf-8") == render(CW, REG, kb), "regenerar: python -m idiem.web_crosswalk"


def _broken(**changes):
    cw = copy.deepcopy(CW)
    web_id = changes.pop("web_id")
    entry = next(e for e in cw["entries"] if e["web_id"] == web_id)
    entry.update(changes)
    return cw


@pytest.mark.parametrize("change, expected", [
    ({"web_id": "WEB-056", "evidence": ["KB-IPR-001"]}, "NUEVO no puede tener evidencia"),
    ({"web_id": "WEB-058", "evidence": ["KB-XXX-999"]}, "evidencia inexistente"),
    ({"web_id": "WEB-058", "reserve": ["R0076"]}, "relación excluida"),
    ({"web_id": "WEB-097", "evidence": ["KB-IPR-003"]}, "SOLO_RESERVA debe tener solo reserva"),
    ({"web_id": "WEB-015", "conflicts": []}, "BLOQUEADO sin motivo"),
    ({"web_id": "WEB-064", "new_scope": ""}, "PARCIAL sin new_scope"),
    ({"web_id": "WEB-057", "proposed_cells": ["INFRA INVENTADA"]}, "célula propuesta desconocida"),
])
def test_validator_fails_closed(kb, change, expected):
    errors = validate(_broken(**change), REG, kb)
    assert any(expected in e for e in errors), errors


def test_missing_service_detected(kb):
    cw = copy.deepcopy(CW)
    cw["entries"] = [e for e in cw["entries"] if e["web_id"] != "WEB-101"]
    assert "WEB-101: servicio web sin cruzar" in validate(cw, REG, kb)


def test_cells_come_from_2a2_evidence_not_from_site(kb):
    # Ingeniería contractual: 2A.2 la tiene en IPR, IHA e IOM.
    assert cells_2a2(kb, BY_ID["WEB-008"]) == sorted(
        ["INFRA PÚBLICA RESILIENTE", "INFRA HOSPITALARIA Y ASISTENCIAL", "INFRA OPERACIÓN MINERA"])
    # Lo nuevo no tiene célula 2A.2: solo propuesta.
    assert cells_2a2(kb, BY_ID["WEB-056"]) == []
    # Transporte sigue en CONTENT_GAP: ningún servicio web se propone ahí.
    assert all("INFRA CRÍTICA TRANSPORTE" not in e["proposed_cells"] for e in CW["entries"])


def test_editorial_memory_prevails(kb):
    # Control de productividad bloqueado por MKT aunque el sitio lo ofrezca.
    assert BY_ID["WEB-015"]["status"] == BY_ID["WEB-092"]["status"] == "BLOQUEADO"
    # El claim «único triaxial gigante» del sitio queda marcado como bloqueado.
    assert any("triaxial" in c for c in BY_ID["WEB-011"]["conflicts"])
