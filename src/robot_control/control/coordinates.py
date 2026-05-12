from robot_control.data.letters import Letter
from math import sqrt, atan2, cos, sin
from dataclasses import dataclass
import csv
from typing import List, Dict
import logging

'''
sketch:
                ^x
               /
              /
             /
            /
           /
          /
         /
        /
       /            *(x, y) -> (r, phi)
      /              
     /            
    / <  
   /    \\phi
  /        \\
 /          |  
/------------------------------>y 

ABER ACHTUNG: DIES GILT NUR, WENN DAVOR DIE Y-KOORDINATEN VORHER NEGIERT WURDEN!!!

class Coordinates represents the coordinates of a point in the 2D space, with x and y values between 0.0 and 1.0.
It also provides methods to calculate the differences between coordinates and to convert those differences into actions and durations.
This can be used by the trajectory class, so you just have to give a letter and it will calculate the actions and durations for you 
to move the robot accordingly.

possible pipeline:
1. convert letter points to coordinates
2. calculate differences between coordinates
3. calculate actions and durations based on the differences
'''

logger = logging.getLogger('Coordinate logger')
logger.setLevel(logging.INFO)

@dataclass
class CoordinateConfig:
    """Konfiguration für die Berechnung von Aktionen und Dauer auf Basis der Koordinaten sowie Spezifizierung der Koordinatengrenzen"""
    X_MIN: float
    X_MAX: float
    Y_MIN: float
    Y_MAX: float
    MAX_SPEED: float
    DURATION_SCALER: float

    @property
    def max_abs_x_diff(self):
        return abs(self.X_MAX - self.X_MIN)
    
    @property
    def max_abs_y_diff(self):
        return abs(self.Y_MAX - self.Y_MIN)

DEFAULT_CFG = CoordinateConfig(X_MIN=0,X_MAX=1,Y_MIN=0,Y_MAX=1,MAX_SPEED=0.07,DURATION_SCALER=0.1)

class Coordinates:
    """
    Repräsentiert einen Punkt im 2D-Raum.
    Die Methoden sind zur Berechnung von Aktionen und Dauern und Koordinatentransformation
    """
    x: float
    y: float

    cfg: CoordinateConfig

    MAX_SPEED: float = 0.03 # velocity along phi direction with x_vel <= MAX_SPEED and y_vel <= MAX_SPEED
    DURATION_SCALER: float = 0.1 # scale duration to make sure the robot's move range

    r: float
    phi: float # in radians, angle between the positive y-axis and the line connecting the origin to the point (x, y), measured counterclockwise
    def __init__(self, x: float, y: float, cfg: CoordinateConfig = None):
        self.x = x
        self.y = y
        self.cfg = cfg if cfg is not None else DEFAULT_CFG

    @classmethod
    def from_tuple(cls, coords: tuple):
        return cls(coords[0], coords[1])

    @property
    def r(self) -> float:
        return sqrt(self.x**2 + self.y**2)

    @property
    def phi(self) -> float:
        return atan2(self.x, self.y)
    
    def __repr__(self):
        return f"Coordinates(x={self.x}, y={self.y})"
    
    def __str__(self):
        return f"Coordinates: P({self.x}|{self.y})"

    def __sub__(self, other):  
        x_diff = self.x - other.x
        y_diff = self.y - other.y
        if (abs(x_diff) > self.cfg.max_abs_x_diff) or (abs(y_diff) > self.cfg.max_abs_y_diff):
            raise ValueError("Coordinate differences must be within config limits")
        return Coordinates(x_diff, y_diff, self.cfg)

    @staticmethod
    def log_action_and_duration(ad: tuple[dict]) -> None: #ad := action_and_duration = (action, duration)
        """Loggt Infos zu einer Periode"""
        logger.info("Actions: {'x.vel': " + str(ad[0]['x.vel']) + ", 'y.vel': " + str(ad[0]['y.vel']) + ", 'theta.vel': 0.0" + "}")
        logger.info("Duration: " + str(ad[1]) + " seconds")

    
    # methods to convert coordinates into actions and durations for the robot to move accordingly
    @staticmethod
    def invert_y_coordinates(coordinates: tuple["Coordinates", ...]) -> tuple["Coordinates", ...]:
        """
        Invertiert die y-Koordinaten.
        Dies ist notwendig, da die Koordinaten des Roboters gegenüber der obigen Skizze invertiert sind.
        :param coordinates: Koordinaten, Tupel aus Koordinaten, die invertiert werden sollen
        :type coordinates: tupel[Coordinates, ...]
        :return: tuple[Coordinates, ...]
        """
        return tuple(
            Coordinates(c.x, -c.y)
            for c in coordinates
        )


    @staticmethod
    def letter_to_coordinates(letter: Letter, cfg: CoordinateConfig) -> list["Coordinates"]:
        """Methode, um einen Buchstaben in Koordinaten umzuwandeln"""
        return [Coordinates(x, y, cfg) for x, y in letter.points]
    
    @staticmethod
    def coordinates_to_differences(coords: list["Coordinates"]) -> list["Coordinates"]:
        """Berechnung der Differenz von Koortdinaten, Ausgabeliste ist um 1 Element kürzer als Eingabe"""
        return [coords[i+1] - coords[i] for i in range(len(coords)-1)]

    def diff_to_action_and_duration(self) -> tuple[dict, float]: # calculate actions and durations from coordinate differences
        """Berechnet Aktionen und Zeitdauern auf Basis der Differenz der Koordinaten sowie der Konfigurationsinstanz"""
        if self.r == 0:
            x_vel = 0.0
            y_vel = 0.0
            theta = 0.0
            duration = 0.0
            return ({
                'x.vel': x_vel,
                'y.vel': y_vel,
                'theta.vel': theta
            }, duration
            )
        x_vel = sin(self.phi) * self.cfg.MAX_SPEED # scale velocity to maximum of 0.05
        y_vel = cos(self.phi) * self.cfg.MAX_SPEED # scale velocity to maximum of 0.05

        # calculate duration based on the distance to be covered and the velocity, using the maximum velocity of 0.05 as reference
        duration = self.r / sqrt(x_vel**2 + y_vel**2) * self.cfg.DURATION_SCALER # t = s/v with maximum r is sqrt(2) for coordinates between 0.0 and 1.0

        return ({
            'x.vel': x_vel,
            'y.vel': y_vel,
            'theta.vel': 0.0
            }, duration)
    
    @staticmethod
    def read_csv_file(file_path: str) -> List[Dict[str, str]]:
        """
        Liest eine CSV-Datei ein und gibt die Daten als Liste von Dictionaries zurück.
        :param file_path: Pfad zur CSV-Datei
        :return: Liste von Dictionaries, jeweils ein Dict pro Zeile, Schlüssel = Spaltenname
        """
        data = []
        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            print(f"Datei nicht gefunden: {file_path}")
        except Exception as e:
            print(f"Fehler beim Lesen der CSV: {e}")
        return data

    @staticmethod
    def csv_to_coords(file_path: str, cfg: CoordinateConfig):
        csv_data = Coordinates.read_csv_file(file_path)
        print(f"csv_data:\n{csv_data}")
        coords = []
        for line in csv_data:
            coords.append(Coordinates(float(line['x']), float(line['y']), cfg))
        return coords

'''
# example usage
if __name__ == "__main__":
    print(f"Letter A: {str(LETTER_A)}")
    Coordinates.invert_y_coordinates(LETTER_A.points) # invert y-coordinates of letter A points to match the robot's coordinate system
    letter_a_coords = Coordinates.invert_y_coordinates(Coordinates.letter_to_coordinates(LETTER_A))
    differences = Coordinates.coordinates_to_differences(letter_a_coords)

    actions_and_durations = [
        diff.diff_to_action_and_duration()
        for diff in differences
    ]

    print("Actions and durations for letter A:")
    for action_and_duration in actions_and_durations:
        Coordinates.print_action_and_duration(action_and_duration)
'''