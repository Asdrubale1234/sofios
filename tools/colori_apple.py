#!/usr/bin/env python3
"""Colori dei temi SofiOS nello stile «Apple»: scuro #1C1C1E, chiaro #F2F2F7, accento blu di sistema, arancione per le azioni principali.
Uso: colori_apple.py CARTELLA_INCLUDES   (riscrive SofiOS.colors e SofiOSChiaro.colors e adatta la decorazione delle finestre scura)"""
import os, sys
inc = sys.argv[1]
P = lambda *a: os.path.join(inc, *a)
def c(t): return "%d,%d,%d" % t
TEMI = {
 "SofiOS": dict(nome="SofiOS", win=(28, 28, 30), win2=(44, 44, 46), view=(28, 28, 30), view2=(36, 36, 38), btn=(58, 58, 60), fg=(255, 255, 255), fgi=(142, 142, 147),
                att=(255, 159, 10), link=(10, 132, 255), vis=(191, 90, 242), neg=(255, 69, 58), neu=(255, 159, 10), pos=(48, 209, 88), sel=(10, 132, 255), deco=(10, 132, 255)),
 "SofiOSChiaro": dict(nome="SofiOS chiaro", win=(242, 242, 247), win2=(229, 229, 234), view=(255, 255, 255), view2=(247, 247, 250), btn=(255, 255, 255), fg=(28, 28, 30), fgi=(110, 110, 115),
                att=(194, 94, 0), link=(0, 122, 255), vis=(142, 68, 173), neg=(255, 59, 48), neu=(194, 94, 0), pos=(36, 150, 66), sel=(0, 122, 255), deco=(0, 122, 255)),
}
for file, t in TEMI.items():
    comune = dict(ForegroundNormal=c(t["fg"]), ForegroundInactive=c(t["fgi"]), ForegroundActive=c(t["att"]), ForegroundLink=c(t["link"]), ForegroundVisited=c(t["vis"]),
                  ForegroundNegative=c(t["neg"]), ForegroundNeutral=c(t["neu"]), ForegroundPositive=c(t["pos"]), DecorationFocus=c(t["deco"]), DecorationHover=c(t["deco"]))
    sez = {"View": dict(BackgroundNormal=c(t["view"]), BackgroundAlternate=c(t["view2"]), **comune), "Window": dict(BackgroundNormal=c(t["win"]), BackgroundAlternate=c(t["win2"]), **comune),
           "Button": dict(BackgroundNormal=c(t["btn"]), BackgroundAlternate=c(t["win2"]), **comune),
           "Selection": dict(BackgroundNormal=c(t["sel"]), BackgroundAlternate=c(t["sel"]), ForegroundNormal="255,255,255", ForegroundInactive="255,255,255", ForegroundActive="255,255,255",
                             ForegroundLink="255,255,255", ForegroundVisited="255,255,255", ForegroundNegative="255,210,210", ForegroundNeutral="255,235,170", ForegroundPositive="210,255,230",
                             DecorationFocus="255,255,255", DecorationHover="255,255,255")}
    for n in ("Tooltip", "Complementary", "Header"): sez[n] = dict(BackgroundNormal=c(t["win"]), BackgroundAlternate=c(t["win2"]), **comune)
    s = "# %s\n[General]\nColorScheme=%s\nName=%s\n\n" % (t["nome"], file, t["nome"])
    for n, d in sez.items(): s += "[Colors:%s]\n" % n + "".join("%s=%s\n" % kv for kv in d.items()) + "\n"
    s += "[WM]\nactiveBackground=%s\nactiveForeground=%s\ninactiveBackground=%s\ninactiveForeground=%s\nactiveBlend=%s\ninactiveBlend=%s\n" % (c(t["win"]), c(t["fg"]), c(t["win2"]), c(t["fgi"]), c(t["fg"]), c(t["fgi"]))
    open(P("usr/share/color-schemes", file + ".colors"), "w").write(s)
# decorazione delle finestre scura: dal blu notte al grigio
d = P("usr/share/aurorae/themes/SofiOS/decoration.svg")
if os.path.exists(d):
    svg = open(d).read()
    for a, b in (("#0b2740", "#262628"), ("#0e2e4d", "#2c2c2e"), ("#08203a", "#1c1c1e"), ("#06182c", "#161618")): svg = svg.replace(a, b)
    open(d, "w").write(svg)
print("ok")
