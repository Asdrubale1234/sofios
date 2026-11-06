#!/bin/bash
# Gira dentro un contenitore Debian 13 (trixie).
set -euxo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends live-build debootstrap xorriso squashfs-tools ca-certificates \
  grub-efi-amd64-bin grub-pc-bin mtools dosfstools isolinux syslinux syslinux-common xz-utils cpio gnupg
cd /work/live
lb clean --purge || true
lb config
lb build
mkdir -p /work/out
cp -v ./*.iso /work/out/
