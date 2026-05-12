import tkinter as tk
from tkinter import ttk
import subprocess
import sys
import webbrowser


class StartWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.tk.call('tk', 'scaling', 2.5)
        self.root.title("Steuerungsmethode auswählen")
        self.root.geometry("1200x600")
        self.button_style = ttk.Style()
        self.button_style.configure('Kim.TButton', font=('Helvetica', 24))


        self._build_ui()

    def _build_ui(self):
        label = ttk.Label(
            self.root,
            text="Wähle eine Steuerungsmethode:",
            font=("Helvetica", 30),
        )
        label.pack(pady=20)

        btn_viser = ttk.Button(
            self.root,
            text="Steuerung über Viser-Slider",
            command=self.start_viser_sliders,
            style='Kim.TButton',
        )
        #btn_viser.config(height=50, width=300)
        btn_viser.pack(pady=20)

        btn_other = ttk.Button(
            self.root,
            text="Andere Steuerung",
            command=self.start_viser_default,
            style='Kim.TButton',
        )
        #btn_other.config(height=50, width=300)
        btn_other.pack(pady=20)

    def start_viser_sliders(self):
        webbrowser.get("firefox").open("http://localhost:8080")
        self._start_subprocess("robot_control.app.app_viser_sliders")

    def start_viser_default(self):
        webbrowser.get("firefox").open("http://localhost:8080")
        self._start_subprocess("robot_control.app.app_viser")

    def _start_subprocess(self, module_path: str):
        self.root.destroy()

        subprocess.run(
            [sys.executable, "-m", module_path],
            cwd=self._get_project_root(),
        )

    def _get_project_root(self):
        # geht davon aus, dass GUI im Package läuft
        return None  # optional weglassen, siehe Erklärung unten

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    StartWindow().run()