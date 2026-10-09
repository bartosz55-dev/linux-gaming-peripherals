# ESP-NOW Peer-to-Peer Protocol Guide

ESP-NOW is a connectionless Wi-Fi communication protocol developed by Espressif. It allows up to 250-byte packets to be exchanged directly between ESP devices in under 5ms without needing a Wi-Fi router.

---

## 1. Getting MAC Address of Board
Each board has a factory Wi-Fi MAC address:
```cpp
#include <WiFi.h>
void setup() {
    Serial.begin(115200);
    WiFi.mode(WIFI_MODE_STA);
    Serial.print("Board MAC Address: ");
    Serial.println(WiFi.macAddress());
}
void loop() {}
```

---

## 2. Sender Blueprint

```cpp
#include <esp_now.h>
#include <WiFi.h>

// Replace with Receiver's MAC Address:
uint8_t receiverMAC[] = {0x24, 0x0A, 0xC4, 0xXX, 0xXX, 0xXX};

typedef struct struct_message {
    char title[32];
    float value;
} struct_message;

struct_message myData;
esp_now_peer_info_t peerInfo;

void onDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    Serial.print("\r\nDelivery Status: ");
    Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Success" : "Fail");
}

void setup() {
    Serial.begin(115200);
    WiFi.mode(WIFI_STA);

    if (esp_now_init() != ESP_OK) {
        Serial.println("Error initializing ESP-NOW");
        return;
    }

    esp_now_register_send_cb(onDataSent);

    // Register peer
    memcpy(peerInfo.peer_addr, receiverMAC, 6);
    peerInfo.channel = 0;  
    peerInfo.encrypt = false;

    if (esp_now_add_peer(&peerInfo) != ESP_OK) {
        Serial.println("Failed to add peer");
        return;
    }
}

void loop() {
    strcpy(myData.title, "Temperature");
    myData.value = 23.4;
    esp_now_send(receiverMAC, (uint8_t *) &myData, sizeof(myData));
    delay(2000);
}
```

---

## 3. Broadcast Mode
To broadcast to ALL listening ESP devices simultaneously, set the MAC address to:
`uint8_t broadcastAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};`
