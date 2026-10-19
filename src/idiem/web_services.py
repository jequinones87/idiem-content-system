"""Registro de servicios publicados en www.idiem.cl/servicios (evidencia auxiliar candidata).

El sitio web NO es fuente de verdad: la librería 2A.2 (data/) manda. Cada servicio extraído
entra como ``VERIFY`` (decisión MKT 19-10-2026) y solo puede citarse como ``auxiliary_id``
(``WEB-xxx``) después de que MKT lo valide (campo ``validated_by``).

Jerarquía del sitio:
  categoria  /servicios/<cat>                       (descripción en /servicios)
  area       /servicios/<cat>/<area>                (h4 + párrafos)
  servicio   /servicios/<cat>/<area>/<servicio>     (h4 + párrafos + prestaciones)

Re-extracción auditable: los IDs se conservan por ruta; si el texto de un servicio cambia,
su validación se borra y vuelve a ``VERIFY`` (fail closed).

Uso:
    python -m idiem.web_services            # extrae y escribe config/topic_bank/web_services.json
    python -m idiem.web_services --cache DIR  # guarda/reutiliza el HTML descargado en DIR
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

from .loader import REPO_ROOT

BASE = "https://www.idiem.cl"
INDEX_PATH = "/servicios"
REGISTRY = REPO_ROOT / "config" / "topic_bank" / "web_services.json"
USER_AGENT = "idiem-content-system/1.0 (registro interno de servicios)"
DELAY_S = 0.5

LEVELS = {2: "categoria", 3: "area", 4: "servicio"}

# Textos promocionales que no pasan al copy (voz de marca sin superlativos; CLAUDE.md regla 6).
PROMO_PATTERNS = [
    r"alt[oa]s? est[aá]ndar(es)?", r"alta tecnolog[ií]a", r"alta especializaci[oó]n",
    r"\bl[ií]der(es)?\b", r"\b[uú]nic[oa]s?\b", r"\bmejor(es)?\b", r"de excelencia",
    r"vanguardia", r"todo (de )?tipo", r"gran parte", r"gran variedad", r"\bprincipales?\b",
]
# Afirmaciones que necesitan respaldo propio (acreditaciones, certificaciones, normas).
CLAIM_PATTERNS = [r"certific\w*", r"acredit\w*", r"\bnorma\w*", r"\bISO\b", r"\bINN\b"]

_BLOCK_TAGS = {"h3", "h4", "p", "label", "li"}


class _Page(HTMLParser):
    """Recolecta bloques de texto (tag, texto) y enlaces /servicios/... de una página."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[tuple[str, str]] = []
        self.links: list[str] = []
        self._skip = 0
        self._stack: list[list] = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "svg"):
            self._skip += 1
            return
        if tag == "a":
            href = dict(attrs).get("href") or ""
            if href.startswith(INDEX_PATH + "/"):
                link = href.split("?")[0].split("#")[0].rstrip("/")
                self.links.append(link)
                self.blocks.append(("a", link))
        if tag in _BLOCK_TAGS:
            self._stack.append([tag, []])

    def handle_endtag(self, tag):
        if tag in ("script", "style", "svg"):
            self._skip = max(0, self._skip - 1)
            return
        if tag in _BLOCK_TAGS and self._stack and self._stack[-1][0] == tag:
            t, parts = self._stack.pop()
            text = _clean("".join(parts))
            if text:
                self.blocks.append((t, text))

    def handle_data(self, data):
        if not self._skip and self._stack:
            self._stack[-1][1].append(data)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _parse(html: str) -> _Page:
    p = _Page()
    p.feed(html)
    return p


def fetch(path: str, cache: Path | None = None) -> str:
    if cache:
        f = cache / (path.strip("/").replace("/", "__") + ".html")
        if f.exists():
            return f.read_text("utf-8")
    req = urllib.request.Request(BASE + path, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8")
    time.sleep(DELAY_S)
    if cache:
        cache.mkdir(parents=True, exist_ok=True)
        f.write_text(html, "utf-8")
    return html


# --- extracción por página --------------------------------------------------------------

_END_MARKERS = ("¿Tienes dudas", "Partners", "help_outline")


def parse_detail(html: str) -> dict:
    """Área o servicio: h4 título, párrafos de descripción y prestaciones (checkbox labels).

    El contenido vive en la columna principal (``col-lg-9``); la barra lateral solo trae enlaces.
    """
    i = html.find('class="col-lg-9"')
    if i < 0:
        raise ValueError("página sin columna de contenido (col-lg-9)")
    page = _parse(html[i:])
    title, description, offerings = None, [], []
    for tag, text in page.blocks:
        if tag == "a":
            continue
        if any(text.startswith(m) or m in text[:20] for m in _END_MARKERS):
            break
        if tag == "h4" and title is None:
            title = text
        elif tag == "p" and title is not None:
            description.append(text)
        elif tag == "label" and title is not None:
            offerings.append(text)
    if not title:
        raise ValueError("página sin título (h4)")
    return {"title": title, "description": description, "offerings": offerings}


def parse_index(html: str) -> dict[str, dict]:
    """/servicios: cada categoría es un h3 + párrafos hasta 'Ver más'; el enlace
    'Ver especialidades' que sigue indica su ruta. Devuelve {ruta: {title, description}}."""
    page = _parse(html)
    out: dict[str, dict] = {}
    current, collecting = None, False
    for tag, text in page.blocks:
        if tag == "h3":
            current, collecting = {"title": text, "description": []}, True
        elif tag == "p" and current is not None and collecting:
            if text == "Ver más":
                collecting = False
            else:
                current["description"].append(text)
        elif tag == "a" and current is not None and text.count("/") == 2:
            out.setdefault(text, current)
            current = None
    return out


def _children(html: str, path: str) -> list[str]:
    depth = path.count("/") + 1
    return sorted({h for h in _parse(html).links if h.startswith(path + "/") and h.count("/") == depth})


def _flags(texts: list[str], patterns: list[str]) -> list[str]:
    found = []
    for t in texts:
        for pat in patterns:
            for m in re.finditer(pat, t, flags=re.I):
                found.append(m.group(0))
    return sorted(set(found), key=str.lower)


def _hash(item: dict) -> str:
    payload = json.dumps([item["title"], item["description"], item["offerings"]], ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


# --- crawl ------------------------------------------------------------------------------


def crawl(cache: Path | None = None) -> list[dict]:
    index_html = fetch(INDEX_PATH, cache)
    index_desc = parse_index(index_html)
    categories = sorted(index_desc)

    items: list[dict] = []
    queue = list(categories)
    seen: set[str] = set()
    while queue:
        path = queue.pop(0)
        if path in seen:
            continue
        seen.add(path)
        html = fetch(path, cache)
        level = LEVELS[path.count("/")]
        if level == "categoria":
            # La página de categoría no siempre trae título/descripción; manda /servicios.
            if path not in index_desc:
                raise ValueError(f"{path}: categoría sin descripción en {INDEX_PATH}")
            detail = {**index_desc[path], "offerings": []}
        else:
            detail = parse_detail(html)
        items.append({"path": path, "level": level, "parent": path.rsplit("/", 1)[0]
                      if level != "categoria" else None, **detail})
        if level != "servicio":
            queue.extend(c for c in _children(html, path) if c not in seen)
    return items


# --- registro ---------------------------------------------------------------------------

RULES = {
    "hierarchy": "2A.2 (knowledge_id) manda. www.idiem.cl es evidencia auxiliar CANDIDATA; no se copia a data/ ni crea capacidades técnicas nuevas (CLAUDE.md reglas 1, 2 y 7).",
    "classification": "Todo servicio WEB-* entra como VERIFY (MKT 19-10-2026). Solo con validated_by se cita como auxiliary_id (WEB-xxx) en briefs y copies.",
    "promo_flags": "Los textos en promo_flags son promocionales/superlativos: no pasan al copy aunque el servicio esté validado (voz de marca sin superlativos).",
    "claim_flags": "Menciones de certificación, acreditación o normas: requieren respaldo en 2A.2 o validación específica antes de afirmarse.",
    "cells": "El sitio no asigna célula. La célula se decide con config/cell_rules.json al usar el servicio; nunca se mueve conocimiento entre células para cubrir cuota (regla 9). Transporte sigue en CONTENT_GAP.",
    "recrawl": "Al re-extraer, los IDs se conservan por ruta. Si el texto cambia (content_hash), la validación se borra y el servicio vuelve a VERIFY.",
    "duplicates": "El sitio repite áreas bajo varias categorías; same_text_as apunta al primer WEB-* con el mismo texto.",
}


def build_registry(items: list[dict], previous: dict | None = None, today: str | None = None) -> dict:
    prev_by_path = {x["path"]: x for x in (previous or {}).get("services", [])}
    next_n = 1 + max((int(x["id"][4:]) for x in prev_by_path.values()), default=0)
    by_hash: dict[str, str] = {}
    path_to_id: dict[str, str] = {}
    services = []
    for it in items:  # crawl en anchura: el padre siempre precede al hijo
        old = prev_by_path.get(it["path"])
        if old:
            wid = old["id"]
        else:
            wid = f"WEB-{next_n:03d}"
            next_n += 1
        path_to_id[it["path"]] = wid
        h = _hash(it)
        texts = [it["title"], *it["description"], *it["offerings"]]
        rec = {
            "id": wid,
            "level": it["level"],
            "path": it["path"],
            "url": BASE + it["path"],
            "parent_id": path_to_id[it["parent"]] if it["parent"] else None,
            "title": it["title"],
            "description": it["description"],
            "offerings": it["offerings"],
            "class": "VERIFY",
            "promo_flags": _flags(texts, PROMO_PATTERNS),
            "claim_flags": _flags(texts, CLAIM_PATTERNS),
            "content_hash": h,
        }
        if h in by_hash:
            rec["same_text_as"] = by_hash[h]
        else:
            by_hash[h] = wid
        if old and old.get("content_hash") == h and old.get("validated_by"):
            rec["validated_by"] = old["validated_by"]
            rec["validated_on"] = old.get("validated_on")
        services.append(rec)
    services.sort(key=lambda r: r["id"])
    return {
        "version": 1,
        "extracted_on": today or date.today().isoformat(),
        "source": BASE + INDEX_PATH,
        "description": "Servicios publicados en el sitio de IDIEM, texto literal. Complementa 2A.2 sin reemplazarla.",
        "rules": RULES,
        "counts": {lvl: sum(1 for s in services if s["level"] == lvl) for lvl in LEVELS.values()},
        "services": services,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cache", type=Path, help="directorio para guardar/reutilizar HTML")
    ap.add_argument("--out", type=Path, default=REGISTRY)
    args = ap.parse_args(argv)
    previous = json.loads(args.out.read_text("utf-8")) if args.out.exists() else None
    registry = build_registry(crawl(args.cache), previous)
    args.out.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(json.dumps(registry["counts"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
