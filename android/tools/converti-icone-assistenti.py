#!/usr/bin/env python3
"""Converte le icone degli assistenti del computer (SVG) in icone Android (VectorDrawable) e stampa i colori del riquadro.
Uso: converti-icone-assistenti.py <cartella-con-gli-svg> <cartella-drawable-uscita>"""
import re, sys, os, glob

def percorso(d):
    # tokenizzazione che sa leggere i flag compatti degli archi (es. "a4 4 0 018 0")
    pos = 0; cmd = None; out = []
    n = len(d)
    num = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
    def salta():
        nonlocal pos
        while pos < n and d[pos] in " ,\t\r\n": pos += 1
    pesi = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}
    while True:
        salta()
        if pos >= n: break
        if d[pos].isalpha():
            cmd = d[pos]; pos += 1
            if cmd in "Zz": out.append("Z"); continue
        k = pesi[cmd.upper()]
        vals = []
        for j in range(k):
            salta()
            if cmd.upper() == "A" and j in (3, 4):
                vals.append(d[pos]); pos += 1      # flag: un solo carattere
            else:
                m = num.match(d, pos)
                if not m: raise ValueError("percorso non leggibile: " + d[pos:pos + 20])
                vals.append(m.group(0)); pos += m.end() - m.start()
        out.append(cmd + " " + " ".join(vals))
        if cmd == "M": cmd = "L"
        elif cmd == "m": cmd = "l"
    return " ".join(out)

def cerchio(cx, cy, r):
    return "M %g,%g a %g,%g 0 1,0 %g,0 a %g,%g 0 1,0 %g,0 z" % (cx - r, cy, r, r, 2 * r, r, r, -2 * r)

def rettangolo(x, y, w, h, rx):
    rx = min(rx, w / 2, h / 2)
    if rx == 0: return "M %g,%g h %g v %g h %g z" % (x, y, w, h, -w)
    return ("M %g,%g h %g a %g,%g 0 0,1 %g,%g v %g a %g,%g 0 0,1 %g,%g h %g a %g,%g 0 0,1 %g,%g v %g a %g,%g 0 0,1 %g,%g z"
            % (x + rx, y, w - 2 * rx, rx, rx, rx, rx, h - 2 * rx, rx, rx, -rx, rx, -(w - 2 * rx), rx, rx, -rx, -rx, -(h - 2 * rx), rx, rx, rx, -rx))

def attr(t, nome, predefinito=None):
    m = re.search(r'\b%s="([^"]*)"' % nome, t)
    return m.group(1) if m else predefinito

src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
for f in sorted(glob.glob(os.path.join(src, "*.svg"))):
    nome = os.path.basename(f).replace("sofios-assistente-", "").replace("ass-", "").replace(".svg", "")
    s = open(f, encoding="utf-8").read()
    colori = re.findall(r'stop-color="(#[0-9a-fA-F]{6})"', s)
    gruppo = re.search(r"<g [^>]*>(.*)</g>", s, re.S).group(1)
    percorsi = []
    for el in re.finditer(r"<(path|circle|rect)\b([^>]*)/?>", gruppo):
        tipo, a = el.group(1), el.group(2)
        if tipo == "path": percorsi.append(percorso(attr(a, "d")))
        elif tipo == "circle": percorsi.append(cerchio(float(attr(a, "cx")), float(attr(a, "cy")), float(attr(a, "r"))))
        else: percorsi.append(rettangolo(float(attr(a, "x", "0")), float(attr(a, "y", "0")), float(attr(a, "width")), float(attr(a, "height")), float(attr(a, "rx", "0"))))
    xml = ['<vector xmlns:android="http://schemas.android.com/apk/res/android"',
           '    android:width="48dp" android:height="48dp" android:viewportWidth="24" android:viewportHeight="24">',
           '    <group android:translateX="4.8" android:translateY="4.8" android:scaleX="0.6" android:scaleY="0.6">']
    for p in percorsi:
        xml.append('        <path android:strokeColor="#FFFFFF" android:strokeWidth="1.9" android:strokeLineCap="round" '
                   'android:strokeLineJoin="round" android:pathData="%s" />' % p)
    xml += ['    </group>', '</vector>']
    open(os.path.join(dst, "ic_ass_%s.xml" % nome), "w").write("\n".join(xml) + "\n")
    print(nome, colori)
