from typing import List, Dict, Set, Any
import logging

logger = logging.getLogger(__name__)

class ImpactAnalysisEngine:
    """
    Engine for performing impact analysis on requirements.
    Determines which design modules, test cases, and other requirements
    are affected when a specific requirement changes.
    """

    def __init__(self, repository):
        """
        Initialize the engine with a data repository.
        
        Args:
            repository: An instance of DatabaseRepository (or similar) 
                        that provides data access methods.
        """
        self.repo = repository

    def analyze_impact(self, req_id: str) -> Dict[str, Any]:
        """
        Performs a full impact analysis for a given requirement ID.
        
        Finds all downstream impacted requirements by traversing the dependency 
        graph, and collects all linked design modules and test cases for both 
        the root requirement and all impacted requirements.
        
        Args:
            req_id (str): The ID of the root requirement to analyze.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - 'root_requirement': The ID of the analyzed requirement
                - 'impacted_requirements': List of dependent requirement IDs
                - 'impacted_design_modules': List of linked design module IDs
                - 'impacted_test_cases': List of linked test case IDs
                - 'success': Boolean indicating if the analysis succeeded
                - 'message': Status or error message
        """
        # Validate existence of root requirement
        if not self.repo.get_requirement(req_id):
            return {
                "success": False,
                "message": f"Requirement with ID '{req_id}' not found.",
                "root_requirement": req_id,
                "impacted_requirements": [],
                "impacted_design_modules": [],
                "impacted_test_cases": []
            }

        try:
            # 1. Find all impacted downstream requirements (BFS traversal to handle cycles safely)
            impacted_reqs = self._find_downstream_requirements(req_id)
            
            # Combine root requirement and all impacted requirements to find artifacts
            all_affected_reqs = {req_id} | impacted_reqs
            
            impacted_designs = set()
            impacted_tests = set()

            # 2. Collect linked artifacts for all affected requirements
            for r_id in all_affected_reqs:
                impacted_designs.update(self.repo.get_design_links_for_requirement(r_id))
                impacted_tests.update(self.repo.get_test_links_for_requirement(r_id))

            return {
                "success": True,
                "message": "Impact analysis completed successfully.",
                "root_requirement": req_id,
                "impacted_requirements": sorted(list(impacted_reqs)),
                "impacted_design_modules": sorted(list(impacted_designs)),
                "impacted_test_cases": sorted(list(impacted_tests))
            }

        except Exception as e:
            logger.error(f"Error during impact analysis for {req_id}: {e}")
            return {
                "success": False,
                "message": f"An error occurred during analysis: {e}",
                "root_requirement": req_id,
                "impacted_requirements": [],
                "impacted_design_modules": [],
                "impacted_test_cases": []
            }

    def _find_downstream_requirements(self, root_req_id: str) -> Set[str]:
        """
        Traverses the dependency graph using Breadth-First Search (BFS) to find 
        all requirements that depend (directly or indirectly) on the root requirement.
        
        Args:
            root_req_id (str): The ID of the starting requirement.
            
        Returns:
            Set[str]: A set of impacted requirement IDs (excluding the root).
        """
        impacted = set()
        queue = [root_req_id]
        
        while queue:
            current_id = queue.pop(0)
            
            # Retrieve requirements that depend on 'current_id'
            # Note: The repository needs a method that queries: 
            # SELECT req_id FROM requirement_dependency WHERE depends_on_req_id = ?
            dependent_reqs = self._get_requirements_depending_on(current_id)
            
            for dep_id in dependent_reqs:
                # Prevent infinite loops in case of circular dependencies
                if dep_id not in impacted and dep_id != root_req_id:
                    impacted.add(dep_id)
                    queue.append(dep_id)
                    
        return impacted

    def _get_requirements_depending_on(self, target_req_id: str) -> List[str]:
        """
        Helper to fetch requirements that depend on a specific target.
        If the repository doesn't have this method natively, we implement it here 
        by reaching into the DB connection safely.
        """
        # If repo natively supports it:
        if hasattr(self.repo, 'get_requirements_depending_on'):
            return self.repo.get_requirements_depending_on(target_req_id)
            
        # Fallback implementation assuming self.repo has get_connection()
        try:
            with self.repo.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT req_id FROM requirement_dependency WHERE depends_on_req_id = ?", 
                    (target_req_id,)
                )
                return [row['req_id'] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to fetch dependencies for {target_req_id}: {e}")
            return []
