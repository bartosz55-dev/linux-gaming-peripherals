# ESP32 Bootloader & Flashing Deep Dive

## Boot Strapping Pins
ESP32 samples specific pins at power-up (rising edge of EN / RST) to configure boot mode:

| Pin | Function | Flash Boot Mode (Normal) | UART Download Boot Mode |
| :--- | :--- | :--- | :--- |
| **GPIO0** | Boot mode select | **HIGH** (Pull-up) | **LOW** (Pull to GND) |
| **GPIO2** | Boot mode select | **LOW** or Floating | **LOW** or Floating |
| **GPIO12 (MTDI)** | Flash Voltage selection | **LOW** (3.3V flash) | **LOW** (Caution: HIGH forces 1.8V flash - can brick flash!) |
| **GPIO15 (MTDO)** | ROM messages output | **HIGH** (UART0 output enabled)| Don't care |

> [!WARNING]
> Never connect pull-up resistors or high-impedance loads that hold GPIO12 HIGH during reset on 3.3V flash modules (like standard ESP32-WROOM-32), or flash memory will not be readable.

## Flash Modes
- **QIO (Quad I/O)**: Fastest, uses 4 data lines for both command/address and data.
- **QOUT (Quad Output)**: 4 lines for data, standard lines for address.
- **DIO (Dual I/O)**: Compatible with almost all boards and clones. Standard default.
- **DOUT (Dual Output)**: Safest fallback mode if flash errors occur during boot.

When running `esptool.py`, default to `--flash_mode dio` and `--flash_freq 40m` if encountering SPI flash CRC errors.
