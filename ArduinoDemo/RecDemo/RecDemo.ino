#include <ArduinoJson.h>

#define LED_PIN 13  // LED连接的引脚

void setup() {
  // 初始化串口通讯，设置波特率为115200
  Serial.begin(115200);
  // 设定LED_PIN为OUTPUT模式
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  if(Serial.available()){
    // 设定缓存区
    StaticJsonDocument<200> doc;

    // 将接收到的串口数据解析为Json
    DeserializationError error = deserializeJson(doc, Serial);

    // 如果解析出错，打印错误
    if (error) {
      Serial.print(F("deserializeJson() failed: "));
      Serial.println(error.f_str());
      return;
    }

    // 从Json中取得"test"字段的值
    const char* text = doc["text"];

    // 根据text的值来控制LED
    if (strcmp(text, "open") == 0) {
      digitalWrite(LED_PIN, HIGH);   // 打开LED
      Serial.println("LED is turned on");
    }
    else if (strcmp(text, "close") == 0) {
      digitalWrite(LED_PIN, LOW);    // 关闭LED
      Serial.println("LED is turned off");
    }
  }
}
