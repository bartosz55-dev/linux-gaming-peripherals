---
name: redragon-k530-keyboard
description: >-
  Diagnostics, driver control, RGB lighting management, and custom configuration
  for Redragon K530 Draconic mechanical keyboards (0c45:5004 / Sonix SN32F248B) on Linux.
  Use when detecting, troubleshooting, setting lighting modes, remapping keys, or configuring
  permissions for Redragon K530 keyboards.
---

# Redragon K530 Draconic Keyboard Skill

This skill provides procedures, scripts, and reference documentation for managing, controlling, and configuring the **Redragon K530 Draconic** mechanical gaming keyboard under Linux (Arch Linux, Ubuntu/Debian, Fedora).

## Hardware Specifications
- **Device**: Redragon K530 Draconic (60% Compact RGB Mechanical Keyboard)
- **Vendor ID**: `0x0C45` (Microdia / SONiX)
- **Product ID**: `0x5004` (SONiX Draconic)
- **Microcontroller**: EVision VS11K09A-1 / Sonix SN32F248B (ARM Cortex-M0)
- **Control Interface**: HID Interface 1 (`Usage Page: 0xFF1C`, `Usage: 0x0092`, `Report ID: 0x04`)

---

## Quick Reference / Commands

### 1. Check Keyboard Connection and Status
Run the status check to verify USB endpoints and access permissions:
```bash
./scripts/k530ctl --status
```
Or directly via the toolchain path:
```bash
/home/user1/test/tools/k530ctl.py --status
```

### 2. Configure Non-Root Permissions (udev)
If `/dev/hidraw*` is restricted (`Permission denied`):
```bash
sudo ./scripts/setup_permissions.sh
```
This installs `/etc/udev/rules.d/99-redragon-k530.rules` and reloads udev.

### 3. Change Lighting Modes and Colors
List all supported lighting modes:
```bash
./scripts/k530ctl --list-modes
```

Common mode commands:
* **Static Color (Czerwony)**:
  ```bash
  ./scripts/k530ctl --mode static --color red --brightness 4
  ```
* **Static Color (HEX)**:
  ```bash
  ./scripts/k530ctl --mode static --color "#00FFAA" --brightness 3
  ```
* **Color Wave (Tęcza)**:
  ```bash
  ./scripts/k530ctl --mode wave --speed 3 --random
  ```
* **Breathing (Oddychanie z wybranym kolorem)**:
  ```bash
  ./scripts/k530ctl --mode breathing --color blue --speed 5
  ```
* **Wyłączenie podświetlenia**:
  ```bash
  ./scripts/k530ctl --mode static --color off --brightness 0
  ```

### 4. Official Windows Configuration Suite
If access to the official graphical utility is needed under Linux:
```bash
/home/user1/test/drivers/run_k530_wine.sh
```

---

## Detailed References
- [HID Protocol & Packet Layout](./references/protocol.md)
- [Lighting Modes & Parameter Reference](./references/modes.md)
