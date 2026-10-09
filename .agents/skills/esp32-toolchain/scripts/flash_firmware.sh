#!/usr/bin/env bash
# Helper script to auto-detect ESP32 serial port and flash binaries
set -euo pipefail

PORT="${1:-/dev/ttyUSB0}"
BAUD="${2:-921600}"

if [ ! -e "$PORT" ]; then
    # Try finding first available USB/ACM port
    DETECTED=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | head -n 1 || true)
    if [ -n "$DETECTED" ]; then
        PORT="$DETECTED"
        echo "[*] Auto-detected port: $PORT"
    else
        echo "[-] Error: No serial port found. Plug in ESP32."
        exit 1
    fi
fi

echo "[*] Querying ESP32 chip info on $PORT..."
esptool --port "$PORT" chip-id
echo "[*] Flash chip details:"
esptool --port "$PORT" flash-id
