#!/usr/bin/env bash
set -e

echo "=== LeKiwi START ==="

# 1. Host-Fenster starten (NEUES TERMINAL)
echo "Starte LeKiwi Host (SSH)..."
gnome-terminal -- bash -lc "
    ssh -t 192.168.0.242 'bash -i -c lekiwi_host_start'
"

# 2. Rechte setzen
echo "Setze USB Rechte..."
sudo chmod 666 /dev/ttyACM*

# 3. Conda aktivieren
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lerlekiwi

# 4. In Parent-Folder des Projekts wechseln
cd ~/lerlekiwi/src/lerobot/my_programs

# 5. Kurz warten, damit Leader initialisiert werden kann
sleep 8

# 6. GUI starten
echo "Starte robot_control..."
python -m robot_control
