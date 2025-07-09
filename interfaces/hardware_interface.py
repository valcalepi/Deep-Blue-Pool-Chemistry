# /interfaces/hardware_interface.py
from abc import ABC, abstractmethod

class HardwareInterface(ABC):
    """Abstract interface for hardware interactions."""
    
    @abstractmethod
    def connect(self):
        """Establish connection to the hardware."""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnect from the hardware."""
        pass
    
    @abstractmethod
    def send_command(self, command):
        """Send command to the hardware."""
        pass
    
    @abstractmethod
    def read_data(self):
        """Read data from the hardware."""
        pass
