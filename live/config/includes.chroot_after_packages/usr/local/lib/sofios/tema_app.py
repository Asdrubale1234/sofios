"""Fa seguire alle app di SofiOS il tema chiaro/scuro scelto dall'utente.
Le app hanno colori scritti nel loro stile (blu notte e oro); con il tema chiaro i colori di sfondo, testo e bordi
si invertono di luminosità (restano gli accenti dorati e i pulsanti)."""
import colorsys, re

_HEX = re.compile(r"#([0-9a-fA-F]{6})\b")

def _chiaro():
    try:
        from PyQt6.QtWidgets import QApplication
        return QApplication.palette().window().color().lightness() > 150
    except Exception:
        return False

def _accento(h):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    _, l, s = colorsys.rgb_to_hls(r, g, b)
    return s > 0.6 and 0.4 < l < 0.82             # oro e azzurri vivi: restano uguali

def _inverti(m):
    h = m.group(1)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hh, l, s = colorsys.rgb_to_hls(r, g, b)
    if _accento(h):                                  # testo dorato su sfondo chiaro: lo scurisco per leggerlo
        r2, g2, b2 = colorsys.hls_to_rgb(hh, l * 0.55, s)
        return "#%02x%02x%02x" % (round(r2 * 255), round(g2 * 255), round(b2 * 255))
    l2 = 1 - l
    if l2 > 0.7: l2 = 0.86 + (l2 - 0.7) * 0.4
    l2 = min(0.97, max(0.10, l2)); s2 = s * 0.3
    r2, g2, b2 = colorsys.hls_to_rgb(hh, l2, s2)
    return "#%02x%02x%02x" % (round(r2 * 255), round(g2 * 255), round(b2 * 255))

def _blocco(b):
    # una regola con sfondo di accento (es. pulsante oro) resta com'è, testo compreso
    for m in re.finditer(r"background(?:-color)?\s*:\s*#([0-9a-fA-F]{6})", b):
        if _accento(m.group(1)): return b
    return _HEX.sub(_inverti, b)

def adatta(stile):
    if not _chiaro(): return stile
    return "}".join(_blocco(b) for b in stile.split("}"))
