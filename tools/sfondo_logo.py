#!/usr/bin/env python3
"""Sfondo chiaro di SofiOS: fondo bianco-azzurro con il logo al centro. Uso: sfondo_logo.py CARTELLA_INCLUDES [FILE_ANTEPRIMA]"""
import os, sys
import numpy as np
from PIL import Image, ImageFilter
inc = sys.argv[1]
W, H = 1920, 1080
logo = Image.open("docs/logo-sofios-chiaro.png").convert("RGBA")
y = np.linspace(0, 1, H)[:, None, None]
fondo = np.array([252, 253, 255.]) * (1 - y) + np.array([232, 241, 252.]) * y
fondo = np.broadcast_to(fondo, (H, W, 3)).copy()
yy, xx = np.mgrid[0:H, 0:W]
d = np.sqrt(((xx - W / 2) / 700) ** 2 + ((yy - H * 0.47) / 520) ** 2)
alone = np.exp(-d ** 2)[..., None] * 0.55
fondo = fondo * (1 - alone) + np.array([190, 222, 250.]) * alone
base = Image.fromarray(fondo.astype(np.uint8)).convert("RGBA")
L = 460
lg = logo.resize((L, L), Image.LANCZOS)
cx, cy = (W - L) // 2, int(H * 0.47 - L / 2)
ombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sh = Image.new("RGBA", (L, L), (20, 60, 110, 0)); sh.putalpha(lg.split()[3].point(lambda v: int(v * 0.35)))
ombra.paste(sh, (cx, cy + 26), sh)
ombra = ombra.filter(ImageFilter.GaussianBlur(34))
base = Image.alpha_composite(base, ombra)
base.paste(lg, (cx, cy), lg)
res = base.convert("RGB")
d_ = os.path.join(inc, "usr/share/wallpapers/SofiOSChiaro/contents/images"); os.makedirs(d_, exist_ok=True)
res.save(os.path.join(d_, "1920x1080.png"), optimize=True)
if len(sys.argv) > 2: res.resize((960, 540)).save(sys.argv[2])
