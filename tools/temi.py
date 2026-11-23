#!/usr/bin/env python3
"""I tre temi di SofiOS: «Argento e rosso» (predefinito), «Grigio scuro e rosso», «Bianco e oro».
Uso: temi.py CARTELLA_INCLUDES [CARTELLA_ANTEPRIME]   (dalla radice del repository: serve docs/logo-sofios-chiaro.png)"""
import os, shutil, sys
import numpy as np
from PIL import Image, ImageFilter
inc = sys.argv[1]; prev = sys.argv[2] if len(sys.argv) > 2 else None
P = lambda *a: os.path.join(inc, *a)
W, H = 3840, 2160

TEMI = {
 "argento": dict(file="Silver_Red", lnf="org.sofios.desktop", nome="SofiOS argento e rosso", desc="Argento satinato con accenti rossi", colori="SofiOSArgento", sfondo="SofiOSArgento",
     icone="SofiOS-chiaro", barre="breeze-light", finestre="SofiOSChiaro", scuro=False,
     base=(236, 238, 242), base2=(204, 207, 214), nastro=((120, 8, 22), (205, 20, 42), (240, 90, 100)),
     win=(230, 232, 236), win2=(218, 221, 227), view=(248, 249, 251), view2=(240, 242, 245), btn=(244, 245, 247), fg=(28, 28, 30), fgi=(110, 110, 118),
     acc=(196, 28, 46), sel=(196, 28, 46), selfg=(255, 255, 255), link=(170, 20, 40), neg=(200, 40, 40), neu=(190, 110, 0), pos=(30, 140, 80)),
 "grafite": dict(file="Dark_Grey_Red", lnf="org.sofios.graphite", nome="SofiOS grigio scuro e rosso", desc="Grigio antracite con accenti rossi", colori="SofiOSGrafite", sfondo="SofiOSGrafite",
     icone="SofiOS", barre="breeze-dark", finestre="SofiOSGrafite", scuro=True,
     base=(44, 46, 52), base2=(16, 17, 20), nastro=((110, 6, 20), (200, 22, 44), (245, 100, 110)),
     win=(36, 38, 43), win2=(46, 48, 54), view=(26, 27, 31), view2=(32, 34, 38), btn=(52, 54, 61), fg=(236, 237, 240), fgi=(160, 163, 172),
     acc=(226, 52, 68), sel=(196, 28, 46), selfg=(255, 255, 255), link=(255, 120, 132), neg=(255, 138, 128), neu=(255, 190, 90), pos=(111, 224, 176)),
 "oro": dict(file="White_Gold", lnf="org.sofios.gold", nome="SofiOS bianco e oro", desc="Bianco perla con accenti dorati", colori="SofiOSOro", sfondo="SofiOSOro",
     icone="SofiOS-chiaro", barre="breeze-light", finestre="SofiOSChiaro", scuro=False,
     base=(248, 245, 238), base2=(226, 222, 212), nastro=((140, 98, 18), (214, 172, 72), (248, 226, 156)),
     win=(244, 241, 234), win2=(232, 228, 218), view=(252, 251, 247), view2=(244, 241, 234), btn=(250, 248, 243), fg=(40, 36, 28), fgi=(120, 112, 98),
     acc=(168, 118, 16), sel=(176, 124, 20), selfg=(255, 255, 255), link=(150, 100, 10), neg=(200, 40, 40), neu=(190, 110, 0), pos=(30, 140, 80)),
}

def nastro_img(t):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = xx / W; v = yy / H
    a = np.array(t["base"], np.float32); b = np.array(t["base2"], np.float32)
    k = np.clip(0.5 * v + 0.4 * u, 0, 1)[..., None]
    fondo = a * (1 - k) + b * k
    # luce morbida in alto a sinistra (zona tranquilla per le icone) e un secondo riflesso a destra
    luce1 = np.exp(-(((xx - W * 0.25) / (W * 0.4)) ** 2 + ((yy - H * 0.2) / (H * 0.45)) ** 2))[..., None]
    luce2 = np.exp(-(((xx - W * 0.85) / (W * 0.25)) ** 2 + ((yy - H * 0.6) / (H * 0.3)) ** 2))[..., None]
    fondo = fondo + luce1 * (-12 if t["scuro"] else 18) + luce2 * (-8 if t["scuro"] else 8)
    sc, me, ch = (np.array(c_, np.float32) for c_ in t["nastro"])
    # tre nastri: uno sottile e uno medio dietro, uno grande davanti. (a, b, c, d, e, f, g, spessore, scala)
    NASTRI = [(0.30, 0.95, 1.06, 0.80, 0.22, 1.00, 0.30, 85, 0.85), (0.00, 1.15, 1.00, 0.88, 0.30, 1.05, 0.35, 150, 1.0), (-0.12, 1.30, 1.05, 0.98, 0.30, 1.10, 0.40, 230, 1.0)]
    for (a_, b_, c_, d_, e_, f_, g_, sp0, sc_) in NASTRI:
        ts = np.linspace(0, 1, 13000, dtype=np.float32)
        cx = W * (a_ + b_ * ts); cy = H * (c_ - d_ * ts + e_ * np.sin(ts * np.pi * f_) * (1 - ts * g_))
        dx = np.gradient(cx); dy = np.gradient(cy); n = np.hypot(dx, dy) + 1e-6
        nx = -dy / n; ny = dx / n
        spess = (sp0 * 0.25 + sp0 * 0.75 * np.sin(np.pi * np.clip(ts * 1.05, 0, 1)) ** 1.3) * (W / 1920.0) * sc_ * 0.5
        mask = np.zeros((H, W), np.float32); luce = np.zeros((H, W), np.float32)
        qs = np.linspace(-1, 1, 1500, dtype=np.float32)
        for i0 in range(0, len(ts), 1300):
            sl = slice(i0, i0 + 1300)
            px = (cx[sl, None] + nx[sl, None] * spess[sl, None] * qs[None, :]).astype(np.int32)
            py = (cy[sl, None] + ny[sl, None] * spess[sl, None] * qs[None, :]).astype(np.int32)
            ok = (px >= 0) & (px < W) & (py >= 0) & (py < H)
            qq = np.broadcast_to(qs[None, :], px.shape)
            mask[py[ok], px[ok]] = 1; luce[py[ok], px[ok]] = qq[ok]
        m = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2.2))
        l = Image.fromarray(((luce + 1) / 2 * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(26))
        mm = np.asarray(m).astype(np.float32)[..., None] / 255.0; ll = np.asarray(l).astype(np.float32)[..., None] / 255.0
        lunga = (0.5 + 0.5 * np.sin((xx / W * 3.2 + yy / H * 1.4) * np.pi))[..., None] * 0.18          # variazione di luce lungo il nastro
        ll = np.clip(ll + lunga - 0.09, 0, 1)
        riflesso = np.exp(-((ll - 0.36) / 0.10) ** 2) * 0.55 + np.exp(-((ll - 0.78) / 0.07) ** 2) * 0.28
        nas = sc * (1 - ll) + me * ll
        nas = nas * (1 - riflesso * 0.55) + ch * riflesso * 0.55
        nas = nas * (1 - np.clip(np.abs(ll - 0.5) * 2 - 0.7, 0, 1) * 0.25)                              # bordi leggermente piu' scuri
        ombra = np.asarray(m.filter(ImageFilter.GaussianBlur(70))).astype(np.float32)[..., None] / 255.0
        if t["scuro"]:
            lum = np.asarray(m.filter(ImageFilter.GaussianBlur(45))).astype(np.float32)[..., None] / 255.0
            fondo = fondo + lum * me * 0.28 - ombra * 6                                                  # alone rosso
        else:
            fondo = fondo * (1 - ombra * 0.22)
        fondo = fondo * (1 - mm) + nas * mm
    return Image.fromarray(np.clip(fondo, 0, 255).astype(np.uint8)).convert("RGB")

def c(t): return "%d,%d,%d" % tuple(t)
def schema(t):
    comune = dict(ForegroundNormal=c(t["fg"]), ForegroundInactive=c(t["fgi"]), ForegroundActive=c(t["acc"]), ForegroundLink=c(t["link"]), ForegroundVisited=c(t["fgi"]),
                  ForegroundNegative=c(t["neg"]), ForegroundNeutral=c(t["neu"]), ForegroundPositive=c(t["pos"]), DecorationFocus=c(t["sel"]), DecorationHover=c(t["sel"]))
    sez = {"View": dict(BackgroundNormal=c(t["view"]), BackgroundAlternate=c(t["view2"]), **comune),
           "Window": dict(BackgroundNormal=c(t["win"]), BackgroundAlternate=c(t["win2"]), **comune),
           "Button": dict(BackgroundNormal=c(t["btn"]), BackgroundAlternate=c(t["win2"]), **comune),
           "Selection": dict(BackgroundNormal=c(t["sel"]), BackgroundAlternate=c(t["sel"]), ForegroundNormal=c(t["selfg"]), ForegroundInactive=c(t["selfg"]), ForegroundActive=c(t["selfg"]),
                             ForegroundLink=c(t["selfg"]), ForegroundVisited=c(t["selfg"]), ForegroundNegative="255,210,210", ForegroundNeutral="255,235,170", ForegroundPositive="210,255,230",
                             DecorationFocus=c(t["selfg"]), DecorationHover=c(t["selfg"]))}
    for n in ("Tooltip", "Complementary", "Header"): sez[n] = dict(BackgroundNormal=c(t["win"]), BackgroundAlternate=c(t["win2"]), **comune)
    s = "# %s\n[General]\nColorScheme=%s\nName=%s\n\n" % (t["nome"], t["colori"], t["nome"])
    for n, d in sez.items(): s += "[Colors:%s]\n" % n + "".join("%s=%s\n" % kv for kv in d.items()) + "\n"
    s += "[ColorEffects:Disabled]\nColor=56,56,56\nColorAmount=0\nColorEffect=0\nContrastAmount=0.65\nContrastEffect=1\nIntensityAmount=0.1\nIntensityEffect=2\n\n"
    s += "[ColorEffects:Inactive]\nChangeSelectionColor=true\nColor=112,111,110\nColorAmount=0.025\nColorEffect=2\nContrastAmount=0.1\nContrastEffect=2\nEnable=false\nIntensityAmount=0\nIntensityEffect=0\n\n"
    s += "[WM]\nactiveBackground=%s\nactiveForeground=%s\ninactiveBackground=%s\ninactiveForeground=%s\nactiveBlend=%s\ninactiveBlend=%s\n" % (c(t["win"]), c(t["fg"]), c(t["win2"]), c(t["fgi"]), c(t["fg"]), c(t["fgi"]))
    return s

# --- 0) via i temi vecchi
for p in ("usr/share/color-schemes/SofiOS.colors", "usr/share/color-schemes/SofiOSChiaro.colors", "usr/share/color-schemes/SofiOSArgento.colors"):
    if os.path.exists(P(p)): os.remove(P(p))
for d in ("usr/share/wallpapers/SofiOS", "usr/share/wallpapers/SofiOSChiaro", "usr/share/wallpapers/SofiOSArgento", "usr/share/plasma/look-and-feel/org.sofios.light", "usr/share/plasma/look-and-feel/org.sofios.silver",
          "usr/share/plasma/look-and-feel/org.sofios.gold", "usr/share/plasma/look-and-feel/org.sofios.graphite", "usr/share/plasma/desktoptheme/sofios-chiaro"):
    shutil.rmtree(P(d), ignore_errors=True)

# --- 1) decorazione finestre scura (grafite): copia di quella scura con grigi al posto dei blu
dec = P("usr/share/aurorae/themes/SofiOSGrafite")
if os.path.isdir(P("usr/share/aurorae/themes/SofiOS")):       # la prima volta: parte dalla decorazione scura originale
  shutil.rmtree(dec, ignore_errors=True); shutil.copytree(P("usr/share/aurorae/themes/SofiOS"), dec)
  svg = open(os.path.join(dec, "decoration.svg")).read()
  for a_, b_ in (("#0b2740", "#25272c"), ("#0e2e4d", "#2e3036"), ("#08203a", "#1d1e22"), ("#06182c", "#17181b")): svg = svg.replace(a_, b_)
  open(os.path.join(dec, "decoration.svg"), "w").write(svg)
  os.rename(os.path.join(dec, "SofiOSrc"), os.path.join(dec, "SofiOSGrafiterc"))
  md = open(os.path.join(dec, "metadata.desktop")).read().replace("Name=SofiOS\n", "Name=SofiOS grigio scuro\n", 1).replace("X-KDE-PluginInfo-Name=SofiOS", "X-KDE-PluginInfo-Name=SofiOSGrafite")
  open(os.path.join(dec, "metadata.desktop"), "w").write(md)
  if os.path.exists(os.path.join(dec, "metadata.json")):
      _j = open(os.path.join(dec, "metadata.json")).read().replace('"SofiOS"', '"SofiOSGrafite"')
      open(os.path.join(dec, "metadata.json"), "w").write(_j)
  shutil.rmtree(P("usr/share/aurorae/themes/SofiOS"), ignore_errors=True)

# --- 2) i tre temi
for chiave, t in TEMI.items():
    img = nastro_img(t)
    d = P("usr/share/wallpapers", t["sfondo"], "contents/images"); os.makedirs(d, exist_ok=True); img.save(os.path.join(d, "3840x2160.png"), optimize=True)
    if prev: os.makedirs(prev, exist_ok=True); img.save(os.path.join(prev, "SofiOS_%s.png" % t["file"]), optimize=True)
    open(P("usr/share/wallpapers", t["sfondo"], "metadata.json"), "w").write('{"KPlugin": {"Id": "%s", "Name": "%s", "Authors": [{"Name": "SofiOS"}], "License": "CC-BY-SA-4.0"}}\n' % (t["sfondo"], t["nome"]))
    open(P("usr/share/color-schemes", t["colori"] + ".colors"), "w").write(schema(t))
    lnf = P("usr/share/plasma/look-and-feel", t["lnf"])
    os.makedirs(os.path.join(lnf, "contents/previews"), exist_ok=True)
    if not os.path.exists(os.path.join(lnf, "metadata.json")) or chiave != "argento":
        open(os.path.join(lnf, "metadata.json"), "w").write('{"KPlugin":{"Id":"%s","Name":"%s","Description":"%s","Authors":[{"Name":"SofiOS"}],"Version":"1.0","License":"GPL-2.0+","Category":""},"KPackageStructure":"Plasma/LookAndFeel"}\n' % (t["lnf"], t["nome"], t["desc"]))
    else:
        open(os.path.join(lnf, "metadata.json"), "w").write('{"KPlugin":{"Id":"%s","Name":"%s","Description":"%s","Authors":[{"Name":"SofiOS"}],"Version":"1.0","License":"GPL-2.0+","Category":""},"KPackageStructure":"Plasma/LookAndFeel"}\n' % (t["lnf"], t["nome"], t["desc"]))
    open(os.path.join(lnf, "contents/defaults"), "w").write(
        "[kdeglobals][General]\nColorScheme=%s\n\n[kdeglobals][KDE]\nwidgetStyle=Breeze\n\n[plasmarc][Theme]\nname=%s\n\n[Wallpaper]\nImage=%s\n\n[kdeglobals][Icons]\nTheme=%s\n\n"
        "[kwinrc][org.kde.kdecoration2]\nlibrary=org.kde.kwin.aurorae\ntheme=__aurorae__svg__%s\n" % (t["colori"], t["barre"], t["sfondo"], t["icone"], t["finestre"]))
    img.resize((800, 450)).save(os.path.join(lnf, "contents/previews/preview.png")); img.save(os.path.join(lnf, "contents/previews/fullscreenpreview.jpg"), quality=88)
print("ok")
