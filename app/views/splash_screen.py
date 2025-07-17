import tkinter as tk
from PIL import Image, ImageTk

class SplashScreen:
    def __init__(self, root, duration=3000):
        self.root = root
        self.duration = duration
        self.window = tk.Toplevel(root)
        self.window.overrideredirect(True)
        self.window.geometry("600x300+400+200")
        self.window.configure(bg="#003B73")

        self._build_ui()
        self.window.after(self.duration, self.window.destroy)

    def _build_ui(self):
        try:
            logo = Image.open("assets/images/deep_blue_logo.png").resize((120, 120))
            photo = ImageTk.PhotoImage(logo)
            label_img = tk.Label(self.window, image=photo, bg="#003B73")
            label_img.image = photo
            label_img.pack(pady=20)
        except Exception:
            tk.Label(self.window, text="Deep Blue", font=("Segoe UI", 20), fg="#47E6B1", bg="#003B73").pack(pady=20)

        tk.Label(self.window, text="Initializing sensors and dashboard...", font=("Segoe UI", 10), fg="white", bg="#003B73").pack(pady=10)
