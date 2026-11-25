"""Luma dentro i programmi: la posa giusta al posto giusto (le stesse immagini del widget sul desktop)."""
import os, json
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel

ALTEZZA = 140      # Luma ha la stessa altezza in tutti i programmi (tranne il Benvenuto)
CARTELLA = os.environ.get("SOFIOS_POSE", "/usr/share/plasma/plasmoids/org.sofios.mascotte/contents/images")

IMPOSTAZIONI = os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "sofios", "luma.json")

def attiva():
    """True se Luma si vede nelle pagine dei programmi (si cambia dalla casella di Luma)"""
    try: return bool(json.load(open(IMPOSTAZIONI)).get("programmi", True))
    except Exception: return True

def salva_attiva(v):
    try:
        os.makedirs(os.path.dirname(IMPOSTAZIONI), exist_ok=True)
        with open(IMPOSTAZIONI + ".tmp", "w") as f: json.dump({"programmi": bool(v)}, f)
        os.replace(IMPOSTAZIONI + ".tmp", IMPOSTAZIONI)
    except OSError: pass

def pixmap(nome, altezza):
    p = QPixmap(os.path.join(CARTELLA, "sofi-%s.png" % nome))
    if p.isNull(): p = QPixmap(os.path.join(CARTELLA, "sofi-neutra.png"))
    return p.scaledToHeight(altezza, Qt.TransformationMode.SmoothTransformation)

LISTA = []      # le Luma aperte in questo programma: si nascondono tutte insieme

def mostra_tutte(v):
    for e in LISTA:
        try: e.setVisible(bool(v))
        except RuntimeError: pass

def etichetta(nome, altezza=None):
    """un QLabel trasparente con la posa; luma.imposta(et, 'nome') la cambia"""
    e = QLabel(); e.setStyleSheet("background: transparent;"); e.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    e._altezza = altezza or ALTEZZA; imposta(e, nome); LISTA.append(e); return e

def imposta(e, nome):
    e.setPixmap(pixmap(nome, e._altezza)); e.setFixedSize(e.pixmap().size()); e.setAccessibleName("Luma, la mascotte")
    if not attiva(): e.hide()
