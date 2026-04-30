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
import contextlib
from typing import List, Tuple, Optional


class Database:
    """
    Database access class for SQLite operations.
    
    This class manages the SQLite database connection and provides
    methods for all database operations in the RTM Tool.
    
    Attributes:
        db_path (str): Path to the SQLite database file
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the database connection and create tables if needed.
        
        Args:
            db_path: Path to the SQLite database file
        """
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(base_dir, "rtm_database.db")
        else:
            self.db_path = db_path
        self._create_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Create and return a new database connection with foreign keys enabled.
        
        Returns:
            SQLite connection object with foreign keys enabled
        """
        conn = sqlite3.connect(self.db_path)
        # Enable foreign key support
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @contextlib.contextmanager
    def _connection(self):
        """Context manager for database connections."""
        conn = self._get_connection()
        try:
            with conn:
                yield conn
        finally:
            conn.close()
    
    def _create_tables(self) -> None:
        """
        Create all required database tables if they don't exist.
        """
        with self._connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS requirements (
                    req_id TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    req_type TEXT NOT NULL CHECK(req_type IN ('Functional', 'Non-Functional'))
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS design_modules (
                    module_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_cases (
                    test_id TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    expected_result TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS requirement_design_map (
                    req_id TEXT NOT NULL,
                    module_id TEXT NOT NULL,
                    PRIMARY KEY (req_id, module_id),
                    FOREIGN KEY (req_id) REFERENCES requirements(req_id) ON DELETE CASCADE,
                    FOREIGN KEY (module_id) REFERENCES design_modules(module_id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS requirement_testcase_map (
                    req_id TEXT NOT NULL,
                    test_id TEXT NOT NULL,
                    PRIMARY KEY (req_id, test_id),
                    FOREIGN KEY (req_id) REFERENCES requirements(req_id) ON DELETE CASCADE,
                    FOREIGN KEY (test_id) REFERENCES test_cases(test_id) ON DELETE CASCADE
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS requirement_dependencies (
                    parent_id TEXT NOT NULL,
                    child_id TEXT NOT NULL,
                    PRIMARY KEY (parent_id, child_id),
                    FOREIGN KEY (parent_id) REFERENCES requirements(req_id) ON DELETE CASCADE,
                    FOREIGN KEY (child_id) REFERENCES requirements(req_id) ON DELETE CASCADE
                )
            ''')
    
    # ==================== REQUIREMENT OPERATIONS ====================
    
    def add_requirement(self, req_id: str, description: str, req_type: str) -> bool:
        """
        Add a new requirement to the database.
        """
        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO requirements (req_id, description, req_type) VALUES (?, ?, ?)",
                    (req_id, description, req_type)
                )
            return True
        except sqlite3.IntegrityError as e:
            msg = str(e)
            if "UNIQUE constraint failed" in msg:
                return "duplicate"
            elif "FOREIGN KEY constraint failed" in msg:
                return "foreign_key"
            else:
                return f"constraint:{msg}"
    
    def get_all_requirements(self) -> List[Tuple[str, str, str]]:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT req_id, description, req_type FROM requirements ORDER BY req_id")
            return cursor.fetchall()
    
    def requirement_exists(self, req_id: str) -> bool:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM requirements WHERE req_id = ?", (req_id,))
            return cursor.fetchone() is not None
    
    # ==================== DESIGN MODULE OPERATIONS ====================
    
    def add_design_module(self, module_id: str, name: str, description: str) -> bool:
        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO design_modules (module_id, name, description) VALUES (?, ?, ?)",
                    (module_id, name, description)
                )
            return True
        except sqlite3.IntegrityError as e:
            msg = str(e)
            if "UNIQUE constraint failed" in msg:
                return "duplicate"
            elif "FOREIGN KEY constraint failed" in msg:
                return "foreign_key"
            else:
                return f"constraint:{msg}"
    
    def get_all_design_modules(self) -> List[Tuple[str, str, str]]:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT module_id, name, description FROM design_modules ORDER BY module_id")
            return cursor.fetchall()
    
    def design_module_exists(self, module_id: str) -> bool:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM design_modules WHERE module_id = ?", (module_id,))
            return cursor.fetchone() is not None
    
    # ==================== TEST CASE OPERATIONS ====================
    
    def add_test_case(self, test_id: str, description: str, expected_result: str) -> bool:
        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO test_cases (test_id, description, expected_result) VALUES (?, ?, ?)",
                    (test_id, description, expected_result)
                )
            return True
        except sqlite3.IntegrityError as e:
            msg = str(e)
            if "UNIQUE constraint failed" in msg:
                return "duplicate"
            elif "FOREIGN KEY constraint failed" in msg:
                return "foreign_key"
            else:
                return f"constraint:{msg}"
    
    def get_all_test_cases(self) -> List[Tuple[str, str, str]]:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT test_id, description, expected_result FROM test_cases ORDER BY test_id")
            return cursor.fetchall()
    
    def test_case_exists(self, test_id: str) -> bool:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM test_cases WHERE test_id = ?", (test_id,))
            return cursor.fetchone() is not None
    
    # ==================== MAPPING OPERATIONS ====================
    
    def add_requirement_design_mapping(self, req_id: str, module_id: str) -> bool:
        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO requirement_design_map (req_id, module_id) VALUES (?, ?)",
                    (req_id, module_id)
                )
            return True
        except sqlite3.IntegrityError as e:
            msg = str(e)
            if "UNIQUE constraint failed" in msg:
                return "duplicate"
            elif "FOREIGN KEY constraint failed" in msg:
                return "foreign_key"
            else:
                return f"constraint:{msg}"
    
    def add_requirement_testcase_mapping(self, req_id: str, test_id: str) -> bool:
        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO requirement_testcase_map (req_id, test_id) VALUES (?, ?)",
                    (req_id, test_id)
                )
            return True
        except sqlite3.IntegrityError as e:
            msg = str(e)
            if "UNIQUE constraint failed" in msg:
                return "duplicate"
            elif "FOREIGN KEY constraint failed" in msg:
                return "foreign_key"
            else:
                return f"constraint:{msg}"
    
    def get_design_modules_for_requirement(self, req_id: str) -> List[str]:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT module_id FROM requirement_design_map WHERE req_id = ? ORDER BY module_id",
                (req_id,)
            )
            return [row[0] for row in cursor.fetchall()]
    
    def get_test_cases_for_requirement(self, req_id: str) -> List[str]:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT test_id FROM requirement_testcase_map WHERE req_id = ? ORDER BY test_id",
                (req_id,)
            )
            return [row[0] for row in cursor.fetchall()]
    
    def get_traceability_matrix_data(self) -> List[Tuple[str, str, str, str, str]]:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT
                    r.req_id,
                    r.description,
                    r.req_type,
                    COALESCE(mods.modules, '') as modules,
                    COALESCE(tests.tests, '') as tests
                FROM requirements r
                LEFT JOIN (
                    SELECT req_id, GROUP_CONCAT(module_id) as modules
                    FROM requirement_design_map
                    GROUP BY req_id
                ) mods ON r.req_id = mods.req_id
                LEFT JOIN (
                    SELECT req_id, GROUP_CONCAT(test_id) as tests
                    FROM requirement_testcase_map
                    GROUP BY req_id
                ) tests ON r.req_id = tests.req_id
                ORDER BY r.req_id
            ''')
            return cursor.fetchall()

    def get_all_requirement_dependencies(self) -> List[Tuple[str, str]]:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT parent_id, child_id FROM requirement_dependencies")
            return cursor.fetchall()

    def get_requirement_design_mappings(self, req_ids: List[str]) -> dict:
        if not req_ids:
            return {}
        placeholders = ','.join('?' for _ in req_ids)
        query = f"SELECT req_id, module_id FROM requirement_design_map WHERE req_id IN ({placeholders}) ORDER BY req_id, module_id"
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(req_ids))
            rows = cursor.fetchall()

        mapping = {}
        for req_id, module_id in rows:
            mapping.setdefault(req_id, []).append(module_id)
        return mapping

    def get_requirement_testcase_mappings(self, req_ids: List[str]) -> dict:
        if not req_ids:
            return {}
        placeholders = ','.join('?' for _ in req_ids)
        query = f"SELECT req_id, test_id FROM requirement_testcase_map WHERE req_id IN ({placeholders}) ORDER BY req_id, test_id"
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(req_ids))
            rows = cursor.fetchall()

        mapping = {}
        for req_id, test_id in rows:
            mapping.setdefault(req_id, []).append(test_id)
        return mapping
    
    # ==================== DEPENDENCY OPERATIONS ====================
    
    def add_requirement_dependency(self, parent_id: str, child_id: str) -> bool:
        if parent_id == child_id:
            return False # Cannot depend on itself
            
        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO requirement_dependencies (parent_id, child_id) VALUES (?, ?)",
                    (parent_id, child_id)
                )
            return True
        except sqlite3.IntegrityError as e:
            msg = str(e)
            if "UNIQUE constraint failed" in msg:
                return "duplicate"
            elif "FOREIGN KEY constraint failed" in msg:
                return "foreign_key"
            else:
                return f"constraint:{msg}"

    def get_dependencies_for_requirement(self, req_id: str) -> List[str]:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT parent_id FROM requirement_dependencies WHERE child_id = ?",
                (req_id,)
            )
            return [row[0] for row in cursor.fetchall()]

    def get_dependents_for_requirement(self, req_id: str) -> List[str]:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT child_id FROM requirement_dependencies WHERE parent_id = ?",
                (req_id,)
            )
            return [row[0] for row in cursor.fetchall()]

    def get_consistency_issues(self) -> List[Tuple[str, str, str]]:
        """
        Detects traceability gaps using a single efficient SQL query.
        
        Returns:
            List of tuples: (issue_type, entity_id, message)
        """
        query = """
            -- 1. Requirements without design
            SELECT 'NO_DESIGN' as type, req_id as id, 'No design module linked' as message
            FROM requirements
            WHERE req_id NOT IN (SELECT req_id FROM requirement_design_map)

            UNION ALL

            -- 2. Requirements without test cases
            SELECT 'NO_TEST' as type, req_id as id, 'No test case linked' as message
            FROM requirements
            WHERE req_id NOT IN (SELECT req_id FROM requirement_testcase_map)

            UNION ALL

            -- 3. Orphan test cases
            SELECT 'ORPHAN_TEST' as type, test_id as id, 'Not linked to any requirement' as message
            FROM test_cases
            WHERE test_id NOT IN (SELECT test_id FROM requirement_testcase_map)

            UNION ALL

            -- 4. Orphan design modules
            SELECT 'ORPHAN_DESIGN' as type, module_id as id, 'Not linked to any requirement' as message
            FROM design_modules
            WHERE module_id NOT IN (SELECT module_id FROM requirement_design_map)
        """
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()

    def clear_all_data(self) -> None:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM requirement_dependencies")
            cursor.execute("DELETE FROM requirement_testcase_map")
            cursor.execute("DELETE FROM requirement_design_map")
            cursor.execute("DELETE FROM test_cases")
            cursor.execute("DELETE FROM design_modules")
            cursor.execute("DELETE FROM requirements")
