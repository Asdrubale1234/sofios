#!/usr/bin/env python3
"""Installa la ISO su un disco virtuale (QEMU/UEFI) scegliendo un livello, con schermate vere.
Uso: installa-iso.py ISO CARTELLA MINUTI LIVELLO(base|android|windows|completo)
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
cmd = ["qemu-system-x86_64", "-machine", "q35,accel=kvm:tcg", "-cpu", "max", "-smp", "2", "-m", "4096",
       "-cdrom", iso, "-boot", "d", "-vga", "std", "-display", "none", "-no-reboot",
       "-drive", "file=/tmp/disco.qcow2,if=virtio,format=qcow2",
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
livello = sys.argv[4] if len(sys.argv) > 4 else "base"
def aspetta(sec, nome, ogni=15):
    fine = time.time() + sec
    while time.time() < fine and proc.poll() is None:
        foto(nome); time.sleep(ogni)
LIV = {"base": (365, 134), "android": (365, 149), "windows": (365, 164), "completo": (365, 179)}
try:
    aspetta(30, "avvio", 10); tasti("ret")
    aspetta(60, "caricamento", 10)
    aspetta(100, "desktop", 20)
    tasti("alt-f4"); time.sleep(4); foto("dopo-benvenuto")       # chiude il benvenuto
    tasti("alt-f2"); time.sleep(3); scrivi("Installa SofiOS"); time.sleep(4); tasti("ret")
    aspetta(150, "installer", 15)
    for pagina in range(1, 4):                 # benvenuto, posizione, tastiera
        time.sleep(5); foto(f"pagina{pagina}"); clic(1020, 690); time.sleep(6)
    time.sleep(5); foto("programmi")
    clic(*LIV[livello]); time.sleep(3); foto("programmi-" + livello)
    clic(1020, 690); time.sleep(8); foto("partizioni")
    clic(376, 186); time.sleep(4); foto("partizioni-cancella")
    clic(1020, 690); time.sleep(8); foto("utente")
    for (x, y, t) in ((430, 165, "Prova Uno"), (430, 278, "sofios-prova"), (430, 335, "ProvaSofios1!"), (636, 335, "ProvaSofios1!")):
        clic(x, y); time.sleep(1); scrivi(t); time.sleep(1)
    foto("utente-compilato")
    clic(1020, 690); time.sleep(8); foto("riepilogo")
    clic(1020, 690); time.sleep(4); foto("conferma")
    tasti("ret"); time.sleep(5); foto("avvio-installazione")
    aspetta(massimo * 60 - int(time.time() - inizio) - 120, "installazione", 60)
except Exception as e:
    L("errore:", repr(e))
finally:
    L("fine")
    try: cmdmon("quit")
    except Exception: pass
    try: proc.wait(timeout=30)
    except Exception: proc.kill()
    log.close()
