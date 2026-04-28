"""
Requirement Model Module

This module defines the Requirement data class that represents
a software requirement in the traceability system.
"""


class Requirement:
    """
    Represents a software requirement.
    
    Attributes:
        req_id (str): Unique identifier for the requirement (e.g., 'REQ-001')
        description (str): Detailed description of the requirement
        req_type (str): Type of requirement - 'Functional' or 'Non-Functional'
    """
    
    def __init__(self, req_id: str, description: str, req_type: str):
        """
        Initialize a new Requirement instance.
        
        Args:
            req_id: Unique identifier for the requirement
            description: Description of what the requirement specifies
            req_type: Either 'Functional' or 'Non-Functional'
        """
        self.req_id = req_id
        self.description = description
        self.req_type = req_type
    
    def __repr__(self) -> str:
        """Return a string representation of the requirement."""
        return f"Requirement(id={self.req_id}, type={self.req_type})"
    
    def to_tuple(self) -> tuple:
        """
        Convert the requirement to a tuple for database operations.
        
        Returns:
            Tuple containing (req_id, description, req_type)
        """
        return (self.req_id, self.description, self.req_type)
