#!/usr/bin/env bash
# ==============================================================================
# Redragon K530 Draconic Keyboard - Konfiguracja uprawnień udev dla Linux
# Umożliwia dostęp bez roota do interfejsu Vendor HID (0c45:5004) dla k530ctl oraz OpenRGB
# ==============================================================================

set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "[!] Ten skrypt wymaga uprawnień administratora (root):"
    echo "    sudo ./setup_k530_permissions.sh"
    exit 1
fi

REAL_USER="${SUDO_USER:-$USER}"
UDEV_RULE_FILE="/etc/udev/rules.d/99-redragon-k530.rules"

echo "==> 1. Konfiguracja grupy 'input' dla użytkownika '${REAL_USER}'..."
if getent group input >/dev/null 2>&1; then
    usermod -a -G input "${REAL_USER}"
    echo "    [OK] Dodano użytkownika '${REAL_USER}' do grupy 'input'"
fi

echo "==> 2. Tworzenie reguł udev w ${UDEV_RULE_FILE}..."
cat << 'EOF' > "${UDEV_RULE_FILE}"
# Redragon K530 Draconic Mechanical Keyboard (VID: 0x0C45, PID: 0x5004)
# Umożliwia sterowanie podświetleniem RGB i profilami użytkownika przez hidapi / k530ctl / OpenRGB
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0c45", ATTRS{idProduct}=="5004", MODE:="0666", GROUP="input", TAG+="uaccess"
KERNEL=="hidraw*", ATTRS{idVendor}=="0c45", ATTRS{idProduct}=="5004", MODE:="0666", GROUP="input", TAG+="uaccess"
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="0c45", ATTRS{idProduct}=="5004", MODE:="0666", GROUP="input", TAG+="uaccess"
EOF

chmod 644 "${UDEV_RULE_FILE}"
echo "    [OK] Zapisano reguły udev."

echo "==> 3. Przeładowanie reguł udev w systemie..."
udevadm control --reload-rules
udevadm trigger

echo "==> 4. Aktualizacja uprawnień dla aktualnie podłączonych węzłów hidraw..."
for h in /sys/class/hidraw/hidraw*; do
    if [ -f "$h/device/uevent" ]; then
        if grep -q "00000C45:00005004" "$h/device/uevent" 2>/dev/null; then
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
echo "Sukces! Reguły udev zostały zainstalowane pomyślnie."
echo "Teraz możesz zarządzać klawiaturą bez uprawnień roota komendą:"
echo "    /home/user1/test/tools/k530ctl.py --status"
echo "=============================================================================="
