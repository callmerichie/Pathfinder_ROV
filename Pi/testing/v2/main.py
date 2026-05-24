import threading

from camera import init_camera, load_model, CameraStream
from arduino import init_arduino, driving_rov
from battery import battery_task
from app import create_app


# --- Shared state ---
list_objects    = {"fps": None, "objects": []}
object_tracked  = {"enabled": False, "object_id": None, "class_name": None}
sensor_distances = {"s1": -1, "s2": -1}   # -1 = not yet read / out of range
keys      = [0, 0, 0, 0]
keys_lock = threading.Lock()

# --- Hardware init ---
picam2  = init_camera()
model   = load_model()
arduino = init_arduino()

# --- Camera stream (starts inference thread immediately) ---
camera_stream = CameraStream(picam2, model, list_objects, object_tracked)

# --- App init ---
app, socketio = create_app(camera_stream, list_objects, object_tracked, keys, keys_lock)


if __name__ == "__main__":
    socketio.start_background_task(driving_rov, arduino, keys, keys_lock, socketio, sensor_distances)
    socketio.start_background_task(battery_task, socketio)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, use_reloader=False)