#!/usr/bin/env python3
"""Il programma del computer unisce la cassaforte fatta dal tablet (K) con la A, e il risultato deve essere uguale
a quello che ha ottenuto il tablet. Uso: verifica-unione.py <cassaforte_unione.py> <cartella-fixture>"""
import os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[1])))
import cassaforte_unione as U
from pykeepass import PyKeePass
d = sys.argv[2]; pw = "provaprova"
def p(n): return os.path.join(d, n)
def istantanea(f):
    kp = PyKeePass(f, password=pw); righe = []
    for e in kp.entries:
        if kp.recyclebin_group is not None and e.group == kp.recyclebin_group: continue
        storia = ",".join(sorted((h.password or "") for h in e.history))
        righe.append("|".join(["/".join(e.parentgroup.path or []), e.title or "", e.username or "", e.password or "", e.url or "", e.notes or "", storia]))
    for x in kp.tree.getroot().findall("./Root/DeletedObjects/DeletedObject"): righe.append("ELIMINATA|" + x.findtext("UUID"))
    return sorted(righe)
shutil.copy(p("unione-A.kdbx"), p("unione-pc-AK.kdbx")); print("AK", U.unisci(p("unione-pc-AK.kdbx"), p("unione-K.kdbx"), pw))
pc = istantanea(p("unione-pc-AK.kdbx")); kt = istantanea(p("unione-kotlin-AK.kdbx"))
if pc != kt:
    print("DIVERSO\n solo PC:", [x for x in pc if x not in kt], "\n solo tablet:", [x for x in kt if x not in pc]); sys.exit(1)
print("OK: il PC unisce la cassaforte del tablet (con eliminazioni e modifiche) e ottiene lo stesso risultato; voci:", len(pc))
