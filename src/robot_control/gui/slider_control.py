from __future__ import annotations

import time
from typing import Literal

import numpy as np
import tyro
from robot_descriptions.loaders.yourdfpy import load_robot_description
from yourdfpy import URDF
import os
from numpy import pi, cos, sin

import viser
from viser.extras import ViserUrdf

import threading

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray


from robot_control.data.default_arm_poses import CLOSED_REST


mode = 0
letter = None
x_list = []
y_list = []
current_slider_values = [0.0] * 9

joint_limits = [(-pi, pi),
                    (-pi, pi),
                    (-pi, pi),
                    (-3/4 * pi, 3/4 * pi), 
                    (-6/5 * pi, pi/4),
                    (-pi/4, 4/3 * pi),
                    (-pi/2, pi),
                    (-6/5 * pi, 6/5 * pi),
                    (-2, 0.1)
]

def create_robot_control_sliders(
    server: viser.ViserServer, viser_urdf: ViserUrdf
) -> tuple[list[viser.GuiInputHandle[float]], list[float]]:
    """
    Erstellt in Viser Schieberegler für die Gelenkwinkel des Roboters.
    :param server: ViserServer-Instanz, auf der die GUI-Elemente erstellt werden sollen
    :type server: viser.ViserServer
    :return: tuple[slider_handles, initial_config]
    """

    slider_handles: list[viser.GuiInputHandle[float]] = []
    initial_config: list[float] = []

    def update_sliders(_):
        global current_slider_values
        current_slider_values = [slider.value for slider in slider_handles]
        viser_urdf.update_cfg(np.array(current_slider_values))

    for i, (joint_name, _) in enumerate(viser_urdf.get_actuated_joint_limits().items()):
        lower, upper = joint_limits[i]
        initial_pos = 0.0
        slider = server.gui.add_slider(
            label=joint_name,
            min=lower,
            max=upper,
            step=1e-3,
            initial_value=initial_pos,
        )
        slider.on_update(  # When sliders move, we update the URDF configuration.
            update_sliders
        )
        slider_handles.append(slider)
        initial_config.append(initial_pos)
        if i < 3:
            slider.visible = False  # Verstecke die ersten drei Slider (Basisbewegung), da sie nicht über die GUI gesteuert werden sollen
    return slider_handles, initial_config



class TrajectorySubscriber(Node): # auch von ros-Ordner importierbar
    """ROS-Node, der die Trajektorien empfängt, die von der ROS-Action gesendet werden. Hier speichern wir die empfangenen Daten in self.latest_data."""
    def __init__(self):
        super().__init__('trajectory_subscriber')

        self.subscription = self.create_subscription(
            Float32MultiArray,
            'trajectory',
            self.callback,
            10
        )

        self.latest_data = None  # hier speichern wir die Daten

    def callback(self, msg):
        """Callback-Funktion, die aufgerufen wird, wenn eine Nachricht empfangen wird. Hier speichern wir die Daten."""
        self.latest_data = msg.data


class SliderPublisher(Node): # auch von ros-Ordner importierbar
    """ROS-Node, der die aktuellen Werte der Schieberegler an ROS sendet, damit sie von einem Publisher empfangen und in der Teleoperation verarbeitet werden können."""
    def __init__(self):
        super().__init__('slider_publisher')
        self.publisher = self.create_publisher(Float32MultiArray, 'slider', 10)

    def publish(self, data):
        msg = Float32MultiArray()
        msg.data = self.slider_to_real(data)
        self.publisher.publish(msg)
        # print("target_trajectory:", data)

    def slider_to_real(self, data):
        """Rechnet die Werte der Schieberegler in die Werte um, die von ROS erwartet werden (Grad statt Radiant, Korrektur der Reihenfolge und Vorzeichen 
        entsprechend der URDF-Konfiguration). Wenn die Schieberegler bei 0 stehen, soll der Follower-Arm die geschlossene Ruhestellung innehalten."""
        for i in range(len(data)):
            data[i] = np.rad2deg(data[i])
        
        data[0] = data[0] + CLOSED_REST['arm_shoulder_pan.pos']
        data[1] = - data[1] + CLOSED_REST['arm_shoulder_lift.pos']
        data[2] = - data[2] + CLOSED_REST['arm_elbow_flex.pos']
        data[3] =  - data[3] + CLOSED_REST['arm_wrist_flex.pos']
        data[4] = 0.5 * (- data[4]) + CLOSED_REST['arm_wrist_roll.pos']
        data[5] = - data[5] + CLOSED_REST['arm_gripper.pos']
        return data

def visualization(server: viser.ViserServer, urdf_path: str = "robot_control/src/robot_control/description/LeKiwi.urdf",
    load_meshes: bool = True,
    load_collision_meshes: bool = False,
    only_sliders = False
    ) -> None:
    """
    Visualisierung des Roboters in der Viser-Umgebung.
    Dafür muss ein Viser-Server initialisiert und der Roboter geladen werden. Anschließend werden alle GUI-Elemente erstellt,
        es werden Funktionen für die Umrechnung der ROS-Nachrichten in die URDF definiert und ein Loop gestartet, 
        der die ROS-Nachrichten empfängt und die URDF-Konfiguration entsprechend aktualisiert.
    :param server: ViserServer-Instanz, auf der die Visualisierung erstellt werden soll
    :type server: viser.ViserServer
    :param urdf_path: Pfad zur URDF-Datei des Roboters
    :type urdf_path: str
    :param load_meshes: Ob die visuellen Meshes des Roboters geladen werden sollen
    :type load_meshes: bool
    :param load_collision_meshes: Ob die Kollisions-Meshes des Roboters geladen werden sollen
    :type load_collision_meshes: bool
    """
    # --- ROBOTER + GUI ERST NACH MODUS ---
    #urdf_path = "description/LeKiwi.urdf"
    urdf = URDF.load(urdf_path, load_meshes=load_meshes, build_scene_graph=load_meshes,
                 load_collision_meshes=load_collision_meshes,
                 build_collision_scene_graph=load_collision_meshes)
    viser_urdf = ViserUrdf(
        server,
        urdf_or_path=urdf,
        load_meshes=load_meshes,
        load_collision_meshes=load_collision_meshes,
        collision_mesh_color_override=(1.0, 0.0, 0.0, 0.5),
    )

    # Aktuelle Position und Orientierung
    robot_base_name = "base_plate_layer1-v5"
    base_pos = (0.0, 0.0, 0.0)       # aus URDF
    coord_origin = tuple((np.array(base_pos) + np.array([0.0, 0.0, 0.055])).tolist())  # Etwas über dem Boden
    theta = pi/2
    q_z = np.array([cos(theta/2), 0, 0, sin(theta/2)])
    base_orient = (1.0, 0.0, 0.0, 0.0) # Quaternion

    def quat_mult(q, p):
        """Multipliziert zwei Quaternionen q und p."""
        w1, x1, y1, z1 = q
        w2, x2, y2, z2 = p
        w = w1*w2 - x1*x2 - y1*y2 - z1*z2
        x = w1*x2 + x1*w2 + y1*z2 - z1*y2
        y = w1*y2 - x1*z2 + y1*w2 + z1*x2
        z = w1*z2 + x1*y2 - y1*x2 + z1*w2
        return np.array([w, x, y, z])
    
    def msg_to_arm(msg): #Umrechnung der Werte von ROS-Nachricht (Grad) in URDF-konforme Werte (Radiant)
        """
        Wandelt ROS-Nachricht in URDF-konforme Werte um. 
        Die Nachricht enthält die Gelenkwinkel in Grad, die in Radiant umgerechnet und entsprechend der URDF-Konfiguration korrigiert werden müssen. 
        Außerdem werden die ersten drei Werte (Basisbewegung) auf 0 gesetzt, da sie nicht über die GUI gesteuert werden sollen.
        :param msg: Liste der Gelenkwinkel in Grad, wie sie von ROS empfangen werden
        :type msg: list[float]
        :return: Liste der Gelenkwinkel in Radiant, korrigiert für die URDF-Konfiguration
        :rtype: list[float]
        """
        list_value_in_2pi = []
        for value in msg:
            value_in_2pi = pi / 180 * value - pi  # 0 ... 360 -> -pi ... pi
            list_value_in_2pi.append(value_in_2pi)
        #Reihenfolge korrigieren
        list_value_in_2pi = [0.0] * 3 + list_value_in_2pi[:6] # setzt Geschwindigkeiten zu 0
        arm_joints = list_value_in_2pi[3:]
        return arm_joints

    def arm_joints_to_urdf(arm_joints: list[float]) -> None: # rechnet Nachrichten des Listeners in URDF-konforme Werte um und aktualisiert die URDF-Konfiguration
        """
        Wandelt Gelenkwinkel in Radiant um und korrigiert sie für die URDF-Konfiguration.
        :param arm_joints: Liste der Gelenkwinkel in Radiant, die aus msg_to_arm hervorgeht
        :type arm_joints: list[float]
        """
        arm_joints[0] = arm_joints[0] + pi
        arm_joints[1] = - arm_joints[1] + pi/2
        arm_joints[2] = - arm_joints[2] - pi/2
        arm_joints[3] =  - arm_joints[3] - pi/2
        arm_joints[4] = 2 * (- arm_joints[4]) + pi/2
        arm_joints[5] = - arm_joints[5] + pi 
        list_value_in_2pi = [0.0] * 3 + arm_joints
        viser_urdf.update_cfg(np.array(list_value_in_2pi))

    coord_orient = quat_mult(base_orient, q_z)

    frame = server.scene.add_frame(
        "/robot_base",
        wxyz=coord_orient,
        position=coord_origin,
        axes_length=0.2,
        axes_radius=0.007,
        origin_radius=0.03
    )

    # Create grid.
    trimesh_scene = viser_urdf._urdf.scene or viser_urdf._urdf.collision_scene

    grid = server.scene.add_grid(
        "/grid",
        width=2,
        height=2,
        position=(
            0.0,
            0.0,
            # Get the minimum z value of the trimesh scene.
            trimesh_scene.bounds[0, 2] if trimesh_scene is not None else 0.0,
        ),
    )

    # Create sliders in GUI that help us move the robot joints.

    with server.gui.add_folder("Joint position control"):
        (slider_handles, initial_config) = create_robot_control_sliders(
            server, viser_urdf
        )


        
    # Add visibility checkboxes.
    with server.gui.add_folder("Visibility"):
        show_coord_system_cb = server.gui.add_checkbox(
            "Show coordinate system",
            True,  # initial sichtbar
        )
        show_meshes_cb = server.gui.add_checkbox(
            "Show meshes",
            viser_urdf.show_visual,  # initial True
        )
        show_collision_meshes_cb = server.gui.add_checkbox(
            "Show collision meshes",
            viser_urdf.show_collision,  # initial True
        )
        show_grid_cb = server.gui.add_checkbox(
            "Show grid",
            True,  # initial sichtbar
        )

    # Callback für Koordinatensystem
    @show_coord_system_cb.on_update
    def _(_):
        frame.visible = show_coord_system_cb.value

    # Callback für Visual-Meshes
    @show_meshes_cb.on_update
    def _(_):
        viser_urdf.show_visual = show_meshes_cb.value

    # Callback für Kollisions-Meshes
    @show_collision_meshes_cb.on_update
    def _(_):
        viser_urdf.show_collision = show_collision_meshes_cb.value
    
    @show_grid_cb.on_update
    def _(_):
        grid.visible = show_grid_cb.value

    # Hide checkboxes if meshes are not loaded.
    show_meshes_cb.visible = load_meshes
    show_collision_meshes_cb.visible = load_collision_meshes

    # Set initial robot configuration.
    initial_config = [0.0] * 9
    viser_urdf.update_cfg(np.array(initial_config))

    rclpy.init()
    ros_node = TrajectorySubscriber()
    slider_publisher = SliderPublisher()

    while True:
        rclpy.spin_once(ros_node, timeout_sec=0)

        # --- 1. IMMER: Slider-Daten senden ---
        target_trajectory = current_slider_values[3:]
        slider_publisher.publish(target_trajectory)

        # --- 2. OPTIONAL: empfangene Daten verarbeiten ---
        if ros_node.latest_data is not None:
            data = ros_node.latest_data
            # print("data =", data)

            arm_joints = msg_to_arm(data)
            arm_joints_to_urdf(arm_joints)

        time.sleep(0.01)


# Inferenzbeispiel:
#threading.Thread(target=main, daemon=True).start()

#while viser_gui.mode == 0:
#    sleep(0.05)

#print("Modus gewählt:", viser_gui.mode)

#if __name__ == "__main__":
#    main()