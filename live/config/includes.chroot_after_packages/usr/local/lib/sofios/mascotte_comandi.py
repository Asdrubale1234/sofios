"""Comandi semplici della mascotte SofiOS: capisce frasi come «apri il browser», «cerca fattura», «volume al 40».
Nessuna intelligenza artificiale e nessun invio all'esterno: sono regole sul testo. Qui c'e' solo la logica (provabile senza finestre)."""
import os, re, glob, time, shlex, shutil, subprocess, unicodedata

# ------------------------------------------------------------------ testo
def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]+", " ", t).strip()

ARTICOLI = {"il", "lo", "la", "i", "gli", "le", "un", "una", "uno", "l", "per", "favore", "piacere", "programma", "app", "applicazione", "mi", "ti",
            "che", "di", "del", "della", "dei", "delle", "al", "alla", "su", "in", "a", "da", "il", "poi", "ora", "adesso", "puoi", "potresti", "vorrei", "voglio"}

def parole_utili(t):
    return [p for p in norm(t).split() if p not in ARTICOLI]

# nome detto dalle persone -> nomi reali nel menu
SINONIMI = {
    "office": ["libreoffice", "writer", "calc", "impress"], "word": ["writer"], "excel": ["calc"], "powerpoint": ["impress"],
    "browser": ["firefox", "browser"], "internet": ["firefox", "browser"], "web": ["firefox", "browser"], "chrome": ["firefox", "browser"],
    "posta": ["thunderbird", "mail"], "email": ["thunderbird", "mail"], "mail": ["thunderbird", "mail"],
    "calcolatrice": ["kcalc", "calcolatrice"], "terminale": ["konsole", "terminale"], "note": ["note", "kwrite"],
    "file": ["file", "dolphin"], "cartelle": ["file", "dolphin"], "documenti": ["file", "dolphin"],
    "impostazioni": ["impostazioni", "systemsettings"], "settings": ["impostazioni", "systemsettings"],
    "foto": ["gwenview", "immagini"], "immagini": ["gwenview", "immagini"], "pdf": ["okular", "documenti"],
    "musica": ["vlc", "elisa", "lettore"], "video": ["vlc", "lettore"], "password": ["password", "cassaforte"], "cassaforte": ["cassaforte", "password"],
    "negozio": ["sostore"], "store": ["sostore"], "programmi": ["sostore"], "aggiornamenti": ["aggiorna"],
}

# ------------------------------------------------------------------ programmi installati
DIRECTORY_MENU = ("/usr/local/share/applications", "/usr/share/applications", os.path.expanduser("~/.local/share/applications"))

def _leggi_desktop(p):
    try: t = open(p, encoding="utf-8", errors="replace").read()
    except OSError: return None
    voce = {}; dentro = False
    for r in t.splitlines():
        r = r.strip()
        if r.startswith("["): dentro = (r == "[Desktop Entry]"); continue
        if dentro and "=" in r:
            k, v = r.split("=", 1); voce.setdefault(k.strip(), v.strip())
    if voce.get("Type") != "Application" or voce.get("NoDisplay", "").lower() == "true" or voce.get("Hidden", "").lower() == "true": return None
    if "Exec" not in voce: return None
    voce["_file"] = p
    voce["_nome"] = voce.get("Name[it]") or voce.get("Name") or os.path.basename(p)
    return voce

def programmi_installati(cartelle=DIRECTORY_MENU):
    """un elenco di voci del menu; i file in /usr/local (nostri) vincono su quelli di pacchetto"""
    visti = {}
    for d in cartelle:
        for p in sorted(glob.glob(os.path.join(d, "*.desktop"))):
            v = _leggi_desktop(p)
            visti[os.path.basename(p)] = v
    return [v for v in visti.values() if v]

def cerca_programmi(frase, voci):
    """voci del menu che corrispondono al nome detto; piu' alto = piu' sicuro"""
    parole = parole_utili(frase)
    if not parole: return []
    nomi = set(parole)
    for p in parole:
        for s in SINONIMI.get(p, []): nomi.add(s)
    ris = []
    for v in voci:
        n = norm(v["_nome"]); g = norm(v.get("GenericName", "")); k = norm(v.get("Keywords", "")); idf = norm(os.path.basename(v["_file"]).replace(".desktop", ""))
        punti = 0
        if n == " ".join(parole): punti = 100
        elif all(p in n.split() or p in idf.split() for p in parole): punti = 80
        elif all(p in n or p in idf for p in parole): punti = 60
        else:
            for c in nomi:
                if c == n: punti = max(punti, 70)
                elif c in n.split() or c in idf.split(): punti = max(punti, 55)
                elif len(c) > 3 and (c in n or c in idf): punti = max(punti, 40)
                elif len(c) > 3 and (c in g or c in k.split()): punti = max(punti, 25)
        if punti: ris.append((punti, v))
    ris.sort(key=lambda x: (-x[0], x[1]["_nome"].lower()))
    if not ris: return []
    migliore = ris[0][0]
    return [v for p, v in ris if p >= migliore - 10][:6]

def comando_da_exec(v):
    c = re.sub(r"%[a-zA-Z%]", "", v["Exec"]).strip()
    try: return shlex.split(c)
    except ValueError: return c.split()

def apri_programma(v):
    a = comando_da_exec(v)
    if not a: return False
    try:
        subprocess.Popen(a, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True,
                         cwd=os.path.expanduser("~"))
        return True
    except OSError: return False

def nome_processo(v):
    a = comando_da_exec(v)
    while a and (a[0] in ("env", "sh", "bash", "flatpak", "/usr/bin/env") or "=" in a[0]): a = a[1:]
    return os.path.basename(a[0])[:15] if a else None

def chiudi_programma(v):
    """chiede al programma di chiudersi (SIGTERM, con salvataggio se lo prevede). Ritorna True se c'era qualcosa da chiudere"""
    n = nome_processo(v)
    if not n: return False
    if subprocess.run(["pgrep", "-x", n], capture_output=True).returncode != 0: return False
    subprocess.run(["pkill", "-x", n]); return True

def pacchetto_di(v):
    try:
        r = subprocess.run(["dpkg-query", "-S", v["_file"]], capture_output=True, text=True, timeout=10)
        if r.returncode == 0: return r.stdout.split(":")[0].strip()
    except Exception: pass
    return None

# ------------------------------------------------------------------ cerca file
TIPI = {
    "foto": (".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".bmp", ".tif", ".tiff"), "immagini": (".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".bmp", ".svg"),
    "immagine": (".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".bmp", ".svg"),
    "musica": (".mp3", ".flac", ".ogg", ".wav", ".m4a", ".opus"), "canzoni": (".mp3", ".flac", ".ogg", ".wav", ".m4a", ".opus"),
    "video": (".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v"), "film": (".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v"),
    "pdf": (".pdf",), "documenti": (".pdf", ".doc", ".docx", ".odt", ".txt", ".rtf", ".xls", ".xlsx", ".ods", ".ppt", ".pptx", ".odp"),
    "documento": (".pdf", ".doc", ".docx", ".odt", ".txt", ".rtf", ".xls", ".xlsx", ".ods", ".ppt", ".pptx", ".odp"),
}
SALTA = {".cache", ".local", "node_modules", "proc", "sys", "dev", "__pycache__", ".git", ".mozilla", ".thunderbird", ".config", "lost+found", ".Trash"}
TIPI_RETE = ("cifs", "smb3", "smbfs", "nfs", "nfs4", "fuse.sshfs", "davfs", "fuse.rclone", "9p")

def radici_ricerca():
    """cartella personale, dischi e chiavette collegati, cartelle di rete gia' collegate"""
    r = [os.path.expanduser("~")]
    for g in ("/media/*", "/media/*/*", "/mnt/*", "/run/media/*/*", "/run/user/%d/gvfs/*" % os.getuid(), "/srv"):
        r += [p for p in glob.glob(g) if os.path.isdir(p)]
    try:
        for riga in open("/proc/mounts"):
            d = riga.split()
            if len(d) > 2 and d[2] in TIPI_RETE and os.path.isdir(d[1]): r.append(d[1])
    except OSError: pass
    visti = [];
    for p in r:
        rp = os.path.realpath(p)
        if not any(rp == v or rp.startswith(v + "/") for v in visti): visti.append(rp)
    return visti

def cerca_file(frase, radici=None, tempo=12, massimo=40):
    """nomi di file che contengono tutte le parole. «foto», «pdf»... limitano il tipo. Ritorna (elenco, finito_in_tempo)"""
    parole = parole_utili(frase)
    parole = [p for p in parole if p not in ("file", "cartella", "documento", "documenti", "cerca", "trova", "cercami", "trovami") or p in TIPI]
    estensioni = None; nomi = []
    for p in parole:
        if p in TIPI: estensioni = (estensioni or ()) + TIPI[p]
        else: nomi.append(p)
    if not nomi and not estensioni: return [], True
    fine = time.time() + tempo; trovati = []; in_tempo = True
    for rad in (radici or radici_ricerca()):
        for cur, dirs, files in os.walk(rad, onerror=lambda e: None):
            if time.time() > fine: in_tempo = False; break
            dirs[:] = [d for d in dirs if d not in SALTA and not d.startswith(".")]
            for f in files:
                nf = norm(f)
                if nomi and not all(p in nf for p in nomi): continue
                if estensioni and not f.lower().endswith(estensioni): continue
                trovati.append(os.path.join(cur, f))
                if len(trovati) >= massimo * 5: break
            if len(trovati) >= massimo * 5: break
        if not in_tempo or len(trovati) >= massimo * 5: break
    def chiave(p):
        try: return -os.path.getmtime(p)
        except OSError: return 0
    trovati.sort(key=chiave)
    return trovati[:massimo], in_tempo

# ------------------------------------------------------------------ volume, luminosita', tema
def _esegui(cmd):
    try: return subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    except Exception: return None

def volume(livello=None, delta=None, muto=None):
    """livello 0-100, delta in punti, muto True/False. Ritorna un testo, o None se non si puo'"""
    if shutil.which("wpctl"):
        s = "@DEFAULT_AUDIO_SINK@"
        if muto is not None: r = _esegui(["wpctl", "set-mute", s, "1" if muto else "0"])
        elif livello is not None: r = _esegui(["wpctl", "set-volume", s, "%.2f" % (max(0, min(100, livello)) / 100)])
        else: r = _esegui(["wpctl", "set-volume", "-l", "1.0", s, "%d%%%s" % (abs(delta), "+" if delta > 0 else "-")])
        if r and r.returncode == 0: return "Fatto."
    if shutil.which("pactl"):
        s = "@DEFAULT_SINK@"
        if muto is not None: r = _esegui(["pactl", "set-sink-mute", s, "1" if muto else "0"])
        elif livello is not None: r = _esegui(["pactl", "set-sink-volume", s, "%d%%" % max(0, min(100, livello))])
        else: r = _esegui(["pactl", "set-sink-volume", s, "%+d%%" % delta])
        if r and r.returncode == 0: return "Fatto."
    return None

BR = ["busctl", "--user", "call", "org.kde.Solid.PowerManagement", "/org/kde/Solid/PowerManagement/Actions/BrightnessControl", "org.kde.Solid.PowerManagement.Actions.BrightnessControl"]
def luminosita(livello=None, delta=None):
    """percentuale 0-100 o variazione; None se questo schermo non si regola"""
    m = _esegui(BR + ["brightnessMax"]); a = _esegui(BR + ["brightness"])
    try:
        massimo = int(m.stdout.split()[-1]); attuale = int(a.stdout.split()[-1])
    except Exception: return None
    if massimo <= 0: return None
    nuovo = round(massimo * livello / 100) if livello is not None else attuale + round(massimo * delta / 100)
    nuovo = max(1, min(massimo, nuovo))
    r = _esegui(BR + ["setBrightness", "i", str(nuovo)])
    return "Fatto." if r and r.returncode == 0 else None

def tema(chiaro):
    nomi = {"argento": "org.sofios.desktop", "scuro": "org.sofios.graphite", "oro": "org.sofios.gold"}
    r = _esegui(["plasma-apply-lookandfeel", "-a", nomi.get(chiaro if isinstance(chiaro, str) else ("chiaro" if chiaro else "scuro"), "org.sofios.desktop")])
    return "Fatto." if r and r.returncode == 0 else None

# ------------------------------------------------------------------ capire la frase
def _numero(t):
    m = re.search(r"(\d{1,3})", t)
    if m: return int(m.group(1))
    parole = {"zero": 0, "dieci": 10, "venti": 20, "trenta": 30, "quaranta": 40, "cinquanta": 50, "sessanta": 60, "settanta": 70, "ottanta": 80, "novanta": 90, "cento": 100, "massimo": 100, "meta": 50}
    for k, v in parole.items():
        if re.search(r"\b%s\b" % k, t): return v
    return None

def interpreta(frase):
    """(azione, argomento): apri / chiudi / disinstalla / installa / cerca-file / cerca-web / volume / luminosita / tema / schermata / aiuto / niente"""
    t = norm(frase)
    if not t: return ("niente", None)
    if re.search(r"\b(aiuto|cosa sai fare|cosa puoi fare|che cosa sai fare|comandi)\b", t): return ("aiuto", None)
    if re.search(r"\b(schermata|screenshot|cattura (lo )?schermo|foto (allo )?schermo)\b", t): return ("schermata", None)
    if re.search(r"\btema\b|\bmodalita (chiara|scura)\b|\bmetti (chiaro|scuro)\b", t) or re.search(r"\b(chiaro|scuro)\b", t) and re.search(r"\b(metti|passa|cambia|usa|attiva)\b", t):
        if re.search(r"\b(oro|dorat|bianc)", t): return ("tema", "oro")
        if re.search(r"\b(grigi|scur|antracite|nero)", t): return ("tema", "scuro")
        if re.search(r"\b(argent|ross|chiar)", t): return ("tema", "argento")
    if re.search(r"\bvolume\b|\baudio\b|\bsilenzio\b|\bmuto\b|\bmutal", t):
        if re.search(r"\b(togli|riattiva|riattivare) (il )?(muto|silenzio)\b|\bsmuta\b|\bnon muto\b", t): return ("volume", ("muto", False))
        if re.search(r"\b(muto|silenzio|zitto|muta|mutalo)\b", t): return ("volume", ("muto", True))
        n = _numero(t)
        if re.search(r"\b(alza|aumenta|piu forte|piu alto)\b", t): return ("volume", ("delta", n if n is not None and "%" in frase else 10))
        if re.search(r"\b(abbassa|diminuisci|riduci|piu basso|piano)\b", t): return ("volume", ("delta", -(n if n is not None and "%" in frase else 10)))
        if n is not None: return ("volume", ("livello", n))
    if re.search(r"\bluminosit|\bschermo (piu )?(chiaro|scuro|luminoso)|\billuminazione\b", t):
        n = _numero(t)
        if re.search(r"\b(alza|aumenta|piu luminos|piu chiaro)\b", t): return ("luminosita", ("delta", n if n is not None and "%" in frase else 10))
        if re.search(r"\b(abbassa|diminuisci|riduci|meno luminos|piu scuro)\b", t): return ("luminosita", ("delta", -(n if n is not None and "%" in frase else 10)))
        if n is not None: return ("luminosita", ("livello", n))
    m = re.match(r"(?:per favore |puoi |potresti |vorrei |voglio )*(?:cerca|cercami|trova|trovami|dove (?:e|sono)|dov e|dove si trova)\s+(?:su internet |in internet |sul web |online )(.+)", t)
    if m: return ("cerca-web", m.group(1))
    m = re.match(r"(?:per favore |puoi |potresti |vorrei |voglio |mi )*(?:cerca|cercami|trova|trovami|dove (?:e|sono)|dov e|dove si trova|cerca file|trova file)\s+(.+)", t)
    if m: return ("cerca-file", m.group(1))
    for verbo, azione in (("apri|aprimi|avvia|avviami|lancia|fai partire|mostrami|vai su|vai a", "apri"), ("chiudi|chiudimi|termina|ferma|spegni|esci da", "chiudi"),
                          ("disinstalla|disinstallami|rimuovi|togli|elimina|cancella", "disinstalla"), ("installa|installami|scarica|aggiungi", "installa")):
        m = re.match(r"(?:per favore |puoi |potresti |vorrei |voglio |mi |ti prego )*(?:%s)\s+(.+)" % verbo, t)
        if m: return (azione, m.group(1))
    return ("niente", None)

AIUTO = ("Posso fare queste cose:\n"
         "• apri / chiudi un programma: «apri il browser», «chiudi la posta»\n"
         "• installa / disinstalla un programma: «installa GIMP», «disinstalla Krita» (ti chiedo sempre conferma)\n"
         "• cercare file in tutto il PC, nei dischi collegati e nelle cartelle di rete: «cerca fattura», «cerca foto mare»\n"
         "• volume: «volume al 40», «alza il volume», «muto»\n"
         "• luminosità dello schermo: «luminosità 70», «abbassa la luminosità»\n"
         "• tema: «metti il tema scuro», «tema chiaro»\n"
         "• «fai una schermata»; «cerca su internet…» apre il browser")
