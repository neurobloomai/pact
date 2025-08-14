# main_server.py
"""
Main PACT server with HR workflow integration
Combines core PACT protocol with HR workflow extensions
"""

import sys
import os
from flask import Flask, request, jsonify

# Import core PACT functionality
from pact_cli_mock import app as pact_app, match_capabilities

# Import HR workflow module
try:
    from hr_workflows import hr_bp
    hr_workflows_available = True
    print("✅ HR Workflows module loaded successfully")
except ImportError as e:
    hr_workflows_available = False
    print(f"⚠️  HR Workflows module not available: {e}")

def create_integrated_server():
    """Create integrated PACT server with HR workflows"""
    
    # Use the existing PACT app as base
    app = pact_app
    
    # Register HR workflow blueprint if available
    if hr_workflows_available:
        app.register_blueprint(hr_bp)
        print("🏢 HR Workflows registered at /hr/*")
    
    # Add integration status endpoint
    @app.route("/status", methods=["GET"])
    def server_status():
        return jsonify({
            "server": "PACT Protocol Server",
            "version": "0.2.0",
            "core_pact": "✅ Available",
            "hr_workflows": "✅ Available" if hr_workflows_available else "❌ Not Available",
            "endpoints": {
                "core_pact": {
                    "translate": "/translate",
                    "negotiate": "/negotiate",
                    "root": "/"
                },
                "hr_workflows": {
                    "coordinate": "/hr/coordinate",
                    "workflows": "/hr/workflows/<type>",
                    "status": "/hr/workflows/<id>/status",
                    "capabilities": "/hr/capabilities",
                    "demo_data": "/hr/demo-data",
                    "health": "/hr/health"
                } if hr_workflows_available else "Not Available"
            },
            "usage": {
                "core_pact": "Agent interoperability and intent translation",
                "hr_workflows": "Complete HR process automation and coordination"
            }
        })
    
    # Add comprehensive demo endpoint
    @app.route("/demo", methods=["GET"])
    def demo_commands():
        base_url = "http://127.0.0.1:8000"
        
        commands = {
            "core_pact_examples": {
                "translate_intent": f"""
curl -X POST {base_url}/translate \\
-H 'Content-Type: application/json' \\
-d '{{"sender": {{"platform": "Dialogflow"}}, "recipient": {{"platform": "Rasa"}}, "payload": {{"intent": "check_order_status", "entities": {{"order_id": "A123456"}}, "text": "Where is my order?"}}}}'
                """.strip(),
                
                "negotiate_capability": f"""
curl -X POST {base_url}/negotiate \\
-H 'Content-Type: application/json' \\
-d '{{"action": "create", "parameters": {{"title": "Demo Meeting", "start_time": "2025-08-12T10:00:00Z", "participants": ["alice", "bob"]}}}}'
                """.strip()
            }
        }
        
        if hr_workflows_available:
            commands["hr_workflow_examples"] = {
                "onboarding_workflow": f"""
curl -X POST {base_url}/hr/workflows/onboarding \\
-H 'Content-Type: application/json' \\
-d '{{"employee_name": "Alice Johnson", "email": "alice.johnson@company.com", "department": "Engineering", "start_date": "2025-09-01", "manager": "bob.smith@company.com", "position": "Senior Software Engineer", "salary": 125000}}'
                """.strip(),
                
                "workflow_status": f"""
curl {base_url}/hr/workflows/wf_onboarding_12345678/status
                """.strip(),
                
                "hr_capabilities": f"""
curl {base_url}/hr/capabilities
                """.strip(),
                
                "hr_demo_data": f"""
curl {base_url}/hr/demo-data
                """.strip()
            }
        
        return jsonify({
            "demo_commands": commands,
            "instructions": {
                "1": "Start the server: python main_server.py",
                "2": "Test core PACT: Use translate/negotiate examples",
                "3": "Test HR workflows: Use onboarding/status examples", 
                "4": "Check server status: curl http://127.0.0.1:8000/status"
            }
        })
    
    return app

if __name__ == "__main__":
    print("🚀 Starting Integrated PACT Server")
    print("=" * 50)
    print("🔗 Core PACT Protocol: ✅ Loaded")
    
    if hr_workflows_available:
        print("🏢 HR Workflows: ✅ Loaded")
        print("📋 Available HR endpoints:")
        print("   • POST /hr/coordinate - Single HR action")
        print("   • POST /hr/workflows/<type> - Complete workflow")
        print("   • GET  /hr/workflows/<id>/status - Status check")
        print("   • GET  /hr/capabilities - Agent capabilities")
        print("   • GET  /hr/demo-data - Sample test data")
    else:
        print("🏢 HR Workflows: ❌ Not Available")
    
    print("=" * 50)
    print("🌐 Server starting on http://127.0.0.1:8000")
    print("📖 Demo commands: curl http://127.0.0.1:8000/demo")
    print("📊 Server status: curl http://127.0.0.1:8000/status")
    
    app = create_integrated_server()
    app.run(debug=True, port=8000)
