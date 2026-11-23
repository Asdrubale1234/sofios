#!/usr/bin/env python3
"""Sfondi di SofiOS con la Lanterna e il mare ligure (grafica pulita), uno per tema. Uso: sfondo_lanterna.py CARTELLA_USCITA [tema]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cairosvg
from icona_ufficiale import faro, DEFS_COMUNI

TEMI = {
 "argento": dict(file="Silver_Red", cielo=("#fbfcfe", "#d3d9e3"), mare=("#2f9fd6", "#0b4f8a"), medio=("#35d0cf", "#1a8fb4"), fronte=("#7ee4dc", "#1b9fc6"), roccia=("#aeb6c2", "#7a8493"), alone=0.9, notte=False),
 "grafite": dict(file="Dark_Grey_Red", cielo=("#2c2f36", "#111318"), mare=("#17608f", "#082b4d"), medio=("#1c9aa8", "#0f607c"), fronte=("#2fc0c4", "#126b9a"), roccia=("#4a505b", "#23272e"), alone=1.0, notte=True),
 "oro": dict(file="White_Gold", cielo=("#fffdf8", "#e9e3d4"), mare=("#4aa9d0", "#1b6a9c"), medio=("#5fd6cf", "#2a9bb4"), fronte=("#9cebe0", "#3aaed0"), roccia=("#c9c1ae", "#968c76"), alone=0.9, notte=False),
}
W, H = 3840, 2160

def svg(t):
    cx, base = 2900, 1560
    fz, (lx, ly) = faro(cx, base, 1000, 300)
    sc, f = t["cielo"], t
    notte = t["notte"]
    onde = lambda y, amp, ph: "M-100 %d C 500 %d, 900 %d, 1500 %d S 2500 %d, 3200 %d S 3900 %d, 3980 %d L3980 2260 L-100 2260 Z" % (y, y - amp, y + amp, y + ph, y - amp, y + ph, y - amp // 2, y)
    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H), "<defs>", DEFS_COMUNI,
         '<linearGradient id="cielo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % sc,
         '<linearGradient id="m1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % t["mare"],
         '<linearGradient id="m2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % t["medio"],
         '<linearGradient id="m3" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % t["fronte"],
         '<linearGradient id="roccia" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % t["roccia"],
         '<radialGradient id="aloneG" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff2b8" stop-opacity="%.2f"/><stop offset=".45" stop-color="#ffd25e" stop-opacity=".4"/><stop offset="1" stop-color="#ffd25e" stop-opacity="0"/></radialGradient>' % t["alone"],
         "</defs>", '<rect width="%d" height="%d" fill="url(#cielo)"/>' % (W, H)]
    # alone di luce e fasci sottili
    p.append('<ellipse cx="%d" cy="%d" rx="1200" ry="820" fill="url(#aloneG)"/>' % (lx, ly))
    p.append('<polygon points="%d,%d -100,%d -100,%d" fill="url(#raggioL)" opacity="%.2f"/>' % (lx - 60, ly, ly - 170, ly + 150, 0.55 if not notte else 0.5))
    p.append('<polygon points="%d,%d 3980,%d 3980,%d" fill="url(#raggioR)" opacity="%.2f"/>' % (lx + 60, ly, ly - 120, ly + 130, 0.45))
    # mare in lontananza, con la linea dell'orizzonte
    p.append('<rect x="-10" y="1440" width="3860" height="800" fill="url(#m1)"/>')
    p.append('<path d="%s" fill="url(#m1)"/>' % onde(1500, 60, -40))
    p.append('<path d="%s" fill="url(#m2)"/>' % onde(1640, 110, 70))
    p.append('<path d="%s" fill="none" stroke="url(#cresta)" stroke-width="12" stroke-linecap="round" opacity=".8"/>' % onde(1640, 110, 70).split(" L")[0])
    # roccia con il faro
    p.append('<path d="M2380 1700 C 2500 1590, 2700 1540, 2900 1545 C 3150 1540, 3340 1600, 3470 1720 L 3540 1760 L 2300 1760 Z" fill="url(#roccia)"/>')
    p.append(fz)
    p.append('<path d="M2800 1560 L3000 1560 L3040 2200 L2760 2200Z" fill="url(#riflesso)" opacity=".32"/>')
    p.append('<path d="%s" fill="url(#m3)"/>' % onde(1800, 150, 90))
    p.append('<path d="%s" fill="none" stroke="url(#cresta)" stroke-width="16" stroke-linecap="round"/>' % onde(1800, 150, 90).split(" L")[0])
    p.append('<path d="%s" fill="url(#m1)" opacity=".85"/>' % onde(1990, 120, 70))
    p.append('<path d="%s" fill="none" stroke="url(#cresta)" stroke-width="12" stroke-linecap="round" opacity=".7"/>' % onde(1990, 120, 70).split(" L")[0])
    p.append("</svg>")
    return "\n".join(p)

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for k, t in TEMI.items():
        if len(sys.argv) > 2 and sys.argv[2] != k: continue
        s = svg(t); open(os.path.join(out, "SofiOS_%s.svg" % t["file"]), "w").write(s)
        cairosvg.svg2png(bytestring=s.encode(), write_to=os.path.join(out, "SofiOS_%s.png" % t["file"]), output_width=W, output_height=H)
    print("ok")
