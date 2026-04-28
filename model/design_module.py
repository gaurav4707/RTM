"""
Design Module Model

This module defines the DesignModule data class that represents
a software design module in the traceability system.
"""


class DesignModule:
    """
    Represents a software design module.
    
    Attributes:
        module_id (str): Unique identifier for the module (e.g., 'DM-001')
        name (str): Name of the design module
        description (str): Detailed description of the module's purpose
    """
    
    def __init__(self, module_id: str, name: str, description: str):
        """
        Initialize a new DesignModule instance.
        
        Args:
            module_id: Unique identifier for the design module
            name: Short name for the module
            description: Detailed description of the module
        """
        self.module_id = module_id
        self.name = name
        self.description = description
    
    def __repr__(self) -> str:
        """Return a string representation of the design module."""
        return f"DesignModule(id={self.module_id}, name={self.name})"
    
    def to_tuple(self) -> tuple:
        """
        Convert the design module to a tuple for database operations.
        
        Returns:
            Tuple containing (module_id, name, description)
        """
        return (self.module_id, self.name, self.description)
