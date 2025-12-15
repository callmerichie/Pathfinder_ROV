/*
Program: Send Strings to Raspberry Pi
File: send_string_to_raspberrypi.ino
Description: Send strings from Arduino to a Raspberry Pi
Author: Addison Sears-Collins
Website: https://automaticaddison.com
Date: July 5, 2020
*/
 
void setup(){
   
  // Set the baud rate  
  Serial.begin(9600);
   
}
 
void loop(){
   
  // Print "Hello World" every second
  // We do println to add a new line character '\n' at the end
  // of the string.
  Serial.println("Hello! My name is Arduino.");
  delay(1000);
}