# hr_workflows/__init__.py
"""
PACT HR Workflows Module
Extends PACT core with HR-specific coordination capabilities

This module provides:
- HR agent capability definitions
- Workflow templates for common HR processes
- Coordination endpoints for HR systems
"""

from .hr_coordinator import hr_bp
from .hr_capabilities import HR_CAPABILITIES  
from .workflow_templates import WORKFLOW_TEMPLATES
from .hr_demo_data import get_demo_data

__version__ = "0.1.0"
__author__ = "NeuroBloom.ai"
__description__ = "HR Workflow Coordination using PACT Protocol"

__all__ = [
    "hr_bp", 
    "HR_CAPABILITIES", 
    "WORKFLOW_TEMPLATES", 
    "get_demo_data"
]
