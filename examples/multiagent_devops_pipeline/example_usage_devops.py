#!/usr/bin/env python3
"""
PACT DevOps Pipeline - Example Usage

This script demonstrates how to use the PACT DevOps Pipeline for various
deployment scenarios including basic usage, production deployment, and
monitoring pipeline execution.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any

from core_pipeline_orchestrator import PACTDevOpsPipeline
from agent_implementations import (
    CodeAgent, TestAgent, SecurityAgent, 
    DeployAgent, MonitorAgent, NotifyAgent
)
from pipeline_configs import PIPELINE_CONFIGS, apply_environment_overrides


async def setup_pipeline_orchestrator() -> PACTDevOpsPipeline:
    """Initialize and configure the pipeline orchestrator"""
    
    print("🔧 Setting up PACT DevOps Pipeline...")
    
    # Initialize orchestrator
    orchestrator = PACTDevOpsPipeline(redis_url="redis://localhost:6379")
    await orchestrator.initialize()
    
    # Register all agents
    agents = [
        CodeAgent(),
        TestAgent(), 
        SecurityAgent(),
        DeployAgent(),
        MonitorAgent(),
        NotifyAgent()
    ]
    
    for agent in agents:
        orchestrator.register_agent(agent)
        print(f"   ✅ Registered agent: {agent.name}")
    
    # Register pipeline configurations
    for config_name, config in PIPELINE_CONFIGS.items():
        orchestrator.register_pipeline_config(config_name, config)
        print(f"   ✅ Registered config: {config_name}")
    
    print("✅ Pipeline orchestrator setup complete!\n")
    return orchestrator


async def example_basic_deployment(orchestrator: PACTDevOpsPipeline):
    """Example: Basic deployment pipeline"""
    
    print("📦 Example 1: Basic Deployment Pipeline")
    print("=" * 50)
    
    # Simulate a git push event
    trigger_event = {
        "repository": "company/awesome-web-app",
        "branch": "feature/user-authentication",
        "commit_hash": "abc123def456789",
        "author": "developer@company.com",
        "environment": "staging",
        "metadata": {
            "commit_message": "Add user authentication system",
            "files_changed": ["src/auth.py", "tests/test_auth.py"],
            "triggered_via": "example_script"
        }
    }
    
    print(f"🚀 Triggering pipeline for: {trigger_event['repository']}")
    print(f"   Branch: {trigger_event['branch']}")
    print(f"   Commit: {trigger_event['commit_hash'][:8]}...")
    print(f"   Environment: {trigger_event['environment']}")
    
    start_time = time.time()
    
    try:
        # Execute default pipeline
        pipeline_id = await orchestrator.execute_pipeline(trigger_event, "default")
        
        execution_time = time.time() - start_time
        print(f"✅ Pipeline completed successfully!")
        print(f"   Pipeline ID: {pipeline_id}")
        print(f"   Execution time: {execution_time:.2f} seconds")
        
        # Get final pipeline status
        status = await orchestrator.get_pipeline_status(pipeline_id)
        if status:
            print(f"   Final status: {status.get('status')}")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {str(e)}")
    
    print()


async def example_production_deployment(orchestrator: PACTDevOpsPipeline):
    """Example: Production deployment with comprehensive checks"""
    
    print("🏭 Example 2: Production Deployment Pipeline")
    print("=" * 50)
    
    # Production deployment event
    trigger_event = {
        "repository": "company/awesome-web-app",
        "branch": "main",
        "commit_hash": "def456abc789123",
        "author": "senior-dev@company.com", 
        "environment": "production",
        "metadata": {
            "commit_message": "Release v2.1.0 - Performance improvements",
            "release_version": "v2.1.0",
            "approval_required": True,
            "triggered_via": "example_script"
        }
    }
    
    print(f"🚀 Triggering PRODUCTION pipeline for: {trigger_event['repository']}")
    print(f"   Branch: {trigger_event['branch']}")
    print(f"   Version: {trigger_event['metadata']['release_version']}")
    print(f"   Environment: {trigger_event['environment']}")
    
    start_time = time.time()
    
    try:
        # Execute production pipeline with comprehensive checks
        pipeline_id = await orchestrator.execute_pipeline(trigger_event, "production")
        
        execution_time = time.time() - start_time
        print(f"✅ Production pipeline completed!")
        print(f"   Pipeline ID: {pipeline_id}")
        print(f"   Execution time: {execution_time:.2f} seconds")
        
    except Exception as e:
        print(f"❌ Production pipeline failed: {str(e)}")
    
    print()


async def example_microservice_deployment(orchestrator: PACTDevOpsPipeline):
    """Example: Fast microservice deployment"""
    
    print("⚡ Example 3: Microservice Deployment Pipeline")
    print("=" * 50)
    
    # Microservice deployment event
    trigger_event = {
        "repository": "company/payment-service",
        "branch": "hotfix/payment-timeout-fix",
        "commit_hash": "789abc123def456",
        "author": "devops@company.com",
        "environment": "staging",
        "metadata": {
            "service_type": "microservice",
            "deployment_strategy": "rolling",
            "triggered_via": "example_script"
        }
    }
    
    print(f"🚀 Triggering microservice pipeline for: {trigger_event['repository']}")
    print(f"   Branch: {trigger_event['branch']}")
    print(f"   Service: Payment Service")
    print(f"   Strategy: Rolling deployment")
    
    start_time = time.time()
    
    try:
        # Execute microservice pipeline (faster, lightweight)
        pipeline_id = await orchestrator.execute_pipeline(trigger_event, "microservice")
        
        execution_time = time.time() - start_time
        print(f"✅ Microservice pipeline completed!")
        print(f"   Pipeline ID: {pipeline_id}")
        print(f"   Execution time: {execution_time:.2f} seconds")
        
    except Exception as e:
        print(f"❌ Microservice pipeline failed: {str(e)}")
    
    print()


async def example_ml_model_deployment(orchestrator: PACTDevOpsPipeline):
    """Example: ML model deployment with A/B testing"""
    
    print("🤖 Example 4: ML Model Deployment Pipeline")
    print("=" * 50)
    
    # ML model deployment event
    trigger_event = {
        "repository": "company/recommendation-model",
        "branch": "model/v3.2-improved-accuracy",
        "commit_hash": "456def789abc123",
        "author": "ml-engineer@company.com",
        "environment": "staging",
        "metadata": {
            "model_type": "recommendation_engine",
            "model_version": "v3.2",
            "accuracy_improvement": "2.3%",
            "a_b_testing": True,
            "triggered_via": "example_script"
        }
    }
    
    print(f"🚀 Triggering ML model pipeline for: {trigger_event['repository']}")
    print(f"   Model: Recommendation Engine v3.2")
    print(f"   Improvement: +2.3% accuracy")
    print(f"   A/B Testing: Enabled")
    
    start_time = time.time()
    
    try:
        # Execute ML model pipeline
        pipeline_id = await orchestrator.execute_pipeline(trigger_event, "ml_model")
        
        execution_time = time.time() - start_time
        print(f"✅ ML model pipeline completed!")
        print(f"   Pipeline ID: {pipeline_id}")
        print(f"   Execution time: {execution_time:.2f} seconds")
        
    except Exception as e:
        print(f"❌ ML model pipeline failed: {str(e)}")
    
    print()


async def example_emergency_hotfix(orchestrator: PACTDevOpsPipeline):
    """Example: Emergency hotfix deployment"""
    
    print("🚨 Example 5: Emergency Hotfix Deployment")
    print("=" * 50)
    
    # Emergency hotfix event
    trigger_event = {
        "repository": "company/payment-service",
        "branch": "hotfix/critical-security-fix",
        "commit_hash": "emergency123456",
        "author": "security-team@company.com",
        "environment": "production",
        "metadata": {
            "priority": "critical",
            "security_fix": True,
            "bypass_staging": True,
            "incident_id": "INC-2024-001",
            "triggered_via": "example_script"
        }
    }
    
    print(f"🚨 EMERGENCY: Triggering hotfix pipeline for: {trigger_event['repository']}")
    print(f"   Branch: {trigger_event['branch']}")
    print(f"   Priority: CRITICAL")
    print(f"   Direct to production: YES")
    
    start_time = time.time()
    
    try:
        # Execute emergency hotfix pipeline (minimal checks, fast deployment)
        pipeline_id = await orchestrator.execute_pipeline(trigger_event, "hotfix")
        
        execution_time = time.time() - start_time
        print(f"✅ Emergency hotfix deployed!")
        print(f"   Pipeline ID: {pipeline_id}")
        print(f"   Execution time: {execution_time:.2f} seconds")
        
    except Exception as e:
        print(f"❌ Emergency hotfix failed: {str(e)}")
    
    print()


async def example_monitoring_pipeline_execution(orchestrator: PACTDevOpsPipeline):
    """Example: Real-time pipeline monitoring"""
    
    print("📊 Example 6: Pipeline Monitoring & Management")
    print("=" * 50)
    
    # Start a pipeline in the background
    trigger_event = {
        "repository": "company/monitoring-demo",
        "branch": "main",
        "commit_hash": "monitor123456",
        "author": "demo@company.com",
        "environment": "staging",
        "metadata": {"demo": True}
    }
    
    print("🚀 Starting pipeline for monitoring demo...")
    
    # Execute pipeline without waiting
    pipeline_task = asyncio.create_task(
        orchestrator.execute_pipeline(trigger_event, "default")
    )
    
    # Monitor pipeline execution
    print("📊 Monitoring pipeline execution...")
    
    for i in range(10):
        # List active pipelines
        active_pipelines = await orchestrator.list_active_pipelines()
        print(f"   Active pipelines: {len(active_pipelines)}")
        
        if active_pipelines:
            for pipeline_id in active_pipelines[:3]:  # Show first 3
                status = await orchestrator.get_pipeline_status(pipeline_id)
                if status:
                    context = json.loads(status.get("context", "{}"))
                    print(f"     {pipeline_id}: {status.get('status')} - {context.get('repository', 'unknown')}")
        
        await asyncio.sleep(2)  # Check every 2 seconds
        
        # Check if our demo pipeline completed
        if pipeline_task.done():
            break
    
    # Wait for completion
    try:
        pipeline_id = await pipeline_task
        print(f"✅ Monitoring demo completed: {pipeline_id}")
    except Exception as e:
        print(f"❌ Monitoring demo failed: {str(e)}")
    
    print()


async def example_environment_specific_configs(orchestrator: PACTDevOpsPipeline):
    """Example: Environment-specific configuration overrides"""
    
    print("🌍 Example 7: Environment-Specific Configurations")
    print("=" * 50)
    
    # Show how configs change based on environment
    base_config = PIPELINE_CONFIGS["default"]
    
    environments = ["development", "staging", "production"]
    
    for env in environments:
        print(f"📋 Configuration for {env.upper()} environment:")
        
        # Apply environment overrides
        env_config = apply_environment_overrides(base_config, env)
        
        print(f"   Timeout: {env_config.get('timeout_minutes', 'default')} minutes")
        
        # Look for quality thresholds in actions
        for stage in env_config.get("stages", []):
            for action in stage.get("actions", []):
                if action.get("action") == "code.check_quality":
                    threshold = action.get("params", {}).get("quality_threshold", "default")
                    print(f"   Quality threshold: {threshold}")
                    break
        
        print()


async def demonstrate_agent_capabilities():
    """Demonstrate individual agent capabilities"""
    
    print("🤖 Example 8: Individual Agent Capabilities")
    print("=" * 50)
    
    # Create agents
    agents = {
        "code": CodeAgent(),
        "test": TestAgent(),
        "security": SecurityAgent(),
        "deploy": DeployAgent(),
        "monitor": MonitorAgent(),
        "notify": NotifyAgent()
    }
    
    # Test parameters
    test_params = {
        "pipeline_id": "demo_pipeline",
        "repository": "company/demo-app",
        "branch": "main",
        "commit_hash": "demo123456",
        "environment": "staging"
    }
    
    # Demonstrate each agent
    for agent_name, agent in agents.items():
        print(f"🔧 Testing {agent_name.upper()} Agent:")
        
        # Get agent's supported actions (this would be defined in each agent)
        sample_actions = {
            "code": "code.analyze_changes",
            "test": "tests.run_unit", 
            "security": "security.scan_vulnerabilities",
            "deploy": "deploy.to_staging",
            "monitor": "monitor.check_health",
            "notify": "notify.slack_team"
        }
        
        action = sample_actions.get(agent_name)
        if action:
            try:
                result = await agent.execute_pact_action(action, test_params)
                success = result.get("success", False)
                status = "✅ SUCCESS" if success else "⚠️  PARTIAL"
                print(f"   {action}: {status}")
                
                # Show some result details
                if "duration_ms" in result:
                    print(f"     Duration: {result['duration_ms']}ms")
                if "test_results" in result:
                    tests = result["test_results"]
                    print(f"     Tests: {tests.get('tests_passed', 0)}/{tests.get('tests_run', 0)} passed")
                if "deployment" in result:
                    deployment = result["deployment"]
                    print(f"     Deployed to: {deployment.get('environment', 'unknown')}")
                
            except Exception as e:
                print(f"   {action}: ❌ FAILED - {str(e)}")
        
        print()


async def main():
    """Run all examples"""
    
    print("🚀 PACT DevOps Pipeline - Comprehensive Examples")
    print("=" * 60)
    print()
    
    try:
        # Setup
        orchestrator = await setup_pipeline_orchestrator()
        
        # Run examples
        await example_basic_deployment(orchestrator)
        await example_production_deployment(orchestrator)
        await example_microservice_deployment(orchestrator)
        await example_ml_model_deployment(orchestrator)
        await example_emergency_hotfix(orchestrator)
        await example_monitoring_pipeline_execution(orchestrator)
        await example_environment_specific_configs(orchestrator)
        await demonstrate_agent_capabilities()
        
        print("🎉 All examples completed successfully!")
        print("=" * 60)
        print()
        print("💡 Next steps:")
        print("   • Start the web server: python devops_web_server.py")
        print("   • Set up webhooks with your Git provider")
        print("   • Configure monitoring and alerting")
        print("   • Customize pipeline configurations for your needs")
        print("   • Deploy to production with proper Redis/database setup")
        
        # Cleanup
        await orchestrator.shutdown()
        
    except Exception as e:
        print(f"❌ Example execution failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
