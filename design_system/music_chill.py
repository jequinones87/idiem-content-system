"""Música de fondo "chill house" sutil, sintetizada (sin licencias de terceros).

Determinística (semilla fija): mismo resultado en cada corrida, para que el video
sea reproducible y auditable. Elementos: bombo suave a negras, hi-hat a contratiempo,
pad de acordes (Am9 – Fmaj7 – Cmaj7 – Em7) con "sidechain", bajo sub y fade in/out.

Uso:
  python3 design_system/music_chill.py <segundos> <salida.wav>
"""
from __future__ import annotations

import sys
import wave

import numpy as np

SR = 44100
BPM = 118
BEAT = 60.0 / BPM


def _note(m: float) -> float:
    return 440.0 * 2 ** ((m - 69) / 12)


def _lowpass(x: np.ndarray, cutoff: float) -> np.ndarray:
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):  # one-pole; suficiente para un pad suave
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def render(seconds: float, seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)

    # ---- pad de acordes (un acorde por compás de 4 tiempos) ----
    chords = [[57, 60, 64, 67, 71], [53, 57, 60, 64], [48, 55, 59, 64], [52, 55, 59, 62]]
    bar = 4 * BEAT
    pad = np.zeros(n)
    for b in range(int(seconds / bar) + 1):
        s, e = int(b * bar * SR), min(n, int((b + 1) * bar * SR))
        if s >= n:
            break
        tt = t[s:e] - t[s]
        seg = np.zeros(e - s)
        for m in chords[b % len(chords)]:
            f = _note(m)
            for det in (-0.12, 0.12):  # dos osciladores levemente desafinados
                ph = 2 * np.pi * f * (1 + det / 100) * tt
                seg += 0.5 * np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.07 * np.sin(3 * ph)
        env = np.minimum(1, tt / 0.35) * np.minimum(1, (tt[-1] - tt + 1e-9) / 0.25)
        pad[s:e] += seg * env
    pad = _lowpass(pad / 6.0, 1400)

    # ---- sidechain (el pad "respira" con el bombo) ----
    beat_pos = (t % BEAT) / BEAT
    duck = 0.55 + 0.45 * np.minimum(1, beat_pos / 0.45)
    out += 0.42 * pad * duck

    # ---- bajo sub (raíz del acorde, en corcheas a contratiempo) ----
    roots = [45, 41, 36, 40]
    for i in range(int(seconds / (BEAT / 2))):
        if i % 2 == 0:
            continue
        s = int(i * BEAT / 2 * SR)
        L = int(0.22 * SR)
        if s + L > n:
            break
        tt = np.arange(L) / SR
        f = _note(roots[int(i * BEAT / 2 / bar) % 4])
        out[s:s + L] += 0.20 * np.sin(2 * np.pi * f * tt) * np.exp(-tt * 9)

    # ---- bombo suave a negras ----
    for i in range(int(seconds / BEAT) + 1):
        s = int(i * BEAT * SR)
        L = int(0.30 * SR)
        if s + L > n:
            break
        tt = np.arange(L) / SR
        f = 48 + 70 * np.exp(-tt * 35)
        out[s:s + L] += 0.38 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 11)

    # ---- hi-hat a contratiempo (ruido filtrado, muy bajo) ----
    noise = rng.standard_normal(n)
    hp = noise - _lowpass(noise, 6000)
    for i in range(int(seconds / BEAT) + 1):
        s = int((i + 0.5) * BEAT * SR)
        L = int(0.06 * SR)
        if s + L > n:
            break
        out[s:s + L] += 0.05 * hp[s:s + L] * np.exp(-np.arange(L) / SR * 60)

    # ---- fade in/out + normalización conservadora (fondo sutil) ----
    fade = np.minimum(1, t / 1.5) * np.minimum(1, (seconds - t) / 2.0)
    out *= fade
    out /= max(1e-9, np.max(np.abs(out)))
    return out * 0.32  # pico ≈ -10 dBFS; el video la baja aún más en la mezcla


def write_wav(x: np.ndarray, path: str) -> None:
    data = (np.clip(x, -1, 1) * 32767).astype("<i2")
    stereo = np.column_stack([data, data]).ravel()
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(stereo.tobytes())


if __name__ == "__main__":
    write_wav(render(float(sys.argv[1])), sys.argv[2])
