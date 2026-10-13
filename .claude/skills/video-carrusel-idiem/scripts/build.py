#!/usr/bin/env python3
"""Arma el HTML animado a partir de un JSON de configuración.

Uso:
    python3 scripts/build.py config/mi_video.json --out salida/mi_video

Genera:
    <out>/video.html      reproducible en el navegador y capturable cuadro a cuadro
    <out>/timeline.json   tiempos de cada corte (los usa music.py y qa.py)
"""
import argparse
import base64
import json
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SHAPES = ("path", "line", "circle", "rect", "polyline", "polygon", "ellipse")


def b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode()


def icon_svg(name):
    p = ASSETS / "icons" / f"{name}.svg"
    if not p.exists():
        disponibles = sorted(x.stem for x in (ASSETS / "icons").glob("*.svg"))
        sys.exit(f"Ícono '{name}' no existe. Disponibles: {', '.join(disponibles)}\n"
                 "Para agregar otro: copia el SVG de lucide.dev (trazo, sin relleno) en assets/icons/.")
    s = p.read_text(encoding="utf-8")
    inner = re.search(r"<svg[^>]*>(.*)</svg>", s, re.S).group(1)
    inner = re.sub(r"<!--.*?-->", "", inner, flags=re.S).strip()
    # pathLength="1" en cada trazo permite dibujarlo con stroke-dashoffset 1 → 0
    inner = re.sub(r"<(%s)\b(?![^>]*pathLength)" % "|".join(SHAPES), r'<\1 pathLength="1"', inner)
    return f'<svg viewBox="0 0 24 24">{inner}</svg>'


def round_half(x):
    return math.floor(x * 2 + 0.5) / 2


def words(s):
    return len(re.findall(r"\w+", s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cfg_path = pathlib.Path(a.config).resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    steps = cfg["steps"]
    if not 1 <= len(steps) <= 9:
        sys.exit("Se esperan entre 1 y 9 láminas interiores.")

    # ---- tiempos: todo en múltiplos de 0,5 s para que cada corte caiga en un pulso a 120 BPM ----
    t = cfg.get("timing", {})
    cover = round_half(t.get("cover", 4.0))
    if "step" in t:
        step = round_half(t["step"])
    else:
        mx = max(words(" ".join(s["title"])) + words(" ".join(s["body"])) for s in steps)
        step = min(9.0, max(5.5, round_half(1.6 + mx / 4.4)))  # ≈ 260 palabras/min + entrada de 1,6 s
    close = round_half(t.get("close", 6.0))
    total = cover + step * len(steps) + close
    close += (2 - total % 2) % 2  # duración total múltiplo de un compás (2 s)
    total = cover + step * len(steps) + close
    timing = {"cover": cover, "step": step, "close": close}

    # ---- foto ----
    photo = cfg["photo"]
    ppath = (cfg_path.parent / photo["file"]).resolve()
    if not ppath.exists():
        sys.exit(f"No encuentro la foto: {ppath}")
    mime = "image/png" if ppath.suffix.lower() == ".png" else "image/jpeg"
    photo_uri = f"data:{mime};base64,{b64(ppath)}"

    data = {
        "timing": timing,
        "photo": {"focus": photo.get("focus", "50% 50%"), "zoom": photo.get("zoom", 1.10), "glow": photo.get("glow")},
        "cover": cfg["cover"],
        "steps": [{"title": s["title"], "body": s["body"], "iconSvg": icon_svg(s["icon"])} for s in steps],
        "closing": cfg["closing"],
    }

    html = (ROOT / "template" / "video_template.html").read_text(encoding="utf-8")
    logo = (ASSETS / "logo_idiem_blanco.svg").read_text(encoding="utf-8")
    rep = {
        "__TITLE__": cfg.get("name", "Video IDIEM"),
        "__FONT400__": b64(ASSETS / "montserrat-400.woff2"),
        "__FONT700__": b64(ASSETS / "montserrat-700.woff2"),
        "__SLOGAN__": b64(ASSETS / "eslogan_alfa.png"),
        "__LOGO__": logo,
        "__PHOTO__": photo_uri,
        "__CONFIG__": json.dumps(data, ensure_ascii=False),
    }
    for k, v in rep.items():
        html = html.replace(k, v)
    (out / "video.html").write_text(html, encoding="utf-8")

    cuts = [cover + step * k for k in range(len(steps) + 1)]
    tl = {"duration": total, "cover": cover, "step": step, "steps": len(steps), "close_at": cuts[-1],
          "cuts": cuts, "bpm": 120}
    (out / "timeline.json").write_text(json.dumps(tl, indent=2), encoding="utf-8")
    print(f"OK  {out/'video.html'}  ·  duración {total:.1f} s  ·  portada {cover} s  ·  {len(steps)} láminas × {step} s  ·  cierre {close} s")


if __name__ == "__main__":
    main()
