#!/usr/bin/env python3
"""SofiOS: genera gli sfondi e le pose di Luma con Nano Banana (Google), direttamente dal tuo computer.
La chiave di Google resta sul tuo computer (variabile GEMINI_API_KEY): non viene salvata ne' inviata a nessun altro.
Uso:  python3 genera.py --prova     (fa UNA sola immagine per controllare che tutto funzioni)
      python3 genera.py             (fa tutte quelle che mancano)
      python3 genera.py sfondi      (solo gli sfondi)   |   python3 genera.py pose   (solo le pose)"""
import base64, json, os, subprocess, sys, time, urllib.request, urllib.error, zipfile

CHIAVE = os.environ.get("GEMINI_API_KEY", "").strip()                   # solo se usi --aistudio (il servizio a prepagamento di AI Studio)
USA_AISTUDIO = "--aistudio" in sys.argv
MODELLO = os.environ.get("MODELLO", "gemini-nano-banana-2.1")           # il modello che su Vertex AI ha gia' funzionato per Luca
REGIONE = os.environ.get("REGIONE", "global")
QUI = os.path.dirname(os.path.abspath(__file__)); RIF = os.path.join(QUI, "riferimenti"); OUT = os.path.join(QUI, "uscita")
SFONDI = [("pc-tv-16x9", "16:9", "4K"), ("pc-tablet-3x2", "3:2", "2K"), ("schermo-largo-21x9", "21:9", "2K"), ("tablet-verticale-3x4", "3:4", "2K"), ("telefono-9x16", "9:16", "2K"), ("orologio-quadrato", "1:1", "2K")]
NOTE_FORMATO = {"pc-tv-16x9": "Per computer e televisione.", "pc-tablet-3x2": "Per computer e tablet.", "schermo-largo-21x9": "Per schermo molto largo: il logo resta al centro, la scena si allarga ai lati.",
                "tablet-verticale-3x4": "Per tablet in verticale: il logo al centro.", "telefono-9x16": "Per telefono in verticale: il logo un poco sopra il centro, per lasciare spazio a orologio e icone.",
                "orologio-quadrato": "Per orologio con schermo tondo: logo piccolo, ben dentro un cerchio centrale; i bordi sfumano dolcemente."}
POSE = [("neutra", "in posa neutra, ferma e serena, braccia lungo i fianchi"), ("saluta", "mentre saluta, con un braccio alzato"),
        ("parla", "mentre parla, con la lanterna accesa di luce gialla e un'espressione di chi sta dicendo qualcosa"), ("ascolta", "mentre ascolta, con la lanterna accesa di luce turchese e una mano all'orecchio"),
        ("pensa", "mentre pensa, con la lanterna accesa di luce viola e una mano al mento"), ("felice", "felice, con le braccia alzate e un grande sorriso"), ("preoccupata", "preoccupata, con le mani strette davanti al petto")]

VOLTI = [("felice", "felice, con un grande sorriso"), ("concentrata", "concentrata, con le sopracciglia leggermente abbassate e lo sguardo fisso"), ("curiosa", "curiosa, con un sopracciglio alzato e lo sguardo di lato"),
         ("preoccupata", "preoccupata, con le sopracciglia inclinate e la bocca storta"), ("soddisfatta", "soddisfatta, con gli occhi socchiusi e un piccolo sorriso"), ("attenta", "attenta, con gli occhi ben aperti e un'espressione vigile")]
POSE_EXTRA = [("sorpresa", "sorpresa, con gli occhi spalancati, la bocca a O e le mani alzate"), ("dorme", "che dorme in piedi, con gli occhi chiusi, la testa un po' reclinata e la lanterna SPENTA")]
ACCESSO = [("scuro", "sfondo-scuro.jpg", "notte stellata sul mare"), ("chiaro", "sfondo-chiaro.jpg", "cielo azzurro sul mare")]

def immagine_b64(nome):
    with open(os.path.join(RIF, nome), "rb") as f: return base64.b64encode(f.read()).decode()

_token = {"v": None}
def gcloud(*args):
    r = subprocess.run(["gcloud"] + list(args), capture_output=True, text=True)
    if r.returncode != 0: raise RuntimeError((r.stderr or r.stdout).strip()[:300])
    return r.stdout.strip()
def token(rinnova=False):
    if rinnova or not _token["v"]: _token["v"] = gcloud("auth", "print-access-token")
    return _token["v"]
def progetto():
    return os.environ.get("PROGETTO") or gcloud("config", "get-value", "project")

def chiedi(testo, riferimenti, rapporto, qualita):
    parti = [{"text": testo}] + [{"inlineData": {"mimeType": "image/jpeg", "data": immagine_b64(r)}} for r in riferimenti]
    cfg = {"responseModalities": ["TEXT", "IMAGE"], "imageConfig": {"aspectRatio": rapporto, "imageSize": qualita}}
    corpo = {"contents": [{"role": "user", "parts": parti}], "generationConfig": cfg}
    q = os.environ.get("QUALITA", "").strip()
    if q.lower() in ("nessuna", "no"): cfg["imageConfig"].pop("imageSize")          # se il modello non accetta la dimensione, la tolgo
    elif q: cfg["imageConfig"]["imageSize"] = q
    if "2.5" in MODELLO: cfg["imageConfig"].pop("imageSize", None)
    if USA_AISTUDIO:
        url = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % MODELLO
        intest = lambda: {"Content-Type": "application/json", "x-goog-api-key": CHIAVE}
    else:
        host = "aiplatform.googleapis.com" if REGIONE == "global" else "%s-aiplatform.googleapis.com" % REGIONE
        url = "https://%s/v1/projects/%s/locations/%s/publishers/google/models/%s:generateContent" % (host, progetto(), REGIONE, MODELLO)
        intest = lambda: {"Content-Type": "application/json", "Authorization": "Bearer " + token()}
    for tentativo in range(4):
        try:
            rq = urllib.request.Request(url, data=json.dumps(corpo).encode(), headers=intest())
            with urllib.request.urlopen(rq, timeout=300) as r: d = json.loads(r.read().decode())
            for c in d.get("candidates", []):
                for p in c.get("content", {}).get("parts", []):
                    dati = p.get("inlineData") or p.get("inline_data")
                    if dati: return base64.b64decode(dati["data"])
            print("   nessuna immagine nella risposta:", json.dumps(d)[:300]); return None
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:500]
            if e.code == 401 and not USA_AISTUDIO: print("   rinnovo il token…"); token(True); continue
            if e.code in (429, 500, 503): print("   il servizio e' occupato, riprovo tra poco…"); time.sleep(20 * (tentativo + 1)); continue
            print("   ERRORE %s: %s" % (e.code, msg)); return None
        except Exception as e:
            print("   errore:", e); time.sleep(10)
    return None

errori_di_fila = 0
def lavoro(nome, testo, rif, rapporto, qualita):
    global errori_di_fila
    percorso = os.path.join(OUT, nome + ".png")
    if os.path.exists(percorso): print("gia' fatta:", nome); return True
    if errori_di_fila >= 3: print("Mi fermo: 3 errori di fila. Controlla il messaggio qui sopra."); raise SystemExit(1)
    print("sto creando:", nome, "(%s, %s)" % (rapporto, qualita))
    dati = chiedi(testo, rif, rapporto, qualita)
    if not dati: errori_di_fila += 1; time.sleep(5); return False
    errori_di_fila = 0
    open(percorso, "wb").write(dati); print("   salvata:", percorso); return True

def main():
    if USA_AISTUDIO and not CHIAVE:
        print("Con --aistudio serve la chiave: export GEMINI_API_KEY=..."); return 1
    if not USA_AISTUDIO:
        try: print("Uso Vertex AI, progetto:", progetto(), "- modello:", MODELLO, "- regione:", REGIONE)
        except Exception as e: print("gcloud non risponde:", e); return 1
    os.makedirs(OUT, exist_ok=True); cosa = [a for a in sys.argv[1:] if not a.startswith("--")]; prova = "--prova" in sys.argv; fatte = 0
    global errori_di_fila
    errori_di_fila = 0
    if not cosa or "sfondi" in cosa:      # (con «extra» si fanno solo i volti, le pose in piu' e gli sfondi di accesso)
        for tema, rif in (("scuro", "sfondo-scuro.jpg"), ("chiaro", "sfondo-chiaro.jpg")):
            for nome, rapporto, q in SFONDI:
                testo = ("Rifai questa immagine di riferimento mantenendo IDENTICI la scena, i colori, lo stile e il logo «S + SofiOS» al centro. Cambia solo l'inquadratura per il formato richiesto (%s). %s "
                         "Il logo sempre al centro e con la stessa proporzione rispetto all'immagine; le cose importanti dentro una zona centrale sicura, perche' ai lati l'immagine puo' essere ritagliata. "
                         "Nessun altro testo, nessuna cornice, nessun dispositivo. Massima nitidezza." % (rapporto, NOTE_FORMATO[nome]))
                if lavoro("sfondo-%s-%s" % (tema, nome), testo, [rif], rapporto, q): fatte += 1
                if prova and fatte: print("Prova fatta: controlla la cartella «uscita»."); return 0
    if not cosa or "pose" in cosa:
        for nome, descr in POSE:
            testo = ("Usa come riferimento la mascotte Luma (il faro di pietra con il viso, il tetto dorato e le piccole braccia): MANTIENI IDENTICI stile, colori, proporzioni e viso. Disegnala %s. "
                     "Figura intera, centrata, stessa grandezza e stessa posizione di tutte le altre pose, con la base sempre alla stessa altezza. Sfondo verde uniforme #00FF00, senza ombre sul verde, "
                     "nessun testo, nessuna etichetta." % descr)
            if lavoro("luma-%s" % nome, testo, ["luma-pose.jpg", "luma-concentrata.jpg"], "1:1", "1K"): fatte += 1
            if prova and fatte: print("Prova fatta: controlla la cartella «uscita»."); return 0
    if "extra" in cosa:
        for nome, descr in VOLTI:
            testo = ("Usa come riferimento la mascotte Luma: MANTIENI IDENTICI stile, colori, materiali e viso. Primo piano del volto: solo il viso e la parte alta della torre, inquadrato da vicino. Espressione: %s. "
                     "Sfondo verde uniforme #00FF00, nessun testo, nessuna etichetta." % descr)
            if lavoro("volto-%s" % nome, testo, ["luma-pose.jpg", "luma-concentrata.jpg"], "1:1", "1K"): fatte += 1
        for nome, descr in POSE_EXTRA:
            testo = ("Usa come riferimento la mascotte Luma: MANTIENI IDENTICI stile, colori, proporzioni e viso. Disegnala %s. Figura intera, centrata, stessa grandezza delle altre pose, base alla stessa altezza. "
                     "Sfondo verde uniforme #00FF00, senza ombre sul verde, nessun testo." % descr)
            if lavoro("luma-%s" % nome, testo, ["luma-pose.jpg", "luma-concentrata.jpg"], "1:1", "1K"): fatte += 1
        for tema, rif, scena in ACCESSO:
            testo = ("Rifai questa immagine di riferimento (%s) mantenendo IDENTICI scena, colori e stile, ma SENZA il logo e SENZA nessuna scritta al centro: solo cielo e mare. "
                     "Lascia la parte centrale visivamente tranquilla, per metterci sopra la casella della password. Nessun testo, nessuna cornice." % scena)
            if lavoro("accesso-%s" % tema, testo, [rif], "16:9", "4K"): fatte += 1
    zp = os.path.join(QUI, "risultati-extra.zip" if "extra" in cosa else "risultati.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OUT)):
            if f.endswith(".png") and (("extra" not in cosa) or f.startswith(("volto-", "accesso-", "luma-sorpresa", "luma-dorme"))): z.write(os.path.join(OUT, f), f)
    print("\nFinito. Manda a Claude il file:", zp); return 0

if __name__ == "__main__":
    sys.exit(main())
