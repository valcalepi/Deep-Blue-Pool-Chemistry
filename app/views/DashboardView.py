import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from services.chemical_analysis import evaluate
from services.image_processing.color_calibration import rgb_confidence

class DashboardView:
    def __init__(self, parent, services):
        self.parent = parent
        self.services = services
        self.entries = {}
        self.strip_results = {}
        self._build_ui()

    def _build_ui(self):
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill="both", expand=True)

        self._build_header()
        self._build_manual_entry()
        self._build_strip_analysis()
        self._build_analysis_summary()
        self._build_recent_readings()

    def _build_header(self):
        header = ttk.Label(self.frame, text="🌊 Deep Blue Pool Chemistry Dashboard", font=("Segoe UI", 18, "bold"))
        header.pack(pady=10)

    def _build_manual_entry(self):
        section = ttk.LabelFrame(self.frame, text="Manual Entry")
        section.pack(fill="x", padx=10, pady=5)

        metrics = [
            "pH", "free_chlorine", "total_chlorine", "alkalinity",
            "calcium", "cyanuric_acid", "bromine", "salt",
            "temperature", "water_volume"
        ]

        for metric in metrics:
            row = ttk.Frame(section)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=metric.replace("_", " ").title(), width=20).pack(side="left")
            entry = ttk.Entry(row)
            entry.pack(side="left", fill="x", expand=True)
            self.entries[metric] = entry

        ttk.Button(section, text="Analyze", command=self._submit_manual_reading).pack(pady=5)
        ttk.Button(section, text="Save to Database", command=self._save_manual_reading).pack()

    def _build_strip_analysis(self):
        section = ttk.LabelFrame(self.frame, text="Test Strip Analyzer")
        section.pack(fill="x", padx=10, pady=5)

        ttk.Button(section, text="Capture Strip", command=self._capture_strip).pack()
        ttk.Button(section, text="Analyze Strip", command=self._analyze_strip).pack(pady=5)
        ttk.Button(section, text="Save to Database", command=self._save_strip_reading).pack()

        self.image_label = ttk.Label(section, text="No image")
        self.image_label.pack(pady=5)

        self.strip_output = tk.Text(section, height=8, width=80)
        self.strip_output.pack()

    def _build_analysis_summary(self):
        section = ttk.LabelFrame(self.frame, text="Analysis Summary")
        section.pack(fill="x", padx=10, pady=5)

        self.summary_frame = ttk.Frame(section)
        self.summary_frame.pack()

    def _build_recent_readings(self):
        section = ttk.LabelFrame(self.frame, text="Recent Readings")
        section.pack(fill="x", padx=10, pady=5)

        self.recent_text = tk.Text(section, height=6, width=80)
        self.recent_text.pack()

        self._load_recent_readings()

    def _submit_manual_reading(self):
        readings = {k: v.get() for k, v in self.entries.items()}
        self._display_analysis(readings)

    def _save_manual_reading(self):
        readings = {k: v.get() for k, v in self.entries.items()}
        readings["source"] = "manual"
        self.services["database"].insert_reading(readings)
        self._load_recent_readings()

    def _capture_strip(self):
        path = self.services["test_strip"].capture_image()
        if path:
            image = self.services["test_strip"].get_image_preview()
            if image:
                photo = ImageTk.PhotoImage(image)
                self.image_label.configure(image=photo)
                self.image_label.image = photo

    def _analyze_strip(self):
        results = self.services["test_strip"].analyze()
        self.strip_results = results
        self.strip_output.delete("1.0", tk.END)
        for k, v in results.items():
            self.strip_output.insert(tk.END, f"{k}: {v}\n")
        self._display_analysis(results)

    def _save_strip_reading(self):
        if self.strip_results:
            data = self.strip_results.copy()
            data["source"] = "strip"
            self.services["database"].insert_reading(data)
            self._load_recent_readings()

    def _display_analysis(self, readings):
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        issues = evaluate(readings)
        for metric, status, msg in issues:
            rgb = readings.get(metric)
            confidence = rgb_confidence([int(float(rgb))]*3, [int(float(rgb))]*3) if rgb else 0
            tile = ttk.Frame(self.summary_frame, relief="ridge", borderwidth=2)
            tile.pack(side="left", padx=5, pady=5)

            color = {
                "Good": "#47E6B1",
                "Warning": "#FFD700",
                "Critical": "#FF6347"
            }.get(status, "#D3D3D3")

            label = tk.Label(tile, text=f"{metric}\n{readings.get(metric)}", bg=color, width=12, height=4)
            label.pack()

            bar = ttk.Progressbar(tile, value=confidence, maximum=100)
            bar.pack(fill="x", padx=5)
            ttk.Label(tile, text=f"Confidence: {confidence}%").pack()

            ttk.Label(tile, text=msg, wraplength=120).pack()

    def _load_recent_readings(self):
        self.recent_text.delete("1.0", tk.END)
        rows = self.services["database"].get_recent_readings(limit=5)
        for row in rows:
            self.recent_text.insert(tk.END, f"{row}\n")
