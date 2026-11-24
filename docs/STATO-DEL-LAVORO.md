# SofiOS per PC: stato del lavoro (23/11/2026)

## Cos'è
Sistema operativo italiano, semplice, basato su Debian 13 con desktop KDE Plasma, con aspetto, nomi e icone tutti nostri. Si prova da chiavetta senza installare, oppure si installa.
Versione pronta: ISO `iso-20261123-1246`, costruita da `main` (pagina dei rilasci del progetto su GitHub).

## Cosa c'è
- Installatore in italiano con 4 livelli: Base, Base + Android, Base + Windows, Completo (Base preselezionato).
- SoStore: negozio di programmi nostro, con assistenti online (Claude, ChatGPT, Gemini, Copilot, DeepSeek, Le Chat, Perplexity), programmi Windows (Wine) e app Android (Waydroid). Per le app Android l'utente sceglie i permessi con una schermata nostra. KDE Connect è facoltativo, solo dallo store.
- Tema scuro e tema chiaro SofiOS: cambiano insieme sfondo, barre, menu, finestre e icone. Circa 600 icone disegnate da noi.
- Mascotte del faro come widget sulla scrivania, con una X per toglierla (si rimette da «Aggiungi widget»).
- App nostre: Cassaforte Password, Note, Assistenza (prepara una mail ad assistenza@), Informazioni su SofiOS (con «Componenti e licenze»), Benvenuto, aggiornamenti automatici.
- Tutto in italiano, anche il menu di avvio. Email: info@, assistenza@, privacy@ sul dominio dell'azienda. Sito: sofilabs.it.
- Nessun nome del sistema sotto (KDE, Plasma, Debian, Breeze, Dolphin…) visibile all'utente: pagine delle Impostazioni nascoste, avvisi, scorciatoie, accesso, terminale, widget e titoli delle finestre sono con nomi nostri.

## Come è stato provato
- Prova automatica in una macchina virtuale con oltre 170 foto vere (installatore, Windows, Android, temi, mascotte, nomi) e controllo del testo nelle foto.
- Collaudo del sistema acceso: 0 problemi (nessun servizio in errore, nessun crash).
- **Non provato** su un computer vero (audio, risoluzione, Wi-Fi), né l'installazione accanto a Windows, né il Secure Boot.

## Problemi noti
- Le anteprime dei widget Appunti, Barra delle attività e Avviatore mostrano ancora «www.kde.org» e «kde-stuff» dentro l'immagine (si vede solo in «Aggiungi widget»; l'immagine non è in un file modificabile).
- Nel terminale, il comando `uname` mostra la versione del kernel con «deb13» (non cambiabile).
- Gli autori dei widget («La squadra di Plasma») restano nei dettagli dei widget e nei Crediti per obbligo di licenza.

## Ecosistema (decisioni prese)
- Telefono: Android come base, sui telefoni già in uso, con un pacchetto di app SofiOS e una schermata iniziale nostra (non un sistema nuovo).
- Tablet Intel/AMD e TV: usano lo stesso SofiOS del computer (ramo `tablet/adattamento-tocco`).
- Tablet e telefoni Android: usano l'app SofiOS Android (schermata iniziale, ramo `android/schermata-iniziale`), non un sistema Linux. Il Teclast T40HD non può avere Linux.
- Mascotte-assistente e scelta degli assistenti online: da fare sul PC; l'app Android la vorrà uguale (aspetto e testi), ma con i limiti di Android (chiudere app, installare/disinstallare in silenzio, volume, luminosità, cercare file ovunque).
- Comunicazione solo in casa, sulla stessa rete Wi-Fi, senza server. Motore di sincronizzazione: partire da programmi aperti già pronti.
- Da condividere (in ordine): password, note, file e foto, appunti.
- Vedi anche `docs/ECOSISTEMA.md` e `docs/PROMPT-ALTRE-CHAT.md`.

## Come si lavora
- Sempre in italiano e con parole semplici. Foto vere come anteprime. Nessuna modifica a `main` senza il permesso di Luca. Prima di cambiare un messaggio di sistema, chiedere.
- Strumenti nel progetto: costruzione ISO (`build-iso.yml`), prova con foto (`foto.yml`, `tools/foto-iso.py`), controlli (`tools/collaudo.py`), lettura del testo nelle foto (`tools/ocr_nomi.py`).

## Idee future
- Assistente a comandi semplici con la mascotte (apri, chiudi, disinstalla), con modello locale facoltativo.
- Sincronizzazione tra dispositivi (Cartella SofiOS), SofiOS Plus (idee a pagamento), anteprime widget da sistemare.

- Sofi (mascotte, faro di pietra di Nano Banana): clic = casella dei comandi; pose che cambiano con lo stato; ondeggia piano. Stile «un po' più Apple»: angoli +40% nelle app (fatto), dock di vetro e finestre (da fare). Icone originali degli assistenti: decisione di Luca, file da fornire.
