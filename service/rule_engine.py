import abc
from typing import List, Dict, Any

class Rule(abc.ABC):
    """Abstract base class for all rules."""
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The identifier for the rule (e.g. REQ_HAS_TEST)."""
        pass
        
    @abc.abstractmethod
    def evaluate(self, service: Any) -> List[Dict[str, str]]:
        """
        Evaluate the rule against the provided service.
        Returns a list of violation dictionaries.
        """
        pass

class ReqHasTestRule(Rule):
    """Rule: Every requirement must have at least one test case."""
    @property
    def name(self) -> str:
        return "REQ_HAS_TEST"
        
    def evaluate(self, service: Any) -> List[Dict[str, str]]:
        violations = []
        # Get all requirements (format: list of tuples (id, desc, type))
        requirements = service.get_all_requirements()
        
        for req in requirements:
            req_id = req[0]
            # Check for linked test cases
            test_cases = service.db.get_test_cases_for_requirement(req_id)
            if not test_cases:
                violations.append({
                    'rule': self.name,
                    'id': req_id,
                    'status': 'VIOLATION'
                })
        return violations

class RuleEngine:
    """
    Orchestrates the evaluation of multiple traceability rules.
    Designed for extensibility - simply add more Rule subclasses.
    """
    def __init__(self, service: Any):
        self.service = service
        self.rules: List[Rule] = [
            ReqHasTestRule() # Register default rules
        ]
        
    def add_rule(self, rule: Rule):
        """Add a new custom rule to the engine."""
        self.rules.append(rule)
        
    def validate_rules(self) -> List[Dict[str, str]]:
        """
        Runs all registered rules and collects violations.
        
        Returns:
            List[Dict]: List of violation results in the format:
            [{'rule': '...', 'id': '...', 'status': 'VIOLATION'}]
        """
        all_violations = []
        for rule in self.rules:
            violations = rule.evaluate(self.service)
            all_violations.extend(violations)
        return all_violations
