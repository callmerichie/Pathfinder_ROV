#include "Adafruit_VL53L0X.h"

// Motor control pins (L298N)
#define ENA 9
#define IN1 8
#define IN2 7
#define ENB 10
#define IN3 6
#define IN4 5

// VL53L0X shutdown pins and addresses
#define SHT_LOX1 13
#define SHT_LOX2 12
#define LOX1_ADDRESS 0x30
#define LOX2_ADDRESS 0x31

Adafruit_VL53L0X lox1 = Adafruit_VL53L0X();
Adafruit_VL53L0X lox2 = Adafruit_VL53L0X();
VL53L0X_RangingMeasurementData_t measure1;
VL53L0X_RangingMeasurementData_t measure2;

// -1 = not yet read / out of range
int sensor1 = -1;
int sensor2 = -1;

#define OBSTACLE_MM   50    // stop if sensor reads below this
#define SENSOR_INTERVAL 200 // ms between sensor reads

int keys[4];
unsigned long lastSensorRead = 0;


void setID() {
  digitalWrite(SHT_LOX1, LOW);
  digitalWrite(SHT_LOX2, LOW);
  delay(10);
  digitalWrite(SHT_LOX1, HIGH);
  digitalWrite(SHT_LOX2, HIGH);
  delay(10);

  digitalWrite(SHT_LOX1, HIGH);
  digitalWrite(SHT_LOX2, LOW);
  if (!lox1.begin(LOX1_ADDRESS)) {
    Serial.println(F("Failed to boot VL53L0X #1"));
    while (1);
  }
  delay(10);

  digitalWrite(SHT_LOX2, HIGH);
  delay(10);
  if (!lox2.begin(LOX2_ADDRESS)) {
    Serial.println(F("Failed to boot VL53L0X #2"));
    while (1);
  }
}


void readSensors() {
  lox1.rangingTest(&measure1, false);
  lox2.rangingTest(&measure2, false);

  sensor1 = (measure1.RangeStatus != 6) ? measure1.RangeMilliMeter : -1;
  sensor2 = (measure2.RangeStatus != 6) ? measure2.RangeMilliMeter : -1;

  // Send readings to Pi: "D:s1,s2"
  Serial.print("D:");
  Serial.print(sensor1);
  Serial.print(",");
  Serial.println(sensor2);
}


bool obstacleDetected() {
  // -1 means out-of-range (far) → treat as safe
  if (sensor1 != -1 && sensor1 <= OBSTACLE_MM) return true;
  if (sensor2 != -1 && sensor2 <= OBSTACLE_MM) return true;
  return false;
}


void moveForward() {
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
  analogWrite(ENA, 115);   analogWrite(ENB, 115);
}

void moveBackward() {
  digitalWrite(IN1, LOW);  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);  digitalWrite(IN4, HIGH);
  analogWrite(ENA, 115);   analogWrite(ENB, 115);
}

void turnLeft() {
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);  digitalWrite(IN4, LOW);
  analogWrite(ENA, 115);
}

void turnRight() {
  digitalWrite(IN1, LOW);  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
  analogWrite(ENB, 115);
}

void stopVehicle() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  analogWrite(ENA, 0);    analogWrite(ENB, 0);
}


void setup() {
  Serial.begin(115200);

  pinMode(SHT_LOX1, OUTPUT);
  pinMode(SHT_LOX2, OUTPUT);
  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT); pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);

  setID();
}


void loop() {
  // Drain serial buffer: keep only the latest 4-byte command
  while (Serial.available() >= 4) {
    for (int i = 0; i < 4; i++) keys[i] = Serial.read();
  }

  // Act on latest keys, unless an obstacle is blocking
  if (obstacleDetected()) {
    stopVehicle();
  } else {
    if      (keys[0] == 1) moveForward();
    else if (keys[2] == 1) moveBackward();
    else if (keys[1] == 1) turnLeft();
    else if (keys[3] == 1) turnRight();
    else                   stopVehicle();
  }

  // Read sensors every SENSOR_INTERVAL ms (blocking ~60ms but non-critical)
  unsigned long now = millis();
  if (now - lastSensorRead >= SENSOR_INTERVAL) {
    lastSensorRead = now;
    readSensors();
  }
}