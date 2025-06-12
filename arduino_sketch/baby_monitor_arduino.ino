/*
 * Baby Monitoring System - Arduino Control Program
 *
 * Implements bed lifting control and heart rate monitoring functionality
 *
 * Hardware Connections:
 *   - Stepper Motor Driver (Bed Lifting)
 *     - STEP -> Arduino 3
 *     - DIR  -> Arduino 4
 *     - EN   -> Arduino 5
 *   - Optical Sensor (Upper Limit)
 *     - OUT  -> Arduino 8
 *   - Optical Sensor (Lower Limit)
 *     - OUT  -> Arduino 9
 *   - Heart Rate Sensor
 *     - OUT  -> Arduino A0
 *
 * Communication Protocol:
 *   - Using JSON format via serial communication
 *   - Command Format: {"command": "COMMAND_NAME"}
 *   - Response Format: {"type": "RESPONSE_TYPE", "value": VALUE}
 */

#include <ArduinoJson.h>

// Stepper Motor Pins
#define STEP_PIN 3
#define DIR_PIN 4
#define ENABLE_PIN 5

// Limit Switch Pins
#define LIMIT_SWITCH_TOP 8
#define LIMIT_SWITCH_BOTTOM 9

// Heart Rate Sensor Pin
#define HEART_RATE_PIN A0

// Stepper Motor Parameters
#define STEPS_PER_MM 100 // Steps per millimeter
#define MAX_HEIGHT 100   // Maximum height (mm)
#define MIN_HEIGHT 0     // Minimum height (mm)
#define MOTOR_SPEED 500  // Stepper motor speed (steps/second)

// Heart Rate Monitoring Parameters
#define HEART_RATE_SAMPLES 10    // Number of samples for each calculation
#define HEART_RATE_THRESHOLD 550 // Heart beat detection threshold
#define HEART_RATE_INTERVAL 20   // Sampling interval (ms)

// Running Status
bool isRunning = false;
bool isBedMoving = false;
bool isHeartRateMonitoring = false;
int currentHeight = 0;                 // Current height (mm)
int targetHeight = 0;                  // Target height (mm)
int currentHeartRate = 0;              // Current heart rate (BPM)
unsigned long lastHeartRateUpdate = 0; // Last heart rate update time
unsigned long lastHeartBeat = 0;       // Last heartbeat time
int heartBeatCount = 0;                // Heartbeat count
bool heartRateStream = false;          // Whether to stream heart rate data

// Serial Communication Buffer
const int BUFFER_SIZE = 256;
char inputBuffer[BUFFER_SIZE];
int bufferIndex = 0;

void setup()
{
  // Initialize serial communication
  Serial.begin(9600);

  // Initialize stepper motor pins
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  pinMode(ENABLE_PIN, OUTPUT);

  // Initialize limit switch pins
  pinMode(LIMIT_SWITCH_TOP, INPUT_PULLUP);
  pinMode(LIMIT_SWITCH_BOTTOM, INPUT_PULLUP);

  // Initialize heart rate sensor pin
  pinMode(HEART_RATE_PIN, INPUT);

  // Disable motor driver
  disableMotor();

  // Complete initialization
  isRunning = true;

  // Send system ready message
  sendSystemStatus();
}

void loop()
{
  // Check for serial commands
  readSerialCommands();

  // Process bed movement
  if (isBedMoving)
  {
    moveBed();
  }

  // Process heart rate monitoring
  if (isHeartRateMonitoring)
  {
    monitorHeartRate();
  }

  // Short delay
  delay(1);
}

// Read commands from serial port
void readSerialCommands()
{
  while (Serial.available() > 0)
  {
    char c = Serial.read();

    // Store characters until line end
    if (c == '\n')
    {
      // Terminate string
      inputBuffer[bufferIndex] = '\0';

      // Process command
      processCommand(inputBuffer);

      // Reset buffer
      bufferIndex = 0;
    }
    else if (bufferIndex < BUFFER_SIZE - 1)
    {
      // Add character to buffer
      inputBuffer[bufferIndex++] = c;
    }
  }
}

// Process received command
void processCommand(const char *command)
{
  // Create JSON parser
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, command);

  // Check for parsing error
  if (error)
  {
    sendError("Invalid JSON command");
    return;
  }

  // Extract command name
  const char *cmdName = doc["command"];

  if (!cmdName)
  {
    sendError("Missing command field");
    return;
  }

  // Process different commands
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

// Send error message
void sendError(const char *message)
{
  StaticJsonDocument<256> doc;
  doc["type"] = "ERROR";
  doc["message"] = message;

  serializeJson(doc, Serial);
  Serial.println();
}

// Send bed height
void sendBedHeight()
{
  StaticJsonDocument<128> doc;
  doc["type"] = "BED_HEIGHT";
  doc["value"] = currentHeight;

  serializeJson(doc, Serial);
  Serial.println();
}

// Send heart rate data
void sendHeartRate()
{
  StaticJsonDocument<128> doc;
  doc["type"] = "HEART_RATE";
  doc["value"] = currentHeartRate;

  serializeJson(doc, Serial);
  Serial.println();
}

// Send system status
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

// Start bed up
void startBedUp()
{
  // Check upper limit
  if (digitalRead(LIMIT_SWITCH_TOP) == LOW)
  {
    sendError("Bed already at top position");
    return;
  }

  // Set direction and enable
  digitalWrite(DIR_PIN, HIGH); // Up direction
  enableMotor();

  // Start moving
  isBedMoving = true;

  // Send confirmation
  StaticJsonDocument<128> doc;
  doc["type"] = "BED_CONTROL";
  doc["action"] = "UP";
  doc["status"] = "STARTED";

  serializeJson(doc, Serial);
  Serial.println();
}

// Start bed down
void startBedDown()
{
  // Check lower limit
  if (digitalRead(LIMIT_SWITCH_BOTTOM) == LOW)
  {
    sendError("Bed already at bottom position");
    return;
  }

  // Set direction and enable
  digitalWrite(DIR_PIN, LOW); // Down direction
  enableMotor();

  // Start moving
  isBedMoving = true;

  // Send confirmation
  StaticJsonDocument<128> doc;
  doc["type"] = "BED_CONTROL";
  doc["action"] = "DOWN";
  doc["status"] = "STARTED";

  serializeJson(doc, Serial);
  Serial.println();
}

// Stop bed movement
void stopBed()
{
  // Stop moving
  isBedMoving = false;
  disableMotor();

  // Send confirmation
  StaticJsonDocument<128> doc;
  doc["type"] = "BED_CONTROL";
  doc["action"] = "STOP";
  doc["status"] = "STOPPED";

  serializeJson(doc, Serial);
  Serial.println();
}

// Move bed
void moveBed()
{
  // Check limit switches
  bool topLimitReached = (digitalRead(LIMIT_SWITCH_TOP) == LOW);
  bool bottomLimitReached = (digitalRead(LIMIT_SWITCH_BOTTOM) == LOW);

  if ((digitalRead(DIR_PIN) == HIGH && topLimitReached) ||
      (digitalRead(DIR_PIN) == LOW && bottomLimitReached))
  {
    // Reached limit, stop moving
    stopBed();
    return;
  }

  // Send pulse
  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(1000); // Control speed
  digitalWrite(STEP_PIN, LOW);
  delayMicroseconds(1000); // Control speed

  // Update height
  if (digitalRead(DIR_PIN) == HIGH)
  {
    // Up
    currentHeight += 1.0 / STEPS_PER_MM;
    if (currentHeight > MAX_HEIGHT)
    {
      currentHeight = MAX_HEIGHT;
    }
  }
  else
  {
    // Down
    currentHeight -= 1.0 / STEPS_PER_MM;
    if (currentHeight < MIN_HEIGHT)
    {
      currentHeight = MIN_HEIGHT;
    }
  }
}

// Enable motor
void enableMotor()
{
  digitalWrite(ENABLE_PIN, LOW); // Low level enable
}

// Disable motor
void disableMotor()
{
  digitalWrite(ENABLE_PIN, HIGH); // High level disable
}

// Monitor heart rate
void monitorHeartRate()
{
  // Ensure initialized
  if (!isHeartRateMonitoring)
  {
    isHeartRateMonitoring = true;
    heartBeatCount = 0;
    lastHeartBeat = 0;
  }

  // Read sensor value
  int sensorValue = analogRead(HEART_RATE_PIN);
  unsigned long currentTime = millis();

  // Detect heartbeat
  static int lastSensorValue = 0;
  static bool isPeak = false;

  // Detect rising edge crossing threshold (heartbeat peak)
  if (sensorValue > HEART_RATE_THRESHOLD && lastSensorValue <= HEART_RATE_THRESHOLD)
  {
    isPeak = true;
  }
  // Detect falling edge (heartbeat completion)
  else if (isPeak && sensorValue < HEART_RATE_THRESHOLD)
  {
    isPeak = false;

    // Calculate time between two heartbeats
    if (lastHeartBeat > 0)
    {
      unsigned long timeBetweenBeats = currentTime - lastHeartBeat;

      // Heartbeat interval within reasonable range
      if (timeBetweenBeats > 300 && timeBetweenBeats < 2000)
      {
        // Increase count
        heartBeatCount++;

        // Calculate heart rate (BPM)
        if (heartBeatCount >= HEART_RATE_SAMPLES)
        {
          // Calculate average time
          unsigned long totalTime = currentTime - lastHeartRateUpdate;
          float beatsPerSecond = (float)heartBeatCount / (totalTime / 1000.0);
          currentHeartRate = (int)(beatsPerSecond * 60.0);

          // Reset count
          heartBeatCount = 0;
          lastHeartRateUpdate = currentTime;

          // Send heart rate data
          if (heartRateStream)
          {
            sendHeartRate();
          }
        }
      }
    }

    // Save heartbeat time
    lastHeartBeat = currentTime;
  }

  // Save last sensor value
  lastSensorValue = sensorValue;
}