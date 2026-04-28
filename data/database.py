"""
Database Access Module (Data Layer)

This module handles all SQLite database operations for the RTM Tool.
It provides functions for CRUD operations on requirements, design modules,
test cases, and their mappings.

ARCHITECTURE NOTE:
------------------
This is the DATA LAYER in our 3-tier architecture:
  UI Layer -> Service Layer -> Data Layer (this file)

This layer is responsible ONLY for:
  - Database connections
  - SQL queries (CRUD operations)
  - Returning raw data to the service layer

It does NOT perform business logic or validation - that belongs in the service layer.
"""

import sqlite3
import os
from typing import List, Tuple, Optional


class Database:
    """
    Database access class for SQLite operations.
    
    This class manages the SQLite database connection and provides
    methods for all database operations in the RTM Tool.
    
    Attributes:
        db_path (str): Path to the SQLite database file
    """
    
    def __init__(self, db_path: str = "rtm_database.db"):
        """
        Initialize the database connection and create tables if needed.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._create_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Create and return a new database connection.
        
        Returns:
            SQLite connection object with foreign keys enabled
        """
        conn = sqlite3.connect(self.db_path)
        # Enable foreign key support
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def _create_tables(self) -> None:
        """
        Create all required database tables if they don't exist.
        
        Tables created:
        - requirements: Stores software requirements
        - design_modules: Stores design modules
        - test_cases: Stores test cases
        - requirement_design_map: Maps requirements to design modules
        - requirement_testcase_map: Maps requirements to test cases
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # ============================================================
        # TABLE: requirements
        # PURPOSE: Stores software requirements (functional & non-functional)
        # PRIMARY KEY: req_id - unique identifier like 'REQ-001'
        # ============================================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requirements (
                req_id TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                req_type TEXT NOT NULL CHECK(req_type IN ('Functional', 'Non-Functional'))
            )
        ''')
        
        # ============================================================
        # TABLE: design_modules
        # PURPOSE: Stores design/architecture modules that implement requirements
        # PRIMARY KEY: module_id - unique identifier like 'DM-001'
        # ============================================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS design_modules (
                module_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL
            )
        ''')
        
        # ============================================================
        # TABLE: test_cases
        # PURPOSE: Stores test cases that verify requirements
        # PRIMARY KEY: test_id - unique identifier like 'TC-001'
        # ============================================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_cases (
                test_id TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                expected_result TEXT NOT NULL
            )
        ''')
        
        # ============================================================
        # TABLE: requirement_design_map (Junction/Bridge Table)
        # PURPOSE: Creates many-to-many relationship between requirements
        #          and design modules (one requirement can map to multiple
        #          modules, and one module can satisfy multiple requirements)
        # FOREIGN KEYS: Enforce referential integrity - cannot link to
        #               non-existent requirements or modules
        # ON DELETE CASCADE: If a requirement/module is deleted, its
        #                    mappings are automatically removed
        # ============================================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requirement_design_map (
                req_id TEXT NOT NULL,
                module_id TEXT NOT NULL,
                PRIMARY KEY (req_id, module_id),
                FOREIGN KEY (req_id) REFERENCES requirements(req_id) ON DELETE CASCADE,
                FOREIGN KEY (module_id) REFERENCES design_modules(module_id) ON DELETE CASCADE
            )
        ''')
        
        # ============================================================
        # TABLE: requirement_testcase_map (Junction/Bridge Table)
        # PURPOSE: Creates many-to-many relationship between requirements
        #          and test cases (traceability from requirements to tests)
        # FOREIGN KEYS: Enforce referential integrity
        # ON DELETE CASCADE: Automatic cleanup of orphaned mappings
        # ============================================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requirement_testcase_map (
                req_id TEXT NOT NULL,
                test_id TEXT NOT NULL,
                PRIMARY KEY (req_id, test_id),
                FOREIGN KEY (req_id) REFERENCES requirements(req_id) ON DELETE CASCADE,
                FOREIGN KEY (test_id) REFERENCES test_cases(test_id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ==================== REQUIREMENT OPERATIONS ====================
    
    def add_requirement(self, req_id: str, description: str, req_type: str) -> bool:
        """
        Add a new requirement to the database.
        
        Args:
            req_id: Unique identifier for the requirement
            description: Description of the requirement
            req_type: Type ('Functional' or 'Non-Functional')
            
        Returns:
            True if successful, False if requirement ID already exists
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO requirements (req_id, description, req_type) VALUES (?, ?, ?)",
                (req_id, description, req_type)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Duplicate ID - requirement already exists
            return False
        finally:
            conn.close()
    
    def get_all_requirements(self) -> List[Tuple[str, str, str]]:
        """
        Retrieve all requirements from the database.
        
        Returns:
            List of tuples containing (req_id, description, req_type)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT req_id, description, req_type FROM requirements ORDER BY req_id")
        results = cursor.fetchall()
        conn.close()
        return results
    
    def requirement_exists(self, req_id: str) -> bool:
        """
        Check if a requirement with the given ID exists.
        
        Args:
            req_id: The requirement ID to check
            
        Returns:
            True if exists, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM requirements WHERE req_id = ?", (req_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    # ==================== DESIGN MODULE OPERATIONS ====================
    
    def add_design_module(self, module_id: str, name: str, description: str) -> bool:
        """
        Add a new design module to the database.
        
        Args:
            module_id: Unique identifier for the module
            name: Name of the module
            description: Description of the module
            
        Returns:
            True if successful, False if module ID already exists
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO design_modules (module_id, name, description) VALUES (?, ?, ?)",
                (module_id, name, description)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_all_design_modules(self) -> List[Tuple[str, str, str]]:
        """
        Retrieve all design modules from the database.
        
        Returns:
            List of tuples containing (module_id, name, description)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT module_id, name, description FROM design_modules ORDER BY module_id")
        results = cursor.fetchall()
        conn.close()
        return results
    
    def design_module_exists(self, module_id: str) -> bool:
        """
        Check if a design module with the given ID exists.
        
        Args:
            module_id: The module ID to check
            
        Returns:
            True if exists, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM design_modules WHERE module_id = ?", (module_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    # ==================== TEST CASE OPERATIONS ====================
    
    def add_test_case(self, test_id: str, description: str, expected_result: str) -> bool:
        """
        Add a new test case to the database.
        
        Args:
            test_id: Unique identifier for the test case
            description: Description of the test
            expected_result: Expected result of the test
            
        Returns:
            True if successful, False if test ID already exists
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO test_cases (test_id, description, expected_result) VALUES (?, ?, ?)",
                (test_id, description, expected_result)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_all_test_cases(self) -> List[Tuple[str, str, str]]:
        """
        Retrieve all test cases from the database.
        
        Returns:
            List of tuples containing (test_id, description, expected_result)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT test_id, description, expected_result FROM test_cases ORDER BY test_id")
        results = cursor.fetchall()
        conn.close()
        return results
    
    def test_case_exists(self, test_id: str) -> bool:
        """
        Check if a test case with the given ID exists.
        
        Args:
            test_id: The test case ID to check
            
        Returns:
            True if exists, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM test_cases WHERE test_id = ?", (test_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    # ==================== MAPPING OPERATIONS ====================
    
    def add_requirement_design_mapping(self, req_id: str, module_id: str) -> bool:
        """
        Create a mapping between a requirement and a design module.
        
        Args:
            req_id: The requirement ID
            module_id: The design module ID
            
        Returns:
            True if successful, False if mapping already exists
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO requirement_design_map (req_id, module_id) VALUES (?, ?)",
                (req_id, module_id)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def add_requirement_testcase_mapping(self, req_id: str, test_id: str) -> bool:
        """
        Create a mapping between a requirement and a test case.
        
        Args:
            req_id: The requirement ID
            test_id: The test case ID
            
        Returns:
            True if successful, False if mapping already exists
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO requirement_testcase_map (req_id, test_id) VALUES (?, ?)",
                (req_id, test_id)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_design_modules_for_requirement(self, req_id: str) -> List[str]:
        """
        Get all design module IDs mapped to a requirement.
        
        Args:
            req_id: The requirement ID
            
        Returns:
            List of design module IDs
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT module_id FROM requirement_design_map WHERE req_id = ? ORDER BY module_id",
            (req_id,)
        )
        results = [row[0] for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_test_cases_for_requirement(self, req_id: str) -> List[str]:
        """
        Get all test case IDs mapped to a requirement.
        
        Args:
            req_id: The requirement ID
            
        Returns:
            List of test case IDs
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT test_id FROM requirement_testcase_map WHERE req_id = ? ORDER BY test_id",
            (req_id,)
        )
        results = [row[0] for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_traceability_matrix_data(self) -> List[Tuple[str, str, str, str, str]]:
        """
        Get complete traceability matrix data.
        
        Returns:
            List of tuples containing:
            (req_id, req_description, req_type, linked_modules, linked_tests)
            where linked_modules and linked_tests are comma-separated strings
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get all requirements with their linked modules and test cases
        cursor.execute('''
            SELECT 
                r.req_id,
                r.description,
                r.req_type,
                COALESCE(GROUP_CONCAT(DISTINCT rdm.module_id), '') as modules,
                COALESCE(GROUP_CONCAT(DISTINCT rtm.test_id), '') as tests
            FROM requirements r
            LEFT JOIN requirement_design_map rdm ON r.req_id = rdm.req_id
            LEFT JOIN requirement_testcase_map rtm ON r.req_id = rtm.req_id
            GROUP BY r.req_id, r.description, r.req_type
            ORDER BY r.req_id
        ''')
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def clear_all_data(self) -> None:
        """
        Clear all data from the database (used for testing).
        
        Warning: This deletes all records from all tables!
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM requirement_testcase_map")
        cursor.execute("DELETE FROM requirement_design_map")
        cursor.execute("DELETE FROM test_cases")
        cursor.execute("DELETE FROM design_modules")
        cursor.execute("DELETE FROM requirements")
        conn.commit()
        conn.close()
