# Over-The-Air (OTA) Firmware Updates for ESP32

OTA allows firmware updates over Wi-Fi without needing a physical USB connection.

---

## ArduinoOTA Blueprint

```cpp
#include <WiFi.h>
#include <ESPmDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>

void setupOTA() {
    ArduinoOTA.setHostname("esp32-node1");
    // Optional password protection:
    // ArduinoOTA.setPassword("admin123");

    ArduinoOTA.onStart([]() {
        String type = (ArduinoOTA.getCommand() == U_FLASH) ? "sketch" : "filesystem";
        Serial.println("Start updating " + type);
    });
    ArduinoOTA.onEnd([]() {
        Serial.println("\nOTA Update Finished Successfully!");
    });
    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
        Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
    });
    ArduinoOTA.onError([](ota_error_t error) {
        Serial.printf("Error[%u]: ", error);
        if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
        else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
        else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
        else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
        else if (error == OTA_END_ERROR) Serial.println("End Failed");
    });

    ArduinoOTA.begin();
}

void setup() {
    Serial.begin(115200);
    // Connect to WiFi...
    setupOTA();
}

void loop() {
    ArduinoOTA.handle();
}
```

In `platformio.ini`:
```ini
upload_protocol = espota
upload_port = esp32-node1.local
; upload_flags = --auth=admin123
```
