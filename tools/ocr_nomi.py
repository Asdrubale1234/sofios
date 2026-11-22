#!/usr/bin/env python3
"""Legge con il riconoscimento del testo tutte le foto di una cartella e cerca i nomi del sistema sottostante.
Uso: ocr_nomi.py CARTELLA_FOTO [USCITA.json]   (serve rapidocr-onnxruntime)"""
import glob, json, os, re, sys
from rapidocr_onnxruntime import RapidOCR
PAROLE = r"KDE|Plasma|Debian|Kubuntu|Ubuntu|Breeze|Brezza|Dolphin|Konsole|KWrite|Okular|Gwenview|Spectacle|Kirigami|KWin|Baloo|KRunner|Akonadi|Kontact|Discover|Frameworks|deb1[0-9]|GNU/Linux|Linux"
rx = re.compile(r"(?<![A-Za-z])(" + PAROLE + r")(?![a-z])", re.I)
ocr = RapidOCR()
cart = sys.argv[1]
ris = []
for f in sorted(glob.glob(os.path.join(cart, "*.png"))):
    import cv2
    img = cv2.imread(f)
    r, _ = ocr(img)
    for box, testo, conf in (r or []):
        m = rx.search(testo)
        if m:
            ris.append({"foto": os.path.basename(f), "parola": m.group(1), "testo": testo, "conf": round(float(conf), 2)})
if len(sys.argv) > 2:
    json.dump(ris, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
for x in ris: print(x["foto"], "|", x["parola"], "|", x["testo"])
print("trovati:", len(ris))
