import tkinter as tk
from tkinter import filedialog, messagebox
from core.analyzer import TestStripAnalyzer
from core.sensor import SensorManager
from core.dosing_calculator import calculate_volume, recommend_dose
from data.excel_sync import append_to_excel as log_chemistry_data
from data.dashboard import launch_dashboard

class PoolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Deep Blue Pool Chemistry Manager")

        tk.Button(root, text="Analyze Test Strip", command=self.load_image).pack(pady=10)
        tk.Button(root, text="Read Sensor", command=self.read_sensor).pack(pady=10)
        tk.Button(root, text="Launch Dashboard", command=launch_dashboard).pack(pady=10)
        tk.Button(root, text="Dosing Calculator", command=self.open_dosing_calculator).pack(pady=10)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
        if not path:
            return
        analyzer = TestStripAnalyzer()
        hsv = analyzer.preprocess_image(path)
        zones = analyzer.extract_color_zones(hsv)
        results = analyzer.interpret_zones(zones)
        log_chemistry_data(results)
        messagebox.showinfo("Test Strip Results", "\n".join(f"{k}: {v}" for k, v in results.items()))

    def read_sensor(self):
        sensor = SensorManager()
        try:
            sensor.connect()
            data = sensor.read_data()
            log_chemistry_data(data)
            messagebox.showinfo("Sensor Readings", "\n".join(f"{k}: {v}" for k, v in data.items()))
        except Exception as e:
            messagebox.showerror("Sensor Error", str(e))

    def open_dosing_calculator(self):
        top = tk.Toplevel()
        top.title("Dosing Calculator")

        tk.Label(top, text="Length (ft)").grid(row=0, column=0)
        tk.Label(top, text="Width (ft)").grid(row=1, column=0)
        tk.Label(top, text="Avg Depth (ft)").grid(row=2, column=0)
        tk.Label(top, text="Chemical").grid(row=3, column=0)

        length = tk.Entry(top)
        width = tk.Entry(top)
        depth = tk.Entry(top)
        chemical = tk.Entry(top)

        length.grid(row=0, column=1)
        width.grid(row=1, column=1)
        depth.grid(row=2, column=1)
        chemical.grid(row=3, column=1)

        def calculate():
            try:
                vol = calculate_volume(float(length.get()), float(width.get()), float(depth.get()))
                dose = recommend_dose(vol, chemical.get().lower())
                messagebox.showinfo("Dose Recommendation", f"Pool Volume: {vol:.0f} gal\nRecommended {chemical.get().title()} Dose: {dose} gal")
            except ValueError:
                messagebox.showerror("Input Error", "Please enter valid numbers.")

        tk.Button(top, text="Calculate", command=calculate).grid(row=4, column=0, columnspan=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = PoolApp(root)
    root.mainloop()
