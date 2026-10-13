"""Carrusel → video MP4 para redes (formato de prueba, desde noviembre 2026).

Usa las MISMAS láminas renderizadas del carrusel (misma gráfica e información):
cada lámina se mantiene en pantalla el tiempo suficiente para leerla, con un zoom
muy leve (efecto Ken Burns) y fundidos cruzados entre láminas. Música de fondo
chill house sutil, sintetizada en `music_chill.py` (sin licencias de terceros).

Salida: H.264 + AAC, yuv420p, 1080x1080, 30 fps (compatible con LinkedIn/Instagram).

Uso:
  python3 design_system/gen_carousel_video.py out.mp4 lam0.png lam1.png ... \
      [--holds 3.5,4.5,...] [--music-volume 0.35]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import music_chill  # noqa: E402

FPS = 30
SIZE = 1080
FADE = 0.6       # s de fundido cruzado entre láminas
ZOOM = 0.035     # zoom total por lámina (3,5 %)


def default_holds(n: int) -> list[float]:
    """Portada 3.5 s, intermedias 4.5 s (bajada de 2–4 líneas), cierre 4 s."""
    return [3.5] + [4.5] * (n - 2) + [4.0] if n > 1 else [4.0]


def frame_at(img: Image.Image, p: float) -> Image.Image:
    """Lámina con zoom leve centrado; p en [0,1] a lo largo de su tiempo en pantalla."""
    z = 1 + ZOOM * p
    w = int(round(SIZE * z))
    big = img.resize((w, w), Image.LANCZOS)
    o = (w - SIZE) // 2
    return big.crop((o, o, o + SIZE, o + SIZE))


def build(out: Path, slides: list[Path], holds: list[float], music_volume: float) -> float:
    imgs = [Image.open(s).convert("RGB").resize((SIZE, SIZE), Image.LANCZOS) for s in slides]
    # línea de tiempo: cada lámina dura hold; las transiciones se solapan FADE
    starts, t = [], 0.0
    for h in holds:
        starts.append(t)
        t += h - FADE
    total = t + FADE
    nframes = int(round(total * FPS))

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "music.wav"
        music_chill.write_wav(music_chill.render(total + 0.1), str(wav))
        cmd = [ff, "-y", "-loglevel", "error",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{SIZE}x{SIZE}", "-r", str(FPS), "-i", "-",
               "-i", str(wav),
               "-filter:a", f"volume={music_volume}",
               "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(out)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for f in range(nframes):
            tt = f / FPS
            # lámina(s) activas en tt
            cur = max(i for i, s in enumerate(starts) if s <= tt + 1e-9)
            p = min(1.0, (tt - starts[cur]) / holds[cur])
            frame = frame_at(imgs[cur], p)
            # fundido cruzado: primeros FADE s de cada lámina mezclan con la anterior
            if cur > 0 and tt - starts[cur] < FADE:
                a = (tt - starts[cur]) / FADE
                prev = frame_at(imgs[cur - 1], min(1.0, (tt - starts[cur - 1]) / holds[cur - 1]))
                frame = Image.blend(prev, frame, a)
            proc.stdin.write(frame.tobytes())
        proc.stdin.close()
        if proc.wait() != 0:
            raise SystemExit("ffmpeg falló")
    return total


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("slides", nargs="+")
    ap.add_argument("--holds", default="")
    ap.add_argument("--music-volume", type=float, default=0.35)
    a = ap.parse_args()
    slides = [Path(s) for s in a.slides]
    holds = [float(x) for x in a.holds.split(",")] if a.holds else default_holds(len(slides))
    assert len(holds) == len(slides), "una duración por lámina"
    total = build(Path(a.out), slides, holds, a.music_volume)
    print(f"video: {a.out} · {len(slides)} láminas · {total:.1f} s")


if __name__ == "__main__":
    main()
