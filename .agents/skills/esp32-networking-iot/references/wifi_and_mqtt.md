# MQTT & Wi-Fi Architecture for ESP32

## Reliable MQTT Connection Loop (PubSubClient)

```cpp
#include <WiFi.h>
#include <PubSubClient.h>

const char* mqtt_server = "192.168.1.100";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastReconnectAttempt = 0;

void callback(char* topic, byte* payload, unsigned int length) {
    Serial.printf("Message arrived [%s]: ", topic);
    for (int i = 0; i < length; i++) {
        Serial.print((char)payload[i]);
    }
    Serial.println();
}

boolean reconnect() {
    if (client.connect("ESP32_Client_01")) {
        Serial.println("[MQTT] Connected");
        client.subscribe("home/esp32/commands");
        client.publish("home/esp32/status", "online", true);
    }
    return client.connected();
}

void setup() {
    client.setServer(mqtt_server, mqtt_port);
    client.setCallback(callback);
}

void loop() {
    if (!client.connected()) {
        unsigned long now = millis();
        // Non-blocking reconnect attempt every 5 seconds
        if (now - lastReconnectAttempt > 5000) {
            lastReconnectAttempt = now;
            if (reconnect()) {
                lastReconnectAttempt = 0;
            }
        }
    } else {
        client.loop();
    }
}
```
