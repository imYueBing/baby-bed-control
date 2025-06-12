String inputBuffer = "";
bool commandComplete = false;

void setup()
{
  Serial.begin(9600);
}

void loop()
{
  // Read serial content
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

  // Command processing logic
  if (commandComplete)
  {
    inputBuffer.trim(); // Remove extra spaces and line breaks
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
      int hr = getHeartRate(); // Your existing heart rate function
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

    // Reset buffer
    inputBuffer = "";
    commandComplete = false;
  }
}

// The following functions are defined according to your project
void moveMotorUp()
{
  // Control motor upward
}

void moveMotorDown()
{
  // Control motor downward
}

void stopMotor()
{
  // Stop motor
}

int getHeartRate()
{
  // Return the read heart rate value
  return 75; // Example
}
