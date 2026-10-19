"""Archivador de meses planificados con datos (desde noviembre 2026).

Congela en ``content/archive/AAAA-MM.json`` (+ ``.md``) — la memoria ÚNICA — un mes
armado con ``state/plans/AAAA-MM_{asignacion,copies,graficas}.json``. A diferencia de
``archive_month.py`` (sep/oct, que lee los generadores), aquí la huella editorial
usa la ASIGNACIÓN aprobada por MKT antes de redactar (arquetipo, hook_type, cta_type,
pain point, claim); la heurística solo completa lo que falte.

El estado por pieza (publicado / programado / borrador) lo declara quien archiva:
  PYTHONPATH=src python3 design_system/archive_month_plan.py --month 2026-11 \\
      --default-status PROGRAMADO --status 4=PUBLICADO
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
sys.path.insert(0, str(REPO / "src"))

from idiem.archive import build_month_archive, to_markdown  # noqa: E402

CELL_SHORT = {
    "INFRA PÚBLICA RESILIENTE": "IPR",
    "INFRA HOSPITALARIA Y ASISTENCIAL": "IHA",
    "INFRA CRÍTICA TRANSPORTE": "ICT",
    "INFRA OPERACIÓN MINERA": "IOM",
    "LAB MINERO DIGITAL": "LMD",
}
STATUSES = {"PUBLICADO", "PROGRAMADO", "DRAFT"}
_ID_RE = re.compile(r"\b(KB-[A-Z]{3}-|EXT-)(\d{3,4})((?:/\d{3,4})*)")
# Lo que viene después de "Reemplaza a" / "en lugar de" NO es evidencia (p.ej. #9 nov:
# KB-IOM-019 quedó bloqueado por MKT).
_EXCLUDE_AFTER = re.compile(r"reemplaza a|en lugar de|no usar", re.IGNORECASE)


def evidence_from_fact_check(text: str) -> list[str]:
    """IDs citados en la nota de fact-check, expandiendo 'KB-IOM-001/002' y 'EXT-0010/0011'."""
    text = _EXCLUDE_AFTER.split(text or "", maxsplit=1)[0]
    ids = []
    for prefix, first, rest in _ID_RE.findall(text):
        ids.append(prefix + first)
        ids += [prefix + n for n in rest.split("/") if n]
    return ids
_ARCH_ALIASES = {"institucional": "institutional_or_occasion", "efemeride": "institutional_or_occasion"}


def split_copy(full: str) -> dict:
    """hook = 1er párrafo · cta = CTA + hashtags (2 últimos) · body = el resto."""
    paras = [p for p in full.strip().split("\n\n")]
    if len(paras) < 4:
        raise ValueError("copy demasiado corto para separar hook/body/cta")
    return {"hook": paras[0], "body": "\n\n".join(paras[1:-2]), "cta": "\n\n".join(paras[-2:]),
            "full": full.strip(), "chars": len(full.strip())}


def _photo(g: dict) -> dict:
    ph = g.get("photo") or {}
    if ph.get("source") == "library":
        return {"source": "libreria_idiem", "photo_id": ph.get("id", ""),
                "fuente": ph.get("drive", ""), "detalle": ph.get("detalle", "")}
    if ph.get("source") in {"stock", "adobe_stock"}:
        return {"source": "adobe_stock", "stock_id": ph.get("id", ""), "detalle": ph.get("detalle", "")}
    return {"source": ph.get("source", "sin_foto"), "detalle": ph.get("detalle", "")}


def _assignment(a: dict) -> dict:
    arch = _ARCH_ALIASES.get(a.get("archetype"), a.get("archetype"))
    return {k: v for k, v in {"archetype": arch, "hook_type": a.get("hook_type"),
                              "cta_type": a.get("cta_type"), "pain_point": a.get("pain_point"),
                              "claim": a.get("main_claim")}.items() if v}


def build(month: str, statuses: dict[str, str], default_status: str) -> dict:
    plans = REPO / "state" / "plans"
    asig = json.loads((plans / f"{month}_asignacion.json").read_text(encoding="utf-8"))
    copies = json.loads((plans / f"{month}_copies.json").read_text(encoding="utf-8"))
    gfx = json.loads((plans / f"{month}_graficas.json").read_text(encoding="utf-8"))["posts"]
    fact = copies.get("fact_check", {})

    items = [(str(p["seq"]), p, False) for p in asig["posts"]]
    items += [("E", e, True) for e in asig.get("extra", [])]
    posts = []
    for key, a, special in items:
        if key not in copies["copies"]:
            raise ValueError(f"{month}: falta copy para la pieza {key} (fail closed)")
        kid = a.get("knowledge_id")
        evidence = sorted(set(evidence_from_fact_check(fact.get(key, ""))) | ({kid} if kid else set()))
        g = gfx.get(key, {})
        status = statuses.get(key, default_status)
        if status not in STATUSES:
            raise ValueError(f"estado inválido {status!r} para {key}")
        posts.append({
            "seq": int(a["seq"]),
            "content_id": f"EFEM-{month}" if special else f"PLAN-{kid}-{int(a['seq']):02d}",
            "cell": None if special else a["cell"],
            "cell_short": "" if special else CELL_SHORT.get(a["cell"], a["cell"][:3].upper()),
            "subtheme": a.get("theme", ""),
            "editorial_angle": a.get("theme", "") if not special else
            f"efeméride institucional: {a.get('theme', '')} (no traza a knowledge_id)",
            "format": a.get("format") or a.get("type") or "STATIC",
            "date": a.get("date"),
            "knowledge_id": None if special else kid,
            "evidence_ids": [] if special else evidence,
            "graphic": {"svc": g.get("svc", ""), "msg": g.get("msg", ""), "baseline": g.get("base", "")}
            if not special else dict(g.get("special") or {}),
            "photo": _photo(g),
            "copy": split_copy(copies["copies"][key]),
            "assignment": _assignment(a),
            "flags": a.get("flags", []),
            "status": status,
            "posted": status == "PUBLICADO",
        })
    n_pub = sum(p["posted"] for p in posts)
    note = ", ".join(f"{s.lower()} ×{sum(p['status'] == s for p in posts)}"
                     for s in ("PUBLICADO", "PROGRAMADO", "DRAFT") if any(p["status"] == s for p in posts))
    return build_month_archive(month, posts, published=n_pub == len(posts),
                               extra={"publication_note": note,
                                      "verify_before_publish": copies.get("verify_before_publish", [])})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", required=True)
    ap.add_argument("--default-status", default="DRAFT", choices=sorted(STATUSES))
    ap.add_argument("--status", action="append", default=[],
                    help="override por pieza, p.ej. 4=PUBLICADO (repetible)")
    ap.add_argument("--length-override", action="append", default=[],
                    help="excepción al tope de caracteres aprobada por MKT, p.ej. '4=motivo' (repetible)")
    ap.add_argument("--out-dir", default=str(REPO / "content" / "archive"))
    args = ap.parse_args()
    overrides = dict(s.split("=", 1) for s in args.status)
    archive = build(args.month, overrides, args.default_status)
    for item in args.length_override:
        key, reason = item.split("=", 1)
        seq = 13 if key == "E" else int(key)
        next(p for p in archive["posts"] if p["seq"] == seq)["length_override"] = reason
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{args.month}.json").write_text(json.dumps(archive, ensure_ascii=False, indent=2) + "\n",
                                            encoding="utf-8")
    (out / f"{args.month}.md").write_text(to_markdown(archive), encoding="utf-8")
    print(f"archive: {args.month} -> {out}/{args.month}.json + .md ({archive['count']} piezas; "
          f"{archive['publication_note']})")
