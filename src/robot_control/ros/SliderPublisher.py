from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from robot_control.data.default_arm_poses import CLOSED_REST
import numpy as np

class SliderPublisher(Node):
    """
    Publisht die Daten der Slider als Float32MultiArray auf dem ROS-Topic 'slider'.
     - Die Daten werden von der GUI als Liste von 6 Werten empfangen, die die Positionen der 6 Slider repräsentieren.
    """
    def __init__(self):
        super().__init__('slider_publisher')
        self.publisher = self.create_publisher(Float32MultiArray, 'slider', 10)

    def publish(self, data):
        msg = Float32MultiArray()
        msg.data = self.slider_to_real(data)
        self.publisher.publish(msg)
        # print("target_trajectory:", data)

    def slider_to_real(self, data):
        """
        Konvertiert die Daten der Slider für die URDF in reale Werte für die Robotersteuerung.
        """
        # print("data = ", data)
        for i in range(len(data)):
            data[i] = np.rad2deg(data[i])
        # print("new data = ", data)
        
        data[0] = data[0] + CLOSED_REST['arm_shoulder_pan.pos']
        data[1] = - data[1] + CLOSED_REST['arm_shoulder_lift.pos']
        data[2] = - data[2] + CLOSED_REST['arm_elbow_flex.pos']
        data[3] =  - data[3] + CLOSED_REST['arm_wrist_flex.pos']
        data[4] = 0.5 * (- data[4]) + CLOSED_REST['arm_wrist_roll.pos']
        data[5] = - data[5] + CLOSED_REST['arm_gripper.pos']
        # print("slider_to_real from slider_control.py:", data)
        return data