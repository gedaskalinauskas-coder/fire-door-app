#!/usr/bin/env python3
"""Build the PWA icons (icons/icon-192.png, icon-512.png, icon-maskable-192.png,
icon-maskable-512.png) from icons/apple-touch-icon.png, using the colours in the
BRAND block of index.html.  Run from the repo root:  python3 tools/make-icons.py
(needs Pillow + numpy).  Re-run after replacing apple-touch-icon.png for a new brand."""
import re, os
import numpy as np
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
def col(k):
    return re.search(r"\b" + k + r":'(#[0-9a-fA-F]{6})'", src).group(1)
hexrgb = lambda h: tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
BLACK = hexrgb(col('black'))

base = Image.open(os.path.join(ROOT, 'icons/apple-touch-icon.png')).convert('RGB')
a = np.asarray(base).astype(float)
YEL, PINK = hexrgb(col('yellow')), hexrgb(col('pink'))
bg = a[2, 2]
def soft(c):
    # 0..1 coverage of brand colour c against the background, per pixel
    c = np.array(c, float); d = c - bg
    t = ((a - bg) * d).sum(2) / (d * d).sum()
    near = np.abs(a - (bg + t[..., None] * d)).sum(2) < 90
    return np.clip(t, 0, 1) * near
masks = {YEL: soft(YEL), PINK: soft(PINK)}
union = np.maximum(*masks.values()) > .5
ys, xs = np.where(union)
x0, x1, y0, y1 = int(xs.min()), int(xs.max()) + 1, int(ys.min()), int(ys.max()) + 1
cx, cy = (x0 + x1) / 2 / base.width, (y0 + y1) / 2 / base.height  # keep the original placement
h_ratio = (y1 - y0) / base.height
from PIL import ImageFilter

def render(size, scale, centre):
    SS = 4  # supersample, smooth and re-threshold so upscaled edges are clean, not blocky
    S = size * SS
    out = Image.new('RGB', (S, S), BLACK)
    th = int(S * h_ratio * scale); tw = int(th * (x1 - x0) / (y1 - y0))
    px = int(S * centre[0] - tw / 2); py = int(S * centre[1] - th / 2)
    for c, m in masks.items():
        im = Image.fromarray((m[y0:y1, x0:x1] * 255).astype('uint8')).resize((tw, th), Image.BICUBIC)
        im = im.filter(ImageFilter.GaussianBlur(float(th / (y1 - y0) * 0.7))).point(lambda v: 255 if v > 127 else 0)
        out.paste(Image.new('RGB', (tw, th), c), (px, py), im)
    return out.resize((size, size), Image.LANCZOS)

for n in (192, 512):
    render(n, 1.0, (cx, cy)).save(os.path.join(ROOT, f'icons/icon-{n}.png'), optimize=True)
    # maskable: mark shrunk and centred inside the 80% safe zone
    render(n, 0.78, (0.5, 0.5)).save(os.path.join(ROOT, f'icons/icon-maskable-{n}.png'), optimize=True)
print('icons written')
