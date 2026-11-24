# SofiOS: ecosistema di dispositivi (documento di partenza)

Questo documento serve a chi comincia una nuova conversazione di lavoro (tablet, telefono, TV…): spiega dove siamo,
cosa è già stato deciso e come si lavora con Luca, il responsabile di Sofi Labs. Leggilo per intero prima di fare qualsiasi cosa.

## 1. L'idea

SofiOS è un sistema semplice, sicuro e in italiano. L'obiettivo è un **ecosistema**: ogni dispositivo SofiOS riconosce gli altri.
Esempi: una foto scattata dal telefono si trova sulla TV; un messaggio iniziato sul telefono si continua sul tablet;
le password, le note, i file e gli appunti sono gli stessi su tutti i dispositivi.

## 2. Decisioni già prese (da non rimettere in discussione senza motivo)

- **Computer (PC):** SofiOS è un sistema completo basato su Debian con desktop KDE Plasma, costruito con live-build. È il progetto di questo repository.
- **Tablet Intel/AMD e TV:** usano lo stesso SofiOS del computer (ramo `tablet/adattamento-tocco`; mini-PC collegato alla TV). Per la TV servirà più avanti un'interfaccia da telecomando.
- **Tablet e telefoni Android** (compreso il Teclast T40HD di Luca, che non può avere Linux: processore ARM, bootloader bloccato): usano l'**app SofiOS Android**, generica per qualsiasi tablet o telefono, che fa da schermata iniziale. Lavoro nel ramo `android/schermata-iniziale` (cartella `android/`). Il Teclast è solo il primo tablet di prova.
- **Telefono:** **Android come base**, sui **telefoni che le persone hanno già**. Prima versione: un pacchetto di app SofiOS (Cassaforte, Note, File…) più una schermata iniziale nostra, che si installano come qualsiasi app (Play Store o file scaricabile). Un sistema Android completo da installare al posto di quello del telefono è un'idea per dopo, solo per pochi modelli.
- **Comunicazione:** **solo in casa**, quando i dispositivi sono sulla stessa rete Wi-Fi. Si sincronizza tutto da soli, senza server. Niente servizio da remoto (per ora).
- **Motore di sincronizzazione:** partire da programmi aperti già pronti e provati (cartelle sincronizzate, formato aperto per le password), non da zero. Sopra ci mettiamo la nostra identità e le nostre schermate, in modo da poter cambiare il motore in futuro senza che l'utente se ne accorga.
- **Cosa va tenuto uguale su tutti i dispositivi (in ordine):** password, note, file e foto, appunti.
- **Nessun team:** Luca lavora con Claude. Claude scrive il codice e lo prova per quanto possibile nel cloud; Luca prova sul dispositivo vero e riferisce.

## 3. Idea tecnica di base

Quasi tutto si riduce a **file in una cartella uguale su tutti i dispositivi** («Cartella SofiOS»):
- note, file e foto sono già file;
- la Cassaforte password è un file cifrato in formato aperto (compatibile con le app esistenti), sincronizzato cifrato;
- gli appunti sono un piccolo messaggio in tempo reale tra i dispositivi collegati.

Da costruire come pezzi comuni (vedi sezione 6): identità del dispositivo, scoperta in rete, associazione tra dispositivi (con un codice), Cartella SofiOS, appunti condivisi.

## 4. Stato del computer (dove siamo)

- Repository: `asdrubale1234/sofios`. La versione per computer è su `main` (ISO `iso-20261123-1246`). Il lavoro nuovo si fa su un ramo di lavoro a parte: **`main` non si tocca senza il permesso di Luca.**
- ISO costruita da GitHub Actions (`build-iso.yml`); prova automatica in una macchina virtuale (`foto.yml`, `tools/foto-iso.py`) che scatta schermate vere; controlli statici (`tools/collaudo.py`); lettura del testo nelle foto per cercare nomi non nostri (`tools/ocr_nomi.py`).
- Il progetto ha già: installatore in italiano a livelli, SoStore (negozio nostro), supporto Windows (Wine) e Android (Waydroid), tema scuro e chiaro, mascotte come widget, app Assistenza (prepara una mail), Cassaforte Password, Note.

## 5. Regole di lavoro (molto importanti)

- **Tutto in italiano**, con parole semplici. Luca non è uno sviluppatore: spiega cosa fai e perché, senza gergo.
- **Sempre anteprime vere** (schermate reali, non immagini inventate) prima di considerare finito qualcosa. Foto veritiere, non ritoccate né scelte.
- **Non mettere nulla su `main`** e non rendere pubblico nulla senza permesso esplicito.
- **Prima di cambiare un messaggio di sistema o un testo non nostro, dillo a Luca** e aspetta il suo ok.
- **Nessun nome del sistema sottostante visibile all'utente** (KDE, Plasma, Debian, Breeze, Dolphin…). Dove la legge impone di citarli, vanno solo in «Componenti e licenze». I programmi di terzi (Firefox, Wine, Waydroid…) mantengono il loro nome.
- **Loghi altrui:** la regola era «niente marchi o loghi altrui». Luca ha deciso (24 novembre) di usare le **icone originali degli assistenti online** (Claude, ChatGPT, Gemini, Copilot, DeepSeek, Le Chat, Perplexity) al posto di quelle nostre. Ogni azienda ha le sue regole d'uso sui propri loghi e gli store sono severi: la decisione e la responsabilità sono di Luca. I file stanno in `docs/assets/assistenti/` (da fornire). Per tutto il resto le icone e le immagini restano nostre.
- **Onestà prima di tutto**: dire cosa è verificato e cosa no. Non promettere ciò che non si è provato.
- **Privacy**: nessuna statistica verso terzi; non scrivere mai nel progetto gli indirizzi personali di Luca.
- Stile grafico: blu notte `#0b2740`, oro `#ffd479`, la mascotte del faro, icone «riquadro colorato con simbolo bianco».
- **Stile «un po' più Apple»** (deciso da Luca, uguale su PC, tablet e telefono): colori invariati; angoli più morbidi (+40%: pulsanti ~14, schede ~18-20, finestre ~30, dock 32); dock «di vetro» (`#0b1f33` al 70%, filo bianco al 20%, niente sfocatura vera); icone del dock grandi (76 px, angolo ~24%) con il nome sotto; titoli grandi in grassetto; orologio grande e sottile; tocco leggero (95% in 90 ms); entrata dolce di pannelli (dissolvenza e 14 px in ~190 ms). Sul PC: le app di SofiOS hanno già gli angoli +40%; il dock e le finestre di Plasma sono da fare.
- **Sofi, la mascotte** (faro di pietra, 8 pose in `docs/assets/sofi/`): stati — apertura della casella = saluta (poi ascolta dopo 1,4 s); mentre si scrive = ascolta; capisce = pensa; lavora o cerca = concentrata; riuscito = felice; non capito, errore o permesso negato = preoccupata; informazione = parla; casella chiusa = neutra; dopo 3 s si torna ad ascolta. Dissolvenza di 250 ms tra le pose. Ondeggia piano: rotazione da −1,2° a +1,2° col perno ai piedi, 2,6 s per andata e ritorno. Piccola X per nasconderla. I comandi sono quelli di `mascotte_comandi.py`; se cambiano sul PC, il tablet va riallineato.
- Email dell'azienda: info@, assistenza@, privacy@ sul dominio dell'azienda.

## 6. Pezzi comuni da costruire (in questo ordine)

1. **Identità del dispositivo:** codice unico, nome, tipo (pc / tablet / telefono / tv) e chiavi, creati alla prima accensione.
2. **Nome del dispositivo** scelto dall'utente nell'installazione («PC di Luca»).
3. **Scoperta in rete:** i dispositivi SofiOS si annunciano sulla rete di casa.
4. **Associazione:** collegare due dispositivi con un codice o un QR, e ricordare di fidarsi di loro.
5. **Cartella SofiOS:** note, file, foto e password uguali tra due dispositivi, sincronizzati quando sono in casa.
6. **Appunti condivisi.**
7. Pagina «Dispositivi» nelle impostazioni, con le icone di telefono, tablet, TV e computer.

## 7. Come iniziare una nuova conversazione (per Luca)

Incolla questo come primo messaggio nella nuova conversazione:

> Lavoriamo su SofiOS, il progetto di Sofi Labs. Questa conversazione è per il **[tablet / telefono / TV]**. Prima di tutto leggi `docs/ECOSISTEMA.md` nel repository `asdrubale1234/sofios` (ramo `main`) e segui le regole che trovi. Poi dimmi in italiano cosa hai capito e da dove proponi di partire.


## 8. Cartella SofiOS e collegamento dei dispositivi (decisione di Luca, 24 novembre)
Luca vuole un ecosistema «come iCloud, senza server»: scrivo una nota o una password su un dispositivo e la ritrovo sugli altri; lo stesso per le foto. Si collega **una volta sola con un QR** e poi è automatico; sincronizzazione **solo sulla rete di casa** (Syncthing, nessun relay, nessun nostro server). Più avanti, se Sofi Labs vorrà, un account cloud (Sofi ID) con cifratura da un capo all'altro sopra gli stessi file.
Il progetto completo (cartelle, migrazione, regola di unione della cassaforte, pagina «Dispositivi», conflitti) è in `docs/DISPOSITIVI.md`.
