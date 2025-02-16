from abc import ABC, abstractmethod

class BaseTool(ABC):
    """Abstract base class for all tools"""
    
    def __init__(self, name, description):
        self._name = name.lower()  # Store the name in lowercase for consistency
        self._description = description
    
    @property
    def name(self):
        """Getter for tool name."""
        return self._name

    @property
    def description(self):
        """Getter for tool description."""
        return self._description
    
    @abstractmethod
    def use(self, query):
        """Each tool must implement its own `use` method"""
        pass
