#!/usr/bin/env python3
"""Collaudo automatico statico di SofiOS: cerca errori senza bisogno di usare il sistema.
Uso: python3 tools/collaudo.py [rapporto.md]   (esce con codice 1 se trova problemi)"""
import os, re, sys, subprocess, py_compile, configparser, json, glob
import xml.dom.minidom as md
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I = f"{R}/live/config/includes.chroot_after_packages"
bug = []
def B(cat, msg): bug.append((cat, msg))
def rel(p): return os.path.relpath(p, R)
files = [os.path.join(d, f) for d, _, fs in os.walk(I) if "__pycache__" not in d for f in fs]
def testo(p):
    try: return open(p, encoding="utf-8").read()
    except Exception: return None

# 1 sintassi
for p in files:
    t = testo(p)
    if t is None: continue
    first = t.split("\n", 1)[0]
    if p.endswith(".py") or "python" in first:
        try: compile(t, p, "exec")
        except SyntaxError as e: B("Sintassi Python", f"{rel(p)} riga {e.lineno}: {e.msg}")
    elif p.endswith(".sh") or re.search(r"(ba)?sh\b", first) and first.startswith("#!"):
        r = subprocess.run(["bash", "-n", p], capture_output=True, text=True)
        if r.returncode: B("Sintassi shell", f"{rel(p)}: {r.stderr.strip()[:150]}")
        r = subprocess.run(["shellcheck", "-S", "error", "-s", "bash", p], capture_output=True, text=True)
        if r.returncode and "shellcheck" not in r.stderr:
            for m in re.findall(r"In .* line (\d+):\n(.*)\n.*\n(SC\d+.*)", r.stdout)[:3]:
                B("Errore shell (shellcheck)", f"{rel(p)} riga {m[0]}: {m[2][:120]}")
    elif p.endswith((".menu", ".xml", ".svg")):
        try: md.parse(p)
        except Exception as e: B("XML rotto", f"{rel(p)}: {e}")
    elif p.endswith(".json"):
        try: json.load(open(p))
        except Exception as e: B("JSON rotto", f"{rel(p)}: {e}")
    elif p.endswith((".desktop", ".conf")) and "calamares" not in p:
        pass
# 2 file .desktop
for p in files:
    if not p.endswith(".desktop") or "/themes/" in p: continue
    t = testo(p) or ""
    if "[Desktop Entry]" not in t: B("File .desktop", f"{rel(p)}: manca [Desktop Entry]"); continue
    cp = configparser.RawConfigParser(strict=False); cp.optionxform = str
    try: cp.read_string(t)
    except Exception as e: B("File .desktop", f"{rel(p)}: {e}"); continue
    de = cp["Desktop Entry"]
    for k in ("Name", "Exec", "Type"):
        if k not in de: B("File .desktop", f"{rel(p)}: manca {k}=")
    ex = de.get("Exec", "").split()
    if ex:
        c = ex[0]
        if c.startswith("/usr/local") and not os.path.exists(I + c): B("File .desktop", f"{rel(p)}: il comando {c} non esiste")
    ic = de.get("Icon", "")
    if ic.startswith("/") and not os.path.exists(I + ic): B("File .desktop", f"{rel(p)}: icona {ic} mancante")
# 3 marchi vietati nelle parti che l'utente vede
vietati = re.compile(r"\b(Debian|KDE|Kubuntu|Calamares|Wine|Waydroid|LineageOS|Plasma)\b", re.I)
visibili = [p for p in files if re.search(r"(/usr/share/(applications|sofios)|/usr/local/bin/|/etc/calamares/(branding|modules)|\.desktop$|\.menu$)", p)]
for p in visibili:
    if "/themes/" in p: continue
    t = testo(p)
    if not t or p.endswith(".py") and "traduzioni" in p: continue
    for n, riga in enumerate(t.split("\n"), 1):
        s = riga.strip()
        if s.startswith("#") or "import " in s or "QProcess" in s: continue
        if re.search(r"(Name|Comment|GenericName|Keywords)(\[\w+\])?=", s) and vietati.search(s):
            B("Marchio visibile", f"{rel(p)}:{n}: {s[:110]}")
        if p.endswith(".py") or "sofios-" in os.path.basename(p):
            for m in re.findall(r'(?:QLabel|setText|setWindowTitle|QPushButton|setPlaceholderText)\(\s*f?"([^"]{3,})"', s):
                if vietati.search(m) and "waydroid" not in m.lower().split()[:0]:
                    B("Marchio visibile (testo finestra)", f"{rel(p)}:{n}: {m[:100]}")
# 4 percorsi citati che non esistono
pat = re.compile(r"/usr/(?:local/)?(?:lib|share|bin)/sofios[\w./-]*|/usr/local/(?:bin|lib/sofios)/[\w.-]+")
for p in files:
    t = testo(p)
    if not t: continue
    for m in set(pat.findall(t)):
        m = m.rstrip(".,)\"'")
        if "*" in m or "$" in m or m.endswith("/"): continue
        if not (os.path.exists(I + m) or os.path.exists(R + "/live/config" + m) or m.startswith("/usr/share/sofios/livelli") or "/var/" in m or m.endswith(".xpi")):
            B("Percorso inesistente", f"{rel(p)} cita {m}")
# 5 script non eseguibili
for p in files:
    if "/usr/local/bin/" in p or "/usr/local/lib/sofios/" in p:
        t = testo(p) or ""
        if t.startswith("#!") and not os.access(p, os.X_OK): B("Permessi", f"{rel(p)} non è eseguibile")
# 6 hook e liste pacchetti
for h in glob.glob(f"{R}/live/config/hooks/live/*"):
    if not os.access(h, os.X_OK): B("Permessi", f"{rel(h)} non è eseguibile (live-build lo salta)")
pk = set()
for l in open(f"{R}/live/config/package-lists/sofios.list.chroot"):
    l = l.strip()
    if l and not l.startswith("#"):
        if l in pk: B("Pacchetti", f"'{l}' compare due volte nella lista")
        pk.add(l)
# 7 Calamares: moduli citati in settings esistono, livelli coerenti
cal = f"{I}/etc/calamares"
if os.path.exists(f"{cal}/settings.conf"):
    for m in re.findall(r"^\s*-\s*(?:exec|show)?\s*(\w+)", testo(f"{cal}/settings.conf"), re.M): pass
lv = testo(f"{cal}/modules/livelli.conf") or ""
for i in re.findall(r"^\s*-\s*id:\s*(\w+)", lv, re.M):
    if not os.path.exists(f"{I}/usr/share/sofios/livelli/{i}.png") and not os.path.exists(f"{R}/tools/crea_livelli.py"): B("Livelli", f"manca immagine livello {i}")
    if f"packagechooser_livelli" in (testo(f"{cal}/modules/contextualprocess.conf") or "") and f"{i}:" not in testo(f"{cal}/modules/contextualprocess.conf"):
        B("Livelli", f"contextualprocess non gestisce il livello '{i}'")
# 8 flussi di lavoro GitHub
for w in glob.glob(f"{R}/.github/workflows/*.yml"):
    t = testo(w)
    try:
        import yaml; yaml.safe_load(t)
    except ImportError: pass
    except Exception as e: B("Workflow", f"{rel(w)}: YAML rotto {e}")
    if "\t" in t: B("Workflow", f"{rel(w)}: contiene tabulazioni")
# 9 traduzioni: frasi inglesi sfuggite nelle finestre
for p in files:
    if p.endswith(".py") or "/bin/sofios-" in p:
        t = testo(p) or ""
        for n, riga in enumerate(t.split("\n"), 1):
            for m in re.findall(r'(?:QLabel|setText|setWindowTitle|QPushButton)\(\s*f?"([^"]{6,})"', riga):
                if re.match(r"^(Click|Please|Error|Loading|Install|Cancel|Open|Failed|Success|Warning|Press)\b", m):
                    B("Testo in inglese", f"{rel(p)}:{n}: {m[:80]}")
# rapporto
out = [f"# Collaudo automatico SofiOS\n", f"Problemi trovati: **{len(bug)}**\n"]
cat = {}
for c, m in bug: cat.setdefault(c, []).append(m)
for c, ms in sorted(cat.items()):
    out.append(f"\n## {c} ({len(ms)})")
    out += [f"- {m}" for m in ms]
txt = "\n".join(out)
print(txt)
if len(sys.argv) > 1: open(sys.argv[1], "w").write(txt + "\n")
sys.exit(1 if bug else 0)
