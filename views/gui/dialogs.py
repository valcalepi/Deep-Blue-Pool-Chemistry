import tkinter as tk
from .components import LabeledEntry

class SaveDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Save Pool Data")
        self.geometry("400x200")

        self.label = tk.Label(self, text="Are you sure you want to save the pool data?")
        self.label.pack(fill="x")
        
        self.yes_button = tk.Button(self, text="Yes", command=self.on_yes)
        self.no_button = tk.Button(self, text="No", command=self.on_no)
        
        self.yes_button.pack(side="left")
        self.no_button.pack(side="left")
    
    def on_yes(self):
        print("Data saved!")
        self.destroy()
    
    def on_no(self):
        self.destroy()
