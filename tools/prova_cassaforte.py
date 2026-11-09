#!/usr/bin/python3
"""Prova vera della Cassaforte Password con Firefox: compilazione, sito diverso (nessuna password), salvataggio nuova password,
cassaforte chiusa. Si lancia nel servizio online (vedi .github/workflows/cassaforte.yml)."""
import os, sys, time, subprocess, traceback
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from pykeepass import PyKeePass

OUT = "/tmp/out"; os.makedirs(OUT, exist_ok=True)
FILE = os.path.expanduser("~/Password/cassaforte.kdbx"); PW = "prova-password-1"
risultati = []
def esito(nome, ok, dettaglio=""):
    risultati.append((nome, ok)); print(("OK    " if ok else "ERRORE"), nome, dettaglio, flush=True)

def avvia_app():
    amb = dict(os.environ, QT_QPA_PLATFORM="offscreen", SOFIOS_PASSWORD_FILE=FILE, SOFIOS_PROVA_SBLOCCA=PW)
    return subprocess.Popen(["python3", "/usr/local/bin/sofios-password"], env=amb, stdout=open(OUT + "/app.txt", "a"), stderr=subprocess.STDOUT)

def main():
    app = avvia_app(); time.sleep(4)
    o = Options(); o.add_argument("-headless"); o.binary_location = "/usr/bin/firefox-esr"
    o.set_preference("xpinstall.signatures.required", False)
    d = webdriver.Firefox(options=o, service=Service("/usr/local/bin/geckodriver", log_output=OUT + "/gecko.txt"))
    try:
        d.install_addon("/tmp/cassaforte.xpi", temporary=True); time.sleep(2)
        att = WebDriverWait(d, 20)
        # 1. compila
        d.get("http://localhost:8765/login.html")
        att.until(lambda x: x.find_elements(By.CSS_SELECTOR, "img.cassaforte-pulsante"))
        d.find_element(By.CSS_SELECTOR, "img.cassaforte-pulsante").click()
        att.until(lambda x: x.find_elements(By.CSS_SELECTOR, "#cassaforte-menu button"))
        testo = d.find_element(By.CSS_SELECTOR, "#cassaforte-menu").text
        d.save_screenshot(OUT + "/menu.png")
        esito("il menu mostra la voce del sito", "mario" in testo, repr(testo))
        d.find_element(By.CSS_SELECTOR, "#cassaforte-menu button").click(); time.sleep(1)
        u = d.find_element(By.ID, "utente").get_attribute("value"); p = d.find_element(By.ID, "pw").get_attribute("value")
        d.save_screenshot(OUT + "/compilato.png")
        esito("utente e password compilati", u == "mario" and p == "segreta123", u + "/" + ("*" * len(p)))
        # 2. sito diverso: nessuna password
        d.get("http://127.0.0.1:8765/login.html")
        att.until(lambda x: x.find_elements(By.CSS_SELECTOR, "img.cassaforte-pulsante"))
        d.find_element(By.CSS_SELECTOR, "img.cassaforte-pulsante").click(); time.sleep(3)
        t2 = d.find_element(By.CSS_SELECTOR, "#cassaforte-menu").text
        esito("su un sito diverso non offre password", "Nessuna password" in t2 and "mario" not in t2, repr(t2))
        # 3. proposta di salvataggio
        d.get("http://localhost:8765/login.html")
        att.until(lambda x: x.find_element(By.ID, "utente"))
        d.find_element(By.ID, "utente").send_keys("luigi"); d.find_element(By.ID, "pw").send_keys("nuova-pw-9")
        d.find_element(By.ID, "invia").click()
        att.until(lambda x: x.find_elements(By.ID, "cassaforte-proposta"))
        d.save_screenshot(OUT + "/proposta.png")
        esito("propone di salvare la nuova password", "luigi" in d.find_element(By.ID, "cassaforte-proposta").text)
        d.find_element(By.CSS_SELECTOR, "#cassaforte-proposta button").click(); time.sleep(3)
        kp = PyKeePass(FILE, password=PW)
        salvata = [e for e in kp.entries if e.username == "luigi" and e.password == "nuova-pw-9"]
        esito("la nuova password e' nella cassaforte", len(salvata) == 1)
        # 3b. stessa password: non la richiede
        d.get("http://localhost:8765/login.html"); att.until(lambda x: x.find_element(By.ID, "utente"))
        d.find_element(By.ID, "utente").send_keys("luigi"); d.find_element(By.ID, "pw").send_keys("nuova-pw-9"); d.find_element(By.ID, "invia").click()
        time.sleep(6)
        esito("non richiede una password gia' salvata", not d.find_elements(By.ID, "cassaforte-proposta"))
        # 4. cassaforte spenta
        app.terminate(); app.wait(); time.sleep(1)
        d.get("http://localhost:8765/login.html"); att.until(lambda x: x.find_elements(By.CSS_SELECTOR, "img.cassaforte-pulsante"))
        d.find_element(By.CSS_SELECTOR, "img.cassaforte-pulsante").click(); time.sleep(4)
        t4 = d.find_element(By.CSS_SELECTOR, "#cassaforte-menu").text
        d.save_screenshot(OUT + "/chiusa.png")
        esito("con la cassaforte chiusa lo dice e offre di aprirla", "chiusa" in t4 and "Apri Cassaforte" in t4, repr(t4))
    except Exception:
        traceback.print_exc(); esito("prova interrotta da un errore", False)
        try: d.save_screenshot(OUT + "/errore.png")
        except Exception: pass
    finally:
        d.quit()
        try: app.terminate()
        except Exception: pass
    print("RIEPILOGO:", sum(1 for _, ok in risultati if ok), "su", len(risultati))
    return 0 if all(ok for _, ok in risultati) else 1
if __name__ == "__main__": sys.exit(main())
