"""Editorial novelty engine — diversidad editorial más allá de la taxonómica.

Distingue:
  * diversidad TAXONÓMICA (distinto knowledge_id / servicio / subtema), y
  * diversidad EDITORIAL (distinto claim / pain / hook / arquetipo / CTA / enfoque).

Compara una pieza candidata contra el historial reciente (ventana configurable de
meses, leída de ``content/archive/``) y produce un score de novedad determinista y
auditable, más un resumen del historial para el redactor. NUNCA es fuente de hechos:
el historial sirve para EVITAR REPETICIÓN, no para afirmar.

Sin dependencias externas ni embeddings: similitud local (Jaccard de tokens
normalizados) + comparación de dimensiones de la huella + equivalencia estructural
(mismo pain+hook+arquetipo+CTA => editorialmente cercano aunque cambie el vocabulario).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Optional

from .loader import CONFIG_DIR, REPO_ROOT
from .editorial_fingerprint import (
    EditorialFingerprint,
    fingerprint_archive_post,
    tokens,
)

ARCHIVE_DIR = REPO_ROOT / "content" / "archive"
DIVERSITY_CONFIG = CONFIG_DIR / "editorial_diversity.json"


def load_diversity_config(path: Path | None = None) -> dict:
    with (path or DIVERSITY_CONFIG).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _as_dict(fp) -> dict:
    return fp.to_dict() if isinstance(fp, EditorialFingerprint) else dict(fp)


# --- historial ---------------------------------------------------------------
def previous_months(month: str, n: int) -> list[str]:
    year, mon = (int(x) for x in month.split("-"))
    out: list[str] = []
    for _ in range(n):
        mon -= 1
        if mon == 0:
            mon, year = 12, year - 1
        out.append(f"{year:04d}-{mon:02d}")
    return out


def load_month_fingerprints(month: str, archive_dir: Path | None = None) -> list[dict]:
    """Fingerprints de un mes archivado (usa los guardados o los computa)."""
    path = (archive_dir or ARCHIVE_DIR) / f"{month}.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    out: list[dict] = []
    for p in data.get("posts", []):
        fp = p.get("editorial_fingerprint") or fingerprint_archive_post(p).to_dict()
        out.append(fp)
    return out


def load_history(month: str, window_months: int | None = None,
                 archive_dir: Path | None = None) -> list[dict]:
    """Fingerprints de los ``window_months`` meses anteriores a ``month``."""
    if window_months is None:
        window_months = load_diversity_config().get("history_window_months", 3)
    hist: list[dict] = []
    for m in previous_months(month, window_months):
        hist.extend(load_month_fingerprints(m, archive_dir))
    return hist


def editorial_history_summary(history: Iterable[dict], *, top: int = 24) -> dict:
    """Resumen compacto para el redactor (EVITAR REPETICIÓN, no es fuente de hechos)."""
    fps = [_as_dict(f) for f in history]

    def uniq(seq):
        seen, out = set(), []
        for x in seq:
            if x and x not in seen:
                seen.add(x); out.append(x)
        return out

    return {
        "recent_subthemes": uniq(f.get("subtheme") for f in fps)[:top],
        "recent_claims": uniq(f.get("primary_claim") for f in fps)[:top],
        "recent_pain_points": uniq(f.get("pain_point") for f in fps)[:top],
        "recent_pain_categories": uniq(f.get("pain_category") for f in fps)[:top],
        "recent_hooks": uniq(f.get("pain_point") for f in fps)[:top],
        "recent_hook_types": uniq(f.get("hook_type") for f in fps),
        "recent_archetypes": uniq(f.get("editorial_archetype") for f in fps),
        "recent_cta_types": uniq(f.get("cta_type") for f in fps),
        "recent_knowledge_ids": uniq(f.get("knowledge_id") for f in fps),
        "recent_phrases_to_avoid": uniq(f.get("primary_claim") for f in fps)[:12],
    }


# --- similitud ---------------------------------------------------------------
def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _claim_tokens(fp: dict) -> set[str]:
    return tokens(f"{fp.get('primary_claim','')} {fp.get('subtheme','')}")


def _pain_tokens(fp: dict) -> set[str]:
    return tokens(fp.get("pain_point", ""))


def structural_signature(fp: dict) -> tuple:
    """Firma estructural: mismo pain+hook+arquetipo+CTA => editorialmente cercano."""
    fp = _as_dict(fp)
    return (fp.get("pain_category"), fp.get("hook_type"),
            fp.get("editorial_archetype"), fp.get("cta_type"))


# --- novedad -----------------------------------------------------------------
def novelty_score(candidate, history: Iterable[dict],
                  config: dict | None = None) -> tuple[float, list[str]]:
    """Score de novedad en [0,1] (1 = totalmente novedoso) + razones de penalización."""
    cfg = config or load_diversity_config()
    w = cfg["novelty_weights"]
    sim = cfg["similarity"]
    c = _as_dict(candidate)
    hist = [_as_dict(h) for h in history]
    if not hist:
        return 1.0, []

    reasons: list[str] = []
    penalty = 0.0
    max_penalty = sum(v for k, v in w.items() if not k.startswith("_"))

    def hit(dim, cond, detail):
        nonlocal penalty
        if cond:
            penalty += w[dim]
            reasons.append(f"{dim}: {detail}")

    hist_kids = {h.get("knowledge_id") for h in hist}
    hist_subs = {h.get("subtheme") for h in hist if h.get("subtheme")}
    hist_hooktypes = [h.get("hook_type") for h in hist]
    hist_arch = [h.get("editorial_archetype") for h in hist]
    hist_cta = [h.get("cta_type") for h in hist]
    hist_pain = [h.get("pain_category") for h in hist]
    hist_vis = [h.get("visual_theme") for h in hist]

    hit("knowledge_id", c.get("knowledge_id") in hist_kids and c.get("knowledge_id"),
        f"{c.get('knowledge_id')} ya usado")
    hit("subtheme", c.get("subtheme") in hist_subs and c.get("subtheme"),
        f"subtema '{c.get('subtheme')}' ya usado")
    hit("hook_type", c.get("hook_type") in hist_hooktypes, f"hook_type={c.get('hook_type')}")
    hit("editorial_archetype", c.get("editorial_archetype") in hist_arch,
        f"arquetipo={c.get('editorial_archetype')}")
    hit("cta_type", c.get("cta_type") in hist_cta, f"cta_type={c.get('cta_type')}")
    hit("pain_point", c.get("pain_category") in hist_pain, f"pain={c.get('pain_category')}")
    hit("visual_theme", c.get("visual_theme") and c.get("visual_theme") in hist_vis,
        f"visual={c.get('visual_theme')}")

    ct = _claim_tokens(c)
    max_claim = max((jaccard(ct, _claim_tokens(h)) for h in hist), default=0.0)
    hit("copy_similarity", max_claim >= sim["near_duplicate_claim"],
        f"claim similar a histórico (jaccard={max_claim:.2f})")

    score = max(0.0, 1.0 - (penalty / max_penalty)) if max_penalty else 1.0
    return round(score, 3), reasons


def novelty_band(score: float, config: dict | None = None) -> str:
    bands = (config or load_diversity_config())["novelty_bands"]
    if score >= bands["high"]:
        return "high"
    if score >= bands["medium"]:
        return "medium"
    return "low"


def near_duplicates(candidate, others: Iterable[dict],
                    config: dict | None = None) -> list[dict]:
    """Piezas de ``others`` editorialmente cercanas a ``candidate``."""
    cfg = config or load_diversity_config()
    sim = cfg["similarity"]
    c = _as_dict(candidate)
    csig = structural_signature(c)
    ct, cp = _claim_tokens(c), _pain_tokens(c)
    out: list[dict] = []
    for o in others:
        o = _as_dict(o)
        if o.get("content_id") and o.get("content_id") == c.get("content_id"):
            continue
        claim_s = jaccard(ct, _claim_tokens(o))
        pain_s = jaccard(cp, _pain_tokens(o))
        shared_struct = structural_signature(o) == csig
        reasons = []
        if claim_s >= sim["near_duplicate_claim"]:
            reasons.append(f"claim similarity={claim_s:.2f}")
        if pain_s >= sim["near_duplicate_pain"]:
            reasons.append(f"pain similarity={pain_s:.2f}")
        if shared_struct:
            reasons.append(f"misma firma estructural {csig}")
        if reasons:
            out.append({"content_id": o.get("content_id"), "reasons": reasons,
                        "claim_similarity": round(claim_s, 2),
                        "pain_similarity": round(pain_s, 2),
                        "shared_structure": shared_struct})
    return out


def pairwise_near_duplicates(fingerprints: list[dict],
                             config: dict | None = None) -> list[dict]:
    """Pares editorialmente cercanos dentro de un conjunto (p.ej. un mes)."""
    cfg = config or load_diversity_config()
    fps = [_as_dict(f) for f in fingerprints]
    pairs: list[dict] = []
    for i in range(len(fps)):
        for j in range(i + 1, len(fps)):
            hits = near_duplicates(fps[i], [fps[j]], cfg)
            if hits:
                h = hits[0]
                pairs.append({"a": fps[i].get("content_id"), "b": fps[j].get("content_id"),
                              **{k: h[k] for k in ("reasons", "claim_similarity",
                                                   "pain_similarity", "shared_structure")}})
    return pairs


def select_diverse(candidates: list[dict], k: int, history: Iterable[dict] | None = None,
                   config: dict | None = None) -> list[dict]:
    """Selección greedy de ``k`` candidatos que maximiza novedad vs historial y
    diversidad intra-selección. Reutilizable por el planner (pool -> selección).

    NO inventa candidatos: si hay menos de ``k`` válidos, devuelve los que haya.
    """
    cfg = config or load_diversity_config()
    hist = [_as_dict(h) for h in (history or [])]
    pool = [_as_dict(c) for c in candidates]
    chosen: list[dict] = []
    while pool and len(chosen) < k:
        best, best_score = None, -1.0
        for cand in pool:
            score, _ = novelty_score(cand, hist + chosen, cfg)
            if score > best_score:
                best, best_score = cand, score
        chosen.append(best)
        pool.remove(best)
    return chosen
