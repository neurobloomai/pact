# hr_workflows/hr_capabilities.py
"""
HR System Agent Capabilities
Defines what each HR agent can do and required parameters
"""

HR_CAPABILITIES = {
    "ats_agent": {
        "create_profile": ["candidate_name", "email", "position"],
        "update_status": ["candidate_id", "new_status"],
        "schedule_interview": ["candidate_id", "interviewer", "date"],
        "search_candidates": ["position", "skills", "location"],
        "send_offer": ["candidate_id", "offer_details", "deadline"]
    },
    "hris_agent": {
        "setup_employee": ["employee_name", "department", "start_date", "manager"],
        "update_records": ["employee_id", "field", "value"],
        "generate_id": ["employee_name", "department"],
        "enroll_benefits": ["employee_id", "benefit_plan"],
        "create_org_chart": ["department", "reporting_structure"]
    },
    "it_agent": {
        "provision_access": ["employee_id", "department", "access_level"],
        "create_accounts": ["employee_name", "email", "department"],
        "revoke_access": ["employee_id", "immediate"],
        "setup_hardware": ["employee_id", "equipment_type", "delivery_date"],
        "configure_vpn": ["employee_id", "access_type"]
    },
    "calendar_agent": {
        "schedule_onboarding": ["employee_name", "manager", "date"],
        "book_review_meetings": ["reviewer", "reviewee", "cycle"],
        "send_reminders": ["meeting_id", "participants"],
        "block_time": ["employee_id", "duration", "purpose"],
        "schedule_training": ["employee_id", "training_type", "date"]
    },
    "notification_agent": {
        "send_welcome": ["employee_name", "manager", "start_date"],
        "notify_team": ["team_members", "new_hire_info"],
        "send_reminder": ["recipient", "message", "urgency"],
        "email_blast": ["recipient_list", "subject", "content"],
        "slack_notification": ["channel", "message", "priority"]
    },
    "payroll_agent": {
        "setup_payroll": ["employee_id", "salary", "pay_frequency"],
        "process_timesheet": ["employee_id", "hours", "pay_period"],
        "generate_paystub": ["employee_id", "pay_period"],
        "handle_tax_forms": ["employee_id", "form_type"],
        "setup_direct_deposit": ["employee_id", "bank_details"]
    },
    "learning_agent": {
        "assign_training": ["employee_id", "course_list", "deadline"],
        "track_progress": ["employee_id", "course_id"],
        "generate_certificate": ["employee_id", "course_id"],
        "recommend_courses": ["employee_id", "skill_gaps"],
        "schedule_mentoring": ["mentee_id", "mentor_id", "frequency"]
    }
}

# Agent priority levels for workflow execution
AGENT_PRIORITIES = {
    "hris_agent": 1,  # High priority - core employee data
    "it_agent": 2,    # High priority - access and security
    "payroll_agent": 3,  # Medium priority - compensation setup
    "calendar_agent": 4,  # Medium priority - scheduling
    "ats_agent": 5,      # Lower priority - candidate tracking
    "notification_agent": 6,  # Lower priority - communications
    "learning_agent": 7   # Lowest priority - training assignments
}

def get_agent_capabilities(agent_name):
    """Get capabilities for a specific agent"""
    return HR_CAPABILITIES.get(agent_name, {})

def get_required_params(agent_name, action):
    """Get required parameters for a specific agent action"""
    agent_caps = HR_CAPABILITIES.get(agent_name, {})
    return agent_caps.get(action, [])

def validate_agent_action(agent_name, action, params):
    """Validate if agent can perform action with given parameters"""
    required_params = get_required_params(agent_name, action)
    provided_params = set(params.keys())
    missing_params = set(required_params) - provided_params
    
    return {
        "valid": len(missing_params) == 0,
        "missing_params": list(missing_params),
        "success_rate": len(provided_params & set(required_params)) / len(required_params) if required_params else 1.0
    }

def get_all_hr_agents():
    """Get list of all available HR agents"""
    return list(HR_CAPABILITIES.keys())

def get_agents_for_action(action):
    """Find which agents can perform a specific action"""
    capable_agents = []
    for agent, capabilities in HR_CAPABILITIES.items():
        if action in capabilities:
            capable_agents.append({
                "agent": agent,
                "required_params": capabilities[action],
                "priority": AGENT_PRIORITIES.get(agent, 10)
            })
    
    # Sort by priority (lower number = higher priority)
    return sorted(capable_agents, key=lambda x: x["priority"])
