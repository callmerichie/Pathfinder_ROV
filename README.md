# PathFinder ROW

The project consists of a land-based ROV remotely controlled by the user.
Specifically, the structure of the ROV is divided as follows:

Mechanical section: Managed by an Arduino R1. Using two DC motors connected to an L298N motor controller, the vehicle can be moved. VL53L0X sensors will also be added to the front of the ROV, allowing it to detect surrounding objects up to 2 meters away and avoid collisions (Collision Avoidance).

‘Smart’ section: A Raspberry Pi 4B will be used, connected via serial to the Arduino board, in order to divide tasks and balance the workload. A camera will be installed to provide video streaming to the user. The Raspberry Pi will run Object Detection models, allowing the user to select a recognized object and have the ROV navigate intelligently and autonomously up to the collision limit of the selected object. The user will therefore have two driving modes: manual mode and autonomous mode based on the chosen object.

Communication: The user will connect remotely and use a web page to send commands to the Raspberry Pi. Since remote access is involved, I plan to use a VPS as a bridge between the user and the Raspberry Pi board.


<img width="401" height="251" alt="architettura_pathfindeer drawio" src="https://github.com/user-attachments/assets/e1361ac5-a300-49b7-8b3c-9215857f79a7" />

# Working Method

- Arudino:
    1. Testing: 
       - Sensors VL53L0X shares the same bus, that means to give each sensor a unique I²C address in software and use the XSHUT pin on each sensor so you can turn them on one at a time and change their address.
         - schema
       - L298N Motor Controller and the motors powered by 4 AA batteries 1.2V with a total of 4.8V
         <img width="2976" height="1658" alt="l298n-arduino_bb" src="https://github.com/user-attachments/assets/8f8e8c80-7f9f-45e8-acd9-b85705d65529" />

         
- Raspberry PI:
    1. Testing:
       - Arducam OV5647 camera module with built-in motorized IR-CUT filter attached via CSI.
         1. Picamaera2 
         2. Picamaera2 with Flask for localhost streaming
       - UPS for power supply with 1 18650 battery
       - Two-way communication PI-Arduino
         1. find the ttyACM0 port (USB-ARDUINO)
         2. set the baud rate to 9600 (stty -F /dev/ttyACM0 9600)
