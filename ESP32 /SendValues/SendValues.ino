#include <Wire.h>             // Include the I2C library
#include "Adafruit_VL53L0X.h" // Include the VL53L0X library

// Create an instance of the VL53L0X sensor
Adafruit_VL53L0X lox = Adafruit_VL53L0X();

// Variable to store the measurement data
VL53L0X_RangingMeasurementData_t measure;
uint32_t t_val = 0;
void setup() {
  // Initialize Serial communication at 115200 baud
  Serial.begin(115200);
  pinMode(4,OUTPUT);
  while (!Serial) {
    delay(1);
  }

  if (!lox.begin(VL53L0X_I2C_ADDR, false, &Wire, Adafruit_VL53L0X::VL53L0X_SENSE_HIGH_ACCURACY)) {
    while (1) {
      delay(10);
    }
  }
}

void loop() {
  t_val = millis();
  VL53L0X_Error status = lox.getSingleRangingMeasurement(&measure, false); // false = disable debug prints

  if (status == VL53L0X_ERROR_NONE) {
    // Print the distance measurement:
    // measure.RangeStatus == 4 indicates "Phase out of valid limits" or "Sigma Fail" or out of range
    if (measure.RangeStatus != 4) {
      Serial.print("Distance(mm): ");
      Serial.print(measure.RangeMilliMeter);
    } else {
      Serial.print("Distance(mm): ");
      Serial.print("NaN");
    }

    // --- Optional: Print more details from the measurement struct ---
    // Serial.print("Signal Rate (Mcps): "); Serial.println(measure.SignalRateRtnMegaCps / 65536.0);
    // Serial.print("Ambient Rate (Mcps): "); Serial.println(measure.AmbientRateRtnMegaCps / 65536.0);
    // Serial.print("Sigma (mm): "); Serial.println(measure.SigmaMilliMeter / 65536.0);
    // Serial.print("Status: "); Serial.println((int)measure.RangeStatus);
    // lox.printRangeStatus(&measure); // Helper function to decode status

  } else {
    Serial.print("Distance(mm): ");
    Serial.print("NaN");
  }
  Serial.print("\tFSR Reading: ");
  Serial.print(analogRead(4));
  Serial.print("\tTime(ms):");
  Serial.println(t_val);
  delay(50);
}