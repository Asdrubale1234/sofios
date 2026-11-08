"""SoStore - parte Windows: programmi Windows provati, installati con Wine dal sito ufficiale del produttore.
Il file si scarica solo da indirizzi https; se il produttore pubblica l'impronta sha256 (es. GitHub) viene controllata."""
import json, os, re, urllib.request

PREFIX = os.environ.get("WINEPREFIX", os.path.expanduser("~/.wine"))
CACHE = os.path.join(os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache")), "sofios-store", "windows")
AMBIENTE = {"WINEDLLOVERRIDES": "mscoree,mshtml=", "WINEDEBUG": "-all", "WINEPREFIX": PREFIX}   # niente richieste di Mono/Gecko

def percorso(win):
    """C:\\Program Files\\X\\y.exe -> percorso vero dentro il disco C: di Wine"""
    w = win.replace("\\", "/")
    if w[1:3].lower() == ":/": w = w[3:]
    return os.path.join(PREFIX, "drive_c", w)

def eseguibile(app):
    for c in app.get("eseguibile", []):
        if os.path.exists(percorso(c)): return c
    return None

def installato(app):
    return eseguibile(app) is not None

def risolvi(app):
    """(url, sha256 o None) del programma di installazione piu' recente"""
    if app.get("github"):
        req = urllib.request.Request("https://api.github.com/repos/%s/releases/latest" % app["github"], headers={"Accept": "application/vnd.github+json", "User-Agent": "SoStore"})
        with urllib.request.urlopen(req, timeout=30) as r: d = json.load(r)
        for a in d.get("assets", []):
            if re.fullmatch(app["file"], a["name"]):
                dg = a.get("digest") or ""
                return a["browser_download_url"], (dg.split(":", 1)[1] if dg.startswith("sha256:") else None)
        raise RuntimeError("file di installazione non trovato")
    return app["url"], app.get("sha256")
