# hr_workflows/workflow_templates.py
"""
HR Workflow Templates
Defines step-by-step processes for common HR workflows
"""

WORKFLOW_TEMPLATES = {
    "onboarding": {
        "name": "Employee Onboarding",
        "description": "Complete new hire onboarding process",
        "estimated_duration": 420,  # 7 minutes total
        "steps": [
            {
                "step": 1,
                "name": "Create ATS Profile",
                "agent": "ats_agent",
                "action": "create_profile",
                "depends_on": [],
                "estimated_time": 30,
                "critical": True,
                "description": "Create candidate profile in ATS system"
            },
            {
                "step": 2,
                "name": "Setup Employee Record",
                "agent": "hris_agent",
                "action": "setup_employee",
                "depends_on": ["step_1"],
                "estimated_time": 120,
                "critical": True,
                "description": "Create employee record and generate ID"
            },
            {
                "step": 3,
                "name": "Provision IT Access",
                "agent": "it_agent",
                "action": "provision_access",
                "depends_on": ["step_2"],
                "estimated_time": 180,
                "critical": True,
                "description": "Create accounts and provision system access"
            },
            {
                "step": 4,
                "name": "Setup Payroll",
                "agent": "payroll_agent",
                "action": "setup_payroll",
                "depends_on": ["step_2"],
                "estimated_time": 90,
                "critical": True,
                "description": "Configure payroll and compensation"
            },
            {
                "step": 5,
                "name": "Schedule Onboarding",
                "agent": "calendar_agent",
                "action": "schedule_onboarding",
                "depends_on": ["step_2"],
                "estimated_time": 60,
                "critical": False,
                "description": "Schedule first day meetings and orientation"
            },
            {
                "step": 6,
                "name": "Send Welcome Package",
                "agent": "notification_agent",
                "action": "send_welcome",
                "depends_on": ["step_2", "step_5"],
                "estimated_time": 30,
                "critical": False,
                "description": "Send welcome email and first day instructions"
            },
            {
                "step": 7,
                "name": "Assign Training",
                "agent": "learning_agent",
                "action": "assign_training",
                "depends_on": ["step_3"],
                "estimated_time": 45,
                "critical": False,
                "description": "Assign mandatory training courses"
            }
        ]
    },
    
    "performance_review": {
        "name": "Performance Review Cycle",
        "description": "Quarterly performance review process",
        "estimated_duration": 150,  # 2.5 minutes
        "steps": [
            {
                "step": 1,
                "name": "Schedule Review Meetings",
                "agent": "calendar_agent",
                "action": "book_review_meetings",
                "depends_on": [],
                "estimated_time": 90,
                "critical": True,
                "description": "Schedule all review meetings for the cycle"
            },
            {
                "step": 2,
                "name": "Send Review Reminders",
                "agent": "notification_agent",
                "action": "send_reminder",
                "depends_on": ["step_1"],
                "estimated_time": 15,
                "critical": False,
                "description": "Send reminders to reviewers and reviewees"
            },
            {
                "step": 3,
                "name": "Update HR Records",
                "agent": "hris_agent",
                "action": "update_records",
                "depends_on": ["step_1"],
                "estimated_time": 45,
                "critical": True,
                "description": "Update employee records with review cycle info"
            }
        ]
    },
    
    "offboarding": {
        "name": "Employee Offboarding",
        "description": "Complete employee departure process",
        "estimated_duration": 105,  # 1.75 minutes
        "steps": [
            {
                "step": 1,
                "name": "Revoke IT Access",
                "agent": "it_agent",
                "action": "revoke_access",
                "depends_on": [],
                "estimated_time": 60,
                "critical": True,
                "description": "Immediately revoke all system access"
            },
            {
                "step": 2,
                "name": "Update Employee Status",
                "agent": "hris_agent",
                "action": "update_records",
                "depends_on": [],
                "estimated_time": 30,
                "critical": True,
                "description": "Mark employee as departed in HR system"
            },
            {
                "step": 3,
                "name": "Notify Team",
                "agent": "notification_agent",
                "action": "notify_team",
                "depends_on": ["step_1"],
                "estimated_time": 15,
                "critical": False,
                "description": "Inform team members of departure"
            }
        ]
    },
    
    "promotion": {
        "name": "Employee Promotion",
        "description": "Process employee promotion and role change",
        "estimated_duration": 240,  # 4 minutes
        "steps": [
            {
                "step": 1,
                "name": "Update HR Records",
                "agent": "hris_agent",
                "action": "update_records",
                "depends_on": [],
                "estimated_time": 60,
                "critical": True,
                "description": "Update title, salary, and reporting structure"
            },
            {
                "step": 2,
                "name": "Update IT Access",
                "agent": "it_agent",
                "action": "provision_access",
                "depends_on": ["step_1"],
                "estimated_time": 90,
                "critical": True,
                "description": "Update system access for new role"
            },
            {
                "step": 3,
                "name": "Update Payroll",
                "agent": "payroll_agent",
                "action": "setup_payroll",
                "depends_on": ["step_1"],
                "estimated_time": 60,
                "critical": True,
                "description": "Process salary change and new compensation"
            },
            {
                "step": 4,
                "name": "Notify Organization",
                "agent": "notification_agent",
                "action": "email_blast",
                "depends_on": ["step_1"],
                "estimated_time": 30,
                "critical": False,
                "description": "Announce promotion to organization"
            }
        ]
    }
}

def get_workflow_template(workflow_type):
    """Get a specific workflow template"""
    return WORKFLOW_TEMPLATES.get(workflow_type)

def get_available_workflows():
    """Get list of all available workflow types"""
    return {
        name: {
            "name": template["name"],
            "description": template["description"],
            "estimated_duration": template["estimated_duration"],
            "step_count": len(template["steps"])
        }
        for name, template in WORKFLOW_TEMPLATES.items()
    }

def get_workflow_dependencies(workflow_type):
    """Get dependency graph for a workflow"""
    template = get_workflow_template(workflow_type)
    if not template:
        return None
    
    dependencies = {}
    for step in template["steps"]:
        step_id = f"step_{step['step']}"
        dependencies[step_id] = {
            "depends_on": step["depends_on"],
            "agent": step["agent"],
            "action": step["action"],
            "critical": step["critical"]
        }
    
    return dependencies

def validate_workflow_params(workflow_type, params):
    """Validate required parameters for a workflow"""
    required_params = {
        "onboarding": ["employee_name", "department", "start_date", "manager", "email", "position", "salary"],
        "performance_review": ["employee_id", "reviewer", "review_cycle"],
        "offboarding": ["employee_id", "last_day", "reason"],
        "promotion": ["employee_id", "new_title", "new_salary", "new_department", "effective_date"]
    }
    
    required = required_params.get(workflow_type, [])
    provided = set(params.keys())
    missing = set(required) - provided
    
    return {
        "valid": len(missing) == 0,
        "missing_params": list(missing),
        "provided_params": list(provided),
        "completion_rate": len(provided & set(required)) / len(required) if required else 1.0
    }

def get_critical_steps(workflow_type):
    """Get only the critical steps for a workflow"""
    template = get_workflow_template(workflow_type)
    if not template:
        return []
    
    return [step for step in template["steps"] if step.get("critical", False)]
