from tkinter import *
import csv

def open_coords_gui(parent, on_done=None):
    window = Toplevel(parent)
    window.geometry("2500x1200")

    x_list = []
    y_list = []

    def values_to_csv(x_list: list[float], y_list: list[float]):
        with open("robot_control/data/trajectory.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["x", "y"])
            for x, y in zip(x_list, y_list):
                writer.writerow([x, y])

    # Eingabe für die Anzahl Punkte
    Label(window, text="Anzahl der Punkte", font=("Arial", 25)).grid(column=0, row=0)

    entry_number_of_points = Entry(window, font=("Arial", 25))
    entry_number_of_points.grid(column=1, row=0)

    #Status-Label für Fehlermeldungen
    status_label = Label(window, text="", font=("Arial", 25))
    status_label.grid(column=0, row=3, columnspan=2)
    status2_label = Label(window, text="", font=("Arial", 25))

    # Funktion, die beim Klick auf "Bestätigen" ausgeführt wird
    def check_points_and_create_entries():
        text = entry_number_of_points.get()
        if text == "":
            print("Bitte eine Zahl eingeben.")
            status_label.config(text="Bitte eine Zahl eingeben.", fg="red")
            return

        try:
            number_of_points = int(text)
        except ValueError:
            print("Ungültige Eingabe! Zahl von 1 bis 10 erforderlich")
            status_label.config(text="Ungültige Zahl!", fg="red")
            return

        if number_of_points <= 0 or number_of_points >= 11:
            print("Die Anzahl der Punkte muss zwischen 1 und 10 (1 <= x <= 11) liegen.")
            status_label.config(text="Die Anzahl der Punkte muss zwischen 1 und 10 liegen.", fg="red")
            return

        # Alte Eingabefelder und Hinweis löschen, falls schon welche existieren
        status_label.config(text="")
        entry_number_of_points.config(state="disabled")
        for widget in x_list + y_list:
            widget.destroy()
        x_list.clear()
        y_list.clear()

        Label(window, font=("Arial", 25), text="Punkt").grid(column=0, row=3)
        Label(window, font=("Arial", 25), text="x").grid(column=1, row=3)
        Label(window, font=("Arial", 25), text="y").grid(column=2, row=3)
        # Neue Eingabefelder erzeugen
        for i in range(number_of_points):
            Label(window, text=f"Punkt {i+1}" ,font=("Arial", 25)).grid(column=0, row=i+4)
            entry_x = Entry(window, font=("Arial", 20))
            entry_y = Entry(window, font=("Arial", 20))
            entry_x.grid(column=1, row=i+4)
            entry_y.grid(column=2, row=i+4)
            x_list.append(entry_x)
            y_list.append(entry_y)

        # Submit-Button erzeugen (nur einmal, z. B. unter den Feldern)
        submit_btn = Button(window, text="Submit", font=("Arial", 20), command=submit_action)
        submit_btn.grid(column=1, row=number_of_points+4, columnspan=3, pady=10)
        status2_label.grid(column=0, row=number_of_points+5, columnspan=2)

    def warning(msg: str):
        print(msg)
        status2_label.config(text=msg, fg="red")



    # Funktion Submit
    def submit_action():
        x_vals = [e.get() for e in x_list]
        y_vals = [e.get() for e in y_list]
        print("X-Werte:", x_vals)
        print("Y-Werte:", y_vals)

        for i, x in enumerate(x_vals):
            if x == "":
                msg = "Mindestens eine x-Eingabe fehlt!"
                warning(msg)
                return
            try:
                x_vals[i] = float(x)
            except ValueError:
                msg = "Mindestens eine ungültige x-Eingabe!"
                warning(msg)
                return

        for i, y in enumerate(y_vals):
            if y == "":
                msg = "Mindestens eine y-Eingabe fehlt!"
                warning(msg)
                return
            try:
                y_vals[i] = float(y)
            except ValueError:
                msg = "Mindestens eine ungültige y-Eingabe!"
                warning(msg)
                return
        values_to_csv(x_vals, y_vals)
        window.destroy()
        if on_done:
            on_done()

    # Button für Anzahl Punkte
    Button(window, text="Bestätigen", font=("Arial", 25), command=check_points_and_create_entries).grid(column=1, row=1)

    #window.mainloop()