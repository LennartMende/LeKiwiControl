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

'''
Dieses Skript ermöglicht es, den Roboter eine vorgegebene Trajektorie abfahren zu lassen.
Es gibt zwei Modi zur Auswahl:
- Modus C: Koordinaten (coordinates) - der Roboter fährt eine Trajektorie ab, die in einer csv-Datei vorgegeben ist (Pfad zur csv-Datei muss im Skript angegeben werden)
- Modus L: Buchstabe (letter) - der Roboter fährt eine Trajektorie ab, die einem Buchstaben entspricht, der über die Kommandozeile eingegeben wird (Großbuchstaben A-Z)
Die Trajektorien für die Buchstaben sind vordefiniert und können in der Datei letters.py eingesehen werden. Die csv-Datei für die Koordinaten muss im vorgegebenen Format 
vorliegen, damit sie korrekt eingelesen werden kann (siehe ControlConfig.config_from_csv_and_pose
- die Teleoperationsskripte werden zur Inferenz verwendet, wobei nicht wirklich teleoperiert wird, sondern die Aktionen mithilfe der Trajektorienklasse in sinnvolle
Aktionen umgewandelt, eingeteilt und dann an den Roboter gesendet werden.
'''

### IMPORTS ###
import time
import logging
import argparse
import os
from importlib.resources import files

from lerobot.robots.lekiwi import LeKiwiClient, LeKiwiClientConfig
from lerobot.teleoperators.keyboard.teleop_keyboard import KeyboardTeleop, KeyboardTeleopConfig
from lerobot.teleoperators.so100_leader import SO100Leader, SO100LeaderConfig
from lerobot.utils.robot_utils import busy_wait
#from lerobot.utils.visualization_utils import init_rerun, log_rerun_data
# lerobot.my_programs.robot_control.control import ...
from robot_control.control.control_cfg import ControlConfig
from robot_control.data.letters import DefaultLetters, letter_dict
from robot_control.data.default_arm_poses import DefaultArmPose
# from control.coordinates import Coordinates

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray

try:
    from lerobot.utils.visualization_utils import init_rerun, log_rerun_data
except ImportError:
    init_rerun = lambda *args, **kwargs: None
    log_rerun_data = lambda *args, **kwargs: None



parser = argparse.ArgumentParser(description="Wähle einen Modus")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-c", action="store_true", help="Modus C (Koordinaten) aktivieren")
group.add_argument("-l", metavar="LETTER", type=str, help="Modus L (Buchstaben) aktivieren")

args = parser.parse_args()




### CONFIGURATION ###
FPS = 30

# Create the robot and teleoperator configurations
robot_config = LeKiwiClientConfig(remote_ip="192.168.0.242", id="my_lekiwi")
teleop_arm_config = SO100LeaderConfig(port="/dev/ttyACM0", id="my_awesome_leader_arm")
keyboard_config = KeyboardTeleopConfig(id="my_laptop_keyboard")

# Initialize the robot and teleoperator
robot = LeKiwiClient(robot_config)
keyboard = KeyboardTeleop(keyboard_config)

# Connect to the robot and teleoperator
# To connect you already should have this script running on LeKiwi: `python -m lerobot.robots.lekiwi.lekiwi_host --robot.id=my_awesome_kiwi`
robot.connect()
keyboard.connect()

#init logger
logger = logging.getLogger("Logger")
logger.setLevel(logging.INFO)
logger.propagate = False
#for handler in logger.handlers:
#    logger.removeHandler(handler)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Init rerun viewer
init_rerun(session_name="lekiwi_teleop")

# Initialize ROS node for subscribing to observations
rclpy.init(args=None)
ros_node = Node("trajectory_publisher")
ros_publisher = ros_node.create_publisher(Float32MultiArray, "trajectory", 10)


### ACTIONS FOR INITIALIZING PAINTING ###
def paint_start():
    _ = robot.send_action({**DefaultArmPose.OPEN_PENCIL.value, 'x.vel': 0.0, 'y.vel': 0.0, 'theta.vel': 0.0})
    time.sleep(2.0)
    _ = robot.send_action({**DefaultArmPose.HALF_OPEN_PENCIL.value, 'x.vel': 0.0, 'y.vel': 0.0, 'theta.vel': 0.0})
    logger.info("Stift einlegen und festhalten und mit 'b' und ENTER bestätigen, um fortzufahren!\n")
    while(input() != 'b'):
        time.sleep(0.1)
    _ = robot.send_action({**DefaultArmPose.CLOSED_PENCIL.value, 'x.vel': 0.0, 'y.vel': 0.0, 'theta.vel': 0.0})
    logger.info("'b' und ENTER drücken, um fortzufahren!\n")
    while (input() != 'b'):
        time.sleep(0.1)
    _ = robot.send_action({**DefaultArmPose.CLOSED_PENCIL_PAINT_LIFTED.value, 'x.vel': 0.0, 'y.vel': 0.0, 'theta.vel': 0.0})
    time.sleep(0.5)
    _ = robot.send_action({**DefaultArmPose.CLOSED_PENCIL_PAINT.value, 'x.vel': 0.0, 'y.vel': 0.0, 'theta.vel': 0.0})
    logger.info("Der Arm verändert seine Pose leicht, um den Stift aufzudrücken... Kurz warten")
    time.sleep(1.5)


letter = ''

# Modusentscheidung und entsprechende Konfiguration laden
if args.c:
    logger.info("Modus C - Koordinaten (coordinates) gewählt")
    file_path = files("robot_control").joinpath("data/trajectory.csv")
    print(file_path)
    control_config = ControlConfig.config_from_csv_and_pose(file_path, DefaultArmPose.CLOSED_PENCIL.value)
elif args.l:
    logger.info("Modus L - Buchstaben (letter) gewählt - Buchstabe ", args.l)
    letter = args.l
    paint_start()  # perform the paint start actions to initialize the painting process
    letter = letter_dict[letter]
    control_config = ControlConfig.config_from_letter_and_pose(letter, DefaultArmPose.CLOSED_PENCIL_PAINT.value)

counter = 0
for action, duration in zip(control_config.actions, control_config.durations):
    action_start = time.perf_counter()
    while time.perf_counter() - action_start < duration:  # perform each action for its specified duration
        t0 = time.perf_counter()
        #if (counter % 100):
        #    logger.info(f"Performing action: {action}")
        
        observation = robot.get_observation()

        # logger.info("observation:\n", observation)

        # Send action to robot
        _ = robot.send_action(action)

        #optional: log data to rerun viewer
        log_rerun_data(observation=observation, action=action)

        # Publish the trajectory to ROS topic
        msg = Float32MultiArray()

        if isinstance(observation, dict):
            obs_array = [float(v) for v in list(observation.values())[:9]]
        else:
            obs_array = list(observation[:9])

        msg.data = obs_array
        ros_publisher.publish(msg)

        # ROS intern updaten (sehr wichtig!)
        rclpy.spin_once(ros_node, timeout_sec=0)


        #counter = counter + 1
        #logger.info("duration = ", max(1.0 / FPS - (time.perf_counter() - t0), 0.0))
        busy_wait(max(1.0 / FPS - (time.perf_counter() - t0), 0.0))


time.sleep(2.0)  # wait for a moment before ending the program to ensure the last action is finished

if args.l:
    logger.info("Aktionen abgeschlossen. Arm fährt in Ruhepose zurück.")

    logger.info("Erst wird der Arm angehoben.")
    rest_pose = DefaultArmPose.CLOSED_PENCIL_PAINT_LIFTED.value  # set arm to rest pose after performing the actions
    action = {**rest_pose,
            'x.vel': 0.0, # set speed to 0 after performing the actions
            'y.vel': 0.0,
            'theta.vel': 0.0}
    _ = robot.send_action(action)
    action = [float(v) for v in list(action.values())[:9]]
    msg.data = action
    ros_publisher.publish(msg)
    rclpy.spin_once(ros_node, timeout_sec=0)
    time.sleep(2.0)


    rest_pose = DefaultArmPose.CLOSED_REST.value  # set arm to rest pose after performing the actions
    action = {**rest_pose,
            'x.vel': 0.0, # set speed to 0 after performing the actions
            'y.vel': 0.0,
            'theta.vel': 0.0}
    _ = robot.send_action(action)
    action = [float(v) for v in list(action.values())[:9]]
    msg.data = action
    ros_publisher.publish(msg)
    rclpy.spin_once(ros_node, timeout_sec=0)


    logger.info("Der Arm wird jetzt abgerüstet. Dazu\n\
                1. Bitte den Stift festhalten\n \
                2. 'b' und ENTER drücken, um fortzufahren\n \
                3. Stift herausnehmen\n \
                4. 'b' und ENTER drücken, um fortzufahren")

    while(input() != 'b'):
        time.sleep(0.1)

logger.info("Aktionen abgeschlossen. Arm fährt in Ruhepose zurück.")
rest_pose = DefaultArmPose.OPEN_REST.value  # set arm to rest pose after performing the actions
action = {**rest_pose,
        'x.vel': 0.0, # set speed to 0 after performing the actions
        'y.vel': 0.0,
        'theta.vel': 0.0}
_ = robot.send_action(action)
action = [float(v) for v in list(action.values())[:9]]
msg.data = action
ros_publisher.publish(msg)
rclpy.spin_once(ros_node, timeout_sec=0)

logger.info("ROS-Node wird heruntergefahren...\n")

ros_node.destroy_node()
rclpy.shutdown()

logger.info("Jetzt kann ein neuer Modus gewählt werden.\n")