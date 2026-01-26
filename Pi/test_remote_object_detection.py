from flask import Flask, Response, render_template
from picamera2 import Picamera2
from ultralytics import YOLO
import cv2
import json
import time


# log file to keep track for each models performance & let the user see a list of the objects that the camera caputre


# Set up the camera with Picamera
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
picam2.preview_configuration.align()
picam2.configure(config)
picam2.start()
time.sleep(2)  # Camera warm-up

# Load YOLO
model = YOLO("yolo11n_ncnn_model", task="detect", verbose=True)


# Flask object
app = Flask(__name__)

# Function to generate frames from the camera
def generate_frames():
    while True:
        frame = picam2.capture_array()

        # Convert RGB → BGR for OpenCV
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Run YOLO model on the captured frame and store the results
        results = model(frame, conf=0.5)

        # Output the visual detection data, we will draw this on our camera preview window
        annotated_frame = results[0].plot()

        # Get inference time
        inference_time = results[0].speed['inference']
        fps = 1000 / inference_time  # Convert to milliseconds
        text = f'FPS: {fps:.1f}'

        # objects to json
        objects_dictionary_to_json(results[0], fps)

        # Define font and position
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 1, 2)[0]
        text_x = annotated_frame.shape[1] - text_size[0] - 10  # 10 pixels from the right
        text_y = text_size[1] + 10  # 10 pixels from the top

        # Draw the text on the annotated frame
        cv2.putText(annotated_frame, text, (text_x, text_y), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            frame_bytes +
            b'\r\n'
        )


# storing the identified objects to a json
def objects_dictionary_to_json(model_results, fps):
    # dictionary structure
    latest_objects = {"time": time.time(), "fps": fps, "objects":[]}
    count = 1

    for box in model_results.boxes:
        class_id = int(box.cls[0])
        class_name = model_results.names[class_id]
        confidence = float(box.conf[0])

        latest_objects["objects"].append({
            "class_id": class_id,
            "class_name": class_name,
            "confidence": confidence,
            "count": count
        })

        print(latest_objects)


    with open('./output.json', 'w') as outfile:
        json.dump(latest_objects, outfile, indent=4)


# Route to serve the video stream
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route to show the list of object detected from the model
@app.route('/get_list_objects')
def get_list_objects():
    pass


# Route to serve the HTML page that displays the video stream
@app.route('/')
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

