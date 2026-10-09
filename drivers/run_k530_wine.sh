#!/usr/bin/env bash
# ==============================================================================
# Uruchamianie oficjalnej aplikacji Redragon K530RGB Keyboard w środowisku Wine
# ==============================================================================

set -euo pipefail

APP_DIR="/home/user1/test/drivers/k530_software"
EXE_NAME="Redragon K530RGB Keyboard.exe"

if [ ! -f "$APP_DIR/$EXE_NAME" ]; then
    echo "[!] Nie znaleziono pliku '$EXE_NAME' w $APP_DIR"
    exit 1
fi

echo "==> Uruchamianie oficjalnego oprogramowania Redragon K530 przez Wine..."
cd "$APP_DIR"
exec wine "$EXE_NAME" "$@"
