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

from dataclasses import dataclass

import csv

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray

import subprocess, sys

from importlib.resources import files


class ModeGui:
    """
    Diese Klasse kümmert sich um die Auswahl des Modus und die Eingabe der notwendigen Informationen (z.B. Buchstabe oder Koordinaten) über die GUI.
    """
    def __init__(self):
        self.mode = 0
        self.letter = None
        self.x_list = []
        self.y_list = []
        self.buttons = []
        self.md_list = []
        self.log_handle = None

    def setup(self, server: viser.ViserServer) -> None:
        """
        Bereitet die GUI vor, z.B. durch das Hinzufügen von Überschriften oder Anweisungen. setup() wird einmalig zu Beginn aufgerufen, um die GUI zu initialisieren.
        :param server: ViserServer-Instanz, die für die GUI verwendet wird
        :type server: viser.ViserServer
        """
        self.log_handle = server.gui.add_markdown("### Status: Ready")

    def run(self, server) -> None:
        """
        Startet die GUI und wählt den Modus aus. run() wirkt blockierend, da die Modus-Auswahl blockiert, bis der Nutzer eine Auswahl getroffen hat. 
        Danach wird die GUI entsprechend der Auswahl angepasst (z.B. Eingabefelder für Buchstaben oder Koordinaten sichtbar gemacht).
        :param server: ViserServer-Instanz, die für die GUI verwendet wird
        :type server: viser.ViserServer
        """
        self._select_mode(server)

    def _choose_mode(self, server: viser.ViserServer, option1:str, int1:int, option2:str, int2:int, main_buttons: bool = False) -> None:
        """Hilfsmethode, um zwischen zwei Optionen zu wählen. Die Optionen werden als Buttons dargestellt, die Auswahl wird in self.mode gespeichert. 
        Wenn main_buttons=True, werden die Buttons der Instanz hinzugefügt, damit sie später wieder sichtbar gemacht werden können.
        :param server: ViserServer-Instanz, die für die GUI verwendet wird
        :type server: viser.ViserServer
        :param option1: Text für die erste Option, z.B. "Live steuern"
        :type option1: str
        :param int1: Integer, der in self.mode gespeichert wird, wenn die erste Option gewählt wird, z.B. 8
        :type int1: int
        :param option2: Text für die zweite Option, z.B. "Trajektorie verfolgen"
        :type option2: str
        :param int2: Integer, der in self.mode gespeichert wird, wenn die zweite Option gewählt wird, z.B. 9
        :type int2: int
        :param main_buttons: Ob die Buttons der Instanz hinzugefügt werden sollen, damit sie später wieder sichtbar gemacht werden können, z.B. True
        :type main_buttons: bool
        """
        self.mode = 0

        opt1_btn = server.gui.add_button(option1)
        opt2_btn = server.gui.add_button(option2)

        if main_buttons:
            self.buttons.extend([opt1_btn, opt2_btn])

        @opt1_btn.on_click
        def _(_):
            self.mode = int1
            self.log_handle.content = f"{option1.split(' ')[0]}-Modus gewählt"
            print(option1.split(' ')[0] + "-Modus gewählt")

        @opt2_btn.on_click
        def _(_):
            self.mode = int2
            self.log_handle.content = f"{option2.split(' ')[0]}-Modus gewählt"
            print(option2.split(' ')[0] + "-Modus gewählt")

        while self.mode == 0:
            time.sleep(0.05)

        # Buttons unsichtbar machen, wichtige Buttons (main_buttons=True) werden dem Objekt hinzugefügt und können später wieder sichtbar gemacht werden.
        opt1_btn.visible = False
        opt2_btn.visible = False
    


    def get_input_with_commit(self, server: viser.ViserServer, label, validate_fn, error_msg, initial_value=""):
        """
        Hilfsmethode, um eine Eingabe mit einem Bestätigungsbutton zu erstellen. Die Eingabe wird erst übernommen, 
            wenn der Nutzer auf "Bestätigen" klickt und die Eingabe validiert ist.
        :param server: ViserServer-Instanz, die für die GUI verwendet wird
        :type server: viser.ViserServer
        :param label: Label für das Eingabefeld, z.B. "Buchstabe"
        :type label: str
        :param validate_fn: Funktion, die die Eingabe validiert. Sie sollte einen booleschen Wert zurückgeben, 
            der angibt, ob die Eingabe gültig ist, und den verarbeiteten Wert, z.B. lambda v: (len(v) == 1 and 'a' <= v.lower() <= 'z', v.lower())
        :type validate_fn: function
        :param error_msg: Fehlermeldung, die angezeigt wird, wenn die Eingabe ungültig ist, z.B. "Bitte genau einen Buchstaben (a-z) eingeben!"
        :type error_msg: str
        :param initial_value: Initialer Wert für das Eingabefeld, z.B. ""
        :type initial_value: str
        """
        result = [None]  # mutable container

        input_field = server.gui.add_text(label, initial_value=str(initial_value))
        warning_label = server.gui.add_markdown("")
        commit_button = server.gui.add_button("Bestätigen")

        @commit_button.on_click
        def _(_):
            value = input_field.value.strip()

            valid, processed_value = validate_fn(value)
            self.letter = processed_value

            if valid:
                result[0] = processed_value
                warning_label.content = "Eingabe bestätigt"
                print(f"Bestätigt: {processed_value}")
            else:
                warning_label.content = f"## ⛔ {error_msg}"

        # Warten bis bestätigt
        while result[0] is None:
            time.sleep(0.05)

        # Aufräumen
        input_field.visible = False
        warning_label.visible = False
        commit_button.visible = False

        return result[0]
    
    def values_to_csv(self):
        """
        Speichert die aktuellen Trajektorienwerte in einer CSV-Datei. Die Datei wird im Format "x,y" gespeichert, wobei jede Zeile einen Punkt der Trajektorie repräsentiert.
        """
        with open(files("robot_control").joinpath("data/trajectory.csv"), "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["x", "y"])
            for x, y in zip(self.x_list, self.y_list):
                writer.writerow([x, y])
        

    def _select_mode(self, server: viser.ViserServer) -> None:
        """
        Wählt den konkreten Modus für die Steuerung des Roboters aus und setzt die resultierenden Instanzfelder (z.B. self.mode, self.letter, self.x_list, self.y_list) 
            entsprechend. Die Modus-Auswahl erfolgt über Buttons in der GUI, die Auswahl wird in self.mode gespeichert.
        :param server: ViserServer-Instanz, die für die GUI verwendet wird
        :type server: viser.ViserServer
        """
        mode_btn = server.gui.add_button("Nochmal den Modus auswählen")
        @mode_btn.on_click
        def _(_):
            self.mode = -1
            self.log_handle.content = f"### Neuwahl-Modus gewählt."
            mode_btn.visible = False
            return
        
        self._choose_mode(server, "Live steuern", 8, "Trajektorie verfolgen", 9, main_buttons=True)
        if self.mode == 8:
            self._choose_mode(server, "Teleoperation", 1, "Controllersteuerung", 2)
            self.log_handle.content = f"### Modus gewählt: {self.mode}"
            return
        elif self.mode == 9:
            self._choose_mode(server, "Buchstaben zeichnen", 3, "Koordinaten vorgeben", 4)

        if self.mode == 3:
            def validate_letter(value):
                value = value.lower()
                if len(value) == 1 and 'a' <= value <= 'z':
                    return True, value
                return False, None
            
            self.letter = self.get_input_with_commit(
                server,
                "Buchstabe",
                validate_letter,
                "Bitte genau einen Buchstaben (a-z) eingeben!"
            )
            return

        elif self.mode == 4:
            self._choose_mode(server, "GUI-Eingabe", 5, "csv-Pfad eingeben", 6)
            if self.mode == 5:
                self.x_list.clear()
                self.y_list.clear()
                self.md_list.clear()
                def validate_number(value):
                    try:
                        num = int(value)
                        if 1 <= num <= 10:
                            return True, num
                    except:
                        pass
                    return False, None

                number = self.get_input_with_commit(
                    server,
                    "Anzahl der Punkte (zwischen 1 und 10)",
                    validate_number,
                    "Anzahl der Punkte muss zwischen 1 und 10 liegen!"
                )

                for i in range(number):
                    md = server.gui.add_markdown(f"### Punkt {i+1}")
                    x = self.get_input_with_commit(
                        server,
                        f"Punkt {i+1} - x-Koordinate",
                        lambda v: (True, v) if v.replace('.','',1).isdigit() else (False, None),
                        "Bitte gültige Zahl eingeben!"
                    )
                    self.x_list.append(x)
                    y = self.get_input_with_commit(
                        server,
                        f"Punkt {i+1} - y-Koordinate",
                        lambda v: (True, v) if v.replace('.','',1).isdigit() else (False, None),
                        "Bitte gültige Zahl eingeben!"
                    )
                    self.y_list.append(y)
                    self.log_handle.content = f"Punkt {i+1}: ({x}, {y})"
                    self.md_list.append(md)
                
                for md in self.md_list:
                    md.visible = False
                self.mode = 4
                self.log_handle.content = f"Koordinaten eingegeben: {list(zip(self.x_list, self.y_list))}"
                self.values_to_csv()
                return

            if self.mode == 6:
                def validate_path(value):
                    if os.path.isfile(value):
                        return True, os.path.abspath(value)
                    return False, None

                filepath = self.get_input_with_commit(
                    server,
                    "CSV-Pfad",
                    validate_path,
                    "Datei existiert nicht!"
                )
                self.mode = 4
                return


class TrajectorySubscriber(Node): # auch von ros-Ordner importierbar
    """
    Abonniert das Topic "trajectory", welches die Trajektorie des realen Roboters darstellt und speichert die empfangenen Daten in self.latest_data. 
    Die Daten werden als Liste von Float-Werten erwartet, die die Trajektorie repräsentieren.
    """
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
        self.latest_data = msg.data
        #print("Empfangene Trajektorie:", self.latest_data)

class MsgProcessor:
    """
    Zustandslose Helper-Klasse: Verarbeitet empfangene ROS-Nachrichten und gewinnt daraus die Pose der Basis bzw. des Arms in Radiant.
    """
    @staticmethod
    def msg_to_arm(msg): #Umrechnung der Werte von ROS-Nachricht (Grad) in URDF-konforme Werte (Radiant)
        list_value_in_2pi = []
        for value in msg:
            value_in_2pi = pi / 180 * value - pi  # 0 ... 360 -> -pi ... pi
            list_value_in_2pi.append(value_in_2pi)
        #Reihenfolge korrigieren
        arm_joints = list_value_in_2pi[:6] # setzt Geschwindigkeiten zu 0
        return arm_joints
    
    @staticmethod
    def msg_to_base(msg):
        x_vel = - msg[6]
        y_vel = msg[7]
        theta_vel = float(np.deg2rad(msg[8]))
        #print(f"Empfangene Basisgeschwindigkeit: x={x_vel}, y={y_vel}, theta={theta_vel}") # Base-Geschwindigkeiten im Welt-Koordinatensystem
        return x_vel, y_vel, theta_vel



@dataclass
class LekiwiCfg:
    """
    Physische Parameter des LeKiwi, die für die Kinematikberechnung relevant sind. (Die Werte wurden aus der URDF-Datei entnommen.)
    """
    r = 0.052  # Radien der Räder
    R = 0.103   # Abstand der Räder zum Mittelpunkt
    alpha7 = 60
    alpha8 = 180
    alpha9 = 300


class LeKiwiKinematics:
    """
    Klasse für die Kinematik des LeKiwi, insbesondere für die Umrechnung von Basisgeschwindigkeiten in Radgeschwindigkeiten (IK) 
        und die Berechnung der neuen Pose der Basis. Außerdem Berechnung der URDF-Arm-Pose aus den Joints.
    source: https://www.youtube.com/watch?v=lJ6PH--el54&t=813s -> 13:33 - 27:27
    """
    def __init__(self, cfg: LekiwiCfg = LekiwiCfg()):
        """
        Initialisiert die Kinematik mit den gegebenen physischen Parametern des LeKiwi. Außerdem werden die Anfangspositionen der Räder auf 0 gesetzt.
        """
        self.pos7 = 0.0
        self.pos8 = 0.0
        self.pos9 = 0.0
        self.cfg = cfg
    
    def arm_joints_to_urdf(arm_joints: list[float]) -> list[float]: # rechnet Nachrichten des Listeners in URDF-konforme Werte um und aktualisiert die URDF-Konfiguration
        """
        Konvertiert Gelenkwinkel aus ROS/Listener-Konvention in URDF-Konvention.

        Coordinate system / conventions:
        - Input: Gelenkwinkel in Radiant (ROS-Konvention)
        - Output: Gelenkwinkel in Radiant (URDF-konform)
        - Enthält Vorzeichen- und Offset-Korrekturen pro Joint

        Joint transformations:
        - joint 0: +π offset
        - joint 1: Spiegelung + π/2
        - joint 2: Spiegelung - π/2
        - joint 3: Spiegelung - π/2
        - joint 4: Skalierung + Spiegelung + π/2
        - joint 5: Spiegelung + π

        Args:
            arm_joints: Liste von 6 Gelenkwinkeln in Radiant (ROS frame)

        Returns:
            list[float]: URDF-korrigierte Gelenkwinkel in Radiant
        """
        arm_joints[0] = arm_joints[0] + pi
        arm_joints[1] = - arm_joints[1] + pi/2
        arm_joints[2] = - arm_joints[2] - pi/2
        arm_joints[3] =  - arm_joints[3] - pi/2
        arm_joints[4] = 2 * (- arm_joints[4]) + pi/2
        arm_joints[5] = - arm_joints[5] + pi 
        return arm_joints
    
    def _single_vel_from_base(self, base_vel, alpha) -> float:
        """
        Konvertiert die Basisgeschwindigkeit in die Geschwindigkeit eines einzelnen Rads.
        Die Gesamtbewegung ergibt sich durch Superposition der Bewegungen der einzelnen Räder, 
            die jeweils durch die Basisgeschwindigkeit und den Winkel des Rads (alpha) bestimmt werden:
        theta = (sin(alpha) * x_vel + cos(alpha) * y_vel + R * theta_vel) / r
        Zudem muss die Winkelgeschwindigkeit in die translatorische Bewegung umgerechnet werden.
        :param base_vel: Tuple der Basisgeschwindigkeiten (x_vel, y_vel, theta_vel)
            -> resultiert aus MsgProcessor.msg_to_base(msg), mit msg als ROS-Nachricht
        :type base_vel: tuple[float, float, float]
        :param alpha: Winkel des Rads in Radiant
        :type alpha: float
        """
        wheel_multiplier =  1 / self.cfg.r
        theta = sin(alpha) * base_vel[0] 
        theta += cos(alpha) * base_vel[1]
        theta += self.cfg.R * base_vel[2] # in degree
        theta *= wheel_multiplier
        return theta
    
    def base_vel_to_wheel_vel(self, base_vel) -> tuple[float, float, float]:
        """
        Konvertiert die Basisgeschwindigkeit in einzelne Radgeschwindigkeiten um (IK), um die Räder in der URDF zu rotieren.
        Die Berechnung erfolgt für jedes Rad basierend auf der Basisgeschwindigkeit und dem Winkel des Rads (alpha).

        :param base_vel: Tuple der Basisgeschwindigkeiten (x_vel, y_vel, theta_vel)
        :type base_vel: tuple[float, float, float]
        :return: Tuple der Radgeschwindigkeiten (theta7, theta8, theta9)
        :rtype: tuple[float, float, float]
        """
        alpha7_rad = np.deg2rad(self.cfg.alpha7)
        alpha8_rad = np.deg2rad(self.cfg.alpha8)
        alpha9_rad = np.deg2rad(self.cfg.alpha9)

        theta7 = self._single_vel_from_base(base_vel, alpha8_rad) # change 8->7, 9->8, 7->9 because urdf <-> message order
        theta8 = self._single_vel_from_base(base_vel, alpha9_rad)
        theta9 = self._single_vel_from_base(base_vel, alpha7_rad)
        return theta7, theta8, theta9

    def wheel_vel_to_urdf(self, wheel_vel, dt = 0.015) -> tuple[float, float, float]: # wheels are spinned
        """
        Konvertiert die Radgeschwindigkeiten in die URDF-Positionen (für jeden Zeitpunkt),
            somit dreht sich das Rad entsprechend der Geschwindigkeit, um die Bewegung der Basis zu simulieren.
        Die Positionen der Räder werden durch Integration der Geschwindigkeiten über die Zeit berechnet
            (pos += theta * dt), wobei dt die Zeit zwischen den Updates ist (z.B. 0.015s).
        :param wheel_vel: Tuple der Radgeschwindigkeiten (theta7, theta8, theta9)
        :type wheel_vel: tuple[float, float, float]
        :param dt: Zeitintervall für die Integration der Radgeschwindigkeiten, Standardwert ist 0.015s 
            -> muss im Normalfall angepasst werden, bspw. mit der Loop-Zeit der R3egelung und GUI
        :type dt: float
        :return: Tuple der neuen Radpositionen (pos7, pos8, pos9), die in der URDF verwendet werden, um die Räder zu drehen
        :rtype:
        """
        theta7, theta8, theta9 = wheel_vel
        self.pos7 -= theta7 * dt # in urdf the direction is opposite
        self.pos8 -= theta8 * dt
        self.pos9 -= theta9 * dt
        base_pos = [self.pos7, self.pos8, self.pos9]
        return base_pos
    
    @staticmethod
    def quat_mult(q, p):
        """Multipliziert zwei Quaternionen q und p. Diese Methode wird verwendet, um die Orientierung der Basis zu aktualisieren, 
            wenn sie sich bewegt (Rotation um die z-Achse). Die Quaternionen werden in der Form (w, x, y, z) dargestellt."""
        w1, x1, y1, z1 = q
        w2, x2, y2, z2 = p
        w = w1*w2 - x1*x2 - y1*y2 - z1*z2
        x = w1*x2 + x1*w2 + y1*z2 - z1*y2
        y = w1*y2 - x1*z2 + y1*w2 + z1*x2
        z = w1*z2 + x1*y2 - y1*x2 + z1*w2
        return np.array([w, x, y, z])

    
    def base_pos_wxyz(self, position, wxyz, base_msg: int, dt: float = 0.015): # robot moves
        """
        Zurzeit noch Legacy-Code, um die Pose der Basis zu berechnen, wenn sie sich bewegt. 
        Berechnet die neue Position und Orientierung der Basis basierend auf der empfangenen Basisgeschwindigkeit (base_msg) und der Zeit (dt).
        Die Position wird durch Integration der Basisgeschwindigkeit über die Zeit berechnet (position += velocity * dt), 
        und die Orientierung wird durch Multiplikation der aktuellen Orientierung mit einer neuen Quaternion aktualisiert
        """
        x_diff = base_msg[0] * dt
        y_diff = - base_msg[1] * dt
        position = (position[0] + x_diff, position[1] + y_diff, position[2])
        theta_diff = base_msg[2] * dt
        q_z = np.array([cos(theta_diff/2), 0, 0, sin(theta_diff/2)])
        wxyz = self.quat_mult(wxyz, q_z)
        return [position, wxyz]



class RobotVisualization:
    """
    Visualisiert die reale Szene, Hilfsmittel und GUI-Elemente in der Viser-Umgebung. Dazu zählen:
        - Laden und Anzeigen des URDF-Modells des Roboters
        - Erstellen eines Koordinatensystems für die Basis des Roboters
        - Erstellen von GUI-Elementen (z.B. Checkboxen) zur Steuerung der Sichtbarkeit von Elementen (z.B. Koordinatensystem, Meshes, Grid)
    """

    def __init__(self, urdf_path: str = files("robot_control").joinpath("description/LeKiwi.urdf")):
        print(f"URDF-Pfad: {urdf_path}")
        self.urdf_path = urdf_path
        self.base_path = urdf_path.parent
        robot_frame = None
        self.viser_urdf = None
    
    def _create_robot_frame(self, server: viser.ViserServer, base_pos: tuple[float, float, float] = (0.0, 0.0, 0.0), 
                            coord_origin: tuple[list[np.array[float, float, float]]] = np.array([0.0, 0.0, 0.0]),
                            theta: float = pi/2):
        """
        Erstellt das Koordinatensystem für die Basis des Roboters. Die Orientierung des Koordinatensystems wird durch eine Rotation um die z-Achse um theta bestimmt,
            da die Basis des LeKiwi in der URDF um 90 Grad um die z-Achse gedreht ist. Das Koordinatensystem wird als Frame in der Viser-Szene hinzugefügt, 
            mit der Position coord_origin und der berechneten Orientierung. Die Sichtbarkeit des Koordinatensystems kann später über eine Checkbox in der GUI gesteuert werden.
        Das Frame gilt als Parent für die Elemente des Roboters, der Rohboter hängt also an diesem Frame, damit sich alles entsprechend der Bewegung der Basis mitbewegt.
        Da der Roboter selbst nicht bewegt werden kann, muss man die Basis bewegen, um die Bewegung des Roboters zu simulieren.
            
        :param server: ViserServer-Instanz, die für die GUI verwendet wird
        :type server: viser.ViserServer
        :param base_pos: Anfangsposition der Basis, Standardwert ist (0.0, 0.0, 0.0)
        :type base_pos: tuple[float, float, float]
        :param coord_origin: Ursprung des Koordinatensystems, Standardwert ist (0.0, 0.0, 0.0)
        :type coord_origin: tuple[list[np.array[float, float, float]]]
        :param theta: Rotation um die z-Achse in Radiant, um die Orientierung des Koordinatensystems anzupassen, Standardwert ist pi/2 (90 Grad)
        :type theta: float
        """
        q_z = np.array([cos(theta/2), 0, 0, sin(theta/2)])
        base_orient = (1.0, 0.0, 0.0, 0.0) # Quaternion

        coord_orient = LeKiwiKinematics.quat_mult(base_orient, q_z)
        server.frame = server.scene.add_frame(
            "/robot_base",
            wxyz=coord_orient,
            position=coord_origin,
            axes_length=0.2,
            axes_radius=0.007,
            origin_radius=0.03
        )
        
    def _load_urdf(self, server: viser.ViserServer, load_meshes: bool = True, load_collision_meshes: bool = False) -> None:
        """
        Lädt das URDF-Modell des Roboters und fügt es der Viser-Szene hinzu. Das URDF wird mit den angegebenen Optionen geladen, 
            um die Visual-Meshes und/oder Kollisions-Meshes zu laden.
        Das URDF-Modell wird als ViserUrdf-Objekt erstellt, das an das zuvor erstellte Koordinatensystem (Frame) der Basis angehängt wird, 
            damit sich der Roboter entsprechend der Bewegung der Basis mitbewegt. 
        Die Sichtbarkeit der Meshes kann später über Checkboxen in der GUI gesteuert werden. Wenn load_meshes=False und load_collision_meshes=False,
        werden keine Meshes geladen.

        :param server: ViserServer-Instanz, die für die GUI verwendet wird
        :type server: viser.ViserServer
        :param load_meshes: Ob die Visual-Meshes des URDF geladen werden sollen, Standardwert ist True
        :type load_meshes: bool
        :param load_collision_meshes: Ob die Kollisions-Meshes des URDF geladen werden sollen, Standardwert ist False
        :type load_collision_meshes: bool
        """
        urdf = URDF.load(self.urdf_path, load_meshes=load_meshes, 
                        build_scene_graph=load_meshes, load_collision_meshes=load_collision_meshes,
                    build_collision_scene_graph=load_collision_meshes, mesh_dir=self.base_path)
        self.viser_urdf = ViserUrdf(
            server,
            urdf_or_path=urdf,
            root_node_name="/robot_base", 
            load_meshes=load_meshes,
            load_collision_meshes=load_collision_meshes,
            collision_mesh_color_override=(1.0, 0.0, 0.0, 0.5),
        )
    
    def _create_checkboxes(self, server: viser.ViserServer, load_meshes: bool = True, load_collision_meshes: bool = False):
        """
        Erstellt die Sichtbarkeits-Checkboxen für die GUI. 
        Da die GUI eventbasiert arbeitet, wird mithilfe der on_update-Callbacks die Sichtbarkeit der entsprechenden Elemente 
            (Koordinatensystem, Visual-Meshes, Kollisions-Meshes, Grid) in der Viser-Szene gesteuert, wenn die Checkboxen aktualisiert werden.
        
        :param server: ViserServer-Instanz, die für die GUI verwendet wird
        :type server: viser.ViserServer
        :param load_meshes: Ob die Visual-Meshes des URDF geladen werden sollen, Standardwert ist True. Wenn False, wird die Checkbox für die Visual-Meshes nicht angezeigt.
        :type load_meshes: bool
        :param load_collision_meshes: Ob die Kollisions-Meshes des URDF geladen werden sollen, Standardwert ist False. Wenn False, wird die Checkbox für die Kollisions-Meshes nicht angezeigt.
        :type load_collision_meshes: bool
        """
        # Add visibility checkboxes.
        with server.gui.add_folder("Visibility"):
            show_coord_system_cb = server.gui.add_checkbox(
                "Show coordinate system",
                True,  # initial sichtbar
            )
            show_meshes_cb = server.gui.add_checkbox(
                "Show meshes",
                self.viser_urdf.show_visual,  # initial True
            )
            show_collision_meshes_cb = server.gui.add_checkbox(
                "Show collision meshes",
                self.viser_urdf.show_collision,  # initial True
            )
            show_grid_cb = server.gui.add_checkbox(
                "Show grid",
                True,  # initial sichtbar
            )

        # Callback für Koordinatensystem
        @show_coord_system_cb.on_update
        def _(_):
            server.frame.visible = show_coord_system_cb.value

        # Callback für Visual-Meshes
        @show_meshes_cb.on_update
        def _(_):
            self.viser_urdf.show_visual = show_meshes_cb.value

        # Callback für Kollisions-Meshes
        @show_collision_meshes_cb.on_update
        def _(_):
            self.viser_urdf.show_collision = show_collision_meshes_cb.value
        
        @show_grid_cb.on_update
        def _(_):
            self.grid.visible = show_grid_cb.value

        # Hide checkboxes if meshes are not loaded.
        show_meshes_cb.visible = load_meshes
        show_collision_meshes_cb.visible = load_collision_meshes

        # Set initial robot configuration.
        initial_config = [0.0] * 9
        self.viser_urdf.update_cfg(np.array(initial_config))

    def setup(self, server):
        self._create_robot_frame(server)
        self._load_urdf(server)
        # Create grid
        trimesh_scene = self.viser_urdf._urdf.scene or self.viser_urdf._urdf.collision_scene
        self.grid = server.scene.add_grid(
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
        self._create_checkboxes(server)
    
    def base_move(self, server: viser.ViserServer, base_msg: int, dt: float = 0.015):
        x_diff = base_msg[0] * dt
        y_diff = - base_msg[1] * dt
        server.frame.position = (server.frame.position[0] + x_diff, server.frame.position[1] + y_diff, server.frame.position[2])
        theta_diff = base_msg[2] * dt
        q_z = np.array([cos(theta_diff/2), 0, 0, sin(theta_diff/2)])
        server.frame.wxyz = LeKiwiKinematics.quat_mult(server.frame.wxyz, q_z)
        


class Application:
    """
    Hauptanwendungsklasse für die Robotiksteuerung.
    Diese Klasse integriert die verschiedenen Komponenten der Anwendung, einschließlich der GUI, der Kinematik und der Visualisierung.
     - Initialisiert die Viser-Server-Instanz und setzt die Anfangskamera-position.
     - Erstellt Instanzen der ModeGui, LeKiwiKinematics und RobotVisualization-Klassen.
     - Initialisiert ROS2 und erstellt einen Subscriber für die Trajektorie des Roboters.
     - Startet die Hauptschleife, die die Modusänderungen überwacht, die ROS-Nachrichten verarbeitet und die Visualisierung aktualisiert.
     - Beinhaltet Methoden zum Starten der Steuerung basierend auf dem ausgewählten Modus, zum Behandeln von Modusänderungen und zum Herunterfahren der Anwendung.
    """
    def __init__(self):
        self.server = viser.ViserServer()
        self.server.initial_camera.position = (0.5, 0.5, 0.5)

        self.modeGui = ModeGui()
        self.leKiwiKinematics = LeKiwiKinematics()
        self.robotVisualization = RobotVisualization()
        self.robotVisualization.setup(self.server)

        rclpy.init()
        self.traj_subscriber = TrajectorySubscriber()

        self.current_process = None
        self.current_mode = None

    def start(self):
        """
        Startet die Anwendung. Zunächst wird die blockierende Modus-Auswahl gestartet, bei der der Nutzer den gewünschten Modus für die Steuerung des Roboters auswählt. 
        Sobald ein Modus ausgewählt wurde, wird die Hauptschleife gestartet, 
        die kontinuierlich die Modusänderungen überwacht, die ROS-Nachrichten verarbeitet und die Visualisierung aktualisiert.
        """
        # 1. BLOCKIERENDE MODE-AUSWAHL
        self.modeGui.setup(self.server)
        self.modeGui.run(self.server)
        self.current_mode = self.modeGui.mode

        self.modeGui.log_handle.content = f"Initialer Modus: {self.current_mode}"

        # 2. MAIN LOOP STARTEN
        self.start_control()
        self.run()
        

    def run(self):
        """
        Dauerschleife, die die Modusänderungen überwacht, die ROS-Nachrichten verarbeitet und die Visualisierung aktualisiert.
         - Überwacht die Modusänderungen durch Aufruf von handle_mode_change(), um sicherzustellen, dass die Steuerung entsprechend dem ausgewählten Modus gestartet wird.
         - Verarbeitet die ROS-Nachrichten, indem sie die neuesten Trajektorie-Daten abruft, 
                die Basis- und Armpositionen berechnet und die URDF-Konfiguration sowie die Basisbewegung in der Visualisierung aktualisiert.
        """
        self.t0 = time.perf_counter()

        try:
            while True:
                self.t_begin = time.perf_counter()
                self.handle_mode_change()
                if self.current_mode is None:
                    self.modeGui.run(self.server)
                    self.current_mode = self.modeGui.mode
                    self.start_control()
                rclpy.spin_once(self.traj_subscriber, timeout_sec=0)
                if self.traj_subscriber.latest_data is not None:
                    data = self.traj_subscriber.latest_data
                    arm_pos = LeKiwiKinematics.arm_joints_to_urdf(
                        MsgProcessor.msg_to_arm(data)
                    )
                    duration = time.perf_counter() - self.t0
                    base_pos = self.leKiwiKinematics.wheel_vel_to_urdf(
                        self.leKiwiKinematics.base_vel_to_wheel_vel(
                            MsgProcessor.msg_to_base(data)
                        ),
                        dt=duration
                    )
                    self.t0 = time.perf_counter()
                    full_robot_pos = base_pos + arm_pos
                    self.robotVisualization.viser_urdf.update_cfg(
                        np.array(full_robot_pos)
                    )
                    self.robotVisualization.base_move(
                        self.server,
                        MsgProcessor.msg_to_base(data),
                        dt=duration
                    )
                time.sleep(max(1/30 - (time.perf_counter() - self.t_begin), 0))

        except KeyboardInterrupt:
            self.shutdown()
            print("Thread beendet")

    def shutdown(self):
        """
        Beendet die Anwendung und stoppt alle laufenden Prozesse.
        """
        if self.current_process is not None:
            self.current_process.terminate()
            self.current_process = None

        rclpy.shutdown()

    def start_control(self):
        """
        Startet die Steuerung basierend auf dem ausgewählten Modus.
        """
        if self.current_mode == 1:
            self.modeGui.log_handle.content = "Starte Teleoperation..."
            self.current_process = subprocess.Popen(
                ["python", files("robot_control").joinpath("teleop_scripts/teleoperate_ros.py")]
            )

        elif self.current_mode == 2:
            self.modeGui.log_handle.content = "Starte Controllersteuerung..."
            self.current_process = subprocess.Popen(
                ["python", files("robot_control").joinpath("teleop_scripts/control_gamepad.py")]
            )

        elif self.current_mode == 3:
            self.modeGui.log_handle.content = "Zeichne Buchstaben..."
            self.current_process = subprocess.Popen(
                [sys.executable, "-m", "robot_control.control.trajectory_mode", "-l", self.modeGui.letter],
                cwd="/home/student/lerlekiwi/src/lerobot/my_programs"
            )

        elif self.current_mode == 4:
            self.modeGui.log_handle.content = "Verfolge Koordinaten..."
            self.current_process = subprocess.Popen(
                [sys.executable, "-m", "robot_control.control.trajectory_mode", "-c"],
                cwd="/home/student/lerlekiwi/src/lerobot/my_programs"
            )

    def handle_mode_change(self):
        """
        Überwacht Änderungen im Modus und passt die GUI entsprechend an.
        """
        if self.modeGui.mode == -1:
            self.reset_gui_state()
    
    def reset_gui_state(self):
        """
        Setzt den GUI-Zustand zurück, um eine neue Modus-Auswahl zu ermöglichen. 
        Alle laufenden Prozesse werden gestoppt, die Buttons werden entfernt und die Modus-Variable wird zurückgesetzt.
        """
        if self.current_process is not None:
            self.current_process.terminate()
            self.current_process = None

        for b in self.modeGui.buttons:
            b.visible = False
        self.modeGui.buttons.clear()

        self.modeGui.mode = 0
        self.current_mode = None

        self.request_mode_selection = True

# inference:
# #import threading
# from robot_control.gui.viser_gui2 import Application

# def main():
#     app = Application()
#     try:
#         app.start()
#     except KeyboardInterrupt:
#         app.shutdown()


# if __name__ == "__main__":
#     main()

