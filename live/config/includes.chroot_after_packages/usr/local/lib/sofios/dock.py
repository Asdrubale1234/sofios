"""Il Dock di SofiOS: mettere e togliere i programmi dalla barra in basso (con Plasma, tramite il suo scripting interno)."""
import json, re, subprocess

def _js(azione, desktop_id):
    return """
var risultato = "nessun-dock"; var ps = panels();
for (var i = 0; i < ps.length; i++) {
  var p = ps[i]; if (p.location != "bottom") continue;
  var ids = p.widgetIds;
  for (var j = 0; j < ids.length; j++) {
    var w = p.widgetById(ids[j]); if (w.type != "org.kde.plasma.icontasks") continue;
    w.currentConfigGroup = ["General"];
    var cur = w.readConfig("launchers", []);
    if (typeof cur === "string") cur = cur.length ? cur.split(",") : [];
    var voce = "applications:%s"; var presente = cur.indexOf(voce) >= 0;
    if ("%s" == "aggiungi" && !presente) { cur.push(voce); w.writeConfig("launchers", cur); w.reloadConfig(); }
    if ("%s" == "togli" && presente) { cur = cur.filter(function (x) { return x != voce; }); w.writeConfig("launchers", cur); w.reloadConfig(); }
    risultato = (cur.indexOf(voce) >= 0) ? "presente" : "assente";
  }
}
risultato;
""" % (desktop_id, azione, azione)

def _esegui(azione, desktop_id):
    """ritorna 'presente', 'assente' o None se non si riesce a parlare con la barra"""
    try:
        r = subprocess.run(["busctl", "--user", "call", "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell", "evaluateScript", "s", _js(azione, desktop_id)],
                           capture_output=True, text=True, timeout=15)
    except Exception:
        return None
    if r.returncode != 0: return None
    m = re.search(r"(presente|assente|nessun-dock)", r.stdout)
    return m.group(1) if m else ("presente" if azione == "aggiungi" else "assente")

def nel_dock(desktop_id): return _esegui("leggi", desktop_id) == "presente"
def metti(desktop_id): return _esegui("aggiungi", desktop_id) == "presente"
def togli(desktop_id): return _esegui("togli", desktop_id) == "assente"
