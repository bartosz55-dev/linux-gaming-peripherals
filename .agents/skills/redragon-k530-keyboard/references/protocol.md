# Redragon K530 / Sonix SN32F248B USB HID Protocol

## Overview
The Redragon K530 Draconic communicates proprietary control messages through USB HID interface 1 using vendor-defined 64-byte packets with Report ID `0x04`.

- **Vendor ID**: `0x0C45`
- **Product ID**: `0x5004`
- **Usage Page**: `0xFF1C`
- **Usage**: `0x0092`
- **Report ID**: `0x04`
- **Packet Size**: 64 bytes

## Checksum Algorithm
For packets requiring validation (commands `0x06` and `0x11`), a 16-bit sum is calculated across bytes `0x03` through `0x3F`:

```python
checksum = sum(packet[3:64]) & 0xFFFF
packet[1] = checksum & 0xFF        # Low byte
packet[2] = (checksum >> 8) & 0xFF # High byte
```

## Command Opcodes

### 1. `COMMAND_BEGIN` (0x01)
Initializes communication session before sending configuration packets.
- `packet[0] = 0x04` (Report ID)
- `packet[1] = 0x01`
- `packet[2] = 0x00`
- `packet[3] = 0x01`
- Rest of packet padded with `0x00`.

### 2. `COMMAND_END` (0x02)
Finalizes communication session and saves changes to keyboard volatile memory.
- `packet[0] = 0x04` (Report ID)
- `packet[1] = 0x02`
- `packet[2] = 0x00`
- `packet[3] = 0x02`
- Rest of packet padded with `0x00`.

### 3. `COMMAND_SET_PARAMETER` (0x06)
Sets global parameters like lighting mode, brightness, speed, and color.
- `packet[0] = 0x04` (Report ID)
- `packet[3] = 0x06`
- `packet[4] = 0x08` (Length of parameter data payload)
- `packet[5] = 0x00` (Parameter ID: 0 = Lighting Configuration)
- Data payload (bytes 8–15):
  - `packet[8]`: Mode ID (`0x01`–`0x14`)
  - `packet[9]`: Brightness (`0` to `4`)
  - `packet[10]`: Speed (`0` = fastest, `10` = slowest)
  - `packet[11]`: Direction (`0` = left/normal, `1` = right)
  - `packet[12]`: Random / Rainbow flag (`0` = single color, `1` = rainbow cycle)
  - `packet[13]`: Red (`0`–`255`)
  - `packet[14]`: Green (`0`–`255`)
  - `packet[15]`: Blue (`0`–`255`)
- Followed by checksum calculation across bytes 3–63 into bytes 1–2.

### 4. `COMMAND_WRITE_CUSTOM_COLOR_DATA` (0x11)
Transfers per-key RGB matrices (up to 54 bytes per packet slice).
- `packet[0] = 0x04`
- `packet[3] = 0x11`
- `packet[4] = slice_size`
- `packet[5] = offset_lo`
- `packet[6] = offset_hi`
- `packet[8...] = rgb_data`
