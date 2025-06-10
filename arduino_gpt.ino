  String inputBuffer = "";
  bool commandComplete = false;

  void setup()
  {
    Serial.begin(9600);
  }

  void loop()
  {
    // 读取串口内容
    while (Serial.available() > 0)
    {
      char inChar = (char)Serial.read();
      if (inChar == '\n' || inChar == '\r')
      {
        commandComplete = true;
      }
      else
      {
        inputBuffer += inChar;
      }
    }

    // 命令处理逻辑
    if (commandComplete)
    {
      inputBuffer.trim(); // 去除多余空格和换行符
      Serial.print("[RECV] ");
      Serial.println(inputBuffer);

      if (inputBuffer == "UP")
      {
        moveMotorUp();
        Serial.println("[ACK] UP");
      }
      else if (inputBuffer == "DOWN")
      {
        moveMotorDown();
        Serial.println("[ACK] DOWN");
      }
      else if (inputBuffer == "STOP")
      {
        stopMotor();
        Serial.println("[ACK] STOP");
      }
      else if (inputBuffer == "GET_HEART_RATE")
      {
        int hr = getHeartRate(); // 你已有的心率函数
        Serial.print("[HEART] ");
        Serial.println(hr);
      }
      else if (inputBuffer == "GET_STATUS")
      {
        Serial.println("[STATUS] OK");
      }
      else
      {
        Serial.println("[ERROR] UNKNOWN_COMMAND");
      }

      // 重置缓冲区
      inputBuffer = "";
      commandComplete = false;
    }
  }

  // 以下函数根据你的项目定义
  void moveMotorUp()
  {
    // 모터 상향 제어

  }

  void moveMotorDown()
  {
    // 控制电机向下
  }

  void stopMotor()
  {
    // 停止电机
  }

  int getHeartRate()
  {
    // 返回读取的心率值
    return 75; // 示例
  }
