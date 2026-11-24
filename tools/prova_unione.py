import os, sys, time, shutil, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "live/config/includes.chroot_after_packages/usr/local/lib/sofios"))
from pykeepass import create_database, PyKeePass
import cassaforte_unione as U
d = tempfile.mkdtemp(); pw = "provaprova"
base = os.path.join(d, "base.kdbx"); kp = create_database(base, password=pw)
g = kp.add_group(kp.root_group, "Banca")
kp.add_entry(kp.root_group, "Posta", "luca", "p1", url="https://posta.it"); kp.add_entry(g, "Conto", "luca", "c1", notes="àèì ☺\nseconda riga")
kp.add_entry(kp.root_group, "DaCancellare", "x", "x"); kp.add_entry(kp.root_group, "Comune", "a", "a"); kp.save()
A = os.path.join(d, "A.kdbx"); B = os.path.join(d, "B.kdbx"); shutil.copy(base, A); shutil.copy(base, B)
time.sleep(1.1)
a = PyKeePass(A, password=pw)                                    # dispositivo A: modifica Posta, nuova voce, elimina DaCancellare
e=a.find_entries(title="Posta", first=True); e.save_history(); e.password = "p2-da-A"; U.modificata(e); a.add_entry(a.root_group, "SoloA", "u", "pa")
U.elimina_voce(a, a.find_entries(title="DaCancellare", first=True)); a.save()
time.sleep(1.1)
b = PyKeePass(B, password=pw)                                    # dispositivo B: modifica Posta (dopo), Conto, nuova voce, modifica DaCancellare (prima dell'eliminazione? no: dopo non c'e')
e=b.find_entries(title="Posta", first=True); e.save_history(); e.password = "p3-da-B"; U.modificata(e); e=b.find_entries(title="Conto", first=True); e.save_history(); e.password = "c2-da-B"; U.modificata(e)
b.add_entry(b.root_group, "SoloB", "u", "pb"); b.add_entry(b.root_group.subgroups[0] if b.root_group.subgroups else b.root_group, "ContoNuovo", "u", "pn"); b.save()
r = U.unisci(A, B, pw)
m = PyKeePass(A, password=pw)
t = {e.title: e.password for e in m.entries}
print(r); print(t)
assert t["Posta"] == "p3-da-B", "vince l'ultima modifica"
assert any(x.password == "p2-da-A" for x in m.find_entries(title="Posta", first=True).history), "la versione persa resta in cronologia"
assert t["Conto"] == "c2-da-B" and "SoloA" in t and "SoloB" in t and "ContoNuovo" in t
assert "DaCancellare" not in t, "le eliminate restano eliminate"
assert m.find_entries(title="Conto", first=True).notes == "àèì ☺\nseconda riga" and m.find_entries(title="Conto", first=True).parentgroup.name == "Banca"
# idempotenza e simmetria: unire di nuovo non cambia
r2 = U.unisci(A, B, pw); m2 = PyKeePass(A, password=pw); assert {e.title: e.password for e in m2.entries} == t
# l'altra direzione: B unito con A ha lo stesso contenuto
U.unisci(B, A, pw); mb = PyKeePass(B, password=pw); assert {e.title: e.password for e in mb.entries} == t, {e.title: e.password for e in mb.entries}
# una voce eliminata su un lato e modificata dopo sull'altro torna in vita
C = os.path.join(d, "C.kdbx"); D = os.path.join(d, "D.kdbx"); shutil.copy(A, C); shutil.copy(A, D); time.sleep(1.1)
c = PyKeePass(C, password=pw); U.elimina_voce(c, c.find_entries(title="Comune", first=True)); c.save(); time.sleep(1.1)
dd = PyKeePass(D, password=pw); e=dd.find_entries(title="Comune", first=True); e.password = "nuova"; U.modificata(e); dd.save()
U.unisci(C, D, pw); mc = PyKeePass(C, password=pw); assert {e.title: e.password for e in mc.entries}["Comune"] == "nuova"
print("TUTTE LE PROVE OK; file .bak presente:", os.path.exists(A + ".bak"), "versione:", m.version)
