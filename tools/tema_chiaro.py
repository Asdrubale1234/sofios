#!/usr/bin/env python3
"""Costruisce le parti del tema SofiOS chiaro: sfondo di giorno, finestre chiare, anteprime. Uso: tema_chiaro.py CARTELLA_INCLUDES"""
import os, re, sys
import numpy as np
from PIL import Image, ImageFilter
inc = sys.argv[1]
P = lambda *a: os.path.join(inc, *a)

# 1) sfondo di giorno: stessa scena, colori chiari, senza stelle; la mascotte resta quella originale
src = Image.open(P("usr/share/wallpapers/SofiOS/contents/images/1920x1080.png")).convert("RGB")
a = np.asarray(src).astype(float)
sfondo = np.asarray(src.filter(ImageFilter.MedianFilter(9))).astype(float)
L = sfondo.mean(axis=2) / 255.0
h = a.shape[0]
y = np.arange(h)[:, None]
cielo_alto = np.array([205, 228, 252.]); cielo_basso = np.array([244, 249, 255.])
yy = np.clip(y / 540.0, 0, 1)[..., None]
cielo = cielo_alto * (1 - yy) + cielo_basso * yy
t = np.clip((L - 0.05) / 0.2, 0, 1)[..., None]                # nel mare: fasce più o meno chiare
mare_a = np.array([112, 172, 236.]); mare_b = np.array([160, 205, 247.])
mare = mare_a * (1 - t) + mare_b * t
out = np.where((y >= 540)[..., None], mare, cielo)
# la mascotte: pixel che non sono sfondo blu scuro
reg = (slice(640, 940), slice(1500, 1760))
r, g, b = a[..., 0], a[..., 1], a[..., 2]
sfondo_blu = (r < 70) & (g < 105) & (b < 140)
mask = (~sfondo_blu)
m = np.zeros(mask.shape, bool); m[reg] = mask[reg]
im = Image.fromarray((m * 255).astype(np.uint8))
im = im.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
alpha = (np.asarray(im).astype(float) / 255.0)[..., None]
out = out * (1 - alpha) + a * alpha
res = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
os.makedirs(P("usr/share/wallpapers/SofiOSChiaro/contents/images"), exist_ok=True)
# (lo sfondo chiaro con il logo si fa con sfondo_logo.py)
open(P("usr/share/wallpapers/SofiOSChiaro/metadata.json"), "w").write('{"KPlugin": {"Id": "SofiOSChiaro", "Name": "SofiOS chiaro", "Authors": [{"Name": "SofiOS"}], "License": "CC-BY-SA-4.0"}}\n')
res.resize((400, 225)).save("/tmp/anteprima-sfondo-chiaro.png")

# 2) colori: bianco e grigio chiaro (stile Apple), accento blu SofiOS
p = P("usr/share/color-schemes/SofiOSChiaro.colors")
s = open(p).read()
def sezione(nome, valori):
    global s
    blocco = "[Colors:%s]\n" % nome + "".join("%s=%s\n" % kv for kv in valori.items())
    s = re.sub(r"\[Colors:%s\]\n(?:[^\[]*)" % nome, lambda _: blocco + "\n", s)
comune = {"ForegroundNormal": "28,28,30", "ForegroundInactive": "110,110,118", "ForegroundActive": "10,110,220", "ForegroundLink": "10,110,220",
          "ForegroundVisited": "120,80,200", "ForegroundNegative": "210,50,50", "ForegroundNeutral": "190,110,0", "ForegroundPositive": "30,140,80",
          "DecorationFocus": "10,110,220", "DecorationHover": "10,110,220"}
sezione("View", {"BackgroundNormal": "255,255,255", "BackgroundAlternate": "246,246,249", **comune})
sezione("Window", {"BackgroundNormal": "242,242,247", "BackgroundAlternate": "232,232,238", **comune})
sezione("Button", {"BackgroundNormal": "255,255,255", "BackgroundAlternate": "238,238,243", **comune})
sezione("Selection", {"BackgroundNormal": "10,110,220", "BackgroundAlternate": "10,110,220", "ForegroundNormal": "255,255,255", "ForegroundInactive": "225,238,255",
          "ForegroundActive": "255,255,255", "ForegroundLink": "255,255,255", "ForegroundVisited": "255,255,255", "ForegroundNegative": "255,210,210",
          "ForegroundNeutral": "255,235,170", "ForegroundPositive": "210,255,230", "DecorationFocus": "255,255,255", "DecorationHover": "255,255,255"})
for n in ("Tooltip", "Complementary", "Header"):
    sezione(n, {"BackgroundNormal": "250,250,252", "BackgroundAlternate": "238,238,243", **comune})
s = re.sub(r"\[WM\]\n[^\[]*", "[WM]\nactiveBackground=246,246,248\nactiveForeground=28,28,30\ninactiveBackground=236,236,240\ninactiveForeground=130,130,138\nactiveBlend=28,28,30\ninactiveBlend=130,130,138\n", s)
open(p, "w").write(s)

# 3) bordo e barra del titolo delle finestre: copia di quello scuro con colori chiari
import shutil
da, a_ = P("usr/share/aurorae/themes/SofiOS"), P("usr/share/aurorae/themes/SofiOSChiaro")
shutil.rmtree(a_, ignore_errors=True); shutil.copytree(da, a_)
svg = open(os.path.join(a_, "decoration.svg")).read()
for scuro_, chiaro_ in (("#0b2740", "#f6f6f8"), ("#0e2e4d", "#ececf0"), ("#08203a", "#e4e4ea"), ("#06182c", "#d9d9e0")):
    svg = svg.replace(scuro_, chiaro_)
open(os.path.join(a_, "decoration.svg"), "w").write(svg)
rc = open(os.path.join(a_, "SofiOSrc")).read()
rc = rc.replace("ActiveTextColor=225,225,225", "ActiveTextColor=40,40,44").replace("InactiveTextColor=120,120,120", "InactiveTextColor=150,150,158")
rc = rc.replace("ActiveTextShadowColor=255,255,255", "ActiveTextShadowColor=255,255,255")
os.rename(os.path.join(a_, "SofiOSrc"), os.path.join(a_, "SofiOSChiarorc"))
open(os.path.join(a_, "SofiOSChiarorc"), "w").write(rc)
md = open(os.path.join(a_, "metadata.desktop")).read().replace("Name=SofiOS", "Name=SofiOS chiaro").replace("X-KDE-PluginInfo-Name=SofiOS", "X-KDE-PluginInfo-Name=SofiOSChiaro")
open(os.path.join(a_, "metadata.desktop"), "w").write(md)
if os.path.exists(os.path.join(a_, "metadata.json")):
    j = open(os.path.join(a_, "metadata.json")).read().replace('"SofiOS"', '"SofiOS chiaro"')
    open(os.path.join(a_, "metadata.json"), "w").write(j)

# 4) barre del desktop (pannello, menu, finestre a comparsa): tema chiaro con i colori del tema
d = P("usr/share/plasma/desktoptheme/sofios-chiaro")
os.makedirs(d, exist_ok=True)
open(os.path.join(d, "metadata.json"), "w").write('{"KPlugin": {"Id": "sofios-chiaro", "Name": "SofiOS chiaro", "Description": "Barre e menu chiari", "Authors": [{"Name": "SofiOS"}], "License": "GPL-2.0-or-later"}, "KPackageStructure": "Plasma/Theme"}\n')
colori = ["[ColorEffects:Disabled]\nColor=56,56,56\nColorAmount=0\nColorEffect=0\nContrastAmount=0.65\nContrastEffect=1\nIntensityAmount=0.1\nIntensityEffect=2\n"]
for n, bg, fg in (("Window", "246,246,248", "28,28,30"), ("Button", "255,255,255", "28,28,30"), ("View", "255,255,255", "28,28,30"), ("Tooltip", "250,250,252", "28,28,30"), ("Complementary", "250,250,252", "28,28,30")):
    colori.append("[Colors:%s]\nBackgroundNormal=%s\nBackgroundAlternate=238,238,243\nForegroundNormal=%s\nForegroundInactive=110,110,118\nForegroundActive=10,110,220\nForegroundLink=10,110,220\nForegroundVisited=120,80,200\nForegroundNegative=210,50,50\nForegroundNeutral=190,110,0\nForegroundPositive=30,140,80\nDecorationFocus=10,110,220\nDecorationHover=10,110,220\n" % (n, bg, fg))
open(os.path.join(d, "colors"), "w").write("\n".join(colori))
print("ok")
