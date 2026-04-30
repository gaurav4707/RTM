"""
Analysis Engine Module (Service Layer)

This module provides advanced analysis capabilities for the RTM Tool,
specifically focusing on impact analysis via requirement dependency graphs.
"""

from typing import List, Set, Dict
from data.database import Database

class AnalysisEngine:
    """
    Engine for performing impact analysis on requirements.
    """
    
    def __init__(self, db: Database):
        """
        Initialize with a database instance.
        """
        self.db = db
        
    def get_impacted_requirements(self, start_req_id: str) -> Set[str]:
        """
        Perform a downstream impact analysis.
        Finds all requirements that directly or indirectly depend on the starting requirement.
        
        Uses a Breadth-First Search (BFS) to traverse the dependency graph.
        
        Args:
            start_req_id: The ID of the requirement that has changed.
            
        Returns:
            Set of impacted requirement IDs.
        """
        impacted = set()
        queue = [start_req_id]
        visited = {start_req_id}
        
        while queue:
            current_id = queue.pop(0)
            
            # Find all requirements that depend on current_id (children)
            dependents = self.db.get_dependents_for_requirement(current_id)
            
            for dep_id in dependents:
                if dep_id not in visited:
                    visited.add(dep_id)
                    impacted.add(dep_id)
                    queue.append(dep_id)
                    
        return impacted

    def get_dependency_chain(self, req_id: str) -> List[str]:
        """
        Finds all requirements that the given requirement depends on (upstream).
        """
        dependencies = []
        queue = [req_id]
        visited = {req_id}
        
        while queue:
            current_id = queue.pop(0)
            parents = self.db.get_dependencies_for_requirement(current_id)
            
            for parent_id in parents:
                if parent_id not in visited:
                    visited.add(parent_id)
                    dependencies.append(parent_id)
                    queue.append(parent_id)
                    
        return dependencies
