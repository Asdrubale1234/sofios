# Dispositivi e cartella SofiOS: come si collegano (progetto)

Scritto dalla chat del PC. Vale per PC, tablet e telefono. Stato: la **struttura delle cartelle e l'unione della cassaforte sono fatte sul PC**; la **pagina «Dispositivi» è solo progettata**.

## 1. La cartella SofiOS (uguale ovunque)
```
SofiOS/
  Note/       un file .txt per nota: nota-AAAAMMGG-HHMMSS.txt (titolo = prima riga non vuota); salvataggio atomico (.tmp poi rinomina)
  Password/   cassaforte.kdbx (KeePass KDBX4) e cassaforte.kdbx.bak
  Foto/       foto e video
  File/       file dell'utente; File/Schermate per le schermate
  .stignore   «*.tmp»: i file temporanei non si sincronizzano
```
- **Sul PC** sta in `~/SofiOS` (la cartella personale). Sul tablet in `/storage/emulated/0/SofiOS`.
- **Migrazione sul PC:** alla prima apertura di Note e di Cassaforte Password, le note di `~/Note` e la cassaforte di `~/Password` vengono **copiate** in `~/SofiOS`. Mai spostate, mai cancellate, mai sovrascritte, con un messaggio chiaro all'utente. Codice: `cartella_sofios.py`.

## 2. Come si sincronizza
- **Syncthing** (programma aperto, dati cifrati, nessun nostro server). Solo **rete di casa**: scoperta locale sì; scoperta globale, relay e attraversamento del router **no**.
- Sul PC Syncthing parte come servizio dell'utente, con la sua pagina web chiusa agli altri (solo `127.0.0.1`) e la chiave di accesso generata alla prima accensione. SofiOS lo guida e ne mostra lo stato; l'utente non vede mai Syncthing.
- **Foto:** il tablet invia la cartella della fotocamera (DCIM) in sola spedizione; sul PC arriva in `SofiOS/Foto` in sola ricezione. Così cancellare una foto sul PC non la toglie dal tablet, e viceversa non si perde niente. (Proposta, da confermare con Luca.)

## 3. Pagina «Dispositivi» (nelle impostazioni di SofiOS)
1. Elenco dei dispositivi collegati, con icona (computer, tablet, telefono, TV), nome («PC di Luca») e stato: *Collegato* · *Sincronizzo…* · *Non in casa*.
2. Bottone **«Collega un nuovo dispositivo»**: mostra un **QR** con il codice del PC e il suo nome, e il codice scritto per esteso sotto.
3. L'altro dispositivo scansiona il QR. Si approva **su entrambi** con un messaggio «Vuoi fidarti di *Tablet di Luca*?».
4. Alla prima volta SofiOS condivide la cartella SofiOS e, sul tablet, anche la fotocamera in sola spedizione.
5. Bottone «Rimuovi dispositivo» (non cancella i file).
Testi in italiano semplice. Mai nomi di Syncthing nell'interfaccia (solo in «Componenti e licenze»).

## 4. Conflitti
- **Note:** se due dispositivi modificano la stessa nota offline, Syncthing crea una copia «*.sync-conflict-*». La nota mostra «Ci sono due versioni di questa nota» con le due a confronto: l'utente sceglie, o le tiene tutte e due. Non si perde niente.
- **Cassaforte:** regola di unione scritta e provata (`cassaforte_unione.py`, prova in `tools/prova_unione.py`):
  1. si lavora per voce (UUID);
  2. una voce presente solo da una parte si aggiunge, a meno che l'altra non l'abbia eliminata dopo l'ultima modifica;
  3. se una voce c'è da entrambe vince l'**ultima modifica**, e la versione che perde finisce nella **cronologia** della voce;
  4. le voci eliminate restano eliminate (elenco DeletedObjects); una voce modificata dopo l'eliminazione torna in vita;
  5. nel dubbio si tiene;
  6. salvataggio con copia `.bak` e scrittura atomica.
- **Importante per chi scrive le app:** ad ogni modifica di una voce va aggiornata la data di modifica (`entry.touch(modify=True)`) e ad ogni eliminazione va registrata in DeletedObjects (`elimina_voce`). Altrimenti l'unione non può decidere chi vince. Il PC lo fa già.
- **Come collaudare insieme:** `python3 tools/prova_unione.py` (serve `pykeepass`). Il tablet deve implementare la stessa regola in Kotlin e confrontare il risultato con questo programma sugli stessi file: stesse voci, stesse password, stessa cronologia.

## 5. Da fare sul PC (in ordine)
1. Pagina «Dispositivi» con il QR (serve il pacchetto Syncthing nella ISO e il servizio dell'utente, spento finché non si collega il primo dispositivo).
2. Avviso «due versioni» nelle Note.
3. Unione automatica della cassaforte quando compare un file in conflitto.
4. Cartella Foto e foto del PC verso gli altri dispositivi, se Luca lo vorrà.
