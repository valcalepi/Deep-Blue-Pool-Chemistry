import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
from core.analyzer import TestStripAnalyzer
from core.sensor import SensorManager
from core.dosing_calculator import calculate_volume, recommend_dose
from data.excel_sync import append_to_excel as log_chemistry_data

class PoolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Deep Blue Pool Chemistry Manager")

        tabs = ttk.Notebook(root)
        tabs.pack(expand=1, fill="both")

        self.strip_tab = ttk.Frame(tabs)
        self.sensor_tab = ttk.Frame(tabs)
        self.dose_tab = ttk.Frame(tabs)
        self.dashboard_tab = ttk.Frame(tabs)

        tabs.add(self.strip_tab, text="Test Strip")
        tabs.add(self.sensor_tab, text="Sensor")
        tabs.add(self.dose_tab, text="Dosing Calculator")
        tabs.add(self.dashboard_tab, text="Dashboard")

        self.setup_strip_tab()
        self.setup_sensor_tab()
        self.setup_dose_tab()
        self.setup_dashboard_tab()

    def setup_strip_tab(self):
        tk.Button(self.strip_tab, text="Analyze Test Strip", command=self.load_image).pack(pady=20)

    def setup_sensor_tab(self):
        tk.Button(self.sensor_tab, text="Read Sensor", command=self.read_sensor).pack(pady=20)

    def setup_dose_tab(self):
        entries = {}
        for i, label in enumerate(["Length (ft)", "Width (ft)", "Avg Depth (ft)", "Chemical"]):
            tk.Label(self.dose_tab, text=label).grid(row=i, column=0)
            entries[label] = tk.Entry(self.dose_tab)
            entries[label].grid(row=i, column=1)

        def calculate():
            try:
                vol = calculate_volume(float(entries["Length (ft)"].get()), float(entries["Width (ft)"].get()), float(entries["Avg Depth (ft)"].get()))
                dose = recommend_dose(vol, entries["Chemical"].get().lower())
                messagebox.showinfo("Dose Recommendation", f"Pool Volume: {vol:.0f} gal\nRecommended {entries['Chemical'].get().title()} Dose: {dose} gal")
            except ValueError:
                messagebox.showerror("Input Error", "Please enter valid numbers.")

        tk.Button(self.dose_tab, text="Calculate", command=calculate).grid(row=4, column=0, columnspan=2)

    def setup_dashboard_tab(self):
        tk.Label(self.dashboard_tab, text="Click below to launch dashboard in browser").pack(pady=10)
        tk.Button(self.dashboard_tab, text="Launch Dashboard", command=lambda: webbrowser.open("http://localhost:8501")).pack()

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

if __name__ == "__main__":
    root = tk.Tk()
    app = PoolApp(root)
    root.mainloop()
