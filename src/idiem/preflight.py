"""Verificación previa a producir contenido (CLAUDE.md § Antes de producir).

Responde, sin modificar nada, a las tres preguntas que evitan proponer piezas desalineadas:
  1. ¿Hay ramas remotas con trabajo que esta rama todavía no integra? (decisiones de MKT,
     workstations o fuentes que no veo si no las fusiono)
  2. ¿Qué workstations y métodos vigentes hay? (config/production_registry.json)
  3. ¿Cuál es el siguiente ID libre de fuente (SRC) y tema (TOP), contando todas las ramas?

Uso:
  python -m idiem.preflight            # informe completo (hace `git fetch`)
  python -m idiem.preflight --brief    # resumen corto (lo usa el hook de inicio de sesión)
  python -m idiem.preflight --no-fetch # sin red
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "config" / "production_registry.json"
BANK = "config/topic_bank/expert_sources.json"


def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True,
                              timeout=60).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def pending_branches() -> list[dict]:
    """Ramas remotas con commits que HEAD no contiene (excluye main vacía y la rama propia)."""
    head = _git("rev-parse", "--abbrev-ref", "HEAD")
    out = []
    for ref in _git("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin").splitlines():
        name = ref.removeprefix("origin/")
        if name in ("HEAD", "main", head) or ref == "origin":
            continue
        n = _git("rev-list", "--count", f"HEAD..{ref}")
        if n and n != "0":
            last = _git("log", "-1", "--format=%cd · %s", "--date=short", ref)
            out.append({"branch": name, "commits": int(n), "last": last})
    return sorted(out, key=lambda b: b["last"], reverse=True)


def _ids_in(text: str, prefix: str) -> set[int]:
    return {int(m) for m in re.findall(rf'"id":\s*"{prefix}-(\d{{3}})"', text)}


def next_ids() -> dict:
    """Máximo SRC/TOP usado en HEAD y en todas las ramas remotas → siguiente ID libre."""
    texts = [(ROOT / BANK).read_text("utf-8") if (ROOT / BANK).exists() else ""]
    for ref in _git("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin").splitlines():
        texts.append(_git("show", f"{ref}:{BANK}"))
    src = set().union(*(_ids_in(t, "SRC") for t in texts))
    top = set().union(*(_ids_in(t, "TOP") for t in texts))
    return {"SRC": f"SRC-{max(src, default=0) + 1:03d}", "TOP": f"TOP-{max(top, default=0) + 1:03d}"}


def report(brief: bool = False, fetch: bool = True) -> str:
    if fetch:
        _git("fetch", "-q", "origin")
    reg = json.loads(REGISTRY.read_text("utf-8"))
    lines = ["IDIEM · verificación previa (docs/14_PLAYBOOK_PRODUCCION.md)"]
    pend = pending_branches()
    if pend:
        lines.append(f"⚠ {len(pend)} rama(s) con trabajo NO integrado en esta rama — revisar/fusionar antes de producir:")
        lines += [f"   - {b['branch']} (+{b['commits']}) · {b['last']}" for b in pend]
    else:
        lines.append("✔ Esta rama contiene el trabajo de todas las ramas remotas.")
    ids = next_ids()
    lines.append(f"Siguientes IDs libres (todas las ramas): {ids['SRC']} · {ids['TOP']}")
    if brief:
        lines.append("Antes de producir: leer docs/14_PLAYBOOK_PRODUCCION.md y el workstation de los 2 últimos meses.")
        return "\n".join(lines)
    lines.append(f"Rama de integración: {reg['integration']['branch']}")
    lines.append("Workstations registrados:")
    lines += [f"   - {w['id']:<26} {w['status']:<32} {w['url']}" for w in reg["workstations"]]
    lines.append("Métodos vigentes:")
    for k, m in reg["methods"].items():
        lines.append(f"   - {k}: {m.get('template') or m.get('tool') or m.get('rule')}")
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", action="store_true")
    ap.add_argument("--no-fetch", action="store_true")
    a = ap.parse_args()
    print(report(brief=a.brief, fetch=not a.no_fetch))
