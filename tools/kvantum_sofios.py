#!/usr/bin/env python3
"""Ricolora un tema Kvantum (es. WhiteSur scuro) con i colori di SofiOS: grigi -> blu mare, accenti -> azzurro SofiOS.
Uso: kvantum_sofios.py CARTELLA_ORIGINE NOME_ORIGINE NOME_NUOVO CARTELLA_DESTINAZIONE
Esempio: kvantum_sofios.py Kvantum/WhiteSur WhiteSurDark SofiOS ~/.config/Kvantum/SofiOS"""
import os, re, sys

def blend(a, b, t): return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))

# rampa dei grigi (da scuro a chiaro) -> blu SofiOS
RAMPA = [(0x00, (4, 14, 26)), (0x24, (11, 31, 51)), (0x38, (18, 54, 90)), (0x60, (30, 79, 124)),
         (0x80, (60, 110, 160)), (0xb0, (143, 179, 212)), (0xdf, (232, 241, 248)), (0xff, (255, 255, 255))]

def mappa_grigio(v):
    for (v0, c0), (v1, c1) in zip(RAMPA, RAMPA[1:]):
        if v0 <= v <= v1: return blend(c0, c1, (v - v0) / (v1 - v0))
    return RAMPA[-1][1]

ACCENTI = {  # blu/viola di WhiteSur -> azzurri di SofiOS
    "315bef": "1e6fa8", "5294e2": "2a82c2", "144fb8": "17598a", "3484e2": "59a8ff", "a0b4f8": "1e6fa8",
}

def ricolora(testo):
    def sost(m):
        h = m.group(1).lower()
        if h in ACCENTI: return "#" + ACCENTI[h]
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        if max(r, g, b) - min(r, g, b) <= 12 and h not in ("000000", "ffffff"):
            return "#%02x%02x%02x" % mappa_grigio((r + g + b) // 3)
        if h == "31363b": return "#12365a"
        return m.group(0)
    return re.sub(r"#([0-9a-fA-F]{6})\b", sost, testo)

def main():
    src, nome, nuovo, dst = sys.argv[1:5]
    os.makedirs(dst, exist_ok=True)
    for est in ("kvconfig", "svg"):
        t = open(os.path.join(src, nome + "." + est), encoding="utf-8").read()
        t = ricolora(t)
        if est == "kvconfig":
            t = re.sub(r"(?m)^highlight\.color=.*$", "highlight.color=#1e6fa8", t)
            t = re.sub(r"(?m)^inactive\.highlight\.color=.*$", "inactive.highlight.color=#1e6fa8", t)
            t = re.sub(r"(?m)^text\.color=.*$", "text.color=#e8f1f8", t)
            t = re.sub(r"(?m)^(window\.text|button\.text)\.color=.*$", r"\1.color=#e8f1f8", t)
            t = re.sub(r"(?m)^comment=.*$", "comment=Tema SofiOS", t)
            t = re.sub(r"(?m)^author=.*$", "author=SofiOS (basato su WhiteSur, GPL-3.0)", t)
        open(os.path.join(dst, nuovo + "." + est), "w", encoding="utf-8").write(t)
    print("tema scritto in", dst)
main()
