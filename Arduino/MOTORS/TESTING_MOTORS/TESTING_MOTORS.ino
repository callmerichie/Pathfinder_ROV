// Define motor control pins for L298N Motor Driver
#define ENA 9  // Enable pin for Motor A (PWM speed control)
#define IN1 8  // Input 1 for Motor A (Direction control)
#define IN2 7  // Input 2 for Motor A (Direction control)
#define ENB 10 // Enable pin for Motor B (PWM speed control)
#define IN3 6  // Input 3 for Motor B (Direction control)
#define IN4 5  // Input 4 for Motor B (Direction control)

void setup() {
    // Set all motor driver control pins as outputs
    pinMode(ENA, OUTPUT);
    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    pinMode(ENB, OUTPUT);
    pinMode(IN3, OUTPUT);
    pinMode(IN4, OUTPUT);
}

void loop() {
    // Move Forward - Both motors rotate in the same direction
    digitalWrite(IN1, HIGH); // Motor A: IN1 HIGH, IN2 LOW -> Forward
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH); // Motor B: IN3 HIGH, IN4 LOW -> Forward
    digitalWrite(IN4, LOW);
    analogWrite(ENA, 150); // Set Motor A speed (PWM: 0-255)
    analogWrite(ENB, 150); // Set Motor B speed (PWM: 0-255)
    delay(2000); // Move forward for 2 seconds

    // Move Backward - Both motors rotate in the opposite direction
    digitalWrite(IN1, LOW); // Motor A: IN1 LOW, IN2 HIGH -> Backward
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, LOW); // Motor B: IN3 LOW, IN4 HIGH -> Backward
    digitalWrite(IN4, HIGH);
    analogWrite(ENA, 150); // Set Motor A speed (PWM: 0-255)
    analogWrite(ENB, 150); // Set Motor B speed (PWM: 0-255)
    delay(2000); // Move backward for 2 seconds

    // Stop - Both motors stop
    digitalWrite(IN1, LOW); // Motor A: IN1 LOW, IN2 LOW -> Stop
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW); // Motor B: IN3 LOW, IN4 LOW -> Stop
    digitalWrite(IN4, LOW);
    delay(2000); // Stay stopped for 2 seconds
}
