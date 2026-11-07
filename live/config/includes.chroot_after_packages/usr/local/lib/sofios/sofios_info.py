# Finestra "Informazioni" comune alle app di SofiOS (crediti).
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QKeySequence, QShortcut
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget

VERSIONE = "1.0"
import os
import json
def _crediti():
    base = {"azienda": "Sofi Labs", "anno": "2026", "email": "", "sito": ""}
    try:
        with open(os.environ.get("SOFIOS_CREDITI", "/usr/share/sofios/crediti.json")) as f: base.update(json.load(f))
    except Exception: pass
    return base
DATI_CREDITI = _crediti()
AZIENDA = DATI_CREDITI["azienda"]
CREDITI = "Sviluppato da " + AZIENDA
ANNO = DATI_CREDITI["anno"]
CONTATTI = "  ·  ".join(x for x in (DATI_CREDITI["sito"], DATI_CREDITI["email"]) if x)
LOGO = os.environ.get("SOFIOS_LOGO", "/usr/share/sofios/logo.png")

STILE = """
QDialog { background: #0b2740; }
QLabel { color: #e6f1ff; font-size: 13px; }
QLabel#nome { color: #ffffff; font-size: 22px; font-weight: 700; }
QLabel#sotto { color: #8fb3d4; font-size: 12px; }
QLabel#crediti { color: #ffd479; font-size: 14px; font-weight: 700; }
QWidget#scheda { background: #12365a; border-radius: 14px; }
QPushButton { background: #ffd479; color: #0b2740; border: none; border-radius: 10px; padding: 9px 22px; font-size: 13px; font-weight: 700; }
QPushButton:hover { background: #ffe19e; }
"""
STILE_BOTTONE = "QPushButton#info { background: transparent; color: #8fb3d4; font-weight: 600; padding: 6px 8px; } QPushButton#info:hover { color: #ffd479; }"

def mostra_informazioni(genitore, nome, descrizione="", logo=LOGO):
    d = QDialog(genitore); d.setWindowTitle("Informazioni su " + nome); d.setWindowIcon(QIcon(logo))
    d.setStyleSheet(STILE); d.setFixedWidth(380)
    v = QVBoxLayout(d); v.setContentsMargins(28, 26, 28, 24); v.setSpacing(6)
    i = QLabel(); i.setAlignment(Qt.AlignmentFlag.AlignCenter)
    i.setPixmap(QPixmap(logo).scaled(84, 84, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    v.addWidget(i)
    n = QLabel(nome); n.setObjectName("nome"); n.setAlignment(Qt.AlignmentFlag.AlignCenter); v.addWidget(n)
    s = QLabel("Parte di SofiOS · versione " + VERSIONE); s.setObjectName("sotto"); s.setAlignment(Qt.AlignmentFlag.AlignCenter); v.addWidget(s)
    if descrizione:
        t = QLabel(descrizione); t.setWordWrap(True); t.setAlignment(Qt.AlignmentFlag.AlignCenter); v.addSpacing(8); v.addWidget(t)
    v.addSpacing(12)
    sc = QWidget(); sc.setObjectName("scheda"); l = QVBoxLayout(sc); l.setContentsMargins(16, 14, 16, 14); l.setSpacing(2)
    c = QLabel(CREDITI); c.setObjectName("crediti"); c.setAlignment(Qt.AlignmentFlag.AlignCenter); l.addWidget(c)
    a = QLabel("© " + ANNO + " " + AZIENDA + " · Tutti i diritti riservati"); a.setObjectName("sotto"); a.setAlignment(Qt.AlignmentFlag.AlignCenter); l.addWidget(a)
    if CONTATTI:
        k = QLabel(CONTATTI); k.setObjectName("sotto"); k.setAlignment(Qt.AlignmentFlag.AlignCenter); k.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse); l.addWidget(k)
    v.addWidget(sc)
    v.addSpacing(10)
    b = QPushButton("Chiudi"); b.clicked.connect(d.accept); v.addWidget(b, alignment=Qt.AlignmentFlag.AlignCenter)
    d.exec()

def bottone_informazioni(finestra, nome, descrizione=""):
    """Bottone discreto 'Informazioni' (e tasto F1) da mettere nella finestra dell'app."""
    b = QPushButton("Informazioni"); b.setObjectName("info"); b.setFlat(True); b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setStyleSheet(STILE_BOTTONE)
    b.clicked.connect(lambda: mostra_informazioni(finestra, nome, descrizione))
    QShortcut(QKeySequence("F1"), finestra, activated=lambda: mostra_informazioni(finestra, nome, descrizione))
    return b
