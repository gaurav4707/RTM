"""
Requirement Model Module

This module defines the Requirement data class that represents
a software requirement in the traceability system.
"""


from dataclasses import dataclass

@dataclass
class Requirement:
    """
    Represents a software requirement.
    
    Attributes:
        req_id (str): Unique identifier for the requirement (e.g., 'REQ-001')
        description (str): Detailed description of the requirement
        req_type (str): Type of requirement - 'Functional' or 'Non-Functional'
    """
    req_id: str
    description: str
    req_type: str
    
    def to_tuple(self) -> tuple:
        """
        Convert the requirement to a tuple for database operations.
        
        Returns:
            Tuple containing (req_id, description, req_type)
        """
        return (self.req_id, self.description, self.req_type)
