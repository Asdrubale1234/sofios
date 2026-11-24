#!/usr/bin/env python3
"""Confronto dei comandi di Luma: esegue il programma del computer (mascotte_comandi.py) su molte frasi
e scrive cosa ha capito. Il collaudo di Android deve dare le stesse risposte. Uso: fixture-comandi.py <mascotte_comandi.py> <uscita>"""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("mascotte_comandi", sys.argv[1])
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
FRASI = """apri il browser|apri note|aprimi la posta|avvia la calcolatrice|per favore apri le impostazioni|puoi aprire la cassaforte|lancia firefox
chiudi il browser|chiudimi la posta|termina chrome|spegni il video|esci da note
disinstalla gimp|rimuovi krita|togli la calcolatrice|elimina il programma vlc|cancella gmail
installa gimp|installami vlc|scarica libreoffice|aggiungi telegram
cerca fattura|cercami le foto del mare|trova il contratto|dove si trova la ricevuta|cerca file bolletta luce|per favore trova pdf tasse
cerca su internet gatti buffi|trova online ricetta torta|cercami in internet meteo roma
volume al 40|alza il volume|abbassa il volume|alza il volume del 20%|volume 100|metti il volume a cinquanta|muto|togli il muto|riattiva il silenzio|silenzio|smuta
luminosità 70|luminosita al massimo|abbassa la luminosità|alza la luminosità del 30%|schermo più luminoso|luminosità venti
metti il tema scuro|tema chiaro|passa al tema chiaro|cambia in scuro|modalità scura
fai una schermata|screenshot|cattura lo schermo|foto allo schermo
aiuto|cosa sai fare|che cosa puoi fare|comandi
ciao|come stai|grazie mille|
Apri il Browser!|APRI NOTE|  apri   note  |apri è perché|vai su internet|mostrami le foto|fai partire la musica|apri la cartella documenti""".replace("\n", "|").split("|")
def fmt(a):
    if a is None: return ""
    if isinstance(a, tuple): return "%s:%s" % (a[0], a[1])
    return str(a)
righe = []
for f in FRASI:
    az, arg = M.interpreta(f)
    righe.append("\t".join([f, az, fmt(arg)]))
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(righe) + "\n")
print(len(righe), "frasi")
