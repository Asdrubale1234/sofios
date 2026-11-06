#!/usr/bin/env python3
"""Genera il tema di icone SofiOS (SVG) dalle icone dell'anteprima."""
import re, os, sys
src = sys.argv[1]; out = sys.argv[2]
html = open(src, encoding="utf-8").read()
IC = {}
for m in re.finditer(r'"([^"]+)":\["(#[0-9a-fA-F]+),(#[0-9a-fA-F]+)","(#?\w+)",\'([^\']*)\'\]', html):
    IC[m.group(1)] = (m.group(2), m.group(3), m.group(4), m.group(5))
EXTRA = {
 "Archivi": ("#f2c26b","#c98a2b","#06111c",'<rect x="4" y="3" width="16" height="18" rx="2.5"/><path d="M12 3v10M10 7h4M10 11h4"/>'),
 "Lettore PDF": ("#ff8a80","#d6453b","#fff",'<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M10 13h5M10 17h5"/>'),
 "Dischi": ("#8a97a6","#4d5a68","#fff",'<rect x="3" y="8" width="18" height="8" rx="2.5"/><path d="M7 12h.01M11 12h6"/>'),
 "Collega telefono": ("#4fd1a0","#1f9d77","#fff",'<rect x="7" y="3" width="10" height="18" rx="2.5"/><path d="M11 18h2"/>'),
 "Cerca file": ("#59a8ff","#2a63d6","#fff",'<circle cx="11" cy="11" r="6"/><path d="M16 16l4 4"/>'),
 "Informazioni": ("#59a8ff","#2a63d6","#fff",'<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5h.01"/>'),
 "Backup": ("#4fd1a0","#16795a","#fff",'<path d="M12 4v10M8 10l4 4 4-4M5 19h14"/>'),
 "Monitor": ("#ff9a62","#d9533b","#fff",'<path d="M3 12h4l3-7 4 14 3-7h4"/>'),
 "Editor di testo": ("#b79cff","#6a4fd6","#fff",'<rect x="6" y="4" width="12" height="16" rx="2.5"/><path d="M9 9h6M9 13h6M9 17h3"/>'),
 "Schermate": ("#59a8ff","#2a63d6","#fff",'<path d="M4 8V5h3M17 5h3v3M20 16v3h-3M7 19H4v-3"/><rect x="8" y="9" width="8" height="6" rx="1.5"/>'),
 "Scrittura": ("#59a8ff","#2a63d6","#fff",'<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M10 12h5M10 16h5"/>'),
 "Fogli": IC.get("Foglio di calcolo", ("#4fd1a0","#16795a","#fff",'<rect x="4" y="4" width="16" height="16" rx="2.5"/><path d="M4 10h16M4 15h16M10 4v16"/>')),
 "Video": IC.get("VLC", ("#ff9a3c","#e0661a","#fff",'<path d="M9 6l9 6-9 6z"/>')),
 "SofiOS": ("#12304c","#06111c","#ffd479",'<path d="M12 3v3M9 21h6M10 21V11h4v10M9 11l3-4 3 4M3 8l4 2M21 8l-4 2"/>'),
}
for k, v in EXTRA.items():
    if k not in IC or isinstance(v, tuple) and len(v) == 4 and k in ("Fogli","Video"):
        IC[k] = v
# nome app -> (voce del dizionario, nomi di icona)
MAP = {
 "File": ["sofios-file", "system-file-manager", "org.kde.dolphin", "folder"],
 "Terminale": ["sofios-terminale", "utilities-terminal", "org.kde.konsole", "konsole"],
 "Editor di testo": ["sofios-editor", "kwrite", "org.kde.kwrite", "accessories-text-editor"],
 "Calcolatrice": ["sofios-calcolatrice", "accessories-calculator", "kcalc", "org.kde.kcalc"],
 "Schermate": ["sofios-schermate", "org.kde.spectacle", "spectacle"],
 "Lettore PDF": ["sofios-pdf", "okular", "org.kde.okular"],
 "Foto": ["sofios-foto", "org.kde.gwenview", "gwenview"],
 "Archivi": ["sofios-archivi", "ark", "org.kde.ark"],
 "Collega telefono": ["sofios-telefono", "kdeconnect", "org.kde.kdeconnect"],
 "SoStore": ["sofios-store", "plasma-discover", "org.kde.discover"],
 "Dischi": ["sofios-dischi", "partitionmanager", "org.kde.partitionmanager"],
 "Impostazioni": ["sofios-impostazioni", "preferences-system", "systemsettings", "org.kde.systemsettings"],
 "Browser": ["sofios-browser", "firefox-esr", "firefox", "web-browser"],
 "Scrittura": ["sofios-scrittura", "libreoffice-writer"],
 "Fogli": ["sofios-fogli", "libreoffice-calc"],
 "Video": ["sofios-video", "vlc"],
 "Cerca file": ["sofios-cerca", "org.kde.kfind", "kfind"],
 "Informazioni": ["sofios-info", "kinfocenter", "org.kde.kinfocenter", "hwinfo"],
 "Backup": ["sofios-backup", "kup", "org.kde.kup"],
 "Monitor": ["sofios-monitor", "org.kde.plasma-systemmonitor", "utilities-system-monitor"],
 "SofiOS": ["sofios-logo", "start-here-sofios", "start-here-kde", "start-here", "distributor-logo-sofios", "calamares"],
}
def svg(a, b, stroke, path):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="128" height="128">'
      '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient></defs>'
      '<rect x="0.5" y="0.5" width="23" height="23" rx="6" fill="url(#g)"/>'
      '<g transform="translate(4.8 4.8) scale(0.6)" fill="none" stroke="%s" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">%s</g></svg>') % (a, b, stroke, path)
for d in ("SofiOS/scalable/apps", "hicolor/scalable/apps"):
    os.makedirs(os.path.join(out, d), exist_ok=True)
n = 0
for key, names in MAP.items():
    a, b, st, p = IC[key]
    s = svg(a, b, st, p)
    for nm in names:
        for d in ("SofiOS/scalable/apps", "hicolor/scalable/apps"):
            open(os.path.join(out, d, nm + ".svg"), "w").write(s); n += 1
open(os.path.join(out, "SofiOS/index.theme"), "w").write(
"""[Icon Theme]
Name=SofiOS
Comment=Icone di SofiOS
Inherits=breeze-dark,breeze,hicolor
Directories=scalable/apps

[scalable/apps]
Size=128
MinSize=16
MaxSize=512
Type=Scalable
Context=Applications
""")
print("icone scritte:", n, "app:", len(MAP))
