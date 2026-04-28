"""
Unit Tests for the Requirement Traceability Matrix Tool

This module contains unit tests for testing the core functionality
of the RTM Tool including:
- Adding requirements
- Preventing duplicate IDs
- Creating trace links
- Generating RTM data

To run tests: python -m pytest tests/test_traceability.py
Or: python -m unittest tests.test_traceability

TEST ISOLATION NOTE:
--------------------
These tests use a SEPARATE test database file (test_rtm_database.db)
to ensure tests do NOT affect the production database (rtm_database.db).
Each test:
  1. Creates a fresh test database in setUp()
  2. Clears all data before running
  3. Deletes the test database in tearDown()

This ensures tests are isolated and repeatable.
"""

import unittest
import os
import sys
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from service.trace_service import TraceService
from data.database import Database


class TestRequirements(unittest.TestCase):
    """
    Test cases for requirement operations.
    
    Tests verify that the service layer correctly:
    - Adds valid requirements
    - Rejects duplicate IDs
    - Validates empty fields
    - Strips whitespace from inputs
    """
    
    def setUp(self):
        """
        Set up test fixtures - create a fresh database for each test.
        
        IMPORTANT: Uses a temporary directory to ensure complete isolation
        from the production database. This prevents any test from
        accidentally modifying real data.
        """
        # Create test database in temp directory for complete isolation
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_rtm_database.db")
        self.service = TraceService(db_path=self.test_db_path)
        # Clear any existing data (fresh start for each test)
        self.service.db.clear_all_data()
    
    def tearDown(self):
        """
        Clean up after each test.
        
        Removes the test database file to ensure no test artifacts remain.
        """
        # Remove test database file
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        # Remove temp directory
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_add_requirement_success(self):
        """Test successfully adding a new requirement."""
        success, message = self.service.add_requirement(
            "REQ-001", 
            "System shall allow user login", 
            "Functional"
        )
        self.assertTrue(success)
        self.assertEqual(message, "Requirement added successfully")
        
        # Verify it was added
        requirements = self.service.get_all_requirements()
        self.assertEqual(len(requirements), 1)
        self.assertEqual(requirements[0][0], "REQ-001")
    
    def test_add_requirement_duplicate_id(self):
        """Test that duplicate requirement IDs are rejected."""
        # Add first requirement
        self.service.add_requirement("REQ-001", "First requirement", "Functional")
        
        # Try to add another with same ID
        success, message = self.service.add_requirement(
            "REQ-001", 
            "Different description", 
            "Non-Functional"
        )
        self.assertFalse(success)
        self.assertIn("already exists", message)
    
    def test_add_requirement_empty_id(self):
        """Test that empty requirement ID is rejected."""
        success, message = self.service.add_requirement(
            "", 
            "Some description", 
            "Functional"
        )
        self.assertFalse(success)
        self.assertIn("cannot be empty", message)
    
    def test_add_requirement_empty_description(self):
        """Test that empty description is rejected."""
        success, message = self.service.add_requirement(
            "REQ-001", 
            "   ", 
            "Functional"
        )
        self.assertFalse(success)
        self.assertIn("cannot be empty", message)
    
    def test_add_requirement_whitespace_stripped(self):
        """Test that whitespace is stripped from inputs."""
        success, _ = self.service.add_requirement(
            "  REQ-001  ", 
            "  Description  ", 
            "Functional"
        )
        self.assertTrue(success)
        
        requirements = self.service.get_all_requirements()
        # Verify whitespace was stripped
        self.assertEqual(requirements[0][0], "REQ-001")
        self.assertEqual(requirements[0][1], "Description")


class TestDesignModules(unittest.TestCase):
    """Test cases for design module operations."""
    
    def setUp(self):
        """Set up test fixtures with isolated temp database."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_rtm_database.db")
        self.service = TraceService(db_path=self.test_db_path)
        self.service.db.clear_all_data()
    
    def tearDown(self):
        """Clean up test database and temp directory."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_add_design_module_success(self):
        """Test successfully adding a new design module."""
        success, message = self.service.add_design_module(
            "DM-001", 
            "Authentication Module", 
            "Handles user authentication"
        )
        self.assertTrue(success)
        
        modules = self.service.get_all_design_modules()
        self.assertEqual(len(modules), 1)
        self.assertEqual(modules[0][0], "DM-001")
    
    def test_add_design_module_duplicate_id(self):
        """Test that duplicate module IDs are rejected."""
        self.service.add_design_module("DM-001", "First Module", "Description")
        
        success, message = self.service.add_design_module(
            "DM-001", 
            "Another Module", 
            "Different description"
        )
        self.assertFalse(success)
        self.assertIn("already exists", message)


class TestTestCases(unittest.TestCase):
    """Test cases for test case operations."""
    
    def setUp(self):
        """Set up test fixtures with isolated temp database."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_rtm_database.db")
        self.service = TraceService(db_path=self.test_db_path)
        self.service.db.clear_all_data()
    
    def tearDown(self):
        """Clean up test database and temp directory."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_add_test_case_success(self):
        """Test successfully adding a new test case."""
        success, message = self.service.add_test_case(
            "TC-001", 
            "Test user login with valid credentials", 
            "User is logged in successfully"
        )
        self.assertTrue(success)
        
        test_cases = self.service.get_all_test_cases()
        self.assertEqual(len(test_cases), 1)
        self.assertEqual(test_cases[0][0], "TC-001")
    
    def test_add_test_case_duplicate_id(self):
        """Test that duplicate test case IDs are rejected."""
        self.service.add_test_case("TC-001", "First test", "Expected result")
        
        success, message = self.service.add_test_case(
            "TC-001", 
            "Another test", 
            "Different result"
        )
        self.assertFalse(success)
        self.assertIn("already exists", message)


class TestTraceLinks(unittest.TestCase):
    """
    Test cases for traceability link operations.
    
    These tests verify the core traceability functionality:
    - Linking requirements to design modules
    - Linking requirements to test cases
    - Preventing duplicate links
    - Validating existence before linking
    """
    
    def setUp(self):
        """
        Set up test fixtures with sample data.
        
        Creates a test database pre-populated with:
        - 2 requirements (REQ-001, REQ-002)
        - 1 design module (DM-001)
        - 1 test case (TC-001)
        """
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_rtm_database.db")
        self.service = TraceService(db_path=self.test_db_path)
        self.service.db.clear_all_data()
        
        # Add sample data for testing trace links
        self.service.add_requirement("REQ-001", "User login", "Functional")
        self.service.add_requirement("REQ-002", "User logout", "Functional")
        self.service.add_design_module("DM-001", "Auth Module", "Authentication")
        self.service.add_test_case("TC-001", "Login test", "Success")
    
    def tearDown(self):
        """Clean up test database and temp directory."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_link_requirement_to_design_success(self):
        """Test successfully linking a requirement to a design module."""
        success, message = self.service.link_requirement_to_design("REQ-001", "DM-001")
        self.assertTrue(success)
    
    def test_link_requirement_to_design_duplicate(self):
        """Test that duplicate links are rejected."""
        self.service.link_requirement_to_design("REQ-001", "DM-001")
        
        success, message = self.service.link_requirement_to_design("REQ-001", "DM-001")
        self.assertFalse(success)
        self.assertIn("already exists", message)
    
    def test_link_requirement_to_design_nonexistent_req(self):
        """Test linking with nonexistent requirement fails."""
        success, message = self.service.link_requirement_to_design("REQ-999", "DM-001")
        self.assertFalse(success)
        self.assertIn("does not exist", message)
    
    def test_link_requirement_to_design_nonexistent_module(self):
        """Test linking with nonexistent design module fails."""
        success, message = self.service.link_requirement_to_design("REQ-001", "DM-999")
        self.assertFalse(success)
        self.assertIn("does not exist", message)
    
    def test_link_requirement_to_test_success(self):
        """Test successfully linking a requirement to a test case."""
        success, message = self.service.link_requirement_to_test("REQ-001", "TC-001")
        self.assertTrue(success)
    
    def test_link_requirement_to_test_nonexistent(self):
        """Test linking with nonexistent entities fails."""
        success, message = self.service.link_requirement_to_test("REQ-999", "TC-001")
        self.assertFalse(success)


class TestTraceabilityMatrix(unittest.TestCase):
    """
    Test cases for RTM generation.
    
    These tests verify that the traceability matrix correctly shows
    all requirements with their linked design modules and test cases.
    """
    
    def setUp(self):
        """
        Set up test fixtures with sample data and links.
        
        Creates a complete traceability scenario:
        - REQ-001 -> DM-001, TC-001
        - REQ-002 -> DM-002, TC-002
        """
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_rtm_database.db")
        self.service = TraceService(db_path=self.test_db_path)
        self.service.db.clear_all_data()
        
        # Add sample requirements
        self.service.add_requirement("REQ-001", "User login", "Functional")
        self.service.add_requirement("REQ-002", "User logout", "Functional")
        
        # Add sample design modules
        self.service.add_design_module("DM-001", "Auth Module", "Authentication")
        self.service.add_design_module("DM-002", "Session Module", "Session management")
        
        # Add sample test cases
        self.service.add_test_case("TC-001", "Login test", "Success")
        self.service.add_test_case("TC-002", "Logout test", "Success")
        
        # Create trace links
        self.service.link_requirement_to_design("REQ-001", "DM-001")
        self.service.link_requirement_to_test("REQ-001", "TC-001")
        self.service.link_requirement_to_design("REQ-002", "DM-002")
        self.service.link_requirement_to_test("REQ-002", "TC-002")
    
    def tearDown(self):
        """Clean up test database and temp directory."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_get_traceability_matrix(self):
        """Test generating the traceability matrix."""
        rtm = self.service.get_traceability_matrix()
        
        # Should have 2 rows (one per requirement)
        self.assertEqual(len(rtm), 2)
        
        # Check first row
        self.assertEqual(rtm[0][0], "REQ-001")  # req_id
        self.assertEqual(rtm[0][3], "DM-001")   # linked modules
        self.assertEqual(rtm[0][4], "TC-001")   # linked tests
    
    def test_rtm_with_no_links(self):
        """Test RTM for requirements with no links."""
        # Clear links and add new requirement
        self.service.db.clear_all_data()
        self.service.add_requirement("REQ-003", "Orphan requirement", "Functional")
        
        rtm = self.service.get_traceability_matrix()
        
        self.assertEqual(len(rtm), 1)
        self.assertEqual(rtm[0][3], "")  # No linked modules
        self.assertEqual(rtm[0][4], "")  # No linked tests
    
    def test_rtm_multiple_links(self):
        """Test RTM for requirement with multiple links."""
        # Add another link to REQ-001
        self.service.link_requirement_to_design("REQ-001", "DM-002")
        self.service.link_requirement_to_test("REQ-001", "TC-002")
        
        rtm = self.service.get_traceability_matrix()
        
        # Find REQ-001 row
        req_001_row = next(row for row in rtm if row[0] == "REQ-001")
        
        # Should have multiple modules and tests (comma-separated)
        self.assertIn("DM-001", req_001_row[3])
        self.assertIn("DM-002", req_001_row[3])
        self.assertIn("TC-001", req_001_row[4])
        self.assertIn("TC-002", req_001_row[4])


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
