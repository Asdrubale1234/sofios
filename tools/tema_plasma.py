#!/usr/bin/env python3
"""Tema grafico SofiOS per Plasma (barre, Dock, menu, finestre a comparsa): angoli molto morbidi e vetro.
Disegnato da zero, a 9 parti come richiede Plasma. Genera due temi, sofios-scuro e sofios-chiaro, con i colori dei nostri temi.
Uso: tema_plasma.py CARTELLA_INCLUDES"""
import os, re, sys, shutil
inc = sys.argv[1]
P = lambda *a: os.path.join(inc, *a)

def cornice(W, H, R, riempimento, bordo, margine, ombra=0):
    """SVG 9 parti: rettangolo arrotondato (raggio R) con riempimento semitrasparente e filo sottile. Colori dal tema (classi ColorScheme-*)."""
    I = R                                 # larghezza delle parti d'angolo
    def quarto(x, y, sx, sy):             # quarto di cerchio pieno e il suo filo
        # angolo con centro (cx,cy) = vertice interno
        cx = x + (I if sx > 0 else 0); cy = y + (I if sy > 0 else 0)
        px = cx - sx * R if False else None
        return None
    parti = []
    f = 'class="ColorScheme-Background" fill="currentColor" fill-opacity="%.2f"' % riempimento
    l = 'class="ColorScheme-Text" fill="none" stroke="currentColor" stroke-opacity="%.2f" stroke-width="1"' % bordo
    w, h = W, H
    # angoli: percorsi che riempiono il quarto e un arco di filo
    parti.append('<g id="topleft"><path %s d="M0,%d A%d,%d 0 0 1 %d,0 L%d,%d Z"/><path %s d="M0.5,%d A%d,%d 0 0 1 %d,0.5"/></g>' % (f, R, R, R, R, R, R, l, R, R - 0.5, R - 0.5, R))
    parti.append('<g id="topright"><path %s d="M%d,0 A%d,%d 0 0 1 %d,%d L%d,%d Z"/><path %s d="M%d,0.5 A%.1f,%.1f 0 0 1 %.1f,%d"/></g>' % (f, w - R, R, R, w, R, w - R, R, l, w - R, R - 0.5, R - 0.5, w - 0.5, R))
    parti.append('<g id="bottomleft"><path %s d="M0,%d A%d,%d 0 0 0 %d,%d L%d,%d Z"/><path %s d="M0.5,%d A%.1f,%.1f 0 0 0 %d,%.1f"/></g>' % (f, h - R, R, R, R, h, R, h - R, l, h - R, R - 0.5, R - 0.5, R, h - 0.5))
    parti.append('<g id="bottomright"><path %s d="M%d,%d A%d,%d 0 0 1 %d,%d L%d,%d Z"/><path %s d="M%.1f,%d A%.1f,%.1f 0 0 1 %d,%.1f"/></g>' % (f, w, h - R, R, R, w - R, h, w - R, h - R, l, w - 0.5, h - R, R - 0.5, R - 0.5, w - R, h - 0.5))
    parti.append('<g id="top"><rect %s x="%d" y="0" width="%d" height="%d"/><path %s d="M%d,0.5 H%d"/></g>' % (f, R, w - 2 * R, R, l, R, w - R))
    parti.append('<g id="bottom"><rect %s x="%d" y="%d" width="%d" height="%d"/><path %s d="M%d,%.1f H%d"/></g>' % (f, R, h - R, w - 2 * R, R, l, R, h - 0.5, w - R))
    parti.append('<g id="left"><rect %s x="0" y="%d" width="%d" height="%d"/><path %s d="M0.5,%d V%d"/></g>' % (f, R, R, h - 2 * R, l, R, h - R))
    parti.append('<g id="right"><rect %s x="%d" y="%d" width="%d" height="%d"/><path %s d="M%.1f,%d V%d"/></g>' % (f, w - R, R, R, h - 2 * R, l, w - 0.5, R, h - R))
    parti.append('<rect id="center" %s x="%d" y="%d" width="%d" height="%d"/>' % (f, R, R, w - 2 * R, h - 2 * R))
    parti.append('<rect id="hint-tile-center" x="0" y="0" width="1" height="1" fill="none"/>')
    for nome, x, y, ww, hh in (("hint-top-margin", 0, 0, 1, margine), ("hint-bottom-margin", 0, 0, 1, margine), ("hint-left-margin", 0, 0, margine, 1), ("hint-right-margin", 0, 0, margine, 1)):
        parti.append('<rect id="%s" x="%d" y="%d" width="%d" height="%d" fill="none"/>' % (nome, x, y, ww, hh))
    for nome in ("mask-center",):
        parti.append('<rect id="%s" x="%d" y="%d" width="%d" height="%d" fill="none"/>' % (nome, R, R, w - 2 * R, h - 2 * R))
    stile = '<style type="text/css" id="current-color-scheme">.ColorScheme-Text{color:#e6f1ff}.ColorScheme-Background{color:#0b1f33}</style>'
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n<defs>%s</defs>\n%s\n</svg>\n'
            % (w, h, w, h, stile, "\n".join(parti)))

TEMI = {"sofios-scuro": "usr/share/color-schemes/SofiOS.colors", "sofios-chiaro": "usr/share/color-schemes/SofiOSChiaro.colors"}
for nome, colori in TEMI.items():
    d = P("usr/share/plasma/desktoptheme", nome); shutil.rmtree(d, ignore_errors=True)
    for sub in ("widgets", "translucent/widgets", "opaque/widgets", "dialogs", "translucent/dialogs", "opaque/dialogs"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    c = open(P(colori)).read()
    c = re.sub(r"\[General\][^\[]*", "", c)           # il file «colors» di un tema Plasma ha solo le sezioni dei colori
    open(os.path.join(d, "colors"), "w").write(c.strip() + "\n")
    open(os.path.join(d, "metadata.json"), "w").write('{"KPlugin": {"Id": "%s", "Name": "SofiOS vetro %s", "Description": "Barre e menu di vetro con angoli morbidi", "Authors": [{"Name": "SofiOS"}], "License": "GPL-2.0-or-later"}, "KPackageStructure": "Plasma/Theme"}\n' % (nome, "scuro" if "scuro" in nome else "chiaro"))
    for pref, op in (("", 0.80), ("translucent/", 0.62), ("opaque/", 1.0)):
        open(os.path.join(d, pref + "widgets/panel-background.svg"), "w").write(cornice(64, 64, 24, op, 0.20, 8))
        open(os.path.join(d, pref + "dialogs/background.svg"), "w").write(cornice(64, 64, 20, min(1.0, op + 0.1), 0.20, 12))
    open(os.path.join(d, "widgets/tooltip.svg"), "w").write(cornice(64, 64, 14, 0.92, 0.2, 8))
    open(os.path.join(d, "widgets/background.svg"), "w").write(cornice(64, 64, 18, 0.80, 0.2, 10))
print("ok")
