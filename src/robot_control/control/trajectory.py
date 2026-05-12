#from lerobot.my_programs.default_positions import CLOSED_PENCIL, HALF_OPEN_PENCIL, OPEN_PENCIL, CLOSED_REST, OPEN_REST, OPEN_STRETCHED_TO_SKY, CLOSED_STRETCHED_TO_SKY
from robot_control.control.coordinates import Coordinates, CoordinateConfig
from robot_control.data.letters import Letter#, LETTER_A, LETTER_B, LETTER_C, LETTER_D, LETTER_E, LETTER_F, LETTER_G
from dataclasses import dataclass
### DEFINE ACTIONS TO PERFORM IN SEQUENCE ###
# action is a list of dicts, dict: state at one point in time, list: multiple states in sequence
# define general arm pose


DEFAULT_CFG = CoordinateConfig(X_MIN=0,X_MAX=1,Y_MIN=0,Y_MAX=1,MAX_SPEED=0.07,DURATION_SCALER=0.1)


@dataclass
class TrajectoryStep:
    action: dict
    duration: float

class Trajectory:
    def __init__(self, steps: list[TrajectoryStep]):
        self.steps = steps

    def __len__(self):
        """Anzahl der Perioden"""
        return len(self.steps)
    
    def __str__(self):
        return "\n".join(f"Action: {step.action}, duration: {step.duration} s" for step in self.steps)

    # factories für letter -> trajectorie
    @classmethod
    def letter_to_base_trajectory(cls, letter: Letter, cfg: CoordinateConfig = None) -> "Trajectory":
        """transformiert Buchstaben in Trajektorie der Roboterbasis
        :param letter: letter als Liste von x-y-Tupeln aus dem Skript letters.py
        :param cfg: bestimmt Berechnung der Aktionen und Dauern anhand der Buchstaben"""
        coords = Coordinates.invert_y_coordinates(Coordinates.letter_to_coordinates(letter, cfg))
        diffs = Coordinates.coordinates_to_differences(coords)
        base_traj = [Coordinates.diff_to_action_and_duration(d) for d in diffs]
        traj_steps = [TrajectoryStep(action, duration) for action, duration in base_traj]
        return cls(traj_steps)
    
    @classmethod
    def trajectory_from_letter_pose(cls, letter: Letter, default_arm_action: dict[str, float], cfg: CoordinateConfig = None) -> "Trajectory":
        """Transformiert Buchstaben (für Basis) und Pose (für Arm) in eine Trajektorie für den gesamten Roboter
        :param letter: für Basis-Trajektorie
        :type letter: Letter
        :param default_arm_action: enthält die Posen jeder Periode
        :type default_arm_action: dict[str, float] mit float als Winkel"""
        base_trajectory = Trajectory.letter_to_base_trajectory(letter, cfg = cfg)
        arm_actions = [default_arm_action.copy() for _ in range(len(base_trajectory))]
        trajectory = base_trajectory.add_arm_pose(arm_actions)
        return trajectory


    # factories for coordinates -> trajectory
    @classmethod
    def coordinates_to_base_trajectory(cls, coords: list[Coordinates]) -> "Trajectory":
        """Transformiert Koordinaten im vorgegebenen Format in eine Trajektorie für die Basis
        :param coords: Koordinaten, die angefahren werden sollen
        :type coords: list[Coordinates]
        :return: Trajektorie der Basis mit Zeit und Aktionen
        :rtype: Trajectory
        """
        diffs = Coordinates.coordinates_to_differences(coords)
        base_traj = [Coordinates.diff_to_action_and_duration(d) for d in diffs]
        traj_steps = [TrajectoryStep(action, duration) for action, duration in base_traj]
        return cls(traj_steps)
    
    @classmethod
    def trajectory_from_coordinates_pose(cls, coords: list[Coordinates], default_arm_action: dict[str, float]) -> "Trajectory":
        """Transformiert Koordinaten und Posen in eine gesamte Trajektorie"""
        coords = Coordinates.invert_y_coordinates(coords)
        base_trajectory = Trajectory.coordinates_to_base_trajectory(coords)
        arm_actions = [default_arm_action.copy() for _ in range(len(base_trajectory))]
        trajectory = base_trajectory.add_arm_pose(arm_actions)
        return trajectory


    # add_arm für base_trajectory.add_arm_pose(arm_poses): erzeugt trajectory aus base_trajectory und arm_poses
    def add_arm_pose(self: "Trajectory", arm_poses: list[dict]) -> "Trajectory":
        """Kombiniert Basistrajektorie des Objekts- mit Armtrajektorie (Argument)
        :param arm_poses: Armposen jeder Periode
        :type arm_poses: list[dict]
        :return: Gesamttrajektorie
        :rtype: Trajectory
        """
        if len(self.steps) != len(arm_poses):
            raise ValueError("Number of steps and arm poses must match")
        full_traj = [
            TrajectoryStep({**arm_pose, **step.action}, step.duration)
            for step, arm_pose in zip(self.steps, arm_poses)
        ]
        return Trajectory(full_traj)

    @classmethod
    def csv_to_base_trajectory(cls, file_path: str, cfg: CoordinateConfig = None) -> "Trajectory":
        """Gewinnt die Basis-Trajektorie aus einer CSV mit dem spezifizierten Dateipfad.
        :param file_path: Pfad der csv relativ zum ausführenden Ordner
        :type file_path: str
        :param cfg: Konfiguration, die die Berechnung der Aktionen und Dauern aus den Koordinaten bestimmt
        :type cfg: CoordinateConfig"""
        coords = Coordinates.csv_to_coords(file_path, cfg)
        diffs = Coordinates.coordinates_to_differences(coords)
        base_traj = [Coordinates.diff_to_action_and_duration(d) for d in diffs]
        traj_steps = [TrajectoryStep(action, duration) for action, duration in base_traj]
        return cls(traj_steps)
    
    @classmethod
    def trajectory_from_csv_pose(cls, file_path: str, default_arm_action: dict[str, float], cfg: CoordinateConfig = None) -> "Trajectory":
        """Gewinnt die Trajektorie des gesamten Roboters aus einer CSV (für die Basis) und der Pose (für den Arm)
        :param file_path: Pfad der csv relativ zum ausführenden Ordner
        :type file_path: str
        """
        coords = Coordinates.csv_to_coords(file_path, cfg)
        coords = Coordinates.invert_y_coordinates(coords)
        base_trajectory = Trajectory.coordinates_to_base_trajectory(coords)
        arm_actions = [default_arm_action.copy() for _ in range(len(base_trajectory))]
        trajectory = base_trajectory.add_arm_pose(arm_actions)
        return trajectory