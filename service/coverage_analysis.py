from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class CoverageAnalyzer:
    """
    Analyzes traceability coverage across requirements, design modules, and test cases.
    Computes percentages and categorization (fully traced, partially traced, untraced).
    """

    def __init__(self, repository):
        """
        Initialize the analyzer with a data repository.
        
        Args:
            repository: An instance of DatabaseRepository that provides data access.
        """
        self.repo = repository

    def compute_traceability_coverage(self) -> Dict[str, Any]:
        """
        Computes traceability coverage metrics using an efficient SQL aggregation.
        
        Returns:
            Dict[str, Any]: Structured output containing:
                - total_requirements (int)
                - linked_to_design_count (int)
                - linked_to_design_percentage (float)
                - linked_to_test_count (int)
                - linked_to_test_percentage (float)
                - fully_traced_count (int)
                - fully_traced_percentage (float)
                - partially_traced_count (int)
                - partially_traced_percentage (float)
                - untraced_count (int)
                - untraced_percentage (float)
                - success (bool)
                - message (str)
        """
        query = """
        WITH ReqStats AS (
            SELECT 
                r.id,
                CASE WHEN EXISTS (SELECT 1 FROM requirement_design rd WHERE rd.req_id = r.id) THEN 1 ELSE 0 END as has_design,
                CASE WHEN EXISTS (SELECT 1 FROM requirement_test rt WHERE rt.req_id = r.id) THEN 1 ELSE 0 END as has_test
            FROM requirements r
        )
        SELECT
            COUNT(*) as total_reqs,
            SUM(has_design) as reqs_with_design,
            SUM(has_test) as reqs_with_test,
            SUM(CASE WHEN has_design = 1 AND has_test = 1 THEN 1 ELSE 0 END) as fully_traced,
            SUM(CASE WHEN has_design = 1 AND has_test = 0 THEN 1 
                     WHEN has_design = 0 AND has_test = 1 THEN 1 ELSE 0 END) as partially_traced,
            SUM(CASE WHEN has_design = 0 AND has_test = 0 THEN 1 ELSE 0 END) as untraced
        FROM ReqStats;
        """

        try:
            with self.repo.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                row = cursor.fetchone()

            if not row or row['total_reqs'] == 0:
                return self._empty_coverage_result("No requirements found to analyze.")

            total = row['total_reqs']
            reqs_with_design = row['reqs_with_design'] or 0
            reqs_with_test = row['reqs_with_test'] or 0
            fully_traced = row['fully_traced'] or 0
            partially_traced = row['partially_traced'] or 0
            untraced = row['untraced'] or 0

            return {
                "success": True,
                "message": "Coverage analysis completed successfully.",
                "total_requirements": total,
                "linked_to_design_count": reqs_with_design,
                "linked_to_design_percentage": round((reqs_with_design / total) * 100, 2),
                "linked_to_test_count": reqs_with_test,
                "linked_to_test_percentage": round((reqs_with_test / total) * 100, 2),
                "fully_traced_count": fully_traced,
                "fully_traced_percentage": round((fully_traced / total) * 100, 2),
                "partially_traced_count": partially_traced,
                "partially_traced_percentage": round((partially_traced / total) * 100, 2),
                "untraced_count": untraced,
                "untraced_percentage": round((untraced / total) * 100, 2),
            }

        except Exception as e:
            logger.error(f"Error computing traceability coverage: {e}")
            return self._empty_coverage_result(f"An error occurred: {e}", success=False)

    def _empty_coverage_result(self, message: str, success: bool = True) -> Dict[str, Any]:
        """Helper to return a zero-state result when no data exists or an error occurs."""
        return {
            "success": success,
            "message": message,
            "total_requirements": 0,
            "linked_to_design_count": 0,
            "linked_to_design_percentage": 0.0,
            "linked_to_test_count": 0,
            "linked_to_test_percentage": 0.0,
            "fully_traced_count": 0,
            "fully_traced_percentage": 0.0,
            "partially_traced_count": 0,
            "partially_traced_percentage": 0.0,
            "untraced_count": 0,
            "untraced_percentage": 0.0,
        }
