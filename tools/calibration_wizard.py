import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
import json

class CalibrationWizard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RGB Calibration Wizard")
        self.image_path = None
        self.image = None
        self.photo = None
        self.canvas = None
        self.samples = {}

        self._build_ui()
        self.root.mainloop()

    def _build_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Button(frame, text="Load Strip Image", command=self._load_image).pack(side="left", padx=5)
        tk.Button(frame, text="Save Calibration", command=self._save_calibration).pack(side="left", padx=5)

        self.canvas = tk.Canvas(self.root, width=600, height=400, bg="gray")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_click)

    def _load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.bmp")])
        if not path:
            return
        self.image_path = path
        self.image = Image.open(path)
        self.image = self.image.resize((600, 400))
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

    def _on_click(self, event):
        if not self.image:
            return

        x, y = event.x, event.y
        rgb = self.image.getpixel((x, y))

        chem_name = simpledialog.askstring("Chemical Name", "Enter chemical name (e.g. pH, chlorine):")
        if not chem_name:
            return

        value = simpledialog.askfloat("Chemical Value", f"Enter value for {chem_name} (e.g. 7.4):")
        if value is None:
            return

        self.samples[chem_name] = {
            "rgb": list(rgb),
            "value": value
        }

        messagebox.showinfo("Sample Added", f"{chem_name} = {value}, RGB = {rgb}")

    def _save_calibration(self):
        if not self.samples:
            messagebox.showwarning("No Samples", "No samples to save.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not path:
            return

        with open(path, "w") as f:
            json.dump(self.samples, f, indent=4)

        messagebox.showinfo("Saved", f"Calibration saved to {path}")

if __name__ == "__main__":
    CalibrationWizard()
