#testing image and video remotely
from picamera2 import Picamera2, Preview
import time

picamera = Picamera2()

#photo
camera_config = picamera.create_still_configuration(main={"size": (1920, 1080)}, lores={"size": (640, 480)}, display="lores")
picamera.configure(camera_config)

picamera.start()
time.sleep(5)
picamera.capture_file('test_picamera.jpg')
picamera.stop()

#video
camera_config = picamera.create_video_configuration(main={"size": (1920, 1080)}, lores={"size": (640, 480)}, display="lores")
picamera.configure(camera_config)

picamera.start()
time.sleep(5)
picamera.start_and_record_video('test_video_picamera.mp4',duration=10)
picamera.stop()