#!/usr/bin/env bash
# Legge dal tablet l'elenco dei programmi. NON cambia niente sul tablet.
# Uso: bash elenco-pacchetti.sh        (tablet collegato con il cavo, Debug USB acceso)
set -u
if ! command -v adb >/dev/null; then
  echo "Manca adb. Nel Terminale scrivi:  brew install android-platform-tools"; exit 1
fi
adb start-server >/dev/null 2>&1
if ! adb devices | grep -qw device; then
  echo "Non vedo il tablet. Controlla il cavo e, sul tablet, tocca «Consenti» alla domanda sul Debug USB."; exit 1
fi
OUT="$HOME/Desktop/elenco-tablet.txt"
{
  echo "== Tablet"
  echo "marca:   $(adb shell getprop ro.product.brand | tr -d '\r')"
  echo "modello: $(adb shell getprop ro.product.model | tr -d '\r')"
  echo "Android: $(adb shell getprop ro.build.version.release | tr -d '\r')"
  echo
  echo "== Programmi di sistema (preinstallati)"
  adb shell pm list packages -s | sed 's/^package://' | sort
  echo
  echo "== Programmi installati da te"
  adb shell pm list packages -3 | sed 's/^package://' | sort
  echo
  echo "== Programmi già disattivati"
  adb shell pm list packages -d | sed 's/^package://' | sort
} > "$OUT"
echo "Fatto. Ho scritto l'elenco qui: $OUT"
echo "Apri quel file, copia tutto il testo e incollalo nella chat."
