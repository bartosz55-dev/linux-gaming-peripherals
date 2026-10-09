---
name: esp32-toolchain
description: Comprehensive toolchain guide and automation for ESP32 devices. Use when compiling, flashing, monitoring, partitioning, or managing ESP32 boards (classic ESP32, S2, S3, C3, C6) via esptool, PlatformIO, or ESP-IDF.
---

# ESP32 Toolchain & Flashing Skill

This skill provides step-by-step procedures for managing firmware, flashing microcontrollers, reading chip metadata, and configuring builds for Espressif chips (ESP32, ESP32-S2, ESP32-S3, ESP32-C3, ESP32-C6).

---

## 1. Quick CLI Commands

### Checking Connection & Chip Information
```bash
# Detect chip model, MAC address, features
esptool --port /dev/ttyUSB0 chip-id

# Read flash chip ID and flash size (e.g., 4MB, 8MB, 16MB)
esptool --port /dev/ttyUSB0 flash-id
```

### Full Erase (Recommended when changing partition layouts)
```bash
esptool --port /dev/ttyUSB0 erase-flash
```

### Flashing Firmware Binaries
```bash
# Classic ESP32 (XTENSA dual-core) standard offsets:
esptool --port /dev/ttyUSB0 --baud 921600 write-flash \
  0x1000 bootloader.bin \
  0x8000 partitions.bin \
  0x10000 app.bin

# ESP32-S3 / C3 / C6 (Bootloader starts at 0x0):
esptool --port /dev/ttyUSB0 --baud 921600 write-flash \
  0x0 bootloader.bin \
  0x8000 partitions.bin \
  0x10000 app.bin
```

---

## 2. PlatformIO Workflows

### Initialize a New Project
```bash
# Classic ESP32 Dev Module (Arduino Framework)
pio project init --board esp32dev --project-option "framework=arduino"

# ESP32-S3 DevKit
pio project init --board esp32-s3-devkitc-1 --project-option "framework=arduino"

# ESP-IDF Framework
pio project init --board esp32dev --project-option "framework=espidf"
```

### Build, Upload, and Serial Monitor
```bash
# Compile code
pio run

# Compile and upload to ESP32
pio run --target upload

# Upload LittleFS / SPIFFS filesystem image
pio run --target uploadfs

# Open interactive serial monitor (115200 baud default)
pio device monitor --baud 115200
```

---

## 3. Flash Memory Offsets Reference

| Chip Series | Bootloader Offset | Partition Table | Boot App0 | Default App (OTA0) |
| :--- | :--- | :--- | :--- | :--- |
| **ESP32** | `0x1000` | `0x8000` | `0xe000` | `0x10000` |
| **ESP32-S2** | `0x1000` | `0x8000` | `0xe000` | `0x10000` |
| **ESP32-S3** | `0x0000` | `0x8000` | `0xe000` | `0x10000` |
| **ESP32-C3** | `0x0000` | `0x8000` | `0xe000` | `0x10000` |
| **ESP32-C6** | `0x0000` | `0x8000` | `0xe000` | `0x10000` |

---

## 4. Boot Modes & Flashing Issues

1. **Entering Bootloader Manually**:
   If `esptool` reports `A fatal error occurred: Failed to connect to ESP32: No serial data received`:
   - Press and **hold BOOT** (GPIO0).
   - Press and release **EN / RST**.
   - Release **BOOT**.
   - Re-run `esptool` or upload command.
2. **Auto-Reset Capacitor Fix**:
   On some cheap ESP32 boards with CH340 or CP2102, the DTR/RTS auto-reset timing fails. Solder a 10µF electrolytic or ceramic capacitor between `EN` and `GND` to ensure clean reset into download mode.

---

## 5. Detailed References & Scripts

- [Flashing & Bootloader Deep Dive](./references/flashing_and_bootloader.md)
- [Partition Tables & Filesystems](./references/partition_tables.md)
- Helper Scripts:
  - [flash_firmware.sh](./scripts/flash_firmware.sh)
  - [serial_monitor.py](./scripts/serial_monitor.py)
