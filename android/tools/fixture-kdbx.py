#!/usr/bin/env python3
"""Prepara i file di confronto per i collaudi della Cassaforte, con le stesse librerie del computer (pykeepass, argon2)."""
import os, secrets, sys
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
righe = []

# 1) Argon2: risultati veri della libreria Python
from argon2.low_level import hash_secret_raw, Type
for tipo, nome in ((Type.D, "d"), (Type.ID, "id")):
    for t, m, p, n in ((2, 64, 1, 8), (3, 256, 2, 20), (2, 1024, 2, 32)):
        pw, sale = secrets.token_bytes(n), secrets.token_bytes(32)
        h = hash_secret_raw(pw, sale, time_cost=t, memory_cost=m, parallelism=p, hash_len=32, type=tipo, version=19)
        righe.append("\t".join(["argon2", nome, pw.hex(), sale.hex(), str(t), str(m), str(p), h.hex()]))

# 2) Cassaforti create dal programma del computer
from pykeepass import create_database
VOCI = [
    ("Sito di prova", "mario", "segreta123", "http://localhost/login", "prima riga\nseconda riga àèìòù 🌊"),
    ("Conto banca", "luca", "p@ss;wörd#1", "https://banca.example", ""),
    ("Posta", "luca@example.org", "Zx9-quattro-!", "", "nota breve"),
]
def esc(s): return s.replace("\n", "\\n")

def crea(nome, password, variante=None):
    f = os.path.join(out, nome)
    if os.path.exists(f): os.remove(f)
    kp = create_database(f, password=password)
    if variante:
        try: variante(kp)
        except Exception as e:
            print("variante non disponibile:", nome, e); return
    g = kp.add_group(kp.root_group, "Banche")
    for i, (t, u, p, s, n) in enumerate(VOCI):
        kp.add_entry(g if i == 1 else kp.root_group, t, u, p, url=s or None, notes=n or None)
    kp.save()
    print("creato", nome, "formato", kp.version, "kdf", getattr(kp, "kdf_algorithm", "?"), "cifratura", getattr(kp, "encryption_algorithm", "?"))
    righe.append("\t".join(["kdbx", nome, password]))
    for v in VOCI:
        righe.append("\t".join(["voce", nome, v[0], v[1], v[2], v[3], esc(v[4])]))

crea("pc-predefinita.kdbx", "pc-password-1")
def chacha(kp): kp.encryption_algorithm = "chacha20"
def id_(kp): kp.kdf_algorithm = "argon2id"
def aeskdf(kp):
    kp.kdf_algorithm = "aeskdf"
crea("pc-chacha20.kdbx", "pc-password-2", chacha)
crea("pc-argon2id.kdbx", "pc-password-3", id_)
crea("pc-aeskdf.kdbx", "pc-password-4", aeskdf)

open(os.path.join(out, "fixture.tsv"), "w", encoding="utf-8").write("\n".join(righe) + "\n")
print(len(righe), "righe di confronto in", out)
