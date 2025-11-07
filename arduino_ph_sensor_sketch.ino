/*
 * Arduino Multi-Sensor Reader for Deep Blue Pool Chemistry
 * Copyright (c) 2024 Michael Hayes. All rights reserved.
 * 
 * This sketch reads pH, Temperature, and ORP sensor values
 * Compatible with analog sensors connected to Arduino
 * 
 * Hardware Setup:
 * - pH Sensor Signal -> Arduino A0
 * - Temperature Sensor Signal -> Arduino A1
 * - ORP Sensor Signal -> Arduino A2
 * - All Sensors VCC -> Arduino 5V
 * - All Sensors GND -> Arduino GND
 * 
 * Communication:
 * - Baud Rate: 9600
 * - Command: "READ\n"
 * - Response: "PH:7.2,TEMP:78.5,ORP:650\n"
 */

// ==================== PIN CONFIGURATION ====================

const int PH_SENSOR_PIN = A0;        // pH sensor on A0
const int TEMP_SENSOR_PIN = A1;      // Temperature sensor on A1
const int ORP_SENSOR_PIN = A2;       // ORP sensor on A2

// ==================== pH CALIBRATION ====================

// pH Calibration Values (UPDATE AFTER CALIBRATION)
float PH_CALIBRATION_SLOPE = 3.5;
float PH_CALIBRATION_INTERCEPT = -3.2;

// ==================== TEMPERATURE CALIBRATION ====================

// Temperature Calibration (for DS18B20 or analog temp sensor)
// Adjust these based on your sensor type
float TEMP_CALIBRATION_SLOPE = 100.0;     // Degrees per volt
float TEMP_CALIBRATION_OFFSET = 0.0;      // Offset in degrees

// ==================== ORP CALIBRATION ====================

// ORP Calibration (Oxidation-Reduction Potential)
// Typical range: -2000mV to +2000mV
float ORP_CALIBRATION_SLOPE = 1000.0;     // mV per volt
float ORP_CALIBRATION_OFFSET = -2000.0;   // Offset in mV

// ==================== READING CONFIGURATION ====================

const int NUM_SAMPLES = 10;          // Number of samples to average
const int SAMPLE_DELAY = 50;         // Delay between samples (ms)

// ==================== GLOBAL VARIABLES ====================

String inputCommand = "";
boolean commandComplete = false;

// ==================== SETUP ====================

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Configure analog reference (use default 5V)
  analogReference(DEFAULT);
  
  // Wait for serial to initialize
  while (!Serial) {
    ; // Wait for serial port to connect
  }
  
  // Send ready message
  Serial.println("READY");
  
  // Reserve space for input command
  inputCommand.reserve(50);
}

// ==================== MAIN LOOP ====================

void loop() {
  // Check for incoming commands
  if (commandComplete) {
    processCommand(inputCommand);
    
    // Clear the command
    inputCommand = "";
    commandComplete = false;
  }
}

// ==================== SERIAL EVENT ====================

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    
    if (inChar == '\n') {
      commandComplete = true;
    } else {
      inputCommand += inChar;
    }
  }
}

// ==================== COMMAND PROCESSING ====================

void processCommand(String command) {
  command.trim();
  command.toUpperCase();
  
  if (command == "READ") {
    // Read all sensors and send results
    float phValue = readPH();
    float tempValue = readTemperature();
    float orpValue = readORP();
    
    // Send in format: PH:7.2,TEMP:78.5,ORP:650
    Serial.print("PH:");
    Serial.print(phValue, 2);
    Serial.print(",TEMP:");
    Serial.print(tempValue, 1);
    Serial.print(",ORP:");
    Serial.println(orpValue, 0);
    
  } else if (command == "PH") {
    // Read only pH
    float phValue = readPH();
    Serial.print("PH:");
    Serial.println(phValue, 2);
    
  } else if (command == "TEMP") {
    // Read only temperature
    float tempValue = readTemperature();
    Serial.print("TEMP:");
    Serial.println(tempValue, 1);
    
  } else if (command == "ORP") {
    // Read only ORP
    float orpValue = readORP();
    Serial.print("ORP:");
    Serial.println(orpValue, 0);
    
  } else if (command == "VOLTAGE") {
    // Read raw voltages from all sensors
    float phVoltage = readVoltage(PH_SENSOR_PIN);
    float tempVoltage = readVoltage(TEMP_SENSOR_PIN);
    float orpVoltage = readVoltage(ORP_SENSOR_PIN);
    
    Serial.print("PH_V:");
    Serial.print(phVoltage, 3);
    Serial.print(",TEMP_V:");
    Serial.print(tempVoltage, 3);
    Serial.print(",ORP_V:");
    Serial.println(orpVoltage, 3);
    
  } else if (command == "CALIBRATE") {
    // Send current calibration values
    Serial.println("=== pH Calibration ===");
    Serial.print("SLOPE:");
    Serial.println(PH_CALIBRATION_SLOPE, 4);
    Serial.print("INTERCEPT:");
    Serial.println(PH_CALIBRATION_INTERCEPT, 4);
    
    Serial.println("=== Temperature Calibration ===");
    Serial.print("SLOPE:");
    Serial.println(TEMP_CALIBRATION_SLOPE, 4);
    Serial.print("OFFSET:");
    Serial.println(TEMP_CALIBRATION_OFFSET, 4);
    
    Serial.println("=== ORP Calibration ===");
    Serial.print("SLOPE:");
    Serial.println(ORP_CALIBRATION_SLOPE, 4);
    Serial.print("OFFSET:");
    Serial.println(ORP_CALIBRATION_OFFSET, 4);
    
  } else if (command == "HELP") {
    // Send help information
    printHelp();
    
  } else {
    // Unknown command
    Serial.println("ERROR:UNKNOWN_COMMAND");
  }
}

// ==================== pH READING ====================

float readPH() {
  // Read voltage from pH sensor
  float voltage = readVoltage(PH_SENSOR_PIN);
  
  // Apply calibration equation: pH = slope * voltage + intercept
  float pH = (PH_CALIBRATION_SLOPE * voltage) + PH_CALIBRATION_INTERCEPT;
  
  // Constrain to valid pH range (0-14)
  pH = constrain(pH, 0.0, 14.0);
  
  return pH;
}

// ==================== TEMPERATURE READING ====================

float readTemperature() {
  // Read voltage from temperature sensor
  float voltage = readVoltage(TEMP_SENSOR_PIN);
  
  // Apply calibration equation: Temp = slope * voltage + offset
  float temperature = (TEMP_CALIBRATION_SLOPE * voltage) + TEMP_CALIBRATION_OFFSET;
  
  // Constrain to reasonable range (32-120°F or 0-50°C)
  temperature = constrain(temperature, 32.0, 120.0);
  
  return temperature;
}

// ==================== ORP READING ====================

float readORP() {
  // Read voltage from ORP sensor
  float voltage = readVoltage(ORP_SENSOR_PIN);
  
  // Apply calibration equation: ORP = slope * voltage + offset
  float orp = (ORP_CALIBRATION_SLOPE * voltage) + ORP_CALIBRATION_OFFSET;
  
  // Constrain to reasonable range (-2000 to +2000 mV)
  orp = constrain(orp, -2000.0, 2000.0);
  
  return orp;
}

// ==================== VOLTAGE READING ====================

float readVoltage(int pin) {
  long sum = 0;
  
  // Take multiple samples and average
  for (int i = 0; i < NUM_SAMPLES; i++) {
    sum += analogRead(pin);
    delay(SAMPLE_DELAY);
  }
  
  // Calculate average
  float average = sum / (float)NUM_SAMPLES;
  
  // Convert to voltage (0-1023 -> 0-5V)
  float voltage = average * (5.0 / 1023.0);
  
  return voltage;
}

// ==================== HELP INFORMATION ====================

void printHelp() {
  Serial.println("=== Arduino Multi-Sensor Commands ===");
  Serial.println("READ - Read all sensors (pH, Temp, ORP)");
  Serial.println("PH - Read pH only");
  Serial.println("TEMP - Read temperature only");
  Serial.println("ORP - Read ORP only");
  Serial.println("VOLTAGE - Read raw voltages");
  Serial.println("CALIBRATE - Show calibration values");
  Serial.println("HELP - Show this help");
  Serial.println("====================================");
}

// ==================== NOTES ====================

/*
 * SENSOR WIRING:
 * 
 * pH Sensor:
 *   Signal -> A0
 *   VCC -> 5V
 *   GND -> GND
 * 
 * Temperature Sensor:
 *   Signal -> A1
 *   VCC -> 5V
 *   GND -> GND
 * 
 * ORP Sensor:
 *   Signal -> A2
 *   VCC -> 5V
 *   GND -> GND
 * 
 * CALIBRATION:
 * 
 * pH Sensor:
 *   1. Use the Arduino Calibration Wizard
 *   2. Update PH_CALIBRATION_SLOPE and PH_CALIBRATION_INTERCEPT
 * 
 * Temperature Sensor:
 *   1. Place in ice water (32°F / 0°C)
 *   2. Read voltage with "VOLTAGE" command
 *   3. Place in boiling water (212°F / 100°C)
 *   4. Read voltage again
 *   5. Calculate: SLOPE = (212 - 32) / (V_hot - V_cold)
 *   6. Calculate: OFFSET = 32 - (SLOPE * V_cold)
 * 
 * ORP Sensor:
 *   1. Use ORP calibration solution (typically 220mV or 470mV)
 *   2. Read voltage with "VOLTAGE" command
 *   3. Calculate: SLOPE = (known_mV - 0) / (measured_V - 2.5)
 *   4. Adjust OFFSET if needed
 * 
 * TESTING:
 * 
 * 1. Open Serial Monitor (9600 baud)
 * 2. Type "READ" -> Should show: PH:7.2,TEMP:78.5,ORP:650
 * 3. Type "PH" -> Should show: PH:7.2
 * 4. Type "TEMP" -> Should show: TEMP:78.5
 * 5. Type "ORP" -> Should show: ORP:650
 * 6. Type "VOLTAGE" -> Shows raw voltages for debugging
 * 
 * TROUBLESHOOTING:
 * 
 * If pH shows 9.4 but should be 7.2:
 *   - Recalibrate pH sensor using wizard
 *   - Check pH sensor connections
 *   - Verify sensor is in water, not air
 * 
 * If temperature shows wrong value:
 *   - Adjust TEMP_CALIBRATION_SLOPE and TEMP_CALIBRATION_OFFSET
 *   - Check sensor type (some sensors output different ranges)
 *   - Verify sensor is working (test with multimeter)
 * 
 * If ORP shows wrong value:
 *   - Adjust ORP_CALIBRATION_SLOPE and ORP_CALIBRATION_OFFSET
 *   - Check sensor connections
 *   - ORP sensors need time to stabilize (2-3 minutes)
 */