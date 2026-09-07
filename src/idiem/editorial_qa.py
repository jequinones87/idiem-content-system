"""Editorial QA — control de diversidad editorial de una parrilla (separado del QA factual).

El QA factual (brief/drafting: allowed_facts, claims bloqueados, fuga de hechos,
CONTENT_GAP) sigue intacto y manda. Esta capa evalúa lo OTRO: que el mes no se sienta
repetitivo (arquetipos, CTA, hooks, pains, claims, subtemas, similitud, visual).

Produce hallazgos PASS/WARNING/FAIL con motivos legibles (no True/False), por pieza y
por mes, y un reporte mensual auditable para revisión humana antes de aprobar la grilla.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from .loader import load_editorial_style
from .editorial_fingerprint import ARCHETYPES, CTA_TYPES, VISUAL_THEMES
from .editorial_novelty import (
    ARCHIVE_DIR,
    load_diversity_config,
    load_history,
    load_month_fingerprints,
    novelty_band,
    novelty_score,
    pairwise_near_duplicates,
)

PASS, WARNING, FAIL = "PASS", "WARNING", "FAIL"
_ORDER = {PASS: 0, WARNING: 1, FAIL: 2}


@dataclass
class Finding:
    level: str
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.level}] {self.code}: {self.message}"


@dataclass
class QAReport:
    month: str
    status: str
    findings: list[Finding] = field(default_factory=list)
    summary: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "month": self.month, "status": self.status,
            "findings": [f.__dict__ for f in self.findings],
            "summary": self.summary,
        }


def _worst(findings: list[Finding]) -> str:
    return max((f.level for f in findings), key=lambda l: _ORDER[l], default=PASS)


def load_posts(month: str, archive_dir: Path | None = None) -> list[dict]:
    path = (archive_dir or ARCHIVE_DIR) / f"{month}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("posts", [])


# --- por pieza ---------------------------------------------------------------
def check_piece(post: dict, *, style: dict | None = None) -> list[Finding]:
    style = style or load_editorial_style()
    length = style["length"]
    hard_max = length["hard_max_characters"]
    pref_max = length.get("preferred_max_characters", hard_max)
    cid = post.get("content_id", "?")
    out: list[Finding] = []

    chars = (post.get("copy") or {}).get("chars")
    if chars is None:
        c = post.get("copy") or {}
        chars = len(f"{c.get('hook','')}\n\n{c.get('body','')}\n\n{c.get('cta','')}")
    if chars > hard_max:
        out.append(Finding(FAIL, "char_limit", f"{cid}: {chars} > {hard_max} caracteres (tope duro)."))
    elif chars > pref_max:
        out.append(Finding(WARNING, "char_len", f"{cid}: {chars} car. sobre el rango preferido ({pref_max})."))

    fp = post.get("editorial_fingerprint")
    if not fp:
        out.append(Finding(FAIL, "fingerprint_missing", f"{cid}: sin editorial_fingerprint."))
        return out
    required = ("hook_type", "cta_type", "editorial_archetype", "pain_category", "primary_claim")
    missing = [k for k in required if not fp.get(k)]
    if missing:
        out.append(Finding(FAIL, "fingerprint_incomplete", f"{cid}: faltan campos {missing}."))
    if fp.get("cta_type") not in CTA_TYPES:
        out.append(Finding(FAIL, "cta_invalid", f"{cid}: cta_type inválido {fp.get('cta_type')!r}."))
    if fp.get("editorial_archetype") not in ARCHETYPES:
        out.append(Finding(FAIL, "archetype_invalid", f"{cid}: arquetipo inválido {fp.get('editorial_archetype')!r}."))
    vt = fp.get("visual_theme")
    if vt is not None and vt not in VISUAL_THEMES:
        out.append(Finding(WARNING, "visual_theme_unknown", f"{cid}: visual_theme desconocido {vt!r}."))
    if not out:
        out.append(Finding(PASS, "piece_ok", f"{cid}: pieza válida."))
    return out


# --- por mes -----------------------------------------------------------------
def _concentration(counter: Counter, cap: int, code: str, label: str) -> list[Finding]:
    out = []
    for key, n in counter.items():
        if key and n > cap:
            out.append(Finding(WARNING, code, f"{label} '{key}' se repite {n} veces (máx {cap})."))
    return out


def check_month(month: str, *, posts: list[dict] | None = None,
                style: dict | None = None, config: dict | None = None) -> QAReport:
    cfg = config or load_diversity_config()
    style = style or load_editorial_style()
    posts = posts if posts is not None else load_posts(month)
    findings: list[Finding] = []

    if not posts:
        return QAReport(month, FAIL, [Finding(FAIL, "no_content", f"Sin piezas archivadas para {month}.")])

    # piezas
    for p in posts:
        findings.extend(f for f in check_piece(p, style=style) if f.level != PASS)

    fps = [p.get("editorial_fingerprint") or {} for p in posts]
    d = cfg["diversity"]

    arch = Counter(f.get("editorial_archetype") for f in fps)
    cta = Counter(f.get("cta_type") for f in fps)
    hook = Counter(f.get("hook_type") for f in fps)
    pain = Counter(f.get("pain_category") for f in fps)
    subs = Counter(f.get("subtheme") for f in fps if f.get("subtheme"))
    vis = Counter(f.get("visual_theme") for f in fps if f.get("visual_theme"))
    photos = Counter(f.get("photo_id") for f in fps if f.get("photo_id"))

    findings += _concentration(arch, d["max_same_archetype"], "archetype_concentration", "arquetipo")
    findings += _concentration(cta, d["max_same_cta_type"], "cta_concentration", "cta_type")
    findings += _concentration(hook, d["max_same_hook_type"], "hook_concentration", "hook_type")
    findings += _concentration(pain, d["max_same_pain_point"], "pain_concentration", "pain")
    findings += _concentration(subs, d["max_same_subtheme"], "subtheme_concentration", "subtema")
    findings += _concentration(vis, d["max_same_visual_theme"], "visual_concentration", "visual_theme")

    distinct_arch = len([k for k in arch if k])
    if distinct_arch < d["min_distinct_archetypes"]:
        findings.append(Finding(WARNING, "archetype_diversity_low",
                                f"Solo {distinct_arch} arquetipos distintos (mín {d['min_distinct_archetypes']})."))
    distinct_subs = len(subs)
    if distinct_subs < d["min_distinct_subthemes"]:
        findings.append(Finding(WARNING, "subtheme_diversity_low",
                                f"Solo {distinct_subs} subtemas distintos (mín {d['min_distinct_subthemes']})."))

    # foto repetida dentro del mes
    for pid, n in photos.items():
        if n > 1:
            findings.append(Finding(WARNING, "photo_reuse", f"Foto '{pid}' usada {n} veces en el mes."))

    # foto repetida vs cooldown (meses anteriores). Fail-safe si month no es fecha real.
    cooldown = cfg["cooldown"]["same_photo_months"]
    try:
        hist = load_history(month, window_months=cooldown)
    except Exception:
        hist = []
    hist_photos = {h.get("photo_id") for h in hist if h.get("photo_id")}
    for pid in photos:
        if pid in hist_photos:
            findings.append(Finding(WARNING, "photo_cooldown",
                                    f"Foto '{pid}' reutilizada dentro de {cooldown} meses."))

    # similitud editorial dentro del mes
    for pr in pairwise_near_duplicates(fps, cfg):
        findings.append(Finding(WARNING, "near_duplicate",
                                f"{pr['a']} ↔ {pr['b']}: {', '.join(pr['reasons'])}."))

    summary = {
        "posts": len(posts),
        "archetypes": dict(arch), "cta_types": dict(cta), "hook_types": dict(hook),
        "pain_categories": dict(pain), "visual_themes": dict(vis),
        "distinct_archetypes": distinct_arch, "distinct_subthemes": distinct_subs,
    }
    status = _worst(findings) if findings else PASS
    if not findings:
        findings.append(Finding(PASS, "month_ok", "Sin problemas de diversidad editorial."))
    return QAReport(month, status, findings, summary)


# --- reporte mensual ---------------------------------------------------------
def monthly_editorial_report(month: str, *, posts: list[dict] | None = None) -> str:
    cfg = load_diversity_config()
    posts = posts if posts is not None else load_posts(month)
    report = check_month(month, posts=posts, config=cfg)
    hist = load_history(month)
    fps = [p.get("editorial_fingerprint") or {} for p in posts]

    cells = Counter(p.get("cell_short") or (p.get("cell") or "—") for p in posts)
    services = Counter(f.get("service") or "—" for f in fps)
    bands = Counter()
    for f in fps:
        bands[novelty_band(novelty_score(f, hist, cfg)[0], cfg)] += 1

    L = [f"# Reporte editorial — {month}", "",
         f"**POSTS:** {len(posts)}  ·  **STATUS QA:** {report.status}", ""]

    def block(title, counter):
        L.append(f"## {title}")
        for k, n in counter.most_common():
            L.append(f"- {k}: {n}")
        L.append("")

    block("Distribución por célula", cells)
    block("Distribución por servicio", services)
    block("Arquetipos", Counter(report.summary["archetypes"]))
    block("CTA types", Counter(report.summary["cta_types"]))
    block("Hook types", Counter(report.summary["hook_types"]))
    block("Pain categories", Counter(report.summary["pain_categories"]))
    if report.summary["visual_themes"]:
        block("Visual themes", Counter(report.summary["visual_themes"]))
    L.append("## Novedad vs historial")
    for b in ("high", "medium", "low"):
        L.append(f"- {b}: {bands.get(b, 0)}")
    L.append("")
    L.append("## Hallazgos")
    warns = [f for f in report.findings if f.level != PASS]
    if not warns:
        L.append("- none")
    for f in warns:
        L.append(f"- {f}")
    L.append("")
    return "\n".join(L)


def _cli() -> int:  # pragma: no cover
    import argparse

    ap = argparse.ArgumentParser(description="QA editorial + reporte mensual.")
    ap.add_argument("--month", required=True)
    ap.add_argument("--json", action="store_true", help="Emitir el QAReport como JSON.")
    args = ap.parse_args()
    if args.json:
        print(json.dumps(check_month(args.month).to_dict(), ensure_ascii=False, indent=2))
    else:
        print(monthly_editorial_report(args.month))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_cli())
