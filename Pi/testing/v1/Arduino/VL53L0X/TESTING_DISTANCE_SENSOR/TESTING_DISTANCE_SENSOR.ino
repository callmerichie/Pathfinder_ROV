#include "Adafruit_VL53L0X.h"

Adafruit_VL53L0X sensor = Adafruit_VL53L0X();

void setup() {
  Serial.begin(9600);
  sensor.begin();
}

void loop() {
  VL53L0X_RangingMeasurementData_t measure;    
  sensor.rangingTest(&measure, false); 

  if(measure.RangeStatus == 4) {
    Serial.println("---");
  } else {
    Serial.println(measure.RangeMilliMeter);
  }
 
  delay(100);
}