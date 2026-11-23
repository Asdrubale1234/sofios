#!/usr/bin/env python3
"""Apre con la libreria del computer (pykeepass) una cassaforte fatta da Android e confronta le voci attese."""
import sys
from pykeepass import PyKeePass
f, pw, attese = sys.argv[1:4]
kp = PyKeePass(f, password=pw)
atteso = set(tuple(l.rstrip("\n").split("\t")) for l in open(attese, encoding="utf-8") if l.strip())
trovato = set()
cestino = kp.recyclebin_group
for e in kp.entries:
    if cestino is not None and e.group == cestino: continue
    trovato.add((e.title or "", e.username or "", e.password or "", e.url or "", (e.notes or "").replace("\n", "\\n")))
print(f, "formato", kp.version, "voci", len(trovato))
if trovato != atteso:
    print("DIVERSO\n attese ma non trovate:", sorted(atteso - trovato), "\n trovate ma non attese:", sorted(trovato - atteso))
    sys.exit(1)
print("OK: il programma del computer legge tutto come previsto")
