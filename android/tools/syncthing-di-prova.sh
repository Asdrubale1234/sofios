#!/bin/bash
# Avvia un Syncthing vero (solo per i collaudi) su 127.0.0.1:8384, senza TLS, con la chiave scritta in /tmp/st/chiave.
sudo apt-get install -y syncthing 2>&1 | tail -1
mkdir -p /tmp/st && syncthing generate --home=/tmp/st --no-default-folder 2>&1 | tail -2
python3 - <<'PY'
import re
p = "/tmp/st/config.xml"; s = open(p).read()
s = re.sub(r'(<gui enabled="true" tls=")(true|false)"', r'\1false"', s)
s = re.sub(r'<address>[^<]*</address>', '<address>127.0.0.1:8384</address>', s, count=1)
open(p, "w").write(s)
open("/tmp/st/chiave", "w").write(re.search(r'<apikey>([^<]*)</apikey>', s).group(1))
PY
(nohup syncthing serve --home=/tmp/st --no-browser --no-upgrade > /tmp/st/log.txt 2>&1 &)
for i in $(seq 1 30); do curl -s -o /dev/null -H "X-API-Key: $(cat /tmp/st/chiave)" http://127.0.0.1:8384/rest/system/ping && break; sleep 1; done
