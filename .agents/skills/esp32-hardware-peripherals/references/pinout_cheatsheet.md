# ESP32 Pinout Cheatsheet & Modern Variants

## 1. Classic ESP32 (30-pin & 38-pin DevKit)

| Pin | Native Function | ADC | Touch | Safe for Output? | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| GPIO 0 | Strapping / BOOT | ADC2_CH1 | TOUCH1 | ⚠️ Caution | Pulled UP internally. Pulled LOW to enter bootloader. |
| GPIO 1 | UART0 TX | - | - | ⚠️ Serial TX | Debug output. |
| GPIO 2 | Strapping | ADC2_CH2 | TOUCH2 | ⚠️ Caution | Connected to on-board blue LED on many DevKits. |
| GPIO 3 | UART0 RX | - | - | ⚠️ Serial RX | Serial programming input. |
| GPIO 4 | General IO | ADC2_CH0 | TOUCH0 | ✅ Safe | General purpose. |
| GPIO 5 | VSPI CS | - | - | ✅ Safe | Strapping pin on some variants. |
| GPIO 12| Strapping | ADC2_CH5 | TOUCH5 | ⚠️ Caution | MTDI: Must NOT be pulled HIGH at boot (sets 1.8V flash). |
| GPIO 13| General IO / HSPI | ADC2_CH4 | TOUCH4 | ✅ Safe | General purpose. |
| GPIO 14| HSPI CLK | ADC2_CH6 | TOUCH6 | ✅ Safe | General purpose. |
| GPIO 15| Strapping | ADC2_CH3 | TOUCH3 | ⚠️ Caution | MTDO: Serial boot output enable. |
| GPIO 16| UART2 RX | - | - | ✅ Safe | Free to use (Note: Used by PSRAM on WROVER!). |
| GPIO 17| UART2 TX | - | - | ✅ Safe | Free to use (Note: Used by PSRAM on WROVER!). |
| GPIO 18| VSPI SCK | - | - | ✅ Safe | General purpose. |
| GPIO 19| VSPI MISO | - | - | ✅ Safe | General purpose. |
| GPIO 21| I2C SDA | - | - | ✅ Safe | Wire default SDA. |
| GPIO 22| I2C SCL | - | - | ✅ Safe | Wire default SCL. |
| GPIO 23| VSPI MOSI | - | - | ✅ Safe | General purpose. |
| GPIO 25| DAC1 | ADC2_CH8 | - | ✅ Safe | Real analog DAC output. |
| GPIO 26| DAC2 | ADC2_CH9 | - | ✅ Safe | Real analog DAC output. |
| GPIO 27| General IO | ADC2_CH7 | TOUCH7 | ✅ Safe | General purpose. |
| GPIO 32| 32kHz Crystal / IO| ADC1_CH4 | TOUCH9 | ✅ Safe | Works with Wi-Fi! |
| GPIO 33| 32kHz Crystal / IO| ADC1_CH5 | TOUCH8 | ✅ Safe | Works with Wi-Fi! |
| GPIO 34| Input Only | ADC1_CH6 | - | ❌ Input Only | No internal pull-up! External pull-up required. |
| GPIO 35| Input Only | ADC1_CH7 | - | ❌ Input Only | No internal pull-up! External pull-up required. |
| GPIO 36| SENSOR_VP / In | ADC1_CH0 | - | ❌ Input Only | Low noise analog input. |
| GPIO 39| SENSOR_VN / In | ADC1_CH3 | - | ❌ Input Only | Low noise analog input. |

---

## 2. ESP32-S3 Differences
- Native USB OTG / JTAG built-in on GPIO 19 (D-) and GPIO 20 (D+).
- Dual-core Xtensa LX7 with vector instructions (AI acceleration).
- No DAC on S3! Use external I2S DAC (e.g. MAX98357A / PCM5102).

## 3. ESP32-C3 / C6 Differences
- Single-core RISC-V 32-bit architecture.
- Pin-compatible with ESP8266 form factor in some compact modules.
- C6 adds Wi-Fi 6, 802.15.4 (Zigbee & Thread / Matter).
