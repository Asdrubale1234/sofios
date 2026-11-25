#!/usr/bin/env python3
"""SofiOS: genera gli sfondi e le pose di Luma con Nano Banana (Google), direttamente dal tuo computer.
La chiave di Google resta sul tuo computer (variabile GEMINI_API_KEY): non viene salvata ne' inviata a nessun altro.
Uso:  python3 genera.py             (fa TUTTE le immagini che mancano, una sola corsa; salta quelle gia' fatte)
      python3 genera.py --prova     (una sola immagine, per controllare che tutto funzioni)
      python3 genera.py nuovi       (i 28 nuovi: pose funzioni e comandi, volti, installatore, sito, negozio, tablet)
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

NUOVI.update({
 "10-pose-comandi": [(n, STILE_LUMA + "Disegnala " + d + ". " + VERDE, REF_LUMA, "1:1", "1K") for n, d in (
    ("volume", "con un piccolo altoparlante in mano e due archi sonori accanto, con aria attenta"),
    ("luminosita", "che tiene in alto un piccolo sole luminoso, con gli occhi socchiusi per la luce"),
    ("schermata", "che regge una piccola macchina fotografica e fa una foto, con un occhio chiuso"),
    ("tema", "che tiene in una mano un sole e nell'altra una mezzaluna, con aria curiosa"),
    ("disinstalla", "che butta con cura un pacchetto in un piccolo cestino, con aria ordinata"),
    ("apri", "che spalanca una grande finestra luminosa con le due braccia, con aria accogliente"),
    ("chiudi", "che chiude con delicatezza una finestra, con un piccolo gesto gentile"))],
 "11-volti-chat": [(n, "Usa come riferimento la mascotte Luma: MANTIENI IDENTICI stile, colori, materiali e viso. Primo piano del volto: solo il viso e la parte alta della torre. Espressione: " + d + ". Sfondo verde uniforme #00FF00, nessun testo, nessuna etichetta.", REF_LUMA, "1:1", "1K") for n, d in (
    ("ride", "che ride di gusto, con gli occhi chiusi dalla gioia"),
    ("innamorata", "con occhi a forma di cuore e un sorriso dolce"),
    ("triste", "triste, con gli occhi lucidi e le sopracciglia inclinate"),
    ("arrabbiata", "un po' arrabbiata, con le sopracciglia abbassate e la bocca stretta"),
    ("furba", "furba, con un occhiolino e un sorrisetto"),
    ("ok", "con un sorriso sicuro e un sopracciglio alzato, come per dire va bene. IMPORTANTE: primo piano molto ravvicinato come le altre, il viso grande che riempie quasi tutta l'immagine, NON la figura intera"))],
 "12-sito-illustrazioni": [(n, "Illustrazione per il sito di SofiOS, formato 4:3: " + d + ". Grafica 3D morbida come le immagini di riferimento, con mare e cielo sfumati. Nessun testo, nessun logo, nessuna scritta.", REF_LUMA + ["sfondo-chiaro.jpg"], "4:3", "2K") for n, d in (
    ("sicurezza", "Luma accanto a un grande scudo luminoso con un lucchetto"),
    ("privacy", "Luma che tiene un piccolo occhio con una barra sopra, come simbolo di niente spionaggio"),
    ("rete-di-casa", "Luma con una casetta, un portatile, un tablet e un telefono collegati da linee di luce"),
    ("foto", "Luma con una piccola cornice e tante foto che volano dolcemente verso di lei"),
    ("assistenti", "Luma con intorno sette nuvolette di dialogo vuote, senza loghi e senza testo"),
    ("italiano", "Luma sotto un grande cielo, con una piccola bandiera italiana in mano e un'aria orgogliosa"))],
 "13-sostore-categorie": [(n, "Testata larga e bassa per una categoria di un negozio di programmi: " + d + ". Stessa grafica 3D morbida delle immagini di riferimento, mare e cielo sfumati, spazio libero a sinistra per mettere un titolo. Nessun testo, nessun logo.", REF_LUMA + ["sfondo-scuro.jpg"], "21:9", "1K") for n, d in (
    ("giochi", "Luma con un piccolo controller in mano"),
    ("ufficio", "Luma con una piccola scrivania, un foglio e una matita"),
    ("internet", "Luma con un globo terrestre luminoso in mano"),
    ("foto-e-video", "Luma con una macchina fotografica e una pellicola"),
    ("musica", "la mascotte Luma, il faro di pietra con il viso e il tetto dorato (NON una stella, NON un altro personaggio), con grandi cuffie sopra la lanterna e qualche nota musicale intorno"),
    ("sviluppo", "Luma con un piccolo portatile e simboli di codice luminosi"))],
 "14-tablet-primo-avvio": [(n, "Illustrazione verticale per il primo avvio di un'app per tablet: " + d + ". Grafica 3D morbida come le immagini di riferimento, mare e cielo sfumati, Luma in basso e spazio libero in alto. Nessun testo, nessun logo.", REF_LUMA + ["sfondo-chiaro.jpg"], "9:16", "2K") for n, d in (
    ("benvenuto", "Luma che saluta con un braccio alzato"),
    ("sincronizza", "Luma con un tablet e un portatile collegati da linee di luce"),
    ("sicurezza", "Luma con uno scudo luminoso e un lucchetto"))],
 "15-sfondi-con-luma": [("%s-%s" % (tema, fmt.replace(":", "x")), "Sfondo per computer e tablet: mare e cielo come nell'immagine di riferimento, con la mascotte Luma molto piccola (circa un decimo dell'altezza) sul bordo di un piccolo scoglio in basso a sinistra, che guarda l'orizzonte. Niente logo, nessun testo, zona centrale libera.", REF_LUMA + [rif], fmt, "2K")
                        for tema, rif in (("scuro", "sfondo-scuro.jpg"), ("chiaro", "sfondo-chiaro.jpg")) for fmt in ("16:9", "9:16")],
})

NUOVI.update({
 "16-avvio-e-installatore": [
    ("boot-scuro-4x3", "Sfondo per la schermata di avvio del computer (menu di avvio), formato 4:3: stessa scena dell'immagine di riferimento (notte stellata sul mare, onde morbide con linee di luce). Niente logo e nessuna scritta: lascia libera la zona centrale per il logo. Nessun testo.", ["sfondo-scuro.jpg"], "4:3", "1K"),
    ("installatore-testata", "Testata larga e bassa per una schermata di installazione: notte stellata sul mare come nell'immagine di riferimento, con la mascotte Luma piccola a destra che saluta e spazio libero a sinistra. Nessun testo, nessun logo.", REF_LUMA + ["sfondo-scuro.jpg"], "21:9", "1K")],
 "17-avatar": [(n, "Ritratto quadrato di Luma, la mascotte (il faro di pietra con il viso): inquadra il viso e la parte alta della torre da vicino, sorridente, " + d + ". MANTIENI IDENTICI stile, colori e viso dei riferimenti. Nessun testo, nessun logo.", REF_LUMA + [rif], "1:1", "1K")
               for n, d, rif in (("scuro", "con dietro un mare di notte sfumato e blu", "sfondo-scuro.jpg"), ("chiaro", "con dietro un mare chiaro di giorno sfumato e azzurro", "sfondo-chiaro.jpg"))],
 "18-livelli": [(n, "Illustrazione per una scheda dell'installatore, formato 16:9: " + d + ". Grafica 3D morbida come le immagini di riferimento, mare e cielo sfumati chiari, Luma a sinistra e spazio libero a destra. Nessun testo, nessun logo, nessuna scritta.", REF_LUMA + ["sfondo-chiaro.jpg"], "16:9", "1K") for n, d in (
    ("base", "Luma leggera e sorridente che tiene una piccola piuma, per dire che il sistema e' leggero"),
    ("completo", "Luma felice circondata da piccole finestre, un telefono e un portatile, per dire che c'e' tutto"),
    ("android", "Luma con un telefono in mano da cui escono piccole icone colorate generiche, senza loghi"),
    ("windows", "Luma accanto a una grande finestra di legno aperta, con un solo grande vetro azzurro e luminoso, SENZA riquadri colorati e senza nessun logo"))],
})

LOGO_BASE = ("Nuovo logo di SofiOS, sistema operativo italiano. Mantieni l'idea del logo attuale mostrato nei riferimenti: un faro e, ai suoi piedi, un'onda del mare la cui forma disegna chiaramente la lettera S. "
             "Rifallo con uno stile unico e coerente con la mascotte Luma (3D morbido: pietra chiara calda e lanterna dorata, niente rosso, niente vetro): linee pulite, forme semplici, riconoscibile anche molto piccolo. "
             "Il faro NON ha il viso. USA COME MODELLO DI DISEGNO le immagini «logo-modello»: stesso faro di pietra chiara con lanterna dorata, stessa onda a forma di S, stesso stile morbido e luminoso; semplificalo solo dove serve. Nessun altro testo oltre a quello richiesto. ")
NUOVI.update({
 "19-logo": [
    ("icona-scura", LOGO_BASE + "Icona quadrata con angoli morbidi (stile icone Apple); FUORI dal quadrato lo sfondo e' verde uniforme #00FF00 (verra' tolto); dentro, sfondo a sfumatura blu notte e azzurro mare, luce calda dalla lanterna, onda-S chiara in primo piano. Nessun testo.", ["logo-modello-scuro.jpg"] + REF_LUMA, "1:1", "2K"),
    ("icona-chiara", LOGO_BASE + "Icona quadrata con angoli morbidi (stile icone Apple); FUORI dal quadrato lo sfondo e' verde uniforme #00FF00 (verra' tolto); dentro, sfondo a sfumatura azzurro cielo e bianco, onda-S azzurra e bianca in primo piano. Nessun testo.", ["logo-modello-chiaro.jpg"] + REF_LUMA, "1:1", "2K"),
    ("icona-semplice", LOGO_BASE + "Versione ancora piu' semplice, quasi piatta: solo due o tre colori, faro stilizzato e onda-S grande e nitida, adatta a una icona di 32 pixel. Icona quadrata con angoli morbidi; FUORI dal quadrato lo sfondo e' verde uniforme #00FF00 (verra' tolto). Nessun testo.", ["logo-modello-scuro.jpg"] + REF_LUMA, "1:1", "2K"),
    ("icona-onda-grande", LOGO_BASE + "Variante in cui l'onda-S e' la protagonista e occupa gran parte dell'icona, con il faro piu' piccolo sopra la cresta. Icona quadrata con angoli morbidi; FUORI dal quadrato lo sfondo e' verde uniforme #00FF00 (verra' tolto). Nessun testo.", ["logo-modello-scuro.jpg"] + REF_LUMA, "1:1", "2K"),
    ("marchio-scuro", LOGO_BASE + "Marchio orizzontale su sfondo verde uniforme #00FF00 (verra' tolto per renderlo trasparente: NESSUN verde dentro il logo o nel testo, nessuna ombra sul verde, nessun riflesso): a sinistra il simbolo (faro con onda-S) senza il quadrato dell'icona, a destra la scritta «SofiOS» in un carattere moderno, pulito e sottile, bianca. La S del simbolo e la S di «SofiOS» devono avere lo stesso disegno. Scrivi esattamente SofiOS, senza altre parole.", ["logo-modello-scuro.jpg"], "21:9", "2K"),
    ("marchio-chiaro", LOGO_BASE + "Marchio orizzontale su sfondo verde uniforme #00FF00 (verra' tolto per renderlo trasparente: NESSUN verde dentro il logo o nel testo, nessuna ombra sul verde, nessun riflesso): a sinistra il simbolo (faro con onda-S) senza il quadrato dell'icona, a destra la scritta «SofiOS» in un carattere moderno, pulito e sottile, blu scuro. La S del simbolo e la S di «SofiOS» devono avere lo stesso disegno. Scrivi esattamente SofiOS, senza altre parole.", ["logo-modello-chiaro.jpg"], "21:9", "2K")],
})

LABS_BASE = ("Logo per Sofi Labs, una piccola azienda italiana che crea giochi, app e sistemi. Il simbolo di Sofi Labs e' LO STESSO del sistema SofiOS: il faro di pietra chiara con lanterna dorata e, ai suoi piedi, l'onda del mare la cui forma disegna la lettera S (la S di Sofi). "
             "Usa come modello di disegno le immagini «logo-modello»: stesso faro, stessa onda-S, stesso stile morbido e luminoso, senza il viso. Linee pulite, riconoscibile anche piccolissimo. Nessun altro testo oltre a quello richiesto. ")
VERDE_LOGO = " su sfondo verde uniforme #00FF00 (verra' tolto per renderlo trasparente: NESSUN verde dentro il logo o nel testo, nessuna ombra sul verde, nessun riflesso)"
NUOVI.update({
 "20-sofi-labs": [
    ("simbolo-monocromo-scuro", LABS_BASE + "Solo il simbolo (faro con onda-S) in UN SOLO COLORE blu scuro, senza sfumature ne' dettagli fotografici, linee nette, adatto a stampa e timbro" + VERDE_LOGO + ". Nessun testo.", ["logo-modello-chiaro.jpg"], "1:1", "2K"),
    ("simbolo-monocromo-chiaro", LABS_BASE + "Solo il simbolo (faro con onda-S) in UN SOLO COLORE bianco, senza sfumature ne' dettagli fotografici, linee nette, per pagine scure" + VERDE_LOGO + ". Nessun testo.", ["logo-modello-scuro.jpg"], "1:1", "2K"),
    ("marchio-scuro", LABS_BASE + "Marchio orizzontale: a sinistra il simbolo (faro con onda-S) senza il quadrato dell'icona, a destra la scritta «Sofi Labs» in un carattere moderno, pulito e sottile. Simbolo E scritta sono dello STESSO unico colore piatto, BIANCO, senza sfumature ne' dettagli fotografici (per pagine scure; il simbolo e' una silhouette pulita)" + VERDE_LOGO + ". La S del simbolo e la S della scritta hanno lo stesso disegno. Scrivi esattamente «Sofi Labs», senza altre parole.", ["logo-modello-scuro.jpg"], "21:9", "2K"),
    ("marchio-chiaro", LABS_BASE + "Marchio orizzontale: a sinistra il simbolo (faro con onda-S) senza il quadrato dell'icona, a destra la scritta «Sofi Labs» in un carattere moderno, pulito e sottile. Simbolo E scritta sono dello STESSO unico colore piatto, BLU SCURO, senza sfumature ne' dettagli fotografici (per pagine chiare; il simbolo e' una silhouette pulita)" + VERDE_LOGO + ". La S del simbolo e la S della scritta hanno lo stesso disegno. Scrivi esattamente «Sofi Labs», senza altre parole.", ["logo-modello-chiaro.jpg"], "21:9", "2K"),
    ("prodotto-di-scuro", LABS_BASE + "Piccolo sigillo da mettere accanto ai prodotti, per pagine scure: il simbolo piccolo (faro con onda-S, senza quadrato, silhouette piatta) e accanto la scritta su due righe: «Un prodotto di» in piccolo, sotto «Sofi Labs» piu' grande. TUTTO (simbolo e scritte) di un unico colore piatto BIANCO" + VERDE_LOGO + ". Scrivi esattamente queste parole, senza altro.", ["logo-modello-scuro.jpg"], "21:9", "1K"),
    ("prodotto-di-chiaro", LABS_BASE + "Piccolo sigillo da mettere accanto ai prodotti, per pagine chiare: il simbolo piccolo (faro con onda-S, senza quadrato, silhouette piatta) e accanto la scritta su due righe: «Un prodotto di» in piccolo, sotto «Sofi Labs» piu' grande. TUTTO (simbolo e scritte) di un unico colore piatto BLU SCURO" + VERDE_LOGO + ". Scrivi esattamente queste parole, senza altro.", ["logo-modello-chiaro.jpg"], "21:9", "1K")],
})

SOCIAL_BASE = ("Immagine di sfondo per le copertine dei social di Sofi Labs, piccola azienda italiana di software. Scena elegante e pulita: un faro lontano e sottile sul mare, "
               "grafica 3D morbida come le immagini di riferimento, nessun personaggio col viso. La parte CENTRALE e' tranquilla e vuota (ci metteremo sopra il logo), il faro sta ai lati o in basso, mai al centro. "
               "Nessun testo, nessun logo, nessuna scritta. ")
NUOVI.update({
 "21-social-e-sito": [
    ("youtube-banner-scuro", SOCIAL_BASE + "Notte stellata sul mare, faro con luce calda a destra, grande spazio libero al centro. Formato 16:9, il contenuto importante solo nella fascia centrale.", ["sfondo-scuro.jpg", "logo-attuale-scuro.jpg"], "16:9", "2K"),
    ("banner-largo-scuro", SOCIAL_BASE + "Notte stellata sul mare, faro con luce calda a sinistra in basso, mare calmo e cielo vuoto al centro. Formato molto largo, orizzonte basso.", ["sfondo-scuro.jpg", "logo-attuale-scuro.jpg"], "21:9", "2K"),
    ("banner-largo-chiaro", SOCIAL_BASE + "Mattina limpida sul mare, cielo azzurro e pesca, faro chiaro a destra in basso, spazio libero al centro. Formato molto largo, orizzonte basso.", ["sfondo-chiaro.jpg", "logo-attuale-chiaro.jpg"], "21:9", "2K"),
    ("sito-header-scuro", SOCIAL_BASE + "Testata larga per il sito web, notte sul mare con onde morbide e linee di luce, faro lontano a destra, spazio libero a sinistra e al centro per un titolo.", ["sfondo-scuro.jpg", "logo-attuale-scuro.jpg"], "21:9", "2K"),
    ("sito-header-chiaro", SOCIAL_BASE + "Testata larga per il sito web, giorno luminoso sul mare, onde morbide, faro lontano a destra, spazio libero a sinistra e al centro per un titolo.", ["sfondo-chiaro.jpg", "logo-attuale-chiaro.jpg"], "21:9", "2K"),
    ("miniatura-youtube-modello", SOCIAL_BASE + "Modello per le miniature dei video: mare e cielo al tramonto, faro sul lato destro, tutto il lato sinistro libero per scrivere un titolo grande. Formato 16:9.", ["sfondo-chiaro.jpg", "logo-attuale-chiaro.jpg"], "16:9", "2K")],
})

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
    if not cosa or "tutto" in cosa: cosa = ["gruppi", "nuovi"]     # senza parole: fa TUTTO quello che manca
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
                    if Image and not cartella.startswith(("7-", "10-", "11-")):
                        tmp = pf[:-4] + ".jpg"; Image.open(pf).convert("RGB").save(tmp, quality=90); z.write(tmp, cartella + "/" + f[:-4] + ".jpg"); os.remove(tmp)
                    else: z.write(pf, cartella + "/" + f)
            print("zip pronto:", zp, "(%d MB)" % (os.path.getsize(zp) // 1000000))
        print("\nFinito. Manda a Claude i file nuovi-*.zip (sono 14, ognuno piccolo)."); return 0
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
