  // Define motor control pins for L298N Motor Driver
  #define ENA 9  // Enable pin for Motor A (PWM speed control)
  #define IN1 8  // Input 1 for Motor A (Direction control)
  #define IN2 7  // Input 2 for Motor A (Direction control)
  #define ENB 10 // Enable pin for Motor B (PWM speed control)
  #define IN3 6  // Input 3 for Motor B (Direction control)
  #define IN4 5  // Input 4 for Motor B (Direction control)
  enum Direction {
    STOP,
    FORWARD,
    BACKWARD,
    LEFT,
    RIGHT
  };

  Direction currentDirection = STOP;

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
    char cmd = Serial.read();

    switch(cmd){
      case 'W': currentDirection = FORWARD; break; 
      case 'S': currentDirection = BACKWARD; break;
      case 'A': currentDirection = LEFT; break;
      case 'D': currentDirection = RIGHT; break;
      default: currentDirection = STOP; break;
    }

    ApplyDirection();
  }

}

void ApplyDirection(){
  switch(currentDirection){
    case FORWARD: moveForward(); break;
    case BACKWARD: moveBackward(); break;
    case LEFT: turnLeft(); break;
    case RIGHT: turnRight(); break;
    default: stopVehicle(); break;
  }
}

void moveForward() {
    digitalWrite(IN1, HIGH); // Motor A: IN1 HIGH, IN2 LOW -> Forward
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH); // Motor B: IN3 HIGH, IN4 LOW -> Forward
    digitalWrite(IN4, LOW);
    analogWrite(ENA, 100); // Set Motor A speed (PWM: 0-255)
    analogWrite(ENB, 100); // Set Motor B speed (PWM: 0-255)
}

void moveBackward() {
    digitalWrite(IN1, LOW); // Motor A: IN1 LOW, IN2 HIGH -> Backward
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, LOW); // Motor B: IN3 LOW, IN4 HIGH -> Backward
    digitalWrite(IN4, HIGH);
    analogWrite(ENA, 100); // Set Motor A speed (PWM: 0-255)
    analogWrite(ENB, 100); // Set Motor B speed (PWM: 0-255)
}

void turnRight(){
    digitalWrite(IN1, LOW); // Motor A: IN1 LOW, IN2 LOW -> STOP
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH); // Motor B: IN3 HIGH, IN4 LOW -> FORWARD
    digitalWrite(IN4, LOW);
    analogWrite(ENB, 100); // Set Motor B speed (PWM: 0-255)
}


void turnLeft(){
    digitalWrite(IN1, HIGH); // Motor A: IN1 HIGH, IN2 LOW -> FORWARD
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW); // Motor B: IN3 LOW, IN4 LOW -> STOP
    digitalWrite(IN4, LOW);
    analogWrite(ENA, 100); // Set Motor A speed (PWM: 0-255)
}

void stopVehicle(){
    digitalWrite(IN1, LOW); // Motor A: IN1 LOW, IN2 LOW -> Stop
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW); // Motor B: IN3 LOW, IN4 LOW -> Stop
    digitalWrite(IN4, LOW);
    analogWrite(ENA, 0);
    analogWrite(ENB, 0);
}