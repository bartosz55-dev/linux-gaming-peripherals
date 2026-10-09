---
name: esp32-networking-iot
description: Wireless connectivity, network protocols, and IoT communication for ESP32. Use when implementing Wi-Fi (STA/AP), ESP-NOW mesh/peer communication, BLE/Bluetooth, MQTT, HTTP/HTTPS web servers, WebSockets, or OTA firmware updates.
---

# ESP32 Networking & IoT Skill

This skill provides protocols, code blueprints, and best practices for Wi-Fi, ESP-NOW, Bluetooth, MQTT, and Over-the-Air (OTA) updates on the ESP32 platform.

---

## 1. Quick Recipe Selection

| Requirement | Recommended Protocol / Library | Latency | Power Consumption |
| :--- | :--- | :--- | :--- |
| ESP-to-ESP peer communication without router | **ESP-NOW** | < 5 ms | Low |
| Smart home cloud/local messaging | **MQTT** (`PubSubClient` / `esp-mqtt`) | ~50-200 ms | Medium |
| Local web dashboard | **ESPAsyncWebServer** / `LittleFS` | Low | Medium |
| Mobile phone configuration & control | **BLE (Bluetooth Low Energy)** | Medium | Very Low |
| Remote firmware flashing | **ArduinoOTA** or **HTTP OTA** | N/A | High during transfer |

---

## 2. Robust Wi-Fi Auto-Reconnection

```cpp
#include <WiFi.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASS";

void WiFiStationConnected(WiFiEvent_t event, WiFiEventInfo_t info) {
    Serial.println("[Wi-Fi] Connected to AP successfully!");
}

void WiFiGotIP(WiFiEvent_t event, WiFiEventInfo_t info) {
    Serial.print("[Wi-Fi] IP address: ");
    Serial.println(WiFi.localIP());
}

void WiFiStationDisconnected(WiFiEvent_t event, WiFiEventInfo_t info) {
    Serial.println("[Wi-Fi] Connection lost! Reconnecting...");
    WiFi.begin(ssid, password);
}

void setup() {
    Serial.begin(115200);
    WiFi.disconnect(true);
    WiFi.onEvent(WiFiStationConnected, WiFiEvent_t::ARDUINO_EVENT_WIFI_STA_CONNECTED);
    WiFi.onEvent(WiFiGotIP, WiFiEvent_t::ARDUINO_EVENT_WIFI_STA_GOT_IP);
    WiFi.onEvent(WiFiStationDisconnected, WiFiEvent_t::ARDUINO_EVENT_WIFI_STA_DISCONNECTED);
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
}
```

---

## 3. Subdocuments & Guides

- [ESP-NOW Protocol Implementation Guide](./references/esp_now_protocol.md)
- [Wi-Fi & MQTT Architecture Patterns](./references/wifi_and_mqtt.md)
- [OTA (Over-The-Air) Firmware Updates Guide](./references/ota_updates.md)
