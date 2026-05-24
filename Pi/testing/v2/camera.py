import cv2
import time
import threading
from picamera2 import Picamera2
from ultralytics import YOLO


_STREAM_SIZE = (640, 480)
_INFER_SIZE  = (320, 240)   # YOLO runs here — 4x fewer pixels than stream size
_SCALE_X = _STREAM_SIZE[0] / _INFER_SIZE[0]   # 2.0
_SCALE_Y = _STREAM_SIZE[1] / _INFER_SIZE[1]   # 2.0
_JPEG_PARAMS = [cv2.IMWRITE_JPEG_QUALITY, 75]
_STREAM_FPS_CAP = 1 / 30


def init_camera():
    picam2 = Picamera2()
    config = picam2.create_video_configuration(
        main={"size": _STREAM_SIZE, "format": "BGR888"}
    )
    picam2.preview_configuration.align()
    picam2.configure(config)
    picam2.start()
    time.sleep(5)  # Camera warm-up
    return picam2


def load_model():
    return YOLO("../yolo11n_ncnn_model", task="detect", verbose=False)


class CameraStream:
    """
    Three independent threads:
      - capture:   fills _latest_raw as fast as the camera allows
      - inference: reads _latest_raw, runs YOLO on a downscaled copy, stores boxes
      - generator: reads _latest_raw + boxes, draws overlay, yields fresh JPEGs
    Inference FPS and stream FPS are fully decoupled.
    """

    def __init__(self, picam2, model, list_objects, object_tracked):
        self._picam2 = picam2
        self._model = model
        self._list_objects = list_objects
        self._object_tracked = object_tracked

        self._latest_raw = None
        self._raw_lock = threading.Lock()

        self._boxes = None
        self._names = None
        self._fps = 0.0
        self._result_lock = threading.Lock()

        threading.Thread(target=self._capture_loop, daemon=True).start()
        threading.Thread(target=self._inference_loop, daemon=True).start()

    # --- internal threads ---

    def _capture_loop(self):
        while True:
            frame = self._picam2.capture_array()
            with self._raw_lock:
                self._latest_raw = frame

    def _inference_loop(self):
        while True:
            with self._raw_lock:
                frame = self._latest_raw

            if frame is None:
                time.sleep(0.01)
                continue

            small = cv2.resize(frame, _INFER_SIZE)
            results = self._model.track(small, conf=0.5, persist=True, verbose=False)

            inference_time = results[0].speed.get("inference", 0)
            fps = 1000 / inference_time if inference_time > 0 else 0

            _populate_objects(results[0], fps, self._list_objects)

            with self._result_lock:
                self._boxes = results[0].boxes
                self._names = results[0].names
                self._fps = fps

    # --- public ---

    def generate_frames(self):
        font = cv2.FONT_HERSHEY_SIMPLEX

        while True:
            with self._raw_lock:
                raw = self._latest_raw

            if raw is None:
                time.sleep(0.05)
                continue

            frame = raw.copy()  # never draw on the shared array

            with self._result_lock:
                boxes = self._boxes
                names = self._names
                fps = self._fps

            tracking_enabled = self._object_tracked["enabled"]
            tracked_id = self._object_tracked["object_id"] if tracking_enabled else None

            # Draw last-known boxes scaled back to stream resolution
            if boxes is not None:
                for box in boxes:
                    if box.id is None:
                        continue

                    box_id = int(box.id[0])

                    if tracking_enabled and box_id != tracked_id:
                        continue

                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    x1, x2 = int(x1 * _SCALE_X), int(x2 * _SCALE_X)
                    y1, y2 = int(y1 * _SCALE_Y), int(y2 * _SCALE_Y)

                    class_id = int(box.cls[0])
                    label = f"{names[class_id]} {float(box.conf[0]):.2f}"

                    if tracking_enabled:
                        color = (0, 0, 255)
                        label = f"TRACKING: {label}"
                    else:
                        color = (0, 255, 0)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, label, (x1, max(y1 - 10, 0)),
                                font, 0.5, color, 2)

            text = f'FPS: {fps:.1f}'
            text_size = cv2.getTextSize(text, font, 1, 2)[0]
            cv2.putText(frame, text,
                        (frame.shape[1] - text_size[0] - 10, text_size[1] + 10),
                        font, 1, (255, 255, 255), 2, cv2.LINE_AA)

            ret, buffer = cv2.imencode('.jpg', frame, _JPEG_PARAMS)
            if not ret:
                continue

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' +
                buffer.tobytes() +
                b'\r\n'
            )

            time.sleep(_STREAM_FPS_CAP)  # don't spin faster than 30fps


def _populate_objects(model_results, fps, list_objects):
    list_objects["fps"] = fps
    list_objects["objects"] = []

    for box in model_results.boxes:
        if box.id is None:
            continue

        class_id = int(box.cls[0])
        list_objects["objects"].append({
            "object_id": int(box.id),
            "class_id": class_id,
            "class_name": model_results.names[class_id],
            "confidence": float(box.conf[0])
        })