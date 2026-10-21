## 1. Ziel des Projekts ##
Die LeKiwi-Roboter können auf verschiedene Arten gesteuert werden.
Im Rahmen dieses Projekts wurden mehrere Steuerungsmodi sowie eine einheitliche Visualisierung mit Viser implementiert.

Implementierte Steuerungsmodi:
   - Teleoperation mit Leader-Follower-Setup
      - Armsteuerung über einen Leader-Arm
      - Basissteuerung über WASD
   - Gamepad-Steuerung
      - Basissteuerung über Controller
      - optional zusätzliche Armsteuerung über Leader-Arm
   - Viser-Slider-Steuerung
      - Armsteuerung über Web-Slider (Viser UI)
      - Basissteuerung über WASD
   - Trajektorienbasierte Steuerung
      - explizite Koordinateneingabe über Viser-GUI
      - Einlesen von CSV-Dateien mit Koordinaten
      - Zeichnen von Großbuchstaben (A–Z)

Ein zentrales Ziel ist die Verbesserung der Bedienbarkeit:
Statt einzelne Skripte über das Terminal zu starten, kann der Steuerungsmodus zur Laufzeit direkt in Viser gewechselt werden. Dadurch entfällt ein Neustart der Anwendung für unterschiedliche Modi.

Zusätzlich wurden ROS2-Nodes implementiert, die in den Teleoperationsskripten verwendet werden und auch unabhängig weiterverwendet werden können.


## 2. Struktur des Moduls ##
├── docs  
├── environment.yml  
├── pyproject.toml  
├── README.md  
├── scripts  
└── src  

'docs' enthält die Sphinx-Dokumentation der API (Klassen, Methoden und Attribute der Module control und data).

'scripts' enthält das Startskript für das Gesamtsystem. Dieses initialisiert Leader- und Follower-Setup und startet die zentrale Anwendung mit Modusauswahl.

'src/' enthält den gesamten Python-Quellcode:
   - 'app/': Einstiegspunkt und Implementierungen der Steuerungsmodi
   - 'gui/':  Viser-basierte Visualisierung und UI-Komponenten (inkl. Modusauswahl)
   - 'control/': Trajektoriengenerierung aus Koordinaten, CSV-Dateien oder Buchstaben
   - 'ros/': ROS2 Publisher und Subscriber für Roboterkommunikation
   - 'teleop_scripts/' Low-level Teleoperationsskripte für die einzelnen Modi
   - 'data/': Datenbasis für Bewegungen:
      - Koordinaten
      - Buchstabenrepräsentationen
      - Standard-Armposen

'environment.yml' definiert die Conda-Umgebung, mit der das Projekt entwickelt und getestet wurde.

'pyproject.toml' definiert das Projekt als installierbares Python-Paket und ermöglicht den Modulbetrieb.


## 3. Python-Module

### `app`
Enthält die Ausführungslogik der verschiedenen Steuerungsmodi.  
Die Datei `__main__.py` dient als Entry Point und stellt eine Tkinter-basierte Modusauswahl bereit.

---

### `gui`
Enthält die gesamte Viser-Visualisierung:
- Darstellung des Roboters
- Benutzeroberfläche zur Laufzeit (Moduswechsel in Viser)

---

### `control`
Implementiert die Trajektoriengenerierung aus verschiedenen Eingaben:
- Koordinaten
- CSV-Dateien
- Buchstaben (A–Z)

Diese Module berechnen daraus die entsprechenden Steuerbefehle für den Roboter.

---

### `ros`
Enthält ROS2-Komponenten zur Kommunikation:
- Publisher für Steuerdaten
- Subscriber für Sensor- und Zustandsdaten

---

### `teleop_scripts`
Enthält die konkreten Teleoperationsskripte für die einzelnen Steuerungsmodi.  
Diese werden von der `app`-Schicht abhängig vom gewählten Modus aufgerufen.

---

### `data`
Enthält statische Daten und Definitionsgrundlagen:
- Koordinatenrepräsentationen
- Buchstaben als Bewegungsmuster
- Standard-Armpositionen
- Beispieltrajektorien

---


## 4. Installation
Repository klonen:  
'git clone https://github.com/LennartMende/LeKiwiControl.git'  
'cd LeKiwiControl'  

Als Nächstes die environment aus dem yaml generieren:
conda env create -f environment.yml
Falls Fehler angezeigt werden, stammen diese von nichtkompatiblen Modulen, die aber für dieses Repo nicht wichtig sind.
Außerdem ist eine bestehende ROS2-Umgebung, die gesourcet ist, wichtig, da auf die ROS-Client-Library für Python rclpy) zurückgegriffen wird.

Environment aktivieren:  
'conda activate lerlekiwi'  

Paket im Projektordner installieren:  
'pip install -e .'  

---

## 5. Skript interpretieren und starten

Um das Menü zur Auswahl der Steuerungsmethode zu starten, gib 'python -m robot\_control' ein, während du dich im Parent-Verzeichnis von 'robot_control' befindest.

---
## 6. Hinweise

Dieses Projekt setzt eine bestehende **LeRobot-Installation** voraus.

### Entwicklungsumgebung
- Conda-Environment: `lerlekiwi`

### Roboter (Raspberry Pi)
- Conda-Environment: `lerobot`
- IP-Adresse: `192.168.0.242`

---

### Anpassungen im Startskript (`scripts/lekiwi_start.sh`)

Folgende Stellen müssen ggf. angepasst werden:

#### Zeile 9 – SSH-Zieladresse
```bash
ssh -t <IP> 'bash -i -c lekiwi_host_start'
```

---

#### Zeile 18 – Conda Environment
```bash
conda activate lerlekiwi
```

---

#### Zeile 21 – Projektpfad
Der Pfad muss auf die lokale Installation des `robot_control`-Moduls angepasst werden.
