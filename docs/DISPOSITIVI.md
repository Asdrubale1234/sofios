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
- **Foto: tutto sincronizzato in tutte e due le direzioni, come iCloud Foto** (decisione di Luca). Una foto scattata sul tablet arriva sul PC e viceversa; se la **elimini su un dispositivo si elimina ovunque**. Sul tablet la cartella della fotocamera (DCIM) è collegata a `SofiOS/Foto` del PC.
- **Rete di sicurezza proposta:** in tutte le cartelle si attiva il **cestino a tempo** di Syncthing (le copie eliminate restano 30 giorni in una cartella nascosta e si possono recuperare), così un'eliminazione per errore non è per sempre. Sul tablet l'eliminazione di un file della fotocamera chiede il permesso di Android (limite del sistema).

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

## 5. Fatto sul PC e da fare
**Fatto (24 novembre):** programma «Dispositivi» (`sofios-dispositivi`) con QR, elenco, approvazione, rimozione; libreria `dispositivi.py`; servizio dell'utente `sofios-sincronizza.service` (si accende alla prima apertura di «Dispositivi»); Syncthing e `python3-qrcode` nella ISO. Provato con due istanze sulla stessa macchina: le note e le foto arrivano da una parte all'altra, un'eliminazione passa all'altra e la copia resta nel cestino a 30 giorni.
**Identificatori delle cartelle (uguali su tutti i dispositivi):** `sofios-note` (Note), `sofios-password` (Password), `sofios-foto` (Foto), `sofios-file` (File). Il PC le condivide con ogni dispositivo che approva. Sul tablet vanno create con gli stessi identificatori (la fotocamera DCIM = `sofios-foto`).
**Impostazioni fisse:** scoperta globale, relay, attraversamento del router, statistiche d'uso e aggiornamenti da soli sono spenti. La pagina web interna ascolta solo su `127.0.0.1:8385`.
**QR:** contiene il codice del dispositivo (il codice Syncthing di 56 caratteri); l'app del tablet può leggerlo direttamente.

**Fatto dopo il confronto con la chat del tablet (24 novembre):**
- `.stignore` ora ignora anche `.conflitti` (come sul tablet).
- Cassaforte nuova: Argon2d 32 MiB, 4 passaggi, parallelismo 2 (`parametri_nuova()`), da usare uguale sul tablet per le casseforti nuove. Ogni dispositivo apre comunque le casseforti con altri parametri.
- Note: avviso «Ci sono due versioni di questa nota» con Tieni questa / Tieni l'altra / Tieni tutte e due; le risolte vanno in `Note/.conflitti`.
- Cassaforte: allo sblocco si uniscono da sole le copie `cassaforte.sync-conflict-*.kdbx` (copie unite in `Password/.conflitti`).
- Collegamento: il QR contiene **solo il codice di 56 caratteri**, in maiuscolo con i trattini, senza nome. Il nome viaggia con il collegamento. Sul tablet l'app Syncthing-Fork legge il QR da sola o accetta il codice incollato. SofiOS Android non deve avere un lettore di QR.

**Da fare, in ordine:**
1. (fatto, vedi sopra)
4. Foto sincronizzate in tutte e due le direzioni, con il cestino a 30 giorni.
