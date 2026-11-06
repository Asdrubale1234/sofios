#!/bin/bash
# Gira dentro un contenitore Debian 13 (trixie).
set -euxo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends live-build debootstrap xorriso squashfs-tools ca-certificates \
  grub-efi-amd64-bin grub-pc-bin mtools dosfstools isolinux syslinux syslinux-common xz-utils cpio gnupg
cd /work/live
# Controllo nomi pacchetti: toglie (e segnala nel registro) quelli che non esistono in Debian 13
cat > /etc/apt/sources.list.d/extra.sources <<'S'
Types: deb
URIs: http://deb.debian.org/debian
Suites: trixie
Components: main contrib non-free non-free-firmware
S
apt-get update
for f in config/package-lists/*.list.chroot; do
  : > "$f.new"
  while read -r p; do
    case "$p" in ''|'#'*) continue;; esac
    if apt-cache show "$p" >/dev/null 2>&1; then echo "$p" >> "$f.new"; else echo "ATTENZIONE: pacchetto inesistente tolto: $p"; fi
  done < "$f"
  mv "$f.new" "$f"
done
lb clean --purge || true
lb config
lb build
mkdir -p /work/out
cp -v ./*.iso /work/out/
