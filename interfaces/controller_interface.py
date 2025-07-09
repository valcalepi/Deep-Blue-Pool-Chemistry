# /interfaces/controller_interface.py
from abc import ABC, abstractmethod

class ControllerInterface(ABC):
    """Interface for all controllers."""
    
    @abstractmethod
    def initialize(self):
        """Initialize the controller."""
        pass
    
    @abstractmethod
    def shutdown(self):
        """Perform cleanup operations."""
        pass
