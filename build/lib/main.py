import tkinter as tk
import time
from pynput import keyboard

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ValoTime")  # Set window title
        self.root.resizable(False, False)  # Disable window resizing

        # Set window icon (replace 'path_to_icon.ico' with the actual path to the icon file)
        self.root.iconbitmap('icon.ico')

        # Title label
        self.title_label = tk.Label(root, text="Valo Timer by Maxilef", font=("Helvetica", 24), fg="red")
        self.title_label.pack()

        # Timer label with full precision
        self.label = tk.Label(root, text="00:00.000000", font=("Helvetica", 48))
        self.label.pack()

        # Timer label in seconds
        self.seconds_label = tk.Label(root, text="0.000000", font=("Helvetica", 36))
        self.seconds_label.pack()

        # Instruction frame
        self.instruction_frame = tk.Frame(root, bg="blue")
        self.instruction_frame.pack(fill="both", expand=True)

        # Instruction label
        self.instruction_label = tk.Label(self.instruction_frame, text="Appuyez sur 'V' pour démarrer/arrêter le timer, et sur 'R' pour réinitialiser.", font=("Helvetica", 14), bg="blue", fg="white")
        self.instruction_label.pack(pady=10)

        self.start_time = None
        self.running = False
        self.elapsed_time = 0

        # Start listening to keyboard
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def on_press(self, key):
        if key == keyboard.KeyCode.from_char('v'):
            if not self.running:
                self.start_timer()
            else:
                self.stop_timer()
        elif key == keyboard.KeyCode.from_char('r'):
            self.reset_timer()

    def start_timer(self):
        self.running = True
        self.start_time = time.time() - self.elapsed_time
        self.update_timer()

    def stop_timer(self):
        self.running = False
        self.elapsed_time = time.time() - self.start_time

    def reset_timer(self):
        self.running = False
        self.elapsed_time = 0
        self.label.config(text="00:00.000000")
        self.seconds_label.config(text="0.000000")

    def update_timer(self):
        if self.running:
            elapsed_time = time.time() - self.start_time
            mins, secs = divmod(int(elapsed_time), 60)
            microseconds = int((elapsed_time - int(elapsed_time)) * 1_000_000)

            # Full precision time format
            time_format = f"{mins:02}:{secs:02}.{microseconds:06}"
            self.label.config(text=time_format)

            # Seconds only format
            seconds_format = f"{elapsed_time:.6f}"
            self.seconds_label.config(text=seconds_format)

            self.root.after(10, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
