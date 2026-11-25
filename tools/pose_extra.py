#!/usr/bin/env python3
"""Pose nuove di Luma (Nano Banana): via il verde, stessa scala fissa e base ferma, tela 440x560 come le altre.
Uso: python3 tools/pose_extra.py   (legge docs/assets/nano/originali-verde/*.jpg e scrive nel widget e in docs/assets/sofi)"""
import os, sys, numpy as np
from PIL import Image, ImageFilter
R = "live/config/includes.chroot_after_packages/usr/share/plasma/plasmoids/org.sofios.mascotte/contents/images/"
SRC = "docs/assets/nano/originali-verde/"
def chiave(im):
    a = np.asarray(im.convert("RGB")).astype(float); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    dist = np.clip((g - np.maximum(r, b)) / 200.0, 0, 1); alpha = 1 - np.clip((dist - 0.12) / 0.20, 0, 1)
    g2 = np.where(dist > 0.04, np.minimum(g, np.maximum(r, b) * 1.02 + 2), g)
    out = Image.fromarray(np.dstack([r, g2, b, alpha * 255]).astype(np.uint8), "RGBA")
    al = out.split()[3].point(lambda v: 0 if v < 24 else v).filter(ImageFilter.GaussianBlur(0.5)); out.putalpha(al); return out
dati = {}
for f in sorted(os.listdir(SRC)):
    n = f[:-4]; p = chiave(Image.open(SRC + f)); m = np.asarray(p.split()[3]) > 60
    ys, xs = np.where(m); fondo = ys.max(); riga = m[max(0, fondo - 60):fondo + 1]; cx = int(np.mean(np.where(riga)[1]))
    larg = np.where(riga)[1].max() - np.where(riga)[1].min()
    if n in ("stampante", "disinstalla", "musica"): cx, fondo = 515, 982      # oggetti accanto alla base spostano il centro misurato: la torre e' al solito posto
    dati[n] = (p, fondo, cx, larg)
S = float(sys.argv[1]) if len(sys.argv) > 1 else 0.54    # scala fissa: tutte le pose escono nate alla stessa grandezza
for n, (p, fondo, cx, larg) in dati.items():
    p2 = p.resize((int(p.width * S), int(p.height * S)), Image.LANCZOS)
    tela = Image.new("RGBA", (440, 560), (0, 0, 0, 0)); tela.alpha_composite(p2, (220 - int(cx * S), 556 - int(fondo * S)))
    tela.save(R + "sofi-%s.png" % n, optimize=True); tela.save("docs/assets/sofi/sofi-%s.png" % n, optimize=True)
    print(n, "base", fondo, "centro", cx, "larghezza base", larg)
