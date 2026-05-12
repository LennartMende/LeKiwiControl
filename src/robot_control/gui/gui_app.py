from tkinter import *
from tkinter import filedialog
from robot_control.gui.gui_coords import open_coords_gui
import os, shutil


def run_gui():
    def warning(message: str, row: int):
        print(message)
        status_label.config(text=message, fg="red")

    global root
    root = Tk()
    root.geometry("2500x1200")

    status_label = Label(root, text="", font=("Arial", 20))
    status_label.grid(column=0, row=1)

    # Zum Löschen des Screens bei jeder neuen Auswahl
    def clear_screen():
        for widget in root.winfo_children():
            if widget != status_label:
                widget.destroy()

    # live Steuerung mit Leader/ Controller
    def live_action():
        clear_screen()
        teleop_or_controller = Label(root, text="Soll der Roboter teleoperativ oder mit dem Controller gesteuert werden?", font=("Arial", 25)).grid(column=0, row=0)
        teleop_btn = Button(root, text="Teleoperieren", font=("Arial", 20), command=teleop_action)
        teleop_btn.grid(column=0, row=1)
        controller_btn = Button(root, text="Mit Controller steuern", font=("Arial", 20), command=controller_action)
        controller_btn.grid(column=1, row=1)


    def teleop_action():
        clear_screen()
        global mode
        mode = 1
        root.destroy()

    def controller_action():
        clear_screen()
        global mode
        mode = 2
        root.destroy()

    # benutzerdefinierte Trajektorie 
    def userdef_action():
        clear_screen()
        letter_or_coords = Label(root, text="Soll der Roboter einen Buchstaben zeichnen oder Koordinaten abarbeiten?", font=("Arial", 25))
        letter_or_coords.grid(column=0, row=0)
        letter_btn = Button(root, text="Buchstaben zeichnen", font=("Arial", 20), command=letter_action)
        letter_btn.grid(column=0, row=1)
        coords_btn = Button(root, text="Koordinaten abarbeiten", font=("Arial", 20), command=coords_action)
        coords_btn.grid(column=1, row=1)

    def letter_action():
        clear_screen()
        Label(root, text ="Welcher Buchstabe soll gezeichnet werden?", font=("Arial", 25)).grid(column=0, row=0)
        letter_entry = Entry(root, font=("Arial", 20))
        letter_entry.grid(column=0, row=2)
        Button(root, text="Bestätigen", font=("Arial", 25), command=lambda: check_letter(letter_entry)).grid(column=1, row=1)

    def check_letter(l_entry):
        global letter
        letter = l_entry.get()
        if len(letter) != 1:
            warning(message="Bitte genau einen Buchstaben eingeben.", row=1)
            return
        if not((ord(letter) >= 65 and ord(letter) <=90) or (ord(letter) >= 97 and ord(letter) <=122)):
            warning(message=f"Bitte einen Buchstaben eingeben. {letter} ist kein Buchstabe", row=1)
            return
        
        letter = letter.lower()
        status_label.config(text="")
        l_entry.config(state="disabled")

        global mode
        mode = 3
        root.destroy()


    def coords_action():
        clear_screen()
        coords = Label(root, text ="Wie werden die Koordinaten vorgegeben?", font=("Arial", 25))
        coords.grid(column=0, row=0)
        gui_btn = Button(root, text="Jetzt Koordinaten über die GUI vorgeben", font=("Arial", 20), command=gui_action)
        gui_btn.grid(column=0, row=1)
        csv_btn = Button(root, text="Gespeicherte csv verwenden", font=("Arial", 20), command=csv_action)
        csv_btn.grid(column=1, row=1)

    def gui_action():
        clear_screen()
        def on_coords_done():
            global mode
            mode = 4
            root.destroy()
        open_coords_gui(root, on_done=on_coords_done)

    def open_file() -> None:
        filepath = filedialog.askopenfilename()
        print("File will be retrieved from ", filepath)
        print("filepath = ", filepath)
        print()
        file = Label(root, text =f"Die Datei aus {filepath} wird genommen.", font=("Arial", 25)).grid(column=0, row=0)
        source = os.path.abspath(filepath)
        cwd = os.getcwd()
        target = ""
        if cwd.endswith("my_programs"):
            target = cwd + "/robot_control/data/trajectory.csv"
        elif cwd.endswith("robot_control"):
            target = cwd + "/data/trajectory.csv"
        elif cwd.endswith("robot_control/app"):
            target = os.path.abspath("../data/trajectory.csv")
        else:
            raise Exception("You have to be in my_programs, my_programs/robot_control or in my_programs/robot_control/app")
        print("source = ", source, " target = ", target)
        if (source != target):
            shutil.copy(filepath, target)

    def csv_action():
        clear_screen()
        global mode
        open_file()
        mode = 4
        root.destroy()

    gui_btn = Button(root, text="GUI", font=("Arial", 20), command=gui_action)
    csv_btn = Button(root, text="CSV", font=("Arial", 20), command=csv_action)


    live_or_userdef = Label(root, text="Hallo.\n Soll der Roboter live gesteuert werden oder soll er eine benutzerdefinierte Trajektorie verfolgen?", font=("Arial", 25))
    live_or_userdef.grid(column=0, row=0)
    live_btn = Button(root, text="Live steuern", font=("Arial", 20), command=live_action)
    live_btn.grid(column=0, row=1)
    userdef_btn = Button(root, text="Trajektorie verfolgen", font=("Arial", 20), command=userdef_action)
    userdef_btn.grid(column=1, row=1)

    
    root.mainloop()
    return