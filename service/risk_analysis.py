from enum import Enum
from typing import Callable, List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class RiskLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class RiskAnalyzer:
    """
    Evaluates the risk of a requirement based on its traceability and other factors.
    Uses a rule-based engine to allow easy extension of risk criteria.
    """

    def __init__(self, repository):
        """
        Initialize the RiskAnalyzer with a data repository.
        
        Args:
            repository: An instance of DatabaseRepository providing DB access.
        """
        self.repo = repository
        self.rules: List[Callable[[Dict[str, Any]], Optional[RiskLevel]]] = []
        self._register_default_rules()

    def add_rule(self, rule_func: Callable[[Dict[str, Any]], Optional[RiskLevel]]) -> None:
        """
        Add a custom rule to the analyzer. Rules are evaluated in the order they are added.
        A rule should return a RiskLevel if it applies, or None if it doesn't.
        """
        self.rules.append(rule_func)

    def _register_default_rules(self) -> None:
        """
        Registers the base traceability rules. 
        Higher severity rules should be evaluated first.
        """
        
        def rule_no_test_cases(context: Dict[str, Any]) -> Optional[RiskLevel]:
            if context.get('test_count', 0) == 0:
                return RiskLevel.HIGH
            return None

        def rule_no_design(context: Dict[str, Any]) -> Optional[RiskLevel]:
            if context.get('design_count', 0) == 0:
                return RiskLevel.MEDIUM
            return None

        # Add rules in order of priority/severity
        self.rules.extend([
            rule_no_test_cases,
            rule_no_design
        ])

    def evaluate_requirement_risk(self, req_id: str) -> Dict[str, Any]:
        """
        Calculates the risk score for a specific requirement.
        
        Args:
            req_id (str): The ID of the requirement to evaluate.
            
        Returns:
            Dict[str, Any]: A dictionary containing the risk level and metadata.
        """
        if not self.repo.get_requirement(req_id):
            return {
                "success": False,
                "message": f"Requirement '{req_id}' not found.",
                "req_id": req_id,
                "risk_level": None
            }

        # 1. Gather context data for the rules
        try:
            design_links = self.repo.get_design_links_for_requirement(req_id)
            test_links = self.repo.get_test_links_for_requirement(req_id)
            
            context = {
                "req_id": req_id,
                "design_count": len(design_links),
                "test_count": len(test_links)
            }
            
            # 2. Evaluate rules in sequence
            assigned_risk = RiskLevel.LOW  # Default risk if no higher risk rules trigger
            
            for rule in self.rules:
                result = rule(context)
                if result:
                    assigned_risk = result
                    break  # Stop at the first (highest priority) rule that triggers

            return {
                "success": True,
                "req_id": req_id,
                "risk_level": assigned_risk.value,
                "context": context
            }
            
        except Exception as e:
            logger.error(f"Error evaluating risk for {req_id}: {e}")
            return {
                "success": False,
                "message": str(e),
                "req_id": req_id,
                "risk_level": None
            }

    def evaluate_all_requirements(self) -> List[Dict[str, Any]]:
        """
        Convenience method to evaluate risk for all requirements in the system.
        """
        results = []
        reqs = self.repo.get_all_requirements()
        for req in reqs:
            results.append(self.evaluate_requirement_risk(req['id']))
        return results
