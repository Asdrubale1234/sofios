"""Fa seguire alle app di SofiOS il tema scelto (scuro o chiaro), nello stile «Apple» di SofiOS.
Le app hanno colori scritti nel loro stile; qui diventano: grigi neutri (scuro #1C1C1E, chiaro #F2F2F7), pulsante principale arancione,
pulsante secondario blu trasparente. Gli angoli sono piu' morbidi (+40%)."""
import re

def _chiaro():
    try:
        from PyQt6.QtWidgets import QApplication
        return QApplication.palette().window().color().lightness() > 150
    except Exception:
        return False

# colori scritti nelle app (blu notte e oro) -> colori Apple
NEUTRI_SCURO = {"#0b2740": "#1c1c1e", "#08203a": "#161618", "#12365a": "#2c2c2e", "#17426b": "#3a3a3c", "#1e4f7c": "#3a3a3c", "#25507c": "#48484a", "#2a4d6e": "#48484a",
                "#e6f1ff": "#f2f2f7", "#8fb3d4": "#8e8e93", "#9fc2e4": "#98989d", "#d4e6f8": "#e5e5ea", "#b9d3ec": "#c7c7cc"}
NEUTRI_CHIARO = {"#0b2740": "#f2f2f7", "#08203a": "#e5e5ea", "#12365a": "#ffffff", "#17426b": "#e5e5ea", "#1e4f7c": "#d1d1d6", "#25507c": "#c7c7cc", "#2a4d6e": "#c7c7cc",
                 "#e6f1ff": "#1c1c1e", "#8fb3d4": "#6e6e73", "#9fc2e4": "#6e6e73", "#d4e6f8": "#3a3a3c", "#b9d3ec": "#48484a"}
ORO = ("#ffd479", "#ffe19e")                    # oro dei pulsanti e dei titoli
SECONDARI = ("#1e6fa8", "#2a82c2", "#2a82c0")   # blu dei pulsanti secondari
TESTO_ARANCIO = "#1c1c1e"

def _decl_colori(val, mappa):
    return re.sub(r"#[0-9a-fA-F]{6}\b", lambda m: mappa.get(m.group(0).lower(), m.group(0)), val)

def _blocco(b, chiaro):
    if "{" not in b: return b
    sel, corpo = b.split("{", 1); sel_l = sel.lower()
    righe = [r for r in corpo.split(";")]
    bg = ""
    for r in righe:
        m = re.match(r"\s*background(?:-color)?\s*:\s*(#[0-9a-fA-F]{6})", r)
        if m: bg = m.group(1).lower()
    e_oro = bg in ORO; e_sec = bg in SECONDARI; e_sel = "selected" in sel_l and bg != ""
    mappa = NEUTRI_CHIARO if chiaro else NEUTRI_SCURO
    arancio = "#ff9500" if chiaro else "#ff9f0a"; arancio_h = "#ffa933" if chiaro else "#ffb340"
    blu = "#007aff" if chiaro else "#0a84ff"
    out = []
    for r in righe:
        m = re.match(r"(\s*)([\w-]+)\s*:\s*(.+?)\s*$", r)
        if not m: out.append(r); continue
        ind, prop, val = m.group(1), m.group(2).lower(), m.group(3)
        if e_oro:
            if prop.startswith("background"): val = arancio_h if val.lower().startswith(ORO[1]) else arancio
            elif prop == "color": val = TESTO_ARANCIO
            else: val = _decl_colori(val, mappa)
        elif e_sel:
            if prop.startswith("background"): val = blu
            elif prop == "color": val = "#ffffff"
            else: val = _decl_colori(val, mappa)
        elif e_sec:
            h = val.lower().startswith(SECONDARI[1]) or val.lower().startswith(SECONDARI[2])
            if prop.startswith("background"): val = ("rgba(0,122,255,46)" if chiaro else "rgba(10,132,255,72)") if h else ("rgba(0,122,255,26)" if chiaro else "rgba(10,132,255,46)")
            elif prop == "color": val = blu
            else: val = _decl_colori(val, mappa)
        else:
            if prop == "color" and val.lower() == "#ffffff" and chiaro: val = "#1c1c1e"
            elif prop in ("color", "selection-color") or prop.startswith("border") or prop.startswith("background") or prop in ("selection-background-color", "outline"):
                v2 = _decl_colori(val, mappa)
                v2 = re.sub(r"#ffd479", arancio if not (chiaro and prop == "color") else "#c25e00", v2, flags=re.I)
                v2 = re.sub(r"#ffe19e", arancio_h, v2, flags=re.I); val = v2
            else: val = _decl_colori(val, mappa)
        out.append("%s%s: %s" % (ind, prop, val))
        if e_sec and not e_sel and prop.startswith("background"): out.append("%sborder: 1px solid %s" % (ind, blu if not chiaro else "rgba(0,122,255,115)"))
    return sel + "{" + ";".join(out)

def _morbidi(stile):
    return re.sub(r"(border-radius\s*:\s*)(\d+)(px)", lambda m: "%s%d%s" % (m.group(1), round(int(m.group(2)) * 1.4), m.group(3)), stile)

def adatta(stile):
    chiaro = _chiaro()
    stile = _morbidi(stile)
    return "}".join(_blocco(b, chiaro) for b in stile.split("}"))
