#!/usr/bin/env bash
# ==============================================================================
# SteelSeries Aerox 3 Wireless - Konfiguracja uprawnień udev dla Linux
# Umożliwia pełną kontrolę nad myszką (DPI, podświetlenie RGB, odpytywanie baterii)
# bez wymagania uprawnień roota dla aeroxctl oraz aeroxgui.
# ==============================================================================

set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "[!] Ten skrypt wymaga uprawnień administratora (root):"
    echo "    sudo /home/user1/test/setup_aerox_permissions.sh"
    exit 1
fi

REAL_USER="${SUDO_USER:-$USER}"
UDEV_RULE_FILE="/etc/udev/rules.d/99-steelseries-aerox.rules"

echo "==> 1. Konfiguracja grupy 'input' dla użytkownika '${REAL_USER}'..."
if getent group input >/dev/null 2>&1; then
    usermod -a -G input "${REAL_USER}"
    echo "    [OK] Użytkownik '${REAL_USER}' jest przypisany do grupy 'input'"
fi

echo "==> 2. Tworzenie reguł udev w ${UDEV_RULE_FILE}..."
cat << 'EOF' > "${UDEV_RULE_FILE}"
# SteelSeries Aerox 3 Wireless (2.4GHz Dongle: 1038:1838, Wired: 1038:183a)
# Aerox 3 CS2 Dragon Lore (Dongle: 1038:1878, Wired: 1038:187a)
# Aerox 3 Wired (1038:1836)
SUBSYSTEMS=="usb", ATTRS{idVendor}=="1038", ATTRS{idProduct}=="1838", MODE:="0666", GROUP="input", TAG+="uaccess"
KERNEL=="hidraw*", ATTRS{idVendor}=="1038", ATTRS{idProduct}=="1838", MODE:="0666", GROUP="input", TAG+="uaccess"
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="1038", ATTRS{idProduct}=="1838", MODE:="0666", GROUP="input", TAG+="uaccess"

SUBSYSTEMS=="usb", ATTRS{idVendor}=="1038", ATTRS{idProduct}=="183a", MODE:="0666", GROUP="input", TAG+="uaccess"
KERNEL=="hidraw*", ATTRS{idVendor}=="1038", ATTRS{idProduct}=="183a", MODE:="0666", GROUP="input", TAG+="uaccess"
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="1038", ATTRS{idProduct}=="183a", MODE:="0666", GROUP="input", TAG+="uaccess"

SUBSYSTEMS=="usb", ATTRS{idVendor}=="1038", ATTRS{idProduct}=="1878", MODE:="0666", GROUP="input", TAG+="uaccess"
KERNEL=="hidraw*", ATTRS{idVendor}=="1038", ATTRS{idProduct}=="1878", MODE:="0666", GROUP="input", TAG+="uaccess"
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="1038", ATTRS{idProduct}=="1878", MODE:="0666", GROUP="input", TAG+="uaccess"

SUBSYSTEMS=="usb", ATTRS{idVendor}=="1038", ATTRS{idProduct}=="187a", MODE:="0666", GROUP="input", TAG+="uaccess"
KERNEL=="hidraw*", ATTRS{idVendor}=="1038", ATTRS{idProduct}=="187a", MODE:="0666", GROUP="input", TAG+="uaccess"
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="1038", ATTRS{idProduct}=="187a", MODE:="0666", GROUP="input", TAG+="uaccess"

SUBSYSTEMS=="usb", ATTRS{idVendor}=="1038", ATTRS{idProduct}=="1836", MODE:="0666", GROUP="input", TAG+="uaccess"
KERNEL=="hidraw*", ATTRS{idVendor}=="1038", ATTRS{idProduct}=="1836", MODE:="0666", GROUP="input", TAG+="uaccess"
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="1038", ATTRS{idProduct}=="1836", MODE:="0666", GROUP="input", TAG+="uaccess"
EOF

chmod 644 "${UDEV_RULE_FILE}"
echo "    [OK] Zapisano reguły udev."

echo "==> 3. Przeładowanie reguł udev w systemie..."
udevadm control --reload-rules
udevadm trigger

echo "==> 4. Aktualizacja uprawnień dla aktualnie podłączonych węzłów hidraw..."
for h in /sys/class/hidraw/hidraw*; do
    if [ -f "$h/device/uevent" ]; then
        if grep -qE "00001038:0000(1838|183A|1878|187A|1836)" "$h/device/uevent" 2>/dev/null; then
            DEVNODE="/dev/$(basename "$h")"
            if [ -c "$DEVNODE" ]; then
                chmod 666 "$DEVNODE"
                echo "    [OK] Ustawiono chmod 666 dla $DEVNODE"
            fi
        fi
    fi
done

echo ""
echo "=============================================================================="
echo "Sukces! Reguły udev dla SteelSeries Aerox 3 zostały zainstalowane pomyślnie."
echo "Teraz możesz zarządzać myszką bez uprawnień roota poleceniem:"
echo "    /home/user1/test/tools/aeroxctl.py --status"
echo "=============================================================================="
