from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class ConsistencyChecker:
    """
    Checks the RTM system for data inconsistencies and orphaned entities.
    """

    def __init__(self, database):
        """
        Initialize the checker with a database instance.
        
        Args:
            database: An instance of Database providing DB access.
        """
        self.db = database

    def check_consistency(self) -> List[Dict[str, str]]:
        """
        Scans the database for traceability issues using optimized SQL.
        
        Issues detected:
        - NO_DESIGN: Requirements missing design module links
        - NO_TEST: Requirements missing test case links
        - ORPHAN_DESIGN: Orphan design modules (not linked to any requirement)
        - ORPHAN_TEST: Orphan test cases (not linked to any requirement)
        
        Returns:
            List[Dict[str, str]]: A list of dictionaries representing issues.
        """
        try:
            raw_issues = self.db.get_consistency_issues()
            return [
                {
                    'type': issue[0],
                    'id': issue[1],
                    'message': issue[2]
                }
                for issue in raw_issues
            ]
        except Exception as e:
            logger.error(f"Consistency check failed: {e}")
            return [{
                'type': 'ERROR',
                'id': 'SYSTEM',
                'message': f"Failed to perform consistency check: {str(e)}"
            }]
