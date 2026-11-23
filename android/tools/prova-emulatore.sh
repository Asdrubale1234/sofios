#!/usr/bin/env bash
# Prova vera di SofiOS su un tablet simulato (Pixel Tablet, Android 14).
# Installa l'app, la imposta come schermata iniziale e scatta schermate reali.
# Uso: prova-emulatore.sh <apk-sofios> <apk-finto-fully> <cartella-uscita>
set -u
APK="$1"; FINTO="$2"; OUT="$3"; PKG=it.sofilabs.sofios
mkdir -p "$OUT"; LOG="$OUT/registro.txt"; : > "$LOG"
scrivi() { echo "$*" | tee -a "$LOG"; }
foto_subito() { adb exec-out screencap -p > "$OUT/$1.png"; scrivi "foto: $1.png"; }
foto() { sleep 3; adb exec-out screencap -p > "$OUT/$1.png"; scrivi "foto: $1.png"; }
# Aspetta (al massimo 40 secondi) che l'app in primo piano contenga il testo dato
aspetta_primo_piano() {
  for _ in $(seq 1 20); do in_primo_piano | grep -q "$1" && return 0; sleep 2; done
  return 1
}
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
tocca_testo() { tocca_con_durata "$1" 0; }
tocca_a_lungo() { tocca_con_durata "$1" 1200; }
tocca_con_durata() {
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
  if [ "$2" = 0 ]; then scrivi "tocco «$1» in $xy"; adb shell input tap $xy
  else scrivi "tocco lungo «$1» in $xy"; adb shell input swipe $xy $xy $2; fi
}

scrivi "== Dispositivo"
scrivi "modello: $(adb shell getprop ro.product.model | tr -d '\r')"
scrivi "Android: $(adb shell getprop ro.build.version.release | tr -d '\r') (API $(adb shell getprop ro.build.version.sdk | tr -d '\r'))"
scrivi "schermo: $(adb shell wm size | tr -d '\r')"

# Nel simulato spengo il lanciatore di Google (non serve e rallenta la prova)
adb shell pm disable-user --user 0 com.google.android.apps.nexuslauncher 2>&1 | tee -a "$LOG"
scrivi "== Installazione (SofiOS e un FINTO Fully, solo per la prova)"
adb install -r "$APK" 2>&1 | tee -a "$LOG"
adb install -r "$FINTO" 2>&1 | tee -a "$LOG"

scrivi "== Imposto SofiOS come schermata iniziale"
adb shell cmd role add-role-holder android.app.role.HOME $PKG 2>&1 | tee -a "$LOG"
scrivi "schermata iniziale scelta: $(adb shell cmd role get-role-holders android.app.role.HOME | tr -d '\r')"

scrivi "== A. Prima di toccare Casa: SofiOS non apre niente da solo"
sleep 8
in_primo_piano | grep -q "$PKG" || adb shell input keyevent KEYCODE_HOME
aspetta_primo_piano "$PKG/.MainActivity" || scrivi "ATTENZIONE: SofiOS non è in primo piano"
sleep 6
scrivi "in primo piano: $(in_primo_piano)"
in_primo_piano | grep -q "$PKG/.MainActivity" || scrivi "ATTENZIONE: Fully si è aperto da solo senza che nessuno toccasse Casa"
foto A-prima-di-toccare-casa

scrivi "== A2. Tocco Casa: si apre Fully (e da ora parte sempre da solo)"
tocca_testo "Casa"
aspetta_primo_piano "de.ozerov.fully" || scrivi "ATTENZIONE: Casa non si è aperta"
foto A2-casa-aperta

scrivi "== B. Chiudo Casa (tasto Indietro): sotto trovo SofiOS, con il puntino verde"
adb shell input keyevent KEYCODE_BACK
aspetta_primo_piano "$PKG/.MainActivity" || scrivi "ATTENZIONE: SofiOS non è tornato in primo piano"
sleep 2
scrivi "in primo piano: $(in_primo_piano)"
foto B-schermata-iniziale

scrivi "== B2. Mascotte: tocco, compare la X, la tolgo; uso l'icona accanto a Impostazioni per rimetterla"
tocca_testo "Mascotte SofiOS"; sleep 1
foto_subito B2-mascotte-con-x
tocca_testo "Nascondi la mascotte"; sleep 1
foto B3-mascotte-tolta
tocca_testo "Mostra o nascondi la mascotte"; sleep 1
foto_subito B4-icona-mascotte-tocco
tocca_testo "Mostra o nascondi la mascotte"; sleep 1
foto_subito B4b-mascotte-di-nuovo-tolta
tocca_testo "Mostra o nascondi la mascotte"; sleep 1
foto B5-mascotte-rimessa

scrivi "== C. Tasto Home non riapre Casa"
adb shell input keyevent KEYCODE_HOME; sleep 3
scrivi "in primo piano: $(in_primo_piano)"
foto C-tasto-home

scrivi "== N. Note: scrivo, seconda nota, chiudo e riapro, elimino"
contenuto_note() { adb shell "run-as $PKG sh -c 'for f in files/Note/*.txt; do echo \"\$f: \$(cat \$f)\"; done'" 2>&1 | tr -d '\r' | tee -a "$LOG"; }
tocca_testo "Note"; sleep 3
foto N1-note-vuota
adb shell input text "Spesa%sdel%ssabato"; sleep 2
foto_subito N2-prima-nota
scrivi "file sul tablet dopo la prima nota:"; contenuto_note
tocca_testo "Nuova nota"; sleep 2
adb shell input text "Chiamare%sLuca"; sleep 2
foto_subito N3-due-note
scrivi "file sul tablet dopo la seconda nota:"; contenuto_note
adb shell am force-stop $PKG; sleep 1
adb shell input keyevent KEYCODE_HOME; sleep 4
tocca_testo "Note"; sleep 3
foto N4-dopo-chiusura-e-riapertura
tocca_testo "Spesa del sabato"; sleep 2
foto_subito N5-riaperta-la-prima-nota
tocca_testo "Elimina nota"; sleep 2
foto_subito N6-conferma-eliminazione
tocca_testo "Sì"; sleep 2
foto_subito N7-dopo-eliminazione
scrivi "file sul tablet dopo l'eliminazione:"; contenuto_note
adb shell input keyevent KEYCODE_HOME; sleep 3
aspetta_primo_piano "$PKG/.MainActivity" || scrivi "ATTENZIONE: dalle Note il tasto Home non torna a SofiOS"

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
aspetta_primo_piano "de.ozerov.fully" || scrivi "ATTENZIONE: Casa non si è aperta"
scrivi "in primo piano: $(in_primo_piano)"
foto E-dopo-riavvio-casa

scrivi "== F. Chiudo Casa dopo il riavvio: sotto trovo SofiOS"
adb shell input keyevent KEYCODE_BACK
aspetta_primo_piano "$PKG/.MainActivity" || scrivi "ATTENZIONE: SofiOS non è tornato in primo piano"
sleep 2
scrivi "in primo piano: $(in_primo_piano)"
foto F-dopo-riavvio-schermata-iniziale

scrivi "== G. Tengo premuto su Casa: Fully non deve più partire da solo"
tocca_a_lungo "Casa"; sleep 1
foto_subito G-puntino-spento
adb reboot
aspetta_avvio
sleep 10
scrivi "in primo piano dopo il riavvio: $(in_primo_piano)"
in_primo_piano | grep -q "$PKG/.MainActivity" || scrivi "ATTENZIONE: dopo il riavvio Fully è partito anche se l'avevo spento"
foto G2-dopo-riavvio-senza-casa

ok=1
grep -q ATTENZIONE "$LOG" && ok=0
grep -q ERRORE "$LOG" && ok=0
in_primo_piano | grep -q "$PKG/.MainActivity" || ok=0
if [ $ok = 1 ]; then scrivi "ESITO FINALE: OK"; else scrivi "ESITO FINALE: NON OK"; fi
