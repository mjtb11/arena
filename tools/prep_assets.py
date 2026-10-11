#!/usr/bin/env python3
"""Prepare assets: remove flat background from character poses & prop sprites,
slice the prop sprite-sheet, normalize backgrounds, copy Persian fonts."""
import os, sys, collections
from collections import deque
from PIL import Image

ROOT = '/home/user/arena'
OUT = os.path.join(ROOT, 'video', 'public', 'assets')
for d in ('char', 'props', 'bg'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)
os.makedirs(os.path.join(ROOT, 'video', 'public', 'fonts'), exist_ok=True)


def bg_color(im):
    px = im.convert('RGB').load()
    w, h = im.size
    cnt = collections.Counter()
    for x in range(0, w, 2):
        cnt[px[x, 0]] += 1
        cnt[px[x, h - 1]] += 1
    for y in range(0, h, 2):
        cnt[px[0, y]] += 1
        cnt[px[w - 1, y]] += 1
    return cnt.most_common(1)[0][0]


def cut(im, eps=25):
    """Flood-fill (border-connected) removal of flat near-background color."""
    im = im.convert('RGB')
    w, h = im.size
    px = im.load()
    bg = bg_color(im)
    near = bytearray(w * h)
    for y in range(h):
        row = y * w
        for x in range(w):
            c = px[x, y]
            if abs(c[0] - bg[0]) <= eps and abs(c[1] - bg[1]) <= eps and abs(c[2] - bg[2]) <= eps:
                near[row + x] = 1
    seen = bytearray(w * h)
    dq = deque()
    for x in range(w):
        for i in (x, (h - 1) * w + x):
            if near[i] and not seen[i]:
                seen[i] = 1
                dq.append(i)
    for y in range(h):
        for i in (y * w, y * w + w - 1):
            if near[i] and not seen[i]:
                seen[i] = 1
                dq.append(i)
    while dq:
        i = dq.popleft()
        x = i % w
        for j in (i - 1, i + 1, i - w, i + w):
            if j < 0 or j >= w * h or seen[j] or not near[j]:
                continue
            if j == i - 1 and x == 0:
                continue
            if j == i + 1 and x == w - 1:
                continue
            seen[j] = 1
            dq.append(j)
    out = Image.new('RGBA', (w, h))
    op = out.load()
    for y in range(h):
        for x in range(w):
            i = y * w + x
            if seen[i]:
                op[x, y] = (0, 0, 0, 0)
            else:
                c = px[x, y]
                op[x, y] = (c[0], c[1], c[2], 255)
    return out


def bbox_crop(im):
    bb = im.getbbox()  # uses alpha
    return im.crop(bb) if bb else im


print('== character poses ==')
for i in (1, 2, 3, 4):
    src = os.path.join(ROOT, f'character_pose_0{i}.png')
    im = cut(Image.open(src))
    im = bbox_crop(im)
    dst = os.path.join(OUT, 'char', f'pose_0{i}.png')
    im.save(dst)
    print(f'pose_0{i}: {im.size} -> {dst}')

print('== prop sprite sheet ==')
sheet = cut(Image.open(os.path.join(ROOT, 'Create_historical_objects_asset___20261011180824-removebg-preview.png')))
W, H = sheet.size
cells = {
    'horse':   (0, 0, W // 2, 150),
    'sword':   (W // 2, 0, W, 150),
    'flag':    (0, 150, W // 2, 278),
    'decree':  (W // 2, 150, W, 278),
    'chair':   (0, 278, W // 2, H),
    'turban':  (W // 2, 278, W, H),
}
for name, box in cells.items():
    sub = bbox_crop(sheet.crop(box))
    dst = os.path.join(OUT, 'props', f'{name}.png')
    sub.save(dst)
    print(f'{name}: {sub.size} -> {dst}')

print('== backgrounds ==')
bgs = {
    'paper':   '2Q6OF47g2vOG_Y6NK8q09zpEF6I-t0OZDyqzSyKiVHa5Qh7jww.png',
    'plain':   'LFkhz58kGjdjr8EbsojhqO6tw-Q-GgZRwvB4S-O7_y_odGV1zQ.png',
    'council': 'tIl-e-YKy1PkAmpxcPdR-FgXvao-y__eEcPuTCSh5BsWrfIffw.png',
}
for name, fn in bgs.items():
    im = Image.open(os.path.join(ROOT, fn)).convert('RGB')
    dst = os.path.join(OUT, 'bg', f'{name}.jpg')
    im.save(dst, quality=90)
    print(f'{name}: {im.size} -> {dst} ({os.path.getsize(dst)//1024} KB)')

print('== fonts ==')
fsrc = os.path.join(ROOT, 'video', 'node_modules', '@fontsource', 'vazirmatn', 'files')
fdst = os.path.join(ROOT, 'video', 'public', 'fonts')
for weight in (400, 500, 700, 800, 900):
    for subset in ('arabic', 'latin'):
        fn = f'vazirmatn-{subset}-{weight}-normal.woff2'
        src = os.path.join(fsrc, fn)
        if os.path.exists(src):
            import shutil
            shutil.copy(src, os.path.join(fdst, fn))
print('fonts copied:', sorted(os.listdir(fdst)))
