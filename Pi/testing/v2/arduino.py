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
    sensor_updated = False
    while True:
        with keys_lock:
            current = bytes(keys)

        if current != last_sent:
            arduino.write(current)
            last_sent = current

        while arduino.in_waiting > 0:
            line = arduino.readline().decode(errors='ignore').strip()
            # print(f"RAW: {repr(line)}")  # debug: see everything

            if line.startswith('D:'):
                _parse_sensor_line(line, sensor_distances)
                sensor_updated = True
            elif line:
                print(f"Arduino: {line}")

        if sensor_updated:
            socketio.emit('sensor_update', sensor_distances)
            sensor_updated = False

        socketio.sleep(0.01)


def _parse_sensor_line(line, sensor_distances):
    try:
        parts = line[2:].split(',')
        sensor_distances['s1'] = int(parts[0])
        sensor_distances['s2'] = int(parts[1])
        # print(f"Sensors → s1: {sensor_distances['s1']} mm, s2: {sensor_distances['s2']} mm")
    except (ValueError, IndexError):
        pass
