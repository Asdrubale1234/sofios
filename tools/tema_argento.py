#!/usr/bin/env python3
"""Tema SofiOS «Argento e rosso»: argento satinato con il rosso come accento (selezioni, pulsanti, dettagli).
Uso: tema_argento.py CARTELLA_INCLUDES [FILE_ANTEPRIMA]   (dopo tema_chiaro.py, di cui riusa colori e finestre)"""
import os, re, shutil, sys, json
import numpy as np
from PIL import Image, ImageFilter
inc = sys.argv[1]
P = lambda *a: os.path.join(inc, *a)
W, H = 1920, 1080

# 1) sfondo: argento satinato con un nastro rosso che attraversa lo schermo
yy, xx = np.mgrid[0:H, 0:W].astype(float)
u = xx / W; v = yy / H
base = 232 - 20 * v - 10 * u                                   # argento che scurisce piano piano
bagliore = np.exp(-(((xx - W * 0.3) / 700) ** 2 + ((yy - H * 0.25) / 400) ** 2)) * 18
g = np.clip(base + bagliore, 0, 255)
fondo = np.stack([g, g + 2, g + 6], axis=-1)

def curva(t):                                                   # nastro dal basso a sinistra all'alto a destra
    x = W * (-0.1 + 1.25 * t)
    y = H * (0.95 - 0.95 * t + 0.28 * np.sin(t * np.pi * 1.1) * (1 - t * 0.4))
    return x, y
mask = np.zeros((H, W)); luce = np.zeros((H, W))
ts = np.linspace(0, 1, 5200)
cx_, cy_ = curva(ts); dx_ = np.gradient(cx_); dy_ = np.gradient(cy_)
for t in ts:
    cx, cy = curva(t)
    sp = 40 + 210 * np.sin(np.pi * min(1, t * 1.05)) ** 1.3   # spessore che cresce e cala
    i_ = int(round(t * 5199)); ang = np.arctan2(dy_[i_], dx_[i_])
    nx, ny = -np.sin(ang), np.cos(ang)
    for s in np.linspace(-1, 1, 700):
        px = int(cx + nx * sp * s); py = int(cy + ny * sp * s)
        if 0 <= px < W and 0 <= py < H:
            mask[py, px] = 1; luce[py, px] = s
m = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(3))
l = Image.fromarray(((luce + 1) / 2 * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(14))
mm = np.asarray(m).astype(float)[..., None] / 255.0
ll = np.asarray(l).astype(float)[..., None] / 255.0
rosso_scuro = np.array([120, 8, 22.]); rosso = np.array([205, 20, 42.]); rosso_chiaro = np.array([240, 90, 100.])
t_ = np.clip(1 - np.abs(ll - 0.38) * 2.4, 0, 1)
nastro = rosso_scuro * (1 - ll) + rosso * ll
nastro = nastro * (1 - t_ * 0.5) + rosso_chiaro * t_ * 0.5
ombra = np.asarray(m.filter(ImageFilter.GaussianBlur(40))).astype(float)[..., None] / 255.0
fondo = fondo * (1 - ombra * 0.18)
fondo = fondo * (1 - mm) + nastro * mm
res = Image.fromarray(np.clip(fondo, 0, 255).astype(np.uint8)).convert("RGBA")

# il logo SofiOS al centro, in piccolo
logo = Image.open("docs/logo-sofios-chiaro.png").convert("RGBA")
L = 340
lg = logo.resize((L, L), Image.LANCZOS)
cx, cy = (W - L) // 2, int(H * 0.46 - L / 2)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); s_ = Image.new("RGBA", (L, L), (40, 40, 50, 0)); s_.putalpha(lg.split()[3].point(lambda v_: int(v_ * 0.3)))
sh.paste(s_, (cx, cy + 20), s_); sh = sh.filter(ImageFilter.GaussianBlur(26))
res = Image.alpha_composite(res, sh); res.paste(lg, (cx, cy), lg)
res = res.convert("RGB")
d_ = P("usr/share/wallpapers/SofiOSArgento/contents/images"); os.makedirs(d_, exist_ok=True)
res.save(os.path.join(d_, "1920x1080.png"), optimize=True)
open(P("usr/share/wallpapers/SofiOSArgento/metadata.json"), "w").write('{"KPlugin": {"Id": "SofiOSArgento", "Name": "SofiOS argento e rosso", "Authors": [{"Name": "SofiOS"}], "License": "CC-BY-SA-4.0"}}\n')
if len(sys.argv) > 2: res.resize((960, 540)).save(sys.argv[2])

# 2) colori: argento, accento rosso
s = open(P("usr/share/color-schemes/SofiOSChiaro.colors")).read()
for a_, b_ in (("10,110,220", "196,28,46"), ("242,242,247", "230,232,236"), ("232,232,238", "218,221,227"), ("246,246,249", "240,242,245"),
               ("238,238,243", "226,229,234"), ("255,255,255\nBackgroundAlternate=246", "248,249,251\nBackgroundAlternate=240"),
               ("225,238,255", "255,226,229"), ("246,246,248", "232,234,238"), ("236,236,240", "222,225,230"),
               ("SofiOSChiaro", "SofiOSArgento"), ("SofiOS chiaro", "SofiOS argento e rosso")):
    s = s.replace(a_, b_)
open(P("usr/share/color-schemes/SofiOSArgento.colors"), "w").write(s)

# 3) pacchetto del tema globale
d = P("usr/share/plasma/look-and-feel/org.sofios.silver")
shutil.rmtree(d, ignore_errors=True); shutil.copytree(P("usr/share/plasma/look-and-feel/org.sofios.light"), d)
j = open(os.path.join(d, "metadata.json")).read().replace("org.sofios.light", "org.sofios.silver").replace("SofiOS chiaro", "SofiOS argento e rosso").replace("SofiOS con colori chiari", "SofiOS argento con accenti rossi")
open(os.path.join(d, "metadata.json"), "w").write(j)
df = open(os.path.join(d, "contents/defaults")).read().replace("SofiOSChiaro", "SofiOSArgento")
open(os.path.join(d, "contents/defaults"), "w").write(df.replace("__aurorae__svg__SofiOSArgento", "__aurorae__svg__SofiOSChiaro"))
res.resize((800, 450)).save(os.path.join(d, "contents/previews/preview.png"))
res.save(os.path.join(d, "contents/previews/fullscreenpreview.jpg"), quality=88)
print("ok")
