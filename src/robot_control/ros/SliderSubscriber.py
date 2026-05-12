from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import threading

class SliderSubscriber(Node):
    def __init__(self):
        super().__init__('trajectory_subscriber')

        self.lock = threading.Lock()
        self.latest_data = None

        self.subscription = self.create_subscription(
            Float32MultiArray,
            'slider',
            self.callback,
            10
        )

        self.latest_data = None

    def callback(self, msg):
        with self.lock:
            self.latest_data = list(msg.data)