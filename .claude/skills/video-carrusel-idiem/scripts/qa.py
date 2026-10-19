#!/usr/bin/env python3
"""Control de calidad del MP4 final (no del HTML): fotogramas clave, hoja de contacto y verificación técnica.

Uso:
    python3 scripts/qa.py salida/mi_video [--video video_musica.mp4] [--originales carpeta_con_laminas/]

Escribe:
    <out>/qa/hoja_transiciones.jpg   fotogramas en cada entrada, a mitad de lámina y en el cierre
    <out>/qa/comparacion.jpg         (si das --originales) lámina original vs. fotograma asentado, lado a lado
y lista en consola lo que hay que revisar a ojo.
"""
import argparse
import json
import pathlib
import re
import subprocess

from PIL import Image, ImageDraw


def frame(video, t, path):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", str(path)], check=True)
    return Image.open(path).convert("RGB")


def sheet(items, cols, w, path):
    rows = (len(items) + cols - 1) // cols
    sh = Image.new("RGB", (cols * w, rows * w), "white")
    for i, (label, im) in enumerate(items):
        im = im.resize((w, w), Image.LANCZOS)
        d = ImageDraw.Draw(im); d.rectangle([0, w - 22, w, w], fill=(0, 0, 0)); d.text((8, w - 18), label, fill=(255, 230, 0))
        sh.paste(im, ((i % cols) * w, (i // cols) * w))
    sh.save(path, quality=90)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir")
    ap.add_argument("--video", default=None)
    ap.add_argument("--originales", default=None)
    a = ap.parse_args()
    out = pathlib.Path(a.outdir); qa = out / "qa"; qa.mkdir(exist_ok=True)
    tl = json.loads((out / "timeline.json").read_text())
    video = out / (a.video or ("video_musica.mp4" if (out / "video_musica.mp4").exists() else "video.mp4"))

    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate:format=duration",
                            "-of", "json", str(video)], capture_output=True, text=True)
    info = json.loads(probe.stdout)
    v = [s for s in info["streams"] if s["codec_type"] == "video"][0]
    aud = [s for s in info["streams"] if s["codec_type"] == "audio"]
    dur = float(info["format"]["duration"])
    checks = [
        ("Resolución 1080×1080", v["width"] == 1080 and v["height"] == 1080),
        ("Códec H.264", v["codec_name"] == "h264"),
        ("30 fps", v["r_frame_rate"] == "30/1"),
        (f"Duración {dur:.2f} s = línea de tiempo {tl['duration']:.2f} s", abs(dur - tl["duration"]) < 0.1),
    ]
    if aud:
        meas = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"],
                              capture_output=True, text=True).stderr
        I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", meas)[-1]); pk = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", meas)[-1])
        checks += [(f"Audio AAC · {I:.1f} LUFS (objetivo −17 ±1)", aud[0]["codec_name"] == "aac" and abs(I + 17) <= 1.0),
                   (f"Pico de audio {pk:.1f} dBTP (≤ −1)", pk <= -1.0)]

    cuts, step, cover, close = tl["cuts"], tl["step"], tl["cover"], tl["close_at"]
    pts = [("portada 1,2 s", 1.2), (f"portada {cover-0.2:.1f} s", cover - 0.2)]
    for k in range(tl["steps"]):
        t0 = cuts[k]
        pts += [(f"L{k+1:02d} entrando", t0 + 0.6), (f"L{k+1:02d} asentada", t0 + step / 2)]
    pts += [("cierre entrando", close + 0.5), ("cierre +2,5 s", close + 2.5), ("último cuadro", tl["duration"] - 0.05)]
    items = [(f"{lab} · {t:.2f}s", frame(video, t, qa / f"f_{i:02d}.png")) for i, (lab, t) in enumerate(pts)]
    sheet(items, 4, 360, qa / "hoja_transiciones.jpg")

    if a.originales:
        origs = sorted(p for p in pathlib.Path(a.originales).iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg"))
        mids = [cover - 0.8] + [cuts[k] + step / 2 for k in range(tl["steps"])] + [tl["duration"] - 0.05]
        pairs = []
        for i, (o, t) in enumerate(zip(origs, mids)):
            pairs += [(f"original {o.name}", Image.open(o).convert("RGB")), (f"video {t:.2f}s", frame(video, t, qa / f"c_{i:02d}.png"))]
        sheet(pairs, 4, 400, qa / "comparacion.jpg")

    print(f"QA de {video}")
    for name, ok in checks:
        print(("  ✔ " if ok else "  ✘ ") + name)
    print(f"  → Revisa a ojo {qa/'hoja_transiciones.jpg'}" + (f" y {qa/'comparacion.jpg'}" if a.originales else ""))
    print("    textos idénticos a las láminas · nada cortado ni fuera del margen de 60 px · íconos sin puntos sueltos ·\n"
          "    sin cuadros vacíos > 0,3 s · logo y número no parpadean entre láminas · el video termina sobre el logo")
    if not all(ok for _, ok in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
