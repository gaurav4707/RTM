import sqlite3
import os
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class DatabaseRepository:
    def __init__(self, db_path: str = "rtm_database.db"):
        self.db_path = db_path
        self._initialize_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _initialize_db(self):
        """Creates the database schema if it doesn't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Requirements table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS requirements (
                    id TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            ''')
            
            # Design Modules table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS design_modules (
                    id TEXT PRIMARY KEY,
                    description TEXT NOT NULL
                )
            ''')
            
            # Test Cases table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_cases (
                    id TEXT PRIMARY KEY,
                    description TEXT NOT NULL
                )
            ''')
            
            # Requirement to Design Module mapping
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS requirement_design (
                    req_id TEXT,
                    design_id TEXT,
                    PRIMARY KEY (req_id, design_id),
                    FOREIGN KEY (req_id) REFERENCES requirements (id) ON DELETE CASCADE,
                    FOREIGN KEY (design_id) REFERENCES design_modules (id) ON DELETE CASCADE
                )
            ''')
            
            # Requirement to Test Case mapping
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS requirement_test (
                    req_id TEXT,
                    test_id TEXT,
                    PRIMARY KEY (req_id, test_id),
                    FOREIGN KEY (req_id) REFERENCES requirements (id) ON DELETE CASCADE,
                    FOREIGN KEY (test_id) REFERENCES test_cases (id) ON DELETE CASCADE
                )
            ''')
            
            # Requirement Dependency mapping
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS requirement_dependency (
                    req_id TEXT,
                    depends_on_req_id TEXT,
                    PRIMARY KEY (req_id, depends_on_req_id),
                    FOREIGN KEY (req_id) REFERENCES requirements (id) ON DELETE CASCADE,
                    FOREIGN KEY (depends_on_req_id) REFERENCES requirements (id) ON DELETE CASCADE
                )
            ''')
            conn.commit()

    # --- Requirements CRUD ---
    
    def add_requirement(self, req_id: str, description: str, type: str, priority: str, status: str) -> Tuple[bool, str]:
        if not req_id or not description:
            return False, "Requirement ID and description are required."
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO requirements (id, description, type, priority, status) VALUES (?, ?, ?, ?, ?)",
                    (req_id, description, type, priority, status)
                )
            return True, "Requirement added successfully."
        except sqlite3.IntegrityError:
            return False, f"Requirement with ID {req_id} already exists."
        except Exception as e:
            return False, f"Error adding requirement: {e}"

    def get_requirement(self, req_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM requirements WHERE id = ?", (req_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
            
    def get_all_requirements(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM requirements")
            return [dict(row) for row in cursor.fetchall()]

    def update_requirement(self, req_id: str, description: str, type: str, priority: str, status: str) -> Tuple[bool, str]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE requirements SET description=?, type=?, priority=?, status=? WHERE id=?",
                    (description, type, priority, status, req_id)
                )
                if cursor.rowcount == 0:
                    return False, f"Requirement with ID {req_id} not found."
            return True, "Requirement updated successfully."
        except Exception as e:
            return False, f"Error updating requirement: {e}"

    def delete_requirement(self, req_id: str) -> Tuple[bool, str]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM requirements WHERE id=?", (req_id,))
                if cursor.rowcount == 0:
                    return False, f"Requirement with ID {req_id} not found."
            return True, "Requirement deleted successfully."
        except Exception as e:
            return False, f"Error deleting requirement: {e}"

    # --- Design Modules CRUD ---
    
    def add_design_module(self, design_id: str, description: str) -> Tuple[bool, str]:
        if not design_id or not description:
            return False, "Design Module ID and description are required."
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO design_modules (id, description) VALUES (?, ?)",
                    (design_id, description)
                )
            return True, "Design Module added successfully."
        except sqlite3.IntegrityError:
            return False, f"Design Module with ID {design_id} already exists."
        except Exception as e:
            return False, f"Error adding design module: {e}"

    def get_design_module(self, design_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM design_modules WHERE id = ?", (design_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_design_modules(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM design_modules")
            return [dict(row) for row in cursor.fetchall()]

    def delete_design_module(self, design_id: str) -> Tuple[bool, str]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM design_modules WHERE id=?", (design_id,))
                if cursor.rowcount == 0:
                    return False, f"Design Module with ID {design_id} not found."
            return True, "Design Module deleted successfully."
        except Exception as e:
            return False, f"Error deleting design module: {e}"

    # --- Test Cases CRUD ---
    
    def add_test_case(self, test_id: str, description: str) -> Tuple[bool, str]:
        if not test_id or not description:
            return False, "Test Case ID and description are required."
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO test_cases (id, description) VALUES (?, ?)",
                    (test_id, description)
                )
            return True, "Test Case added successfully."
        except sqlite3.IntegrityError:
            return False, f"Test Case with ID {test_id} already exists."
        except Exception as e:
            return False, f"Error adding test case: {e}"

    def get_test_case(self, test_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test_cases WHERE id = ?", (test_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_test_cases(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test_cases")
            return [dict(row) for row in cursor.fetchall()]

    def delete_test_case(self, test_id: str) -> Tuple[bool, str]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM test_cases WHERE id=?", (test_id,))
                if cursor.rowcount == 0:
                    return False, f"Test Case with ID {test_id} not found."
            return True, "Test Case deleted successfully."
        except Exception as e:
            return False, f"Error deleting test case: {e}"

    # --- Relationships (Links) ---
    
    def link_requirement_design(self, req_id: str, design_id: str) -> Tuple[bool, str]:
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO requirement_design (req_id, design_id) VALUES (?, ?)",
                    (req_id, design_id)
                )
            return True, "Successfully linked requirement to design module."
        except sqlite3.IntegrityError:
            return False, "Link already exists or invalid IDs provided."
        except Exception as e:
            return False, f"Error linking requirement and design module: {e}"

    def link_requirement_test(self, req_id: str, test_id: str) -> Tuple[bool, str]:
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO requirement_test (req_id, test_id) VALUES (?, ?)",
                    (req_id, test_id)
                )
            return True, "Successfully linked requirement to test case."
        except sqlite3.IntegrityError:
            return False, "Link already exists or invalid IDs provided."
        except Exception as e:
            return False, f"Error linking requirement and test case: {e}"

    def link_requirement_dependency(self, req_id: str, depends_on_req_id: str) -> Tuple[bool, str]:
        if req_id == depends_on_req_id:
            return False, "A requirement cannot depend on itself."
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO requirement_dependency (req_id, depends_on_req_id) VALUES (?, ?)",
                    (req_id, depends_on_req_id)
                )
            return True, "Successfully added requirement dependency."
        except sqlite3.IntegrityError:
            return False, "Dependency link already exists or invalid IDs provided."
        except Exception as e:
            return False, f"Error adding dependency link: {e}"

    def get_design_links_for_requirement(self, req_id: str) -> List[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT design_id FROM requirement_design WHERE req_id = ?", (req_id,))
            return [row['design_id'] for row in cursor.fetchall()]
            
    def get_test_links_for_requirement(self, req_id: str) -> List[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT test_id FROM requirement_test WHERE req_id = ?", (req_id,))
            return [row['test_id'] for row in cursor.fetchall()]

    def get_dependencies_for_requirement(self, req_id: str) -> List[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT depends_on_req_id FROM requirement_dependency WHERE req_id = ?", (req_id,))
            return [row['depends_on_req_id'] for row in cursor.fetchall()]
