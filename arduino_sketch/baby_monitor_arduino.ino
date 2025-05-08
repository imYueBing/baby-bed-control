/*
 * 婴儿监控系统 - Arduino控制程序
 *
 * 实现床体升降控制和心率监测功能
 *
 * 硬件连接:
 *   - 步进电机驱动器 (床体升降)
 *     - STEP -> Arduino 3
 *     - DIR  -> Arduino 4
 *     - EN   -> Arduino 5
 *   - 光电传感器 (上限位)
 *     - OUT  -> Arduino 8
 *   - 光电传感器 (下限位)
 *     - OUT  -> Arduino 9
 *   - 心率传感器
 *     - OUT  -> Arduino A0
 *
 * 通信协议:
 *   - 使用JSON格式通过串行通信
 *   - 命令格式: {"command": "COMMAND_NAME"}
 *   - 响应格式: {"type": "RESPONSE_TYPE", "value": VALUE}
 */

#include <ArduinoJson.h>

// 步进电机引脚
#define STEP_PIN 3
#define DIR_PIN 4
#define ENABLE_PIN 5

// 限位开关引脚
#define LIMIT_SWITCH_TOP 8
#define LIMIT_SWITCH_BOTTOM 9

// 心率传感器引脚
#define HEART_RATE_PIN A0

// 步进电机参数
#define STEPS_PER_MM 100 // 每毫米的步数
#define MAX_HEIGHT 100   // 最大高度 (mm)
#define MIN_HEIGHT 0     // 最小高度 (mm)
#define MOTOR_SPEED 500  // 步进电机速度 (步/秒)

// 心率监测参数
#define HEART_RATE_SAMPLES 10    // 每次计算的样本数
#define HEART_RATE_THRESHOLD 550 // 心跳检测阈值
#define HEART_RATE_INTERVAL 20   // 采样间隔 (ms)

// 运行状态
bool isRunning = false;
bool isBedMoving = false;
bool isHeartRateMonitoring = false;
int currentHeight = 0;                 // 当前高度 (mm)
int targetHeight = 0;                  // 目标高度 (mm)
int currentHeartRate = 0;              // 当前心率 (BPM)
unsigned long lastHeartRateUpdate = 0; // 上次心率更新时间
unsigned long lastHeartBeat = 0;       // 上次心跳时间
int heartBeatCount = 0;                // 心跳计数
bool heartRateStream = false;          // 是否流式发送心率数据

// 串行通信缓冲区
const int BUFFER_SIZE = 256;
char inputBuffer[BUFFER_SIZE];
int bufferIndex = 0;

void setup()
{
  // 初始化串行通信
  Serial.begin(9600);

  // 初始化步进电机引脚
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  pinMode(ENABLE_PIN, OUTPUT);

  // 初始化限位开关引脚
  pinMode(LIMIT_SWITCH_TOP, INPUT_PULLUP);
  pinMode(LIMIT_SWITCH_BOTTOM, INPUT_PULLUP);

  // 初始化心率传感器引脚
  pinMode(HEART_RATE_PIN, INPUT);

  // 禁用电机驱动器
  disableMotor();

  // 完成初始化
  isRunning = true;

  // 发送系统就绪消息
  sendSystemStatus();
}

void loop()
{
  // 检查串行命令
  readSerialCommands();

  // 处理床体移动
  if (isBedMoving)
  {
    moveBed();
  }

  // 处理心率监测
  if (isHeartRateMonitoring)
  {
    monitorHeartRate();
  }

  // 短暂延迟
  delay(1);
}

// 从串行端口读取命令
void readSerialCommands()
{
  while (Serial.available() > 0)
  {
    char c = Serial.read();

    // 存储字符，直到行结束
    if (c == '\n')
    {
      // 终止字符串
      inputBuffer[bufferIndex] = '\0';

      // 处理命令
      processCommand(inputBuffer);

      // 重置缓冲区
      bufferIndex = 0;
    }
    else if (bufferIndex < BUFFER_SIZE - 1)
    {
      // 添加字符到缓冲区
      inputBuffer[bufferIndex++] = c;
    }
  }
}

// 处理接收到的命令
void processCommand(const char *command)
{
  // 创建JSON解析器
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, command);

  // 检查解析错误
  if (error)
  {
    sendError("Invalid JSON command");
    return;
  }

  // 提取命令名称
  const char *cmdName = doc["command"];

  if (!cmdName)
  {
    sendError("Missing command field");
    return;
  }

  // 处理不同的命令
  if (strcmp(cmdName, "BED_UP") == 0)
  {
    startBedUp();
  }
  else if (strcmp(cmdName, "BED_DOWN") == 0)
  {
    startBedDown();
  }
  else if (strcmp(cmdName, "BED_STOP") == 0)
  {
    stopBed();
  }
  else if (strcmp(cmdName, "BED_HEIGHT") == 0)
  {
    sendBedHeight();
  }
  else if (strcmp(cmdName, "HEART_RATE") == 0)
  {
    sendHeartRate();
  }
  else if (strcmp(cmdName, "HEART_RATE_SUBSCRIBE") == 0)
  {
    heartRateStream = true;
  }
  else if (strcmp(cmdName, "HEART_RATE_UNSUBSCRIBE") == 0)
  {
    heartRateStream = false;
  }
  else if (strcmp(cmdName, "SYSTEM_STATUS") == 0)
  {
    sendSystemStatus();
  }
  else
  {
    sendError("Unknown command");
  }
}

// 发送错误消息
void sendError(const char *message)
{
  StaticJsonDocument<256> doc;
  doc["type"] = "ERROR";
  doc["message"] = message;

  serializeJson(doc, Serial);
  Serial.println();
}

// 发送床体高度
void sendBedHeight()
{
  StaticJsonDocument<128> doc;
  doc["type"] = "BED_HEIGHT";
  doc["value"] = currentHeight;

  serializeJson(doc, Serial);
  Serial.println();
}

// 发送心率数据
void sendHeartRate()
{
  StaticJsonDocument<128> doc;
  doc["type"] = "HEART_RATE";
  doc["value"] = currentHeartRate;

  serializeJson(doc, Serial);
  Serial.println();
}

// 发送系统状态
void sendSystemStatus()
{
  StaticJsonDocument<256> doc;
  doc["type"] = "SYSTEM_STATUS";
  doc["bed_height"] = currentHeight;
  doc["heart_rate"] = currentHeartRate;
  doc["bed_moving"] = isBedMoving;
  doc["heart_rate_monitoring"] = isHeartRateMonitoring;

  serializeJson(doc, Serial);
  Serial.println();
}

// 启动床体上升
void startBedUp()
{
  // 检查上限位
  if (digitalRead(LIMIT_SWITCH_TOP) == LOW)
  {
    sendError("Bed already at top position");
    return;
  }

  // 设置方向和启用
  digitalWrite(DIR_PIN, HIGH); // 上升方向
  enableMotor();

  // 开始移动
  isBedMoving = true;

  // 发送确认
  StaticJsonDocument<128> doc;
  doc["type"] = "BED_CONTROL";
  doc["action"] = "UP";
  doc["status"] = "STARTED";

  serializeJson(doc, Serial);
  Serial.println();
}

// 启动床体下降
void startBedDown()
{
  // 检查下限位
  if (digitalRead(LIMIT_SWITCH_BOTTOM) == LOW)
  {
    sendError("Bed already at bottom position");
    return;
  }

  // 设置方向和启用
  digitalWrite(DIR_PIN, LOW); // 下降方向
  enableMotor();

  // 开始移动
  isBedMoving = true;

  // 发送确认
  StaticJsonDocument<128> doc;
  doc["type"] = "BED_CONTROL";
  doc["action"] = "DOWN";
  doc["status"] = "STARTED";

  serializeJson(doc, Serial);
  Serial.println();
}

// 停止床体移动
void stopBed()
{
  // 停止移动
  isBedMoving = false;
  disableMotor();

  // 发送确认
  StaticJsonDocument<128> doc;
  doc["type"] = "BED_CONTROL";
  doc["action"] = "STOP";
  doc["status"] = "STOPPED";

  serializeJson(doc, Serial);
  Serial.println();
}

// 移动床体
void moveBed()
{
  // 检查限位开关
  bool topLimitReached = (digitalRead(LIMIT_SWITCH_TOP) == LOW);
  bool bottomLimitReached = (digitalRead(LIMIT_SWITCH_BOTTOM) == LOW);

  if ((digitalRead(DIR_PIN) == HIGH && topLimitReached) ||
      (digitalRead(DIR_PIN) == LOW && bottomLimitReached))
  {
    // 到达限位，停止移动
    stopBed();
    return;
  }

  // 发送脉冲
  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(1000); // 控制速度
  digitalWrite(STEP_PIN, LOW);
  delayMicroseconds(1000); // 控制速度

  // 更新高度
  if (digitalRead(DIR_PIN) == HIGH)
  {
    // 上升
    currentHeight += 1.0 / STEPS_PER_MM;
    if (currentHeight > MAX_HEIGHT)
    {
      currentHeight = MAX_HEIGHT;
    }
  }
  else
  {
    // 下降
    currentHeight -= 1.0 / STEPS_PER_MM;
    if (currentHeight < MIN_HEIGHT)
    {
      currentHeight = MIN_HEIGHT;
    }
  }
}

// 启用电机
void enableMotor()
{
  digitalWrite(ENABLE_PIN, LOW); // 低电平启用
}

// 禁用电机
void disableMotor()
{
  digitalWrite(ENABLE_PIN, HIGH); // 高电平禁用
}

// 监测心率
void monitorHeartRate()
{
  // 确保已经初始化
  if (!isHeartRateMonitoring)
  {
    isHeartRateMonitoring = true;
    heartBeatCount = 0;
    lastHeartBeat = 0;
  }

  // 读取传感器值
  int sensorValue = analogRead(HEART_RATE_PIN);
  unsigned long currentTime = millis();

  // 检测心跳
  static int lastSensorValue = 0;
  static bool isPeak = false;

  // 检测上升沿越过阈值（心跳峰值）
  if (sensorValue > HEART_RATE_THRESHOLD && lastSensorValue <= HEART_RATE_THRESHOLD)
  {
    isPeak = true;
  }
  // 检测下降沿（心跳完成）
  else if (isPeak && sensorValue < HEART_RATE_THRESHOLD)
  {
    isPeak = false;

    // 计算两次心跳之间的时间
    if (lastHeartBeat > 0)
    {
      unsigned long timeBetweenBeats = currentTime - lastHeartBeat;

      // 心跳间隔在合理范围内
      if (timeBetweenBeats > 300 && timeBetweenBeats < 2000)
      {
        // 增加计数
        heartBeatCount++;

        // 计算心率 (BPM)
        if (heartBeatCount >= HEART_RATE_SAMPLES)
        {
          // 计算平均时间
          unsigned long totalTime = currentTime - lastHeartRateUpdate;
          float beatsPerSecond = (float)heartBeatCount / (totalTime / 1000.0);
          currentHeartRate = (int)(beatsPerSecond * 60.0);

          // 重置计数
          heartBeatCount = 0;
          lastHeartRateUpdate = currentTime;

          // 发送心率数据
          if (heartRateStream)
          {
            sendHeartRate();
          }
        }
      }
    }

    // 保存心跳时间
    lastHeartBeat = currentTime;
  }

  // 保存上一次传感器值
  lastSensorValue = sensorValue;
}