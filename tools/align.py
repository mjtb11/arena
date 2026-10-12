#!/usr/bin/env python3
"""Align narration audio chunks to the 16 script lines via DP (duration model)."""
import wave, struct, math, json

PATH = '/home/user/arena/video/public/audio/narration_mono.wav'

LINES = [
    "مَنَم شیرِ ژیانِ قِزِلباش!",
    "البته... قبل از این‌که شیر بشویم، خیلی دویدیم؛ بیشتر هم دنبالِ اسب‌هایمان!",
    "ما از طایفه‌های مختلف آمدیم؛ با کلاه‌های سرخ، شمشیرهای تیز، و وفاداری به خاندانِ صَفَوی.",
    "دورِ شاه‌اسماعیل جمع شدیم؛ جوان بود، امّا رؤیایش کوچک نبود.",
    "ما جنگیدیم، او شاه شد، و کم‌کم صاحبِ منصب و قدرت شدیم.",
    "دیروز دنبالِ زینِ اسب بودیم؛ امروز دنبالِ صندلیِ بهتر!",
    "[خنده کوتاه]",
    "امّا وقتی چند سردار، هم‌زمان، خودشان را مهم‌ترین مردِ مملکت بدانند...",
    "خب، جلسه کوتاه نمی‌شود!",
    "رقابت‌ها بالا گرفت.",
    "بعدها، شاه‌عباس برای مهارِ قدرتِ ما، نیروی تازه‌ای به سپاه آورد؛ تا همه‌چیز به قزلباش‌ها وابسته نباشد.",
    "آن‌وقت فهمیدیم:",
    "رسیدن به قدرت، یک جنگ است؛ نگه‌داشتنش، هزار جنگ!",
    "حالا...",
    "کلاه مرا بیاورید؛ بی‌کلاه، این‌همه اُبُهَت هدر می‌رود!",
    "[خنده کوتاه]",
]

def weight(t):
    if t.startswith('['):
        return 10.0  # laugh: short burst
    return sum(1 for ch in t if not ch.isspace())

w = wave.open(PATH, 'rb')
sr = w.getframerate()
n = w.getnframes()
samples = struct.unpack('<%dh' % n, w.readframes(n))
w.close()

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

chunks = []
i, m = 0, len(active)
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
        chunks.append((i * 0.02, j * 0.02))
        i = j
    else:
        i += 1
chunks = [c for c in chunks if c[1] - c[0] >= 0.12]

durs = [b - a for a, b in chunks]
weights = [weight(t) for t in LINES]
scale = sum(durs) / sum(weights)
exp = [wt * scale for wt in weights]

NC, NL = len(chunks), len(LINES)
INF = float('inf')
# dp[l][c] = min cost aligning first l lines to chunks[0:c]
dp = [[INF] * (NC + 1) for _ in range(NL + 1)]
bk = [[0] * (NC + 1) for _ in range(NL + 1)]
dp[0][0] = 0.0
for l in range(1, NL + 1):
    for c in range(l, NC + 1):
        best, bs = INF, 0
        # group = chunks[s:c]
        run = 0.0
        for s in range(c - 1, l - 2, -1):
            run += durs[s]
            # penalize giving a laugh line multiple chunks heavily
            pen = 0.0
            if LINES[l - 1].startswith('[') and (c - s) > 1:
                pen = 4.0 * (c - s)
            # penalize splitting very short lines across many chunks
            v = dp[l - 1][s] + (run - exp[l - 1]) ** 2 + pen
            if v < best:
                best, bs = v, s
        dp[l][c] = best
        bk[l][c] = bs

groups = []
c = NC
for l in range(NL, 0, -1):
    s = bk[l][c]
    groups.append((s, c))
    c = s
groups.reverse()

out = []
print('line  start    end     dur   text')
for idx, ((s, e), txt) in enumerate(zip(groups, LINES)):
    st, en = chunks[s][0], chunks[e - 1][1]
    out.append({'line': idx + 1, 'text': txt, 'start': round(st, 2), 'end': round(en, 2),
                'chunks': [s, e - 1]})
    print('%3d  %6.2f  %6.2f  %5.2f  %s' % (idx + 1, st, en, en - st, txt[:46]))

with open('/home/user/arena/tools/line_timing.json', 'w', encoding='utf-8') as f:
    json.dump({'total': round(n / sr, 2), 'lines': out}, f, ensure_ascii=False, indent=2)
print('saved tools/line_timing.json')
