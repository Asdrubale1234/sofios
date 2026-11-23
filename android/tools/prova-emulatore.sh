#!/usr/bin/env bash
# Prova vera di SofiOS su un tablet simulato (Pixel Tablet, Android 14).
# Installa l'app, la imposta come schermata iniziale e scatta schermate reali.
# Uso: prova-emulatore.sh <apk-sofios> <apk-finto-fully> <cartella-uscita>
set -u
APK="$1"; FINTO="$2"; OUT="$3"; PKG=it.sofilabs.sofios
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
    if f'text="{sys.argv[2]}"' in t or f'content-desc="{sys.argv[2]}"' in t:
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

scrivi "== Installazione (SofiOS e un FINTO Fully, solo per la prova)"
adb install -r "$APK" 2>&1 | tee -a "$LOG"
adb install -r "$FINTO" 2>&1 | tee -a "$LOG"

scrivi "== Imposto SofiOS come schermata iniziale"
adb shell cmd role add-role-holder android.app.role.HOME $PKG 2>&1 | tee -a "$LOG"
scrivi "schermata iniziale scelta: $(adb shell cmd role get-role-holders android.app.role.HOME | tr -d '\r')"

scrivi "== A. Prima accensione: SofiOS parte e apre da solo Casa"
adb shell input keyevent KEYCODE_HOME; sleep 4
scrivi "in primo piano: $(in_primo_piano)"
foto A-casa-aperta-da-sola

scrivi "== B. Chiudo Casa (tasto Indietro): sotto trovo SofiOS"
adb shell input keyevent KEYCODE_BACK; sleep 2
scrivi "in primo piano: $(in_primo_piano)"
foto B-schermata-iniziale

scrivi "== C. Tasto Home non riapre Casa"
adb shell input keyevent KEYCODE_HOME; sleep 3
scrivi "in primo piano: $(in_primo_piano)"
foto C-tasto-home

scrivi "== D. Tocco su Impostazioni e ritorno"
tocca_testo "Impostazioni"; sleep 3
scrivi "in primo piano: $(in_primo_piano)"
foto D-impostazioni
adb shell input keyevent KEYCODE_HOME; sleep 3
scrivi "dopo Home: $(in_primo_piano)"

scrivi "== E. Riavvio del tablet: Casa deve riaprirsi da sola"
adb reboot
aspetta_avvio
scrivi "schermata iniziale scelta dopo il riavvio: $(adb shell cmd role get-role-holders android.app.role.HOME | tr -d '\r')"
scrivi "in primo piano: $(in_primo_piano)"
foto E-dopo-riavvio-casa

scrivi "== F. Chiudo Casa dopo il riavvio: sotto trovo SofiOS"
adb shell input keyevent KEYCODE_BACK; sleep 2
scrivi "in primo piano: $(in_primo_piano)"
foto F-dopo-riavvio-schermata-iniziale

ok=1
in_primo_piano | grep -q "$PKG/.MainActivity" || ok=0
if [ $ok = 1 ]; then scrivi "ESITO FINALE: OK"; else scrivi "ESITO FINALE: NON OK"; fi
