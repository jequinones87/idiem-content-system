"""Cruce de los servicios de www.idiem.cl (WEB-*) contra la librería 2A.2 (+ extensión 2A.3).

El mapeo es manual y vive en ``config/topic_bank/web_crosswalk.json``. Este módulo lo
valida contra los archivos canónicos (fail closed), deriva las células desde la evidencia
y genera la vista legible ``docs/12_CRUCE_WEB_VS_2A2.md``.

Precedencia: 2A.2 manda. Si un servicio tiene evidencia (knowledge_id / EXT / AUX), el copy
usa el texto y la política de esa evidencia; el sitio solo aporta ``new_scope``, que es VERIFY.
Las células de un servicio respaldado salen de su evidencia, nunca del sitio (regla 9).

Uso:
    python -m idiem.web_crosswalk          # valida y regenera docs/12_CRUCE_WEB_VS_2A2.md
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from .loader import CONFIG_DIR, REPO_ROOT, KnowledgeBase, load_knowledge_base

CROSSWALK = CONFIG_DIR / "topic_bank" / "web_crosswalk.json"
REGISTRY = CONFIG_DIR / "topic_bank" / "web_services.json"
DOC = REPO_ROOT / "docs" / "12_CRUCE_WEB_VS_2A2.md"

STATUSES = ("RESPALDADO", "PARCIAL", "SOLO_RESERVA", "NUEVO", "BLOQUEADO")


def _load(path: Path) -> dict:
    return json.loads(path.read_text("utf-8"))


def evidence_cell(kb: KnowledgeBase, ref: str) -> str | None:
    """Célula de una evidencia en célula (KB/EXT/AUX/OVR); None si el id no existe."""
    if ref.startswith("KB-"):
        it = kb.item_by_id.get(ref)
        return it.cell if it else None
    if ref.startswith("EXT-"):
        rec = kb.enrichment_by_id(ref)
        return rec["cell"] if rec else None
    if ref.startswith("AUX-"):
        aux = kb.aux_by_id.get(ref)
        return aux.cell if aux else None
    if ref.startswith("OVR-"):
        rec = kb.policy_override_for(ref[len("OVR-"):])
        return rec["cell"] if rec and rec["override_id"] == ref else None
    return None


def cells_2a2(kb: KnowledgeBase, entry: dict) -> list[str]:
    return sorted({c for ref in entry["evidence"] if (c := evidence_cell(kb, ref))})


def validate(crosswalk: dict, registry: dict, kb: KnowledgeBase) -> list[str]:
    """Errores de consistencia; lista vacía = válido."""
    errors: list[str] = []
    services = {s["id"]: s for s in registry["services"]}
    unique = {i for i, s in services.items() if "same_text_as" not in s}
    entries = crosswalk["entries"]
    ids = [e["web_id"] for e in entries]
    if len(ids) != len(set(ids)):
        errors.append("web_id duplicado en el cruce")
    for missing in sorted(unique - set(ids)):
        errors.append(f"{missing}: servicio web sin cruzar")
    for extra in sorted(set(ids) - unique):
        errors.append(f"{extra}: no es un servicio web único (o no existe)")
    cells = set(kb.cells())
    for e in entries:
        wid, status = e["web_id"], e["status"]
        if status not in STATUSES:
            errors.append(f"{wid}: estado inválido {status}")
        for ref in e["evidence"]:
            if evidence_cell(kb, ref) is None:
                errors.append(f"{wid}: evidencia inexistente {ref}")
        for ref in e["reserve"]:
            if ref not in kb.reserve_relation_ids:
                errors.append(f"{wid}: {ref} no es relación de reserva")
        for ref in e["related"]:
            if evidence_cell(kb, ref) is None and ref not in kb.reserve_relation_ids:
                errors.append(f"{wid}: relacionado inexistente {ref}")
        for ref in e["evidence"] + e["reserve"] + e["related"]:
            if ref in kb.excluded_relation_ids:  # regla 8
                errors.append(f"{wid}: usa relación excluida {ref}")
        if not set(e["proposed_cells"]) <= cells:
            errors.append(f"{wid}: célula propuesta desconocida")
        has_ev, has_res = bool(e["evidence"]), bool(e["reserve"])
        if status in ("RESPALDADO", "PARCIAL") and not has_ev:
            errors.append(f"{wid}: {status} sin evidencia en célula")
        if status == "PARCIAL" and not e["new_scope"]:
            errors.append(f"{wid}: PARCIAL sin new_scope")
        if status == "SOLO_RESERVA" and (has_ev or not has_res):
            errors.append(f"{wid}: SOLO_RESERVA debe tener solo reserva")
        if status == "NUEVO" and (has_ev or has_res):
            errors.append(f"{wid}: NUEVO no puede tener evidencia ni reserva")
        if status == "BLOQUEADO" and not e["conflicts"]:
            errors.append(f"{wid}: BLOQUEADO sin motivo")
    return errors


# --- vista legible ----------------------------------------------------------------------

_SHORT = {
    "INFRA PÚBLICA RESILIENTE": "IPR",
    "INFRA HOSPITALARIA Y ASISTENCIAL": "IHA",
    "INFRA CRÍTICA TRANSPORTE": "ICT",
    "INFRA OPERACIÓN MINERA": "IOM",
    "LAB MINERO DIGITAL": "LMD",
}


def _cells(cs: list[str]) -> str:
    return ", ".join(_SHORT.get(c, c) for c in cs) or "—"


def _ids(refs: list[str], limit: int = 6) -> str:
    if not refs:
        return "—"
    shown = ", ".join(f"`{r}`" for r in refs[:limit])
    return shown + (f" +{len(refs) - limit}" if len(refs) > limit else "")


def _md(text: str) -> str:
    return text.replace("|", "/").replace("\n", " ")


def render(crosswalk: dict, registry: dict, kb: KnowledgeBase) -> str:
    services = {s["id"]: s for s in registry["services"]}
    dups: dict[str, list[str]] = {}
    for s in registry["services"]:
        if "same_text_as" in s:
            dups.setdefault(s["same_text_as"], []).append(s["id"])
    entries = sorted(crosswalk["entries"], key=lambda e: e["web_id"])
    count = Counter(e["status"] for e in entries)

    out = [
        "# 12 — Cruce servicios web (www.idiem.cl) vs librería 2A.2",
        "",
        "> Vista generada por `python -m idiem.web_crosswalk` desde",
        "> `config/topic_bank/web_crosswalk.json` (mapeo) y `config/topic_bank/web_services.json` (textos).",
        "> No editar a mano: editar el JSON y regenerar.",
        f"> Cruce al {crosswalk['date']} · base: {', '.join(crosswalk['basis'])}.",
        "",
        "## Reglas",
        "",
        *[f"- {r}" for r in crosswalk["rules"]],
        "",
        "## Decisiones de MKT",
        "",
        *[f"- **{d['date']}** — {d['decision']} ({', '.join(d['applies_to'])})" for d in crosswalk.get("decisions", [])],
        "",
        "## Resumen",
        "",
        "| Estado | Servicios web únicos | Qué significa |",
        "|---|---|---|",
        *[f"| **{s}** | {count.get(s, 0)} | {crosswalk['statuses'][s]} |" for s in STATUSES],
        "",
        "Células: IPR = Infra Pública Resiliente · IHA = Infra Hospitalaria y Asistencial · "
        "IOM = Infra Operación Minera · LMD = Lab Minero Digital · ICT (Transporte) sigue en CONTENT_GAP.",
        "",
    ]

    sections = [
        ("RESPALDADO", "Servicios ya respaldados en 2A.2 (usar el knowledge_id; el sitio solo aporta detalle VERIFY)"),
        ("PARCIAL", "Respaldo parcial (núcleo en 2A.2; lo nuevo del sitio está disponible en VERIFY)"),
        ("SOLO_RESERVA", "Con evidencia 2A.2 fuera de las células priorizadas (MKT decide célula)"),
        ("NUEVO", "Contenido nuevo, sin respaldo en 2A.2 (disponible en VERIFY; se valida con el post)"),
        ("BLOQUEADO", "Bloqueados por la memoria editorial"),
    ]
    for status, title in sections:
        rows = [e for e in entries if e["status"] == status]
        out += [f"## {title} — {len(rows)}", ""]
        if status in ("RESPALDADO",):
            out += ["| WEB | Servicio (sitio) | Células 2A.2 | Evidencia | Detalle nuevo (VERIFY) | Alertas |",
                    "|---|---|---|---|---|---|"]
        else:
            out += ["| WEB | Servicio (sitio) | Células 2A.2 | Evidencia / reserva | Alcance nuevo (VERIFY) | "
                    "Célula propuesta [Inferencia] | Condición / alertas |",
                    "|---|---|---|---|---|---|---|"]
        for e in rows:
            s = services[e["web_id"]]
            also = dups.get(e["web_id"], [])
            name = f"{_md(s['title'])} ({s['level']})" + (f" · también {', '.join(also)}" if also else "")
            ev = _ids(e["evidence"])
            if e["reserve"]:
                ev += " · reserva " + _ids(e["reserve"], 4)
            if e["related"]:
                ev += " · relac. " + _ids(e["related"], 3)
            alerts = " ".join(_md(c) for c in e["conflicts"])
            if s["promo_flags"] and "promocional" not in alerts:
                alerts = (alerts + " Promo: " + ", ".join(s["promo_flags"])).strip()
            if status == "RESPALDADO":
                alerts = " ".join(x for x in (_md(e["cell_condition"]), alerts) if x)
                out.append(f"| `{e['web_id']}` | {name} | {_cells(cells_2a2(kb, e))} | {ev} | "
                           f"{_md(e['new_scope']) or '—'} | {alerts or '—'} |")
            else:
                cond = " ".join(x for x in (_md(e["cell_condition"]), alerts) if x)
                out.append(f"| `{e['web_id']}` | {name} | {_cells(cells_2a2(kb, e))} | {ev} | "
                           f"{_md(e['new_scope']) or '—'} | {_cells(e['proposed_cells'])} | {cond or '—'} |")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="solo validar (no escribe el doc)")
    args = ap.parse_args(argv)
    crosswalk, registry, kb = _load(CROSSWALK), _load(REGISTRY), load_knowledge_base()
    errors = validate(crosswalk, registry, kb)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if not args.check:
        DOC.write_text(render(crosswalk, registry, kb), "utf-8")
    print(json.dumps(Counter(e["status"] for e in crosswalk["entries"]), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
