# SteelSeries Aerox 3 HID Protocol Specification

## Overview
Communication with SteelSeries Aerox 3 Wireless mice is done via standard USB HID Output Reports.

- **Interface**: Interface 3 (`Usage Page: 0xFFC0`, `Usage: 0x0001`)
- **Report Format**: Output Report (`0x00` Report ID followed by command bytes).
- **Wireless Modification**: In 2.4 GHz wireless mode, bit 6 is OR-ed to the first opcode (`opcode | 0x40`).

---

## Command Table

| Opcode (Wired) | Opcode (Wireless) | Description | Payload Structure |
|---|---|---|---|
| `0x92` | `0xD2` | Read Battery Status | None. Response 64 bytes. `data[1] & 0x80`: charging; `((data[1] & 0x7F) - 1) * 5`: % |
| `0x21` | `0x61` | Set RGB Zone Color | `[0x01, zone, R, G, B]`. Zone: 0 (Top), 1 (Middle), 2 (Bottom) |
| `0x22` | `0x62` | Rainbow Wave Effect | `[0xFF]` |
| `0x26` | `0x66` | Reactive Click Color | `[R, G, B]` or `[0x00]` for disable |
| `0x2D` | `0x6D` | Set DPI Stages | `[count, selected_idx, b0, b1, ...]` mapped via TrueMove Air table |
| `0x2B` | `0x6B` | Set Polling Rate | `[rate_code]`. 1000Hz: `0x00`, 500Hz: `0x01`, 250Hz: `0x02`, 125Hz: `0x03` |
| `0x29` | `0x69` | Set Sleep Timer | `[b0, b1, b2]` = `minutes * 60000` (little-endian uint24) |
| `0x23` | `0x63` | Set Dim Timer | `[0x0F, 0x01, 0x00, 0x00, b0, b1, b2]` = `seconds * 1000` (little-endian uint24) |
| `0x11` | `0x51` | Save to Onboard Memory | `[0x00]` |
