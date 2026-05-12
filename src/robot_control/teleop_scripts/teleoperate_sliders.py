#!/usr/bin/env python3

import time
import threading
import numpy as np
import array

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray

from lerobot.robots.lekiwi import LeKiwiClient, LeKiwiClientConfig
from lerobot.teleoperators.keyboard.teleop_keyboard import KeyboardTeleop, KeyboardTeleopConfig
from lerobot.utils.robot_utils import busy_wait

try:
    from lerobot.utils.visualization_utils import init_rerun, log_rerun_data
except ImportError:
    init_rerun = lambda *args, **kwargs: None
    log_rerun_data = lambda *args, **kwargs: None

# =========================
# ROS NODE: SUBSCRIBER
# =========================
class SliderSubscriber(Node): # auch von ros-Ordner importierbar
    def __init__(self):
        super().__init__('slider_subscriber')

        self.lock = threading.Lock()
        self.latest_data = None

        self.subscription = self.create_subscription(
            Float32MultiArray,
            'slider',
            self.callback,
            10
        )

        self.latest_data = None  # hier speichern wir die Daten

    def callback(self, msg):
        with self.lock:
            self.latest_data = list(msg.data)


# =========================W
# ROS NODE: PUBLISHER
# =========================
class TrajectoryPublisher(Node): # auch von ros-Ordner importierbar
    def __init__(self):
        super().__init__('trajectory_publisher')
        self.pub = self.create_publisher(Float32MultiArray, 'trajectory', 10)

    def publish(self, msg):
        self.pub.publish(msg)



FPS = 30


# Create the robot and teleoperator configurations
robot_config = LeKiwiClientConfig(remote_ip="192.168.0.242", id="my_lekiwi")
keyboard_config = KeyboardTeleopConfig(id="my_laptop_keyboard")

# Initialize the robot and teleoperator
robot = LeKiwiClient(robot_config)
keyboard = KeyboardTeleop(keyboard_config)

# Connect to the robot and teleoperator
# To connect you already should have this script running on LeKiwi: `python -m lerobot.robots.lekiwi.lekiwi_host --robot.id=my_awesome_kiwi`
robot.connect()
keyboard.connect()

# Init rerun viewer
init_rerun(session_name="lekiwi_teleop")


# =========================
# ROS SETUP
# =========================
rclpy.init(args=None)
ros_pub = TrajectoryPublisher()
ros_sub = SliderSubscriber()

def get_action(action: dict[str, float]) -> dict[str, float]:
    start = time.perf_counter()
    action = {f"{motor}.pos": val for motor, val in action.items()}
    dt_ms = (time.perf_counter() - start) * 1e3
    return action

def arm_action_to_bits(action: dict[str, float]) -> dict[str, float]:
    action['arm_shoulder_pan.pos'] = 2047 + 647 + action['arm_shoulder_pan.pos'] * 11.3636 # now joint_value is in bits
    action['arm_shoulder_lift.pos'] = 2047 - 37 + action['arm_shoulder_lift.pos'] * 11.3636 # now joint_value is in bits
    action['arm_elbow_flex.pos'] = 2047 - 974 + action['arm_elbow_flex.pos'] * 11.3636 # now joint_value is in bits
    action['arm_wrist_flex.pos'] = 2047 - 223 + action['arm_wrist_flex.pos'] * 11.3636 # now joint_value is in bits
    action['arm_wrist_roll.pos'] = 2047 + 427 + action['arm_wrist_roll.pos'] * 11.3636 # now joint_value is in bits
    action['arm_gripper.pos'] = 2047 - 850 + action['arm_gripper.pos'] * 11.3636 # now joint_value is in bits
    return action

print("Starting teleop loop...")
#try:
while True:
    try:
        t0 = time.perf_counter()

        # Get robot observation
        observation = robot.get_observation()

        # Get teleop action
        # Arm
        with ros_sub.lock:
            data = ros_sub.latest_data.copy() if ros_sub.latest_data is not None else None
        # if data is None:
        #     print("ROS data is None:\nROS-data is: ", None)
        # else:
        #     print("ROS data is not None, ROS data is: ", data)
        #arm_action = {f"arm_{k}": v for k, v in arm_action.items()}
        # Keyboard
        if ros_sub.latest_data is not None:
            keyboard_keys = keyboard.get_action()
            base_action = robot._from_keyboard_to_base_action(keyboard_keys)

            arm_action = {
                'arm_shoulder_pan.pos': data[0], 
                'arm_shoulder_lift.pos': data[1], 
                'arm_elbow_flex.pos': data[2], 
                'arm_wrist_flex.pos': data[3], 
                'arm_wrist_roll.pos': data[4], 
                'arm_gripper.pos': data[5]
            }

            action = {**arm_action, **base_action} if len(base_action) > 0 else arm_action

            # print(f"\naction = {action}\n")
            
            # Send action to robot
            _ = robot.send_action(action)

            # Visualize
            log_rerun_data(observation=observation, action=action)

        # Publish the trajectory to ROS topic
        # print("observation.value = ", list(observation.values())[:9])
        msg = Float32MultiArray()
        msg.data = [float(v) for v in list(observation.values())[:9]]
        # print("msg.data:", msg.data)
        ros_pub.publish(msg)

        rclpy.spin_once(ros_sub, timeout_sec=0)

        # print("duration = ", max(1.0 / FPS - (time.perf_counter() - t0), 0.0))
        busy_wait(max(1.0 / FPS - (time.perf_counter() - t0), 0.0))
    except rclpy._rclpy_pybind11.RCLError:
        print("ROS context invalid → exiting loop")
        break