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
    active_workflows[workflow_id]["steps"][0]["result"] = step_result
    active_workflows[workflow_id]["status"] = "in_progress"
    active_workflows[workflow_id]["completed_steps"] = 1
    
    return jsonify({
        "workflow_id": workflow_id,
        "workflow_type": workflow_type,
        "workflow_name": template["name"],
        "status": "initiated",
        "total_steps": len(workflow_steps),
        "estimated_completion_time": f"{total_time} seconds",
        "first_step_completed": step_result,
        "next_steps": [
            {
                "step": step["step"],
                "name": step["name"],
                "agent": step["agent"], 
                "action": step["action"],
                "status": "queued",
                "depends_on": step["depends_on"],
                "critical": step.get("critical", False)
            } for step in workflow_steps[1:]
        ],
        "tracking_url": f"/hr/workflows/{workflow_id}/status"
    })

@hr_bp.route('/workflows/<workflow_id>/status', methods=['GET'])
def workflow_status(workflow_id):
    """Check workflow execution status"""
    if workflow_id not in active_workflows:
        return jsonify({"error": "Workflow not found"}), 404
    
    workflow = active_workflows[workflow_id]
    
    # Simulate progressive completion based on time elapsed
    created_time = datetime.fromisoformat(workflow["created_at"])
    elapsed_seconds = (datetime.now() - created_time).total_seconds()
    
    completed_steps = []
    pending_steps = []
    in_progress_steps = []
    
    cumulative_time = 0
    
    for i, step in enumerate(workflow["steps"]):
        cumulative_time += step["estimated_time"]
        
        if elapsed_seconds >= cumulative_time or "result" in step:
            # Step should be completed
            if "result" not in step:
                step["result"] = simulate_step_execution(step, workflow["params"], workflow_id)
            completed_steps.append(step["result"])
        elif elapsed_seconds >= (cumulative_time - step["estimated_time"]):
            # Step is in progress
            progress_pct = ((elapsed_seconds - (cumulative_time - step["estimated_time"])) / step["estimated_time"]) * 100
            in_progress_steps.append({
                "step": step["step"],
                "name": step["name"],
                "agent": step["agent"],
                "action": step["action"],
                "status": "in_progress",
                "progress": f"{min(progress_pct, 100):.1f}%",
                "depends_on": step["depends_on"]
            })
        else:
            # Step is pending
            pending_steps.append({
                "step": step["step"],
                "name": step["name"],
                "agent": step["agent"],
                "action": step["action"], 
                "status": "pending",
                "depends_on": step["depends_on"],
                "critical": step.get("critical", False)
            })
    
    total_steps = len(workflow["steps"])
    completed_count = len(completed_steps)
    progress = (completed_count / total_steps) * 100
    
    # Update workflow status
    if progress == 100:
        workflow["status"] = "completed"
    elif completed_count > 0:
        workflow["status"] = "in_progress"
    
    workflow["completed_steps"] = completed_count
    
    return jsonify({
        "workflow_id": workflow_id,
        "type": workflow["type"],
        "name": workflow["name"],
        "status": workflow["status"],
        "progress": f"{progress:.1f}%",
        "completed_steps": completed_steps,
        "in_progress_steps": in_progress_steps,
        "pending_steps": pending_steps,
        "total_steps": total_steps,
        "created_at": workflow["created_at"],
        "estimated_completion": workflow["estimated_completion"]
    })

@hr_bp.route('/workflows', methods=['GET'])
def list_workflows():
    """List all available workflow templates and active workflows"""
    return jsonify({
        "available_templates": get_available_workflows(),
        "active_workflows": [
            {
                "workflow_id": wf_id,
                "type": wf["type"],
                "name": wf["name"],
                "status": wf["status"],
                "progress": f"{(wf['completed_steps'] / wf['total_steps'] * 100):.1f}%",
                "created_at": wf["created_at"]
            } for wf_id, wf in active_workflows.items()
        ],
        "total_active": len(active_workflows),
        "hr_agents_available": get_all_hr_agents()
    })

@hr_bp.route('/capabilities', methods=['GET'])
def hr_capabilities():
    """Get all HR agent capabilities"""
    return jsonify({
        "hr_agents": HR_CAPABILITIES,
        "total_agents": len(HR_CAPABILITIES),
        "total_actions": sum(len(actions) for actions in HR_CAPABILITIES.values()),
        "agent_summary": {
            agent: {
                "action_count": len(actions),
                "available_actions": list(actions.keys())
            } for agent, actions in HR_CAPABILITIES.items()
        }
    })

@hr_bp.route('/capabilities/<agent_name>', methods=['GET'])
def agent_capabilities(agent_name):
    """Get capabilities for a specific HR agent"""
    if agent_name not in HR_CAPABILITIES:
        return jsonify({
            "error": f"Agent '{agent_name}' not found",
            "available_agents": list(HR_CAPABILITIES.keys())
        }), 404
    
    capabilities = HR_CAPABILITIES[agent_name]
    return jsonify({
        "agent": agent_name,
        "capabilities": capabilities,
        "action_count": len(capabilities),
        "actions": list(capabilities.keys())
    })

@hr_bp.route('/demo-data', methods=['GET'])
def hr_demo_data():
    """Provide sample data for HR workflow testing"""
    return jsonify(get_demo_data())

@hr_bp.route('/demo-data/<workflow_type>', methods=['GET'])
def workflow_demo_data(workflow_type):
    """Get demo data for a specific workflow type"""
    sample = get_sample_for_workflow(workflow_type)
    if not sample:
        return jsonify({
            "error": f"No demo data available for workflow: {workflow_type}",
            "available_workflows": ["onboarding", "performance_review", "offboarding", "promotion"]
        }), 404
    
    return jsonify({
        "workflow_type": workflow_type,
        "sample_data": sample,
        "curl_example": f"""
curl -X POST http://127.0.0.1:8000/hr/workflows/{workflow_type} \\
-H 'Content-Type: application/json' \\
-d '{json.dumps(sample)}'
        """.strip()
    })

@hr_bp.route('/health', methods=['GET'])
def hr_health():
    """Health check for HR workflow system"""
    return jsonify({
        "status": "healthy",
        "hr_module_version": "0.1.0",
        "available_workflows": len(WORKFLOW_TEMPLATES),
        "available_agents": len(HR_CAPABILITIES),
        "active_workflows": len(active_workflows),
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "coordination": "/hr/coordinate",
            "workflows": "/hr/workflows/<type>",
            "status": "/hr/workflows/<id>/status",
            "capabilities": "/hr/capabilities",
            "demo_data": "/hr/demo-data"
        }
    })

# Error handlers for HR Blueprint
@hr_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": "Bad Request",
        "message": "Invalid request format or missing required parameters",
        "timestamp": datetime.now().isoformat()
    }), 400

@hr_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found", 
        "message": "The requested resource was not found",
        "timestamp": datetime.now().isoformat()
    }), 404

@hr_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
        "timestamp": datetime.now().isoformat()
    }), 500
