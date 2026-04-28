"""
Trace Service Module (Business Logic Layer)

This module contains the business logic layer for the RTM Tool.
It acts as an intermediary between the UI layer and the data layer,
providing validation and orchestration of operations.

ARCHITECTURE NOTE:
------------------
This is the SERVICE LAYER (also called Business Logic Layer) in our 3-tier architecture:
  UI Layer -> Service Layer (this file) -> Data Layer

This layer is responsible for:
  - Input validation (empty checks, format validation)
  - Business rules (duplicate ID prevention, existence checks)
  - Coordinating between UI and database
  - Returning user-friendly success/error messages

The UI layer should NEVER directly access the database - it must go through this service.
"""

from typing import List, Tuple, Optional
import sys
import os

# Add parent directory to path for imports when running as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import Database
from model.requirement import Requirement
from model.design_module import DesignModule
from model.test_case import TestCase


class TraceService:
    """
    Business logic service for traceability operations.
    
    This class provides methods for managing requirements, design modules,
    test cases, and their trace relationships. It includes input validation
    and error handling.
    
    Attributes:
        db (Database): Database access object
    """
    
    def __init__(self, db_path: str = "rtm_database.db"):
        """
        Initialize the trace service with a database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db = Database(db_path)
    
    # ==================== VALIDATION HELPERS ====================
    
    def _validate_not_empty(self, value: str, field_name: str) -> Tuple[bool, str]:
        """
        Validate that a string value is not empty or whitespace-only.
        
        Args:
            value: The string to validate
            field_name: Name of the field for error message
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value or not value.strip():
            return False, f"{field_name} cannot be empty"
        return True, ""
    
    # ==================== REQUIREMENT OPERATIONS ====================
    
    def add_requirement(self, req_id: str, description: str, req_type: str) -> Tuple[bool, str]:
        """
        Add a new requirement with validation.
        
        Args:
            req_id: Unique identifier for the requirement
            description: Description of the requirement
            req_type: Type ('Functional' or 'Non-Functional')
            
        Returns:
            Tuple of (success, message) where message contains error details if failed
        """
        # Validate all fields are not empty
        valid, error = self._validate_not_empty(req_id, "Requirement ID")
        if not valid:
            return False, error
        
        valid, error = self._validate_not_empty(description, "Description")
        if not valid:
            return False, error
        
        # Validate requirement type
        if req_type not in ['Functional', 'Non-Functional']:
            return False, "Type must be 'Functional' or 'Non-Functional'"
        
        # Clean the input (strip whitespace)
        req_id = req_id.strip()
        description = description.strip()
        
        # Attempt to add to database
        if self.db.add_requirement(req_id, description, req_type):
            return True, "Requirement added successfully"
        else:
            return False, f"Requirement ID '{req_id}' already exists"
    
    def get_all_requirements(self) -> List[Tuple[str, str, str]]:
        """
        Get all requirements from the database.
        
        Returns:
            List of tuples containing (req_id, description, req_type)
        """
        return self.db.get_all_requirements()
    
    def get_requirement_ids(self) -> List[str]:
        """
        Get a list of all requirement IDs.
        
        Returns:
            List of requirement ID strings
        """
        requirements = self.db.get_all_requirements()
        return [req[0] for req in requirements]
    
    # ==================== DESIGN MODULE OPERATIONS ====================
    
    def add_design_module(self, module_id: str, name: str, description: str) -> Tuple[bool, str]:
        """
        Add a new design module with validation.
        
        Args:
            module_id: Unique identifier for the module
            name: Name of the module
            description: Description of the module
            
        Returns:
            Tuple of (success, message) where message contains error details if failed
        """
        # Validate all fields are not empty
        valid, error = self._validate_not_empty(module_id, "Module ID")
        if not valid:
            return False, error
        
        valid, error = self._validate_not_empty(name, "Module Name")
        if not valid:
            return False, error
        
        valid, error = self._validate_not_empty(description, "Description")
        if not valid:
            return False, error
        
        # Clean the input
        module_id = module_id.strip()
        name = name.strip()
        description = description.strip()
        
        # Attempt to add to database
        if self.db.add_design_module(module_id, name, description):
            return True, "Design module added successfully"
        else:
            return False, f"Module ID '{module_id}' already exists"
    
    def get_all_design_modules(self) -> List[Tuple[str, str, str]]:
        """
        Get all design modules from the database.
        
        Returns:
            List of tuples containing (module_id, name, description)
        """
        return self.db.get_all_design_modules()
    
    def get_design_module_ids(self) -> List[str]:
        """
        Get a list of all design module IDs.
        
        Returns:
            List of module ID strings
        """
        modules = self.db.get_all_design_modules()
        return [mod[0] for mod in modules]
    
    # ==================== TEST CASE OPERATIONS ====================
    
    def add_test_case(self, test_id: str, description: str, expected_result: str) -> Tuple[bool, str]:
        """
        Add a new test case with validation.
        
        Args:
            test_id: Unique identifier for the test case
            description: Description of the test
            expected_result: Expected result of the test
            
        Returns:
            Tuple of (success, message) where message contains error details if failed
        """
        # Validate all fields are not empty
        valid, error = self._validate_not_empty(test_id, "Test ID")
        if not valid:
            return False, error
        
        valid, error = self._validate_not_empty(description, "Description")
        if not valid:
            return False, error
        
        valid, error = self._validate_not_empty(expected_result, "Expected Result")
        if not valid:
            return False, error
        
        # Clean the input
        test_id = test_id.strip()
        description = description.strip()
        expected_result = expected_result.strip()
        
        # Attempt to add to database
        if self.db.add_test_case(test_id, description, expected_result):
            return True, "Test case added successfully"
        else:
            return False, f"Test ID '{test_id}' already exists"
    
    def get_all_test_cases(self) -> List[Tuple[str, str, str]]:
        """
        Get all test cases from the database.
        
        Returns:
            List of tuples containing (test_id, description, expected_result)
        """
        return self.db.get_all_test_cases()
    
    def get_test_case_ids(self) -> List[str]:
        """
        Get a list of all test case IDs.
        
        Returns:
            List of test case ID strings
        """
        test_cases = self.db.get_all_test_cases()
        return [tc[0] for tc in test_cases]
    
    # ==================== MAPPING OPERATIONS ====================
    
    def link_requirement_to_design(self, req_id: str, module_id: str) -> Tuple[bool, str]:
        """
        Create a trace link between a requirement and a design module.
        
        Args:
            req_id: The requirement ID
            module_id: The design module ID
            
        Returns:
            Tuple of (success, message)
        """
        # Validate inputs
        valid, error = self._validate_not_empty(req_id, "Requirement ID")
        if not valid:
            return False, error
        
        valid, error = self._validate_not_empty(module_id, "Module ID")
        if not valid:
            return False, error
        
        # Check if requirement exists
        if not self.db.requirement_exists(req_id):
            return False, f"Requirement '{req_id}' does not exist"
        
        # Check if design module exists
        if not self.db.design_module_exists(module_id):
            return False, f"Design Module '{module_id}' does not exist"
        
        # Create the mapping
        if self.db.add_requirement_design_mapping(req_id, module_id):
            return True, f"Linked {req_id} to {module_id}"
        else:
            return False, "This mapping already exists"
    
    def link_requirement_to_test(self, req_id: str, test_id: str) -> Tuple[bool, str]:
        """
        Create a trace link between a requirement and a test case.
        
        Args:
            req_id: The requirement ID
            test_id: The test case ID
            
        Returns:
            Tuple of (success, message)
        """
        # Validate inputs
        valid, error = self._validate_not_empty(req_id, "Requirement ID")
        if not valid:
            return False, error
        
        valid, error = self._validate_not_empty(test_id, "Test ID")
        if not valid:
            return False, error
        
        # Check if requirement exists
        if not self.db.requirement_exists(req_id):
            return False, f"Requirement '{req_id}' does not exist"
        
        # Check if test case exists
        if not self.db.test_case_exists(test_id):
            return False, f"Test Case '{test_id}' does not exist"
        
        # Create the mapping
        if self.db.add_requirement_testcase_mapping(req_id, test_id):
            return True, f"Linked {req_id} to {test_id}"
        else:
            return False, "This mapping already exists"
    
    # ==================== TRACEABILITY MATRIX ====================
    
    def get_traceability_matrix(self) -> List[Tuple[str, str, str, str, str]]:
        """
        Get the complete traceability matrix data.
        
        Returns:
            List of tuples containing:
            (req_id, description, type, linked_modules, linked_tests)
        """
        return self.db.get_traceability_matrix_data()
