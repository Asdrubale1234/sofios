"""Collegamento dei dispositivi e sincronizzazione della cartella SofiOS, sulla sola rete di casa.
Sotto c'e' Syncthing (programma aperto, dati cifrati, nessun server nostro): all'utente non compare mai il suo nome.
Impostazioni fisse: niente scoperta globale, niente relay, niente attraversamento del router, niente statistiche d'uso, niente aggiornamenti da soli."""
import json, os, re, subprocess, urllib.request, urllib.error, xml.etree.ElementTree as ET
import cartella_sofios as CS

CASA = os.environ.get("SOFIOS_SYNC_CASA", os.path.expanduser("~/.config/sofios/sincronizza"))
PORTA = os.environ.get("SOFIOS_SYNC_PORTA", "8385")
INDIRIZZO = "127.0.0.1:" + PORTA
NOME_FILE = os.path.expanduser("~/.config/sofios/dispositivo.json")
CESTINO_GIORNI = "30"
# gli identificatori delle cartelle devono essere uguali su tutti i dispositivi
CARTELLE = (("sofios-note", "Note", "Note"), ("sofios-password", "Password", "Password"), ("sofios-foto", "Foto", "Foto"), ("sofios-file", "File", "File"))

def nome_dispositivo():
    try: return json.load(open(NOME_FILE, encoding="utf-8"))["nome"]
    except Exception: return "PC di " + (os.environ.get("USER") or "casa").capitalize()

def salva_nome(nome):
    os.makedirs(os.path.dirname(NOME_FILE), exist_ok=True)
    json.dump({"nome": nome.strip()}, open(NOME_FILE, "w", encoding="utf-8"), ensure_ascii=False)

def _programma():
    return os.environ.get("SOFIOS_SYNC_BIN", "syncthing")

def prepara():
    """crea la configurazione la prima volta (chiavi, impostazioni di sola rete di casa, cartelle con cestino a 30 giorni)"""
    CS.prepara(); os.makedirs(CASA, mode=0o700, exist_ok=True)
    conf = os.path.join(CASA, "config.xml")
    if not os.path.exists(conf):
        subprocess.run([_programma(), "generate", "--home=" + CASA, "--no-default-folder"], capture_output=True, timeout=120, check=True)
    t = ET.parse(conf); r = t.getroot(); o = r.find("options"); g = r.find("gui")
    def imposta(nodo, nome, valore):
        x = nodo.find(nome)
        if x is None: x = ET.SubElement(nodo, nome)
        x.text = valore
    for k, v in (("globalAnnounceEnabled", "false"), ("relaysEnabled", "false"), ("natEnabled", "false"), ("localAnnounceEnabled", "true"),
                 ("urAccepted", "-1"), ("urSeen", "3"), ("autoUpgradeIntervalH", "0"), ("startBrowser", "false"), ("crashReportingEnabled", "false")):
        imposta(o, k, v)
    g.set("tls", "false"); imposta(g, "address", INDIRIZZO)
    mio = r.find("device").get("id")
    d0 = r.find("device"); d0.set("name", nome_dispositivo())
    for fid, nome, sotto in CARTELLE:
        f = next((x for x in r.findall("folder") if x.get("id") == fid), None)
        if f is None:
            f = ET.SubElement(r, "folder", {"id": fid, "label": nome, "path": os.path.join(CS.BASE, sotto), "type": "sendreceive", "fsWatcherEnabled": "true", "fsWatcherDelayS": "5"})
            ET.SubElement(f, "device", {"id": mio})
            v = ET.SubElement(f, "versioning", {"type": "trashcan"}); ET.SubElement(v, "param", {"key": "cleanoutDays", "val": CESTINO_GIORNI})
    ET.indent(t); t.write(conf, encoding="utf-8", xml_declaration=True); os.chmod(conf, 0o600)
    return mio

def _chiave():
    return ET.parse(os.path.join(CASA, "config.xml")).getroot().find("gui").findtext("apikey")

def _api(percorso, metodo="GET", corpo=None):
    rq = urllib.request.Request("http://%s/rest/%s" % (INDIRIZZO, percorso), method=metodo, headers={"X-API-Key": _chiave(), "Content-Type": "application/json"},
                                data=None if corpo is None else json.dumps(corpo).encode())
    with urllib.request.urlopen(rq, timeout=5) as r:
        t = r.read().decode(); return json.loads(t) if t.strip() else {}

def acceso():
    try: _api("system/ping"); return True
    except Exception: return False

def avvia():
    prepara()
    subprocess.run(["systemctl", "--user", "enable", "--now", "sofios-sincronizza.service"], capture_output=True)

def ferma():
    subprocess.run(["systemctl", "--user", "disable", "--now", "sofios-sincronizza.service"], capture_output=True)

def il_mio_codice():
    return ET.parse(os.path.join(CASA, "config.xml")).getroot().find("device").get("id")

def valido(codice):
    return bool(re.fullmatch(r"([A-Z2-7]{7}-){7}[A-Z2-7]{7}", (codice or "").strip().upper()))

def collegati():
    """[(codice, nome, stato)] stato: 'collegato' | 'non in casa'"""
    mio = il_mio_codice(); conf = _api("config/devices"); conn = _api("system/connections").get("connections", {})
    return [(d["deviceID"], d.get("name") or d["deviceID"][:7], "collegato" if conn.get(d["deviceID"], {}).get("connected") else "non in casa") for d in conf if d["deviceID"] != mio]

def in_attesa():
    """dispositivi che hanno chiesto di collegarsi e aspettano il tuo ok: [(codice, nome)]"""
    try: p = _api("cluster/pending/devices")
    except Exception: return []
    return [(k, (v or {}).get("name") or k[:7]) for k, v in p.items()]

def fidati(codice, nome):
    """approva un dispositivo e gli condivide le cartelle SofiOS"""
    codice = codice.strip().upper()
    _api("config/devices/" + codice, "PUT", {"deviceID": codice, "name": nome or codice[:7], "addresses": ["dynamic"], "autoAcceptFolders": False})
    for fid, _, _ in CARTELLE:
        f = _api("config/folders/" + fid)
        if not any(d["deviceID"] == codice for d in f["devices"]):
            f["devices"].append({"deviceID": codice, "introducedBy": "", "encryptionPassword": ""}); _api("config/folders/" + fid, "PUT", f)

def rimuovi(codice):
    for fid, _, _ in CARTELLE:
        f = _api("config/folders/" + fid); f["devices"] = [d for d in f["devices"] if d["deviceID"] != codice]; _api("config/folders/" + fid, "PUT", f)
    _api("config/devices/" + codice, "DELETE")

def sincronizzato():
    """percentuale media di completamento verso i dispositivi collegati, o None"""
    try:
        tot = []
        for cod, _, st in collegati():
            if st != "collegato": continue
            for fid, _, _ in CARTELLE: tot.append(_api("db/completion?device=%s&folder=%s" % (cod, fid)).get("completion", 100))
        return sum(tot) / len(tot) if tot else None
    except Exception: return None
