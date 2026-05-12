# !/usr/bin/env python

# Copyright 2025 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


### IMPORTS ###
import time

from lerobot.robots.lekiwi import LeKiwiClient, LeKiwiClientConfig
from lerobot.teleoperators.keyboard.teleop_keyboard import KeyboardTeleop, KeyboardTeleopConfig
from lerobot.teleoperators.so100_leader import SO100Leader, SO100LeaderConfig
from lerobot.utils.robot_utils import busy_wait
from torchgen.executorch.api.et_cpp import return_type

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray

try:
    from lerobot.utils.visualization_utils import init_rerun, log_rerun_data
except ImportError:
    init_rerun = lambda *args, **kwargs: None
    log_rerun_data = lambda *args, **kwargs: None

### CONFIGURATION ###
FPS = 30

# Create the robot and teleoperator configurations
robot_config = LeKiwiClientConfig(remote_ip="192.168.0.242", id="my_lekiwi")
teleop_arm_config = SO100LeaderConfig(port="/dev/ttyACM0", id="my_awesome_leader_arm")
keyboard_config = KeyboardTeleopConfig(id="my_laptop_keyboard")

# Initialize the robot and teleoperator
robot = LeKiwiClient(robot_config)
leader_arm = SO100Leader(teleop_arm_config)
keyboard = KeyboardTeleop(keyboard_config)

# Connect to the robot and teleoperator
# To connect you already should have this script running on LeKiwi: `python -m lerobot.robots.lekiwi.lekiwi_host --robot.id=my_awesome_kiwi`
robot.connect()
leader_arm_connected = True
try:
    leader_arm.connect()
except Exception as e:
    leader_arm_connected = False
keyboard.connect()



# Init rerun viewer
init_rerun(session_name="lekiwi_teleop")

import pygame
pygame.init()
pygame.joystick.init()

stick = pygame.joystick.Joystick(0)
stick.init()
default_arm_pose = {'arm_shoulder_pan.pos': -0.4146249528835284,
           'arm_shoulder_lift.pos': -99.2430613961312,
           'arm_elbow_flex.pos': 98.92280071813286,
           'arm_wrist_flex.pos': 51.09207708779445,
           'arm_wrist_roll.pos': 0.7570207570207543,
           'arm_gripper.pos': 0.5582137161084529}

print("Name:", stick.get_name())
print("Achsen:", stick.get_numaxes())
print("Buttons:", stick.get_numbuttons())
print("Hats:", stick.get_numhats())


speed = 0 # genereller Faktor für Translation und Rotation, Erhöhung durch R2 (8, button 7), Senkung durch L2 (7, button 6) möglich
t0 = time.perf_counter()
theta_vel = 0
THETA_FACTOR = 60
xy_scaler = 0.3

# Initialize ROS node for subscribing to observations
rclpy.init(args=None)
ros_node = Node("trajectory_publisher")
ros_publisher = ros_node.create_publisher(Float32MultiArray, "trajectory", 10)

def interrupt(): # interrupt für Stoppen
    t_interrupt = time.perf_counter()
    action = {**default_arm_pose,
              'x.vel': 0,
              'y.vel': 0,
              'theta.vel': 0}
    robot.send_action(action)
    t_inter_start = time.perf_counter()
    _, state = robot._get_data()
    while (state['x.vel'] != 0 or state['y.vel'] != 0 or state['x.vel'] != 0): # Transl. und Rot. müssen 0 werden
        time.sleep(0.02)
        _, state = robot._get_data()
    print("Stopping the robot took ", time.perf_counter() - t_inter_start, " s")
    raise Exception("RTobot was stopped by pushing button 9 or 10.")

while 1:
    arm_action = {}
    # falls Leader-Arm nicht verbunden: nur Steuerung der Basis, dann arm_pose = default
    if leader_arm_connected:
        arm_action = leader_arm.get_action()
        arm_action = {f"arm_{k}": v for k, v in arm_action.items()}
    else:
        arm_action = default_arm_pose
    pygame.event.pump()  # Required to update joystick state

    x = - stick.get_axis(1)
    y = - stick.get_axis(0)

    if 0.1 > x > -0.1:
        x = 0

    if 0.1 > y > -0.1:
        y = 0

    theta_left = stick.get_button(5)
    theta_right = stick.get_button(4)

    stop = stick.get_button(8) or stick.get_button(9) # Stoppen, falls 10 oder 9 (button 8 oder button 9) gedrückt
    if stop:
        interrupt()
    
    theta_vel = THETA_FACTOR * (speed * int(theta_right) - speed * int(theta_left))
    
    if (time.perf_counter() - t0 > 0.01):
        t0 = time.perf_counter()
        speed_inc = stick.get_button(7)
        speed_dec = stick.get_button(6)

        speed += 0.01 * int(speed_inc) - 0.01 * int(speed_dec)
        speed = max(0,min(1,speed))
    
    x_vel = x * xy_scaler * speed
    y_vel = y * xy_scaler * speed

    #print("w/s:", x, "a/d:", y)
    #print("speed = ", speed)
    #print("theta_speed = ", theta_vel)

    observation = robot.get_observation()

    action = {**arm_action,
              'x.vel': x_vel,
              'y.vel': y_vel,
              'theta.vel': theta_vel}
    _ = robot.send_action(action)

    log_rerun_data(observation=observation, action=action)

    msg = Float32MultiArray()
    msg.data = [float(v) for v in list(observation.values())[:9]]
    print("msg.data = ", msg.data)
    #print("msg.data:", msg.data)
    ros_publisher.publish(msg)
    rclpy.spin_once(ros_node, timeout_sec=0)

    # _, state = robot._get_data()
    # print("x.vel = ", state['x.vel'], "y.vel = ", state['y.vel'], "theta.vel = ", state['theta.vel'])

    time.sleep(0.05)
