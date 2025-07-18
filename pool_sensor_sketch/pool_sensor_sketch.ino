/**
• Deep Blue Pool Chemistry - Advanced Arduino Sensor Integration
• 
• This sketch reads data from multiple pool water quality sensors and sends
• the data to the Deep Blue Pool Chemistry application via serial communication.
• 
• Supported sensors:
• - pH sensor (analog)
• - Temperature sensor (DS18B20)
• - ORP sensor (analog)
• - TDS/EC sensor (analog)
• - Turbidity sensor (analog)
• 
• Communication protocol:
• JSON format: {"pH": 7.2, "temp": 25.5, "orp": 650, "tds": 450, "turb": 0.5}
 */


#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>


// Pin definitions
#define PH_SENSOR_PIN A0
#define ORP_SENSOR_PIN A1
#define TDS_SENSOR_PIN A2
#define TURBIDITY_PIN A3
#define TEMP_SENSOR_PIN 2


// Constants for sensor calibration
#define PH_OFFSET 0.0
#define PH_SLOPE 3.3
#define ORP_OFFSET 0.0
#define TDS_FACTOR 0.5
#define TURBIDITY_FACTOR 0.5


// Setup OneWire and DallasTemperature for temperature sensor
OneWire oneWire(TEMP_SENSOR_PIN);
DallasTemperature tempSensors(&oneWire);


// Variables for sensor readings
float ph_value = 0.0;
float temperature = 0.0;
int orp_value = 0;
int tds_value = 0;
float turbidity = 0.0;


// Variables for timing
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 2000; // Send data every 2 seconds


// Variables for serial communication
String inputString = "";
boolean stringComplete = false;


void setup() {
  // Initialize serial communication
  Serial.begin(9600);


  // Initialize temperature sensor
  tempSensors.begin();


  // Initialize analog pins
  pinMode(PH_SENSOR_PIN, INPUT);
  pinMode(ORP_SENSOR_PIN, INPUT);
  pinMode(TDS_SENSOR_PIN, INPUT);
  pinMode(TURBIDITY_PIN, INPUT);


  // Reserve memory for JSON document
  inputString.reserve(200);


  // Print startup message
  Serial.println("Deep Blue Pool Chemistry - Arduino Sensor System");
  Serial.println("Ready to receive commands and send sensor data");
}


void loop() {
  // Check if it's time to send data
  unsigned long currentTime = millis();
  if (currentTime - lastSendTime >= sendInterval) {
    // Read sensor values
    readSensors();


// Send data as JSON
sendSensorData();

// Update last send time
lastSendTime = currentTime;

  }


  // Process incoming commands
  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
}


void readSensors() {
  // Read pH sensor
  int ph_raw = analogRead(PH_SENSOR_PIN);
  ph_value = convertPH(ph_raw);


  // Read temperature sensor
  tempSensors.requestTemperatures();
  temperature = tempSensors.getTempCByIndex(0);


  // Read ORP sensor
  int orp_raw = analogRead(ORP_SENSOR_PIN);
  orp_value = convertORP(orp_raw);


  // Read TDS sensor
  int tds_raw = analogRead(TDS_SENSOR_PIN);
  tds_value = convertTDS(tds_raw);


  // Read turbidity sensor
  int turbidity_raw = analogRead(TURBIDITY_PIN);
  turbidity = convertTurbidity(turbidity_raw);
}


float convertPH(int raw_value) {
  // Convert raw analog value to pH
  // This is a simplified conversion - actual implementation would depend on your specific sensor
  float voltage = raw_value * (5.0 / 1023.0);
  return 7.0 - ((voltage - 2.5) / PH_SLOPE) + PH_OFFSET;
}


int convertORP(int raw_value) {
  // Convert raw analog value to ORP (mV)
  // This is a simplified conversion - actual implementation would depend on your specific sensor
  float voltage = raw_value * (5.0 / 1023.0);
  return int(((voltage - 2.5) * 1000) + ORP_OFFSET);
}


int convertTDS(int raw_value) {
  // Convert raw analog value to TDS (ppm)
  // This is a simplified conversion - actual implementation would depend on your specific sensor
  float voltage = raw_value * (5.0 / 1023.0);
  return int(voltage * 500 * TDS_FACTOR);
}


float convertTurbidity(int raw_value) {
  // Convert raw analog value to turbidity (NTU)
  // This is a simplified conversion - actual implementation would depend on your specific sensor
  float voltage = raw_value * (5.0 / 1023.0);
  return voltage * TURBIDITY_FACTOR;
}


void sendSensorData() {
  // Create JSON document
  StaticJsonDocument<200> doc;


  // Add sensor values to JSON
  doc["pH"] = ph_value;
  doc["temp"] = temperature;
  doc["orp"] = orp_value;
  doc["tds"] = tds_value;
  doc["turb"] = turbidity;


  // Serialize JSON to serial
  serializeJson(doc, Serial);
  Serial.println();
}


void processCommand(String command) {
  // Remove newline characters
  command.trim();


  // Parse JSON command
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, command);


  // Check if parsing succeeded
  if (error) {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    return;
  }


  // Process commands
  if (doc.containsKey("calibrate")) {
    String sensor = doc["calibrate"];
    float value = doc["value"];
    calibrateSensor(sensor, value);
  } else if (doc.containsKey("interval")) {
    int interval = doc["interval"];
    updateInterval(interval);
  }
}


void calibrateSensor(String sensor, float value) {
  // Calibrate the specified sensor
  if (sensor == "pH") {
    // Implement pH calibration
    Serial.println("Calibrating pH sensor to " + String(value));
  } else if (sensor == "orp") {
    // Implement ORP calibration
    Serial.println("Calibrating ORP sensor to " + String(value));
  } else if (sensor == "tds") {
    // Implement TDS calibration
    Serial.println("Calibrating TDS sensor to " + String(value));
  }
}


void updateInterval(int interval) {
  // Update the send interval
  sendInterval = interval;
  Serial.println("Updated send interval to " + String(interval) + " ms");
}


void serialEvent() {
  // Read incoming serial data
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;


// Check for end of command
if (inChar == '\

') {
      stringComplete = true;
    }
  }
}