# hr_workflows/hr_coordinator.py
"""
HR Workflow Coordinator
Main coordination logic and Flask Blueprint for HR workflows
"""

import json
import time
import uuid
import sys
import os
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify

# Import from local HR modules
from .hr_capabilities import (
    HR_CAPABILITIES, 
    validate_agent_action, 
    get_agents_for_action,
    get_all_hr_agents
)
from .workflow_templates import (
    WORKFLOW_TEMPLATES,
    get_workflow_template,
    get_available_workflows, 
    validate_workflow_params,
    get_critical_steps
)
from .hr_demo_data import get_demo_data, get_sample_for_workflow

# Import PACT core functions (assumes parent directory structure)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from pact_cli_mock import match_capabilities
except ImportError:
    # Fallback if PACT core not available
    def match_capabilities(action, parameters):
        return {"agent_id": "fallback_agent", "match_score": 0.5}

# Create Blueprint for HR workflows
hr_bp = Blueprint('hr_workflows', __name__, url_prefix='/hr')

# Active workflow tracking
active_workflows = {}

def simulate_step_execution(step, params, workflow_id):
    """Simulate executing a workflow step with realistic responses"""
    
    # Realistic response templates
    responses = {
        "ats_agent": {
            "create_profile": f"✅ Profile created for {params.get('employee_name', 'employee')} in ATS",
            "update_status": "✅ Candidate status updated successfully",
            "schedule_interview": f"✅ Interview scheduled with {params.get('interviewer', 'interviewer')}"
        },
        "hris_agent": {
            "setup_employee": f"✅ Employee ID EMP{uuid.uuid4().hex[:6].upper()} generated for {params.get('employee_name', 'employee')}",
            "update_records": "✅ Employee records updated in HRIS system",
            "generate_id": f"✅ Generated ID: EMP{uuid.uuid4().hex[:6].upper()}"
        },
        "it_agent": {
            "provision_access": f"✅ IT access provisioned for {params.get('department', 'department')} department",
            "create_accounts": f"✅ Created accounts: {params.get('email', 'user@company.com')}",
            "revoke_access": "✅ All system access revoked successfully"
        },
        "calendar_agent": {
            "schedule_onboarding": f"✅ Onboarding meeting scheduled with {params.get('manager', 'manager')}",
            "book_review_meetings": "✅ Performance review meetings scheduled",
            "send_reminders": "✅ Calendar reminders sent to participants"
        },
        "notification_agent": {
            "send_welcome": f"✅ Welcome email sent to {params.get('employee_name', 'employee')}",
            "notify_team": "✅ Team notification emails sent",
            "send_reminder": "✅ Reminder notifications sent"
        },
        "payroll_agent": {
            "setup_payroll": f"✅ Payroll configured: ${params.get('salary', 'N/A')} salary",
            "process_timesheet": "✅ Timesheet processed for pay period",
            "setup_direct_deposit": "✅ Direct deposit configured"
        },
        "learning_agent": {
            "assign_training": "✅ Mandatory training courses assigned",
            "track_progress": "✅ Training progress tracking enabled",
            "schedule_mentoring": "✅ Mentoring sessions scheduled"
        }
    }
    
    agent_responses = responses.get(step["agent"], {})
    response = agent_responses.get(step["action"], f"✅ {step['action']} completed")
    
    return {
        "step": step["step"],
        "name": step["name"],
        "agent": step["agent"],
        "action": step["action"],
        "status": "completed",
        "result": response,
        "execution_time_seconds": step["estimated_time"],
        "timestamp": datetime.now().isoformat(),
        "workflow_id": workflow_id
    }

@hr_bp.route('/coordinate', methods=['POST'])
def hr_coordinate():
    """Single HR action coordination using PACT foundation"""
    data = request.get_json()
    
    hr_intent = data.get("intent")
    parameters = data.get("parameters", {})
    
    # Find capable HR agents
    capable_agents = get_agents_for_action(hr_intent)
    
    if capable_agents:
        best_agent = capable_agents[0]  # Highest priority agent
        validation = validate_agent_action(best_agent["agent"], hr_intent, parameters)
        
        coordination_result = {
            "coordination_id": f"coord_{uuid.uuid4().hex[:8]}",
            "matched_agent": best_agent["agent"],
            "action": hr_intent,
            "status": "coordinated" if validation["valid"] else "partial",
            "success_rate": validation["success_rate"],
            "missing_params": validation.get("missing_params", []),
            "estimated_completion_seconds": 60,
            "timestamp": datetime.now().isoformat()
        }
        return jsonify(coordination_result)
    else:
        return jsonify({
            "status": "failed",
            "message": f"No HR agent found for action: {hr_intent}",
            "available_actions": list(set([action for agent in HR_CAPABILITIES.values() for action in agent.keys()]))
        }), 404

@hr_bp.route('/workflows/<workflow_type>', methods=['POST'])
def execute_workflow(workflow_type):
    """Execute complete HR workflow sequence"""
    data = request.get_json()
    
    # Validate workflow type
    template = get_workflow_template(workflow_type)
    if not template:
        return jsonify({
            "error": f"Unknown workflow type: {workflow_type}",
            "available_workflows": list(WORKFLOW_TEMPLATES.keys())
        }), 400
    
    # Validate parameters
    validation = validate_workflow_params(workflow_type, data)
    if not validation["valid"]:
        return jsonify({
            "error": "Missing required parameters",
            "missing_params": validation["missing_params"],
            "provided_params": validation["provided_params"],
            "completion_rate": f"{validation['completion_rate']*100:.1f}%"
        }), 400
    
    # Create workflow instance
    workflow_id = f"wf_{workflow_type}_{uuid.uuid4().hex[:8]}"
    workflow_steps = template["steps"].copy()
    
    # Calculate total estimated time
    total_time = sum(step["estimated_time"] for step in workflow_steps)
    
    # Store workflow
    active_workflows[workflow_id] = {
        "type": workflow_type,
        "name": template["name"],
        "status": "initiated",
        "steps": workflow_steps,
        "params": data,
        "created_at": datetime.now().isoformat(),
        "estimated_completion": (datetime.now() + timedelta(seconds=total_time)).isoformat(),
        "total_steps": len(workflow_steps),
        "completed_steps": 0
    }
    
    # Execute first step immediately (simulation)
    first_step = workflow_steps[0]
    step_result = simulate_step_execution(first_step, data, workflow_id)
    
    # Update workflow status
    active_workflows[workflow_
