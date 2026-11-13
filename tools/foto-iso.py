#!/usr/bin/env python3
"""Avvia la ISO in QEMU (UEFI) e salva schermate vere in una cartella.
Uso: foto-iso.py ISO CARTELLA [minuti_massimi]
Non e' un test: se qualcosa non va, salva comunque quello che ha visto e un file registro.txt."""
import os, sys, time, socket, subprocess, hashlib, glob, shutil

iso, out = sys.argv[1], sys.argv[2]
massimo = int(sys.argv[3]) if len(sys.argv) > 3 else 40
os.makedirs(out, exist_ok=True)
log = open(os.path.join(out, "registro.txt"), "w")
def L(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(s, flush=True); log.write(s + "\n"); log.flush()

codice = next((p for p in ["/usr/share/OVMF/OVMF_CODE_4M.fd", "/usr/share/OVMF/OVMF_CODE.fd",
                           "/usr/share/ovmf/OVMF.fd"] if os.path.exists(p)), None)
vars_src = next((p for p in ["/usr/share/OVMF/OVMF_VARS_4M.fd", "/usr/share/OVMF/OVMF_VARS.fd"] if os.path.exists(p)), None)
L("OVMF:", codice, vars_src, "kvm:", os.path.exists("/dev/kvm"))
subprocess.run(["qemu-img", "create", "-f", "qcow2", "/tmp/disco.qcow2", "30G"], check=True, capture_output=True)
subprocess.run(["qemu-img", "create", "-f", "qcow2", "/tmp/disco2.qcow2", "20G"], check=True, capture_output=True)   # secondo disco: solo per le prove di Android
cmd = ["qemu-system-x86_64", "-machine", "q35,accel=kvm:tcg", "-cpu", "max", "-smp", "2", "-m", "4096",
       "-cdrom", iso, "-boot", "d", "-vga", "std", "-display", "none", "-no-reboot",
       "-drive", "file=/tmp/disco.qcow2,if=virtio,format=qcow2", "-drive", "file=/tmp/disco2.qcow2,if=virtio,format=qcow2",
       "-device", "qemu-xhci", "-device", "usb-kbd", "-device", "usb-tablet",
       "-netdev", "user,id=n0", "-device", "virtio-net-pci,netdev=n0",
       "-monitor", "unix:/tmp/qmon,server,nowait", "-qmp", "unix:/tmp/qmp,server,nowait",
       "-serial", "file:" + os.path.join(out, "seriale.txt")]
if codice and vars_src:
    shutil.copy(vars_src, "/tmp/OVMF_VARS.fd")
    cmd += ["-drive", f"if=pflash,format=raw,readonly=on,file={codice}", "-drive", "if=pflash,format=raw,file=/tmp/OVMF_VARS.fd"]
elif codice:
    cmd += ["-bios", codice]
proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=open(os.path.join(out, "qemu-errori.txt"), "w"))
for _ in range(30):
    if os.path.exists("/tmp/qmon"): break
    time.sleep(1)
mon = socket.socket(socket.AF_UNIX); mon.connect("/tmp/qmon"); mon.settimeout(5)
def cmdmon(c):
    mon.sendall((c + "\n").encode()); time.sleep(0.4)
    try: mon.recv(65536)
    except Exception: pass
import json
qmp = None
try:
    for _ in range(15):
        if os.path.exists("/tmp/qmp"): break
        time.sleep(1)
    qmp = socket.socket(socket.AF_UNIX); qmp.connect("/tmp/qmp"); qmp.settimeout(5)
    qmp.recv(65536); qmp.sendall(b'{"execute":"qmp_capabilities"}\n'); time.sleep(0.3); qmp.recv(65536)
    L("QMP collegato (mouse assoluto)")
except Exception as e:
    L("QMP non disponibile:", repr(e)); qmp = None
def qmp_eventi(ev):
    qmp.sendall((json.dumps({"execute": "input-send-event", "arguments": {"events": ev}}) + "\n").encode()); time.sleep(0.3)
    try: qmp.recv(65536)
    except Exception: pass
cmdmon("")  # saluto
inizio = time.time(); n = 0; ultimo_hash = None; visti = set()

def foto(nome):
    """salva una schermata; restituisce True se e' diversa dalla precedente"""
    global n, ultimo_hash
    ppm = "/tmp/f.ppm"
    if os.path.exists(ppm): os.remove(ppm)
    cmdmon(f"screendump {ppm}")
    for _ in range(10):
        if os.path.exists(ppm) and os.path.getsize(ppm) > 1000: break
        time.sleep(0.5)
    if not os.path.exists(ppm): return False
    h = hashlib.md5(open(ppm, "rb").read()).hexdigest()
    nuova = h != ultimo_hash; ultimo_hash = h
    if h not in visti:
        visti.add(h); n += 1
        png = os.path.join(out, f"{n:03d}-{int(time.time()-inizio):04d}s-{nome}.png")
        subprocess.run(["convert", ppm, png], check=False)
        L("foto", os.path.basename(png))
    return nuova

def clic(x, y, w=1280, h=800):
    """clic con il mouse assoluto (tavoletta USB) tramite QMP: 'mouse_move' di HMP e' solo relativo e con la tavoletta non muove nulla"""
    if qmp is None: return
    ax = int(x * 32767 / w); ay = int(y * 32767 / h)
    qmp_eventi([{"type": "abs", "data": {"axis": "x", "value": ax}}, {"type": "abs", "data": {"axis": "y", "value": ay}}]); time.sleep(0.6)
    qmp_eventi([{"type": "btn", "data": {"down": True, "button": "left"}}]); time.sleep(0.2)
    qmp_eventi([{"type": "btn", "data": {"down": False, "button": "left"}}]); time.sleep(0.8)
def tasti(*k):
    for t in k:
        cmdmon(f"sendkey {t}"); time.sleep(0.3)
# tastiera ITALIANA nella macchina di prova: i tasti hanno nomi della tastiera americana
SPECIALI = {"-": "slash", "_": "shift-slash", ".": "dot", ":": "shift-dot", "/": "shift-7", "=": "shift-0", "'": "minus", ",": "comma"}
def scrivi(testo):
    for c in testo:
        if c == " ": tasti("spc")
        elif c.isupper(): tasti("shift-" + c.lower())
        elif c in SPECIALI: tasti(SPECIALI[c])
        else: tasti(c)
def aspetta(sec, nome, ogni=15):
    fine = time.time() + sec
    while time.time() < fine and proc.poll() is None:
        foto(nome); time.sleep(ogni)

def aspetta_serie(testo, sec, nome, ogni=120):
    """aspetta che nella porta seriale compaia `testo` (es. fine dello scaricamento di Android)"""
    fine = time.time() + sec
    while time.time() < fine and proc.poll() is None:
        try:
            if testo in open(os.path.join(out, "seriale.txt"), errors="ignore").read(): return True
        except OSError: pass
        foto(nome); time.sleep(ogni)
    return False

try:
    L("attendo il menu di avvio")
    aspetta(30, "avvio", 10)
    tasti("ret")          # avvia la voce predefinita se il menu aspetta
    L("avvio premuto, attendo il caricamento")
    aspetta(60, "caricamento", 10)
    L("desktop appena avviato")
    t0 = time.time()
    while time.time() - t0 < 330 and proc.poll() is None:   # prima del blocco schermo (5 minuti)
        foto("desktop"); time.sleep(20)
    L("provo a sbloccare con la password della prova (live)")
    tasti("shift"); time.sleep(4)     # il primo tasto sveglia la schermata di blocco, se c'e'
    scrivi("live"); tasti("ret"); time.sleep(8)
    aspetta(60, "sbloccato", 12)
    L("chiudo il benvenuto e apro l'installer")
    tasti("alt-f4"); time.sleep(4); foto("dopo-benvenuto")
    for app_nome in ("Mail", "Cassaforte", "Note", "Browser"):     # i programmi nuovi, aperti dal menu veloce
        tasti("alt-f2"); time.sleep(3); scrivi(app_nome); time.sleep(4); tasti("ret")
        aspetta(40 if app_nome in ("Mail", "Browser") else 15, "app-" + app_nome.lower(), 8)
        tasti("alt-f4"); time.sleep(4)
        if app_nome in ("Mail", "Browser"):   # hanno finestre in piu' (benvenuto di Mail): chiusura sicura
            tasti("alt-f2"); time.sleep(3); scrivi("pkill -f " + ("thunderbird" if app_nome == "Mail" else "firefox")); time.sleep(2); tasti("ret"); time.sleep(4)
    # altre schermate del sistema: ognuna provata da sola (se una fallisce si va avanti)
    def schermata(nome, comando, attesa, chiudi="alt-f4"):
        try:
            L("schermata:", nome)
            tasti("alt-f2"); time.sleep(3); scrivi(comando); time.sleep(3); tasti("ret")
            time.sleep(attesa); foto(nome); time.sleep(1); foto(nome + "-b")
            if chiudi: tasti(chiudi); time.sleep(3)
        except Exception as e:
            L("errore nella schermata", nome, repr(e))
    schermata("accesso-sddm", "sddm-greeter-qt6 --test-mode --theme /usr/share/sddm/themes/sofios", 12)
    schermata("info-sistema", "Informazioni su SofiOS", 15)
    schermata("impostazioni", "Impostazioni", 20)
    schermata("utenti", "systemsettings kcm_users", 15)
    schermata("file", "File", 15)
    schermata("sostore", "SoStore", 25)
    try:
        L("collaudo automatico nel sistema acceso")
        esegui_c = lambda c: (tasti("alt-f2"), time.sleep(3), scrivi(c), time.sleep(2), tasti("ret"))
        esegui_c("sofios-prova-store collaudo"); aspetta_serie("### collaudo-fine", 400, "collaudo", 60)
        esegui_c("sofios-prova-store collaudo-duro"); aspetta_serie("### collaudo-duro-fine", 700, "collaudo-duro", 60)
    except Exception as e:
        L("errore collaudo", repr(e))
    # --- prova vera di SoStore nella ISO: Programmi Windows (Wine) e Android (Waydroid); i risultati escono dalla porta seriale
    def esegui(cmd):
        tasti("alt-f2"); time.sleep(3); scrivi(cmd); time.sleep(2); tasti("ret")
    def serie(nome):
        esegui("sofios-prova-store " + nome); time.sleep(10)
    try:
        L("prova Windows: Notepad++ con Wine")
        serie("kernel")
        esegui("sofios-prova-store windows")
        aspetta(780, "win-installazione", 30)
        serie("windows-log")
        esegui("sofios-prova-store windows-apri")
        aspetta(150, "win-aperto", 30)
        tasti("alt-f4"); time.sleep(3)
        esegui("pkill -f notepad"); time.sleep(3)
    except Exception as e:
        L("errore prova Windows", repr(e))
    try:
        L("prova Android: attivazione e avvio")
        esegui("sofios-prova-store android-attiva")
        L("Android pronto: %s" % aspetta_serie("Android pronto.", 4200, "android-attivazione", 150))
        serie("android-stato")
        esegui("sofios-prova-store android-avvio")
        aspetta(150, "android-avvio", 25)
        serie("android-stato")
        esegui("sofios-prova-store android-app")
        aspetta(900, "android-app", 45)
        serie("android-lista")
        esegui("sofios-prova-store android-apri")
        aspetta(60, "android-app-aperta", 20)
        esegui("sofios-prova-store android-lingua")
        aspetta(150, "android-lingua", 25)
        tasti("alt-f4"); time.sleep(3)        # chiude la finestra delle impostazioni di Android
    except Exception as e:
        L("errore prova Android", repr(e))
    try:
        L("schermata: menu")
        tasti("meta_l"); time.sleep(4); foto("menu-applicazioni")
        clic(60, 203); time.sleep(3); foto("menu-aiuto")          # categoria "Aiuto": cosa contiene?
        tasti("esc"); time.sleep(2)
    except Exception as e:
        L("errore nel menu", repr(e))
    try:
        L("schermata: blocco")
        tasti("alt-f2"); time.sleep(3); scrivi("loginctl lock-session"); time.sleep(3); tasti("ret")
        time.sleep(8); foto("blocco"); time.sleep(1)
        scrivi("live"); tasti("ret"); time.sleep(6); foto("dopo-blocco")
    except Exception as e:
        L("errore nel blocco", repr(e))
    # chiude cio' che fosse rimasto aperto, poi apre l'installer con il nome completo
    for prog in ("plasma-discover", "firefox", "systemsettings", "dolphin"):
        tasti("alt-f2"); time.sleep(3); scrivi("pkill -f " + prog); time.sleep(2); tasti("ret"); time.sleep(3)
    tasti("alt-f2"); time.sleep(3); scrivi("Installa SofiOS"); time.sleep(4); foto("krunner")
    tasti("ret")
    aspetta(150, "installer", 15)
    # pagine dell'installer: si clicca "Avanti" (Alt+A e' condiviso con "Annulla"); non si preme mai "Installa"
    for pagina in range(1, 5):   # benvenuto, lingua, tastiera, livello di installazione
        time.sleep(6); foto(f"pagina{pagina}")
        clic(1020, 690); time.sleep(6)      # "Avanti"
    time.sleep(6); foto("partizioni")
    clic(376, 186)                       # "Cancella disco": mostra file system e opzioni, senza installare nulla
    time.sleep(5); foto("partizioni-cancella")
    clic(1020, 690); time.sleep(8); foto("utente")
except Exception as e:
    L("errore:", repr(e))
finally:
    L("fine")
    try: cmdmon("quit")
    except Exception: pass
    try: proc.wait(timeout=20)
    except Exception: proc.kill()
    log.close()
