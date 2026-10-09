---
name: steelseries-aerox-mouse
description: >-
  Diagnostics, driver control, RGB lighting management, DPI sensitivity, and battery monitoring
  for SteelSeries Aerox 3 Wireless and Wired gaming mice on Linux. Use when detecting,
  configuring, setting lighting, tweaking CPI/DPI, checking battery, or fixing udev permissions.
---

# SteelSeries Aerox 3 Gaming Mouse Skill

This skill provides procedures, scripts, and technical documentation for managing and configuring the **SteelSeries Aerox 3 Wireless** (2.4 GHz & Wired USB) gaming mouse under Linux.

## Hardware Specifications
- **Device**: SteelSeries Aerox 3 Wireless / Wired (Ultralight 66g / 68g RGB Gaming Mouse)
- **Sensor**: SteelSeries TrueMove Air Optical Sensor (PixArt PAW3335, 100 – 18,000 DPI, 400 IPS, 40G)
- **Vendor ID**: `0x1038` (SteelSeries ApS)
- **Product IDs**:
  - `0x1838`: Aerox 3 Wireless (2.4 GHz Dongle Mode)
  - `0x183A`: Aerox 3 Wireless (Wired USB Mode)
  - `0x1878`: Aerox 3 Wireless CS2 Edition (2.4 GHz Dongle Mode)
  - `0x187A`: Aerox 3 Wireless CS2 Edition (Wired USB Mode)
  - `0x1836`: Aerox 3 Wired
- **Control Interface**: HID Interface 3 (`Usage Page: 0xFFC0`, `Usage: 0x0001`, Endpoint 3)
- **Wireless Command Flag**: In 2.4 GHz wireless mode, the first byte of every command must have bit 6 set (`command[0] |= 0x40`).

---

## Quick Reference / Commands

### 1. Check Connection, Battery & Status
Check device connection, wireless mode, and battery status:
```bash
./scripts/aeroxctl --status
```
Or directly:
```bash
/home/user1/test/tools/aeroxctl.py --status
```

Only query battery percentage:
```bash
/home/user1/test/tools/aeroxctl.py --battery
```

### 2. Configure Non-Root Permissions (udev)
If `/dev/hidraw*` reports `Permission denied`:
```bash
sudo /home/user1/test/setup_aerox_permissions.sh
```
This installs `/etc/udev/rules.d/99-steelseries-aerox.rules` and sets immediate `chmod 666` on the device nodes.

### 3. Change RGB Lighting
* **All Zones (Single Color)**:
  ```bash
  /home/user1/test/tools/aeroxctl.py --color "#FF5200"
  /home/user1/test/tools/aeroxctl.py --color orange
  ```
* **Individual 3-Zone Control**:
  ```bash
  /home/user1/test/tools/aeroxctl.py --top red --middle cyan --bottom blue
  ```
* **Rainbow Wave Effect**:
  ```bash
  /home/user1/test/tools/aeroxctl.py --rainbow
  ```
* **Reactive Click Lighting**:
  ```bash
  /home/user1/test/tools/aeroxctl.py --reactive "#00FF00"
  ```

### 4. DPI Sensitivity Presets
Configure up to 5 DPI stages (from 100 to 18,000 CPI):
```bash
/home/user1/test/tools/aeroxctl.py --dpi 400 800 1200 2400 3200 --preset 1
```

### 5. Polling Rate (Hz)
Set USB reporting rate (1000, 500, 250, 125 Hz):
```bash
/home/user1/test/tools/aeroxctl.py --polling-rate 1000
```

### 6. Power Management
Set Sleep Timer (minutes) and Dim Timer (seconds):
```bash
/home/user1/test/tools/aeroxctl.py --sleep-timer 5 --dim-timer 30
```

### 7. Save to Onboard Memory
Persist current settings across reboots and different machines:
```bash
/home/user1/test/tools/aeroxctl.py --save
```

### 8. Graphical User Interface (GUI)
Launch the native SteelSeries GG / Engine control panel:
```bash
/home/user1/test/tools/aeroxgui.py
```

---

## Technical References
- [HID Protocol Reference](file:///home/user1/test/.agents/skills/steelseries-aerox-mouse/references/protocol.md)
- [Hardware & TrueMove Air Details](file:///home/user1/test/.agents/skills/steelseries-aerox-mouse/references/hardware.md)
