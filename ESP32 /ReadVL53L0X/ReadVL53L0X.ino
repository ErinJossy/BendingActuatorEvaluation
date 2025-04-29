#include <Wire.h>             // Include the I2C library
#include "Adafruit_VL53L0X.h" // Include the VL53L0X library

// Create an instance of the VL53L0X sensor
Adafruit_VL53L0X lox = Adafruit_VL53L0X();

// Variable to store the measurement data
VL53L0X_RangingMeasurementData_t measure;

void setup() {
  // Initialize Serial communication at 115200 baud
  Serial.begin(115200);

  // Wait for the Serial port to connect (important for native USB boards like Leonardo, Micro, etc.)
  while (!Serial) {
    delay(1);
  }

  Serial.println("Adafruit VL53L0X Test - High Accuracy Mode");

  // Initialize the I2C bus (Wire library)
  // Note: You might need Wire.begin(SDA_PIN, SCL_PIN); on some boards (like ESP32)
  // if using non-default I2C pins.
  Wire.begin();

  // --- Initialize the VL53L0X sensor ---
  // The begin function can take parameters:
  // begin(i2c_addr, debug, i2c_interface, sensor_config)
  // We will set the sensor_config to High Accuracy.
  Serial.println("Initializing VL53L0X sensor...");
  if (!lox.begin(VL53L0X_I2C_ADDR, false, &Wire, Adafruit_VL53L0X::VL53L0X_SENSE_HIGH_ACCURACY)) {
    Serial.println(F("Failed to boot VL53L0X sensor. Check wiring or I2C address."));
    // Halt execution if the sensor fails to initialize
    while (1) {
      delay(10);
    }
  }
  Serial.println(F("VL53L0X sensor OK!"));

  // --- Optional: Print sensor configuration details ---
  // High Accuracy mode typically uses a longer timing budget.
  // Let's check the timing budget set by the High Accuracy profile.
  uint32_t timing_budget_us = lox.getMeasurementTimingBudgetMicroSeconds();
  Serial.print(F("Timing budget (uS): ")); Serial.println(timing_budget_us);
  // Note: High accuracy mode uses a timing budget of 200ms (200000 us)

  Serial.println(F("\nStarting measurements..."));
}

void loop() {
  // --- Perform a Single Ranging Measurement ---
  // This is often preferred over continuous mode for better control
  // and understanding when each measurement happens.
  // Serial.print("Ranging... "); // Uncomment for verbose output

  // Get a measurement. This function handles starting, waiting, and reading.
  // It stores the result in the 'measure' struct.
  VL53L0X_Error status = lox.getSingleRangingMeasurement(&measure, false); // false = disable debug prints

  // Check if the measurement was successful
  if (status == VL53L0X_ERROR_NONE) {
    // Print the distance measurement:
    // measure.RangeStatus == 4 indicates "Phase out of valid limits" or "Sigma Fail" or out of range
    if (measure.RangeStatus != 4) {
      Serial.print("Distance (mm): ");
      Serial.println(measure.RangeMilliMeter);
    } else {
      Serial.println("Out of range or error");
    }

    // --- Optional: Print more details from the measurement struct ---
    // Serial.print("Signal Rate (Mcps): "); Serial.println(measure.SignalRateRtnMegaCps / 65536.0);
    // Serial.print("Ambient Rate (Mcps): "); Serial.println(measure.AmbientRateRtnMegaCps / 65536.0);
    // Serial.print("Sigma (mm): "); Serial.println(measure.SigmaMilliMeter / 65536.0);
    // Serial.print("Status: "); Serial.println((int)measure.RangeStatus);
    // lox.printRangeStatus(&measure); // Helper function to decode status

  } else {
    // Print the error code if the measurement failed
    Serial.print("Ranging failed with error: ");
    Serial.println(status);
  }

  // Add a delay between measurements.
  // Since High Accuracy mode takes ~200ms per measurement,
  // a small additional delay is reasonable.
  delay(100);
}