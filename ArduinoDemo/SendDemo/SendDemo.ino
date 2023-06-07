#include <ArduinoJson.h>

// 准备 JSON 文档
StaticJsonDocument<100> doc;

void setup() {
  Serial.begin(115200);
}

void loop() {
  int x = 0;
  int y = 0;
  int head = 0;
  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 200; j++) { // 在2s内向某个方向走50个单位，每0.01s走一个单位
      switch (head) {
        case 0: // Up
          y++;
          break;
        case 90: // Right
          x++;
          break;
        case 180: // Down
          y--;
          break;
        case 270: // Left
          x--;
          break;
      }

      // 组装 JSON
      doc["x"] = x;
      doc["y"] = y;
      doc["head"] = head;

      // 输出 JSON
      serializeJson(doc, Serial);
      Serial.println();

      // 0.01秒后再次运行
      delay(10);
    }
    // 每2s后改变方向
    head = (head + 90) % 360;
  }
}
