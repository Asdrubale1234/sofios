#!/bin/sh
# Prova veloce: copia nel sistema acceso i file del ramo (usr, etc), senza ricostruire la ISO. Solo per le prove.
cp -a /mnt/usr /mnt/etc / 2>/dev/null
chmod +x /usr/local/bin/sofios-* /usr/local/lib/sofios/* 2>/dev/null
echo "### patch-applicata" > /dev/ttyS0 2>/dev/null
exit 0
