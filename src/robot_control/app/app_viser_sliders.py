'''
Dieses Skript ermöglicht die Steuerung mithilfe der Viser-Slider.
'''

import subprocess
from robot_control.gui import slider_control
import threading
import viser
import time


server = viser.ViserServer()
server.initial_camera.position = (0.5, 0.5, 0.5)

# --- GUI parallel starten ---
threading.Thread(target=slider_control.visualization, args=(server,), daemon=True).start()

time.sleep(5)

# Prozess starten
subprocess.run(
        ["python", "robot_control/src/robot_control/teleop_scripts/teleoperate_sliders.py"]
)