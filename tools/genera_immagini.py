#!/usr/bin/env python3
"""SofiOS: genera gli sfondi e le pose di Luma con Nano Banana (Google), direttamente dal tuo computer.
La chiave di Google resta sul tuo computer (variabile GEMINI_API_KEY): non viene salvata ne' inviata a nessun altro.
Uso:  python3 genera.py --prova     (fa UNA sola immagine per controllare che tutto funzioni)
      python3 genera.py             (fa tutte quelle che mancano)
      python3 genera.py sfondi      (solo gli sfondi)   |   python3 genera.py pose   (solo le pose)"""
import base64, json, os, sys, time, urllib.request, urllib.error, zipfile

CHIAVE = os.environ.get("GEMINI_API_KEY", "").strip()
MODELLO = os.environ.get("MODELLO", "gemini-3-pro-image-preview")      # «Nano Banana Pro»: arriva fino a 4K. Alternativa piu' economica: gemini-2.5-flash-image
QUI = os.path.dirname(os.path.abspath(__file__)); RIF = os.path.join(QUI, "riferimenti"); OUT = os.path.join(QUI, "uscita")
SFONDI = [("pc-tv-16x9", "16:9", "4K"), ("pc-tablet-3x2", "3:2", "2K"), ("schermo-largo-21x9", "21:9", "2K"), ("tablet-verticale-3x4", "3:4", "2K"), ("telefono-9x16", "9:16", "2K"), ("orologio-quadrato", "1:1", "2K")]
NOTE_FORMATO = {"pc-tv-16x9": "Per computer e televisione.", "pc-tablet-3x2": "Per computer e tablet.", "schermo-largo-21x9": "Per schermo molto largo: il logo resta al centro, la scena si allarga ai lati.",
                "tablet-verticale-3x4": "Per tablet in verticale: il logo al centro.", "telefono-9x16": "Per telefono in verticale: il logo un poco sopra il centro, per lasciare spazio a orologio e icone.",
                "orologio-quadrato": "Per orologio con schermo tondo: logo piccolo, ben dentro un cerchio centrale; i bordi sfumano dolcemente."}
POSE = [("neutra", "in posa neutra, ferma e serena, braccia lungo i fianchi"), ("saluta", "mentre saluta, con un braccio alzato"),
        ("parla", "mentre parla, con la lanterna accesa di luce gialla e un'espressione di chi sta dicendo qualcosa"), ("ascolta", "mentre ascolta, con la lanterna accesa di luce turchese e una mano all'orecchio"),
        ("pensa", "mentre pensa, con la lanterna accesa di luce viola e una mano al mento"), ("felice", "felice, con le braccia alzate e un grande sorriso"), ("preoccupata", "preoccupata, con le mani strette davanti al petto")]

def immagine_b64(nome):
    with open(os.path.join(RIF, nome), "rb") as f: return base64.b64encode(f.read()).decode()

def chiedi(testo, riferimenti, rapporto, qualita):
    parti = [{"text": testo}] + [{"inline_data": {"mime_type": "image/jpeg", "data": immagine_b64(r)}} for r in riferimenti]
    corpo = {"contents": [{"parts": parti}], "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": rapporto, "imageSize": qualita}}}
    if "2.5" in MODELLO: corpo["generationConfig"]["imageConfig"].pop("imageSize")     # il modello economico non sceglie la qualita'
    rq = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % MODELLO, data=json.dumps(corpo).encode(),
                                headers={"Content-Type": "application/json", "x-goog-api-key": CHIAVE})
    for tentativo in range(4):
        try:
            with urllib.request.urlopen(rq, timeout=300) as r: d = json.loads(r.read().decode())
            for c in d.get("candidates", []):
                for p in c.get("content", {}).get("parts", []):
                    dati = p.get("inlineData") or p.get("inline_data")
                    if dati: return base64.b64decode(dati["data"])
            print("   nessuna immagine nella risposta:", json.dumps(d)[:300]); return None
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:400]
            if e.code in (429, 500, 503): print("   il servizio e' occupato, riprovo tra poco…"); time.sleep(20 * (tentativo + 1)); continue
            print("   ERRORE %s: %s" % (e.code, msg)); return None
        except Exception as e:
            print("   errore di rete:", e); time.sleep(10)
    return None

def lavoro(nome, testo, rif, rapporto, qualita):
    percorso = os.path.join(OUT, nome + ".png")
    if os.path.exists(percorso): print("gia' fatta:", nome); return True
    print("sto creando:", nome, "(%s, %s)" % (rapporto, qualita))
    dati = chiedi(testo, rif, rapporto, qualita)
    if not dati: return False
    open(percorso, "wb").write(dati); print("   salvata:", percorso); return True

def main():
    if not CHIAVE:
        print("Manca la chiave. In Terminale scrivi:  export GEMINI_API_KEY=\"la-tua-chiave\"   e poi rilancia."); return 1
    os.makedirs(OUT, exist_ok=True); cosa = [a for a in sys.argv[1:] if not a.startswith("--")]; prova = "--prova" in sys.argv; fatte = 0
    if not cosa or "sfondi" in cosa:
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
    zp = os.path.join(QUI, "risultati.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OUT)):
            if f.endswith(".png"): z.write(os.path.join(OUT, f), f)
    print("\nFinito. Manda a Claude il file:", zp); return 0

if __name__ == "__main__":
    sys.exit(main())
