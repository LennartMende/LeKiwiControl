from rclpy.node import Node
from std_msgs.msg import Float32MultiArray

class TrajectoryPublisher(Node):
    def __init__(self):
        super().__init__('trajectory_publisher')
        self.pub = self.create_publisher(Float32MultiArray, 'trajectory', 10)

    def publish(self, msg):
        self.pub.publish(msg)