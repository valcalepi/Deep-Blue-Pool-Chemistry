# readings_presenter.py

class ReadingsPresenter:
    def __init__(self, readings):
        """
        Initialize the ReadingsPresenter with a dictionary of water quality readings.
        
        Args:
            readings (dict): A dictionary containing water quality readings.
        """
        self.readings = readings

    def present_readings(self):
        """
        Present the water quality readings in a user-friendly format.
        
        Returns:
            str: A string containing the presented readings.
        """
        presented_readings = "Water Quality Readings:\n"
        
        for parameter, value in self.readings.items():
            presented_readings += f"{parameter}: {value}\n"
        
        return presented_readings

# Example usage:
readings = {
    "pH": 7.2,
    "Chlorine": 1.5,
    "Alkalinity": 80,
    "Calcium Hardness": 200
}

presenter = ReadingsPresenter(readings)
print(presenter.present_readings())
