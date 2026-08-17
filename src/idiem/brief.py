"""Milestone 4 — brief generator.

Produces a brief that validates against ``schemas/content_brief.schema.json``,
enforcing same-cell evidence, content type, approval state, the visual-brief
contract and QA fields. Status stays ``DRAFT`` until human approval (rule 10),
or ``CONTENT_GAP`` when the fact sheet cannot be safely populated.

Copy here is a deterministic scaffold built ONLY from the fact sheet's allowed
facts — it never introduces an IDIEM fact absent from the fact sheet. Rich
drafting is a later milestone (M6) and plugs in behind the same contract.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from .factsheet import FactSheet, build_fact_sheet
from .loader import SCHEMA_DIR, KnowledgeBase

_CELL_CODE = {
    "INFRA PÚBLICA RESILIENTE": "IPR",
    "INFRA HOSPITALARIA Y ASISTENCIAL": "IHA",
    "INFRA CRÍTICA TRANSPORTE": "ICT",
    "INFRA OPERACIÓN MINERA": "IOM",
    "LAB MINERO DIGITAL": "LMD",
}

_VALID_CONTENT_TYPES = {
    "TECHNICAL_INSIGHT",
    "SERVICE_EXPLAINER",
    "PROJECT_EVIDENCE",
    "VALUE_ATTRIBUTE",
    "EXPERT_INPUT_REQUIRED",
}

_schema_cache: dict | None = None


def load_brief_schema() -> dict:
    global _schema_cache
    if _schema_cache is None:
        with (SCHEMA_DIR / "content_brief.schema.json").open("r", encoding="utf-8") as fh:
            _schema_cache = json.load(fh)
    return _schema_cache


def validate_brief(brief: dict) -> None:
    """Raise jsonschema.ValidationError if the brief is not schema-valid."""
    Draft202012Validator(load_brief_schema()).validate(brief)


def is_valid_brief(brief: dict) -> bool:
    return Draft202012Validator(load_brief_schema()).is_valid(brief)


def _content_id(cell: str, topic: str | None) -> str:
    code = _CELL_CODE.get(cell, "GEN")
    digest = hashlib.sha1(f"{cell}|{topic or ''}".encode("utf-8")).hexdigest()[:8]
    return f"IDIEM-{code}-{digest}"


def _editorial_angle(kb: KnowledgeBase, cell: str, provided: str | None) -> str:
    if provided:
        return provided
    cd = kb.cell_def_by_name.get(cell)
    return cd.communication_reference_2026 if cd else ""


def _draft_copy(sheet: FactSheet, angle: str) -> dict:
    """Deterministic, fact-bounded scaffold. Adds no IDIEM facts (M6 replaces)."""
    if sheet.is_content_gap:
        return {"hook": "", "body": "", "cta": ""}
    body = "\n".join(sheet.allowed_facts)
    return {
        "hook": angle,
        "body": body,
        "cta": "Conversemos sobre cómo el respaldo técnico de IDIEM aplica a tu proyecto.",
    }


def build_brief(
    kb: KnowledgeBase,
    cell: str,
    *,
    topic: str | None = None,
    content_type: str = "TECHNICAL_INSIGHT",
    audience: str | None = None,
    objective: str | None = None,
    editorial_angle: str | None = None,
    recommended_format: str = "STATIC",
) -> dict:
    """Build a schema-valid brief dict for ``cell`` (+ optional topic)."""
    if content_type not in _VALID_CONTENT_TYPES:
        raise ValueError(f"content_type inválido: {content_type!r}")
    if recommended_format not in {"STATIC", "CAROUSEL"}:
        raise ValueError(f"recommended_format inválido: {recommended_format!r}")

    sheet = build_fact_sheet(kb, cell, topic=topic, audience=audience)
    angle = _editorial_angle(kb, cell, editorial_angle)

    if sheet.is_content_gap:
        status = "CONTENT_GAP"
        effective_type = "EXPERT_INPUT_REQUIRED"
        expert_required = True
        expert_request = (
            "Falta evidencia técnica activa para esta célula/tema. Se requiere insumo "
            "de especialista o ampliación auditada de la biblioteca antes de generar copy."
        )
    else:
        status = "DRAFT"  # permanece DRAFT hasta aprobación humana (rule 10)
        effective_type = content_type
        expert_required = False
        expert_request = None

    visual_points = sheet.allowed_facts[:3]
    brief = {
        "content_id": _content_id(cell, topic),
        "status": status,
        "cell": cell,
        "content_type": effective_type,
        "audience": audience,
        "objective": objective or f"Contenido de {cell} respaldado por la biblioteca 2A.2.",
        "editorial_angle": angle,
        "core_problem_or_question": topic or "",
        "knowledge_ids": sheet.knowledge_ids,
        "auxiliary_ids": sheet.auxiliary_ids,
        "allowed_facts": sheet.allowed_facts,
        "mandatory_matices": sheet.mandatory_matices,
        "blocked_claims": sheet.blocked_claims,
        "content_gaps": sheet.content_gaps,
        "expert_input_required": expert_required,
        "expert_input_request": expert_request,
        "recommended_format": recommended_format,
        "draft_copy": _draft_copy(sheet, angle),
        "visual_brief": {
            "main_message": angle,
            "supporting_points": visual_points,
            "evidence_to_visualize": sheet.knowledge_ids,
        },
        "traceability": {
            "relation_ids": sheet.relation_ids,
            "document_ids": sheet.document_ids,
        },
        "qa": {
            "fact_check_passed": False,
            "editorial_check_passed": False,
            "human_approval": False,
            "notes": list(sheet.log),
        },
    }

    validate_brief(brief)
    return brief


def write_brief(brief: dict, out_dir: Path) -> Path:
    """Persist a brief to the application output directory (never under data/)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{brief['content_id']}.json"
    with path.open("w", encoding="utf-8") as fh:
        json.dump(brief, fh, ensure_ascii=False, indent=2)
    return path
