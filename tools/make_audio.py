#!/usr/bin/env python3
"""Procedural audio bed: historical-epic light music + SFX, mixed with narration.
All synthesized (no copyright). Narration = user-provided file.
Output: video/public/audio/mix.wav (48 kHz stereo 16-bit)."""
import numpy as np, wave, subprocess, json, os, math

SR = 48000
T = 71.5
A = '/home/user/arena/video/public/audio'
FF = subprocess.run(['python3', '-c', 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())'],
                    capture_output=True, text=True).stdout.strip()

def read_wav(path):
    w = wave.open(path, 'rb')
    sr = w.getframerate(); n = w.getnframes(); ch = w.getnchannels()
    d = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    w.close()
    if ch == 2:
        d = d.reshape(-1, 2).mean(axis=1)
    return d, sr

def resample(d, sr0, sr1):
    if sr0 == sr1:
        return d
    n = int(len(d) * sr1 / sr0)
    idx = np.linspace(0, len(d) - 1, n)
    i0 = np.floor(idx).astype(int)
    i1 = np.minimum(i0 + 1, len(d) - 1)
    f = idx - i0
    return d[i0] * (1 - f) + d[i1] * f

nar, nsr = read_wav(os.path.join(A, 'narration_mono.wav'))
nar = resample(nar, nsr, SR)

N = int(T * SR)
mix = np.zeros((N, 2))
nar_track = np.zeros(N)
L = len(nar)
nar_track[:L] = nar * 0.98

# ---- reused laugh (from narrator, line 7) placed at outro ----
laugh = nar[int(36.70 * SR):int(37.96 * SR)]
# fade edges
lf = np.ones(len(laugh)); k = int(0.03 * SR)
lf[:k] = np.linspace(0, 1, k); lf[-k:] = np.linspace(1, 0, k)
laugh = laugh * lf * 0.9
LO = int(68.70 * SR)
seg = nar_track[LO:LO + len(laugh)]
nar_track[LO:LO + len(laugh)] = seg * 0.25 + laugh  # laugh over the tail silence

# ---- narration envelope for ducking ----
env = np.zeros(N)
win = int(0.1 * SR)
for i in range(0, N - win, win):
    env[i:i + win] = np.sqrt((nar_track[i:i + win] ** 2).mean())
env = np.convolve(env, np.ones(int(0.35 * SR)) / int(0.35 * SR), mode='same')
speech = (env > 0.02).astype(np.float64)
speech = np.convolve(speech, np.ones(int(0.5 * SR)) / int(0.5 * SR), mode='same')
duck = 0.95 - 0.55 * np.clip(speech, 0, 1)

t = np.arange(N) / SR

# ================= MUSIC =================
music = np.zeros(N)
# drone: D2 + A2 + D3 with slow LFO
for f0, g in ((73.42, 0.5), (110.0, 0.32), (146.83, 0.16)):
    lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.06 * t + f0)
    music += g * lfo * np.sin(2 * np.pi * f0 * t + 0.3 * np.sin(2 * np.pi * 0.11 * t))
music *= 0.16

# daf / frame drum: dum (low) & bak (tap)
def drum_dum(ts, g=1.0):
    i0 = int(ts * SR); dur = int(0.5 * SR)
    if i0 + dur > N: dur = N - i0
    tt = np.arange(dur) / SR
    f = 92 * np.exp(-tt * 7) + 46
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 8)
    s += 0.25 * np.random.randn(dur) * np.exp(-tt * 90)
    music[i0:i0 + dur] += g * 0.5 * s

def drum_bak(ts, g=1.0):
    i0 = int(ts * SR); dur = int(0.18 * SR)
    if i0 + dur > N: dur = N - i0
    tt = np.arange(dur) / SR
    s = (np.random.randn(dur) * 0.5 + 0.5 * np.sin(2 * np.pi * 210 * tt)) * np.exp(-tt * 26)
    music[i0:i0 + dur] += g * 0.22 * s

bar = 4.0
bt = 0.0
while bt < T - 2:
    drum_dum(bt + 0.0, 1.0)
    drum_bak(bt + 1.5, 0.8)
    drum_dum(bt + 2.5, 0.85)
    drum_bak(bt + 3.25, 0.7)
    bt += bar
# beat-end accents (storyboard hits)
for ts in (7.3, 17.0, 26.0, 34.0, 41.0, 49.0, 57.0):
    drum_dum(ts, 1.25); drum_dum(ts + 0.22, 0.8)

# santoor/oud-like plucks: Karplus-Strong
def pluck(freq, ts, dur=1.6, g=0.5):
    i0 = int(ts * SR); n = int(dur * SR)
    if i0 + n > N: n = N - i0
    p = max(2, int(SR / freq))
    buf = np.random.randn(p) * 0.6
    out = np.zeros(n)
    b = buf.copy()
    for i in range(n):
        j = i % p
        b[j] = 0.996 * 0.5 * (b[j] + b[(j + 1) % p])
        out[i] = b[j]
    music[i0:i0 + n] += g * out * np.exp(-np.arange(n) / SR * 2.2)

SHUR = [293.66, 311.13, 349.23, 392.0, 440.0, 466.16, 523.25, 587.33]
motifs = {
    0.4:  [0, 2, 3],
    10.5: [3, 4, 3, 2],
    19.3: [0, 4, 7],
    26.2: [5, 4, 3, 4],
    34.2: [2, 3, 2, 0],
    41.2: [4, 3, 2, 1],
    49.2: [0, 2, 4, 5],
    57.9: [7, 5, 4, 3],
    64.6: [3, 2, 0],
}
for ts, seq in motifs.items():
    for k, ni in enumerate(seq):
        pluck(SHUR[ni], ts + k * 0.42, g=0.16)

music *= duck
mix[:, 0] += music
mix[:, 1] += np.roll(music, int(0.011 * SR)) * 0.95 + music * 0.05

# ================= SFX =================
sfx = np.zeros(N)
def add(buf, ts, g=1.0):
    i0 = int(ts * SR)
    i1 = min(N, i0 + len(buf))
    sfx[i0:i1] += buf[:i1 - i0] * g

def noise(dur):
    return np.random.randn(int(dur * SR))

def whoosh(ts, dur=0.7, f0=400, f1=1800, g=0.3):
    n = int(dur * SR); s = noise(dur)
    # moving bandpass via simple resonator sweep
    out = np.zeros(n); y1 = y2 = 0.0
    for i in range(n):
        fc = f0 + (f1 - f0) * (i / n)
        w0 = 2 * np.pi * fc / SR
        a = 0.55
        y1 = (1 - a) * s[i] + a * y1
        y2 = a * y1 + (1 - a) * y2
        out[i] = y1 - y2
    envl = np.sin(np.linspace(0, np.pi, n)) ** 2
    add(out * envl, ts, g)

def clang(ts, g=0.5):
    n = int(0.9 * SR); tt = np.arange(n) / SR
    s = np.zeros(n)
    for f, gg in ((2140, 1.0), (3180, 0.7), (4470, 0.45), (5320, 0.3), (1620, 0.5)):
        s += gg * np.sin(2 * np.pi * f * tt + np.random.rand() * 6) * np.exp(-tt * (6 + f / 900))
    s += 0.6 * noise(0.9) * np.exp(-tt * 40)
    add(s, ts, g)

def thud(ts, g=0.6, f=70):
    n = int(0.5 * SR); tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * (f * np.exp(-tt * 9) + 34) * tt) * np.exp(-tt * 10)
    s += 0.2 * noise(0.5) * np.exp(-tt * 60)
    add(s, ts, g)

def paper(ts, g=0.35):
    n = int(0.45 * SR); tt = np.arange(n) / SR
    s = noise(0.45)
    s = np.convolve(s, np.ones(5) / 5, 'same')
    s *= (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 9 * tt))) * np.exp(-tt * 7)
    add(s, ts, g)

def crowd(ts, dur=6.0, g=0.10):
    n = int(dur * SR)
    s = np.cumsum(noise(dur)) / 400.0
    s = np.convolve(s, np.ones(int(0.05 * SR)) / int(0.05 * SR), 'same')
    s += 0.3 * noise(dur) * 0.05
    envl = np.sin(np.linspace(0, np.pi, n)) ** 1.5
    add(s * envl, ts, g)

def knock(ts, g=0.5):
    n = int(0.25 * SR); tt = np.arange(n) / SR
    s = (np.sin(2 * np.pi * 180 * tt) + 0.5 * np.sin(2 * np.pi * 310 * tt)) * np.exp(-tt * 30)
    s += 0.3 * noise(0.25) * np.exp(-tt * 80)
    add(s, ts, g)

def roll(ts, dur=1.6, g=0.3):
    n = int(dur * SR)
    s = np.zeros(n)
    k = 0
    tt0 = 0.0
    step = 0.09
    while tt0 < dur:
        i0 = int(tt0 * SR); nn = min(int(0.3 * SR), n - i0)
        if nn <= 0:
            break
        tt = np.arange(nn) / SR
        s[i0:i0 + nn] += np.sin(2 * np.pi * 150 * np.exp(-tt * 8) * tt) * np.exp(-tt * 14) * (0.4 + 0.6 * tt0 / dur)
        tt0 += step
    add(s, ts, g)

# --- SFX cue sheet (see docs/audio.md) ---
paper(0.15, 0.4)                 # title paper unfold
whoosh(4.95, 0.8, 300, 1500, 0.30)   # horse shadow pass (beat1)
thud(7.35, 0.5)                  # beat1 end hit
paper(10.55, 0.4)                # map unfold (beat2)
whoosh(12.1, 0.5, 500, 2200, 0.16)   # flags stagger
whoosh(12.9, 0.5, 500, 2200, 0.16)
whoosh(13.7, 0.5, 500, 2200, 0.16)
whoosh(19.35, 1.0, 200, 900, 0.28)   # Ismail emblem swell
clang(26.35, 0.42)               # sword clash 1
clang(27.75, 0.36)               # sword clash 2
thud(29.15, 0.7, 60)             # seal / mandate stamp
knock(32.55, 0.55)               # chair entrance (comic)
knock(33.05, 0.4)
thud(36.6, 0.35, 90)             # laugh beat pillow
crowd(38.4, 7.0, 0.09)           # commanders arguing murmur (beat6)
paper(45.05, 0.3)                # meeting papers
thud(47.2, 0.55, 75)             # rivalry hit
roll(48.0, 1.8, 0.28)            # new army drum roll (beat7)
whoosh(49.3, 0.8, 250, 1200, 0.2)
thud(56.25, 0.8, 50)             # "فهمیدیم" boom
thud(57.95, 0.6, 65)             # یک جنگ
thud(61.95, 0.85, 55)            # هزار جنگ
whoosh(64.65, 0.6, 400, 1600, 0.25)  # hat entrance cloth
paper(68.6, 0.35)                # paper transition out
thud(70.4, 0.5, 60)              # final card

mix[:, 0] += sfx * 0.9
mix[:, 1] += sfx * 0.9

# narration on top (full, unducked)
mix[:, 0] += nar_track
mix[:, 1] += nar_track

# master: gentle comp + normalize
peak = np.abs(mix).max()
mix = mix / peak * 0.89
# fade out last 1.2s
fo = int(1.2 * SR)
mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5

pcm = (mix * 32767).astype(np.int16)
w = wave.open(os.path.join(A, 'mix.wav'), 'wb')
w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes(pcm.tobytes())
w.close()
print('mix.wav written', round(os.path.getsize(os.path.join(A, 'mix.wav')) / 1e6, 2), 'MB, dur', T)
