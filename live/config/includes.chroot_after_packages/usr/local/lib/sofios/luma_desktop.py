"""Luma sul desktop: metterla o toglierla (il widget) parlando con la scrivania di Plasma, come fa dock.py con la barra."""
import re, subprocess

WIDGET = "org.sofios.mascotte"

def _js(azione):
    return """
var trovati = 0; var ds = desktops();
for (var i = 0; i < ds.length; i++) {
  var d = ds[i]; var ids = d.widgetIds;
  for (var j = 0; j < ids.length; j++) {
    var w = d.widgetById(ids[j]);
    if (w.type == "%s") { trovati++; if ("%s" == "togli") { w.remove(); trovati--; } }
  }
  if ("%s" == "metti" && trovati == 0 && i == 0) {
    var gs = {width: 1280, height: 800}; try { gs = screenGeometry(d.screen); } catch (e) {}
    var hl = Math.round(gs.height * 0.26), wl = Math.round(hl * 0.64);
    d.addWidget("%s", Math.max(0, gs.width - wl - 50), Math.max(0, gs.height - hl - 110), wl, hl); trovati = 1;
  }
}
(trovati > 0) ? "si" : "no";
""" % (WIDGET, azione, azione, WIDGET)

def _esegui(azione):
    try:
        r = subprocess.run(["busctl", "--user", "call", "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell", "evaluateScript", "s", _js(azione)],
                           capture_output=True, text=True, timeout=15)
    except Exception:
        return None
    if r.returncode != 0: return None
    m = re.search(r'"?\b(si|no)\b"?', r.stdout)
    return m.group(1) if m else None

def stato():   return _esegui("leggi")      # 'si', 'no' o None (la scrivania non risponde)
def metti():   return _esegui("metti")
def togli():   return _esegui("togli")
