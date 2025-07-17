import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from app.views.dashboard_theme import COLORS, FONTS, SPACING
from services.chemical_analysis import evaluate
from services.image_processing.color_calibration import ColorCalibrator

class DashboardView:
    def __init__(self, parent, services):
        self.parent = parent
        self.services = services
        self.entries = {}
        self.strip_results = {}
        self.calibrator = ColorCalibrator()
        self._build_ui()

    def _build_ui(self):
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill="both", expand=True)

        self._build_header()
        self._build_manual_entry()
        self._build_strip_analysis()
        self._build_analysis_summary()
        self._build_recent_readings()
        self._build_history_chart()

    def _build_header(self):
        header = tk.Canvas(self.frame, height=60, highlightthickness=0)
        header.pack(fill="x")
        header.create_rectangle(0, 0, 1024, 60, fill=COLORS["deep_blue"])
        header.create_text(512, 30, text="🌊 Deep Blue Pool Chemistry Dashboard", font=FONTS["title"], fill=COLORS["text_primary"])

    def _build_manual_entry(self):
        section = ttk.LabelFrame(self.frame, text="Manual Entry", padding=SPACING["pad_x"])
        section.pack(fill="x", padx=SPACING["pad_x"], pady=SPACING["pad_y"])

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
        section = ttk.LabelFrame(self.frame, text="Test Strip Analyzer", padding=SPACING["pad_x"])
        section.pack(fill="x", padx=SPACING["pad_x"], pady=SPACING["pad_y"])

        ttk.Button(section, text="Capture Strip", command=self._capture_strip).pack()
        ttk.Button(section, text="Analyze Strip", command=self._analyze_strip).pack(pady=5)
        ttk.Button(section, text="Save to Database", command=self._save_strip_reading).pack()

        self.image_label = ttk.Label(section)
        self.image_label.pack(pady=5)

        self.strip_output = tk.Text(section, height=8, width=80)
        self.strip_output.pack()

    def _build_analysis_summary(self):
        section = ttk.LabelFrame(self.frame, text="Analysis Summary", padding=SPACING["pad_x"])
        section.pack(fill="x", padx=SPACING["pad_x"], pady=SPACING["pad_y"])

        self.summary_frame = ttk.Frame(section)
        self.summary_frame.pack()

    def _build_recent_readings(self):
        section = ttk.LabelFrame(self.frame, text="Recent Readings", padding=SPACING["pad_x"])
        section.pack(fill="x", padx=SPACING["pad_x"], pady=SPACING["pad_y"])

        self.recent_text = tk.Text(section, height=6, width=80)
        self.recent_text.pack()

        self._load_recent_readings()

    def _build_history_chart(self):
        section = ttk.LabelFrame(self.frame, text="📈 Historical Trends", padding=SPACING["pad_x"])
        section.pack(fill="both", expand=True, padx=SPACING["pad_x"], pady=SPACING["pad_y"])

        fig, ax = plt.subplots(figsize=(6, 3))
        rows = self.services["database"].get_recent_readings(limit=10)

        timestamps = [r[1] for r in rows]
        pH_values = [r[2] for r in rows]
        chlorine_values = [r[3] for r in rows]

        ax.plot(timestamps, pH_values, label="pH", color="#00BFFF", marker="o")
        ax.plot(timestamps, chlorine_values, label="Free Chlorine", color="#47E6B1", marker="x")
        ax.set_title("Recent pH & Free Chlorine Levels")
        ax.set_xticklabels(timestamps, rotation=45, fontsize=8)
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=section)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

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
        flat_results = {k: v["value"] for k, v in results.items()}
        self._display_analysis(flat_results)

    def _save_strip_reading(self):
        if self.strip_results:
            data = {k: v["value"] for k, v in self.strip_results.items()}
            data["source"] = "strip"
            self.services["database"].insert_reading(data)
            self._load_recent_readings()

    def _display_analysis(self, readings):
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        issues = evaluate(readings)
        for metric, status, msg in issues:
            value = readings.get(metric)
            rgb = [int(float(value))]*3 if value else [0, 0, 0]
            confidence = self.calibrator.rgb_confidence(rgb, rgb)

            tile = ttk.Frame(self.summary_frame, relief="ridge", borderwidth=2)
            tile.pack(side="left", padx=5, pady=5)

            color = {
                "Good": COLORS["safe"],
                "Warning": COLORS["warning"],
                "Critical": COLORS["critical"]
            }.get(status, COLORS["tile_glow"])

            label = tk.Label(tile, text=f"{metric}\n{value}", bg=color, fg="black", width=12, height=4)
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
