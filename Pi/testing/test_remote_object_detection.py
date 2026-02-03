from flask import Flask, Response, render_template, jsonify, request
from picamera2 import Picamera2
from ultralytics import YOLO
import cv2
import time


# Set up the camera with Picamera
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
picam2.preview_configuration.align()
picam2.configure(config)
picam2.start()
time.sleep(5)  # Camera warm-up

# Load YOLO
model = YOLO("yolo11n_ncnn_model", task="detect", verbose=True)

#keep track of the object for Flask
list_objects = {
    "fps": None,
    "objects": []
}

# Flask object
app = Flask(__name__)

# Function to generate frames from the camera
def generate_frames():
    while True:
        frame = picam2.capture_array()

        # Convert RGB → BGR for OpenCV
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Run YOLO model on the captured frame and store the results
        results = model.track(frame, conf=0.5, persist=True)

        # Output the visual detection data, we will draw this on our camera preview window
        annotated_frame = results[0].plot()

        # Get inference time
        inference_time = results[0].speed.get("inference", 0)
        fps = 1000 / inference_time if inference_time > 0 else 0  # Convert to milliseconds
        text = f'FPS: {fps:.1f}'

        # objects to json
        populate_dictionary_with_objects(results[0], fps)

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
def populate_dictionary_with_objects(model_results, fps):
    global list_objects

    list_objects["fps"] = fps
    list_objects["objects"] = [] # keeps track of the current objects, removing the old ones


    for box in model_results.boxes:
        if box.id is None:
            continue  # skip untracked detections

        # object_id = int(box.id) if box.id is not None else None
        object_id = int(box.id)
        class_id = int(box.cls[0])
        class_name = model_results.names[class_id]
        confidence = float(box.conf[0])

        list_objects["objects"].append({
            "object_id": object_id,
            "class_id": class_id,
            "class_name": class_name,
            "confidence": confidence
        })



# Route to serve the video stream
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')




# Route to show the list of object detected from the model
@app.route('/get_list_objects')
def get_list_objects():
    return jsonify(list_objects)



# Route to receive the object to track
@app.route('/tracking_object', methods=['POST'])
def tracking_object():
    if request.method == 'POST':
        object_name = data.get['object_id']
        object_class = data.get['class_name']





# Route to stop tracking and ROV
@app.route('/stop_tracking_rov', methods=['POST'])
def stop_tracking_rov():
    pass



# Route to serve the HTML page that displays the video stream
@app.route('/')
def index():
    return render_template("index.html")



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

