#!/usr/bin/env python3
"""Icone SofiOS per Mail, Note, Password (stesso disegno delle altre). Uso: icone_extra.py CARTELLA_ICONE"""
import os, sys
out = sys.argv[1]
ICONE = {
 "sofios-mail":     ("#ffd479", "#e8a33a", "#06111c", '<rect x="3" y="5.5" width="18" height="13" rx="2.5"/><path d="M3.8 7.5l8.2 6 8.2-6"/>', ["sofios-mail", "thunderbird", "org.mozilla.Thunderbird", "mozilla-thunderbird", "internet-mail"]),
 "sofios-note":     ("#ff8fb8", "#d6457f", "#fff",    '<path d="M5 4h14v10l-6 6H5z"/><path d="M19 14h-6v6"/>', ["sofios-note"]),
 "sofios-android":  ("#8be37a", "#2e9e4f", "#fff",    '<rect x="5" y="9" width="14" height="11" rx="3"/><path d="M8 9a4 4 0 018 0M7.5 4.5l1.6 2.4M16.5 4.5l-1.6 2.4"/><path d="M9.5 13v.01M14.5 13v.01"/>', ["sofios-android", "waydroid"]),
 "sofios-windows":  ("#7cc4ff", "#2b6fd6", "#fff",    '<rect x="4" y="4" width="16" height="16" rx="2.5"/><path d="M12 4v16M4 12h16"/>', ["sofios-windows", "wine"]),
 "sofios-assistente": ("#c9a2ff", "#6b3fd1", "#fff",    '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M18.5 15.5l.8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8z"/>', ["sofios-assistente"]),
 "sofios-password": ("#3fc1c9", "#1d7f8c", "#fff",    '<rect x="5" y="11" width="14" height="10" rx="2.5"/><path d="M8 11V8a4 4 0 018 0v3M12 15v2"/>', ["sofios-password", "keepassxc", "org.keepassxc.KeePassXC"]),
}
def svg(a, b, st, p):
    import sys as _s, os as _o; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__))); from stile_icone import quadrato
    return quadrato(a, p)
for chiave, (a, b, st, p, nomi) in ICONE.items():
    for d in ("SofiOS/scalable/apps", "hicolor/scalable/apps"):
        os.makedirs(os.path.join(out, d), exist_ok=True)
        for nm in nomi:
            open(os.path.join(out, d, nm + ".svg"), "w").write(svg(a, b, st, p))
print("ok")
