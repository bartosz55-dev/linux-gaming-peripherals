#!/usr/bin/env bash
# ==============================================================================
# ESP32 & USB-UART Permissions Setup for Linux (Arch / Debian / Ubuntu / Fedora)
# Configures udev rules and user permissions for CH340, CP210x, FTDI, and Native ESP32 USB
# ==============================================================================

set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "[!] Ten skrypt musi być uruchomiony z uprawnieniami roota:"
    echo "    sudo ./setup_esp32_permissions.sh"
    exit 1
fi

REAL_USER="${SUDO_USER:-$USER}"

echo "==> 1. Konfiguracja uprawnień użytkownika '${REAL_USER}'..."
# Na Arch Linux grupą portów szeregowych jest 'uucp', na Debian/Ubuntu 'dialout'
if getent group uucp >/dev/null 2>&1; then
    usermod -a -G uucp "${REAL_USER}"
    echo "    [OK] Dodano użytkownika '${REAL_USER}' do grupy 'uucp'"
fi

if getent group dialout >/dev/null 2>&1; then
    usermod -a -G dialout "${REAL_USER}"
    echo "    [OK] Dodano użytkownika '${REAL_USER}' do grupy 'dialout'"
fi

echo "==> 2. Instalacja reguł udev dla mikrokontrolerów ESP32 / programatorów USB..."
UDEV_RULE_SRC="/home/user1/.local/share/esp32-env/99-platformio-udev.rules"
UDEV_RULE_DST="/etc/udev/rules.d/99-platformio-udev.rules"

if [ -f "${UDEV_RULE_SRC}" ]; then
    cp "${UDEV_RULE_SRC}" "${UDEV_RULE_DST}"
    chmod 644 "${UDEV_RULE_DST}"
    echo "    [OK] Skopiowano reguły udev do ${UDEV_RULE_DST}"
else
    echo "    [!] Pobieranie oficjalnych reguł PlatformIO udev..."
    curl -fsSL https://raw.githubusercontent.com/platformio/platformio-core/develop/platformio/assets/system/99-platformio-udev.rules -o "${UDEV_RULE_DST}"
    chmod 644 "${UDEV_RULE_DST}"
    echo "    [OK] Zainstalowano ${UDEV_RULE_DST}"
fi

echo "==> 3. Przeładowanie reguł udev w systemie..."
udevadm control --reload-rules
udevadm trigger

echo "==> 4. Sprawdzanie uprawnień do urządzeń USB..."
if ls -l /dev/ttyUSB* /dev/ttyACM* >/dev/null 2>&1; then
    echo "    Wykryte porty szeregowe:"
    ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || true
else
    echo "    Brak podłączonych urządzeń /dev/ttyUSB* lub /dev/ttyACM*"
fi

echo ""
echo "=============================================================================="
echo "Sukces! Uprawnienia i reguły udev zostały pomyślnie zainstalowane."
echo "UWAGA: Aby zmiany grup weszły w życie w bieżącej powłoce bez przelogowania,"
echo "możesz wykonać: newgrp uucp"
echo "=============================================================================="
