# FreeRTOS Synchronization Patterns on ESP32

## 1. Inter-Task Communication with Queues

Queues provide thread-safe FIFO communication between tasks and ISRs:

```cpp
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>

QueueHandle_t sensorQueue;

struct SensorData {
    float temperature;
    float humidity;
};

void producerTask(void *pvParam) {
    SensorData data;
    for (;;) {
        data.temperature = 24.5;
        data.humidity = 60.0;
        // Send data with a 10-tick timeout
        xQueueSend(sensorQueue, &data, pdMS_TO_TICKS(10));
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

void consumerTask(void *pvParam) {
    SensorData receivedData;
    for (;;) {
        if (xQueueReceive(sensorQueue, &receivedData, portMAX_DELAY) == pdPASS) {
            Serial.printf("T: %.1f C, H: %.1f %%\n", receivedData.temperature, receivedData.humidity);
        }
    }
}

void setup() {
    sensorQueue = xQueueCreate(10, sizeof(SensorData));
    xTaskCreatePinnedToCore(producerTask, "Producer", 2048, NULL, 1, NULL, 1);
    xTaskCreatePinnedToCore(consumerTask, "Consumer", 2048, NULL, 1, NULL, 0);
}
```

## 2. Mutual Exclusion with Mutexes

Protect shared resources (e.g. I2C bus or display buffer):

```cpp
SemaphoreHandle_t i2cMutex = xSemaphoreCreateMutex();

void accessBus() {
    if (xSemaphoreTake(i2cMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
        // Safe to read/write I2C bus
        xSemaphoreGive(i2cMutex);
    }
}
```

## 3. Interrupts to Task (Binary Semaphore from ISR)

```cpp
SemaphoreHandle_t buttonSem;

void IRAM_ATTR buttonISR() {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xSemaphoreGiveFromISR(buttonSem, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

void buttonTask(void *param) {
    for (;;) {
        if (xSemaphoreTake(buttonSem, portMAX_DELAY) == pdTRUE) {
            // Handle debounce and button action
        }
    }
}
```
