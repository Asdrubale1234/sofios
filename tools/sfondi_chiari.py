#!/usr/bin/env python3
"""Varianti dello sfondo chiaro di SofiOS (stesso mare a fasce dello sfondo scuro, con la stessa mascotte).
Uso: sfondi_chiari.py CARTELLA_INCLUDES CARTELLA_USCITA"""
import os, sys
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
inc, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
W, H, S = 1920, 1080, 2          # disegno al doppio e poi riduco: bordi lisci
src = Image.open(os.path.join(inc, "usr/share/wallpapers/SofiOS/contents/images/1920x1080.png")).convert("RGB")
a = np.asarray(src).astype(float)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
m = np.zeros((H, W), bool); reg = (slice(640, 940), slice(1500, 1760))
m[reg] = ~((r < 70) & (g < 105) & (b < 140))[reg]
im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
alpha = (np.asarray(im).astype(float) / 255)[..., None]

def sfumatura(h, c0, c1, y0=0, y1=None):
    y1 = y1 or h
    t = np.clip((np.arange(h) - y0) / max(1, (y1 - y0)), 0, 1)[:, None, None]
    return np.array(c0, float) * (1 - t) + np.array(c1, float) * t

def onda(x, y0, ampl, per, fase):
    return y0 + ampl * np.sin(2 * np.pi * x / per + fase) + ampl * 0.4 * np.sin(2 * np.pi * x / (per * 0.43) + fase * 2.1)

def scena(cielo, orizzonte, fasce, sole=None, nuvole=False, linee=(255, 255, 255)):
    w, h = W * S, H * S
    img = np.ones((h, w, 3)) * sfumatura(h, cielo[0], cielo[1], 0, int(orizzonte * h))
    if sole:
        cx, cy, rr, col = sole
        yy, xx = np.mgrid[0:h, 0:w]
        d = np.sqrt((xx - cx * S) ** 2 + (yy - cy * S) ** 2)
        alone = np.exp(-(d / (rr * S * 5.0)) ** 2)[..., None] * 0.55
        img = img * (1 - alone) + np.array(col, float) * alone
        disco = np.clip((rr * S - d) / 3, 0, 1)[..., None]
        img = img * (1 - disco) + np.array([255, 250, 235.]) * disco
    pil = Image.fromarray(img.astype(np.uint8))
    if nuvole:
        nv = Image.new("L", (w, h), 0); dr = ImageDraw.Draw(nv)
        for (x, y, k) in ((300, 180, 1.0), (760, 120, 0.7), (1250, 260, 0.9), (1600, 150, 0.6), (120, 380, 0.6)):
            for dx, dy, rr in ((0, 0, 60), (70, 14, 50), (-70, 18, 46), (30, -26, 48), (130, 26, 36), (-130, 28, 34)):
                dr.ellipse([(x + dx - rr * k) * S, (y + dy - rr * k * 0.7) * S, (x + dx + rr * k) * S, (y + dy + rr * k * 0.7) * S], fill=235)
        nv = nv.filter(ImageFilter.GaussianBlur(14 * S))
        pil = Image.composite(Image.new("RGB", (w, h), (255, 255, 255)), pil, nv.point(lambda v: int(v * 0.85)))
    img = np.asarray(pil).astype(float)
    x = np.arange(w) / S
    yy = np.arange(h)[:, None] / S
    hor = orizzonte * H
    for i, (col, y0, ampl, per, fase) in enumerate(fasce):
        lim = onda(x, hor + y0, ampl, per, fase)[None, :]
        sotto = np.clip((yy - lim) * S, 0, 1)[..., None]
        img = img * (1 - sotto) + np.array(col, float) * sotto
        # sottile riga chiara sul bordo di ogni onda, come nello sfondo scuro
        riga = np.clip(1 - np.abs(yy - lim) * S / 1.6, 0, 1)[..., None] * 0.55
        img = img * (1 - riga) + np.array(linee, float) * riga
    pil = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    o = np.asarray(pil).astype(float)
    return Image.fromarray(np.clip(o * (1 - alpha) + a * alpha, 0, 255).astype(np.uint8))

mare = lambda c: c
VARIANTI = {
 # A: alba, cielo con tinta calda e sole basso; mare azzurro-verde
 "A-alba": dict(cielo=((176, 208, 246), (255, 226, 205)), orizzonte=0.50, sole=(560, 520, 46, (255, 220, 170)), nuvole=True,
    fasce=[((150, 205, 235), 0, 6, 1900, 0.3), ((118, 186, 226), 90, 10, 1500, 1.4), ((92, 166, 214), 190, 12, 1700, 2.6), ((70, 146, 200), 300, 14, 2100, 0.8), ((52, 126, 186), 410, 14, 1800, 2.0)]),
 # B: giorno limpido, cielo chiaro con nuvole morbide, mare blu SofiOS
 "B-giorno": dict(cielo=((150, 196, 248), (232, 244, 255)), orizzonte=0.50, sole=None, nuvole=True,
    fasce=[((120, 176, 238), 0, 6, 1900, 0.3), ((96, 160, 230), 90, 10, 1500, 1.4), ((76, 144, 222), 190, 12, 1700, 2.6), ((58, 128, 210), 300, 14, 2100, 0.8), ((44, 112, 196), 410, 14, 1800, 2.0)]),
 # C: bianco e minimale, quasi tutto bianco con onde azzurre chiare solo in basso
 "C-bianco": dict(cielo=((248, 250, 253), (252, 253, 255)), orizzonte=0.62, sole=None, nuvole=False,
    fasce=[((226, 238, 252), 0, 8, 1900, 0.3), ((208, 227, 250), 80, 10, 1500, 1.4), ((188, 214, 246), 160, 12, 1700, 2.6), ((166, 200, 240), 250, 14, 2100, 0.8)], linee=(255, 255, 255)),
}
for n, kw in VARIANTI.items():
    scena(**kw).save(os.path.join(out, n + ".png"), optimize=True)
print("ok")
