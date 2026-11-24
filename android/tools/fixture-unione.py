#!/usr/bin/env python3
"""Prepara le cassaforti per provare l'UNIONE: due dispositivi (A e B) modificano la stessa cassaforte, e il programma del
computer (cassaforte_unione.py) le unisce. Il tablet deve ottenere lo stesso risultato.
Uso: fixture-unione.py <cassaforte_unione.py> <cartella-uscita>"""
import os, shutil, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[1])))
import cassaforte_unione as U
from pykeepass import create_database, PyKeePass
out = sys.argv[2]; os.makedirs(out, exist_ok=True)
pw = "provaprova"
def p(n): return os.path.join(out, n)

base = p("unione-base.kdbx")
if os.path.exists(base): os.remove(base)
kp = create_database(base, password=pw)
g = kp.add_group(kp.root_group, "Banca")
kp.add_entry(kp.root_group, "Posta", "luca", "p1", url="https://posta.it")
kp.add_entry(g, "Conto", "luca", "c1", notes="àèì ☺\nseconda riga")
kp.add_entry(kp.root_group, "DaCancellare", "x", "x")
kp.add_entry(kp.root_group, "Comune", "a", "a")
kp.save()
shutil.copy(base, p("unione-A.kdbx")); shutil.copy(base, p("unione-B.kdbx"))
time.sleep(1.1)
a = PyKeePass(p("unione-A.kdbx"), password=pw)       # A: modifica Posta, nuova voce, elimina DaCancellare
e = a.find_entries(title="Posta", first=True); e.save_history(); e.password = "p2-da-A"; U.modificata(e)
a.add_entry(a.root_group, "SoloA", "u", "pa")
U.elimina_voce(a, a.find_entries(title="DaCancellare", first=True)); a.save()
time.sleep(1.1)
b = PyKeePass(p("unione-B.kdbx"), password=pw)       # B: modifica Posta (dopo A), Conto, nuove voci
e = b.find_entries(title="Posta", first=True); e.save_history(); e.password = "p3-da-B"; U.modificata(e)
e = b.find_entries(title="Conto", first=True); e.save_history(); e.password = "c2-da-B"; U.modificata(e)
b.add_entry(b.root_group, "SoloB", "u", "pb")
b.add_entry(b.root_group.subgroups[0], "ContoNuovo", "u", "pn"); b.save()
# risultati del programma del computer, nelle due direzioni
shutil.copy(p("unione-A.kdbx"), p("unione-pc-AB.kdbx")); print("AB", U.unisci(p("unione-pc-AB.kdbx"), p("unione-B.kdbx"), pw))
shutil.copy(p("unione-B.kdbx"), p("unione-pc-BA.kdbx")); print("BA", U.unisci(p("unione-pc-BA.kdbx"), p("unione-A.kdbx"), pw))
# C elimina «Comune», D la modifica dopo: deve tornare in vita
shutil.copy(p("unione-A.kdbx"), p("unione-C.kdbx")); shutil.copy(p("unione-A.kdbx"), p("unione-D.kdbx")); time.sleep(1.1)
c = PyKeePass(p("unione-C.kdbx"), password=pw); U.elimina_voce(c, c.find_entries(title="Comune", first=True)); c.save(); time.sleep(1.1)
d = PyKeePass(p("unione-D.kdbx"), password=pw); e = d.find_entries(title="Comune", first=True); e.password = "nuova"; U.modificata(e); d.save()
shutil.copy(p("unione-C.kdbx"), p("unione-pc-CD.kdbx")); print("CD", U.unisci(p("unione-pc-CD.kdbx"), p("unione-D.kdbx"), pw))
