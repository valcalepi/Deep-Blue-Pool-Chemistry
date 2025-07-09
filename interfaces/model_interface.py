# /interfaces/model_interface.py
from abc import ABC, abstractmethod

class ModelInterface(ABC):
    """Interface for all models."""
    
    @abstractmethod
    def load_data(self):
        """Load data from storage."""
        pass
    
    @abstractmethod
    def save_data(self, data):
        """Save data to storage."""
        pass
