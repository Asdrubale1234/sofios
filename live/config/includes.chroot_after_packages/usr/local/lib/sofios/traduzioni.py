#!/usr/bin/python3
"""Nomi SofiOS dentro i programmi (titoli delle finestre, pagine): modifica le traduzioni italiane (.mo).
Esempio: Discover -> SoStore, Dolphin -> File. Va rieseguito dopo ogni aggiornamento dei pacchetti
(lo fa /etc/apt/apt.conf.d/99sofios-marchio), perche' un aggiornamento riscrive i file originali.
Uso: traduzioni.py [cartella_locale]   (predefinita /usr/share/locale/it/LC_MESSAGES)"""
import os, struct, sys

# dominio -> sostituzioni dentro le traduzioni
#   "X"  : X sostituito ovunque compaia nelle frasi tradotte
#   "=X" : solo la frase che e' esattamente X
#   "+X" : se X non ha traduzione italiana, la si aggiunge
REGOLE = {
    "plasma-discover": [("Discover", "SoStore"), ("+Discover", "SoStore")],
    "dolphin": [("Dolphin", "File"), ("+Dolphin", "File")],
    "systemsettings": [("=Plasma", "SofiOS")],
}

def leggi(dati):
    magia = struct.unpack("<I", dati[:4])[0]
    e = "<" if magia == 0x950412de else ">"
    _, n, oo, ot = struct.unpack(e + "4I", dati[4:20])
    voci = []
    for i in range(n):
        lo, po = struct.unpack(e + "2I", dati[oo + 8 * i: oo + 8 * i + 8])
        lt, pt = struct.unpack(e + "2I", dati[ot + 8 * i: ot + 8 * i + 8])
        voci.append([dati[po:po + lo], dati[pt:pt + lt]])
    return voci

def scrivi(voci):
    voci = sorted(voci, key=lambda v: v[0])
    n = len(voci); oo = 28; ot = oo + 8 * n; inizio = ot + 8 * n
    ids = b""; trs = b""; tab_o = []; tab_t = []
    for k, _ in voci: tab_o.append((len(k), len(ids))); ids += k + b"\0"
    for _, t in voci: tab_t.append((len(t), len(trs))); trs += t + b"\0"
    out = struct.pack("<7I", 0x950412de, 0, n, oo, ot, 0, 0)
    out += b"".join(struct.pack("<2I", l, inizio + p) for l, p in tab_o)
    out += b"".join(struct.pack("<2I", l, inizio + len(ids) + p) for l, p in tab_t)
    return out + ids + trs

def applica(percorso, regole):
    dati = open(percorso, "rb").read()
    voci = leggi(dati)
    cambiate = 0
    presenti = {v[0] for v in voci}
    for vecchio, nuovo in regole:
        if vecchio.startswith("+") and vecchio[1:].encode() not in presenti:
            voci.append([vecchio[1:].encode(), nuovo.encode()]); cambiate += 1
    regole = [r for r in regole if not r[0].startswith("+")]
    for v in voci:
        if v[0] == b"":   # intestazione del file
            continue
        orig = v[1]
        for vecchio, nuovo in regole:
            if vecchio.startswith("="):
                parti = v[1].split(b"\0")
                v[1] = b"\0".join(nuovo.encode() if p == vecchio[1:].encode() else p for p in parti)
            else:
                v[1] = v[1].replace(vecchio.encode(), nuovo.encode())
        if v[1] != orig: cambiate += 1
    if cambiate:
        tmp = percorso + ".sofios-tmp"
        open(tmp, "wb").write(scrivi(voci)); os.chmod(tmp, 0o644); os.replace(tmp, percorso)
    return cambiate

def main():
    cartella = sys.argv[1] if len(sys.argv) > 1 else "/usr/share/locale/it/LC_MESSAGES"
    for dominio, regole in REGOLE.items():
        p = os.path.join(cartella, dominio + ".mo")
        if not os.path.exists(p): print("SOFIOS traduzioni:", dominio, "non presente"); continue
        try: print("SOFIOS traduzioni:", dominio, "frasi cambiate:", applica(p, regole))
        except Exception as e: print("SOFIOS traduzioni:", dominio, "ERRORE", e)
    return 0
if __name__ == "__main__": sys.exit(main())
