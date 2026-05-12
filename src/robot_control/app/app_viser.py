'''
Dieses Skript ist der Entrypoint für die Viser-GUI. 
Es importiert die Application-Klasse aus viser_gui.py, erstellt eine Instanz davon und startet die GUI. 
Wenn der Benutzer die GUI mit einem KeyboardInterrupt (z.B. Strg+C) schließt, wird die shutdown-Methode der Application aufgerufen, um die GUI ordnungsgemäß zu beenden.
Es handelt sich lediglich um die Inferenz der Application-Klasse, Details zur Implementierung können in viser_gui.py gefunden werden.

Es werden folgende Steuerungsmodi ermöglicht:
- Modus 1: Teleoperation mit dem Leader-Arm, Bewegung der Basis mit der Tastatur (wasd)
- Modus 2: Teleoperation mit dem Leader-Arm (optional), Bewegung der Basis mit dem Controller (R2 und L2 -> Geschwindigkeit, R1 und L1 -> Drehung, linker Joystick -> Translation)
- Modus 3: Verfolgung einer Trajektorie mit Koordinateneingabe über die GUI oder bei Angabe einer csv, der Roboter fährt dann die Koordinaten ab
- Modus 4: Schreiben eines Buchstabens, der über die GUI eingegeben wird (Großbuchstaben A-Z)

-> gleichzeitig wird der Roboter live mit einer Verzögerung in der Viser-GUI (Loopback-Adresse 127.0.0.1:8080) angezeigt
-> Bei Bedarf kann der Modus in der GUI geändert werden, für die Zeit der Änderung wird die aktuelle Steuerung gestoppt und die neue gestartet, zudem dauert die Initialisierung kurz

Zur Steuerung mithilfe der Viser-Slider siehe app_viser_sliders.py
'''

from robot_control.gui.viser_gui import Application

def main():
    app = Application()
    try:
        app.start()
    except KeyboardInterrupt:
        app.shutdown()


if __name__ == "__main__":
    main()