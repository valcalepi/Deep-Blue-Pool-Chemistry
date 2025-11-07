/*
 * Deep Blue Pool Chemistry - Realistic Test Sensor
 * Copyright (c) 2024 Michael Hayes. All rights reserved.
 * 
 * This sketch provides realistic pool chemistry readings for testing
 * without requiring actual sensors to be connected.
 * 
 * Upload this to your Arduino to get realistic test data.
 */

// Simulated sensor values (realistic pool chemistry ranges)
float ph_value = 7.4;           // Ideal pH: 7.2-7.6
float temperature = 78.5;       // Comfortable pool temp: 78-82°F
float orp_value = 650.0;        // Good ORP: 650-750 mV

// Add slight variation to make readings more realistic
float ph_variation = 0.0;
float temp_variation = 0.0;
float orp_variation = 0.0;

void setup() {
  Serial.begin(9600);
  
  // Wait for serial connection
  while (!Serial) {
    ; // Wait for serial port to connect
  }
  
  // Initialize random seed
  randomSeed(analogRead(A0));
  
  Serial.println("Deep Blue Pool Chemistry Sensor Ready");
  Serial.println("Commands: READ, PH, TEMP, ORP, HELP");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    command.toUpperCase();
    
    if (command == "READ") {
      // Return all sensor readings
      sendAllReadings();
    }
    else if (command == "PH") {
      // Return only pH
      sendPHReading();
    }
    else if (command == "TEMP") {
      // Return only temperature
      sendTempReading();
    }
    else if (command == "ORP") {
      // Return only ORP
      sendORPReading();
    }
    else if (command == "HELP") {
      // Show available commands
      Serial.println("Available commands:");
      Serial.println("  READ - Get all sensor readings");
      Serial.println("  PH - Get pH reading only");
      Serial.println("  TEMP - Get temperature reading only");
      Serial.println("  ORP - Get ORP reading only");
      Serial.println("  HELP - Show this help message");
    }
    else {
      Serial.println("ERROR: Unknown command. Type HELP for available commands.");
    }
  }
}

void sendAllReadings() {
  // Add small random variations to make readings realistic
  updateVariations();
  
  float current_ph = ph_value + ph_variation;
  float current_temp = temperature + temp_variation;
  float current_orp = orp_value + orp_variation;
  
  // Keep values in realistic ranges
  current_ph = constrain(current_ph, 6.8, 8.2);
  current_temp = constrain(current_temp, 75.0, 85.0);
  current_orp = constrain(current_orp, 600.0, 800.0);
  
  // Send in format: PH:7.40,TEMP:78.50,ORP:650.00
  Serial.print("PH:");
  Serial.print(current_ph, 2);
  Serial.print(",TEMP:");
  Serial.print(current_temp, 2);
  Serial.print(",ORP:");
  Serial.println(current_orp, 2);
}

void sendPHReading() {
  updateVariations();
  float current_ph = ph_value + ph_variation;
  current_ph = constrain(current_ph, 6.8, 8.2);
  
  Serial.print("PH:");
  Serial.println(current_ph, 2);
}

void sendTempReading() {
  updateVariations();
  float current_temp = temperature + temp_variation;
  current_temp = constrain(current_temp, 75.0, 85.0);
  
  Serial.print("TEMP:");
  Serial.println(current_temp, 2);
}

void sendORPReading() {
  updateVariations();
  float current_orp = orp_value + orp_variation;
  current_orp = constrain(current_orp, 600.0, 800.0);
  
  Serial.print("ORP:");
  Serial.println(current_orp, 2);
}

void updateVariations() {
  // Add small random variations (±0.2 for pH, ±1.0 for temp, ±20 for ORP)
  ph_variation = random(-20, 21) / 100.0;      // ±0.2
  temp_variation = random(-100, 101) / 100.0;  // ±1.0
  orp_variation = random(-2000, 2001) / 100.0; // ±20.0
}

/*
 * USAGE INSTRUCTIONS:
 * 
 * 1. Upload this sketch to your Arduino
 * 2. Open Serial Monitor (9600 baud) to test
 * 3. Type "READ" and press Enter to get all readings
 * 4. Type "PH" to get only pH reading
 * 5. Type "TEMP" to get only temperature
 * 6. Type "ORP" to get only ORP
 * 7. Type "HELP" to see available commands
 * 
 * The sketch provides realistic pool chemistry values:
 * - pH: 7.2-7.6 (ideal range with small variations)
 * - Temperature: 78-82°F (comfortable swimming temperature)
 * - ORP: 650-750 mV (good oxidation-reduction potential)
 * 
 * Each reading has small random variations to simulate
 * real sensor behavior.
 */