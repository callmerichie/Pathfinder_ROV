# PathFinder ROW

The project consists of a land-based ROV remotely controlled by the user.
Specifically, the structure of the ROV is divided as follows:

Mechanical section: Managed by an Arduino R1. Using two DC motors connected to an L298N motor controller, the vehicle can be moved. VL53L0X sensors will also be added to the front of the ROV, allowing it to detect surrounding objects up to 2 meters away and avoid collisions (Collision Avoidance).

‘Smart’ section: A Raspberry Pi 4B will be used, connected via serial to the Arduino board, in order to divide tasks and balance the workload. A camera will be installed to provide video streaming to the user. The Raspberry Pi will run Object Detection models, allowing the user to select a recognized object and have the ROV navigate intelligently and autonomously up to the collision limit of the selected object. The user will therefore have two driving modes: manual mode and autonomous mode based on the chosen object.

Communication: The user will connect remotely and use a web page to send commands to the Raspberry Pi. Since remote access is involved, I plan to use a VPS as a bridge between the user and the Raspberry Pi board.


<img width="401" height="251" alt="architettura_pathfindeer drawio" src="https://github.com/user-attachments/assets/e1361ac5-a300-49b7-8b3c-9215857f79a7" />

# Testing each component

- Arudino:
    1. Testing: 
       - Sensors VL53L0X shares the same bus, that means to give each sensor a unique I²C address in software and use the XSHUT pin on each sensor so you can turn them on one at a time and change their address.
         <img width="2888" height="1782" alt="VL53L0X" src="https://github.com/user-attachments/assets/f90b7cb9-e139-4b68-9030-81707e956dbd" /><br>
       - L298N Motor Controller and the motors powered by 4 AA batteries 1.2V with a total of 4.8V
         <img width="2976" height="1658" alt="l298n-arduino_bb" src="https://github.com/user-attachments/assets/8f8e8c80-7f9f-45e8-acd9-b85705d65529" /><br>
       - Combination of the two VL53L0X laser-ranging modules with the L298N motor controller
         <img width="3335" height="2738" alt="VL53L0X-L298N" src="https://github.com/user-attachments/assets/6049aca2-4d41-442f-9342-d74e38c2aa2d" /><br>


         
- Raspberry PI:
    1. Testing:
       - Arducam OV5647 camera module with built-in motorized IR-CUT filter attached via CSI.
         1. Picamera2 
         2. Picamera2 with Flask for localhost streaming
       - Testing Streaming while using Object Detection models:
         a. yolo11n & yolo11n_ncnnn_model ( Ideal for resource-constrained devices like Raspberry Pi and NVIDIA Jetson. NCNN can provide significant performance improvements.
         credits: https://docs.ultralytics.com/integrations/ncnn/#why-export-to-ncnn)
         <img width="713" height="579" alt="Screenshot 2026-01-19 171321" src="https://github.com/user-attachments/assets/f5abbdb0-e118-4fb7-8402-d679f78d4cff" /><br>
         b. yolov8n & yolov8n_ncnn_model <br>
         c. yolov5n & yolov5n_ncnn_model <br>
       - Two-way communication PI-Arduino
         1. find the ttyACM0 port (USB-ARDUINO)
         2. set the baud rate to 115200 (stty -F /dev/ttyACM0 115200)
       - UPS for power supply with 1 18650 battery

