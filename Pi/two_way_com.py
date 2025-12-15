#!/usr/bin/env python3

###############################################################################
# Program: Receive Strings From an Arduino
# File: receive_string_from_arduino.py
# Description: This program runs on a Raspberry Pi. It receives a string from
#  Arduino and prints that string to the screen.
# Author: Addison Sears-Collins
# Website: https://automaticaddison.com
# Date: July 5, 2020
###############################################################################

import serial  # Module needed for serial communication

# Set the port name and the baud rate. This baud rate should match the
# baud rate set on the Arduino.
# Timeout parameter makes sure that program doesn't get stuck if data isn't
# being received. After 1 second, the function will return with whatever data
# it has. The readline() function will only wait 1 second for a complete line
# of input.
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

# Get rid of garbage/incomplete data
ser.flush()

# Infinite loop
while (1):

    # If there is data available
    if (ser.in_waiting > 0):
        # Read everything until the new line character
        # Convert the data from a byte into a string of type 'utf-8'
        # You could also use 'ascii'
        # rstrip() function removes trailing characters like
        # the new line character '\n'
        line = ser.readline().decode('utf-8').rstrip()

        # Print the data received from the Arduino
        print(line)