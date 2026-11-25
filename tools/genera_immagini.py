#!/usr/bin/env python3
"""SofiOS: genera gli sfondi e le pose di Luma con Nano Banana (Google), direttamente dal tuo computer.
La chiave di Google resta sul tuo computer (variabile GEMINI_API_KEY): non viene salvata ne' inviata a nessun altro.
Uso:  python3 genera.py --prova     (fa UNA sola immagine per controllare che tutto funzioni)
      python3 genera.py             (fa tutte quelle che mancano)
      python3 genera.py nuovi       (i 28 nuovi: sfondi senza logo, pose funzioni, installatore, sito)
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

REF_LUMA = ["luma-pose.jpg", "luma-concentrata.jpg"]
STILE_LUMA = ("Usa come riferimento la mascotte Luma (il faro di pietra con il viso, il tetto dorato e le piccole braccia): MANTIENI IDENTICI stile, colori, materiali, proporzioni e viso. ")
VERDE = "Figura intera, centrata, stessa grandezza delle altre pose, base alla stessa altezza. Sfondo verde uniforme #00FF00, senza ombre sul verde, nessun testo, nessuna etichetta."
GRUPPI = {
 "1-pose-eventi": [(n, STILE_LUMA + "Disegnala " + d + ". " + VERDE, REF_LUMA, "1:1", "1K") for n, d in (
    ("scarica", "mentre scarica qualcosa: tiene tra le braccia un grande pacco con una freccia verso il basso, espressione concentrata"),
    ("cerca", "mentre cerca qualcosa con una grande lente d'ingrandimento in mano, un occhio incuriosito"),
    ("batteria-scarica", "stanca e un po' afflosciata, con la lanterna quasi spenta e una piccola batteria scarica ai piedi"),
    ("senza-internet", "perplessa, con una mano a visiera sopra gli occhi come chi cerca il segnale lontano, e una piccola antenna spenta accanto"),
    ("fatto", "soddisfatta, con il pollice alzato e un sorriso sicuro"),
    ("errore", "dispiaciuta, con le mani aperte come per scusarsi e un sopracciglio inclinato"))],
 "2-avvio": [("avvio-sfondo-scuro", "Rifai questa immagine di riferimento (notte stellata sul mare) mantenendo identici scena, colori e stile, ma SENZA logo e SENZA scritte: solo cielo stellato e mare scuro, con il centro tranquillo, per metterci sopra un logo che compare all'accensione. Nessun testo.", ["sfondo-scuro.jpg"], "16:9", "4K"),
             ("avvio-sfondo-scuro-verticale", "Stessa scena (notte stellata sul mare), senza logo e senza scritte, in formato verticale per un tablet o un telefono. Nessun testo.", ["sfondo-scuro.jpg"], "9:16", "2K")],
 "3-sfondi-extra": [("%s-%s-%s" % (tema, nome, fmt.replace(":", "x")), ("Nuova variante dello sfondo di SofiOS. Stesso stile e stessa grafica dell'immagine di riferimento, con il logo «S + SofiOS» al centro e le stesse proporzioni, ma con questa scena: %s. Nessun altro testo, nessuna cornice." % scena), [rif], fmt, "2K")
                    for tema, rif, scene in (("scuro", "sfondo-scuro.jpg", (("alba", "l'alba sul mare, cielo che schiarisce in blu e viola con una luce calda all'orizzonte"), ("tramonto", "il tramonto sul mare, cielo blu profondo e arancio all'orizzonte"), ("luna", "notte con una luna piena sopra il mare che riflette la luce sulle onde"))),
                                             ("chiaro", "sfondo-chiaro.jpg", (("mare-calmo", "mare molto calmo di giorno, cielo limpido azzurro con pochissime nuvole"), ("mattina", "mattina presto sul mare, cielo chiaro con tonalita' pesca e azzurro"), ("nuvole", "cielo azzurro con grandi nuvole bianche morbide sopra il mare")))
                                             ) for nome, scena in scene for fmt in ("16:9", "9:16")],
 "4-sito-e-negozi": [("banner-sostore", "Banner largo per un negozio di programmi, senza nessun testo: la mascotte Luma (il faro di pietra con il viso) a sinistra sulla riva, che saluta, e a destra un mare calmo al tramonto con lo stesso stile delle immagini di riferimento. Spazio libero al centro.", REF_LUMA + ["sfondo-scuro.jpg"], "21:9", "2K"),
                     ("copertina-sito", "Immagine di copertina per un sito: la mascotte Luma sulla roccia di un piccolo faro con il mare azzurro e il cielo al tramonto, stessa grafica 3D morbida delle immagini di riferimento. Nessun testo, nessun logo.", REF_LUMA + ["sfondo-chiaro.jpg"], "16:9", "2K"),
                     ("presentazione", "Immagine pulita per una presentazione: mare e cielo molto sfumati, in tonalita' blu e azzurro come gli sfondi di riferimento, con spazio libero per scrivere. Nessun testo, nessun logo.", ["sfondo-chiaro.jpg"], "16:9", "2K")],
 "5-schermate-vuote": [(n, STILE_LUMA + "Disegnala " + d + ". " + VERDE, REF_LUMA, "1:1", "1K") for n, d in (
    ("nessuna-nota", "che tiene aperto un taccuino con le pagine vuote e una matita, con aria incoraggiante"),
    ("nessun-dispositivo", "che guarda in lontananza un piccolo tablet e un piccolo telefono, con le braccia leggermente aperte come per invitarli"),
    ("offline", "con le braccia incrociate e lo sguardo verso l'alto, in attesa di un segnale che non arriva"),
    ("nessun-risultato", "con una lente d'ingrandimento e le spalle un po' alzate, come chi non ha trovato niente"),
    ("tutto-fatto", "con le braccia alzate in segno di festa e piccoli coriandoli attorno"))],
}

# --- Gruppi nuovi (6-9): tutto SENZA logo e SENZA scritte; il faro ufficiale lo mette il programma di Claude ---
SENZA_LOGO = "SENZA logo e SENZA nessuna scritta: lascia libera la zona centrale, tranquilla, per metterci sopra un logo. Nessun testo, nessuna cornice, nessun dispositivo. Massima nitidezza."
_SC = {"scuro": ("sfondo-scuro.jpg", (("alba", "l'alba sul mare, cielo che schiarisce in blu e viola con una luce calda all'orizzonte"), ("tramonto", "il tramonto sul mare, cielo blu profondo e arancio all'orizzonte"), ("luna", "notte con una luna piena sopra il mare che riflette la luce sulle onde"))),
       "chiaro": ("sfondo-chiaro.jpg", (("mare-calmo", "mare molto calmo di giorno, cielo limpido azzurro con pochissime nuvole"), ("mattina", "mattina presto sul mare, cielo chiaro con tonalita' pesca e azzurro"), ("nuvole", "cielo azzurro con grandi nuvole bianche morbide sopra il mare")))}
_SCENA_INST = "stessa grafica 3D morbida delle immagini di riferimento, con mare e cielo sfumati, la mascotte Luma (il faro di pietra con il viso) a sinistra e spazio libero a destra. Nessun testo, nessun logo, nessuna scritta."
NUOVI = {
 "6-sfondi-senza-logo": [("%s-%s-%s" % (tema, nome, fmt.replace(":", "x")), "Nuova variante dello sfondo di SofiOS. Stesso stile e stessa grafica dell'immagine di riferimento, con questa scena: %s. %s" % (scena, SENZA_LOGO), [rif], fmt, "2K")
                         for tema, (rif, scene) in _SC.items() for nome, scena in scene for fmt in ("16:9", "9:16")],
 "7-pose-funzioni": [(n, STILE_LUMA + "Disegnala " + d + ". " + VERDE, REF_LUMA, "1:1", "1K") for n, d in (
    ("cassaforte", "che custodisce un grande lucchetto dorato stretto al petto, con aria protettiva e sicura"),
    ("foto", "che tiene una fotografia incorniciata in una mano e ha un piccolo cestino accanto, con un sorriso"),
    ("aggiornamenti", "che regge un piccolo globo terrestre con due frecce che girano attorno, con aria attiva"),
    ("stampante", "che porge un foglio di carta appena uscito da una piccola stampante accanto a lei, con aria gentile"),
    ("musica", "con grandi cuffie sopra la lanterna e qualche nota musicale intorno, felice e a ritmo"),
    ("wifi-connesso", "soddisfatta, con tre archi di segnale wi-fi luminosi sopra la lanterna"),
    ("arrivederci", "che saluta con un grande gesto della mano, con aria affettuosa, come quando si spegne il computer"),
    ("schermo-bloccato", "che dorme in piedi, occhi chiusi, la testa reclinata, la lanterna SPENTA e un piccolo lucchetto ai piedi"))],
 "8-installatore": [(n, "Illustrazione larga per una schermata dell'installatore: " + d + ". " + _SCENA_INST, REF_LUMA + ["sfondo-chiaro.jpg"], "16:9", "2K") for n, d in (
    ("benvenuto", "Luma che accoglie e saluta con un braccio alzato, sulla riva al tramonto"),
    ("aspetto", "Luma al centro tra due meta': a sinistra una scena chiara di giorno, a destra la stessa scena scura di notte"),
    ("assistenti", "Luma circondata da sette piccole nuvolette di dialogo vuote, senza nessun logo e senza testo dentro"),
    ("sicurezza", "Luma con davanti uno scudo luminoso con un lucchetto, con aria protettiva"),
    ("dispositivi", "Luma con a fianco un portatile, un tablet e un telefono collegati tra loro da sottili linee di luce"))],
 "9-sito-social": [("anteprima-social", "Immagine per la condivisione sui social, formato largo: la mascotte Luma sulla roccia di un piccolo faro con il mare al tramonto, grafica 3D morbida come le immagini di riferimento, con spazio libero a destra. Nessun testo, nessun logo.", REF_LUMA + ["sfondo-chiaro.jpg"], "16:9", "2K"),
                   ("google-play", "Immagine larga e bassa per un negozio di app: la mascotte Luma a sinistra che saluta, a destra mare calmo e cielo sfumato in blu e azzurro, con spazio libero al centro. Nessun testo, nessun logo.", REF_LUMA + ["sfondo-chiaro.jpg"], "21:9", "2K"),
                   ("sofi-labs", "Immagine quadrata e pulita per un'azienda di software: il faro luminoso di Luma, ma senza viso, stilizzato, di notte sul mare con la luce che si allarga. Nessun testo, nessun logo.", ["sfondo-scuro.jpg", "luma-pose.jpg"], "1:1", "2K")],
}

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
    percorso = os.path.join(OUT, nome + ".png"); os.makedirs(os.path.dirname(percorso), exist_ok=True)
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
    if "gruppi" in cosa:
        for cartella, voci in GRUPPI.items():
            for nome, testo, rif, rapporto, q in voci:
                if lavoro("%s/%s" % (cartella, nome), testo, rif, rapporto, q): fatte += 1
    if "nuovi" in cosa:
        for cartella, voci in NUOVI.items():
            for nome, testo, rif, rapporto, q in voci:
                if lavoro("%s/%s" % (cartella, nome), testo, rif, rapporto, q): fatte += 1
        # zip piccoli: uno per cartella, gli sfondi in JPEG per stare sotto i 30 MB
        try:
            from PIL import Image
        except Exception: Image = None
        for cartella in sorted(NUOVI):
            d = os.path.join(OUT, cartella); zp = os.path.join(QUI, "nuovi-%s.zip" % cartella)
            with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
                for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
                    if not f.endswith(".png"): continue
                    pf = os.path.join(d, f)
                    if Image and not cartella.startswith("7-"):
                        tmp = pf[:-4] + ".jpg"; Image.open(pf).convert("RGB").save(tmp, quality=90); z.write(tmp, cartella + "/" + f[:-4] + ".jpg"); os.remove(tmp)
                    else: z.write(pf, cartella + "/" + f)
            print("zip pronto:", zp, "(%d MB)" % (os.path.getsize(zp) // 1000000))
        print("\nFinito. Manda a Claude i file nuovi-*.zip (sono 4, ognuno piccolo)."); return 0
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
    zp = os.path.join(QUI, "risultati-gruppi.zip" if "gruppi" in cosa else ("risultati-extra.zip" if "extra" in cosa else "risultati.zip"))
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        if "gruppi" in cosa:
            for cartella in sorted(GRUPPI):
                d = os.path.join(OUT, cartella)
                for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
                    if f.endswith(".png"): z.write(os.path.join(d, f), cartella + "/" + f)
        else:
            for f in sorted(os.listdir(OUT)):
                if f.endswith(".png") and (("extra" not in cosa) or f.startswith(("volto-", "accesso-", "luma-sorpresa", "luma-dorme"))): z.write(os.path.join(OUT, f), f)
    print("\nFinito. Manda a Claude il file:", zp); return 0

if __name__ == "__main__":
    sys.exit(main())
