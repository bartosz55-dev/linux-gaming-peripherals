# ESP32 Partition Tables & Storage

ESP32 flash memory is divided according to a partition table (located at offset `0x8000`).

## Standard 4MB Partition Table (CSV Format)

```csv
# Name,   Type, SubType, Offset,  Size, Flags
nvs,      data, nvs,     0x9000,  0x5000,
otadata,  data, ota,     0xe000,  0x2000,
app0,     app,  ota_0,   0x10000, 0x140000,
app1,     app,  ota_1,   0x150000,0x140000,
spiffs,   data, spiffs,  0x290000,0x160000,
coredump, data, coredump,0x3f0000,0x10000,
```

## Huge App (No OTA) Partition Scheme
If your application exceeds 1.3MB (common when including BLE, Wi-Fi, and SSL):
```csv
# Name,   Type, SubType, Offset,  Size, Flags
nvs,      data, nvs,     0x9000,  0x5000,
otadata,  data, ota,     0xe000,  0x2000,
app0,     app,  ota_0,   0x10000, 0x300000,
spiffs,   data, spiffs,  0x310000,0xE0000,
coredump, data, coredump,0x3F0000,0x10000,
```

In `platformio.ini`:
```ini
board_build.partitions = huge_app.csv
```
