"""SoStore - parte Android: catalogo F-Droid (firmato) e Android sul computer (Waydroid).
Il catalogo index-v2.json e' verificato con la firma GPG di F-Droid (chiave inclusa in SofiOS);
ogni app scaricata e' verificata con il suo sha256 scritto nel catalogo."""
import hashlib, json, os, shutil, subprocess, time

REPO = "https://f-droid.org/repo"
CACHE = os.path.join(os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache")), "sofios-store", "android")
CHIAVE = os.environ.get("SOFIOS_FDROID_CHIAVE", "/usr/share/sofios/store/fdroid.gpg")
LINGUE = ("it", "it-IT", "en-US", "en")
ARCH_OK = {"x86_64", "x86"}          # Android sul computer: app senza codice nativo o con versione per PC

def testo(d):
    """campo tradotto del catalogo: italiano se c'e'"""
    if isinstance(d, str): return d
    if not isinstance(d, dict): return ""
    for l in LINGUE:
        if d.get(l): return d[l]
    return next(iter(d.values()), "") if d else ""

def firma_valida(json_path, asc_path, chiave=CHIAVE):
    """True se index-v2.json e' firmato da F-Droid (gpgv con la sola chiave di F-Droid)"""
    if not os.path.exists(chiave): return False
    try:
        r = subprocess.run(["gpgv", "--keyring", chiave, asc_path, json_path], capture_output=True, text=True, timeout=120)
        return r.returncode == 0
    except Exception:
        return False

class CatalogoAndroid:
    def __init__(self):
        self.app = []      # elenco pronto per la ricerca

    def file_catalogo(self):
        return os.path.join(CACHE, "index-v2.json")

    def da_aggiornare(self, ore=24):
        f = self.file_catalogo()
        return not os.path.exists(f) or time.time() - os.path.getmtime(f) > ore * 3600

    def carica(self):
        """legge il catalogo gia' scaricato e verificato"""
        f = self.file_catalogo()
        if not os.path.exists(f): return False
        with open(f, encoding="utf-8") as h: dati = json.load(h)
        out = []
        for pid, p in (dati.get("packages") or {}).items():
            m = p.get("metadata") or {}
            versioni = sorted((p.get("versions") or {}).values(), key=lambda v: (v.get("manifest") or {}).get("versionCode", 0), reverse=True)
            scelta = None
            for v in versioni:
                nat = set((v.get("manifest") or {}).get("nativecode") or [])
                if not nat or nat & ARCH_OK:
                    scelta = v; break
            if not scelta: continue
            icona = testo(m.get("icon") or {})
            out.append({
                "tipo": "android", "pacchetto": pid, "nome": testo(m.get("name")) or pid,
                "descrizione": testo(m.get("summary")), "lunga": testo(m.get("description")),
                "icona": (REPO + icona["name"]) if isinstance(icona, dict) and icona.get("name") else "",
                "apk": REPO + scelta["file"]["name"], "sha256": scelta["file"]["sha256"],
                "versione": (scelta.get("manifest") or {}).get("versionName", ""),
                "aggiornata": m.get("lastUpdated", 0),
            })
        out.sort(key=lambda a: -a["aggiornata"])
        self.app = out
        return True

    def cerca(self, q, massimo=60):
        q = q.lower().strip()
        if not q: return self.app[:massimo]
        res = [a for a in self.app if q in a["nome"].lower() or q in a["descrizione"].lower() or q in a["pacchetto"].lower()]
        res.sort(key=lambda a: (not a["nome"].lower().startswith(q), q not in a["nome"].lower()))
        return res[:massimo]

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

# ---- Android sul computer (Waydroid)
def waydroid_presente():
    return shutil.which("waydroid") is not None

def stato_waydroid():
    """'assente' | 'da_attivare' | 'pronto'  + tipo ('GAPPS'/'VANILLA'/'')"""
    if not waydroid_presente(): return "assente", ""
    cfg = "/var/lib/waydroid/waydroid.cfg"
    if not os.path.exists(cfg) or not os.path.exists("/var/lib/waydroid/images/system.img"):
        return "da_attivare", ""
    tipo = ""
    try:
        t = open(cfg, encoding="utf-8").read()
        tipo = "GAPPS" if "gapps" in t.lower() else "VANILLA"
    except OSError: pass
    return "pronto", tipo

def sessione_attiva():
    try:
        r = subprocess.run(["waydroid", "status"], capture_output=True, text=True, timeout=15)
        return "RUNNING" in r.stdout.upper()
    except Exception:
        return False
