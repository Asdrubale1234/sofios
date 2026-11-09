#!/usr/bin/python3
"""Costruisce il pacchetto .xpi dell'estensione Cassaforte Password: costruisci-estensione.py CARTELLA USCITA.xpi"""
import os, sys, zipfile
src, out = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for nome in sorted(os.listdir(src)):
        p = os.path.join(src, nome)
        if os.path.isfile(p): z.write(p, nome)
print("creato", out)
