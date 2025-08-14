# HR Workflows Module

**PACT Protocol Extension for Human Resources Coordination**

---

## Overview

The HR Workflows module extends the core PACT protocol to provide comprehensive coordination for Human Resources processes. It implements the **Foundation → Workflows → Natural Communication** progression, enabling seamless coordination across HR systems.

### Key Philosophy
> **"Coordination foundation first → Coordination workflows second → Communication becomes natural"**

## Features

### 🏗️ **Foundation Layer**
- **7 HR Agent Types** with 30+ coordinated actions
- **Universal capability negotiation** using PACT core
- **Standardized message formats** for all HR communications

### 🔄 **Workflow Layer** 
- **4 Complete Workflow Templates**: Onboarding, Performance Reviews, Offboarding, Promotions
- **Dependency management** with automatic sequencing
- **Real-time progress tracking** with step-by-step visibility

### 💬 **Natural Communication**
- **Plug-and-play agent integration** using existing coordination infrastructure
- **Automatic intent translation** between different HR platforms
- **Scalable architecture** for adding new agents and workflows

---

## Quick Start

### Installation
```bash
# Ensure you're in the main PACT directory
cd /path/to/pact

# HR workflows are automatically loaded when running main server
python main_server.py
```

### Basic Usage
```bash
# Start a complete onboarding workflow
curl -X POST http://127.0.0.1:8000/hr/workflows/onboarding \
-H 'Content-Type: application/json' \
-d '{
  "employee_name": "Alice Johnson",
  "email": "alice.johnson@company.com", 
  "department": "Engineering",
  "start_date": "2025-09-01",
  "manager": "bob.smith@company.com",
  "position": "Senior Software Engineer",
  "salary": 125000
}'

# Check workflow progress
curl http://127.0.0.1:8000/hr/workflows/wf_onboarding_12345678/status

# Get sample demo data
curl http://127.0.0.1:8000/hr/demo-data
```

---

## Architecture

### Module Structure
```
hr_workflows/
├── __init__.py              # Package interface and exports
├── hr_capabilities.py       # Agent definitions and capabilities  
├── workflow_templates.py    # Workflow step definitions
├── hr_demo_data.py         # Sample data for testing
├── hr_coordinator.py       # Flask Blueprint with coordination logic
└── README.md               # This documentation
```

### Integration with Core PACT
- **Extends** core `/translate` and `/negotiate` endpoints
- **Leverages** existing capability matching logic
- **Uses** standard PACT message envelope format
- **Maintains** separation of concerns with Blueprint pattern

---

## Available Workflows

### 1. **Employee Onboarding** (`/hr/workflows/onboarding`)
**Complete new hire process coordination**
- **Steps**: 7 coordinated actions across 6 agents
- **Duration**: ~7 minutes estimated completion
- **Agents**: ATS → HRIS → IT → Payroll → Calendar → Notifications → Learning

**Required Parameters:**
```json
{
  "employee_name": "string",
  "email": "string", 
  "department": "string",
  "start_date": "YYYY-MM-DD",
  "manager": "string",
  "position": "string",
  "salary": "number"
}
```

### 2. **Performance Review** (`/hr/workflows/performance_review`)
**Quarterly review cycle coordination**
- **Steps**: 3 coordinated actions
- **Duration**: ~2.5 minutes estimated completion  
- **Agents**: Calendar → Notifications → HRIS

### 3. **Employee Offboarding** (`/hr/workflows/offboarding`)
**Complete departure process**
- **Steps**: 3 coordinated actions
- **Duration**: ~1.75 minutes estimated completion
- **Agents**: IT → HRIS → Notifications

### 4. **Employee Promotion** (`/hr/workflows/promotion`)
**Role change and promotion process**
- **Steps**: 4 coordinated actions
- **Duration**: ~4 minutes estimated completion
- **Agents**: HRIS → IT → Payroll → Notifications

---

## HR Agent Capabilities

### **ATS Agent** (Applicant Tracking System)
- `create_profile` - Create candidate profiles
- `update_status` - Update application status
- `schedule_interview` - Coordinate interview scheduling
- `search_candidates` - Find candidates by criteria
- `send_offer` - Send job offers

### **HRIS Agent** (Human Resource Information System)  
- `setup_employee` - Create employee records
- `update_records` - Modify employee data
- `generate_id` - Create employee IDs
- `enroll_benefits` - Benefits enrollment
- `create_org_chart` - Organizational structure

### **IT Agent** (Information Technology)
- `provision_access` - Create system access
- `create_accounts` - Set up user accounts
- `revoke_access` - Remove access rights
- `setup_hardware` - Equipment provisioning
- `configure_vpn` - VPN access setup

### **Calendar Agent** (Scheduling & Meetings)
- `schedule_onboarding` - First-day meetings
- `book_review_meetings` - Performance reviews
- `send_reminders` - Meeting reminders
- `block_time` - Reserve calendar time
- `schedule_training` - Training sessions

### **Notification Agent** (Communications)
- `send_welcome` - Welcome messages
- `notify_team` - Team notifications
- `send_reminder` - General reminders
- `email_blast` - Bulk communications
- `slack_notification` - Slack messages

### **Payroll Agent** (Compensation & Benefits)
- `setup_payroll` - Configure compensation
- `process_timesheet` - Time tracking
- `generate_paystub` - Pay documentation
- `handle_tax_forms` - Tax processing
- `setup_direct_deposit` - Banking setup

### **Learning Agent** (Training & Development)
- `assign_training` - Course assignments
- `track_progress` - Learning progress
- `generate_certificate` - Completion certificates
- `recommend_courses` - Personalized recommendations
- `schedule_mentoring` - Mentorship programs

---

## API Endpoints

### Workflow Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/hr/workflows/<type>` | POST | Execute complete workflow |
| `/hr/workflows/<id>/status` | GET | Check workflow progress |
| `/hr/workflows` | GET | List all workflows and status |

### Coordination & Capabilities
| Endpoint | Method | Description |
|----------|--------|-------------|  
| `/hr/coordinate` | POST | Single HR action coordination |
| `/hr/capabilities` | GET | All agent capabilities |
| `/hr/capabilities/<agent>` | GET | Specific agent capabilities |

### Demo & Testing
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/hr/demo-data` | GET | Sample test data |
| `/hr/demo-data/<workflow>` | GET | Workflow-specific samples |
| `/hr/health` | GET | Module health check |

---

## Examples

### Complete Onboarding Workflow
```bash
# Execute onboarding
curl -X POST http://127.0.0.1:8000/hr/workflows/onboarding \
-H 'Content-Type: application/json' \
-d '{
  "employee_name": "Carlos Rodriguez",
  "email": "carlos.rodriguez@company.com",
  "department": "Marketing", 
  "start_date": "2025-09-15",
  "manager": "sarah.chen@company.com",
  "position": "Marketing Manager",
  "salary": 95000
}'

# Response includes workflow_id for tracking
{
  "workflow_id": "wf_onboarding_a1b2c3d4",
  "status": "initiated",
  "total_steps": 7,
  "first_step_completed": {
    "step": 1,
    "agent": "ats_agent", 
    "result": "✅ Profile created for Carlos Rodriguez in ATS"
  },
  "tracking_url": "/hr/workflows/wf_onboarding_a1b2c3d4/status"
}
```

### Check Workflow Progress
```bash
curl http://127.0.0.1:8000/hr/workflows/wf_onboarding_a1b2c3d4/status

# Response shows real-time progress
{
  "workflow_id": "wf_onboarding_a1b2c3d4",
  "status": "in_progress",
  "progress": "57.1%",
  "completed_steps": [
    {"step": 1, "agent": "ats_agent", "result": "✅ Profile created"},
    {"step": 2, "agent": "hris_agent", "result": "✅ Employee ID EMP4A7B9C generated"},
    {"step": 3, "agent": "it_agent", "result": "✅ IT access provisioned"},
    {"step": 4, "agent": "payroll_agent", "result": "✅ Payroll configured: $95000 salary"}
  ],
  "pending_steps": [
    {"step": 5, "agent": "calendar_agent", "status": "queued"},
    {"step": 6, "agent": "notification_agent", "status": "queued"},
    {"step": 7, "agent": "learning_agent", "status": "queued"}
  ]
}
```

### Single Action Coordination
```bash
# Coordinate single HR action
curl -X POST http://127.0.0.1:8000/hr/coordinate \
-H 'Content-Type: application/json' \
-d '{
  "intent": "setup_employee",
  "parameters": {
    "employee_name": "Test Employee",
    "department": "Engineering"
  }
}'

# Response shows coordination result
{
  "coordination_id": "coord_x1y2z3w4",
  "matched_agent": "hris_agent",
  "action": "setup_employee", 
  "status": "partial",
  "success_rate": 0.5,
  "missing_params": ["start_date", "manager"]
}
```

---

## Testing & Development

### Get Demo Data
```bash
# All demo data
curl http://127.0.0.1:8000/hr/demo-data

# Specific workflow demo data
curl http://127.0.0.1:8000/hr/demo-data/onboarding
curl http://127.0.0.1:8000/hr/demo-data/performance_review
```

### Health Check
```bash
curl http://127.0.0.1:8000/hr/health

{
  "status": "healthy",
  "hr_module_version": "0.1.0",
  "available_workflows": 4,
  "available_agents": 7,
  "active_workflows": 3
}
```

### Adding New Workflows

1. **Define workflow steps** in `workflow_templates.py`:
```python
WORKFLOW_TEMPLATES["new_workflow"] = {
    "name": "New Process",
    "description": "Description here", 
    "steps": [
        # Define coordinated steps
    ]
}
```

2. **Add required parameters** to validation:
```python
# In validate_workflow_params function
"new_workflow": ["param1", "param2", "param3"]
```

3. **Add demo data** in `hr_demo_data.py`:
```python
"new_workflow_samples": [
    # Sample data objects
]
```

---

## Integration Notes

### PACT Core Dependency
- Requires core PACT server (`pact_cli_mock.py`) 
- Uses `match_capabilities()` function for agent matching
- Extends existing `/translate` and `/negotiate` logic

### Blueprint Registration
The HR module registers as a Flask Blueprint:
```python
from hr_workflows import hr_bp
app.register_blueprint(hr_bp)  # Adds /hr/* endpoints
```

### Error Handling
- **400**: Invalid parameters or workflow type
- **404**: Workflow/agent not found  
- **500**: Internal coordination errors

---

## Value Proposition

### For HR Teams
- **Automated coordination** across all HR systems
- **Reduced manual handoffs** between processes
- **Real-time visibility** into workflow progress
- **Standardized processes** regardless of underlying tools

### For IT Teams  
- **Vendor-neutral architecture** works with any HR system
- **Easy integration** using standard PACT protocols
- **Modular design** allows incremental adoption
- **Scalable infrastructure** handles enterprise volumes

### For Leadership
- **Faster onboarding** with coordinated automation
- **Consistent processes** across all departments  
- **Measurable improvements** in HR efficiency
- **Foundation for digital transformation**

---

## Roadmap

### Phase 1: Foundation (Current)
- ✅ 7 core HR agents with 30+ actions
- ✅ 4 complete workflow templates
- ✅ Real-time progress tracking
- ✅ Demo data and testing tools

### Phase 2: Enhancement (Next)
- 🎯 Custom workflow builder
- 🎯 Advanced dependency management
- 🎯 Integration with real HR systems
- 🎯 Workflow analytics and optimization

### Phase 3: Scale (Future)
- 🎯 Multi-tenant workflow management
- 🎯 AI-powered workflow optimization
- 🎯 Advanced reporting and insights
- 🎯 Enterprise security and compliance

---

## Contributing

### Adding New Agents
1. Define capabilities in `hr_capabilities.py`
2. Add priority level in `AGENT_PRIORITIES`
3. Create response templates in `hr_coordinator.py`
4. Add agent to demo data examples

### Creating New Workflows
1. Design step sequence in `workflow_templates.py`
2. Define parameter validation
3. Add demo data samples
4. Test with curl commands

### Testing
```bash
# Run health check
curl http://127.0.0.1:8000/hr/health

# Test all workflow types with demo data
curl http://127.0.0.1:8000/hr/demo-data | jq

# Validate agent capabilities
curl http://127.0.0.1:8000/hr/capabilities
```

---

## Support

### Issues & Questions
- Check server status: `curl http://127.0.0.1:8000/status`  
- Review logs for coordination errors
- Validate JSON request formats
- Ensure all required parameters provided

### Common Solutions
- **"Workflow not found"**: Check available workflows at `/hr/workflows`
- **"Missing parameters"**: Use demo data endpoints for valid examples
- **"Agent not found"**: Review capabilities at `/hr/capabilities`

---

**Built with ❤️ by NeuroBloom.ai**  
*Making HR coordination inevitable, not innovative.*
