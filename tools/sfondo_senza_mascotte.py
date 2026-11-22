#!/usr/bin/env python3
"""Toglie la mascotte dipinta nello sfondo scuro (ora è un widget). Uso: sfondo_senza_mascotte.py ORIGINALE.png USCITA.png"""
import sys
import numpy as np
from PIL import Image, ImageFilter
a = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(float)
H, W, _ = a.shape
x0, x1 = 1380, 1890           # il bordo sinistro e destro della zona da ricostruire (mascotte e ombra)
y0, y1 = 560, 1000
out = a.copy()
# per ogni riga: passaggio morbido tra il colore a sinistra e quello a destra della zona
for y in range(y0, y1):
    L = a[y, x0 - 12:x0].mean(axis=0); R = a[y, x1:x1 + 12].mean(axis=0)
    t = np.linspace(0, 1, x1 - x0)[:, None]
    out[y, x0:x1] = L * (1 - t) + R * t
# le righe sottili delle onde: la zona è ricostruita con un velo di sfumatura verticale per non lasciare scalini
zona = Image.fromarray(out.astype(np.uint8)).crop((x0 - 30, y0 - 20, x1 + 30, y1 + 20)).filter(ImageFilter.GaussianBlur(2.5))
mask = np.zeros((y1 - y0 + 40, x1 - x0 + 60), float); mask[20:-20, 30:-30] = 1
mask = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(12))).astype(float)[..., None] / 255
base = out[y0 - 20:y1 + 20, x0 - 30:x1 + 30]
out[y0 - 20:y1 + 20, x0 - 30:x1 + 30] = base * (1 - mask) + np.asarray(zona).astype(float) * mask
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(sys.argv[2], optimize=True)
