#!/usr/bin/env python3
"""Analyze narration wav: find utterance chunks and silence gaps."""
import wave, struct, math, sys

path = sys.argv[1] if len(sys.argv) > 1 else '/home/user/arena/video/public/audio/narration_mono.wav'
w = wave.open(path, 'rb')
sr = w.getframerate()
n = w.getnframes()
data = w.readframes(n)
w.close()
samples = struct.unpack('<%dh' % n, data)

FRAME = int(sr * 0.02)
rms = []
for i in range(0, n - FRAME, FRAME):
    s = 0
    for j in range(i, i + FRAME, 4):
        v = samples[j]
        s += v * v
    rms.append(math.sqrt(s / (FRAME / 4)))

peak = max(rms)
thr = peak * 0.06
active = [r > thr for r in rms]

# merge: speech chunk = active run; join runs separated by < 0.28s; drop runs < 0.12s
chunks = []
i = 0
m = len(active)
while i < m:
    if active[i]:
        j = i
        while j < m:
            if active[j]:
                j += 1
            else:
                k = j
                while k < m and not active[k]:
                    k += 1
                if k - j <= int(0.28 / 0.02):
                    j = k
                else:
                    break
        chunks.append([i, j])
        i = j
    else:
        i += 1
chunks = [c for c in chunks if (c[1] - c[0]) * 0.02 >= 0.12]

print('peak rms', round(peak), 'thr', round(thr))
print('total dur %.2f' % (n / sr))
print('--- chunks (start, end, dur, gap_before) ---')
prev_end = 0
for idx, (a, b) in enumerate(chunks):
    st, en = a * 0.02, b * 0.02
    print('%2d  %6.2f %6.2f  dur=%5.2f  gap=%5.2f' % (idx, st, en, en - st, st - prev_end))
    prev_end = en
