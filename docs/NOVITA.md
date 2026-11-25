# Novità dopo un aggiornamento

Dopo un aggiornamento, al **primo accesso** compare una schermata con cosa c'è di nuovo. Si vede **una volta sola** per ogni aggiornamento.

## Come funziona
- L'aggiornamento (pacchetto firmato) porta con sé il file `files/usr/share/sofios/novita/NUMERO.json`, dove `NUMERO` è lo stesso della `VERSIONE` dell'aggiornamento. Il percorso è già tra quelli consentiti dal programma di aggiornamento.
- Al login parte `sofios-novita` (avvio automatico). Legge la versione in `/etc/sofios/versione` e quella già vista in `~/.config/sofios/novita-vista`.
- Se la versione è più nuova e il file esiste, mostra la schermata. Chiuderla con «Ho capito» **o con la X** vale come visto: non riappare.
- Se si saltano degli aggiornamenti, si vedono tutte le novità arretrate, dalla più nuova.
- Prima installazione: niente schermata (c'è già il Benvenuto). Dalla chiavetta (live): niente.
- Si può rivedere quando si vuole: menu → «Novità di SofiOS», oppure scrivere «novità» a Luma.

## Come si scrive una novità (file `NUMERO.json`)
```json
{
  "versione": 3,
  "titolo": "Novità di SofiOS",
  "sottotitolo": "Ecco cosa è cambiato con questo aggiornamento.",
  "pose": "festa",
  "voci": [
    {"titolo": "Titolo breve", "testo": "Una o due frasi in parole semplici."}
  ]
}
```
`pose` è una delle pose di Luma (festa, fatto, saluta…). Tienile 3 o 4 voci: chi legge ha fretta.

## Tablet
Stessa idea nell'app: al primo avvio dopo l'aggiornamento (nuovo `versionCode`) una schermata con le novità, una volta sola; il testo arriva da un file dentro l'app.
