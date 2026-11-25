#!/usr/bin/env python3
"""Sofi Labs: ricolora il logo a UN colore per ogni progetto, partendo da un file trasparente.
Uso:  python3 tools/logo_colori.py LOGO_TRASPARENTE.png CARTELLA_USCITA "nome=#rrggbb" "altro=#rrggbb" ...
Esempio:  python3 tools/logo_colori.py marchio-chiaro.png kit "sofios=#0a84ff" "bianco=#ffffff" "gioco-rosso=#e5322d"
Il logo non cambia forma: cambia solo il colore, cosi' sta bene sui colori di ogni progetto."""
import os, sys
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
im = Image.open(src).convert("RGBA"); alfa = im.getchannel("A")
base = os.path.splitext(os.path.basename(src))[0]
for voce in sys.argv[3:]:
    nome, colore = voce.split("=")
    c = tuple(int(colore.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    nuovo = Image.new("RGBA", im.size, c + (0,)); nuovo.putalpha(alfa)
    p = os.path.join(out, "%s-%s.png" % (base, nome)); nuovo.save(p); print(p)
