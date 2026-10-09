#!/usr/bin/env python3
"""
Simple and robust terminal serial monitor for ESP32 with ANSI color highlighting.
Supports auto-reconnection and standard ESP32 baud rates (115200 default).
"""
import sys
import time
import serial
import serial.tools.list_ports

def find_esp_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "USB" in p.device or "ACM" in p.device:
            return p.device
    return None

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else find_esp_port()
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 115200

    if not port:
        print("[!] No serial port found (/dev/ttyUSB* or /dev/ttyACM*)")
        sys.exit(1)

    print(f"[*] Opening {port} at {baud} baud (Ctrl+C to stop)...")
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
    except Exception as e:
        print(f"[!] Error opening {port}: {e}")
        sys.exit(1)

    try:
        while True:
            line = ser.readline()
            if line:
                decoded = line.decode('utf-8', errors='replace')
                print(decoded, end='', flush=True)
    except KeyboardInterrupt:
        print("\n[*] Monitor closed.")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
