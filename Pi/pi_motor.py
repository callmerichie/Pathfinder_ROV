import serial
import time

arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
time.sleep(5)

arduino.reset_output_buffer()
arduino.reset_input_buffer()

commands = ['W','S','D','A']

if (arduino.in_waiting > 0):
    line = arduino.readline().decode('ASCII').strip()
    print("Arduino received:" + line)

while True:
    arduino.write(commands[0].encode('ASCII'))
    time.sleep(5)
    arduino.write(commands[1].encode('ASCII'))
    time.sleep(5)
    arduino.write(commands[2].encode('ASCII'))
    time.sleep(5)
    arduino.write(commands[3].encode('ASCII'))
    time.sleep(5)

    if(arduino.in_waiting > 0):
        line = arduino.readline().decode('ASCII').strip()
        print("Arduino received:" + line)

