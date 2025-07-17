# app/views/basic_dashboard_view.py

import tkinter as tk
from tkinter import ttk

class BasicDashboardView:
    def __init__(self, parent, services):
        self.frame = ttk.Frame(parent, padding=20)
        self.frame.pack(fill="both", expand=True)

        label = ttk.Label(self.frame, text="Basic Dashboard Loaded", font=("Arial", 16))
        label.pack(pady=20)
