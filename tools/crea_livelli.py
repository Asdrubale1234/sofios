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
for k, (t, s, si, no) in L.items():
    im = Image.new("RGB", (640, 470), (13, 43, 74)); d = ImageDraw.Draw(im)
    lg = Image.open(LOGO).convert("RGBA").resize((90, 90)); im.paste(lg, (24, 20), lg)
    d.text((130, 36), t, font=f("Bold", 30), fill=(255, 212, 71))
    d.text((130, 78), s, font=f("Regular", 16), fill=(190, 215, 240))
    d.text((28, 136), "Cosa c'è dentro", font=f("SemiBold", 17), fill=(255, 212, 71))
    y = 170
    for x in si:
        d.text((30, y), "✓", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16), fill=(255, 255, 255))
        d.text((56, y), x, font=f("Regular", 16), fill=(255, 255, 255)); y += 29
    for x in no:
        d.text((30, y), "✗", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16), fill=(150, 170, 195))
        d.text((56, y), x.split(" (")[0] + " (non incluso)", font=f("Regular", 16), fill=(150, 170, 195)); y += 29
    if no: d.text((28, 440), "Quello che manca lo potrai aggiungere in seguito da SoStore.", font=f("Regular", 14), fill=(190, 215, 240))
    im.save(f"{D}/{k}.png")
