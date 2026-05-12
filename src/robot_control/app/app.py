'''
LEGACY: Dieses Skript ist veraltet und wird nicht mehr aktiv gepflegt. Es dient nur noch als Referenz für die Entwicklung der neuen GUI-Struktur.
Dieses Skript ist der Entrypoint für die GUI.
Es handelt sich um eine TKinter-basierte GUI, die es ermöglicht, verschiedene Steuerungsmodi für den Roboter auszuwählen und zu starten.
Die GUI bietet folgende Modi zur Auswahl:
- Modus 1: Teleoperation mit dem Leader-Arm, Bewegung der Basis mit der Tastatur (wasd)
- Modus 2: Teleoperation mit dem Leader-Arm (optional), Bewegung der Basis mit dem Controller (R2 und L2 -> Geschwindigkeit, R1 und L1 -> Drehung, linker Joystick -> Translation)
- Modus 3: Verfolgung einer Trajektorie mit Koordinateneingabe über die GUI oder bei Angabe einer csv, der Roboter fährt dann die Koordinaten ab
- Modus 4: Schreiben eines Buchstabens, der über die GUI eingegeben wird

-> Die GUI hat keine relativen Pfade innerhalb des Projekts, sondern absolute Pfade, da sie von verschiedenen Verzeichnissen aus aufgerufen werden kann, je nachdem, welcher Modus ausgewählt wird.
-> Daher sollte hauptsächlich mit der Viser-GUI gearbeitet werden, da diese eine flexiblere Struktur hat und die Pfade relativ sind, was das Projekt portabler macht.
'''

import subprocess
from robot_control.gui import gui_app
import sys

gui_app.run_gui()

mode = gui_app.mode

if mode == 3:
    letter = gui_app.letter

if mode is None:
    raise Exception("Kein Modus gewählt")

else:
    print("Ausgewählter Modus:", mode)

    # Prozess starten
    if mode == 1:
        subprocess.run(
            ["python", "examples/lekiwi/teleoperate.py"],
            cwd="/home/student/lerlekiwi"
    )
    elif mode == 2:
        subprocess.run(
            ["python", "examples/lekiwi/control_gamepad.py"],
            cwd="/home/student/lerlekiwi"
    )

    elif mode == 3:
        subprocess.run(
            [sys.executable, "-m", "robot_control.control.trajectory_mode", "-l", letter],
            cwd="/home/student/lerlekiwi/src/lerobot/my_programs"
        )

    elif mode == 4:
        subprocess.run(
            [sys.executable, "-m", "robot_control.control.trajectory_mode", "-c"],
            cwd="/home/student/lerlekiwi/src/lerobot/my_programs"
        )