"""Fa seguire alle app di SofiOS il tema scelto dall'utente (argento e rosso, grigio scuro e rosso, bianco e oro).
Le app hanno colori scritti nel loro stile (blu notte e oro): qui i blu diventano grigi neutri, l'oro diventa il colore di
accento del tema (rosso o oro), e con i temi chiari luminosita' di sfondo, testo e bordi si invertono."""
import colorsys, re

_HEX = re.compile(r"#([0-9a-fA-F]{6})\b")

def _tema():
    """(tema chiaro?, colore di accento del tema)"""
    try:
        from PyQt6.QtWidgets import QApplication
        p = QApplication.palette(); h = p.highlight().color()
        return p.window().color().lightness() > 150, (h.red() / 255, h.green() / 255, h.blue() / 255)
    except Exception:
        return False, (0.77, 0.11, 0.18)

def _hls(h):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return colorsys.rgb_to_hls(r, g, b)

def _hex(hh, l, s):
    r, g, b = colorsys.hls_to_rgb(hh % 1.0, min(1, max(0, l)), min(1, max(0, s)))
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))

def _oro(h):                                          # l'oro dei pulsanti e dei titoli
    hh, l, s = _hls(h)
    return 0.07 <= hh <= 0.17 and s > 0.5 and 0.4 < l < 0.92

def _blu(h):                                          # i blu notte e azzurri dello stile originale
    hh, l, s = _hls(h)
    return 0.5 <= hh <= 0.72 and s > 0.2

def _accento_tema(h, chiaro, acc):
    """l'oro diventa l'accento del tema; le sfumature chiare (hover) restano piu' chiare"""
    _, l, _ = _hls(h)
    ah, al, as_ = colorsys.rgb_to_hls(*acc)
    nl = al + (0.1 if l > 0.78 else 0)
    if not chiaro: nl = max(nl, 0.6)                  # scritta su sfondo scuro: deve leggersi
    return _hex(ah, nl, as_)

def _neutro(h, chiaro):
    hh, l, s = _hls(h)
    if chiaro:
        l2 = 1 - l
        if l2 > 0.7: l2 = 0.86 + (l2 - 0.7) * 0.4
        l = min(0.97, max(0.10, l2))
    return _hex(hh, l, s * 0.06 if _blu(h) else s * 0.3 if chiaro else s)

def _blocco(b, chiaro, acc):
    for m in re.finditer(r"background(?:-color)?\s*:\s*#([0-9a-fA-F]{6})", b):
        h = m.group(1)
        if _oro(h):                                   # pulsante oro: diventa del colore del tema, con la scritta leggibile
            b = _HEX.sub(lambda x: _accento_tema(x.group(1), chiaro, acc) if _oro(x.group(1)) else x.group(0), b)
            _, al, _ = colorsys.rgb_to_hls(*acc)
            testo = "#ffffff" if al < 0.62 else "#1c1c1e"
            return re.sub(r"(?<![-\w])color\s*:\s*#[0-9a-fA-F]{6}", "color: " + testo, b)
        if _blu(h) and _hls(h)[2] > 0.4 and _hls(h)[1] > 0.3:            # pulsante blu: diventa grigio, la scritta bianca resta
            return _HEX.sub(lambda x: _neutro(x.group(1), False) if _blu(x.group(1)) else x.group(0), b)
    def per_colore(x):
        h = x.group(1)
        if _oro(h): return _accento_tema(h, chiaro, acc)
        return _neutro(h, chiaro) if (chiaro or _blu(h)) else x.group(0)
    return _HEX.sub(per_colore, b)

def adatta(stile):
    chiaro, acc = _tema()
    return "}".join(_blocco(b, chiaro, acc) for b in stile.split("}"))
