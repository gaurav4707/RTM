"""
Test Case Model Module

This module defines the TestCase data class that represents
a test case in the traceability system.
"""


class TestCase:
    """
    Represents a test case.
    
    Attributes:
        test_id (str): Unique identifier for the test case (e.g., 'TC-001')
        description (str): Description of what the test case verifies
        expected_result (str): The expected outcome when the test passes
    """
    
    def __init__(self, test_id: str, description: str, expected_result: str):
        """
        Initialize a new TestCase instance.
        
        Args:
            test_id: Unique identifier for the test case
            description: Description of the test scenario
            expected_result: Expected outcome of the test
        """
        self.test_id = test_id
        self.description = description
        self.expected_result = expected_result
    
    def __repr__(self) -> str:
        """Return a string representation of the test case."""
        return f"TestCase(id={self.test_id})"
    
    def to_tuple(self) -> tuple:
        """
        Convert the test case to a tuple for database operations.
        
        Returns:
            Tuple containing (test_id, description, expected_result)
        """
        return (self.test_id, self.description, self.expected_result)
