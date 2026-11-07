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
cmd = ["qemu-system-x86_64", "-machine", "q35,accel=kvm:tcg", "-cpu", "max", "-smp", "2", "-m", "4096",
       "-cdrom", iso, "-boot", "d", "-vga", "std", "-display", "none", "-no-reboot",
       "-drive", "file=/tmp/disco.qcow2,if=virtio,format=qcow2",
       "-device", "qemu-xhci", "-device", "usb-kbd", "-device", "usb-tablet",
       "-netdev", "user,id=n0", "-device", "virtio-net-pci,netdev=n0",
       "-monitor", "unix:/tmp/qmon,server,nowait",
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

def tasti(*k):
    for t in k:
        cmdmon(f"sendkey {t}"); time.sleep(0.3)
def scrivi(testo):
    for c in testo:
        if c == " ": tasti("spc")
        elif c.isupper(): tasti("shift-" + c.lower())
        else: tasti(c)
def aspetta(sec, nome, ogni=15):
    fine = time.time() + sec
    while time.time() < fine and proc.poll() is None:
        foto(nome); time.sleep(ogni)

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
    tasti("alt-f2"); time.sleep(3); scrivi("Installa"); time.sleep(4); foto("krunner")
    tasti("ret")
    aspetta(150, "installer", 15)
    for pagina in range(1, 7):
        for t in ("alt-v", "ret", "alt-n"):
            tasti(t); time.sleep(8)
            if foto(f"pagina{pagina}"): break
        aspetta(10, f"pagina{pagina}", 5)
except Exception as e:
    L("errore:", repr(e))
finally:
    L("fine")
    try: cmdmon("quit")
    except Exception: pass
    try: proc.wait(timeout=20)
    except Exception: proc.kill()
    log.close()
