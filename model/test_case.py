"""
Test Case Model Module

This module defines the TestCase data class that represents
a test case in the traceability system.
"""


from dataclasses import dataclass

@dataclass
class TestCase:
    """
    Represents a test case.
    
    Attributes:
        test_id (str): Unique identifier for the test case (e.g., 'TC-001')
        description (str): Description of what the test case verifies
        expected_result (str): The expected outcome when the test passes
    """
    test_id: str
    description: str
    expected_result: str
    
    def to_tuple(self) -> tuple:
        """
        Convert the test case to a tuple for database operations.
        
        Returns:
            Tuple containing (test_id, description, expected_result)
        """
        return (self.test_id, self.description, self.expected_result)
