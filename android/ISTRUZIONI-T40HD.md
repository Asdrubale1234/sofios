# Provare SofiOS sul T40HD (versione 0.1, di prova)

Il file è `android/apk/SofiOS-prova.apk`. È una versione di prova: serve a vedere come va sul tablet vero.

## 1. Installare
1. Porta il file sul tablet (mail a te stesso, cavo, cartella condivisa: come preferisci).
2. Sul tablet tocca il file. Se Android chiede di permettere l'installazione da questa fonte, tocca «Consenti».
3. Tocca «Installa», poi «Apri».

Se compare «App non installata perché in conflitto con un pacchetto esistente»: c'è già una versione di SofiOS
firmata con un'altra chiave. Disinstalla SofiOS (Impostazioni → App → SofiOS → Disinstalla) e installa di nuovo.
Con la chiave di prova fissa (da questa versione) gli aggiornamenti successivi si installano uno sopra l'altro.

## 2. Metterlo come schermata iniziale
1. Premi il tasto Home. Android chiede quale app di avvio usare.
2. Scegli **SofiOS** e tocca **«Sempre»**.
3. Se non chiede niente: Impostazioni → App → App predefinite → App Home → SofiOS.

## 3. Casa (Fully)
1. Tocca l'icona Casa (si vede solo se Fully è installato). Si apre Fully.
2. Da quel momento, dopo ogni accensione, Fully si apre da solo. Sull'icona c'è un puntino verde.
3. Per smettere: tieni premuta l'icona Casa. Il puntino sparisce.
4. Chiudendo Fully trovi SofiOS.
5. Se Fully mostra «Hmmm... Difficult case» (vuole essere lui la Home): tocca «Ignore». Per non vederlo più, nelle
   impostazioni di Fully, Modalità kiosk, spegni l'opzione che blocca il tasto Home («Disable Home Button»).

## 4. Tornare indietro
Impostazioni → App → App predefinite → App Home → scegli quella del Teclast. SofiOS si può disinstallare come qualsiasi app.

## 5. Elenco dei programmi (facoltativo, non cambia niente)
Serve per proporti cosa disattivare. Ogni scelta si potrà annullare.
1. Sul tablet: Impostazioni → Info sul tablet → tocca 7 volte «Numero build». Poi Opzioni sviluppatore → «Debug USB» acceso.
2. Sul Mac, nel Terminale: `brew install android-platform-tools` (solo la prima volta).
3. Collega il tablet con il cavo e tocca «Consenti» sul tablet.
4. Nel Terminale: `bash elenco-pacchetti.sh` (il file è in `android/tools/`).
5. Apri `elenco-tablet.txt` sulla Scrivania, copia il testo e incollalo nella chat.
