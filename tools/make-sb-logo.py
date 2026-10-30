#!/usr/bin/env python3
"""Draw the 'SB' letter-mark logos for S B Fire Door App in the existing brand colours
(yellow #dcca1c, pink #e53376 on black), using Montserrat ExtraBold.  Writes:
  icons/logo-wordmark.png  (600 px wide, soft drop shadow, for dark backgrounds; also embedded as LOGO_SRC)
  /tmp/sb-logo-flat.png    (1200 px wide, flat, for white backgrounds; embedded as LOGO_FLAT_SRC)
  icons/apple-touch-icon.png, icons/favicon-16/32.png, icons/favicon.ico
Then run tools/make-icons.py for the PWA icons.  Run from the repo root."""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.environ.get('SB_FONT', '/usr/share/fonts/truetype/sand-box/google/Montserrat/Montserrat-VariableFont_wght.ttf')
YEL, PINK, BG = (0xdc, 0xca, 0x1c), (0xe5, 0x33, 0x76), (0x0b, 0x0b, 0x0b)

def font(size, w=800):
    f = ImageFont.truetype(FONT, size)
    try: f.set_variation_by_axes([w])
    except Exception: pass
    return f

def mark(scale=1.0):
    """'SB' big in yellow + 'FIRE DOOR' / 'APP' stacked in pink on the right; transparent RGBA, tight crop."""
    S = int(400 * scale)
    W, H = int(S * 4.5), int(S * 1.4)
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    fb = font(S, 800)
    bb = d.textbbox((0, 0), 'SB', font=fb)
    x0, y0 = int(S * .05) - bb[0], int(S * .1) - bb[1]
    d.text((x0, y0), 'SB', font=fb, fill=YEL + (255,))
    capH = bb[3] - bb[1]; right = x0 + bb[2] + int(S * .09)
    fs = font(int(S * .42), 800)
    l1 = d.textbbox((0, 0), 'FIRE DOOR', font=fs); l2 = d.textbbox((0, 0), 'APP', font=fs)
    ch = l1[3] - l1[1]; gap = capH - 2 * ch
    top = int(S * .1)
    d.text((right - l1[0], top - l1[1]), 'FIRE DOOR', font=fs, fill=PINK + (255,))
    d.text((right - l2[0], top + ch + gap - l2[1]), 'APP', font=fs, fill=PINK + (255,))
    return im.crop(im.getbbox())

def shadowed(m, width):
    pad = int(m.width * .06)
    c = Image.new('RGBA', (m.width + 2 * pad, m.height + 2 * pad), (0, 0, 0, 0))
    a = Image.new('L', c.size, 0); a.paste(m.split()[3], (pad + 6, pad + 10))
    sh = Image.new('RGBA', c.size, (0, 0, 0, 255)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(pad * .45)).point(lambda v: int(v * .75)))
    c = Image.alpha_composite(c, sh); c.alpha_composite(m, (pad, pad))
    return c.resize((width, round(c.height * width / c.width)), Image.LANCZOS)

m = mark(1.5)
shadowed(m, 600).save(os.path.join(ROOT, 'icons/logo-wordmark.png'), optimize=True)
m.resize((1200, round(m.height * 1200 / m.width)), Image.LANCZOS).save('/tmp/sb-logo-flat.png', optimize=True)

def icon(size, rounded=False):
    SS = 4; N = size * SS
    im = Image.new('RGBA', (N, N), BG + (255,)); d = ImageDraw.Draw(im)
    f = font(int(N * .56), 800); bb = d.textbbox((0, 0), 'SB', font=f)
    tw_, th = bb[2] - bb[0], bb[3] - bb[1]
    if tw_ > N * .78: f = font(int(N * .56 * N * .78 / tw_), 800); bb = d.textbbox((0, 0), 'SB', font=f); tw_, th = bb[2] - bb[0], bb[3] - bb[1]
    ty = int(N * .43 - th / 2)
    d.text(((N - tw_) / 2 - bb[0], ty - bb[1]), 'SB', font=f, fill=YEL + (255,))
    bw, bh = int(tw_ * .92), int(N * .09); by = ty + th + int(N * .1)
    d.rectangle([(N - bw) // 2, by, (N + bw) // 2, by + bh], fill=PINK + (255,))
    if rounded:
        mk = Image.new('L', (N, N), 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, N - 1, N - 1], radius=int(N * .2), fill=255)
        im.putalpha(mk)
    return im.resize((size, size), Image.LANCZOS)

icon(180).convert('RGB').save(os.path.join(ROOT, 'icons/apple-touch-icon.png'), optimize=True)
icon(32, True).save(os.path.join(ROOT, 'icons/favicon-32.png'), optimize=True)
icon(16, True).save(os.path.join(ROOT, 'icons/favicon-16.png'), optimize=True)
icon(48, True).save(os.path.join(ROOT, 'icons/favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])
print('SB logos written')
