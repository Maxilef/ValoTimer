import os
import tkinter as tk
import time
from pynput import keyboard
import subprocess
import pygetwindow as gw
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ValoTime")
        self.root.resizable(False, False)

        # Change the background color of the root window
        self.root.configure(bg="#424549")

        # Icon setup
        script_dir = os.path.dirname(__file__)
        icon_path = os.path.join(script_dir, 'icon.ico')
        self.root.iconbitmap(icon_path)

        # Key settings
        self.settings = {'start_stop': 'v', 'reset': 'r', 'start_rec': 'o'}
        self.is_recording = False
        self.last_key_press_time = 0
        self.debounce_time = 0.2
        self.ffmpeg_process = None
        self.output_file = None
        self.running = False
        self.is_reset = True
        self.start_time = 0
        self.elapsed_time = 0

        # UI setup
        self.title_label = tk.Label(root, text="Valo Timer by Maxilef", font=("Helvetica", 24), fg="red", bg="#424549")
        self.title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Best score label
        self.best_score_label = tk.Label(root, text="Meilleur Score: N/A", font=("Helvetica", 18), fg="gold", bg="#424549")
        self.best_score_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Listbox for last 10 results
        self.results_listbox = tk.Listbox(root, height=10, font=("Helvetica", 14), bg="#2c2f33", fg="white")
        self.results_listbox.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.label = tk.Label(root, text="00:00.000000", font=("Helvetica", 48), bg="#424549", fg="white")
        self.label.grid(row=1, column=1, columnspan=2, pady=10)

        self.seconds_label = tk.Label(root, text="0.000000", font=("Helvetica", 36), bg="#424549", fg="white")
        self.seconds_label.grid(row=2, column=1, columnspan=2, pady=10)

        self.instruction_frame = tk.Frame(root, bg="#424549")
        self.instruction_frame.grid(row=3, column=0, columnspan=3, pady=10)

        self.instruction_label = tk.Label(self.instruction_frame, font=("Helvetica", 14), bg="#424549", fg="#7289da")
        self.instruction_label.pack(pady=10)
        self.update_instruction_label()

        self.settings_button = tk.Button(root, text="Settings", command=self.open_settings_window, bg="gray", fg="red")
        self.settings_button.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        # Frame for the graph
        self.graph_frame = tk.Frame(root)
        self.graph_frame.grid(row=0, column=3, rowspan=5, padx=20, pady=20, sticky="nsew")

        # Container for the graph
        self.inner_frame = tk.Frame(self.graph_frame)
        self.inner_frame.grid(row=0, column=0, sticky="nsew")

        # Initialize the graph
        self.init_graph()

        # Load initial data
        self.load_results()

        # Keyboard listener
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def init_graph(self):
        self.figure, self.ax = plt.subplots(figsize=(10, 5))
        self.ax.set_title('Score en fonction de la date')
        self.ax.set_xlabel('Date')
        self.ax.set_ylabel('Score (s)')

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.inner_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.update_graph()

        # Connect hover event
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

    def update_graph(self):
        try:
            data = pd.read_csv("times_log.txt", sep=" - ", header=None, names=["Date", "Time"], engine='python')
            data["Time"] = data["Time"].str.replace(' secondes', '').astype(float)
            data["Index"] = range(1, len(data) + 1)

            self.ax.clear()
            self.ax.plot(data["Index"], data["Time"], marker='o')
            self.ax.set_title('Scores Chronologiques')
            self.ax.set_xlabel('Essai n°')
            self.ax.set_ylabel('Score (s)')
            self.ax.grid(True)
            self.canvas.draw()

            # Save data for hover
            self.hover_data = data

        except Exception as e:
            print(f"Erreur lors de la mise à jour du graphique : {e}")

    def on_hover(self, event):
        if event.inaxes == self.ax:
            if hasattr(self, 'annot'):
                self.annot.remove()
                del self.annot
                self.canvas.draw()

            for i, (index, row) in enumerate(self.hover_data.iterrows()):
                x, y = event.xdata, event.ydata
                if abs(x - row['Index']) < 0.5 and abs(y - row['Time']) < 0.1:
                    # Calculer la position de l'annotation en fonction des limites de la fenêtre
                    x_offset = 30 if x < (len(self.hover_data) / 2) else -150  # Ajustement basé sur la position de x
                    y_offset = 30

                    self.annot = self.ax.annotate(
                        f"Date: {row['Date']}\nScore: {row['Time']} s",
                        xy=(row['Index'], row['Time']),
                        xycoords='data',
                        xytext=(x_offset, y_offset),
                        textcoords='offset points',
                        bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="yellow"),
                        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2")
                    )
                    self.canvas.draw()
                    break



    def load_results(self):
        """Load the last 10 results and update the best score."""
        try:
            with open("times_log.txt", "r") as file:
                lines = file.readlines()

            # Get the last 10 results
            last_10_results = lines[-10:]
            self.results_listbox.delete(0, tk.END)
            for line in reversed(last_10_results):  # Reverse to display latest first
                # Extract only the time portion after " - "
                time_only = line.strip().split(" - ")[1]
                self.results_listbox.insert(tk.END, time_only)

            # Update the best score
            times = [float(line.split(" - ")[1].replace(" secondes", "")) for line in lines]
            if times:
                best_time = min(times)
                self.best_score_label.config(text=f"Meilleur Score: {best_time:.6f} secondes")

        except FileNotFoundError:
            print("Le fichier times_log.txt n'a pas été trouvé.")
        except Exception as e:
            print(f"Erreur lors du chargement des résultats : {e}")


    def on_press(self, key):
        current_time = time.time()
        if current_time - self.last_key_press_time < self.debounce_time:
            return
        self.last_key_press_time = current_time

        try:
            key_char = key.char
        except AttributeError:
            key_char = None

        if key_char == self.settings['start_stop']:
            if not self.running:
                self.start_timer()
            else:
                self.stop_timer()
        elif key_char == self.settings['reset']:
            self.reset_timer()
        elif key_char == self.settings['start_rec']:
            self.toggle_recording()

    def start_timer(self):
        if self.is_reset:  # Can only start if the timer has been reset
            self.running = True
            self.start_time = time.time() - self.elapsed_time
            self.is_reset = False  # The timer is no longer reset
            self.update_timer()
        else:
            print("Vous devez réinitialiser le chronomètre avant de le démarrer à nouveau.")

    def stop_timer(self):
        if not self.is_reset:
            self.running = False
            self.elapsed_time = time.time() - self.start_time

            # Stocker l'heure exacte pour cohérence
            exact_elapsed_time = self.elapsed_time

            # Mise à jour de l'affichage
            self.seconds_label.config(text=f"{exact_elapsed_time:.6f}")

            self.save_time_to_file(exact_elapsed_time)  # Passer le temps exact à la fonction
            self.update_graph()  # Mise à jour du graphique
            self.load_results()  # Mise à jour des résultats
        else:
            print("Le chronomètre a déjà été arrêté. Réinitialisez-le avant de recommencer.")


    def reset_timer(self):
        self.running = False
        self.elapsed_time = 0
        self.label.config(text="00:00.000000")
        self.seconds_label.config(text="0.000000")
        self.is_reset = True  # The timer is reset

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        # Find the Valorant window
        windows = gw.getWindowsWithTitle('VALORANT')

        if windows:
            self.window = windows[0]
            print(f"Fenêtre trouvée : {self.window.title}")
            print(f"Position : {self.window.left}, {self.window.top}, Taille : {self.window.width}x{self.window.height}")

            if self.window.left < 0 or self.window.top < 0:
                print("Les coordonnées de la fenêtre sont invalides. Capture de l'écran entier.")
                self.capture_area = None
            else:
                self.capture_area = f"{self.window.left},{self.window.top},{self.window.width},{self.window.height}"
        else:
            print("Fenêtre de Valorant non trouvée.")
            self.capture_area = None

        if not self.is_recording:
            self.is_recording = True
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.output_file = f'output_{timestamp}.mp4'
            ffmpeg_path = r'C:\Users\maxim\ffmpeg\bin\ffmpeg.exe'

            if self.capture_area:
                ffmpeg_input = f'-offset_x {self.window.left} -offset_y {self.window.top} -video_size {self.window.width}x{self.window.height}'
            else:
                ffmpeg_input = '-video_size 1920x1080 -offset_x 0 -offset_y 0'

            self.ffmpeg_process = subprocess.Popen([
                ffmpeg_path,
                '-f', 'gdigrab',
                '-framerate', '30',
                *ffmpeg_input.split(),
                '-i', 'desktop',
                '-c:v', 'libx264',
                '-preset', 'veryfast',
                '-crf', '28',
                '-pix_fmt', 'yuv420p',
                '-r', '30',
                '-loglevel', 'warning',
                self.output_file
            ], stdin=subprocess.PIPE)
            print(f"Enregistrement commencé, fichier : {self.output_file}")

    def stop_recording(self):
        if self.is_recording and self.ffmpeg_process:
            self.is_recording = False
            try:
                if self.ffmpeg_process.stdin:
                    self.ffmpeg_process.stdin.write(b'q')
                    self.ffmpeg_process.stdin.flush()
                self.ffmpeg_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                print("Le processus ffmpeg ne s'est pas arrêté à temps, tentative de terminaison forcée.")
                self.ffmpeg_process.kill()
                self.ffmpeg_process.wait()
            except Exception as e:
                print(f"Erreur lors de l'arrêt de l'enregistrement : {e}")
            finally:
                self.ffmpeg_process = None
                print("Enregistrement arrêté")

    def update_timer(self):
        if self.running:
            elapsed_time = time.time() - self.start_time
            mins, secs = divmod(int(elapsed_time), 60)
            microseconds = int((elapsed_time - int(elapsed_time)) * 1_000_000)

            time_format = f"{mins:02}:{secs:02}.{microseconds:06}"
            self.label.config(text=time_format)

            seconds_format = f"{elapsed_time:.6f}"
            self.seconds_label.config(text=seconds_format)

            self.root.after(10, self.update_timer)

    def save_time_to_file(self, exact_elapsed_time):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        with open("times_log.txt", "a") as file:
            file.write(f"{timestamp} - {exact_elapsed_time:.6f} secondes\n")

    def open_settings_window(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("300x230")

        tk.Label(settings_window, text="Start/Stop Key:").pack(pady=5)
        self.start_stop_entry = tk.Entry(settings_window)
        self.start_stop_entry.insert(0, self.settings['start_stop'])
        self.start_stop_entry.pack(pady=5)

        tk.Label(settings_window, text="Reset Key:").pack(pady=5)
        self.reset_entry = tk.Entry(settings_window)
        self.reset_entry.insert(0, self.settings['reset'])
        self.reset_entry.pack(pady=5)

        tk.Label(settings_window, text="Start Recording Key:").pack(pady=5)
        self.start_rec_entry = tk.Entry(settings_window)
        self.start_rec_entry.insert(0, self.settings['start_rec'])
        self.start_rec_entry.pack(pady=5)

        tk.Button(settings_window, text="Save", command=self.save_settings).pack(pady=10)

    def save_settings(self):
        self.settings['start_stop'] = self.start_stop_entry.get().lower()
        self.settings['reset'] = self.reset_entry.get().lower()
        self.settings['start_rec'] = self.start_rec_entry.get().lower()
        self.update_instruction_label()

    def update_instruction_label(self):
        instruction_text = (f"Appuyez sur '{self.settings['start_stop']}' pour démarrer/arrêter le timer, "
                            f"sur '{self.settings['reset']}' pour réinitialiser, "
                            f"et sur '{self.settings['start_rec']}' pour démarrer/arrêter l'enregistrement.")
        self.instruction_label.config(text=instruction_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
