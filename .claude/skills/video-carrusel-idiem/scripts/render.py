#!/usr/bin/env python3
"""Captura el HTML cuadro a cuadro (Chromium headless vía Playwright) y codifica el MP4.

Uso:
    python3 scripts/render.py salida/mi_video [--fps 30] [--workers 4] [--music salida/mi_video/music.wav]

Nunca grabar la pantalla en tiempo real: cada cuadro se dibuja con window.seek(t) y se captura,
así no hay saltos ni cuadros perdidos aunque la máquina sea lenta.
"""
import argparse
import asyncio
import json
import os
import pathlib
import shutil
import subprocess
import sys

from playwright.async_api import async_playwright


async def open_page(p, html):
    # PW_CHROMIUM: Chromium ya instalado (p. ej. /opt/pw-browsers/chromium en sesiones cloud)
    b = await p.chromium.launch(executable_path=os.environ.get("PW_CHROMIUM") or None)
    pg = await b.new_page(viewport={"width": 1080, "height": 1080})
    await pg.goto(html.resolve().as_uri() + "?capture")
    await pg.evaluate("document.fonts.ready")
    ok = await pg.evaluate("[...document.fonts].filter(f => f.family.includes('Montserrat') && f.status === 'loaded').length")
    if ok < 2:
        raise SystemExit("Montserrat no cargó: el video saldría con una fuente de reemplazo. Revisa assets/.")
    return b, pg


async def worker(p, html, frames_dir, idx, n, fps, workers):
    b, pg = await open_page(p, html)
    for f in range(idx, n, workers):
        await pg.evaluate("t => window.seek(t)", f / fps)
        await pg.screenshot(path=str(frames_dir / f"{f:05d}.png"))
    await b.close()


async def run(html, frames_dir, fps, workers):
    async with async_playwright() as p:
        b, pg = await open_page(p, html)
        bad = await pg.evaluate("window.checkLayout()")
        dur = await pg.evaluate("window.DUR")
        await b.close()
        if bad:
            print("ERROR de diagramación (corrige el JSON antes de renderizar):")
            for x in bad:
                print("  -", x)
            sys.exit(2)
        n = int(round(dur * fps))
        await asyncio.gather(*[worker(p, html, frames_dir, i, n, fps, workers) for i in range(workers)])
        return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--music", help="WAV para mezclar (opcional); se genera con scripts/music.py")
    a = ap.parse_args()
    out = pathlib.Path(a.outdir)
    html = out / "video.html"
    frames = out / "frames"
    shutil.rmtree(frames, ignore_errors=True)
    frames.mkdir(parents=True)
    n = asyncio.run(run(html, frames, a.fps, a.workers))
    mp4 = out / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(a.fps), "-i", str(frames / "%05d.png"),
                    "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-profile:v", "high",
                    "-movflags", "+faststart", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    str(mp4)], check=True)
    print(f"OK  {mp4}  ({n} cuadros a {a.fps} fps)")
    if a.music:
        mp4m = out / "video_musica.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-i", a.music, "-map", "0:v:0", "-map", "1:a:0",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", str(mp4m)],
                       check=True)
        print(f"OK  {mp4m}")
    shutil.rmtree(frames, ignore_errors=True)


if __name__ == "__main__":
    main()
