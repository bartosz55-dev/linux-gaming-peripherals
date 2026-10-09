# ESP32 Sleep Modes & Low-Power Design

The ESP32 supports multiple sleep states:
- **Active Mode**: ~100-240 mA (Wi-Fi + BT active).
- **Light Sleep**: ~0.8 mA (CPU clock-gated, RAM retained, fast wake ~1ms).
- **Deep Sleep**: ~10-15 µA (Main CPU powered down, ULP coprocessor & RTC memory retained).
- **Hibernation**: ~5 µA (Only RTC timer active).

---

## Retaining Variables in Deep Sleep

Variables stored in normal SRAM are lost on wake. To retain state across deep sleep resets, place them in RTC memory:

```cpp
RTC_DATA_ATTR int bootCount = 0;

void setup() {
    Serial.begin(115200);
    bootCount++;
    Serial.printf("Boot count: %d\n", bootCount);

    // Sleep for 60 seconds (in microseconds)
    esp_sleep_enable_timer_wakeup(60ULL * 1000000ULL);

    // External GPIO wakeup (e.g. Button on GPIO 33)
    esp_sleep_enable_ext0_wakeup(GPIO_NUM_33, 0); // Wake on LOW

    Serial.println("Going to sleep now...");
    esp_deep_sleep_start();
}

void loop() {}
```

## Wakeup Causes Identification

```cpp
esp_sleep_wakeup_cause_t wakeup_reason = esp_sleep_get_wakeup_cause();
switch(wakeup_reason) {
    case ESP_SLEEP_WAKEUP_EXT0:     Serial.println("Wakeup by RTC_IO (EXT0)"); break;
    case ESP_SLEEP_WAKEUP_EXT1:     Serial.println("Wakeup by RTC_CNTL (EXT1)"); break;
    case ESP_SLEEP_WAKEUP_TIMER:    Serial.println("Wakeup by Timer"); break;
    case ESP_SLEEP_WAKEUP_TOUCHPAD: Serial.println("Wakeup by Touchpad"); break;
    case ESP_SLEEP_WAKEUP_ULP:      Serial.println("Wakeup by ULP"); break;
    default:                        Serial.println("Normal Power-on reset"); break;
}
```
