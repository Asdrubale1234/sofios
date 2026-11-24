"""La cartella SofiOS: note, password, foto e file uguali su tutti i dispositivi (si sincronizza solo sulla rete di casa).
Struttura identica sul tablet (SofiOS/ nella memoria interna) e sul PC (SofiOS/ nella cartella personale):
  Note/      un file .txt (UTF-8) per nota, nome nota-AAAAMMGG-HHMMSS.txt
  Password/  cassaforte.kdbx (KeePass KDBX4) e cassaforte.kdbx.bak
  Foto/      foto e video
  File/      file dell'utente; File/Schermate per le schermate"""
import os, shutil

BASE = os.environ.get("SOFIOS_CARTELLA", os.path.expanduser("~/SofiOS"))
NOTE = os.environ.get("SOFIOS_NOTE", os.path.join(BASE, "Note"))
PASSWORD_FILE = os.environ.get("SOFIOS_PASSWORD_FILE", os.path.join(BASE, "Password", "cassaforte.kdbx"))
VECCHIE_NOTE = os.path.expanduser("~/Note")
VECCHIA_PASSWORD = os.path.expanduser("~/Password/cassaforte.kdbx")
STIGNORE = "// SofiOS: i file temporanei di salvataggio non si sincronizzano\n*.tmp\n"

def prepara():
    for sotto, modo in (("Note", 0o755), ("Password", 0o700), ("Foto", 0o755), ("File", 0o755), (os.path.join("File", "Schermate"), 0o755)):
        try: os.makedirs(os.path.join(BASE, sotto), mode=modo, exist_ok=True)
        except OSError: pass
    p = os.path.join(BASE, ".stignore")
    if not os.path.exists(p):
        try: open(p, "w", encoding="utf-8").write(STIGNORE)
        except OSError: pass

def migra():
    """COPIA le note e la cassaforte di prima dentro la cartella SofiOS. Non sposta e non cancella niente, e non sovrascrive mai.
    Ritorna un messaggio per l'utente se ha copiato qualcosa, altrimenti None."""
    prepara(); note = 0; cassaforte = False
    if not os.environ.get("SOFIOS_NOTE") and os.path.isdir(VECCHIE_NOTE) and os.path.realpath(VECCHIE_NOTE) != os.path.realpath(NOTE):
        for n in sorted(os.listdir(VECCHIE_NOTE)):
            src, dst = os.path.join(VECCHIE_NOTE, n), os.path.join(NOTE, n)
            if n.endswith(".txt") and os.path.isfile(src) and not os.path.exists(dst):
                try: shutil.copy2(src, dst); note += 1
                except OSError: pass
    if not os.environ.get("SOFIOS_PASSWORD_FILE") and os.path.isfile(VECCHIA_PASSWORD) and os.path.realpath(VECCHIA_PASSWORD) != os.path.realpath(PASSWORD_FILE) and not os.path.exists(PASSWORD_FILE):
        try:
            shutil.copy2(VECCHIA_PASSWORD, PASSWORD_FILE); os.chmod(PASSWORD_FILE, 0o600); cassaforte = True
            if os.path.isfile(VECCHIA_PASSWORD + ".bak") and not os.path.exists(PASSWORD_FILE + ".bak"): shutil.copy2(VECCHIA_PASSWORD + ".bak", PASSWORD_FILE + ".bak")
        except OSError: pass
    if not note and not cassaforte: return None
    parti = []
    if note: parti.append("%d %s" % (note, "nota" if note == 1 else "note"))
    if cassaforte: parti.append("la cassaforte delle password")
    return ("Ho copiato %s nella cartella SofiOS, che si sincronizza con i tuoi altri dispositivi. "
            "Gli originali sono rimasti dove erano: non ho spostato né cancellato niente." % " e ".join(parti))
