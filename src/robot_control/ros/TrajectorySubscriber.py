from rclpy.node import Node
from std_msgs.msg import Float32MultiArray

class TrajectorySubscriber(Node):
    def __init__(self):
        super().__init__('trajectory_subscriber')

        self.subscription = self.create_subscription(
            Float32MultiArray,
            'trajectory',
            self.callback,
            10
        )

        self.latest_data = None

    def callback(self, msg):
        self.latest_data = msg.data