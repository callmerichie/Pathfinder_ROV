import serial

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.flushInput()
ser.flushOutput()

