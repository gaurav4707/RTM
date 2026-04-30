"""
Design Module Model

This module defines the DesignModule data class that represents
a software design module in the traceability system.
"""


from dataclasses import dataclass

@dataclass
class DesignModule:
    """
    Represents a software design module.
    
    Attributes:
        module_id (str): Unique identifier for the module (e.g., 'DM-001')
        name (str): Name of the design module
        description (str): Detailed description of the module's purpose
    """
    module_id: str
    name: str
    description: str
    
    def to_tuple(self) -> tuple:
        """
        Convert the design module to a tuple for database operations.
        
        Returns:
            Tuple containing (module_id, name, description)
        """
        return (self.module_id, self.name, self.description)
