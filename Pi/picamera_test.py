#testing image and video

from picamera2 import Picamera2, Preview
import time

picamera = Picamera2()
camera_config = picamera.create_config()
picamera.configure(camera_config)
picamera.start_preview(Preview.DRM)
picamera.start()

time.sleep(5)

picamera.capture_file('test_picamera.jpg')
picamera.start_and_record_video('test_video_picamera.mp4',duration=10)

picamera.stop()