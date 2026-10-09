# ESP32 Hardware Signal & Power Integrity Debugging

## 1. Power Supply Requirements
- Minimum Current: The power supply must deliver at least **500 mA** continuous current at 3.3V (or 5V into the on-board AMS1117/ME6211 LDO).
- Typical Wi-Fi Spikes: Current draw briefly peaks at 380-450 mA during 802.11b/g/n calibration bursts.
- Decoupling: Always place a 100nF ceramic capacitor as close as possible to the ESP32 VDD pin, along with a bulk 10µF - 100µF tantalum/electrolytic capacitor.

## 2. Pin Level Restrictions
- Logic Level: **Strictly 3.3V CMOS**. The ESP32 is NOT 5V tolerant on its GPIO pins.
- 5V Interfacing:
  - 5V to ESP32: Use a resistor voltage divider (e.g. 1kΩ / 2kΩ) or bi-directional level shifter (BSS138).
  - ESP32 to 5V: 3.3V HIGH is typically recognized as HIGH by TTL inputs (threshold ~2.0V), but for 5V CMOS inputs (threshold ~3.5V), a level shifter is required.

## 3. High-Speed Bus Debugging (I2C & SPI)
- I2C Bus Hanging: If an I2C slave locks the SDA line LOW, toggle SCL 9 times manually to release the bus before calling `Wire.begin()`.
- Pull-Up Resistors: External 4.7kΩ pull-up resistors are recommended for 100kHz, 2.2kΩ for 400kHz. Do not rely solely on internal pull-ups for high-speed I2C buses.
