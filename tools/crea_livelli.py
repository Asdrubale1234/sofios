#!/usr/bin/env python3
"""Genera le immagini dei livelli dell'installatore in usr/share/sofios/livelli/."""
import sys
from PIL import Image, ImageDraw, ImageFont
D = sys.argv[1] if len(sys.argv) > 1 else "."
F = "/usr/share/fonts/opentype/inter/Inter-%s.otf"
def f(s, n): return ImageFont.truetype(F % s, n)
LOGO = "live/config/includes.chroot_after_packages/usr/share/sofios/logo.png"
BASE = ["Internet con Firefox e posta", "Documenti, fogli di calcolo, PDF",
        "Foto, musica e video", "Cassaforte Password e SoStore"]
W = "Programmi Windows (Notepad++, 7-Zip...)"
A = "App Android (serve Internet la prima volta)"
L = {
 "base": ("Base", "Il necessario, il più leggero", BASE, [W, A]),
 "android": ("Base + Android", "Il necessario più le app del telefono", BASE + [A], [W]),
 "windows": ("Base + Windows", "Il necessario più i programmi Windows", BASE + [W], [A]),
 "completo": ("Completo", "Tutto: programmi Windows e app Android", BASE + [W, A], []),
}
ILL = "docs/assets/nano/18-livelli/%s.jpg"
INTER = "/usr/share/fonts/opentype/inter/Inter-%s.otf"
def f(s, n):
    try: return ImageFont.truetype(INTER % s, n)
    except Exception: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if s in ("Bold", "SemiBold") else ""), n)
SIMB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
for k, (t, s, si, no) in L.items():
    im = Image.new("RGB", (640, 470), (28, 28, 30)); d = ImageDraw.Draw(im)
    import numpy as np
    H = 220
    ill = Image.open(ILL % k).convert("RGB"); ill = ill.resize((int(H * ill.width / ill.height), H), Image.LANCZOS)     # intera
    x0 = 640 - ill.width; im.paste(ill, (x0, 0))
    a = np.zeros((H, 640), float); xs = np.arange(640)[None, :]; ys = np.arange(H)[:, None]
    a = np.maximum(np.clip(1 - (xs - x0) / 170.0, 0, 1) * (xs >= x0 - 1), np.clip((ys - (H - 60)) / 60.0, 0, 1) * (xs >= x0 - 1))   # sfuma a sinistra e in basso
    a = np.where(xs < x0, 1.0, a)
    vel = Image.new("RGBA", (640, H), (28, 28, 30, 0)); vel.putalpha(Image.fromarray((a * 255).astype(np.uint8))); im.paste(vel, (0, 0), vel)
    d.text((26, 70), t, font=f("Bold", 30), fill=(245, 245, 247)); d.text((28, 116), s, font=f("Regular", 15), fill=(174, 174, 178))
    y = 236
    for x in si:
        d.text((28, y + 1), "\u2713", font=SIMB, fill=(48, 209, 88)); d.text((54, y), x, font=f("Regular", 15), fill=(245, 245, 247)); y += 27
    for x in no:
        d.text((28, y + 1), "\u2717", font=SIMB, fill=(99, 99, 102)); d.text((54, y), x.split(" (")[0] + " (non incluso)", font=f("Regular", 15), fill=(99, 99, 102)); y += 27
    if no: d.text((26, 444), "Quello che manca lo potrai aggiungere in seguito da SoStore.", font=f("Regular", 13), fill=(142, 142, 147))
    im.save(f"{D}/{k}.png", optimize=True)
