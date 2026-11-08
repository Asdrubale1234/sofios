# Barra laterale di File in italiano (Scrivania): creata al primo accesso, poi l'utente la modifica a piacere
f="$HOME/.local/share/user-places.xbel"
if [ ! -e "$f" ] && [ -r /usr/share/sofios/user-places.xbel.in ]; then
  mkdir -p "$HOME/.local/share" && sed "s#__H__#$HOME#g" /usr/share/sofios/user-places.xbel.in > "$f"
fi
