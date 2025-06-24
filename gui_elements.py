import tkinter as tk

class GUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Chemical Calculator")

        self.customer_name_label = tk.Label(self.window, text="Customer Name:")
        self.customer_name_label.pack()
        self.customer_name_entry = tk.Entry(self.window)
        self.customer_name_entry.pack()

        self.pool_type_label = tk.Label(self.window, text="Pool Type:")
        self.pool_type_label.pack()
        self.pool_type_entry = tk.Entry(self.window)
        self.pool_type_entry.pack()

        self.pool_size_label = tk.Label(self.window, text="Pool Size (gallons):")
        self.pool_size_label.pack()
        self.pool_size_entry = tk.Entry(self.window)
        self.pool_size_entry.pack()

        self.pH_label = tk.Label(self.window, text="pH Level:")
        self.pH_label.pack()
        self.pH_entry = tk.Entry(self.window)
        self.pH_entry.pack()

        self.chlorine_label = tk.Label(self.window, text="Chlorine Level:")
        self.chlorine_label.pack()
        self.chlorine_entry = tk.Entry(self.window)
        self.chlorine_entry.pack()

        self.bromine_label = tk.Label(self.window, text="Bromine Level:")
        self.bromine_label.pack()
        self.bromine_entry = tk.Entry(self.window)
        self.bromine_entry.pack()

        self.alkalinity_label = tk.Label(self.window, text="Alkalinity Level:")
        self.alkalinity_label.pack()
        self.alkalinity_entry = tk.Entry(self.window)
        self.alkalinity_entry.pack()

        self.cyanuric_acid_label = tk.Label(self.window, text="Cyanuric Acid Level:")
        self.cyanuric_acid_label.pack()
        self.cyanuric_acid_entry = tk.Entry(self.window)
        self.cyanuric_acid_entry.pack()

        self.calcium_hardness_label = tk.Label(self.window, text="Calcium Hardness Level:")
        self.calcium_hardness_label.pack()
        self.calcium_hardness_entry = tk.Entry(self.window)
        self.calcium_hardness_entry.pack()

        self.stabilizer_label = tk.Label(self.window, text="Stabilizer Level:")
        self.stabilizer_label.pack()
        self.stabilizer_entry = tk.Entry(self.window)
        self.stabilizer_entry.pack()

        self.salt_label = tk.Label(self.window, text="Salt Level:")
        self.salt_label.pack()
        self.salt_entry = tk.Entry(self.window)
        self.salt_entry.pack()

        self.calculate_button = tk.Button(self.window, text="Calculate", command=self.calculate_chemicals)
        self.calculate_button.pack()

        self.result_label = tk.Label(self.window, text="Result:")
        self.result_label.pack()
        self.result_text = tk.Text(self.window)
        self.result_text.pack()

    def calculate_chemicals(self):
    	customer_name = self.customer_name_entry.get()
    	pool_type = self.pool_type_entry.get()
    	pool_size = float(self.pool_size_entry.get())  # Will crash if input is not numeric
    	pH = float(self.pH_entry.get())
    	chlorine = float(self.chlorine_entry.get())
        bromine = float(self.bromine_entry.get())
        alkalinity = float(self.alkalinity_entry.get())
        cyanuric_acid = float(self.cyanuric_acid_entry.get())
        calcium_hardness = float(self.calcium_hardness_entry.get())
        stabilizer = float(self.stabilizer_entry.get())
        salt = float(self.salt_entry.get())

        chemical_metrics = manage_pool(pool_type, pool_size, pH, chlorine, bromine, alkalinity, cyanuric_acid, calcium_hardness, stabilizer, salt)

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, str(chemical_metrics))
