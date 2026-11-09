"""Cassaforte Password: ponte con il browser. Qui ci sono le regole (quali password si possono dare a quale sito)
e il percorso del canale locale; il collegamento con il programma e' in sofios-password, quello con Firefox in cassaforte-host."""
import os
from urllib.parse import urlparse

SOCKET = os.path.join(os.environ.get("XDG_RUNTIME_DIR") or "/tmp", "sofios-cassaforte.sock")
CONSENSO = os.path.expanduser("~/.config/sofios/cassaforte-browser")

def sito(u):
    """nome del sito (minuscolo, senza www.); vuoto se non valido"""
    u = (u or "").strip()
    if not u: return ""
    try:
        h = urlparse(u if "://" in u else "https://" + u).hostname or ""
    except ValueError:
        return ""
    h = h.lower().rstrip(".")
    return h[4:] if h.startswith("www.") else h

def sicuro(url):
    """le password si compilano solo su https (o sul computer stesso)"""
    try:
        p = urlparse(url or "")
    except ValueError:
        return False
    return p.scheme == "https" or (p.scheme == "http" and (p.hostname or "") in ("localhost", "127.0.0.1"))

def stesso_sito(pagina, voce):
    """la voce vale per la pagina se e' lo stesso sito o un suo sottodominio (mai il contrario, mai un sito simile)"""
    a, b = sito(pagina), sito(voce)
    return bool(a) and bool(b) and (a == b or a.endswith("." + b))

def voci_per(kp, url):
    cestino = getattr(kp, "recyclebin_group", None)
    return [e for e in kp.entries if (cestino is None or e.group != cestino) and e.url and stesso_sito(url, e.url)]

def _trova(kp, url, utente):
    return next((e for e in voci_per(kp, url) if (e.username or "") == (utente or "")), None)

def salva_voce(kp, r, scrivi=True):
    """'nuova' | 'aggiornata' | 'uguale'. Con scrivi=False controlla soltanto."""
    url, utente, pw = r.get("url", ""), r.get("utente", ""), r.get("password", "")
    e = _trova(kp, url, utente)
    if e is None:
        if scrivi:
            titolo = (r.get("titolo") or sito(url) or "Nuova password")[:80]
            kp.add_entry(kp.root_group, titolo, utente, pw, url=url.split("#")[0][:300])
        return "nuova"
    if (e.password or "") == pw: return "uguale"
    if scrivi:
        e.save_history(); e.password = pw
    return "aggiornata"

def rispondi(kp, r):
    """risposta a una richiesta del browser; kp e' la cassaforte aperta. Non passa mai password per 'cerca'."""
    op = r.get("op")
    url = r.get("url", "")
    if op == "cerca":
        return {"ok": True, "voci": [{"id": str(e.uuid), "titolo": e.title or "", "utente": e.username or ""} for e in voci_per(kp, url)]}
    if op == "compila":
        if not sicuro(url): return {"ok": False, "errore": "non_sicuro"}
        for e in voci_per(kp, url):
            if str(e.uuid) == r.get("id"):
                return {"ok": True, "utente": e.username or "", "password": e.password or ""}
        return {"ok": False, "errore": "non_trovata"}
    if op == "controlla":
        return {"ok": True, "stato": salva_voce(kp, r, scrivi=False)}
    return {"ok": False, "errore": "richiesta_sconosciuta"}
