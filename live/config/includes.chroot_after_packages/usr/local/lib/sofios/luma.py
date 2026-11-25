"""Luma dentro i programmi: la posa giusta al posto giusto (le stesse immagini del widget sul desktop)."""
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel

CARTELLA = os.environ.get("SOFIOS_POSE", "/usr/share/plasma/plasmoids/org.sofios.mascotte/contents/images")

def pixmap(nome, altezza):
    p = QPixmap(os.path.join(CARTELLA, "sofi-%s.png" % nome))
    if p.isNull(): p = QPixmap(os.path.join(CARTELLA, "sofi-neutra.png"))
    return p.scaledToHeight(altezza, Qt.TransformationMode.SmoothTransformation)

def etichetta(nome, altezza=140):
    """un QLabel trasparente con la posa; luma.imposta(et, 'nome') la cambia"""
    e = QLabel(); e.setStyleSheet("background: transparent;"); e.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    e._altezza = altezza; imposta(e, nome); return e

def imposta(e, nome):
    e.setPixmap(pixmap(nome, e._altezza)); e.setFixedSize(e.pixmap().size()); e.setAccessibleName("Luma, la mascotte")
