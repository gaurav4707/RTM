"""
Model Package

This package contains data model classes for the RTM Tool:
- Requirement: Represents software requirements
- DesignModule: Represents design modules
- TestCase: Represents test cases
"""

from .requirement import Requirement
from .design_module import DesignModule
from .test_case import TestCase

__all__ = ['Requirement', 'DesignModule', 'TestCase']
