# /interfaces/view_interface.py
from abc import ABC, abstractmethod

class ViewInterface(ABC):
    """Interface for all views."""
    
    @abstractmethod
    def display(self, data):
        """Display data to the user."""
        pass
    
    @abstractmethod
    def clear(self):
        """Clear the display."""
        pass
