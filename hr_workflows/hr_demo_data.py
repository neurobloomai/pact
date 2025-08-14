# hr_workflows/hr_demo_data.py
"""
Demo data for HR workflow testing
Provides realistic sample data for all workflow types
"""

from datetime import datetime, timedelta

def get_demo_data():
    """Get comprehensive demo data for HR workflows"""
    return {
        "onboarding_samples": [
            {
                "employee_name": "Alice Johnson",
                "email": "alice.johnson@company.com",
                "department": "Engineering",
                "start_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                "manager": "bob.smith@company.com",
                "position": "Senior Software Engineer",
                "salary": 125000,
                "location": "Remote"
            },
            {
                "employee_name": "Carlos Rodriguez",
                "email": "carlos.rodriguez@company.com", 
                "department": "Marketing",
                "start_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
                "manager": "sarah.chen@company.com",
                "position": "Marketing Manager",
                "salary": 95000,
                "location": "New York Office"
            },
            {
                "employee_name": "Priya Patel",
                "email": "priya.patel@company.com",
                "department": "Data Science", 
                "start_date": (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),
                "manager": "david.kim@company.com",
                "position": "Senior Data Scientist",
                "salary": 140000,
                "location": "San Francisco Office"
            }
        ],
        
        "performance_review_samples": [
            {
                "employee_id": "EMP001",
                "employee_name": "John Smith",
                "reviewer": "manager@company.com",
                "review_cycle": "Q3_2025",
                "department": "Engineering",
                "review_type": "quarterly"
            },
            {
                "employee_id": "EMP002", 
                "employee_name": "Lisa Wang",
                "reviewer": "director@company.com",
                "review_cycle": "Q3_2025",
                "department": "Product",
                "review_type": "quarterly"
            }
        ],
        
        "offboarding_samples": [
            {
                "employee_id": "EMP003",
                "employee_name": "Mike Chen",
                "last_day": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
                "reason": "resignation",
                "department": "Sales",
                "manager": "sales.manager@company.com"
            },
            {
                "employee_id": "EMP004",
                "employee_name": "Jennifer Adams", 
                "last_day": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                "reason": "relocation",
                "department": "HR",
                "manager": "hr.director@company.com"
            }
        ],
        
        "promotion_samples": [
            {
                "employee_id": "EMP005",
                "employee_name": "Alex Thompson",
                "current_title": "Software Engineer",
                "new_title": "Senior Software Engineer",
                "current_salary": 95000,
                "new_salary": 115000,
                "new_department": "Engineering",
                "effective_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                "manager": "engineering.manager@company.com"
            }
        ]
    }

def get_sample_for_workflow(workflow_type):
    """Get sample data for a specific workflow type"""
    demo_data = get_demo_data()
    
    workflow_mapping = {
        "onboarding": demo_data["onboarding_samples"][0],
        "performance_review": demo_data["performance_review_samples"][0], 
        "offboarding": demo_data["offboarding_samples"][0],
        "promotion": demo_data["promotion_samples"][0]
    }
    
    return workflow_mapping.get(workflow_type)

def get_test_scenarios():
    """Get test scenarios for different workflow conditions"""
    return {
        "success_scenarios": {
            "complete_onboarding": {
                "description": "All required parameters provided",
                "data": get_sample_for_workflow("onboarding"),
                "expected_result": "All 7 steps should execute successfully"
            },
            "standard_review": {
                "description": "Standard quarterly performance review",
                "data": get_sample_for_workflow("performance_review"),
                "expected_result": "3 coordination steps completed"
            }
        },
        
        "partial_scenarios": {
            "incomplete_onboarding": {
                "description": "Missing salary information",
                "data": {
                    "employee_name": "Test Employee",
                    "department": "Engineering",
                    "start_date": "2025-09-01",
                    "manager": "test.manager@company.com"
                    # Missing email, position, salary
                },
                "expected_result": "Should identify missing parameters"
            }
        },
        
        "error_scenarios": {
            "invalid_workflow": {
                "description": "Request for non-existent workflow",
                "data": {"workflow_type": "nonexistent"},
                "expected_result": "Should return 400 error with available workflows"
            }
        }
    }

def get_curl_examples():
    """Get curl command examples for testing"""
    base_url = "http://127.0.0.1:8000"
    
    return {
        "onboarding_workflow": f"""
curl -X POST {base_url}/hr/workflows/onboarding \\
-H 'Content-Type: application/json' \\
-d '{{"employee_name": "Alice Johnson", "email": "alice.johnson@company.com", "department": "Engineering", "start_date": "2025-09-01", "manager": "bob.smith@company.com", "position": "Senior Software Engineer", "salary": 125000}}'
        """.strip(),
        
        "workflow_status": f"""
curl {base_url}/hr/workflows/wf_onboarding_12345678/status
        """.strip(),
        
        "list_workflows": f"""
curl {base_url}/hr/workflows
        """.strip(),
        
        "demo_data": f"""
curl {base_url}/hr/demo-data
        """.strip()
    }
