#!/usr/bin/env python3
"""Sfondo SofiOS: i nastri lucidi sono onde del mare ligure, con la Lanterna in lontananza. Uso: sfondo_onda.py CARTELLA_USCITA [tema]"""
import io, os, sys
import numpy as np
from PIL import Image, ImageFilter
import cairosvg
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icona_ufficiale import faro, DEFS_COMUNI
W, H = 3840, 2160

TEMI = {
 "argento": dict(file="Silver_Red", cielo=("#fcfdff", "#d5dbe5"), mare=("#7cc2e4", "#1c6ca6"), notte=False, aloneop=.85,
     onda=((8, 52, 108), (24, 148, 200), (126, 226, 222)), sottile=((120, 8, 22), (205, 20, 42), (245, 100, 110)), argento=((150, 158, 170), (222, 227, 233), (255, 255, 255))),
 "grafite": dict(file="Dark_Grey_Red", cielo=("#2c2f36", "#101216"), mare=("#14597f", "#082948"), notte=True, aloneop=1.0,
     onda=((6, 34, 76), (16, 112, 160), (70, 200, 200)), sottile=((110, 6, 20), (200, 22, 44), (245, 100, 110)), argento=((90, 96, 106), (170, 176, 186), (235, 238, 242))),
 "oro": dict(file="White_Gold", cielo=("#fffdf8", "#e8e2d2"), mare=("#98d6e4", "#3a93b6"), notte=False, aloneop=.9,
     onda=((18, 96, 140), (56, 168, 196), (170, 238, 228)), sottile=((140, 98, 18), (214, 172, 72), (248, 226, 156)), argento=((170, 160, 140), (230, 224, 210), (255, 253, 246))),
}

def base_svg(t):
    cx, b = 3000, 1130
    fz, (lx, ly) = faro(cx, b, 700, 210)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d"><defs>%s'
            '<linearGradient id="cielo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
            '<radialGradient id="aloneG" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff2b8" stop-opacity="%.2f"/><stop offset=".45" stop-color="#ffd25e" stop-opacity=".4"/><stop offset="1" stop-color="#ffd25e" stop-opacity="0"/></radialGradient></defs>'
            '<rect width="%d" height="%d" fill="url(#cielo)"/><ellipse cx="%d" cy="%d" rx="1100" ry="760" fill="url(#aloneG)"/>'
            '<polygon points="%d,%d -100,%d -100,%d" fill="url(#raggioL)" opacity=".5"/><polygon points="%d,%d 3980,%d 3980,%d" fill="url(#raggioR)" opacity=".4"/>'
            '<defs><linearGradient id="mareG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient></defs><rect x="-10" y="1180" width="3860" height="1100" fill="url(#mareG)"/>'
            '<path d="M2640 1160 C 2760 1100, 2900 1085, 3000 1088 C 3150 1085, 3260 1110, 3340 1160 Z" fill="#9aa3b0"/>%s</svg>'
            % (W, H, W, H, DEFS_COMUNI, t["cielo"][0], t["cielo"][1], t["aloneop"], W, H, lx, ly, lx - 50, ly, ly - 150, ly + 130, lx + 50, ly, ly - 100, ly + 110, t["mare"][0], t["mare"][1], fz))

def nastro(fondo, y0, amp, fase, spess, pal, scuro, lungo=1.0):
    """un nastro lucido che ondeggia con una curva a S; pal = (ombra, colore, luce)"""
    ts = np.linspace(0, 1, 13000, dtype=np.float32)
    cx = W * (-0.1 + 1.2 * ts)
    cy = H * (y0 + amp * np.sin(2 * np.pi * (ts * 1.05 * lungo) + fase) - 0.06 * ts)
    dx = np.gradient(cx); dy = np.gradient(cy); n = np.hypot(dx, dy) + 1e-6
    nx = -dy / n; ny = dx / n
    sp = spess * (0.55 + 0.45 * np.sin(np.pi * np.clip(ts * 1.0, 0, 1)) ** 0.8)
    mask = np.zeros((H, W), np.float32); luce = np.zeros((H, W), np.float32)
    qs = np.linspace(-1, 1, 1400, dtype=np.float32)
    for i0 in range(0, len(ts), 1300):
        sl = slice(i0, i0 + 1300)
        px = np.nan_to_num(cx[sl, None] + nx[sl, None] * sp[sl, None] * qs[None, :]).astype(np.int32)
        py = np.nan_to_num(cy[sl, None] + ny[sl, None] * sp[sl, None] * qs[None, :]).astype(np.int32)
        ok = (px >= 0) & (px < W) & (py >= 0) & (py < H); qq = np.broadcast_to(qs[None, :], px.shape)
        mask[py[ok], px[ok]] = 1; luce[py[ok], px[ok]] = qq[ok]
    m = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2.2))
    l = Image.fromarray(((luce + 1) / 2 * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(24))
    mm = np.asarray(m).astype(np.float32)[..., None] / 255.0; ll = np.asarray(l).astype(np.float32)[..., None] / 255.0
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ll = np.clip(ll + (0.5 + 0.5 * np.sin((xx / W * 3.0 + yy / H * 1.2) * np.pi))[..., None] * 0.16 - 0.08, 0, 1)
    sc, me, ch = (np.array(c, np.float32) for c in pal)
    rif = np.exp(-((ll - 0.34) / 0.10) ** 2) * 0.6 + np.exp(-((ll - 0.78) / 0.07) ** 2) * 0.3
    nas = sc * (1 - ll) + me * ll; nas = nas * (1 - rif * 0.55) + ch * rif * 0.55
    ombra = np.asarray(m.filter(ImageFilter.GaussianBlur(60))).astype(np.float32)[..., None] / 255.0
    fondo = fondo * (1 - ombra * (0.35 if scuro else 0.2))
    return fondo * (1 - mm) + nas * mm

def crea(t):
    base = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=base_svg(t).encode(), output_width=W, output_height=H))).convert("RGB")
    f = np.asarray(base).astype(np.float32)
    f = nastro(f, 0.80, 0.06, 0.5, 120, t["argento"], t["notte"])          # sottile argento, dietro
    f = nastro(f, 0.84, 0.07, 0.2, 230, t["onda"], t["notte"])               # onda grande
    f = nastro(f, 0.93, 0.05, 1.0, 150, t["onda"], t["notte"], 1.1)          # onda in primo piano
    f = nastro(f, 0.88, 0.07, 0.35, 34, t["sottile"], t["notte"])           # nastro sottile rosso
    return Image.fromarray(np.clip(f, 0, 255).astype(np.uint8))

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for k, t in TEMI.items():
        if len(sys.argv) > 2 and sys.argv[2] != k: continue
        crea(t).save(os.path.join(out, "SofiOS_%s.png" % t["file"]), optimize=True)
    print("ok")
