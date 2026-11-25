#!/usr/bin/env python3
"""Elabora le immagini di Nano Banana (cartella con sfondo-*.png e luma-*.png): sfondi nelle misure di ogni dispositivo, pose di Luma senza il verde.
Uso: elabora_immagini.py CARTELLA_IMMAGINI CARTELLA_INCLUDES"""
import os, sys
import numpy as np
from PIL import Image, ImageFilter
src, inc = sys.argv[1], sys.argv[2]
P = lambda *a: os.path.join(inc, *a)
def ingrandisci(im, w, h):
    """ritaglia nel rapporto giusto e ingrandisce con una leggera nitidezza"""
    r = w / h; iw, ih = im.size
    if iw / ih > r: nw = int(ih * r); im = im.crop(((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih))
    else: nh = int(iw / r); im = im.crop((0, (ih - nh) // 2, iw, (ih - nh) // 2 + nh))
    im = im.resize((w, h), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=60, threshold=2))
# 1) sfondi per i dispositivi (cartella docs/assets/sfondi/dispositivi) e per il desktop del sistema
FORMATI = {"pc-tv-16x9": (3840, 2160), "pc-tablet-3x2": (2560, 1600), "schermo-largo-21x9": (3440, 1440), "tablet-verticale-3x4": (1668, 2224), "telefono-9x16": (1440, 2560), "orologio-quadrato": (1080, 1080)}
os.makedirs("docs/assets/sfondi/dispositivi", exist_ok=True)
for tema in ("scuro", "chiaro"):
    for nome, (w, h) in FORMATI.items():
        f = os.path.join(src, "sfondo-%s-%s.png" % (tema, nome))
        if not os.path.exists(f): continue
        im = ingrandisci(Image.open(f).convert("RGB"), w, h)
        im.save("docs/assets/sfondi/dispositivi/sfondo-%s-%s.jpg" % (tema, nome), quality=93)
    cartella = P("usr/share/wallpapers", "SofiOS" if tema == "scuro" else "SofiOSChiaro", "contents/images")
    for g in os.listdir(cartella):
        os.remove(os.path.join(cartella, g))
    for nome, dim in (("pc-tv-16x9", (1920, 1080)), ("pc-tv-16x9", (3840, 2160)), ("pc-tablet-3x2", (2560, 1600)), ("schermo-largo-21x9", (3440, 1440))):
        f = os.path.join(src, "sfondo-%s-%s.png" % (tema, nome))
        if os.path.exists(f): ingrandisci(Image.open(f).convert("RGB"), *dim).save(os.path.join(cartella, "%dx%d.jpg" % dim), quality=92)
    base = Image.open(os.path.join(src, "sfondo-%s-pc-tv-16x9.png" % tema)).convert("RGB")
    prev = P("usr/share/plasma/look-and-feel", "org.sofios.desktop" if tema == "scuro" else "org.sofios.light", "contents/previews")
    base.resize((800, 450), Image.LANCZOS).save(prev + "/preview.png"); ingrandisci(base, 1920, 1080).save(prev + "/fullscreenpreview.jpg", quality=90)
    ingrandisci(base, 1920, 1080).save("docs/assets/sfondi/%s.jpg" % tema, quality=94)
    # anteprime per l'installatore
    base.resize((640, 360), Image.LANCZOS).save(P("usr/share/sofios/aspetto", tema + ".png"), optimize=True)
# 2) pose di Luma: via il verde, stessa grandezza e piedi allineati
def chiave(im):
    a = np.asarray(im.convert("RGB")).astype(float); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    dist = np.clip((g - np.maximum(r, b)) / 200.0, 0, 1); alpha = 1 - np.clip((dist - 0.12) / 0.20, 0, 1)
    g2 = np.where(dist > 0.04, np.minimum(g, np.maximum(r, b) * 1.02 + 2), g)
    out = Image.fromarray(np.dstack([r, g2, b, alpha * 255]).astype(np.uint8), "RGBA")
    al = out.split()[3].point(lambda v: 0 if v < 24 else v).filter(ImageFilter.GaussianBlur(0.5)); out.putalpha(al); return out
NOMI = ("neutra", "saluta", "parla", "ascolta", "pensa", "felice", "concentrata", "preoccupata")
pose = {}
for n in NOMI:
    f = os.path.join(src, "luma-%s.png" % n)
    if os.path.exists(f): pose[n] = chiave(Image.open(f))
if "concentrata" not in pose and os.path.exists("docs/assets/sofi/concentrata-originale.png"):
    pose["concentrata"] = chiave(Image.open("docs/assets/sofi/concentrata-originale.png"))
info = {}
for n, p in pose.items():
    m = p.split()[3].point(lambda v: 255 if v > 60 else 0).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3)); bb = m.getbbox()
    p = p.crop(bb); mm = np.asarray(m.crop(bb)) > 0; basso = mm[int(mm.shape[0] * 0.85):]
    cx = int(np.mean(np.where(basso)[1])) if basso.any() else p.width // 2          # centro della base: i piedi stanno fermi tra una posa e l'altra
    info[n] = (p, cx)
altezza_rif = np.median([p.height for p, _ in info.values()])
s = 500.0 / max(p.height for p, _ in info.values())
os.makedirs("docs/assets/sofi", exist_ok=True)
for n, (p, cx) in info.items():
    f = altezza_rif / p.height if n == "concentrata" and "luma-concentrata.png" not in os.listdir(src) else 1.0      # la posa nata a parte la porto alla stessa grandezza delle altre
    p2 = p.resize((int(p.width * s * f), int(p.height * s * f)), Image.LANCZOS); cx2 = int(cx * s * f)
    tela = Image.new("RGBA", (440, 560), (0, 0, 0, 0)); tela.alpha_composite(p2, (220 - cx2, 560 - p2.height - 4))
    tela.save(P("usr/share/plasma/plasmoids/org.sofios.mascotte/contents/images/sofi-%s.png" % n), optimize=True); tela.save("docs/assets/sofi/sofi-%s.png" % n, optimize=True)
    p.save("docs/assets/sofi/luma-%s-ritagliata.png" % n, optimize=True)
print("ok", sorted(pose))
