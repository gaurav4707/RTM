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

from data.database import Database
from model.requirement import Requirement
from model.design_module import DesignModule
from model.test_case import TestCase
from service.analysis_engine import AnalysisEngine
from service.consistency_checker import ConsistencyChecker
from service.rule_engine import RuleEngine
from service.duplicate_detection import DuplicateDetector
from service.report_generator import ReportGenerator


class TraceService:


    def get_dashboard_metrics(self) -> dict:
        """
        Returns a dashboard metrics dictionary with:
          - coverage metrics
          - traceability breakdown
          - risk summary (counts of HIGH, MEDIUM, LOW)
        """
        # Coverage and breakdown
        coverage = self.get_traceability_coverage()

        # Risk summary: count HIGH, MEDIUM, LOW risk requirements
        risk_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        all_req_ids = self.get_requirement_ids()
        for req_id in all_req_ids:
            risk = self.get_full_impact_analysis(req_id)['risk']
            if risk in risk_counts:
                risk_counts[risk] += 1
            else:
                risk_counts[risk] = 1

        return {
            'coverage': coverage,
            'traceability_breakdown': {
                'fully_traced': coverage['fully_traced'],
                'partially_traced': coverage['partially_traced'],
                'untraced': coverage['untraced']
            },
            'risk_summary': risk_counts
        }

    def get_traceability_coverage(self) -> dict:
        """
        Compute traceability coverage statistics for requirements.
        Returns:
            dict with total, design_coverage, test_coverage, fully_traced, partially_traced, untraced
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        # All requirements
        cursor.execute("SELECT req_id FROM requirements")
        all_reqs = set(row[0] for row in cursor.fetchall())
        total = len(all_reqs)

        # Requirements linked to design
        cursor.execute("SELECT DISTINCT req_id FROM requirement_design_map")
        design_reqs = set(row[0] for row in cursor.fetchall())

        # Requirements linked to test
        cursor.execute("SELECT DISTINCT req_id FROM requirement_testcase_map")
        test_reqs = set(row[0] for row in cursor.fetchall())

        fully_traced = len(design_reqs & test_reqs)
        partially_traced = len((design_reqs ^ test_reqs) & all_reqs)
        untraced = len(all_reqs - (design_reqs | test_reqs))

        design_coverage = len(design_reqs & all_reqs) / total if total else 0.0
        test_coverage = len(test_reqs & all_reqs) / total if total else 0.0

        conn.close()
        return {
            "total": total,
            "design_coverage": design_coverage,
            "test_coverage": test_coverage,
            "fully_traced": fully_traced,
            "partially_traced": partially_traced,
            "untraced": untraced
        }
    """
    Business logic service for traceability operations.
    
    This class provides methods for managing requirements, design modules,
    test cases, and their trace relationships. It includes input validation
    and error handling.
    
    Attributes:
        db (Database): Database access object
        analysis (AnalysisEngine): Impact analysis engine
    """
    
    def __init__(self, db_path: str = "rtm_database.db"):
        """
        Initialize the trace service with a database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db = Database(db_path)
        self.analysis = AnalysisEngine(self.db)
        self.consistency = ConsistencyChecker(self.db)
        self.rule_engine = RuleEngine(self)
        self.duplicate_detector = DuplicateDetector()
    
    def detect_duplicates(self) -> List[dict]:
        """
        Detect semantically similar requirements.
        """
        reqs = self.get_all_requirements()
        # Convert to format expected by detector
        req_list = [{'id': r[0], 'description': r[1]} for r in reqs]
        return self.duplicate_detector.detect_duplicates(req_list)

    def check_new_description(self, description: str) -> Optional[dict]:
        """
        Checks a new description against existing requirements.
        """
        reqs = self.get_all_requirements()
        req_list = [{'id': r[0], 'description': r[1]} for r in reqs]
        return self.duplicate_detector.check_description(description, req_list)

    def suggest_links(self, requirement_text: str) -> dict:
        """
        Suggest relevant design modules and test cases for a requirement description.
        """
        # Get candidates
        design_candidates = [{'id': d[0], 'description': f"{d[1]} {d[2]}"} 
                             for d in self.db.get_all_design_modules()]
        test_candidates = [{'id': t[0], 'description': f"{t[1]} {t[2]}"} 
                           for t in self.db.get_all_test_cases()]

        return {
            'design': self.duplicate_detector.find_top_matches(requirement_text, design_candidates),
            'tests': self.duplicate_detector.find_top_matches(requirement_text, test_candidates)
        }
    
    def validate_rules(self) -> List[dict]:
        """
        Validate all traceability rules.
        """
        return self.rule_engine.validate_rules()
    
    def check_consistency(self) -> List[dict]:
        """
        Check for traceability inconsistencies.
        """
        return self.consistency.check_consistency()

    def validate_system(self) -> dict:
        """
        Consolidates consistency issues and rule violations into a single report.
        
        Returns:
            dict: {
                'issues': [...],
                'rule_violations': [...]
            }
        """
        return {
            'issues': self.check_consistency(),
            'rule_violations': self.validate_rules()
        }

    # ==================== REPORTING OPERATIONS ====================

    def export_traceability_report(self, filename: str) -> bool:
        """Export the full RTM to a PDF report."""
        try:
            data = self.get_traceability_matrix()
            generator = ReportGenerator(filename)
            generator.generate_traceability_report(data)
            return True
        except Exception as e:
            print(f"Failed to export RTM report: {e}")
            return False

    def export_coverage_report(self, filename: str) -> bool:
        """Export coverage metrics to a PDF report."""
        try:
            stats = self.get_traceability_coverage()
            generator = ReportGenerator(filename)
            generator.generate_coverage_report(stats)
            return True
        except Exception as e:
            print(f"Failed to export coverage report: {e}")
            return False

    def export_risk_report(self, filename: str) -> bool:
        """Export risk assessment for all requirements to a PDF report."""
        try:
            risk_items = []
            all_req_ids = self.get_requirement_ids()
            for req_id in all_req_ids:
                analysis = self.get_full_impact_analysis(req_id)
                risk_items.append({
                    'id': req_id,
                    'risk': analysis['risk'],
                    'design': analysis['design'],
                    'tests': analysis['tests']
                })
            
            generator = ReportGenerator(filename)
            generator.generate_risk_report(risk_items)
            return True
        except Exception as e:
            print(f"Failed to export risk report: {e}")
            return False
    
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
        result = self.db.add_requirement(req_id, description, req_type)
        if result is True:
            return True, "Requirement added successfully"
        elif result == "duplicate":
            return False, f"Requirement ID '{req_id}' already exists"
        else:
            return False, f"Database error: {result}"
    
    def get_all_requirements(self) -> List[Tuple[str, str, str]]:
        """
        Get all requirements from the database.
        
        Returns:
            List of tuples containing (req_id, description, req_type)
        """
        return self.db.get_all_requirements()
    
    def get_requirement_by_id(self, req_id: str) -> Optional[Tuple[str, str, str]]:
        """
        Fetch a single requirement by its ID.
        """
        all_reqs = self.get_all_requirements()
        return next((r for r in all_reqs if r[0] == req_id), None)
    
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
        result = self.db.add_design_module(module_id, name, description)
        if result is True:
            return True, "Design module added successfully"
        elif result == "duplicate":
            return False, f"Module ID '{module_id}' already exists"
        else:
            return False, f"Database error: {result}"
    
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
        result = self.db.add_test_case(test_id, description, expected_result)
        if result is True:
            return True, "Test case added successfully"
        elif result == "duplicate":
            return False, f"Test ID '{test_id}' already exists"
        else:
            return False, f"Database error: {result}"
    
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
        result = self.db.add_requirement_design_mapping(req_id, module_id)
        if result is True:
            return True, f"Linked {req_id} to {module_id}"
        elif result == "duplicate":
            return False, "This mapping already exists"
        else:
            return False, f"Database error: {result}"
    
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
        result = self.db.add_requirement_testcase_mapping(req_id, test_id)
        if result is True:
            return True, f"Linked {req_id} to {test_id}"
        elif result == "duplicate":
            return False, "This mapping already exists"
        else:
            return False, f"Database error: {result}"
    
    # ==================== TRACEABILITY MATRIX ====================
    
    def get_traceability_matrix(self) -> List[Tuple[str, str, str, str, str]]:
        """
        Get the complete traceability matrix data.
        
        Returns:
            List of tuples containing:
            (req_id, description, type, linked_modules, linked_tests)
        """
        return self.db.get_traceability_matrix_data()

    # ==================== ANALYSIS OPERATIONS ====================

    def link_requirement_dependency(self, parent_id: str, child_id: str) -> Tuple[bool, str]:
        """
        Create a dependency link between two requirements, preventing cycles.
        """
        if parent_id == child_id:
            return False, "A requirement cannot depend on itself"

        if not self.db.requirement_exists(parent_id):
            return False, f"Parent requirement '{parent_id}' does not exist"

        if not self.db.requirement_exists(child_id):
            return False, f"Child requirement '{child_id}' does not exist"

        # --- CYCLE DETECTION ---
        # If parent_id is reachable from child_id, adding this edge would create a cycle
        edges = self.db.get_all_requirement_dependencies()
        graph = {}
        for p, c in edges:
            graph.setdefault(p, set()).add(c)

        # DFS from child_id to see if parent_id is reachable
        stack = [child_id]
        visited = set()
        while stack:
            node = stack.pop()
            if node == parent_id:
                return False, "Adding this dependency would create a circular dependency."
            if node not in visited:
                visited.add(node)
                stack.extend(graph.get(node, []))

        result = self.db.add_requirement_dependency(parent_id, child_id)
        if result is True:
            return True, f"Requirement '{child_id}' now depends on '{parent_id}'"
        elif result == "duplicate":
            return False, "This dependency already exists"
        elif result == "foreign_key":
            return False, "Dependency failed due to missing referenced requirement."
        elif isinstance(result, str) and result.startswith("constraint:"):
            return False, f"Constraint error: {result[10:]}"
        else:
            return False, "Unknown error occurred while adding dependency."

    def get_impact_analysis(self, req_id: str) -> Tuple[List[str], List[str]]:
        """
        Get upstream dependencies and downstream impact for a requirement.
        
        Returns:
            Tuple of (upstream_dependencies, downstream_impact)
        """
        upstream = self.analysis.get_dependency_chain(req_id)
        downstream = list(self.analysis.get_impacted_requirements(req_id))
        return upstream, downstream

    def get_full_impact_analysis(self, req_id: str) -> dict:
        """
        Produce a comprehensive impact analysis for a single requirement.

        Returns a dict with keys:
          - 'upstream': list of requirement IDs this requirement depends on
          - 'downstream': list of requirement IDs that depend on this requirement
          - 'design': list of linked design module IDs for the requirement
          - 'tests': list of linked test case IDs for the requirement
          - 'risk': one of 'HIGH', 'MEDIUM', 'LOW'

        This method performs bulk queries to avoid N+1 patterns by loading
        dependency edges and mappings in as few queries as possible.
        """
        # Validate requirement exists
        if not self.db.requirement_exists(req_id):
            return {
                'upstream': [],
                'downstream': [],
                'design': [],
                'tests': [],
                'risk': 'HIGH'
            }

        # Load all dependency edges once and build adjacency maps
        edges = self.db.get_all_requirement_dependencies()
        parents_map = {}  # child -> [parents]
        children_map = {}  # parent -> [children]
        for parent, child in edges:
            parents_map.setdefault(child, []).append(parent)
            children_map.setdefault(parent, []).append(child)


        # Upstream: BFS for all ancestors (cycle-safe)
        upstream = []
        visited_up = set([req_id])
        queue_up = [req_id]
        while queue_up:
            cur = queue_up.pop(0)
            for parent in parents_map.get(cur, []):
                if parent not in visited_up:
                    visited_up.add(parent)
                    upstream.append(parent)
                    queue_up.append(parent)

        # Downstream: BFS for all descendants (cycle-safe)
        downstream = []
        visited_down = set([req_id])
        queue_down = [req_id]
        while queue_down:
            cur = queue_down.pop(0)
            for child in children_map.get(cur, []):
                if child not in visited_down:
                    visited_down.add(child)
                    downstream.append(child)
                    queue_down.append(child)

        # Fetch design and test mappings for the root requirement in a single query
        design_map = self.db.get_requirement_design_mappings([req_id])
        test_map = self.db.get_requirement_testcase_mappings([req_id])
        designs = design_map.get(req_id, [])
        tests = test_map.get(req_id, [])

        # Compute risk: no test -> HIGH, no design -> MEDIUM, else LOW
        if not tests:
            risk = 'HIGH'
        elif not designs:
            risk = 'MEDIUM'
        else:
            risk = 'LOW'

        return {
            'upstream': upstream,
            'downstream': downstream,
            'design': designs,
            'tests': tests,
            'risk': risk
        }
