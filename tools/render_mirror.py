#!/usr/bin/env python3
"""
Qezelbash historical motion-graphics — production renderer (Pillow mirror of the
Remotion composition in video/src). Reads the same storyboard spec.
Rules honored: character shown ONLY via the 4 allowed frames; motion limited to
2D translate / uniform scale / camera zoom / cuts & dissolves / frame swapping.
No deformation, no new poses, no lip-sync warping.
Output: out/frames/%05d.png  (1920x1080 @ 24fps)
"""
import os, math, json, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import arabic_reshaper
from bidi.algorithm import get_display

ROOT = '/home/user/arena'
PUB = os.path.join(ROOT, 'video', 'public')
ASSETS = os.path.join(PUB, 'assets')
FONTS = os.path.join(PUB, 'fonts', 'ttf')
OUT = os.path.join(ROOT, 'out', 'frames')
os.makedirs(OUT, exist_ok=True)

W, H = 1920, 1080
FPS = 24
T_END = 71.5

# ---------------- palette ----------------
INK = (43, 29, 22)
PAPER = (239, 230, 208)
CREAM = (242, 232, 213)
CRIMSON = (122, 31, 43)
DEEPRED = (90, 22, 32)
GOLD = (201, 162, 74)
GOLDD = (185, 138, 46)
DBLUE = (35, 54, 79)
BROWN = (107, 74, 47)

# ---------------- easing ----------------
def clamp01(x): return 0.0 if x < 0 else (1.0 if x > 1 else x)
def seg(t, a, b): return clamp01((t - a) / max(1e-9, (b - a)))
def eoc(x): x = clamp01(x); return 1 - (1 - x) ** 3
def eio(x): x = clamp01(x); return x * x * (3 - 2 * x)
def eoq(x): x = clamp01(x); return 1 - (1 - x) ** 5
def eback(x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def spring(x, damp=0.62, freq=7.0):
    x = clamp01(x)
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    return 1 - math.exp(-damp * freq * x) * math.cos(freq * x * 1.35)
def lerp(a, b, k): return a + (b - a) * k

# ---------------- assets ----------------
_cache = {}
def img(key, path):
    if key not in _cache:
        _cache[key] = Image.open(path).convert('RGBA')
    return _cache[key]

def pose(i): return img('pose%d' % i, os.path.join(ASSETS, 'char', 'pose_0%d.png' % i))
def prop(n): return img('prop_' + n, os.path.join(ASSETS, 'props', n + '.png'))
def bg(n): return img('bg_' + n, os.path.join(ASSETS, 'bg', n + '.jpg'))

_font_cache = {}
def font(weight, size):
    k = (weight, size)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(os.path.join(FONTS, 'Vazirmatn-%d.ttf' % weight), size)
    return _font_cache[k]

def fa(text):
    return get_display(arabic_reshaper.reshape(text))

def cover(im, w, h):
    w0, h0 = im.size
    k = max(w / w0, h / h0)
    nw, nh = int(w0 * k + 0.5), int(h0 * k + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    x, y = (nw - w) // 2, (nh - h) // 2
    return im.crop((x, y, x + w, y + h))


def fit(im, max_w, max_h):
    w, h = im.size
    k = min(max_w / w, max_h / h)
    return im.resize((max(1, int(w * k)), max(1, int(h * k))), Image.LANCZOS)

def paste(canvas, im, cx, cy, alpha=1.0, scale=1.0, rot=0.0):
    """paste RGBA im centered at (cx,cy) with uniform scale + optional rotation (2D only)"""
    if scale != 1.0:
        w, h = im.size
        im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1.0:
        im = im.copy()
        a = im.getchannel('A').point(lambda v: int(v * alpha))
        im.putalpha(a)
    w, h = im.size
    canvas.alpha_composite(im, (int(cx - w / 2), int(cy - h / 2)))

# ---------------- text ----------------
def text_block(canvas, text, cx, cy, size=44, weight=500, fill=CREAM, alpha=1.0,
               max_width=1500, line_gap=1.34, anchor='mm', shadow=True):
    if alpha <= 0.01: return
    f = font(weight, size)
    words = text.split(' ')
    lines, cur = [], ''
    for wd in words:
        trial = (cur + ' ' + wd).strip()
        if f.getlength(fa(trial)) > max_width and cur:
            lines.append(cur); cur = wd
        else:
            cur = trial
    if cur: lines.append(cur)
    tmp = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    lh = int(size * line_gap)
    total = lh * len(lines)
    y0 = cy - total / 2 + lh / 2 if anchor == 'mm' else cy + lh / 2
    for i, ln in enumerate(lines):
        yy = y0 + i * lh
        if shadow:
            d.text((cx + 2, yy + 2), fa(ln), font=f, fill=(15, 10, 8, int(150 * alpha)), anchor='mm')
        d.text((cx, yy), fa(ln), font=f, fill=fill + (int(255 * alpha),), anchor='mm')
    canvas.alpha_composite(tmp)

def chip(canvas, text, cx, cy, size=40, weight=700, pad_x=34, pad_y=16,
         bg=INK, fg=CREAM, alpha=1.0, scale=1.0):
    if alpha <= 0.01: return
    f = font(weight, size)
    tw = f.getlength(fa(text))
    w, h = int((tw + pad_x * 2) * scale), int((size * 1.5 + pad_y) * scale)
    tmp = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=int(14 * scale),
                        fill=bg + (int(232 * alpha),))
    d.text((cx, cy), fa(text), font=f, fill=fg + (int(255 * alpha),), anchor='mm')
    canvas.alpha_composite(tmp)

# ---------------- global overlays ----------------
def build_overlays():
    vig = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(vig)
    d.ellipse([-W * 0.25, -H * 0.35, W * 1.25, H * 1.35], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(160))
    vig = vig.point(lambda v: int(90 + v * 165 / 255))
    rng = random.Random(7)
    grains = []
    for g in range(3):
        arr = np.random.default_rng(g).integers(0, 255, (H // 2, W // 2), dtype=np.uint8)
        im = Image.fromarray(arr, 'L').resize((W, H), Image.BILINEAR)
        grains.append(im)
    return vig, grains

VIG, GRAINS = build_overlays()

def grade(canvas, t, dark=0.0, warm=0.0):
    """vignette + grain + optional darken/warm — unified historical look"""
    canvas = canvas.convert('RGBA')
    if dark:
        canvas.alpha_composite(Image.new('RGBA', (W, H), (12, 8, 5, int(255 * dark))))
    if warm:
        canvas.alpha_composite(Image.new('RGBA', (W, H), (120, 70, 20, int(255 * warm))))
    g = GRAINS[int(t * FPS) % 3]
    ga = Image.new('RGBA', (W, H), (128, 120, 100, 0))
    ga.putalpha(g.point(lambda v: v // 16))
    canvas.alpha_composite(ga)
    v = Image.new('RGBA', (W, H), (10, 6, 4, 0))
    v.putalpha(VIG.point(lambda v: 255 - v))
    canvas.alpha_composite(v)
    return canvas

# ---------------- character ----------------
def draw_char(canvas, i, cx, bottom_y, height, t, alpha=1.0, scale=1.0,
              freeze=False, bob_phase=0.0):
    im = pose(i)
    w, h = im.size
    k = height / h
    bob = 0.0 if freeze else math.sin(2 * math.pi * 0.22 * t + bob_phase) * 4
    breath = 1.0 if freeze else 1.0 + 0.012 * math.sin(2 * math.pi * 0.13 * t + 1.0)
    hh = int(height * scale * breath)
    ww = int(w * k * scale * breath)
    im2 = im.resize((ww, hh), Image.LANCZOS)
    paste(canvas, im2, cx, bottom_y - hh / 2 + bob, alpha=alpha)

def char_swap(canvas, i_from, i_to, cx, bottom_y, height, t, t0, dur=0.25, freeze=False):
    k = seg(t, t0, t0 + dur)
    if k <= 0:
        draw_char(canvas, i_from, cx, bottom_y, height, t, freeze=freeze)
    elif k >= 1:
        draw_char(canvas, i_to, cx, bottom_y, height, t, freeze=freeze)
    else:
        draw_char(canvas, i_from, cx, bottom_y, height, t, alpha=1 - k, freeze=freeze)
        draw_char(canvas, i_to, cx, bottom_y, height, t, alpha=k, freeze=freeze)

# ---------------- backgrounds ----------------
def paper_hp():
    """stain-free paper: high-pass grain over warm base"""
    if 'paper_hp' not in _cache:
        g = np.asarray(bg('paper').convert('L'), dtype=np.float32)
        base = np.asarray(bg('paper').convert('L').filter(ImageFilter.GaussianBlur(250)), dtype=np.float32)
        hp = np.clip(128 + (g - base) * 2.4, 0, 255).astype(np.uint8)
        lum = Image.fromarray(hp, 'L')
        rgb = Image.new('RGB', (W, H), (232, 222, 198))
        from PIL import ImageChops
        m = Image.merge('RGB', (lum, lum, lum)).point(lambda v: min(255, v * 2))
        _cache['paper_hp'] = ImageChops.multiply(rgb.convert('L').convert('RGB'), m)
    return _cache['paper_hp']


def bg_paper(canvas, tint=None, darken=0.0, soft=False):
    src = paper_hp() if soft else bg('paper')
    im = cover(src, W, H)
    canvas.alpha_composite(im.convert('RGBA'), (0, 0))
    if tint:
        canvas.alpha_composite(Image.new('RGBA', (W, H), tint))
    if darken:
        canvas.alpha_composite(Image.new('RGBA', (W, H), (16, 10, 7, int(255 * darken))))

def bg_photo(canvas, name, t, scale=1.10, px=0.0, py=0.0, desat=0.35, darken=0.28, blur=0):
    im = bg(name).convert('RGB')
    if desat:
        im = ImageEnhance.Color(im).enhance(1 - desat)
    im = ImageEnhance.Brightness(im).enhance(0.92)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    sw, sh = int(W * scale), int(H * scale)
    im = im.resize((sw, sh), Image.LANCZOS)
    ox = int((sw - W) / 2 + px); oy = int((sh - H) / 2 + py)
    im = im.crop((ox, oy, ox + W, oy + H)).convert('RGBA')
    canvas.alpha_composite(im)
    canvas.alpha_composite(Image.new('RGBA', (W, H), (20, 12, 8, int(255 * darken))))

# ---------------- vector helpers ----------------
def star12(d, cx, cy, r_out, r_in, fill, alpha=255, rot=0.0):
    pts = []
    for i in range(24):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * i / 12 + rot
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill + (alpha,))

def shield(d, cx, cy, w, h, fill, alpha=255):
    x0, y0 = cx - w / 2, cy - h / 2
    d.polygon([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h * 0.62),
               (cx, y0 + h), (x0, y0 + h * 0.62)], fill=fill + (alpha,))
    d.line([(cx, y0 + 6), (cx, y0 + h - 6)], fill=(20, 14, 10, alpha), width=4)
    d.line([(x0 + 8, y0 + h * 0.34), (x0 + w - 8, y0 + h * 0.34)], fill=(20, 14, 10, alpha), width=4)

def crown(d, cx, cy, w, h, fill, alpha=255):
    x0, y0 = cx - w / 2, cy - h / 2
    d.polygon([(x0, y0 + h), (x0, y0 + h * 0.35), (x0 + w * 0.25, y0 + h * 0.6),
               (cx, y0), (x0 + w * 0.75, y0 + h * 0.6), (x0 + w, y0 + h * 0.35),
               (x0 + w, y0 + h)], fill=fill + (alpha,))

# ---------------- subtitles ----------------
SUBS = [
    (0.30, 3.60, "مَنَم شیرِ ژیانِ قِزِلباش!"),
    (4.34, 9.60, "البته... قبل از این‌که شیر بشویم، خیلی دویدیم؛ بیشتر هم دنبالِ اسب‌هایمان!"),
    (10.78, 14.60, "ما از طایفه‌های مختلف آمدیم؛ با کلاه‌های سرخ،"),
    (14.60, 18.60, "شمشیرهای تیز، و وفاداری به خاندانِ صَفَوی."),
    (19.58, 22.60, "دورِ شاه‌اسماعیل جمع شدیم؛"),
    (22.60, 25.90, "جوان بود، امّا رؤیایش کوچک نبود."),
    (26.34, 28.30, "ما جنگیدیم، او شاه شد،"),
    (28.30, 30.40, "و کم‌کم صاحبِ منصب و قدرت شدیم."),
    (31.26, 33.30, "دیروز دنبالِ زینِ اسب بودیم؛"),
    (33.30, 35.60, "امروز دنبالِ صندلیِ بهتر!"),
    (38.30, 41.20, "امّا وقتی چند سردار، هم‌زمان،"),
    (41.20, 43.90, "خودشان را مهم‌ترین مردِ مملکت بدانند..."),
    (45.04, 46.70, "خب، جلسه کوتاه نمی‌شود!"),
    (47.14, 47.80, "رقابت‌ها بالا گرفت."),
    (47.94, 51.60, "بعدها، شاه‌عباس برای مهارِ قدرتِ ما، نیروی تازه‌ای به سپاه آورد؛"),
    (51.60, 55.30, "تا همه‌چیز به قزلباش‌ها وابسته نباشد."),
    (56.42, 57.60, "آن‌وقت فهمیدیم:"),
    (57.82, 60.40, "رسیدن به قدرت، یک جنگ است؛"),
    (60.60, 63.40, "نگه‌داشتنش، هزار جنگ!"),
    (63.70, 64.40, "حالا..."),
    (64.54, 68.30, "کلاه مرا بیاورید؛ بی‌کلاه، این‌همه اُبُهَت هدر می‌رود!"),
]

def subtitles(canvas, t):
    for a, b, txt in SUBS:
        if a - 0.25 <= t < b + 0.3:
            ain = seg(t, a - 0.22, a + 0.10)
            aout = 1 - seg(t, b, b + 0.28)
            al = ain * aout
            if al <= 0.01: continue
            f = font(500, 46)
            # wrap to max 2 lines
            words = txt.split(' ')
            lines, cur = [], ''
            for wd in words:
                trial = (cur + ' ' + wd).strip()
                if f.getlength(fa(trial)) > 1420 and cur:
                    lines.append(cur); cur = wd
                else:
                    cur = trial
            if cur: lines.append(cur)
            lh = 62
            hh = lh * len(lines) + 34
            bw = min(1520, max(f.getlength(fa(ln)) for ln in lines) + 120)
            tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(tmp)
            d.rounded_rectangle([W / 2 - bw / 2, 1080 - 40 - hh, W / 2 + bw / 2, 1080 - 40],
                                radius=18, fill=(24, 15, 10, int(196 * al)))
            d.line([(W / 2 - bw / 2 + 18, 1080 - 40 - hh + 10), (W / 2 - bw / 2 + 18, 1080 - 50)],
                   fill=GOLD + (int(200 * al),), width=5)
            for i, ln in enumerate(lines):
                yy = 1080 - 40 - hh / 2 + (i - (len(lines) - 1) / 2) * lh
                d.text((W / 2, yy), fa(ln), font=f, fill=CREAM + (int(255 * al),), anchor='mm')
            canvas.alpha_composite(tmp)

# ================= BEATS =================
def beat1(canvas, t):
    fade = eoc(seg(t, 0.0, 0.7))
    bg_paper(canvas, tint=(18, 11, 8, 150), darken=0.45 * (1 - fade * 0.35), soft=True)
    if fade < 1:
        canvas.alpha_composite(Image.new('RGBA', (W, H), (8, 5, 4, int(255 * (1 - fade)))))
    # title
    ta = eoc(seg(t, 1.1, 2.1)) * (1 - seg(t, 9.5, 10.2))
    if ta > 0:
        ty = lerp(150, 178, eback(seg(t, 1.1, 2.3)))
        text_block(canvas, "تاریخچهٔ قدرت قزلباش‌ها", 560, ty, size=62, weight=900,
                   fill=GOLD, alpha=ta, max_width=1100, shadow=True)
        lw = eoc(seg(t, 2.0, 2.9)) * 560
        if lw > 2:
            d = ImageDraw.Draw(canvas)
            d.rounded_rectangle([560 - lw / 2, ty + 56, 560 + lw / 2, ty + 62],
                                radius=3, fill=CRIMSON + (int(230 * ta),))
        text_block(canvas, "روایتِ یک سردار", 560, ty + 112, size=34, weight=500,
                   fill=CREAM, alpha=ta * 0.85, max_width=700)
    # horse shadow pass
    hk = seg(t, 4.9, 6.0)
    if 0 < hk < 1:
        hs = prop('horse')
        hs = hs.transpose(Image.FLIP_LEFT_RIGHT)
        sil = Image.new('RGBA', hs.size, (20, 12, 8, 0))
        sil.putalpha(hs.getchannel('A').point(lambda v: int(v * 0.55)))
        sil.paste((22, 13, 9), (0, 0), hs.getchannel('A'))
        sil = sil.filter(ImageFilter.GaussianBlur(5))
        x = lerp(W + 300, -400, eio(hk))
        paste(canvas, fit(sil, 620, 420), x, 760, alpha=0.75 * math.sin(math.pi * hk) ** 0.7)
        dov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(dov)
        for i in range(5):
            dx = x + 260 + i * 60
            r = 26 + i * 12
            d.ellipse([dx - r, 830 - r // 2, dx + r, 830 + r // 2],
                      fill=(120, 90, 60, int(26 * (1 - hk) * (1 - i / 6))))
        canvas.alpha_composite(dov)
    # character
    ck = spring(seg(t, 0.45, 1.7))
    if ck > 0:
        zoom = 1.0 + 0.05 * eio(seg(t, 1.7, 10.2))
        draw_char(canvas, 1, 1330, 1052, 840, t, alpha=eoc(seg(t, 0.45, 1.3)), scale=lerp(0.94, 1.0, ck) * zoom)
    return canvas

def beat2(canvas, t):
    pan = eio(seg(t, 10.1, 19.4))
    bg_photo(canvas, 'plain', t, scale=1.14, px=lerp(-40, 40, pan), py=lerp(-8, 8, pan), desat=0.42, darken=0.34)
    # map card
    mk = eback(seg(t, 10.7, 11.7))
    if mk > 0:
        card = fit(bg('paper'), 660, 460).convert('RGBA')
        m = Image.new('RGBA', card.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(m)
        d.rounded_rectangle([0, 0, card.size[0] - 1, card.size[1] - 1], radius=20, fill=(255, 255, 255, 255))
        card.putalpha(m.getchannel('A'))
        ov = Image.new('RGBA', card.size, (0, 0, 0, 0))
        dd = ImageDraw.Draw(ov)
        L = lambda gx, gy: (gx - 230, gy - 240)
        cx0, cy0 = 560, 470
        outline = [L(cx0 - 210, cy0 - 60), L(cx0 - 120, cy0 - 140), L(cx0 + 40, cy0 - 150),
                   L(cx0 + 170, cy0 - 90), L(cx0 + 220, cy0 + 10), L(cx0 + 130, cy0 + 110),
                   L(cx0 - 40, cy0 + 140), L(cx0 - 180, cy0 + 80)]
        dd.polygon(outline, fill=CRIMSON + (int(38 * mk),), outline=INK + (int(150 * mk),))
        rp = eoc(seg(t, 11.5, 15.5))
        routes = [[L(cx0 - 260, cy0 - 160), L(cx0 - 140, cy0 - 60), L(cx0, cy0)],
                  [L(cx0 + 270, cy0 - 140), L(cx0 + 120, cy0 - 40), L(cx0, cy0)],
                  [L(cx0 - 240, cy0 + 170), L(cx0 - 100, cy0 + 80), L(cx0, cy0)]]
        for r in routes:
            pts = []
            for i in range(25):
                u = i / 24
                if u > rp: break
                p0, p1, p2 = r
                x = (1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0]
                y = (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]
                pts.append((x, y))
            if len(pts) > 1:
                dd.line(pts, fill=GOLDD + (int(200 * mk),), width=4)
        for i, (gx, gy) in enumerate([(cx0 - 260, cy0 - 160), (cx0 + 270, cy0 - 140), (cx0 - 240, cy0 + 170),
                                      (cx0 - 60, cy0 - 100), (cx0 + 90, cy0 + 60), (cx0 - 130, cy0 + 30), (cx0 + 30, cy0 - 60)]):
            pk = eback(seg(t, 12.0 + i * 0.28, 12.5 + i * 0.28))
            if pk > 0:
                dx, dy = L(gx, gy)
                r = 9 * pk
                dd.ellipse([dx - r, dy - r, dx + r, dy + r], fill=CRIMSON + (int(235 * pk),),
                           outline=INK + (int(180 * pk),), width=2)
        lx, ly = L(cx0, cy0)
        dd.ellipse([lx - 13, ly - 13, lx + 13, ly + 13], fill=GOLD + (int(255 * mk),), outline=INK + (200,), width=3)
        card = Image.alpha_composite(card, ov)
        tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        paste(tmp, card, 560, 470, alpha=0.94 * mk, scale=lerp(0.9, 1.0, mk), rot=-2)
        canvas.alpha_composite(tmp)
    # props stagger w/ labels
    props = [('turban', 'کلاهِ سرخ', 12.1, 1150, 330), ('sword', 'شمشیرِ تیز', 12.9, 1160, 560), ('flag', 'پرچم', 13.7, 1155, 790)]
    for name, label, t0, px_, py_ in props:
        k = eback(seg(t, t0, t0 + 0.6))
        if k > 0:
            im = fit(prop(name), 190, 190)
            paste(canvas, im, px_, py_, alpha=k, scale=lerp(0.6, 1.0, k), rot=-4)
            chip(canvas, label, px_, py_ + 118, size=30, weight=700, bg=DEEPRED, fg=CREAM,
                 alpha=eoc(seg(t, t0 + 0.25, t0 + 0.7)))
    # character
    ck = eoc(seg(t, 10.55, 11.3))
    if ck > 0:
        cx = lerp(2020, 1660, eoc(seg(t, 10.55, 11.5))) - 8 * (pan - 0.5) * 2
        draw_char(canvas, 3, cx, 1052, 800, t, alpha=ck)
    return canvas

def beat3(canvas, t):
    g = Image.new('RGBA', (W, H), DBLUE + (255,))
    gd = ImageDraw.Draw(g)
    for y in range(0, H, 4):
        k = y / H
        gd.rectangle([0, y, W, y + 4], fill=(int(lerp(24, 46, k)), int(lerp(34, 30, k)), int(lerp(52, 26, k)), 255))
    canvas.alpha_composite(g)
    pp = cover(bg('paper'), W, H)
    pp.putalpha(pp.getchannel('A').point(lambda v: 46))
    canvas.alpha_composite(pp.convert('RGBA'), (0, 0))
    rng = random.Random(3)
    sov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(sov)
    for i in range(40):
        x, y = rng.randint(0, W), rng.randint(0, 500)
        d.ellipse([x, y, x + 2, y + 2], fill=(240, 230, 200, rng.randint(20, 60)))
    canvas.alpha_composite(sov)
    # growing gold glow
    gk = eio(seg(t, 19.5, 24.5))
    if gk > 0:
        glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        gd2 = ImageDraw.Draw(glow)
        r = lerp(180, 760, gk)
        for i in range(14, 0, -1):
            rr = r * i / 14
            gd2.ellipse([960 - rr, 470 - rr, 960 + rr, 470 + rr], fill=GOLD + (int(9 * (15 - i) / 15 * 8),))
        glow = glow.filter(ImageFilter.GaussianBlur(30))
        canvas.alpha_composite(glow)
    # rays
    rk = eoc(seg(t, 21.5, 24.5))
    if rk > 0:
        rov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(rov)
        for i in range(12):
            a = math.pi * i / 6 + 0.26
            l0, l1 = 150, lerp(150, 620, rk)
            d.line([(960 + l0 * math.cos(a), 470 + l0 * math.sin(a)),
                    (960 + l1 * math.cos(a), 470 + l1 * math.sin(a))],
                   fill=GOLD + (int(90 * rk),), width=3)
        canvas.alpha_composite(rov)
    # emblem (symbolic only: 12-point star + crown, no face)
    ek = spring(seg(t, 19.6, 21.2))
    if ek > 0:
        tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(tmp)
        star12(dd, 960, 450, 150 * ek, 96 * ek, GOLD, alpha=int(235 * ek), rot=t * 0.02)
        star12(dd, 960, 450, 96 * ek, 60 * ek, DEEPRED, alpha=int(255 * ek), rot=t * 0.02)
        crown(dd, 960, 330 - 20 * (1 - ek), 120 * ek, 70 * ek, GOLD, alpha=int(240 * ek))
        canvas.alpha_composite(tmp)
        chip(canvas, "شاه‌اسماعیل", 960, 640, size=44, weight=900, bg=DEEPRED, fg=GOLD,
             alpha=eoc(seg(t, 21.0, 21.8)))
    # camera push-in
    push = eio(seg(t, 21.5, 25.8))
    ck = eoc(seg(t, 19.35, 20.1))
    if ck > 0:
        draw_char(canvas, 1, lerp(430, 470, push), 1052, lerp(780, 850, push), t, alpha=ck)
    return canvas

def beat4(canvas, t):
    bg_paper(canvas, tint=(30, 18, 12, 120), darken=0.38, soft=True)
    d = ImageDraw.Draw(canvas)
    push = eio(seg(t, 26.1, 31.0))
    if t < 27.30:      # جنگ
        k = eback(seg(t, 26.15, 26.75))
        s1 = fit(prop('sword'), 430, 430)
        paste(canvas, s1, 900, 500, alpha=k, scale=lerp(1.35, 1.0, k), rot=58)
        s2 = s1.transpose(Image.FLIP_LEFT_RIGHT)
        paste(canvas, s2, 1020, 500, alpha=k, scale=lerp(1.35, 1.0, k), rot=-58)
        sk = seg(t, 26.35, 26.9)
        if 0 < sk < 1:
            for i in range(10):
                a = math.pi * 2 * i / 10 + 0.3
                l = lerp(30, 240, eoc(sk))
                d.line([(960 + 20 * math.cos(a), 440 + 20 * math.sin(a)),
                        (960 + l * math.cos(a), 440 + l * math.sin(a))],
                       fill=(255, 236, 180, int(220 * (1 - sk))), width=5)
        chip(canvas, "جنگ", 960, 830, size=64, weight=900, bg=CRIMSON, fg=CREAM,
             alpha=eback(seg(t, 26.4, 27.0)))
    elif t < 28.50:   # پیروزی
        k = eoq(seg(t, 27.35, 28.1))
        fl = fit(prop('flag'), 300, 420)
        paste(canvas, fl, 960, lerp(760, 470, k), alpha=eoc(seg(t, 27.35, 27.7)))
        d.line([(960 - 4, lerp(760, 470, k) + 150), (960 - 4, 940)], fill=BROWN + (255,), width=9)
        chip(canvas, "پیروزی", 960, 850, size=64, weight=900, bg=GOLDD, fg=INK,
             alpha=eback(seg(t, 27.6, 28.2)))
    elif t < 29.70:   # منصب
        k = eback(seg(t, 28.55, 29.15))
        dec = fit(prop('decree'), 380, 460)
        paste(canvas, dec, 960, 520, alpha=eoc(seg(t, 28.55, 28.9)), scale=lerp(0.9, 1.0, k), rot=2)
        stk = eback(seg(t, 29.15, 29.55))
        if stk > 0:
            d.ellipse([1040 - 62 * stk, 610 - 62 * stk, 1040 + 62 * stk, 610 + 62 * stk],
                      fill=CRIMSON + (int(225 * stk),), outline=DEEPRED + (255,), width=6)
        chip(canvas, "منصب", 960, 850, size=64, weight=900, bg=DEEPRED, fg=GOLD,
             alpha=eback(seg(t, 28.8, 29.4)))
    else:             # قدرت
        k = eoc(seg(t, 29.75, 30.2))
        rov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(rov)
        for i in range(16):
            a = math.pi * 2 * i / 16 + t * 0.15
            l = lerp(240, 420, eoc(seg(t, 29.75, 30.6)))
            d.line([(1180 + 160 * math.cos(a), 560 + 160 * math.sin(a)),
                    (1180 + l * math.cos(a), 560 + l * math.sin(a))],
                   fill=GOLD + (int(70 * k),), width=4)
        canvas.alpha_composite(rov)
        draw_char(canvas, 4, 1180, 1052, lerp(880, 830, push), t, alpha=k, scale=lerp(1.06, 1.0, k))
        chip(canvas, "قدرت", 620, 560, size=64, weight=900, bg=GOLDD, fg=INK,
             alpha=eback(seg(t, 29.9, 30.5)))
    return canvas

def beat5(canvas, t):
    bg_photo(canvas, 'council', t, scale=1.12, px=10, py=6, desat=0.5, darken=0.40, blur=2)
    freeze = 36.70 <= t < 37.96
    pulse = 1.0
    if freeze:
        pulse = 1.0 + 0.02 * math.sin((t - 36.70) * 2 * math.pi * 2.2)
    # chair
    ck = spring(seg(t, 32.3, 33.3))
    if ck > 0:
        ch = fit(prop('chair'), 330, 380)
        shov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(shov)
        d.ellipse([1250 - 170, 900 - 34, 1250 + 170, 900 + 34], fill=(15, 9, 6, 110))
        canvas.alpha_composite(shov)
        paste(canvas, ch, 1250, 760, alpha=eoc(seg(t, 32.3, 32.7)), scale=lerp(0.5, 1.0, ck) * pulse)
        spot = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(spot)
        sd.ellipse([1250 - 240, 760 - 300, 1250 + 240, 760 + 300], fill=(255, 226, 150, 26))
        spot = spot.filter(ImageFilter.GaussianBlur(60))
        canvas.alpha_composite(spot)
    # character walks toward chair (2D translate only)
    enter = eoc(seg(t, 31.1, 31.8))
    if enter > 0:
        cx = lerp(430, 760, eio(seg(t, 33.4, 34.6)))
        draw_char(canvas, 2, cx, 1052, 800 * pulse, t, alpha=enter, freeze=freeze)
    return canvas

def beat6(canvas, t):
    bg_photo(canvas, 'council', t, scale=1.10, px=-6, py=0, desat=0.55, darken=0.46)
    hold = 45.04 <= t < 46.70
    cards = [(1, 'سردارِ یکم', CRIMSON, 330), (3, 'سردارِ دوم', DBLUE, 760),
             (4, 'سردارِ سوم', BROWN, 1180), (2, 'سردارِ چهارم', GOLDD, 1590)]
    jit = 0
    if 47.14 <= t < 47.80:
        jit = math.sin(t * 60) * 12
    for idx, (pi, label, tint, x0) in enumerate(cards):
        k = eback(seg(t, 38.4 + idx * 0.4, 39.0 + idx * 0.4))
        if k <= 0: continue
        # competition: slide toward center + slight scale
        comp = eio(seg(t, 41.0, 44.0))
        x = lerp(x0, lerp(x0, 960, 0.30), comp) + (jit if idx % 2 == 0 else -jit) * seg(t, 47.14, 47.2)
        y = lerp(545, 525, comp) + lerp(70, 0, k)
        sc = lerp(0.9, 1.0, k) * lerp(1.0, 1.06, comp)
        cw, chh = int(340 * sc), int(450 * sc)
        card = Image.new('RGBA', (cw, chh), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)
        cd.rounded_rectangle([0, 0, cw - 1, chh - 1], radius=22, fill=tint + (235,))
        cd.rounded_rectangle([8, 8, cw - 9, chh - 9], radius=18, outline=CREAM + (140,), width=3)
        pim = fit(pose(pi), cw - 40, chh - 120)
        card.alpha_composite(pim, ((cw - pim.size[0]) // 2, 20))
        f = font(700, 30)
        cd.text((cw // 2, chh - 52), fa(label), font=f, fill=CREAM + (255,), anchor='mm')
        paste(canvas, card, x, y, alpha=eoc(seg(t, 38.4 + idx * 0.4, 38.8 + idx * 0.4)) * k, scale=1.0)
    if hold:
        canvas.alpha_composite(Image.new('RGBA', (W, H), (10, 6, 4, 70)))
    return canvas

def beat7(canvas, t):
    g = Image.new('RGBA', (W, H), DBLUE + (255,))
    gd = ImageDraw.Draw(g)
    for y in range(0, H, 4):
        k = y / H
        gd.rectangle([0, y, W, y + 4], fill=(int(lerp(30, 52, k)), int(lerp(40, 34, k)), int(lerp(58, 30, k)), 255))
    canvas.alpha_composite(g)
    pp = cover(paper_hp(), W, H).convert('RGBA')
    pp.putalpha(pp.getchannel('A').point(lambda v: 40))
    canvas.alpha_composite(pp, (0, 0))
    cam = eio(seg(t, 48.0, 53.0))   # focused -> balanced
    zoom = lerp(1.10, 1.0, cam)
    tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    # divider
    dk = eoc(seg(t, 48.0, 48.6))
    if dk > 0:
        d.line([(960, lerp(540, 150, dk)), (960, lerp(540, 930, dk))], fill=CREAM + (90,), width=4)
    # left: qezelbash block
    lk = eoc(seg(t, 48.0, 48.8))
    if lk > 0:
        d.rounded_rectangle([150, 240, 800, 900], radius=26, fill=CRIMSON + (int(45 * lk),),
                            outline=CRIMSON + (int(150 * lk),), width=3)
    # right: new force shields
    for i, sx in enumerate((1160, 1380, 1600)):
        sk = eback(seg(t, 49.3 + i * 0.6, 49.9 + i * 0.6))
        if sk > 0:
            shield(d, sx, 420, 130 * sk, 160 * sk, DBLUE, alpha=int(235 * sk))
            d.line([(sx, 420 - 80 * sk - 60), (sx, 420 - 80 * sk)], fill=GOLD + (int(200 * sk),), width=6)
    chip(canvas, "قزلباش", 470, 205, size=40, weight=900, bg=CRIMSON, fg=CREAM, alpha=lk)
    chip(canvas, "نیروی تازه", 1380, 205, size=40, weight=900, bg=DBLUE, fg=CREAM,
         alpha=eoc(seg(t, 49.6, 50.2)))
    # power diagram
    nk = eoc(seg(t, 50.5, 51.2))
    if nk > 0:
        nodes = [(960, 830, GOLD), (480, 760, CRIMSON), (1440, 760, DBLUE), (960, 640, BROWN)]
        c0 = nodes[0]
        for nx, ny, col in nodes[1:]:
            lk2 = eoc(seg(t, 51.0, 53.5))
            d.line([(c0[0], c0[1]), (lerp(c0[0], nx, lk2), lerp(c0[1], ny, lk2))],
                   fill=col + (int(190 * nk),), width=6)
        for i, (nx, ny, col) in enumerate(nodes):
            pk = eback(seg(t, 50.5 + i * 0.5, 51.0 + i * 0.5))
            if pk > 0:
                r = 34 * pk
                d.ellipse([nx - r, ny - r, nx + r, ny + r], fill=col + (int(240 * pk),),
                          outline=CREAM + (int(160 * pk),), width=3)
    canvas.alpha_composite(tmp)
    ck = eoc(seg(t, 48.1, 48.9))
    if ck > 0:
        draw_char(canvas, 4, lerp(560, 470, cam), 900, lerp(640, 560, cam), t, alpha=ck)
    # camera zoom applied by cropping
    if zoom > 1.001:
        sw, sh = int(W / zoom), int(H / zoom)
        canvas2 = canvas.crop(((W - sw) // 2, (H - sh) // 2 - 30, (W - sw) // 2 + sw, (H - sh) // 2 - 30 + sh))
        canvas.paste(canvas2.resize((W, H), Image.LANCZOS), (0, 0))
    return canvas

def beat8(canvas, t):
    if t < 68.30:
        bg_paper(canvas, tint=(20, 13, 9, 165), darken=0.46, soft=True)
        shake = math.exp(-max(0, t - 56.25) * 6) * 10 if t > 56.2 else 0
        if shake > 0.3:
            canvas.alpha_composite(Image.new('RGBA', (1, 1), (0, 0, 0, 0)))
        # phrase cards
        c1 = eback(seg(t, 57.8, 58.5))
        if c1 > 0:
            chip(canvas, "رسیدن به قدرت: یک جنگ", 500, 290, size=52, weight=900, bg=CRIMSON, fg=CREAM,
                 alpha=eoc(seg(t, 57.8, 58.2)) * (1 - seg(t, 63.0, 63.5)))
        c2 = eback(seg(t, 60.6, 61.3))
        if c2 > 0:
            chip(canvas, "نگه‌داشتنش: هزار جنگ", 1420, 290, size=52, weight=900, bg=DEEPRED, fg=GOLD,
                 alpha=eoc(seg(t, 60.6, 61.0)) * (1 - seg(t, 63.0, 63.5)))
        freeze = t >= 66.16
        pulse = 1.0 + (0.02 * math.sin((t - 66.16) * 2 * math.pi * 2.2) if freeze else 0.0)
        # character: pose4 -> pose2 at 63.7, translate toward hat 65.3
        cx = lerp(960, 1120, eio(seg(t, 65.3, 66.1)))
        if t < 63.7:
            draw_char(canvas, 4, cx, 1046, 760 * pulse, t, alpha=eoc(seg(t, 56.3, 57.0)), freeze=freeze)
        else:
            char_swap(canvas, 4, 2, cx, 1046, 760 * pulse, t, 63.7, freeze=freeze)
        # hat
        hk = eback(seg(t, 64.5, 65.3))
        if hk > 0:
            hat = fit(prop('turban'), 240, 200)
            glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow)
            gd.ellipse([1420 - 190, 360 - 190, 1420 + 190, 360 + 190], fill=(255, 226, 150, 40))
            glow = glow.filter(ImageFilter.GaussianBlur(50))
            canvas.alpha_composite(glow)
            paste(canvas, hat, 1420, lerp(-160, 360, hk), alpha=eoc(seg(t, 64.5, 64.9)), scale=lerp(0.8, 1.0, hk) * pulse)
        return canvas
    else:
        # paper transition out -> end card
        k = seg(t, 68.30, 69.50)
        bg_paper(canvas, tint=(20, 13, 9, 165), darken=0.46, soft=True)
        freeze = True
        cx = 1120
        char_swap(canvas, 4, 2, cx, 1046, 760, t, 63.7, freeze=freeze)
        hat = fit(prop('turban'), 240, 200)
        paste(canvas, hat, 1420, 360, freeze if False else 1.0)
        # paper wipe
        mask = PAPER_MASK
        thr = int(k * 340 - 40)
        m = mask.point(lambda v: 255 if v < thr else 0)
        m = m.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2)).resize((W, H), Image.BILINEAR)
        pp = cover(bg('paper'), W, H).convert('RGBA')
        card = pp
        canvas.paste(card, (0, 0), m.point(lambda v: int(v * k)))
        if k > 0.55:
            ek = eoc(seg(t, 69.5, 70.1))
            tk = eback(seg(t, 69.7, 70.3))
            if tk > 0:
                hat2 = fit(prop('turban'), 150, 130)
                paste(canvas, hat2, 960, 330, alpha=ek, scale=tk)
            text_block(canvas, "پایان", 960, 480, size=110, weight=900, fill=INK,
                       alpha=eoc(seg(t, 69.7, 70.3)), shadow=False)
            text_block(canvas, "تاریخ، همیشه هم جدی نیست!", 960, 610, size=44, weight=500,
                       fill=DEEPRED, alpha=eoc(seg(t, 70.1, 70.7)), shadow=False)
        fo = seg(t, 70.9, 71.5)
        if fo > 0:
            canvas.alpha_composite(Image.new('RGBA', (W, H), (6, 4, 3, int(255 * eio(fo)))))
        return canvas

BEATS = [
    (0.00, 10.70, beat1, None, 0.0),
    (10.10, 19.45, beat2, 'paperwipe', 0.60),
    (18.90, 26.35, beat3, 'radial', 0.55),
    (26.10, 31.30, beat4, 'flashcut', 0.35),
    (30.95, 38.45, beat5, 'whip', 0.50),
    (37.95, 48.05, beat6, 'paperwipe', 0.50),
    (47.55, 56.45, beat7, 'dissolve', 0.55),
    (55.90, 71.50, beat8, None, 0.0),
]

def render_beat(i, t):
    c = Image.new('RGBA', (W, H), (12, 8, 6, 255))
    BEATS[i][3 - 3](c, t) if False else BEATS[i][2](c, t)
    return c

PAPER_MASK = cover(bg('paper'), W, H).convert('L')

def transition_mask(kind, k):
    if kind == 'dissolve':
        return None, k
    if kind == 'paperwipe':
        thr = int(k * 420 - 60)
        m = PAPER_MASK.point(lambda v: 255 if v < thr else 0)
        m = m.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2)).resize((W, H), Image.BILINEAR)
        return m, None
    if kind == 'radial':
        m = Image.new('L', (W, H), 0)
        d = ImageDraw.Draw(m)
        r = k * 1500
        d.ellipse([960 - r, 540 - r, 960 + r, 540 + r], fill=255)
        return m.filter(ImageFilter.GaussianBlur(30)), None  # radial: geometric, blur ok
    if kind == 'flashcut':
        return None, 1.0 if k > 0.5 else 0.0
    if kind == 'whip':
        return None, eio(k)
    return None, k

def frame(t):
    c = Image.new('RGBA', (W, H), (12, 8, 6, 255))
    # find active beat & transition blend
    idx = 0
    for i, (s, e, fn, tr, td) in enumerate(BEATS):
        if t >= s:
            idx = i
    a = BEATS[idx]
    if idx > 0 and t < BEATS[idx - 1][1]:
        # in overlap window: blend prev -> cur
        prev = BEATS[idx - 1]
        kind, td = prev[3], prev[4]
        k = seg(t, prev[1] - td, prev[1])
        img_a = render_beat(idx - 1, t)
        img_b = render_beat(idx, t)
        m, alpha = transition_mask(kind, k)
        if kind == 'whip':
            off = int(lerp(0, W, alpha))
            c.paste(img_a, (-off, 0))
            c.paste(img_b, (W - off, 0))
        elif m is not None:
            c = Image.composite(img_b, img_a, m).convert('RGBA')
        elif kind == 'flashcut':
            c = img_b if alpha >= 1 else img_a
            if 0.35 < k < 0.65:
                c.alpha_composite(Image.new('RGBA', (W, H), (255, 246, 220, 120)))
        else:
            c = Image.blend(img_a, img_b, alpha).convert('RGBA')
    else:
        c = render_beat(idx, t)
        if idx > 0 and BEATS[idx - 1][3] == 'flashcut':
            kk = seg(t, BEATS[idx][0], BEATS[idx][0] + 0.12)
            if kk < 1:
                c.alpha_composite(Image.new('RGBA', (W, H), (255, 246, 220, int(140 * (1 - kk)))))
    # frame-level shake on music hits
    shake_t = [(7.30, 0.30, 7), (26.35, 0.25, 9), (29.15, 0.25, 8), (56.25, 0.35, 10), (61.95, 0.30, 8)]
    dx = dy = 0
    for ts, dur, amp in shake_t:
        if ts <= t < ts + dur:
            kk = 1 - (t - ts) / dur
            dx = math.sin((t - ts) * 70) * amp * kk
            dy = math.cos((t - ts) * 55) * amp * 0.6 * kk
    if dx or dy:
        c2 = Image.new('RGBA', (W, H), (12, 8, 6, 255))
        c2.paste(c, (int(dx), int(dy)))
        c = c2
    subtitles(c, t)
    c = grade(c, t)
    return c.convert('RGB')

def render_frame_idx(fi):
    t = fi / FPS
    im = frame(min(t, T_END - 1e-4))
    im.save(os.path.join(OUT, '%05d.png' % fi))
    return fi

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'still':
        for ts in [float(x) for x in sys.argv[2:]]:
            im = frame(ts)
            p = os.path.join(ROOT, 'out', 'still_%05.2f.png' % ts)
            im.save(p)
            print('saved', p)
    elif len(sys.argv) > 2 and sys.argv[1] == 'range':
        from multiprocessing import Pool
        a, b = int(sys.argv[2]), int(sys.argv[3])
        with Pool(min(8, os.cpu_count() or 4)) as p:
            for _ in p.imap_unordered(render_frame_idx, range(a, b), chunksize=8):
                pass
        print('rendered range', a, b)
    else:
        from multiprocessing import Pool
        nframes = int(T_END * FPS)
        with Pool(min(8, os.cpu_count() or 4)) as p:
            for _ in p.imap_unordered(render_frame_idx, range(nframes), chunksize=8):
                pass
        print('rendered', nframes, 'frames')
