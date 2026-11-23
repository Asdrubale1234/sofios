#!/usr/bin/env python3
"""Sofi, la mascotte di SofiOS: sei proposte strutturalmente diverse della Lanterna-robot. Disegni vettoriali (SVG).
Uso: mascotte_sofi.py CARTELLA_USCITA"""
import os, sys
import cairosvg

DEFS = """
<linearGradient id="arg" x1="0" x2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".5" stop-color="#dfe4ea"/><stop offset="1" stop-color="#aab3bf"/></linearGradient>
<linearGradient id="argV" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f5f7fa"/><stop offset="1" stop-color="#b7bfca"/></linearGradient>
<linearGradient id="ros" x1="0" x2="1"><stop offset="0" stop-color="#f0384a"/><stop offset=".5" stop-color="#d4142b"/><stop offset="1" stop-color="#9c0c1f"/></linearGradient>
<linearGradient id="rosV" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ee3447"/><stop offset="1" stop-color="#b30f23"/></linearGradient>
<linearGradient id="vis" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2b3140"/><stop offset=".5" stop-color="#0c0f16"/><stop offset="1" stop-color="#141a26"/></linearGradient>
<linearGradient id="vetro" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffbe0"/><stop offset="1" stop-color="#ffd25e"/></linearGradient>
<radialGradient id="alone" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff2b8" stop-opacity=".95"/><stop offset=".4" stop-color="#ffd25e" stop-opacity=".55"/><stop offset="1" stop-color="#ffd25e" stop-opacity="0"/></radialGradient>
<linearGradient id="mare" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#35cfd0"/><stop offset="1" stop-color="#1678b8"/></linearGradient>
<linearGradient id="sfondo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f8f9fb"/><stop offset="1" stop-color="#dde2ea"/></linearGradient>
<filter id="ombra" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#1b2330" flood-opacity=".25"/></filter>
"""
ORO = "#ffd25e"; TURCHESE = "#36d6d0"; VIOLA = "#a58bff"

def occhi(cx, cy, w, h, emo, col=ORO):
    """visore nero con occhi luminosi; w,h = misura del visore. emo: felice, concentrata, curiosa, preoccupata, soddisfatta, attenta"""
    s = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="url(#vis)"/>' % (cx - w / 2, cy - h / 2, w, h, h * 0.42),
         '<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="#ffffff" stroke-opacity=".28" stroke-width="%.1f" stroke-linecap="round"/>' % (cx - w * 0.38, cy - h * 0.34, cx, cy - h * 0.52, cx + w * 0.38, cy - h * 0.34, h * 0.06)]
    ex = w * 0.22; r = h * 0.2; g = 'fill="%s"' % col; ln = 'fill="none" stroke="%s" stroke-width="%.1f" stroke-linecap="round" stroke-linejoin="round"' % (col, h * 0.11)
    for sg in (-1, 1):
        x = cx + sg * ex
        if emo == "felice": s.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" %s/>' % (x - r, cy + r * 0.5, x, cy - r * 1.3, x + r, cy + r * 0.5, ln))
        elif emo == "concentrata": s.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" %s/>' % (x - r * 1.1, cy - r * 0.3, r * 2.2, r * 0.7, r * 0.3, g))
        elif emo == "curiosa": rr = r * (1.25 if sg > 0 else 0.85); s.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" %s/><circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fff"/>' % (x, cy, rr, rr * 1.15, g, x + rr * 0.3, cy - rr * 0.3, rr * 0.28))
        elif emo == "preoccupata": s.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" %s/><path d="M%.1f %.1f L%.1f %.1f" %s/>' % (x, cy + r * 0.2, r * 0.8, r * 1.0, g, x - sg * r * 1.2, cy - r * 1.35, x + sg * r * 1.0, cy - r * 1.0, ln))
        elif emo == "soddisfatta": s.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f Z" %s/>' % (x - r * 1.1, cy + r * 0.1, x, cy - r * 1.5, x + r * 1.1, cy + r * 0.1, g))
        else: s.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" %s/><circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fff" opacity=".9"/>' % (x, cy, r * 1.0, r * 1.25, g, x - r * 0.25, cy - r * 0.4, r * 0.28))
    return "".join(s)

def torre(cx, y0, wb, wt, h, band=True):
    s = ['<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="url(#arg)"/>' % (cx - wb / 2, y0, cx + wb / 2, y0, cx + wt / 2, y0 - h, cx - wt / 2, y0 - h)]
    if band:
        f = 0.22; wb1 = wb + (wt - wb) * f; wb2 = wb + (wt - wb) * (f + 0.2)
        s.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="url(#rosV)"/>' % (cx - wb1 / 2, y0 - h * f, cx + wb1 / 2, y0 - h * f, cx + wb2 / 2, y0 - h * (f + 0.2), cx - wb2 / 2, y0 - h * (f + 0.2)))
    return "".join(s)

def lanterna(cx, y, w, h, luce=ORO, tetto=True):
    s = ['<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="url(#alone)"/>' % (cx, y - h / 2, w * 1.6, h * 1.9),
         '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="%s"/>' % (cx - w / 2, y - h, w, h, h * 0.18, luce)]
    for dx in (-0.25, 0.25): s.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#c6ced8"/>' % (cx + dx * w - 1.2, y - h, 2.4, h))
    if tetto: s.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="url(#ros)"/><circle cx="%.1f" cy="%.1f" r="%.1f" fill="url(#arg)"/>' % (cx - w * 0.6, y - h, cx + w * 0.6, y - h, cx, y - h - h * 0.9, cx, y - h - h * 0.95, h * 0.13))
    return "".join(s)

def braccio(x, y, lung, ang, sp=9):
    return ('<g transform="translate(%.1f %.1f) rotate(%d)"><rect x="%.1f" y="0" width="%.1f" height="%.1f" rx="%.1f" fill="url(#arg)"/>'
            '<circle cx="0" cy="0" r="%.1f" fill="url(#argV)"/><circle cx="0" cy="%.1f" r="%.1f" fill="url(#arg)"/></g>' % (x, y, ang, -sp / 2, sp, lung, sp / 2, sp * 0.9, lung, sp * 0.8))

def gamba(x, y, lung, sp=11):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="url(#arg)"/><ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="url(#ros)"/>'
            % (x - sp / 2, y, sp, lung, sp / 2, x, y + lung, sp * 1.1, sp * 0.55))

def prop(n, emo="felice", luce=ORO, posa="in piedi"):
    """Disegna la proposta n in un riquadro di 400x520 con il centro in (200, 0); base a terra a y=470"""
    s = []
    if n == 1:   # classica: la torre e' corpo e testa, visore nel corpo, arti argentati
        s += [gamba(172, 430, 30), gamba(228, 430, 30), braccio(138, 300, 70, 28), braccio(262, 300, 70, -28), torre(200, 440, 130, 96, 300), lanterna(200, 150, 62, 44, luce),
              '<rect x="146" y="140" width="108" height="14" rx="7" fill="url(#arg)"/>', occhi(200, 225, 86, 56, emo, luce if emo != "felice" else ORO)]
    elif n == 2:  # compatta: tozza, grande visore, piedini, niente braccia (mani sospese)
        s += [gamba(168, 440, 18, 12), gamba(232, 440, 18, 12), torre(200, 450, 170, 126, 210), lanterna(200, 245, 74, 46, luce),
              '<rect x="152" y="235" width="96" height="14" rx="7" fill="url(#arg)"/>', occhi(200, 320, 108, 74, emo, luce),
              '<circle cx="104" cy="365" r="14" fill="url(#arg)"/><circle cx="296" cy="365" r="14" fill="url(#arg)"/>']
    elif n == 3:  # fluttuante: senza gambe, turbina sotto, mani a distanza
        s += ['<ellipse cx="200" cy="495" rx="60" ry="9" fill="#1b2330" opacity=".18"/>', '<path d="M170 420 L230 420 L216 462 L184 462 Z" fill="url(#argV)"/><ellipse cx="200" cy="466" rx="26" ry="8" fill="%s" opacity=".85"/>' % TURCHESE,
              torre(200, 424, 140, 104, 250), lanterna(200, 172, 66, 46, luce), '<rect x="152" y="162" width="96" height="14" rx="7" fill="url(#arg)"/>', occhi(200, 252, 94, 62, emo, luce),
              '<circle cx="104" cy="320" r="17" fill="url(#arg)"/><circle cx="296" cy="320" r="17" fill="url(#arg)"/>']
    elif n == 4:  # doppio corpo: testa = piano alto (lanterna reale a due corpi), corpo = piano basso, giunti robotici
        s += [gamba(176, 440, 26, 10), gamba(224, 440, 26, 10), braccio(142, 355, 60, 35, 8), braccio(258, 355, 60, -35, 8),
              '<rect x="146" y="330" width="108" height="112" rx="14" fill="url(#arg)"/><rect x="146" y="372" width="108" height="26" fill="url(#rosV)"/>',
              '<rect x="178" y="312" width="44" height="22" rx="8" fill="url(#argV)"/>',
              '<rect x="136" y="196" width="128" height="122" rx="20" fill="url(#arg)"/>', occhi(200, 258, 100, 66, emo, luce), lanterna(200, 192, 60, 40, luce)]
    elif n == 5:  # testa-lanterna: la stanza di vetro e' la testa, torso sottile, braccia lunghe
        s += [gamba(184, 420, 40, 10), gamba(216, 420, 40, 10), braccio(160, 300, 90, 20, 8), braccio(240, 300, 90, -20, 8),
              torre(200, 424, 76, 58, 140), '<rect x="140" y="250" width="120" height="14" rx="7" fill="url(#arg)"/>',
              '<rect x="128" y="130" width="144" height="124" rx="38" fill="url(#arg)"/>', occhi(200, 196, 112, 78, emo, luce),
              '<path d="M148 130 L252 130 L200 66 Z" fill="url(#ros)"/><circle cx="200" cy="62" r="8" fill="%s"/>' % luce, '<ellipse cx="200" cy="62" rx="60" ry="46" fill="url(#alone)"/>']
    else:         # luce emozionale: capsula con nucleo luminoso, il colore cambia con lo stato
        s += ['<ellipse cx="200" cy="492" rx="56" ry="8" fill="#1b2330" opacity=".18"/>', gamba(184, 430, 26, 9), gamba(216, 430, 26, 9), braccio(146, 310, 62, 30, 8), braccio(254, 310, 62, -30, 8),
              torre(200, 440, 120, 90, 270, band=False), '<rect x="156" y="372" width="88" height="34" rx="17" fill="url(#vis)"/><circle cx="200" cy="389" r="11" fill="%s"/><circle cx="200" cy="389" r="22" fill="%s" opacity=".35"/>' % (luce, luce),
              lanterna(200, 196, 58, 40, luce), '<rect x="152" y="186" width="96" height="14" rx="7" fill="url(#arg)"/>', occhi(200, 262, 84, 52, emo, luce),
              '<path d="M158 440 L242 440 L240 452 L160 452 Z" fill="url(#rosV)"/>']
    return "".join(s)

def laterale(n):
    """sagoma di profilo semplificata"""
    if n in (1, 4, 5): return torre(200, 440, 100, 70, 290) + lanterna(200, 150, 50, 44) + braccio(205, 300, 66, 12) + gamba(200, 430, 30) + '<rect x="214" y="205" width="30" height="46" rx="14" fill="url(#vis)"/>'
    if n == 2: return torre(200, 450, 130, 96, 210) + lanterna(200, 245, 56, 46) + '<rect x="214" y="300" width="36" height="58" rx="18" fill="url(#vis)"/>' + gamba(200, 440, 18, 12)
    if n == 3: return torre(200, 424, 108, 80, 250) + lanterna(200, 172, 50, 46) + '<rect x="214" y="230" width="34" height="50" rx="16" fill="url(#vis)"/><ellipse cx="200" cy="466" rx="20" ry="7" fill="%s" opacity=".85"/>' % TURCHESE
    return torre(200, 440, 96, 70, 270, band=False) + lanterna(200, 196, 46, 40) + '<rect x="214" y="248" width="30" height="42" rx="14" fill="url(#vis)"/>'

NOMI = {1: "Classica", 2: "Compatta", 3: "Fluttuante", 4: "Doppio corpo", 5: "Testa-lanterna", 6: "Luce emotiva"}
DESC = {1: "La torre è corpo e testa. Visore nel corpo, arti argentati.", 2: "Tozza e simpatica, grande visore, piedini e mani sospese.", 3: "Senza gambe: fluttua con una piccola turbina turchese.",
        4: "Come la vera Lanterna a due corpi: testa e corpo separati.", 5: "La stanza di vetro è la testa; corpo sottile.", 6: "Nucleo luminoso sul petto che cambia colore con lo stato."}
CONSIGLIATA = 1

def tavola(out):
    W, H = 2600, 2100
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" font-family="Inter, Helvetica, Arial, sans-serif">' % (W, H, W, H), "<defs>", DEFS, "</defs>", '<rect width="%d" height="%d" fill="#eef1f5"/>' % (W, H),
         '<text x="60" y="70" font-size="44" font-weight="700" fill="#1b2330">Sofi · sei proposte</text><text x="60" y="108" font-size="22" fill="#5b6573">Davanti, di profilo, volto con sei espressioni, e la luce che cambia con lo stato (parla · ascolta · pensa)</text>']
    for i in range(6):
        n = i + 1; col, riga = i % 3, i // 3
        x0 = 40 + col * 850; y0 = 140 + riga * 960
        s.append('<rect x="%d" y="%d" width="820" height="930" rx="28" fill="url(#sfondo)" stroke="#d0d6df"/>' % (x0, y0))
        s.append('<text x="%d" y="%d" font-size="34" font-weight="700" fill="#1b2330">%d · %s%s</text>' % (x0 + 28, y0 + 52, n, NOMI[n], "   ★ vicina al tuo consiglio" if n == CONSIGLIATA else ""))
        s.append('<text x="%d" y="%d" font-size="18" fill="#5b6573">%s</text>' % (x0 + 28, y0 + 82, DESC[n]))
        s.append('<g transform="translate(%d %d) scale(1.3)" filter="url(#ombra)">%s</g>' % (x0 + 5, y0 + 105, prop(n)))
        s.append('<g transform="translate(%d %d) scale(.6)">%s</g>' % (x0 + 500, y0 + 560, laterale(n)))
        # volto: sei espressioni
        for k, e in enumerate(("felice", "concentrata", "curiosa", "preoccupata", "soddisfatta", "attenta")):
            cx = x0 + 585 + (k % 2) * 140; cy = y0 + 190 + (k // 2) * 105
            vw = {1: 86, 2: 108, 3: 94, 4: 100, 5: 112, 6: 84}[n]; vh = {1: 56, 2: 74, 3: 62, 4: 66, 5: 78, 6: 52}[n]
            sc = 112 / vw
            s.append('<g transform="translate(%.1f %.1f) scale(%.2f) translate(%.1f %.1f)">%s</g>' % (cx, cy, sc, -0, -0, occhi(0, 0, vw, vh, e)))
            s.append('<text x="%.1f" y="%.1f" font-size="14" fill="#5b6573" text-anchor="middle">%s</text>' % (cx, cy + 52, e))
        # luci di stato
        for k, (nome, c) in enumerate((("parla", ORO), ("ascolta", TURCHESE), ("pensa", VIOLA))):
            cx = x0 + 150 + k * 150; cy = y0 + 800
            s.append('<circle cx="%d" cy="%d" r="44" fill="%s" opacity=".35"/><circle cx="%d" cy="%d" r="22" fill="%s"/><text x="%d" y="%d" font-size="16" fill="#1b2330" text-anchor="middle">%s</text>' % (cx, cy, c, cx, cy, c, cx, cy + 70, nome))
    s.append('</svg>')
    svg = "\n".join(s)
    open(os.path.join(out, "Sofi_sei_proposte.svg"), "w").write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(out, "Sofi_sei_proposte.png"), output_width=2600, output_height=2100)

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True); tavola(out); print("ok")
