---
name: esp32-hardware-peripherals
description: Pinout, hardware constraints, FreeRTOS multitasking, and peripheral interfacing (GPIO, ADC, DAC, PWM, I2C, SPI, UART, interrupts) for ESP32 families. Use when designing circuits, assigning pins, reading sensors, using FreeRTOS tasks, or handling low-power deep sleep.
---

# ESP32 Hardware & Peripherals Skill

This skill guides pin selection, peripheral configuration, FreeRTOS real-time task design, and low-power modes across ESP32 chip variants.

---

## 1. Pin Usage Golden Rules (Classic ESP32 WROOM/WROVER)

- **Always Safe to Use**: GPIO 4, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33.
- **Input-Only Pins (No Internal Pull-up / Pull-down)**: GPIO 34, 35, 36 (VP), 39 (VN). Must use external resistors if used with buttons!
- **Forbidden Pins (Connected to internal SPI Flash)**: GPIO 6, 7, 8, 9, 10, 11. Using these will crash the MCU instantly.
- **Strapping Pins (Careful at boot)**:
  - GPIO 0 (Must be HIGH during normal boot)
  - GPIO 2 (Must be LOW or floating during boot)
  - GPIO 12 (Must be LOW during boot to maintain 3.3V flash)
  - GPIO 15 (Must be HIGH to enable serial boot output)
- **ADC2 Conflict**: ADC2 pins (GPIO 0, 2, 4, 12, 13, 14, 15, 25, 26, 27) cannot be read while Wi-Fi is active! Use ADC1 (GPIO 32, 33, 34, 35, 36, 39) when Wi-Fi is running.

---

## 2. Standard Peripheral Interfaces

### I2C (Inter-Integrated Circuit)
- Default Pins: SDA = GPIO 21, SCL = GPIO 22.
- Any GPIO can be configured as I2C:
  ```cpp
  Wire.begin(customSDA, customSCL, 400000); // 400kHz Fast Mode
  ```
- Pull-ups: Always include 4.7kΩ pull-up resistors to 3.3V on SDA/SCL lines.

### SPI (Serial Peripheral Interface)
- VSPI (Default): MOSI = 23, MISO = 19, SCK = 18, CS = 5.
- HSPI: MOSI = 13, MISO = 12, SCK = 14, CS = 15.

### PWM / LEDC (LED Control)
- ESP32 does not use traditional `analogWrite()`. It uses hardware LEDC channels:
  ```cpp
  ledcAttach(pin, frequency, resolution); // e.g. 5000Hz, 8-bit (0-255)
  ledcWrite(pin, dutyCycle);
  ```

---

## 3. FreeRTOS Multitasking on Dual-Core ESP32

The ESP32 runs FreeRTOS with two Xtensa LX6/LX7 cores (Core 0: Protocol CPU, Core 1: Application CPU):

```cpp
TaskHandle_t SensorTaskHandle = NULL;

void SensorTask(void *pvParameters) {
    for (;;) {
        // Read sensor
        vTaskDelay(pdMS_TO_TICKS(100)); // Non-blocking delay
    }
}

void setup() {
    // Pin task to Core 1, leaving Core 0 for Wi-Fi / Bluetooth
    xTaskCreatePinnedToCore(
        SensorTask,          // Task function
        "SensorTask",        // Name
        4096,                // Stack size in bytes/words
        NULL,                // Parameters
        1,                   // Priority (higher = more urgent)
        &SensorTaskHandle,   // Task handle
        1                    // Core ID (0 or 1)
    );
}
```

---

## 4. References

- [Comprehensive Pinout Cheatsheet](./references/pinout_cheatsheet.md)
- [FreeRTOS Architecture & Synchronization Patterns](./references/freertos_patterns.md)
- [Low-Power Deep Sleep & Wakeup Triggers](./references/sleep_modes.md)
