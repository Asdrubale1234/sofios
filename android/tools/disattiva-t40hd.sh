#!/usr/bin/env bash
# Disattiva (NON cancella) i programmi scelti da Luca sul T40HD. Si può annullare.
# Uso: bash disattiva-t40hd.sh [percorso-di-adb]
set -u
ADB="${1:-$HOME/Downloads/platform-tools/adb}"
DESK="$HOME/Desktop"
PRIMA="$DESK/T40HD-prima.txt"
ANNULLA="$DESK/annulla-T40HD.sh"

PACCHETTI="
com.google.android.apps.messaging
com.google.android.apps.wellbeing
com.google.android.apps.turbo
com.google.android.feedback
com.google.android.apps.restore
com.android.bips
com.google.android.printservice.recommendation
com.google.android.googlequicksearchbox
com.sprd.validationtools
com.sprd.engineermode
com.sprd.cameracalibration
com.sprd.camta
com.sprd.logmanager
com.sktl.sktldeviceinfo
com.tencent.soter.soterserver
com.android.egg
com.android.traceur
com.android.gallery3d
com.android.soundrecorder
com.android.fmradio
com.android.musicfx
com.android.dreams.phototable
com.android.dreams.basic
com.android.emergency
com.android.stk
com.google.android.deskclock
com.google.android.dialer
com.google.android.marvin.talkback
"

if ! "$ADB" devices | grep -qw device; then
  echo "Non vedo il tablet. Rifai: adb connect INDIRIZZO:PORTA (lo leggi in Debug wireless sul tablet)."; exit 1
fi

# Mai toccare Fully, SofiOS e la schermata del Teclast (sicurezza)
SALVI="de.ozerov.fully com.fullykiosk.singleapp it.sofilabs.sofios com.android.launcher3 com.android.settings com.android.systemui"

echo "Salvo com'è il tablet adesso in: $PRIMA"
{
  echo "== Disattivati PRIMA"; "$ADB" shell pm list packages -d | sed 's/^package://' | tr -d '\r' | sort
  echo "== Tutti i programmi PRIMA"; "$ADB" shell pm list packages | sed 's/^package://' | tr -d '\r' | sort
} > "$PRIMA"

N=$(echo "$PACCHETTI" | grep -c '[a-z]')
echo
echo "Sto per DISATTIVARE $N programmi (non vengono cancellati e si possono rimettere)."
echo "Premi Invio per continuare, oppure Ctrl+C per fermarti."
read -r _

echo "#!/usr/bin/env bash" > "$ANNULLA"
echo "# Rimette i programmi disattivati da disattiva-t40hd.sh" >> "$ANNULLA"
echo "ADB=\"\${1:-$ADB}\"" >> "$ANNULLA"
OK=0; NO=0
for p in $PACCHETTI; do
  case " $SALVI " in *" $p "*) echo "SALTATO (protetto): $p"; continue;; esac
  if ! "$ADB" shell pm list packages | tr -d '\r' | grep -qx "package:$p"; then
    echo "non presente: $p"; continue
  fi
  r=$("$ADB" shell pm disable-user --user 0 "$p" 2>&1 | tr -d '\r')
  if echo "$r" | grep -q "disabled-user"; then
    echo "disattivato: $p"; OK=$((OK+1))
    echo "\"\$ADB\" shell pm enable \"$p\"" >> "$ANNULLA"
  else
    echo "NON riuscito: $p -> $r"; NO=$((NO+1))
  fi
done
echo
echo "Fatto: $OK disattivati, $NO non riusciti."
echo "Per annullare tutto: bash $ANNULLA"
