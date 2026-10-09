---
name: esp32-troubleshooting
description: Diagnostics and troubleshooting guide for ESP32 hardware and software issues. Use when encountering serial connection errors (permission denied, fatal error), boot loops, brownout detector resets, Guru Meditation core panics, watchdog timeouts, or stack overflows.
---

# ESP32 Troubleshooting & Diagnostics Skill

This skill diagnoses and fixes common hardware, Linux connection, and runtime panic issues on ESP32 microcontrollers.

---

## 1. Serial Port & Permission Issues on Linux

### Problem: `[Errno 13] Permission denied: '/dev/ttyUSB0'`
- **Root Cause**: On Arch Linux, serial ports belong to group `uucp` (on Ubuntu/Debian, `dialout`). The current user is not in this group.
- **Fix**:
  1. Add user to group:
     ```bash
     sudo usermod -a -G uucp $USER
     ```
  2. Reload group in active shell without logout:
     ```bash
     newgrp uucp
     ```
  3. Or install udev rules:
     ```bash
     sudo cp ~/.local/share/esp32-env/99-platformio-udev.rules /etc/udev/rules.d/
     sudo udevadm control --reload-rules && sudo udevadm trigger
     ```

### Problem: `Failed to connect to ESP32: Timed out waiting for packet header`
- **Cause**: The ESP32 is not in bootloader mode, or auto-reset timing failed.
- **Fix**:
  - Hold `BOOT` button, press `EN`, release `BOOT`, then flash.
  - Solder a 10µF capacitor between `EN` and `GND`.

---

## 2. Power & Brownout Resets

### Diagnostic: `Brownout detector was triggered`
- **Root Cause**: When the Wi-Fi or Bluetooth radio switches on, current draw spikes up to 400-500 mA for fractions of a millisecond. If the 3.3V rail dips below ~2.43V, the hardware brownout circuit resets the processor.
- **Fixes**:
  1. Use a high-quality, short USB cable (thin cables cause large voltage drop).
  2. Avoid unpowered USB hubs or long extension cords.
  3. Add a 100µF to 470µF electrolytic capacitor across 3.3V and GND pins on the breadboard.
  4. (Temporary test only) Disable brownout in code:
     ```cpp
     #include "soc/soc.h"
     #include "soc/rtc_cntl_reg.h"
     WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // Disable brownout detector
     ```

---

## 3. Guru Meditation Errors & Crashes

| Panic Reason | Root Cause | Solution |
| :--- | :--- | :--- |
| **LoadProhibited / StoreProhibited** | Dereferencing `NULL` or wild pointer | Check pointer initialization, bounds, and string null-terminators. |
| **Interrupt wdt timeout** | Long operations inside an ISR | Do not use `delay()`, `Serial.print()`, or heavy loops in ISR. Use semaphores. |
| **Task watchdog got triggered** | Task starved idle task or blocked forever | Add `vTaskDelay(1)` or call `yield()` in tight while loops. |
| **Stack overflow** | Task stack allocation too small | Increase stack size in `xTaskCreatePinnedToCore()` (e.g., from 2048 to 4096). |

---

## 4. References

- [Guru Meditation & Core Dump Crash Decoder](./references/panic_codes.md)
- [Hardware Signal & Power Integrity Debugging](./references/hardware_debugging.md)
