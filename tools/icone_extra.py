#!/usr/bin/env python3
"""Icone SofiOS per Mail, Note, Password (stesso disegno delle altre). Uso: icone_extra.py CARTELLA_ICONE"""
import os, sys
out = sys.argv[1]
ICONE = {
 "sofios-mail":     ("#ffd479", "#e8a33a", "#06111c", '<rect x="3" y="5.5" width="18" height="13" rx="2.5"/><path d="M3.8 7.5l8.2 6 8.2-6"/>', ["sofios-mail", "thunderbird", "org.mozilla.Thunderbird", "mozilla-thunderbird", "internet-mail"]),
 "sofios-note":     ("#ff8fb8", "#d6457f", "#fff",    '<path d="M5 4h14v10l-6 6H5z"/><path d="M19 14h-6v6"/>', ["sofios-note"]),
 "sofios-password": ("#3fc1c9", "#1d7f8c", "#fff",    '<rect x="5" y="11" width="14" height="10" rx="2.5"/><path d="M8 11V8a4 4 0 018 0v3M12 15v2"/>', ["sofios-password", "keepassxc", "org.keepassxc.KeePassXC"]),
}
def svg(a, b, st, p):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="128" height="128">'
      '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient></defs>'
      '<rect x="0.5" y="0.5" width="23" height="23" rx="6" fill="url(#g)"/>'
      '<g transform="translate(4.8 4.8) scale(0.6)" fill="none" stroke="%s" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">%s</g></svg>') % (a, b, st, p)
for chiave, (a, b, st, p, nomi) in ICONE.items():
    for d in ("SofiOS/scalable/apps", "hicolor/scalable/apps"):
        os.makedirs(os.path.join(out, d), exist_ok=True)
        for nm in nomi:
            open(os.path.join(out, d, nm + ".svg"), "w").write(svg(a, b, st, p))
print("ok")
