from flask import Flask, Response
from picamera2 import Picamera2
from ultralytics import YOLO
import cv2
import time

# Set up the camera with Picam
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
picam2.preview_configuration.align()
picam2.configure(config)
picam2.start()
time.sleep(2)  # Camera warm-up

# Load YOLOv8
model = YOLO("yolov8n.pt")

app = Flask(__name__)

# Function to generate frames from the camera
def generate_frames():
    while True:
        frame = picam2.capture_array()

        # Convert RGB → BGR for OpenCV
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Run YOLO model on the captured frame and store the results
        results = model(frame)

        # Output the visual detection data, we will draw this on our camera preview window
        annotated_frame = results[0].plot()

        # Get inference time
        inference_time = results[0].speed['inference']
        fps = 1000 / inference_time  # Convert to milliseconds
        text = f'FPS: {fps:.1f}'

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



# Route to serve the video stream
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route to serve the HTML page that displays the video stream
@app.route('/')
def index():
    return '''
        <html>
            <head>
                <title>Live Video Stream</title>
            </head>
            <body>
                <h1>Live Video Feed</h1>
                <img src="/video_feed" style="width:640px; height:480px;">
            </body>
        </html>
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

