import serial
import time


def init_arduino():
    arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    time.sleep(5)
    arduino.reset_output_buffer()
    arduino.reset_input_buffer()
    return arduino


def driving_rov(arduino, keys, keys_lock, socketio, sensor_distances):
    last_sent = None
    while True:
        with keys_lock:
            current = bytes(keys)

        if current != last_sent:
            arduino.write(current)
            last_sent = current

        while arduino.in_waiting > 0:
            line = arduino.readline().decode(errors='ignore').strip()

            if line.startswith('D:'):
                _parse_sensor_line(line, sensor_distances, socketio)
            elif line:
                print(f"Arduino: {line}")

        socketio.sleep(0.01)


def _parse_sensor_line(line, sensor_distances, socketio):
    try:
        parts = line[2:].split(',')
        sensor_distances['s1'] = int(parts[0])
        sensor_distances['s2'] = int(parts[1])
        socketio.emit('sensor_update', sensor_distances)
    except (ValueError, IndexError):
        pass