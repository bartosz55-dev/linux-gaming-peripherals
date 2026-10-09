# ESP32 Panic Codes & Stack Trace Analysis

When an unhandled exception occurs, the ESP32 dumps register contents to UART0:

```text
Guru Meditation Error: Core 1 panic'ed (LoadProhibited). Exception was unhandled.
Core 1 register dump:
PC      : 0x400d1234  PS      : 0x00060030  A0      : 0x800d1456  A1      : 0x3ffb1f20  
A2      : 0x00000000  A3      : 0x3ffb1f40  A4      : 0x00000010  A5      : 0x00000000  
...
Backtrace:0x400d1234:0x3ffb1f20 0x400d1456:0x3ffb1f50 0x400d1999:0x3ffb1fb0
```

## Decoding the Backtrace with `addr2line`

Using the project's compiled ELF file:
```bash
# Xtensa ESP32 toolchain addr2line
~/.platformio/packages/toolchain-xtensa-esp32/bin/xtensa-esp32-elf-addr2line -pfia -e .pio/build/esp32dev/firmware.elf 0x400d1234 0x400d1456
```
This prints the exact source file and line number causing the crash!

In PlatformIO, you can enable the built-in exception decoder in `platformio.ini`:
```ini
monitor_filters = esp32_exception_decoder
```
This automatically translates backtraces in real-time inside `pio device monitor`!
