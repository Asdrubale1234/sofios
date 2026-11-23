#!/usr/bin/env bash
# Prova vera di SofiOS su un tablet simulato (Pixel Tablet, Android 14).
# Installa l'app, la imposta come schermata iniziale e scatta schermate reali.
# Uso: prova-emulatore.sh <apk> <cartella-uscita>
set -u
APK="$1"; OUT="$2"; PKG=it.sofilabs.sofios
mkdir -p "$OUT"; LOG="$OUT/registro.txt"; : > "$LOG"
scrivi() { echo "$*" | tee -a "$LOG"; }
foto() { sleep 3; adb exec-out screencap -p > "$OUT/$1.png"; scrivi "foto: $1.png"; }
in_primo_piano() {
  adb shell dumpsys activity activities | grep -m1 -E 'topResumedActivity|mResumedActivity' | sed 's/^ *//'
}
aspetta_avvio() {
  adb wait-for-device
  for _ in $(seq 1 120); do
    [ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = 1 ] && break
    sleep 2
  done
  sleep 15
  adb shell input keyevent 82 >/dev/null 2>&1   # sblocca lo schermo
}
# Tocca l'elemento che mostra il testo dato (legge la schermata vera, niente coordinate a caso)
tocca_testo() {
  adb shell uiautomator dump /sdcard/ui.xml >/dev/null
  adb pull /sdcard/ui.xml "$OUT/ui.xml" >/dev/null
  xy=$(python3 - "$OUT/ui.xml" "$1" <<'EOF'
import re, sys
xml = open(sys.argv[1], encoding="utf-8").read()
for n in re.finditer(r'<node [^>]*>', xml):
    t = n.group(0)
    if f'text="{sys.argv[2]}"' in t:
        a, b, c, d = map(int, re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', t).groups())
        print((a + c) // 2, (b + d) // 2); break
EOF
)
  rm -f "$OUT/ui.xml"
  if [ -z "$xy" ]; then scrivi "ERRORE: non trovo «$1» sullo schermo"; return 1; fi
  scrivi "tocco «$1» in $xy"; adb shell input tap $xy
}

scrivi "== Dispositivo"
scrivi "modello: $(adb shell getprop ro.product.model | tr -d '\r')"
scrivi "Android: $(adb shell getprop ro.build.version.release | tr -d '\r') (API $(adb shell getprop ro.build.version.sdk | tr -d '\r'))"
scrivi "schermo: $(adb shell wm size | tr -d '\r')"

scrivi "== Installazione"
adb install -r "$APK" 2>&1 | tee -a "$LOG"

scrivi "== Imposto SofiOS come schermata iniziale"
adb shell cmd role add-role-holder android.app.role.HOME $PKG 2>&1 | tee -a "$LOG"
scrivi "schermata iniziale scelta: $(adb shell cmd role get-role-holders android.app.role.HOME | tr -d '\r')"

scrivi "== 1. Schermata iniziale"
adb shell input keyevent KEYCODE_HOME; sleep 2
scrivi "in primo piano: $(in_primo_piano)"
foto 1-schermata-iniziale

scrivi "== 2. Tocco su Impostazioni"
tocca_testo "Impostazioni"
sleep 3
scrivi "in primo piano: $(in_primo_piano)"
foto 2-impostazioni

scrivi "== 3. Tasto Home"
adb shell input keyevent KEYCODE_HOME
scrivi "in primo piano: $(in_primo_piano)"
foto 3-tasto-home

scrivi "== 4. Riavvio del tablet"
adb reboot
aspetta_avvio
scrivi "schermata iniziale scelta dopo il riavvio: $(adb shell cmd role get-role-holders android.app.role.HOME | tr -d '\r')"
scrivi "in primo piano: $(in_primo_piano)"
foto 4-dopo-riavvio

if in_primo_piano | grep -q "$PKG/.MainActivity"; then
  scrivi "ESITO: OK, dopo il riavvio la schermata iniziale è SofiOS"
else
  scrivi "ESITO: NON OK, dopo il riavvio la schermata iniziale non è SofiOS"
fi
