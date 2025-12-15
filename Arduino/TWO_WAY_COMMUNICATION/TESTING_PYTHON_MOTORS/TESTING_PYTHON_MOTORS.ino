  // Define motor control pins for L298N Motor Driver
  #define ENA 9  // Enable pin for Motor A (PWM speed control)
  #define IN1 8  // Input 1 for Motor A (Direction control)
  #define IN2 7  // Input 2 for Motor A (Direction control)
  #define ENB 10 // Enable pin for Motor B (PWM speed control)
  #define IN3 6  // Input 3 for Motor B (Direction control)
  #define IN4 5  // Input 4 for Motor B (Direction control)
  #define string DIRECTION_RIGHT //INPUT FOR RIGHT MOTOR
  #define string DIRECTION_LEFT //INPUT FOR LEFT MOTOR

void setup() {
  // Set the baud rate  
  Serial.begin(9600);

  // Set all motor driver control pins as outputs
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
   if(Serial.available() > 0) {
    DIRECTION_RIGHT = Serial.readStringUntil('\n');
    Serial.print("Hi Raspberry Pi! You sent me: ");
    Serial.println(data);
  }

}


void moveForward() {
    digitalWrite(IN1, HIGH); // Motor A: IN1 HIGH, IN2 LOW -> Forward
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH); // Motor B: IN3 HIGH, IN4 LOW -> Forward
    digitalWrite(IN4, LOW);
}

void moveBackward() {
    digitalWrite(IN1, LOW); // Motor A: IN1 LOW, IN2 HIGH -> Backward
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, LOW); // Motor B: IN3 LOW, IN4 HIGH -> Backward
    digitalWrite(IN4, HIGH);
}

void stopVehicle(){
    digitalWrite(IN1, LOW); // Motor A: IN1 LOW, IN2 LOW -> Stop
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW); // Motor B: IN3 LOW, IN4 LOW -> Stop
    digitalWrite(IN4, LOW);
}