### CONTROL MANUALLY CONFIGURATION ###
# This file defines the configuration for the control_manually program. 
# The configuration includes the number of periods, the actions to be performed, and their durations.
# The actions are defined as a list of dictionaries, where each dictionary represents the state of the robot at a specific point in time.
# The configuration also includes a default set of arm actions that can be used in the control_manually program. 
# It also provides functions to save and load the configuration from a CSV file.

# durations and actions are imported from trajectory.py, which defines a sequence of actions and their corresponding durations.

# from lerobot.my_programs.robot_control.control. import ...

from robot_control.data.default_arm_poses import DefaultArmPose
from robot_control.data.letters import Letter
from robot_control.control.trajectory import Trajectory
from robot_control.control.coordinates import Coordinates, CoordinateConfig


class ControlConfig:
    """
    Konfiguration der Aktionen.

    Args:
        actions (list[dict]): Roboteraktionen pro Periode
        durations (list[float]): Dauer der jeweiligen Perioden
    """
    actions: list[dict]
    durations: list[float]

    def __init__(self, actions: list[dict], durations: list[float]):
        self.actions = actions
        self.durations = durations

    
    def trajectory_to_config(trajectory: Trajectory) -> "ControlConfig":
        """
        Konvertiert eine Trajektorie, die Aktionen und Dauern enthält, in eine ControlConfig, die für die Steuerung des Roboters verwendet werden kann.
        Die ControlConfig kann dann direkt in der Steuerung verwendet werden, um die Aktionen für jede Periode auszuführen und die entsprechenden Dauern einzuhalten.
        """
        actions = [step.action for step in trajectory.steps]
        durations = [step.duration for step in trajectory.steps]
        return ControlConfig(actions, durations)

    @classmethod
    def config_from_letter_and_pose(cls, letter: Letter, pose: DefaultArmPose, cfg: CoordinateConfig=None) -> "ControlConfig":
        """Gewinnt die Config aus einem Bushstaben, der Armpose zu jeder Periode und der CoordinateConfig,
        welche für die Berechnung der Aktionen und Dauern aus den Koordinaten notwendig ist.
        """
        trajectory = Trajectory.trajectory_from_letter_pose(letter=letter, default_arm_action=pose, cfg=cfg)
        return ControlConfig.trajectory_to_config(trajectory)
    
    @classmethod
    def config_from_coordinates_and_pose(cls, coordinates: list["Coordinates"], pose: DefaultArmPose) -> "ControlConfig":
        """Berechnet Config aus Koordinaten der anzufahrenden Punkte und Posen für jede Periode."""
        trajectory = Trajectory.trajectory_from_coordinates_pose(coords=coordinates, default_arm_action=pose)
        return ControlConfig.trajectory_to_config(trajectory)
    
    @classmethod
    def config_from_csv_and_pose(cls, file_path: str, pose: DefaultArmPose, cfg: CoordinateConfig = None) -> "ControlConfig":
        """Berechnet aus der csv (für Basis) mit einer optionalen CoordinateConfig und der Armpose für jede Periode die Trajektorie
        des gesamten Roboters"""
        trajectory = Trajectory.trajectory_from_csv_pose(file_path=file_path, default_arm_action=pose, cfg=cfg)
        return ControlConfig.trajectory_to_config(trajectory)