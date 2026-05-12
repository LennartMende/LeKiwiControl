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

import time

from lerobot.robots.lekiwi import LeKiwiClient, LeKiwiClientConfig, LeKiwiClientConfig2
from lerobot.teleoperators.keyboard.teleop_keyboard import KeyboardTeleop, KeyboardTeleopConfig
from lerobot.teleoperators.so100_leader import SO100Leader, SO100LeaderConfig
from lerobot.utils.robot_utils import busy_wait
#from lerobot.utils.visualization_utils import init_rerun, log_rerun_data

try:
    from lerobot.utils.visualization_utils import init_rerun, log_rerun_data
except ImportError:
    init_rerun = lambda *args, **kwargs: None
    log_rerun_data = lambda *args, **kwargs: None

import glob

tty_ports = glob.glob('/dev/ttyACM*')
number_of_blocked_ports = len(tty_ports)
leader_port = "/dev/ttyACM0"
if number_of_blocked_ports > 1:
    leader_port = "/dev/ttyACM1"
print(f"number_of_blocked_ports = {number_of_blocked_ports}")
print(f"glob.glob('/dev/ttyACM*') = {glob.glob('/dev/ttyACM*')}")
print(f"Leader Port = {leader_port}")

FPS = 30

keyboard_config = KeyboardTeleopConfig(id="my_laptop_keyboard")
keyboard = KeyboardTeleop(keyboard_config)

# Create the robot 1 with teleoperator configurations
robot_config = LeKiwiClientConfig(remote_ip="192.168.0.242", id="my_lekiwi")
teleop_arm_config = SO100LeaderConfig(port="/dev/ttyACM0", id="my_awesome_leader_arm")


# Initialize the robot and teleoperator
robot1 = LeKiwiClient(robot_config)
leader_arm1 = SO100Leader(teleop_arm_config)


# Create the robot 2 with teleoperator configurations
robot_config = LeKiwiClientConfig2(remote_ip="192.168.0.136", id="my_lekiwi2")
teleop_arm_config = SO100LeaderConfig(port=leader_port, id="my_awesome_leader_arm2")


# Initialize the robot and teleoperator
robot2 = LeKiwiClient(robot_config)
leader_arm2 = SO100Leader(teleop_arm_config)

# Connect to the robot and teleoperator
# To connect you already should have this script running on LeKiwi: `python -m lerobot.robots.lekiwi.lekiwi_host --robot.id=my_awesome_kiwi`
robot1.connect()
leader_arm1.connect()

robot2.connect()
leader_arm2.connect()

keyboard.connect()

# Init rerun viewer
#init_rerun(session_name="lekiwi_teleop_arm1")

if not robot1.is_connected or not leader_arm1.is_connected or not keyboard.is_connected:
    raise ValueError("Robot 1, teleop or keyboard is not connected!")

if not robot2.is_connected or not leader_arm2.is_connected:
    raise ValueError("Robot 2 or teleop is not connected!")

print("Starting teleop loop...")
while True:
    t0 = time.perf_counter()

    # Get robot observation
    observation = robot1.get_observation()

    # Retrieve first arm's action
    arm_action = leader_arm1.get_action()
    arm_action = {f"arm_{k}": v for k, v in arm_action.items()}
    # Keyboard
    keyboard_keys = keyboard.get_action()
    base_action = robot1._from_keyboard_to_base_action(keyboard_keys)

    action = {**arm_action, **base_action} if len(base_action) > 0 else arm_action


    ### SECOND ROBOT ###
    # Get robot observation
    observation = robot1.get_observation()

    # Retrieve second arm's action
    arm_action = leader_arm2.get_action()
    arm_action = {f"arm_{k}": v for k, v in arm_action.items()}
    # Keyboard
    keyboard_keys = keyboard.get_action()
    base_action = robot2._from_keyboard_to_base_action(keyboard_keys)

    action2 = {**arm_action, **base_action} if len(base_action) > 0 else arm_action

    # Send action to robot
    _1 = robot1.send_action(action)
    _2 = robot2.send_action(action2)

    # Visualize
    #log_rerun_data(observation=observation, action=action)

    busy_wait(max(1.0 / FPS - (time.perf_counter() - t0), 0.0))