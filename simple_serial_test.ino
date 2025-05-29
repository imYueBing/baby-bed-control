// simple_serial_test.ino

String command = ""; // 用于存储接收到的命令

void setup()
{
  Serial.begin(9600); // 初始化串口通信，波特率9600
  while (!Serial)
  {
    ; // 等待串口连接 (对于某些板子如Leonardo是必需的)
  }
  Serial.println("Arduino is ready. Send 'UP' or 'DOWN'.");
}

void loop()
{
  if (Serial.available() > 0)
  {
    char incomingChar = Serial.read();

    if (incomingChar == '\n')
    { // 命令以换行符结束
      // 处理接收到的命令
      if (command.equalsIgnoreCase("UP"))
      {
        Serial.println("CONFIRMED: UP");
        // 在这里可以添加实际控制电机上升的代码（如果需要）
        // digitalWrite(MOTOR_UP_PIN, HIGH);
      }
      else if (command.equalsIgnoreCase("DOWN"))
      {
        Serial.println("CONFIRMED: DOWN");
        // 在这里可以添加实际控制电机下降的代码（如果需要）
        // digitalWrite(MOTOR_DOWN_PIN, HIGH);
      }
      else if (command.equalsIgnoreCase("GET_HEART_RATE"))
      {
        Serial.println("HEART_RATE_DATA:75");
      }
      else if (command.length() > 0)
      { // 忽略空命令
        Serial.print("UNKNOWN_CMD:");
        Serial.println(command);
      }
      command = ""; // 清空命令字符串以备下次使用
    }
    else if (incomingChar != '\r')
    {                          // 忽略回车符，只处理换行前的字符
      command += incomingChar; // 将字符追加到命令字符串
    }
  }
}