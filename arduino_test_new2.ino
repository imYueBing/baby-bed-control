/*
 * 婴儿床控制和心率监测 Arduino 代码
 *
 * 此代码实现了与树莓派通信的功能，包括：
 * 1. 床体升降控制
 * 2. 心率监测和数据传输
 *
 * 通信协议
 * - 接收命令：UP, DOWN, STOP, GET_HEART_RATE, GET_STATUS
 * - 发送响应：CONFIRMED:<命令>, HEART_RATE_DATA:<值>, UNKNOWN_CMD:<命令>
 */

#include <Arduino.h> // 添加 Arduino 库引用

// 引脚定义
const int BED_UP_PIN = 5;      // 床体上升控制引脚
const int BED_DOWN_PIN = 6;    // 床体下降控制引脚
const int HEART_RATE_PIN = A0; // 心率传感器模拟输入引脚

// 状态变量
int currentHeartRate = 0;
unsigned long lastHeartRateUpdate = 0;
const unsigned long HEART_RATE_UPDATE_INTERVAL = 1000; // 心率更新间隔（毫秒）

// 缓冲区
String inputBuffer = "";
boolean commandComplete = false;

void setup()
{
  // 初始化串口通信
  Serial.begin(9600);

  // 等待串口连接（仅适用于某些 Arduino 板）
  while (!Serial && millis() < 3000)
  {
    ; // 等待串口连接，但最多等待 3 秒
  }

  // 配置引脚
  pinMode(BED_UP_PIN, OUTPUT);
  pinMode(BED_DOWN_PIN, OUTPUT);
  pinMode(HEART_RATE_PIN, INPUT);

  // 初始状态：床体停止
  digitalWrite(BED_UP_PIN, LOW);
  digitalWrite(BED_DOWN_PIN, LOW);

  // 发送就绪消息
  Serial.println("READY");
}

void loop()
{
  // 读取串口命令
  readSerialCommand();

  // 处理完整命令
  if (commandComplete)
  {
    processCommand(inputBuffer);
    inputBuffer = "";
    commandComplete = false;
  }

  // 定期更新心率数据（模拟或实际读取）
  updateHeartRate();
}

// 读取串口命令
void readSerialCommand()
{
  while (Serial.available() > 0)
  {
    char inChar = (char)Serial.read();

    // 调试：打印接收到的字符
    Serial.print("Received: ");
    Serial.println(inChar);

    // 如果收到换行符或回车符，表示命令结束
    if (inChar == '\n' || inChar == '\r')
    {
      commandComplete = true;
      Serial.println("Command complete");
      Serial.print("Complete command received: '");
      Serial.print(inputBuffer);
      Serial.println("'");
      break;
    }
    else
    {
      // 添加字符到缓冲区
      inputBuffer += inChar;
      Serial.print("Current buffer: '");
      Serial.print(inputBuffer);
      Serial.println("'");

      // 检查是否已经有完整命令
      // 如果缓冲区匹配特定命令，立即处理
      if (inputBuffer == "UP" || inputBuffer == "DOWN" ||
          inputBuffer == "STOP" || inputBuffer == "GET_HEART_RATE" ||
          inputBuffer == "GET_STATUS")
      {
        Serial.println("命令匹配，无需等待换行符");
        commandComplete = true;
        break;
      }
    }
  }
}

// 处理命令
void processCommand(String command)
{
  command.trim(); // 去除可能的空格

  Serial.print("Processing command: ");
  Serial.println(command);

  if (command == "UP")
  {
    // 升高床
    bedUp();
    Serial.println("CONFIRMED:UP");
  }
  else if (command == "DOWN")
  {
    // 降低床
    bedDown();
    Serial.println("CONFIRMED:DOWN");
  }
  else if (command == "STOP")
  {
    // 停止床体移动
    bedStop();
    Serial.println("CONFIRMED:STOP");
  }
  else if (command == "GET_HEART_RATE")
  {
    // 发送心率数据
    sendHeartRate();
  }
  else if (command == "GET_STATUS")
  {
    // 发送系统状态
    sendSystemStatus();
  }
  else
  {
    // 未知命令
    Serial.print("UNKNOWN_CMD:");
    Serial.println(command);
  }
}

// 升高床
void bedUp()
{
  digitalWrite(BED_DOWN_PIN, LOW); // 确保下降引脚关闭
  digitalWrite(BED_UP_PIN, HIGH);  // 激活上升引脚
}

// 降低床
void bedDown()
{
  digitalWrite(BED_UP_PIN, LOW);    // 确保上升引脚关闭
  digitalWrite(BED_DOWN_PIN, HIGH); // 激活下降引脚
}

// 停止床体移动
void bedStop()
{
  digitalWrite(BED_UP_PIN, LOW);
  digitalWrite(BED_DOWN_PIN, LOW);
}

// 更新心率数据
void updateHeartRate()
{
  unsigned long currentTime = millis();

  // 每隔一段时间更新心率
  if (currentTime - lastHeartRateUpdate >= HEART_RATE_UPDATE_INTERVAL)
  {
    lastHeartRateUpdate = currentTime;

    // 这里是实际读取心率传感器的代码
    // 在本例中，我们使用模拟引脚读取值并进行简单处理
    // 实际应用中，您需要根据您的心率传感器类型调整这部分代码
    int sensorValue = analogRead(HEART_RATE_PIN);

    // 简单的心率计算示例（这只是一个示例，实际计算取决于您的传感器）
    // 在实际应用中，您可能需要更复杂的算法来处理心率信号
    currentHeartRate = map(sensorValue, 0, 1023, 60, 100);

    // 如果您使用的是数字心率传感器（如MAX30102），则需要使用相应的库
    // 例如：currentHeartRate = heartRateSensor.getHeartRate();
  }
}

// 发送心率数据
void sendHeartRate()
{
  Serial.print("HEART_RATE_DATA:");
  Serial.println(currentHeartRate);
}

// 发送系统状态
void sendSystemStatus()
{
  // 发送床体状态和心率
  Serial.print("STATUS:BED_UP=");
  Serial.print(digitalRead(BED_UP_PIN));
  Serial.print(",BED_DOWN=");
  Serial.print(digitalRead(BED_DOWN_PIN));
  Serial.print(",HEART_RATE=");
  Serial.println(currentHeartRate);
}