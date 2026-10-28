#!/usr/bin/env python3
"""Compone una pista original chill house (120 BPM) ajustada a los cortes del video.

Uso:
    python3 scripts/music.py salida/mi_video [--lufs -17] [--seed 7]

Lee <out>/timeline.json y escribe <out>/music.wav (48 kHz, estéreo).
Estructura: portada = solo ambiente (pad); el ritmo entra en la lámina 01; cada corte de lámina cae
en un pulso, con un barrido suave antes y un respiro del bombo; el cierre retira el ritmo y resuelve
en Do mayor (IV–V–I). Todo es síntesis propia: no usa samples ni material de terceros.

IMPORTANTE: el agente no puede escuchar el audio. Este script mide volumen integrado (LUFS),
pico y balance por bandas; la aprobación final es de una persona escuchando.
"""
import argparse
import json
import math
import pathlib
import re
import subprocess

import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 44100


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir")
    ap.add_argument("--lufs", type=float, default=-17.0)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--xmas", action="store_true",
                    help="toque navideño: cascabeles en el groove y celesta arpegiada (solo si MKT lo pide)")
    a = ap.parse_args()
    out = pathlib.Path(a.outdir)
    tl = json.loads((out / "timeline.json").read_text())
    rng = np.random.default_rng(a.seed)

    BEAT = 60.0 / tl.get("bpm", 120); BAR = 4 * BEAT; S16 = BEAT / 4
    DUR = float(tl["duration"]); TAIL = 3.0; N = int((DUR + TAIL) * SR)
    cuts = tl["cuts"]; T_IN, T_OUT = cuts[0], tl["close_at"]
    t_all = np.arange(N) / SR

    def mtof(m): return 440.0 * 2 ** ((m - 69) / 12.0)
    def buf(): return np.zeros((N, 2))

    def place(dst, x, t0, gl=1.0, gr=1.0):
        i = int(round(t0 * SR))
        if i >= N or i < 0: return
        n = min(len(x), N - i)
        if x.ndim == 1:
            dst[i:i+n, 0] += x[:n] * gl; dst[i:i+n, 1] += x[:n] * gr
        else:
            dst[i:i+n, 0] += x[:n, 0] * gl; dst[i:i+n, 1] += x[:n, 1] * gr

    def filt(x, kind, fc, order=2):
        return signal.sosfilt(signal.butter(order, fc, kind, fs=SR, output='sos'), x, axis=0)

    CH = {'F': (41, [57, 60, 64, 67]), 'G': (43, [59, 62, 64, 69]), 'Em': (40, [59, 62, 64, 67]),
          'Am': (45, [55, 59, 60, 64]), 'C': (36, [55, 59, 62, 64])}
    nb = int(math.ceil(DUR / BAR))
    bars = [['F', 'G', 'Em', 'Am'][i % 4] for i in range(max(0, nb - 3))] + ['F', 'G', 'C'][-min(3, nb):]
    groove = lambda tt: T_IN - 1e-6 <= tt < T_OUT - 1e-6

    # bombo + sidechain
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 54 + 120 * np.exp(-t / 0.036)
    K = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
    K += filt(rng.standard_normal(n) * np.exp(-t / 0.004), 'lowpass', 4500) * 0.26
    K[:88] *= np.linspace(0, 1, 88)
    kick_times = [T_IN + i * BEAT for i in range(int(round((T_OUT - T_IN) / BEAT)) + 1)]
    kick_times = [k for k in kick_times if not any(abs(k - (c - BEAT)) < 1e-6 for c in cuts[1:])]
    kick = buf(); duck = np.ones(N)
    for k in kick_times:
        place(kick, K, k)
        i = int(k * SR); m = min(int(0.42 * SR), N - i); tt = np.arange(m) / SR
        duck[i:i+m] = np.minimum(duck[i:i+m], 1 - 0.55 * np.exp(-tt / 0.13))

    # pad: sierras aditivas con filtro pasa-bajos variable aplicado en el dominio de armónicos (sin aliasing)
    def cutoff(tt):
        base = np.interp(tt, [0, T_IN, T_IN + 7, T_OUT - 7, T_OUT, DUR - 2, DUR + TAIL],
                         [520, 1900, 2300, 2700, 2000, 1150, 600])
        return base * (1 + 0.12 * np.sin(2 * np.pi * tt / 7.3))
    pad = buf()
    for bi, name in enumerate(bars):
        t0 = bi * BAR; length = BAR + (2.6 if bi == nb - 1 else 0.9)
        n = int(length * SR); t = np.arange(n) / SR
        env = np.minimum(1, t / 0.45) * np.minimum(1, (length - t) / 0.9)
        fc = cutoff(t0 + t); i0 = int(t0 * SR); m = min(n, N - i0)
        for mnote in CH[name][1] + [CH[name][1][0] - 12]:
            f0 = mtof(mnote)
            for ch, det in ((0, -5.5), (1, 5.5), (0, 2.0), (1, -2.0)):
                fr = f0 * 2 ** (det / 1200.0); x = np.zeros(n); ph0 = rng.uniform(0, 2 * np.pi)
                for h in range(1, 40):
                    if fr * h > 5200: break
                    x += np.sin(2 * np.pi * fr * h * t + ph0 * h) / h / (1.0 + (fr * h / fc) ** 2.6)
                pad[i0:i0 + m, ch] += (x * env)[:m] * 0.5
    pad *= duck[:, None]

    # teclado tipo piano eléctrico (FM suave), golpes sincopados de deep house
    def ep(m, dur, vel, decay):
        n = int(dur * SR); t = np.arange(n) / SR; fr = mtof(m)
        idx = (1.35 * vel) * np.exp(-t / 0.14) + 0.2
        x = np.sin(2 * np.pi * fr * t + idx * np.sin(2 * np.pi * fr * t)) + 0.18 * np.sin(4 * np.pi * fr * t) * np.exp(-t / 0.08)
        env = np.exp(-t / decay); env[:264] *= np.linspace(0, 1, 264); env[-2205:] *= np.linspace(1, 0, 2205)
        return x * env * vel
    keys = buf()
    for bi, name in enumerate(bars):
        b0 = bi * BAR
        if b0 >= T_OUT - 1e-6: hits = [(0, 0.8, 1.6)]
        elif groove(b0): hits = [(0, 1.0, 0.42), (3, 0.6, 0.30), (6, 0.8, 0.36), (10, 0.55, 0.30)]
        else: hits = [(0, 0.45, 1.1)]
        for step, vel, dec in hits:
            tt = b0 + step * S16
            if b0 < T_OUT <= tt: continue
            for j, mnote in enumerate(CH[name][1]):
                pan = 0.5 + (j - 1.5) * 0.14
                place(keys, ep(mnote, dec * 4.5, vel, dec), tt + j * 0.004, math.cos(pan * math.pi / 2), math.sin(pan * math.pi / 2))
    keys = filt(keys, 'lowpass', 5500)
    dly = buf()
    for d, g, side in ((0.375, 0.34, 0), (0.75, 0.2, 1), (1.125, 0.11, 0)):
        i = int(d * SR); dly[i:, side] += keys[:-i].mean(axis=1) * g
    keys = (keys + filt(dly, 'lowpass', 2200)) * (0.55 + 0.45 * duck)[:, None]

    # bajo
    def bassnote(m, dur, vel, soft=False):
        n = int(dur * SR); t = np.arange(n) / SR; fr = mtof(m)
        x = np.sin(2 * np.pi * fr * t) + 0.35 * np.sin(4 * np.pi * fr * t) + 0.12 * np.sin(6 * np.pi * fr * t)
        if soft: env = np.minimum(1, t / 0.25) * np.minimum(1, (dur - t) / 0.8)
        else:
            env = np.exp(-t / 0.22); env[:352] *= np.linspace(0, 1, 352); env[-1323:] *= np.linspace(1, 0, 1323)
        return np.tanh(x * env * 1.4) / 1.4 * vel
    bass = buf()
    for bi, name in enumerate(bars):
        root = CH[name][0] + (12 if CH[name][0] < 40 else 0); b0 = bi * BAR
        for step, vel in ((2, 1.0), (6, 0.85), (10, 1.0), (14, 0.8)):
            if groove(b0 + step * S16): place(bass, bassnote(root, 0.30, vel), b0 + step * S16)
        if b0 >= T_OUT - 1e-6 or (b0 < T_OUT < b0 + BAR):
            st = max(b0, T_OUT)
            place(bass, bassnote(root, b0 + BAR - st + 0.6 + (1.5 if bi == nb - 1 else 0), 0.55, soft=True), st)
    bass = filt(bass, 'lowpass', 900) * duck[:, None]

    # platillos, shaker y palmas (entran escalonados)
    def burst(dur, decay, kind, fc, order=4):
        n = int(dur * SR); t = np.arange(n) / SR
        return filt(rng.standard_normal(n), kind, fc, order) * np.exp(-t / decay)
    hats = buf(); shk = buf(); clap = buf()
    tt = T_IN + 2 * BAR + BEAT / 2
    while tt < T_OUT - 1e-6:
        place(hats, burst(0.12, 0.028, 'highpass', 7500), tt, 0.85, 1.0); tt += BEAT
    tt = T_IN + 4 * BAR; i = 0
    while tt < T_OUT - 1e-6:
        place(shk, burst(0.07, 0.016, 'highpass', 6000) * (0.45, 0.75, 1.0, 0.7)[i % 4], tt + (0.006 if i % 2 else 0), 1.0, 0.7)
        tt += S16; i += 1
    tt = T_IN + 4 * BAR + BEAT
    while tt < T_OUT - 1e-6:
        c = np.zeros(int(0.3 * SR))
        for off in (0.0, 0.011, 0.023):
            b = burst(0.25, 0.012 if off < 0.02 else 0.09, 'bandpass', [900, 3200], 2)
            j = int(off * SR); c[j:j + len(b)] += b[:len(c) - j]
        place(clap, c, tt); tt += 2 * BEAT

    # barridos antes de cada corte e impacto suave al entrar al cierre
    fx = buf()
    for c in cuts:
        n = SR; t = np.arange(n) / SR; nz = rng.standard_normal((n, 2))
        lo = filt(nz, 'bandpass', [700, 2200]); hi = filt(nz, 'bandpass', [2500, 8000])
        place(fx, (lo * (1 - t[:, None]) + hi * t[:, None]) * (t ** 2.2)[:, None], c - 1.0)
    n = 3 * SR; t = np.arange(n) / SR
    imp = np.sin(2 * np.pi * (52 + 20 * np.exp(-t / 0.06)) * t) * np.exp(-t / 0.5) * 2.2
    place(fx, filt(rng.standard_normal((n, 2)), 'highpass', 3500) * np.exp(-t / 0.9)[:, None] * 0.5 + imp[:, None], T_OUT)

    # reverb por convolución (respuesta al impulso de ruido con caída exponencial)
    def reverb(x, rt=1.9, pre=0.02):
        n = int(rt * 1.6 * SR); t = np.arange(n) / SR
        ir = filt(filt(rng.standard_normal((n, 2)) * np.exp(-t / (rt / 6.9))[:, None], 'highpass', 350), 'lowpass', 5500)
        ir /= np.sqrt((ir ** 2).sum(axis=0))
        o = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[:N] for c in range(2)], axis=1)
        p = int(pre * SR); return np.vstack([np.zeros((p, 2)), o[:-p]])

    # toque navideño opcional: cascabeles (ruido metálico en corcheas) + celesta (campana FM) arpegiada
    xm = buf()
    if a.xmas:
        def jingle():
            n = int(0.16 * SR); t = np.arange(n) / SR; x = np.zeros(n)
            for fr in (5200, 6900, 8300, 9700):
                x += np.sin(2 * np.pi * fr * t + rng.uniform(0, 6.28)) * np.exp(-t / 0.05)
            return filt(x * 0.25 + rng.standard_normal(n) * np.exp(-t / 0.02) * 0.6, 'highpass', 4500)
        tt = T_IN + BEAT / 2; i = 0
        while tt < T_OUT - 1e-6:
            place(xm, jingle() * (1.0 if i % 2 else 0.6), tt, 0.8, 1.0); tt += BEAT / 2; i += 1
        def celesta(m, vel):
            n = int(1.6 * SR); t = np.arange(n) / SR; fr = mtof(m)
            x = np.sin(2 * np.pi * fr * t + 0.9 * np.exp(-t / 0.3) * np.sin(2 * np.pi * fr * 3.5 * t))
            x += 0.3 * np.sin(2 * np.pi * fr * 2.76 * t) * np.exp(-t / 0.25)
            env = np.exp(-t / 0.55); env[:132] *= np.linspace(0, 1, 132)
            return x * env * vel
        for bi, name in enumerate(bars):
            b0 = bi * BAR; notes = sorted(CH[name][1])
            seq = [notes[0] + 12, notes[2] + 12, notes[3] + 12, notes[1] + 24]
            for j, mn in enumerate(seq * 2):
                tt = b0 + j * BEAT / 2
                if tt < DUR - 0.5:
                    pan = 0.3 + 0.4 * (j % 2)
                    place(xm, celesta(mn, 0.55 if groove(tt) else 0.35), tt, math.cos(pan * math.pi / 2), math.sin(pan * math.pi / 2))

    G = dict(kick=0.52, bass=0.40, pad=0.05, keys=0.17, hats=0.11, shk=0.05, clap=0.12, fx=0.035)
    dry = kick * G['kick'] + bass * G['bass'] + pad * G['pad'] + keys * G['keys'] + hats * G['hats'] + shk * G['shk'] + clap * G['clap'] + fx * G['fx'] + xm * 0.11
    send = pad * G['pad'] * 0.5 + keys * G['keys'] * 0.6 + clap * G['clap'] * 0.8 + hats * G['hats'] * 0.15 + fx * G['fx'] * 0.9 + xm * 0.11 * 0.7
    mix = filt(dry + reverb(send) * 0.5, 'highpass', 28)
    g = np.clip(t_all / 0.25, 0, 1) * np.clip((DUR - t_all) / 1.6, 0, 1) ** 1.5
    mix = np.tanh((mix * g[:, None])[:int(DUR * SR)] * 1.15) / 1.15
    mix = mix / np.abs(mix).max() * 0.8

    raw = out / "music_raw.wav"; wav = out / "music.wav"
    wavfile.write(raw, SR, (mix * 32767).astype(np.int16))
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(raw), "-af", "ebur128", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", meas)[-1])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", f"volume={a.lufs - I:.2f}dB", "-ar", "48000", str(wav)], check=True)
    raw.unlink()
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(wav), "-af", "ebur128=peak=true", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    I2 = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", meas)[-1]); pk = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", meas)[-1])
    print(f"OK  {wav}  ·  {I2:.1f} LUFS  ·  pico {pk:.1f} dBTP  ·  {DUR:.1f} s")
    if pk > -1.0:
        print("AVISO: pico sobre -1 dBTP; baja --lufs 1 dB y vuelve a generar.")


if __name__ == "__main__":
    main()
