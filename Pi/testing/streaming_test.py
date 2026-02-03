from flask import Flask, Response
from picamera2 import Picamera2
import cv2
import time

picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()
time.sleep(2)  # Camera warm-up

app = Flask(__name__)

# Function to generate frames from the camera
def generate_frames():
    while True:
        frame = picam2.capture_array()

        # Convert RGB → BGR for OpenCV
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
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
