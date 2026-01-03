#include "Adafruit_VL53L0X.h" //VL53L0X laser-ranging library 

// Define motor control pins for L298N Motor Driver
#define ENA 9  // Enable pin for Motor A (PWM speed control)
#define IN1 8  // Input 1 for Motor A (Direction control)
#define IN2 7  // Input 2 for Motor A (Direction control)
#define ENB 10 // Enable pin for Motor B (PWM speed control)
#define IN3 6  // Input 3 for Motor B (Direction control)
#define IN4 5  // Input 4 for Motor B (Direction control)
const unsigned long RUN_TIME = 5000; // 5 seconds
unsigned long startTime;

// address for the two VL53L0X sensors
#define LOX1_ADDRESS 0x30
#define LOX2_ADDRESS 0x31
int sensor1,sensor2;

// set the pins to shutdown
#define SHT_LOX1 13
#define SHT_LOX2 12

// objects for the vl53l0x
Adafruit_VL53L0X lox1 = Adafruit_VL53L0X();
Adafruit_VL53L0X lox2 = Adafruit_VL53L0X();

// this holds the measurement
VL53L0X_RangingMeasurementData_t measure1;
VL53L0X_RangingMeasurementData_t measure2;

void setID() {
  // all reset
  digitalWrite(SHT_LOX1, LOW);    
  digitalWrite(SHT_LOX2, LOW);
  delay(10);
  // all unreset
  digitalWrite(SHT_LOX1, HIGH);
  digitalWrite(SHT_LOX2, HIGH);
  delay(10);

  // activating LOX1 and reseting LOX2
  digitalWrite(SHT_LOX1, HIGH);
  digitalWrite(SHT_LOX2, LOW);

  // initing LOX1
  if(!lox1.begin(LOX1_ADDRESS)) {
    Serial.println(F("Failed to boot first VL53L0X"));
    while(1);
  }
  delay(10);

  // activating  L0X2
  digitalWrite(SHT_LOX2, HIGH);
  delay(10);

  //initing LOX2
  if(!lox2.begin(LOX2_ADDRESS)) {
    Serial.println(F("Failed to boot second VL53L0X"));
    while(1);
  }
}

void read_dual_sensors() {
  
  lox1.rangingTest(&measure1, false); // pass in 'true' to get debug data printout!
  lox2.rangingTest(&measure2, false); // pass in 'true' to get debug data printout!

  // print sensor one reading
  Serial.print("1: ");
  if(measure1.RangeStatus != 6) {     // if not out of range
    sensor1 = measure1.RangeMilliMeter;    
    Serial.print(sensor1);
    Serial.print("mm");    
  }
  
  Serial.print(" ");

  // print sensor two reading
  Serial.print("2: ");
  if(measure2.RangeStatus != 6) {
    sensor2 = measure2.RangeMilliMeter;
    Serial.print(sensor2);
    Serial.print("mm");
  }
  
  Serial.println();
}

void check_surrounding_area(){
  read_dual_sensors(); //check surrounding area
  while(sensor1 <= 50 || sensor2 <= 50){ // 5cm near
    Serial.println("Object found, impossibile to move rov!");
    read_dual_sensors();
  };
}

void moveForward() {
    digitalWrite(IN1, HIGH); // Motor A: IN1 HIGH, IN2 LOW -> Forward
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH); // Motor B: IN3 HIGH, IN4 LOW -> Forward
    digitalWrite(IN4, LOW);
    analogWrite(ENA, 115); // Set Motor A speed (PWM: 0-255)
    analogWrite(ENB, 115); // Set Motor B speed (PWM: 0-255)
}

void moveBackward() {
    digitalWrite(IN1, LOW); // Motor A: IN1 LOW, IN2 HIGH -> Backward
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, LOW); // Motor B: IN3 LOW, IN4 HIGH -> Backward
    digitalWrite(IN4, HIGH);
    analogWrite(ENA, 115); // Set Motor A speed (PWM: 0-255)
    analogWrite(ENB, 115); // Set Motor B speed (PWM: 0-255)
}

void turnRight(){
    digitalWrite(IN1, LOW); // Motor A: IN1 LOW, IN2 LOW -> STOP
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH); // Motor B: IN3 HIGH, IN4 LOW -> FORWARD
    digitalWrite(IN4, LOW);
    analogWrite(ENB, 115); // Set Motor B speed (PWM: 0-255)
}


void turnLeft(){
    digitalWrite(IN1, HIGH); // Motor A: IN1 HIGH, IN2 LOW -> FORWARD
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW); // Motor B: IN3 LOW, IN4 LOW -> STOP
    digitalWrite(IN4, LOW);
    analogWrite(ENA, 115); // Set Motor A speed (PWM: 0-255)
}

void stopVehicle(){
    digitalWrite(IN1, LOW); // Motor A: IN1 LOW, IN2 LOW -> Stop
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW); // Motor B: IN3 LOW, IN4 LOW -> Stop
    digitalWrite(IN4, LOW);
    analogWrite(ENA, 0);
    analogWrite(ENB, 0);
}

void applyCommand(char command){

  switch(command){
    case 'W':
      Serial.println("Ho ricevuto W");
      break;
    case 'S':
      Serial.println("Ho ricevuto S");
      break;
    case 'D':
      Serial.println("Ho ricevuto D");
      break;
    case 'A':
     Serial.println("Ho ricevuto A");
      break;
    default:
    Serial.println("Ho ricevuto qualcosa di strano!");
      break;
  }
}

// void applyCommand(){
//   read_dual_sensors();
//   startTime = millis();

//   while(true){
//     read_dual_sensors();

//     if(sensor1 <= 50 || sensor2 <= 50){
//       stopVehicle();
//       delay(5000);
//       break;
//     }

//     moveForward();

//     if(millis() - startTime >= RUN_TIME){
//       stopVehicle();
//       delay(5000);
//       break;
//     }
//   }
// }

void setup() {
  Serial.begin(115200);

  // wait until serial port opens for native USB devices
  while (! Serial) { delay(1); }

  // Set all motor driver control and xshut-down pins as outputs
  pinMode(SHT_LOX1, OUTPUT);
  pinMode(SHT_LOX2, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  Serial.println("Shutdown pins inited...");

  digitalWrite(SHT_LOX1, LOW);
  digitalWrite(SHT_LOX2, LOW);

  Serial.println("Both in reset mode...(pins are low)");
  
  
  Serial.println("Starting...");

  setID(); //testing if sensors vl53l0x works
  check_surrounding_area(); //check if object near to rov
}

void loop(){
 if(Serial.available() > 0){
    char command = Serial.read();
    // command.trim();

    applyCommand(command);
    read_dual_sensors();
  }
}