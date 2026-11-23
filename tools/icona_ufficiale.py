#!/usr/bin/env python3
"""Icona ufficiale SofiOS: la Lanterna di Genova sul mare ligure. Tre proposte dello stesso concetto (A, B, C), tutte in SVG.
Uso: icona_ufficiale.py CARTELLA_USCITA [lettera]"""
import os, sys
import cairosvg

DEFS_COMUNI = """
<linearGradient id="torre" x1="0" x2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="#e9edf2"/><stop offset="1" stop-color="#b9c1cc"/></linearGradient>
<linearGradient id="rosso" x1="0" x2="1"><stop offset="0" stop-color="#f0384a"/><stop offset=".5" stop-color="#d4142b"/><stop offset="1" stop-color="#9c0c1f"/></linearGradient>
<linearGradient id="rossoV" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ee3447"/><stop offset="1" stop-color="#b30f23"/></linearGradient>
<linearGradient id="argento" x1="0" x2="1"><stop offset="0" stop-color="#f6f8fb"/><stop offset=".5" stop-color="#cfd5de"/><stop offset="1" stop-color="#9aa3b0"/></linearGradient>
<radialGradient id="luce" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff6c9" stop-opacity="1"/><stop offset=".35" stop-color="#ffdc7a" stop-opacity=".75"/><stop offset="1" stop-color="#ffdc7a" stop-opacity="0"/></radialGradient>
<linearGradient id="vetro" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffbe0"/><stop offset="1" stop-color="#ffd25e"/></linearGradient>
<linearGradient id="raggioL" x1="1" x2="0"><stop offset="0" stop-color="#ffe9a0" stop-opacity=".95"/><stop offset="1" stop-color="#ffe9a0" stop-opacity="0"/></linearGradient>
<linearGradient id="raggioR" x1="0" x2="1"><stop offset="0" stop-color="#ffe9a0" stop-opacity=".95"/><stop offset="1" stop-color="#ffe9a0" stop-opacity="0"/></linearGradient>
<linearGradient id="mareFondo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b86c4"/><stop offset="1" stop-color="#0a3d73"/></linearGradient>
<linearGradient id="mareMedio" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#27c3cf"/><stop offset="1" stop-color="#128aa8"/></linearGradient>
<linearGradient id="mareFronte" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#58dbd6"/><stop offset=".5" stop-color="#1fa7c9"/><stop offset="1" stop-color="#0f5f9c"/></linearGradient>
<linearGradient id="cresta" x1="0" x2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0"/><stop offset=".3" stop-color="#ffffff" stop-opacity=".95"/><stop offset=".7" stop-color="#dbe9f2" stop-opacity=".95"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>
<linearGradient id="riflesso" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff0b8" stop-opacity=".9"/><stop offset="1" stop-color="#fff0b8" stop-opacity="0"/></linearGradient>
"""

def faro(cx, base, alt, larg):
    """torre a due corpi: fascia rossa, balcone argento, lanterna dorata, tetto rosso. cx=centro, base=y della base, alt=altezza totale, larg=larghezza alla base"""
    u = alt / 100.0
    w1 = larg; w2 = larg * 0.72; w3 = larg * 0.62
    y0 = base; y1 = base - 40 * u; y2 = base - 44 * u; y3 = base - 76 * u; y4 = base - 80 * u; y5 = base - 93 * u; y6 = base - 100 * u
    s = []
    s.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="url(#torre)"/>' % (cx - w1 / 2, y0, cx + w1 / 2, y0, cx + w2 / 2, y1, cx - w2 / 2, y1))            # corpo basso
    s.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="url(#rossoV)"/>' % (cx - (w1 + w2) / 4 - 2, y0 - 17 * u, cx + (w1 + w2) / 4 + 2, y0 - 17 * u,
        cx + (w1 + w2) / 4 - 0.3 * (w1 - w2) / 2 + 1, y0 - 26 * u, cx - (w1 + w2) / 4 + 0.3 * (w1 - w2) / 2 - 1, y0 - 26 * u))                                    # fascia rossa
    s.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="url(#argento)"/>' % (cx - w1 * 0.62, y1 - 1 * u, w1 * 1.24, 4.5 * u, 2 * u))                 # balcone
    s.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="url(#torre)"/>' % (cx - w2 * 0.8 / 2, y2 + 0.5 * u, cx + w2 * 0.8 / 2, y2 + 0.5 * u, cx + w3 / 2, y3, cx - w3 / 2, y3))   # corpo alto
    s.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="url(#argento)"/>' % (cx - w2 * 0.62, y3 - 1 * u, w2 * 1.24, 4 * u, 2 * u))                # secondo balcone
    s.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="url(#vetro)"/>' % (cx - w3 * 0.38, y4 - 1.5 * u, w3 * 0.76, 10 * u, 2 * u))                 # lanterna
    for dx in (-0.19, 0.0, 0.19):
        s.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#c9d0d9"/>' % (cx + dx * w3 - 0.6 * u, y4 - 1.5 * u, 1.2 * u, 10 * u))                          # montanti
    s.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="url(#rosso)"/>' % (cx - w3 * 0.5, y4 - 1.5 * u, cx + w3 * 0.5, y4 - 1.5 * u, cx, y5 - 1 * u))                 # tetto rosso
    s.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="url(#argento)"/>' % (cx - 1.1 * u, y5 - 1 * u, 2.2 * u, 7 * u, 1 * u))                     # punta
    return "\n".join(s), (cx, y4 + 3.5 * u)

def onde(y, spess, fronte=True):
    pass

def icona(v):
    sfondi = {"A": ("#fbfcfe", "#d7dde6"), "B": ("#e9f6ff", "#cfe6f5"), "C": ("#e9ecf1", "#c3c9d3")}
    a, b = sfondi[v]
    parti = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">', "<defs>", DEFS_COMUNI,
             '<linearGradient id="sfondo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (a, b),
             '<clipPath id="ritaglio"><rect width="1024" height="1024" rx="228"/></clipPath>', "</defs>", '<g clip-path="url(#ritaglio)">', '<rect width="1024" height="1024" fill="url(#sfondo)"/>']
    if v == "A":
        fz, (lx, ly) = faro(512, 705, 600, 185)
        parti += ['<ellipse cx="%.0f" cy="%.0f" rx="330" ry="260" fill="url(#luce)" opacity=".85"/>' % (lx, ly),
                  '<polygon points="%.0f,%.0f 60,%.0f 60,%.0f" fill="url(#raggioL)"/>' % (lx - 25, ly - 6, ly - 52, ly + 52),
                  '<polygon points="%.0f,%.0f 964,%.0f 964,%.0f" fill="url(#raggioR)"/>' % (lx + 25, ly - 6, ly - 52, ly + 52)]
        parti.append(fz)
        parti += ['<path d="M-20 735 C 160 665, 300 690, 400 742 S 640 815, 810 735 S 960 690, 1044 705 L1044 1044 L-20 1044Z" fill="url(#mareFondo)"/>',
                  '<path d="M-20 790 C 150 730, 330 760, 450 805 S 700 870, 1044 770 L1044 1044 L-20 1044Z" fill="url(#mareMedio)"/>',
                  '<path d="M-20 850 C 140 800, 300 830, 430 880 S 690 940, 1044 840 L1044 1044 L-20 1044Z" fill="url(#mareFronte)"/>',
                  '<path d="M-20 850 C 140 800, 300 830, 430 880 S 690 940, 1044 840" fill="none" stroke="url(#cresta)" stroke-width="12" stroke-linecap="round"/>',
                  '<path d="M-20 790 C 150 730, 330 760, 450 805 S 700 870, 1044 770" fill="none" stroke="url(#cresta)" stroke-width="7" stroke-linecap="round" opacity=".8"/>',
                  '<path d="M470 745 L554 745 L540 1024 L484 1024Z" fill="url(#riflesso)" opacity=".5"/>']
    elif v == "B":
        fz, (lx, ly) = faro(512, 715, 650, 200)
        parti += ['<circle cx="%.0f" cy="%.0f" r="300" fill="url(#luce)" opacity=".9"/>' % (lx, ly), fz,
                  '<path d="M-20 700 C 150 610, 330 660, 430 720 S 650 800, 800 720 S 960 650, 1044 690 L1044 1044 L-20 1044Z" fill="url(#mareFondo)"/>',
                  '<path d="M-20 770 C 120 700, 330 740, 470 800 S 760 860, 1044 740 L1044 1044 L-20 1044Z" fill="url(#mareMedio)"/>',
                  '<path d="M-20 850 C 150 780, 330 820, 470 880 S 760 940, 1044 820 L1044 1044 L-20 1044Z" fill="url(#mareFronte)"/>',
                  '<path d="M-20 850 C 150 780, 330 820, 470 880 S 760 940, 1044 820" fill="none" stroke="url(#cresta)" stroke-width="13" stroke-linecap="round"/>',
                  '<path d="M-20 770 C 120 700, 330 740, 470 800 S 760 860, 1044 740" fill="none" stroke="url(#cresta)" stroke-width="8" stroke-linecap="round" opacity=".85"/>',
                  '<path d="M476 725 L548 725 L536 1024 L488 1024Z" fill="url(#riflesso)" opacity=".5"/>']
    else:
        fz, (lx, ly) = faro(512, 690, 610, 215)
        parti += ['<polygon points="%.0f,%.0f 80,%.0f 80,%.0f" fill="url(#raggioL)"/>' % (lx - 30, ly, ly - 70, ly + 70),
                  '<polygon points="%.0f,%.0f 944,%.0f 944,%.0f" fill="url(#raggioR)"/>' % (lx + 30, ly, ly - 70, ly + 70),
                  '<ellipse cx="%.0f" cy="%.0f" rx="210" ry="200" fill="url(#luce)" opacity=".75"/>' % (lx, ly), fz,
                  '<path d="M-20 720 L1044 720 L1044 1044 L-20 1044Z" fill="url(#mareFondo)"/>',
                  '<path d="M-20 790 C 120 740, 260 760, 360 800 C 470 845, 560 800, 680 770 S 930 760, 1044 800 L1044 1044 L-20 1044Z" fill="url(#mareMedio)"/>',
                  '<path d="M-20 870 C 100 810, 250 820, 340 870 C 430 920, 540 890, 650 850 S 900 830, 1044 890 L1044 1044 L-20 1044Z" fill="url(#mareFronte)"/>',
                  '<path d="M-20 870 C 100 810, 250 820, 340 870 C 430 920, 540 890, 650 850 S 900 830, 1044 890" fill="none" stroke="url(#cresta)" stroke-width="14" stroke-linecap="round"/>',
                  '<path d="M-20 790 C 120 740, 260 760, 360 800 C 470 845, 560 800, 680 770 S 930 760, 1044 800" fill="none" stroke="url(#cresta)" stroke-width="8" stroke-linecap="round" opacity=".85"/>']
    parti += ['<rect x="2" y="2" width="1020" height="1020" rx="226" fill="none" stroke="#ffffff" stroke-opacity=".55" stroke-width="4"/>', "</g>", "</svg>"]
    return "\n".join(parti)

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for v in (sys.argv[2:] or ["A", "B", "C"]):
        svg = icona(v); open(os.path.join(out, "SofiOS_icona_%s.svg" % v), "w").write(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(out, "SofiOS_icona_%s_1024.png" % v), output_width=1024, output_height=1024)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(out, "SofiOS_icona_%s_32.png" % v), output_width=32, output_height=32)
    print("ok")
