#!/usr/bin/env python3
"""Genera le icone di SofiOS (tutte disegnate da noi nello stesso stile) a partire dai tracciati aperti di Lucide (licenza ISC).
Uso: icone_set.py CARTELLA_LUCIDE_ICONS CARTELLA_USCITA   (uscita = .../usr/share/icons)
Due tipi: 'colorate' (quadrato arrotondato con sfumatura + simbolo bianco) e 'semplici' (solo simbolo, prendono il colore del tema)."""
import os, re, sys
src, out = sys.argv[1], sys.argv[2]

def tracciati(nome):
    p = os.path.join(src, nome + ".svg")
    if not os.path.exists(p):
        print("MANCA il simbolo", nome, file=sys.stderr); return None
    t = open(p).read()
    return "".join(re.findall(r"<(?:path|circle|rect|line|polyline|polygon|ellipse)\b[^>]*/>", t))

C = {"blu": ("#6fb3ff", "#2b6fd6"), "azzurro": ("#7cd4ff", "#2a8fd0"), "verde": ("#8be37a", "#2e9e4f"), "arancio": ("#ffd479", "#e8a33a"),
     "rosa": ("#ff8fb8", "#d6457f"), "viola": ("#c9a2ff", "#6b3fd1"), "petrolio": ("#3fc1c9", "#1d7f8c"), "rosso": ("#ff8a80", "#d6453a"), "grigio": ("#aab6c4", "#5b6b7d")}

# ---- icone colorate: nome-icona(e) -> (simbolo, colore)
COLORATE = {
 # categorie del menu
 "applications-accessories applications-utilities": ("wrench", "grigio"), "applications-graphics": ("image", "rosa"),
 "applications-internet": ("globe", "azzurro"), "applications-multimedia": ("circle-play", "viola"), "applications-office": ("file-text", "blu"),
 "applications-system applications-other": ("settings", "grigio"), "applications-development": ("code", "petrolio"), "applications-games": ("gamepad-2", "verde"),
 "applications-education": ("graduation-cap", "arancio"), "applications-science": ("flask-conical", "viola"), "applications-all applications-other-all": ("layout-grid", "blu"),
 "applications-android": ("smartphone", "verde"),
 # impostazioni di sistema
 "input-mouse preferences-desktop-mouse": ("mouse", "grigio"), "input-keyboard preferences-desktop-keyboard": ("keyboard", "grigio"),
 "input-touchpad": ("square-mouse-pointer", "grigio"), "input-touchscreen preferences-desktop-touch": ("hand", "grigio"),
 "input-gamepad preferences-desktop-gamepad": ("gamepad-2", "verde"), "input-tablet preferences-desktop-tablet": ("pen-tool", "viola"),
 "preferences-desktop-sound audio-card preferences-system-sound": ("volume-2", "azzurro"), "preferences-desktop-display preferences-desktop-display-color": ("monitor", "blu"),
 "preferences-desktop-accessibility": ("accessibility", "azzurro"), "preferences-system-bluetooth bluetooth": ("bluetooth", "blu"),
 "drive-removable-media-usb preferences-system-removable-devices": ("usb", "grigio"), "printer preferences-devices-printer": ("printer", "grigio"),
 "preferences-system-network network-workgroup preferences-system-network-wifi": ("wifi", "azzurro"),
 "preferences-desktop-wallpaper": ("image", "rosa"), "preferences-desktop-theme-global preferences-desktop-theme": ("palette", "viola"),
 "preferences-desktop-color": ("paintbrush", "rosa"), "preferences-desktop-font": ("a-large-small", "arancio"), "preferences-desktop-icons": ("shapes", "viola"),
 "preferences-cursor preferences-desktop-cursors": ("mouse-pointer-2", "grigio"), "preferences-desktop-theme-windowdecorations preferences-system-windows-decorations": ("app-window", "blu"),
 "preferences-system-windows preferences-system-windows-behavior": ("app-window", "blu"), "preferences-desktop-launch-feedback": ("rocket", "arancio"),
 "preferences-desktop-screensaver preferences-system-screen-locking": ("lock-keyhole", "grigio"), "preferences-desktop-effects preferences-system-desktop-effects": ("sparkles", "viola"),
 "preferences-desktop-plasma preferences-desktop-workspace": ("layout-dashboard", "blu"), "preferences-desktop-notification preferences-system-notifications": ("bell", "arancio"),
 "preferences-desktop-locale preferences-desktop-language preferences-desktop-locale-regional": ("languages", "verde"), "preferences-system-time clock": ("clock", "blu"),
 "preferences-desktop-user system-users preferences-system-users": ("users", "petrolio"), "user-identity preferences-desktop-user-password": ("user-round", "petrolio"),
 "preferences-system-login": ("log-in", "grigio"), "preferences-system-power-management battery-profile-performance": ("battery-charging", "verde"),
 "preferences-system-session-services preferences-system-startup": ("play", "grigio"), "preferences-desktop-default-applications": ("app-window", "blu"),
 "preferences-desktop-filetype-association preferences-system-file-associations": ("files", "arancio"), "preferences-desktop-text-to-speech": ("speech", "viola"),
 "preferences-system-search preferences-desktop-search": ("search", "blu"), "preferences-desktop-activities": ("layers", "viola"),
 "preferences-security preferences-system-privacy preferences-desktop-security": ("shield-check", "verde"), "preferences-desktop-gestures": ("hand", "viola"),
 "preferences-other preferences-system-other": ("settings", "grigio"), "preferences-desktop preferences-desktop-peripherals": ("sliders-horizontal", "grigio"),
 "preferences-system-network-sharing": ("share-2", "azzurro"), "preferences-desktop-keyboard-shortcut preferences-system-keyboard-shortcuts": ("command", "grigio"),
 "preferences-system-firewall": ("brick-wall", "rosso"), "preferences-system-power": ("power", "rosso"), "preferences-system-startup-and-shutdown": ("power", "grigio"),
 "preferences-desktop-menu-edit kmenuedit": ("list", "grigio"), "preferences-desktop-theme-applications": ("palette", "blu"),
 "preferences-system-bluetooth-battery": ("battery-charging", "blu"), "preferences-system-mobile-network": ("signal", "blu"),
 "preferences-system-vpn network-vpn": ("shield", "azzurro"), "preferences-system-online-accounts preferences-system-network-account": ("at-sign", "blu"),
 "preferences-desktop-remote-desktop krfb krdc": ("monitor-smartphone", "azzurro"), "kdeconnect preferences-system-kdeconnect": ("smartphone", "verde"),
 # assistenti online (un'icona nostra per ciascuno)
 "sofios-assistente-claude": ("sparkles", "arancio"), "sofios-assistente-chatgpt": ("message-circle", "verde"), "sofios-assistente-gemini": ("gem", "viola"),
 "sofios-assistente-copilot": ("bot", "blu"), "sofios-assistente-deepseek": ("telescope", "azzurro"), "sofios-assistente-mistral": ("wind", "rosso"),
 "sofios-assistente-perplexity": ("search", "petrolio"), "sofios-mascotte": ("lightbulb", "arancio"), "sofios-dispositivi": ("monitor-smartphone", "azzurro"),
 # emersi dalla diagnosi sulla ISO
 "gvim": ("file-code", "verde"), "libreoffice-startcenter": ("layout-grid", "blu"), "preferences-desktop-emoticons": ("smile", "arancio"),
 "tools-report-bug": ("bug", "rosso"), "battery": ("battery-charging", "verde"), "emblem-music-symbolic": ("music", "viola"),
 "input-keyboard-virtual": ("keyboard", "grigio"), "krunner plasma-search": ("search", "blu"), "ktip": ("lightbulb", "arancio"),
 "preferences-desktop-baloo": ("file-search", "blu"), "preferences-desktop-display-randr": ("monitor", "blu"), "preferences-desktop-feedback": ("message-square", "azzurro"),
 "preferences-desktop-font-installer": ("a-large-small", "arancio"), "preferences-desktop-gaming": ("gamepad-2", "verde"), "preferences-desktop-notification-bell": ("bell", "arancio"),
 "preferences-desktop-plasma-theme": ("palette", "viola"), "preferences-desktop-touchpad": ("square-mouse-pointer", "grigio"), "preferences-desktop-touchscreen": ("hand", "grigio"),
 "preferences-desktop-virtual": ("layout-grid", "blu"), "preferences-kde-connect": ("smartphone", "verde"), "preferences-security-firewall": ("brick-wall", "rosso"),
 "preferences-smart-status": ("hard-drive", "verde"), "preferences-system-network-connection": ("wifi", "azzurro"), "preferences-system-network-proxy": ("network", "azzurro"),
 "preferences-system-splash": ("rocket", "arancio"), "preferences-system-tabbox": ("layout-panel-left", "blu"), "preferences-system-windows-actions": ("app-window", "blu"),
 "preferences-web-browser-shortcuts": ("globe", "azzurro"), "redshift-status-on": ("moon-star", "arancio"), "xorg": ("monitor", "grigio"),
 # cartelle e luoghi
 "folder-documents": ("file-text", "arancio"), "folder-download": ("download", "arancio"), "folder-music": ("music", "arancio"),
 "folder-pictures": ("image", "arancio"), "folder-videos": ("film", "arancio"), "folder-templates": ("layout-template", "arancio"),
 "folder-public folder-publicshare": ("share-2", "arancio"), "folder-desktop": ("monitor", "arancio"), "user-home folder-home": ("house", "arancio"),
 "folder-remote network-server": ("server", "arancio"), "folder-recent document-open-recent": ("history", "arancio"), "folder-favorites folder-bookmark": ("star", "arancio"),
 "folder-open": ("folder-open", "arancio"), "folder-new": ("folder-plus", "arancio"), "user-trash": ("trash-2", "grigio"), "user-trash-full": ("trash", "grigio"),
 "drive-harddisk drive-harddisk-system": ("hard-drive", "grigio"), "drive-removable-media": ("usb", "grigio"), "drive-optical media-optical": ("disc", "grigio"),
 "drive-multidisk": ("database", "grigio"), "media-flash media-flash-sd-mmc": ("memory-stick", "grigio"),
 # applicazioni
 "system-software-install": ("package", "arancio"), "system-software-update": ("refresh-cw", "verde"), "package-x-generic": ("package", "arancio"),
 "applications-engineering": ("cpu", "petrolio"), "utilities-terminal-root": ("terminal", "rosso"), "org.kde.kmenuedit": ("list", "grigio"),
 "audio-headphones audio-headset": ("headphones", "viola"), "camera-photo camera-web": ("camera", "rosa"), "video-display": ("monitor", "blu"),
 "phone smartphone": ("smartphone", "verde"), "scanner": ("scan", "grigio"), "emblem-system": ("settings", "grigio"),
}

# ---- icone semplici (monocromatiche, prendono il colore del tema chiaro/scuro)
SEMPLICI = {
 "go-previous go-previous-symbolic": "arrow-left", "go-next go-next-symbolic": "arrow-right", "go-up go-up-symbolic": "arrow-up", "go-down go-down-symbolic": "arrow-down",
 "go-home go-home-symbolic": "house", "go-top": "chevrons-up", "go-bottom": "chevrons-down", "go-jump go-jump-symbolic": "corner-down-right",
 "go-previous-view": "chevron-left", "go-next-view": "chevron-right", "arrow-left": "arrow-left", "arrow-right": "arrow-right",
 "list-add list-add-symbolic": "plus", "list-remove list-remove-symbolic": "minus", "edit-delete edit-delete-symbolic edit-delete-remove": "trash-2",
 "edit-clear edit-clear-all edit-clear-symbolic": "eraser", "edit-copy edit-copy-symbolic": "copy", "edit-cut edit-cut-symbolic": "scissors",
 "edit-paste edit-paste-symbolic": "clipboard-paste", "edit-undo edit-undo-symbolic": "undo-2", "edit-redo edit-redo-symbolic": "redo-2",
 "edit-find edit-find-symbolic system-search system-search-symbolic search": "search", "edit-find-replace": "replace", "edit-select-all": "square-dashed",
 "edit-rename": "pencil-line", "document-edit document-edit-symbolic edit-entry": "pencil", "configure configure-symbolic": "settings-2",
 "document-new document-new-symbolic": "file-plus", "document-open document-open-symbolic": "folder-open", "document-save document-save-symbolic": "save",
 "document-save-as": "save-all", "document-print document-print-symbolic": "printer", "document-properties document-properties-symbolic": "file-cog",
 "document-export document-export-symbolic": "upload", "document-import document-import-symbolic": "download", "document-send": "send",
 "view-refresh view-refresh-symbolic reload": "refresh-cw", "view-fullscreen view-fullscreen-symbolic": "maximize", "view-restore": "minimize",
 "view-list-details view-list-text": "list", "view-list-icons view-grid": "layout-grid", "view-list-tree": "list-tree", "view-sort view-sort-ascending": "arrow-up-narrow-wide",
 "view-sort-descending": "arrow-down-wide-narrow", "view-preview": "eye", "view-hidden": "eye-off", "view-visible": "eye", "view-split-left-right": "columns-2",
 "view-media-playlist": "list-music", "view-calendar": "calendar", "view-filter": "filter", "view-pim-mail": "mail", "view-pim-contacts": "contact",
 "zoom-in zoom-in-symbolic": "zoom-in", "zoom-out zoom-out-symbolic": "zoom-out", "zoom-fit-best zoom-original": "scan-search",
 "window-close window-close-symbolic": "x", "dialog-close": "x", "window-new": "app-window", "window-minimize": "minus", "window-maximize": "square",
 "application-exit application-exit-symbolic": "log-out", "dialog-ok dialog-ok-apply": "check", "dialog-cancel": "ban", "dialog-yes": "check", "dialog-no": "x",
 "dialog-information dialog-information-symbolic": "info", "dialog-warning dialog-warning-symbolic": "triangle-alert", "dialog-error dialog-error-symbolic": "circle-x",
 "dialog-question dialog-question-symbolic help-about": "circle-help", "help-contents help-browser": "life-buoy", "help-about-symbolic": "info",
 "system-shutdown system-shutdown-symbolic": "power", "system-reboot system-reboot-symbolic": "rotate-cw", "system-suspend system-suspend-symbolic": "moon",
 "system-hibernate": "snowflake", "system-log-out system-log-out-symbolic": "log-out", "system-lock-screen system-lock-screen-symbolic": "lock",
 "system-switch-user": "users", "system-run system-run-symbolic": "play", "system-help": "life-buoy",
 "media-playback-start media-playback-start-symbolic": "play", "media-playback-pause media-playback-pause-symbolic": "pause", "media-playback-stop media-playback-stop-symbolic": "square",
 "media-skip-forward media-skip-forward-symbolic": "skip-forward", "media-skip-backward media-skip-backward-symbolic": "skip-back", "media-seek-forward": "fast-forward",
 "media-seek-backward": "rewind", "media-record media-record-symbolic": "circle-dot", "media-eject media-eject-symbolic": "arrow-up-to-line",
 "media-playlist-repeat": "repeat", "media-playlist-shuffle": "shuffle", "media-mount media-mount-symbolic": "plug", "media-unmount": "unplug",
 "audio-volume-high audio-volume-high-symbolic": "volume-2", "audio-volume-medium audio-volume-medium-symbolic": "volume-1", "audio-volume-low audio-volume-low-symbolic": "volume",
 "audio-volume-muted audio-volume-muted-symbolic": "volume-x", "microphone-sensitivity-high microphone-sensitivity-medium microphone-sensitivity-low audio-input-microphone audio-input-microphone-symbolic": "mic",
 "microphone-sensitivity-muted microphone-disabled audio-input-microphone-muted": "mic-off", "audio-speakers audio-speakers-symbolic": "speaker",
 "network-wireless network-wireless-symbolic network-wireless-connected-100 network-wireless-signal-excellent network-wireless-signal-excellent-symbolic": "wifi",
 "network-wireless-signal-good network-wireless-signal-good-symbolic": "wifi", "network-wireless-signal-ok network-wireless-signal-ok-symbolic network-wireless-signal-low network-wireless-signal-low-symbolic": "wifi-low",
 "network-wireless-signal-none network-wireless-signal-none-symbolic network-wireless-offline network-wireless-disconnected network-wireless-disabled": "wifi-off",
 "network-wired network-wired-symbolic network-wired-activated network-connect": "cable", "network-offline network-offline-symbolic network-disconnect network-wired-disconnected": "unplug",
 "network-vpn-symbolic": "shield", "network-transmit-receive": "arrow-down-up", "preferences-system-network-symbolic": "globe", "globe": "globe", "internet-web-browser-symbolic": "globe",
 "bluetooth-active bluetooth-active-symbolic bluetooth-symbolic": "bluetooth", "bluetooth-disabled bluetooth-disabled-symbolic": "bluetooth-off",
 "battery-100 battery-full battery-full-symbolic battery-good battery-good-symbolic": "battery-full", "battery-low battery-low-symbolic battery-caution battery-caution-symbolic battery-050 battery-040": "battery-low",
 "battery-charging battery-full-charging battery-good-charging": "battery-charging", "battery-empty battery-empty-symbolic battery-000": "battery-warning", "battery-missing": "battery",
 "brightness-high display-brightness display-brightness-symbolic display-brightness-high": "sun", "display-brightness-low display-brightness-medium": "sun-dim", "night-light night-light-symbolic weather-clear-night": "moon-star",
 "preferences-desktop-display-symbolic video-display-symbolic": "monitor", "computer computer-symbolic": "monitor", "computer-laptop": "laptop", "input-keyboard-symbolic": "keyboard",
 "notifications notification-active notification-symbolic": "bell", "notifications-disabled notification-disabled notification-inactive": "bell-off", "preferences-desktop-notification-symbolic": "bell",
 "mail-send mail-send-symbolic": "send", "mail-message-new mail-message-new-symbolic": "mail-plus", "mail-attachment mail-attachment-symbolic": "paperclip",
 "mail-reply-sender mail-reply-sender-symbolic": "reply", "mail-forward": "forward", "mail-mark-unread": "mail", "mail-mark-read": "mail-open", "mail-unread": "mail",
 "bookmark-new bookmarks": "bookmark", "bookmark-add": "bookmark-plus", "favorite emblem-favorite starred": "star", "non-starred": "star", "emblem-default": "check",
 "lock lock-symbolic emblem-locked object-locked": "lock", "unlock object-unlocked emblem-unlocked": "lock-open", "key password-copy": "key-round", "shield security-high": "shield-check",
 "security-low security-medium": "shield-alert", "preferences-security-symbolic": "shield-check", "dialog-password": "key-round",
 "user-available user-online": "circle-user", "user-away user-idle": "circle-user", "user-offline user-invisible": "circle-user", "user-identity-symbolic avatar-default avatar-default-symbolic": "circle-user",
 "folder-symbolic": "folder", "folder-open-symbolic": "folder-open", "text-x-generic text-plain": "file-text", "text-x-script": "file-code", "application-x-executable": "square-terminal",
 "image-x-generic": "image", "audio-x-generic": "music", "video-x-generic": "film", "application-pdf application-x-pdf": "file-text", "application-zip application-x-compressed-tar application-x-archive": "file-archive",
 "application-x-bittorrent": "magnet", "unknown application-octet-stream": "file", "x-office-document": "file-text", "x-office-spreadsheet": "file-spreadsheet", "x-office-presentation": "presentation",
 "inode-directory-symbolic": "folder", "folder-sync": "folder-sync", "edit-link insert-link": "link", "insert-image": "image-plus", "insert-text": "type", "format-text-bold": "bold",
 "format-text-italic": "italic", "format-text-underline": "underline", "format-justify-left": "align-left", "format-justify-center": "align-center", "format-justify-right": "align-right",
 "format-list-unordered": "list", "format-list-ordered": "list-ordered", "tools-wizard": "wand-sparkles", "tools-check-spelling spellcheck": "spell-check", "utilities-system-monitor-symbolic": "activity",
 "appointment-new appointment": "calendar-plus", "chronometer": "timer", "alarm alarm-symbolic": "alarm-clock", "clock-symbolic": "clock", "dialog-scripts": "scroll-text",
 "usb-symbolic drive-removable-media-usb-symbolic": "usb", "drive-harddisk-symbolic": "hard-drive", "drive-optical-symbolic media-optical-symbolic": "disc", "camera-photo-symbolic": "camera",
 "applications-graphics-symbolic": "image", "applications-internet-symbolic": "globe", "applications-multimedia-symbolic": "circle-play", "applications-office-symbolic": "file-text",
 "applications-system-symbolic applications-utilities-symbolic": "wrench", "applications-development-symbolic": "code", "applications-games-symbolic": "gamepad-2", "applications-science-symbolic": "flask-conical",
 "applications-education-symbolic": "graduation-cap", "preferences-system-symbolic": "settings", "preferences-other-symbolic": "settings", "go-parent-folder": "corner-left-up",
 "hint hint-symbolic": "lightbulb", "dialog-ok-symbolic": "check", "emblem-ok-symbolic": "check", "emblem-important emblem-warning": "triangle-alert", "emblem-error": "circle-x", "emblem-information": "info",
 "kt-add-feeds": "rss", "tag tag-symbolic": "tag", "cloud": "cloud", "cloud-upload": "cloud-upload", "cloud-download": "cloud-download", "sync-synchronizing sync-synchronizing-symbolic": "refresh-cw",
 "sync-error": "circle-alert", "process-working process-working-symbolic": "loader", "run-build": "hammer", "debug-run": "bug", "bug": "bug", "text-speak": "speech",
 "show-menu open-menu open-menu-symbolic application-menu": "menu", "overflow-menu": "ellipsis", "view-more-symbolic": "ellipsis", "handle-sort": "grip-vertical", "pin": "pin", "pin-symbolic": "pin",
 "go-up-symbolic-rtl": "arrow-up", "expand-all": "chevrons-up-down", "collapse-all": "chevrons-down-up", "arrow-up-double": "chevrons-up", "arrow-down-double": "chevrons-down",
 "plasmavault plasmavault-symbolic": "vault", "kdeconnect-symbolic": "smartphone", "phone-symbolic smartphone-symbolic": "smartphone", "screen-capture camera-video-symbolic": "video",
 "accessories-screenshot spectacle-symbolic": "camera", "video-card video-card-symbolic": "cpu", "cpu": "cpu", "memory": "memory-stick", "speedometer": "gauge",
}

def squircle(simbolo, colore):
    a, b = C[colore]; t = tracciati(simbolo)
    if t is None: return None
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="128" height="128">'
      '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient></defs>'
      '<rect x="0.5" y="0.5" width="23" height="23" rx="6" fill="url(#g)"/>'
      '<g transform="translate(4.8 4.8) scale(0.6)" fill="none" stroke="#fff" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">%s</g></svg>') % (a, b, t)

def semplice(simbolo, colore="#e6edf3"):
    t = tracciati(simbolo)
    if t is None: return None
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">'
      '<style type="text/css" id="current-color-scheme">.ColorScheme-Text{color:%s;}</style>'
      '<g class="ColorScheme-Text" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">%s</g></svg>') % (colore, t)

def scrivi(cartella, nomi, svg):
    os.makedirs(os.path.join(out, cartella), exist_ok=True)
    for n in nomi.split():
        open(os.path.join(out, cartella, n + ".svg"), "w").write(svg)

# non sovrascrive le icone già fatte a mano
esistenti = set(os.listdir(os.path.join(out, "SofiOS/scalable/apps"))) if os.path.isdir(os.path.join(out, "SofiOS/scalable/apps")) else set()
n_c = n_s = 0
for nomi, (sim, col) in COLORATE.items():
    s = squircle(sim, col)
    if s:
        scrivi("SofiOS/scalable/apps", " ".join(n for n in nomi.split() if n + ".svg" not in esistenti), s); n_c += len(nomi.split())
for nomi, sim in SEMPLICI.items():
    s = semplice(sim, "#e6edf3")             # tema scuro: simboli chiari
    if s:
        scrivi("SofiOS/scalable/azioni", nomi, s); n_s += len(nomi.split())
    s2 = semplice(sim, "#3b4654")            # tema chiaro: simboli scuri
    if s2:
        scrivi("SofiOS-chiaro/scalable/azioni", nomi, s2)
# il tema di icone chiaro: stesse icone colorate, simboli semplici scuri
import shutil
dest = os.path.join(out, "SofiOS-chiaro/scalable/apps")
shutil.rmtree(dest, ignore_errors=True)
shutil.copytree(os.path.join(out, "SofiOS/scalable/apps"), dest)
open(os.path.join(out, "SofiOS-chiaro/index.theme"), "w").write("""[Icon Theme]
Name=SofiOS chiaro
Comment=Icone di SofiOS per il tema chiaro
Inherits=breeze,hicolor
Directories=scalable/apps,scalable/azioni

[scalable/apps]
Size=128
MinSize=16
MaxSize=512
Type=Scalable
Context=Applications

[scalable/azioni]
Size=16
MinSize=8
MaxSize=512
Type=Scalable
Context=Actions
""")
print("colorate:", n_c, "semplici:", n_s)
