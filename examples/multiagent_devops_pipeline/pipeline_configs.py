#!/usr/bin/env python3
"""
PACT DevOps Pipeline - Configuration Files

This module contains various pipeline configurations for different project types
and deployment scenarios.
"""

# Default pipeline configuration
DEFAULT_PIPELINE_CONFIG = {
    "name": "default",
    "description": "Standard web application deployment pipeline",
    "timeout_minutes": 30,
    "stages": [
        {
            "name": "code_analysis",
            "description": "Code quality and syntax validation",
            "parallel": True,
            "halt_on_failure": True,
            "timeout_minutes": 10,
            "actions": [
                {
                    "agent": "code",
                    "action": "code.analyze_changes",
                    "halt_on_failure": False
                },
                {
                    "agent": "code", 
                    "action": "code.check_quality",
                    "halt_on_failure": True,
                        "deployment_type": "cdn",
                        "build_command": "npm run build",
                        "dist_folder": "dist/"
                    }
                },
                {
                    "agent": "monitor",
                    "action": "monitor.check_health",
                    "halt_on_failure": True,
                    "params": {
                        "environment": "staging",
                        "health_endpoints": ["/health", "/api/status"]
                    }
                }
            ]
        },
        {
            "name": "performance_validation",
            "description": "Frontend performance checks",
            "parallel": True,
            "halt_on_failure": False,
            "timeout_minutes": 5,
            "actions": [
                {
                    "agent": "test",
                    "action": "tests.run_performance",
                    "halt_on_failure": False,
                    "params": {
                        "lighthouse_audit": True,
                        "performance_budget": {
                            "first_contentful_paint": 2000,
                            "largest_contentful_paint": 4000
                        }
                    }
                },
                {
                    "agent": "notify",
                    "action": "notify.slack_team",
                    "halt_on_failure": False
                }
            ]
        }
    ]
}

# Machine Learning pipeline configuration
ML_PIPELINE_CONFIG = {
    "name": "ml_model",
    "description": "Machine learning model deployment pipeline",
    "timeout_minutes": 60,
    "stages": [
        {
            "name": "data_validation",
            "description": "Data quality and model validation",
            "parallel": True,
            "halt_on_failure": True,
            "timeout_minutes": 15,
            "actions": [
                {
                    "agent": "code",
                    "action": "code.analyze_changes",
                    "halt_on_failure": True
                },
                {
                    "agent": "test",
                    "action": "tests.run_unit",
                    "halt_on_failure": True,
                    "params": {
                        "test_type": "model_validation",
                        "data_quality_checks": True
                    }
                }
            ]
        },
        {
            "name": "model_testing",
            "description": "Model performance and accuracy testing",
            "parallel": False,
            "halt_on_failure": True,
            "timeout_minutes": 25,
            "actions": [
                {
                    "agent": "test",
                    "action": "tests.run_integration",
                    "halt_on_failure": True,
                    "params": {
                        "model_performance_tests": True,
                        "accuracy_threshold": 0.85,
                        "bias_detection": True
                    }
                },
                {
                    "agent": "test",
                    "action": "tests.run_performance",
                    "halt_on_failure": True,
                    "params": {
                        "inference_latency_threshold": 100,
                        "throughput_threshold": 1000
                    }
                }
            ]
        },
        {
            "name": "model_deployment",
            "description": "Model deployment with A/B testing",
            "parallel": False,
            "halt_on_failure": True,
            "timeout_minutes": 20,
            "actions": [
                {
                    "agent": "deploy",
                    "action": "deploy.canary_release",
                    "halt_on_failure": True,
                    "params": {
                        "traffic_percentage": 10,
                        "model_version_comparison": True
                    }
                },
                {
                    "agent": "monitor",
                    "action": "monitor.track_metrics",
                    "halt_on_failure": True,
                    "params": {
                        "ml_metrics": ["accuracy", "precision", "recall", "f1_score"],
                        "business_metrics": ["conversion_rate", "revenue_impact"]
                    }
                }
            ]
        }
    ]
}

# Emergency hotfix pipeline
HOTFIX_PIPELINE_CONFIG = {
    "name": "hotfix",
    "description": "Emergency hotfix deployment with minimal checks",
    "timeout_minutes": 10,
    "stages": [
        {
            "name": "critical_validation",
            "description": "Essential validation only",
            "parallel": True,
            "halt_on_failure": True,
            "timeout_minutes": 3,
            "actions": [
                {
                    "agent": "code",
                    "action": "code.validate_syntax",
                    "halt_on_failure": True
                },
                {
                    "agent": "security",
                    "action": "security.validate_secrets",
                    "halt_on_failure": True
                }
            ]
        },
        {
            "name": "minimal_testing",
            "description": "Core functionality tests only",
            "parallel": False,
            "halt_on_failure": True,
            "timeout_minutes": 4,
            "actions": [
                {
                    "agent": "test",
                    "action": "tests.run_unit",
                    "halt_on_failure": True,
                    "params": {
                        "test_filter": "critical_only",
                        "coverage_threshold": 70.0
                    }
                }
            ]
        },
        {
            "name": "emergency_deployment",
            "description": "Direct production deployment",
            "parallel": False,
            "halt_on_failure": True,
            "timeout_minutes": 5,
            "actions": [
                {
                    "agent": "deploy",
                    "action": "deploy.to_production",
                    "halt_on_failure": True,
                    "params": {
                        "skip_staging": True,
                        "deployment_strategy": "immediate"
                    }
                },
                {
                    "agent": "monitor",
                    "action": "monitor.check_health",
                    "halt_on_failure": True
                },
                {
                    "agent": "notify",
                    "action": "notify.slack_team",
                    "halt_on_failure": False,
                    "params": {
                        "urgency": "high",
                        "channel": "#incidents"
                    }
                }
            ]
        }
    ]
}

# Configuration registry
PIPELINE_CONFIGS = {
    "default": DEFAULT_PIPELINE_CONFIG,
    "production": PRODUCTION_PIPELINE_CONFIG,
    "microservice": MICROSERVICE_PIPELINE_CONFIG,
    "frontend": FRONTEND_PIPELINE_CONFIG,
    "ml_model": ML_PIPELINE_CONFIG,
    "hotfix": HOTFIX_PIPELINE_CONFIG
}

def get_pipeline_config(config_name: str) -> dict:
    """Get pipeline configuration by name"""
    return PIPELINE_CONFIGS.get(config_name, DEFAULT_PIPELINE_CONFIG)

def list_available_configs() -> list:
    """List all available pipeline configurations"""
    return list(PIPELINE_CONFIGS.keys())

def validate_pipeline_config(config: dict) -> tuple[bool, list]:
    """Validate a pipeline configuration"""
    errors = []
    
    # Required fields
    required_fields = ["name", "stages"]
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
    
    # Validate stages
    if "stages" in config:
        for i, stage in enumerate(config["stages"]):
            stage_errors = _validate_stage_config(stage, i)
            errors.extend(stage_errors)
    
    return len(errors) == 0, errors

def _validate_stage_config(stage: dict, stage_index: int) -> list:
    """Validate a single stage configuration"""
    errors = []
    
    # Required stage fields
    required_fields = ["name", "actions"]
    for field in required_fields:
        if field not in stage:
            errors.append(f"Stage {stage_index}: Missing required field '{field}'")
    
    # Validate actions
    if "actions" in stage:
        for j, action in enumerate(stage["actions"]):
            action_errors = _validate_action_config(action, stage_index, j)
            errors.extend(action_errors)
    
    return errors

def _validate_action_config(action: dict, stage_index: int, action_index: int) -> list:
    """Validate a single action configuration"""
    errors = []
    
    # Required action fields
    required_fields = ["agent", "action"]
    for field in required_fields:
        if field not in action:
            errors.append(f"Stage {stage_index}, Action {action_index}: Missing required field '{field}'")
    
    return errors

# Environment-specific overrides
ENVIRONMENT_OVERRIDES = {
    "development": {
        "timeout_minutes": 15,
        "quality_threshold": 6.0,
        "coverage_threshold": 70.0,
        "security_scan_level": "basic"
    },
    "staging": {
        "timeout_minutes": 25,
        "quality_threshold": 7.0,
        "coverage_threshold": 80.0,
        "security_scan_level": "standard"
    },
    "production": {
        "timeout_minutes": 45,
        "quality_threshold": 8.0,
        "coverage_threshold": 85.0,
        "security_scan_level": "comprehensive"
    }
}

def apply_environment_overrides(config: dict, environment: str) -> dict:
    """Apply environment-specific overrides to a pipeline configuration"""
    if environment not in ENVIRONMENT_OVERRIDES:
        return config
    
    overrides = ENVIRONMENT_OVERRIDES[environment]
    modified_config = config.copy()
    
    # Apply global overrides
    if "timeout_minutes" in overrides:
        modified_config["timeout_minutes"] = overrides["timeout_minutes"]
    
    # Apply overrides to actions
    for stage in modified_config.get("stages", []):
        for action in stage.get("actions", []):
            params = action.get("params", {})
            
            # Apply quality threshold overrides
            if "quality_threshold" in overrides and action.get("action") == "code.check_quality":
                params["quality_threshold"] = overrides["quality_threshold"]
            
            # Apply coverage threshold overrides
            if "coverage_threshold" in overrides and "coverage_threshold" in params:
                params["coverage_threshold"] = overrides["coverage_threshold"]
            
            # Apply security scan level overrides
            if "security_scan_level" in overrides and action.get("agent") == "security":
                params["scan_level"] = overrides["security_scan_level"]
            
            if params:
                action["params"] = params
    
    return modified_config"quality_threshold": 7.0
                    }
                },
                {
                    "agent": "code",
                    "action": "code.validate_syntax",
                    "halt_on_failure": True
                }
            ]
        },
        {
            "name": "security_scan",
            "description": "Security vulnerability scanning",
            "parallel": True,
            "halt_on_failure": True,
            "timeout_minutes": 8,
            "actions": [
                {
                    "agent": "security",
                    "action": "security.scan_vulnerabilities",
                    "halt_on_failure": True
                },
                {
                    "agent": "security",
                    "action": "security.check_dependencies",
                    "halt_on_failure": True
                },
                {
                    "agent": "security",
                    "action": "security.validate_secrets",
                    "halt_on_failure": True
                }
            ]
        },
        {
            "name": "testing",
            "description": "Automated testing execution",
            "parallel": False,
            "halt_on_failure": True,
            "timeout_minutes": 15,
            "actions": [
                {
                    "agent": "test",
                    "action": "tests.run_unit",
                    "halt_on_failure": True,
                    "params": {
                        "coverage_threshold": 80.0
                    }
                },
                {
                    "agent": "test",
                    "action": "tests.run_integration",
                    "halt_on_failure": True
                },
                {
                    "agent": "test",
                    "action": "tests.check_coverage",
                    "halt_on_failure": False
                }
            ]
        },
        {
            "name": "deployment",
            "description": "Application deployment",
            "parallel": False,
            "halt_on_failure": True,
            "timeout_minutes": 20,
            "actions": [
                {
                    "agent": "deploy",
                    "action": "deploy.to_staging",
                    "halt_on_failure": True
                },
                {
                    "agent": "monitor",
                    "action": "monitor.check_health",
                    "halt_on_failure": True,
                    "params": {
                        "environment": "staging"
                    }
                },
                {
                    "agent": "monitor",
                    "action": "monitor.setup_alerts",
                    "halt_on_failure": False,
                    "params": {
                        "environment": "staging"
                    }
                }
            ]
        },
        {
            "name": "notification",
            "description": "Team notifications and updates",
            "parallel": True,
            "halt_on_failure": False,
            "timeout_minutes": 5,
            "actions": [
                {
                    "agent": "notify",
                    "action": "notify.slack_team",
                    "halt_on_failure": False
                },
                {
                    "agent": "notify",
                    "action": "notify.update_jira",
                    "halt_on_failure": False
                }
            ]
        }
    ]
}

# Production deployment pipeline
PRODUCTION_PIPELINE_CONFIG = {
    "name": "production",
    "description": "Production deployment with comprehensive checks",
    "timeout_minutes": 45,
    "stages": [
        {
            "name": "pre_deployment_validation",
            "description": "Comprehensive pre-deployment validation",
            "parallel": True,
            "halt_on_failure": True,
            "timeout_minutes": 15,
            "actions": [
                {
                    "agent": "code",
                    "action": "code.analyze_changes",
                    "halt_on_failure": True
                },
                {
                    "agent": "code",
                    "action": "code.check_quality", 
                    "halt_on_failure": True,
                    "params": {
                        "quality_threshold": 8.0  # Higher threshold for prod
                    }
                },
                {
                    "agent": "security",
                    "action": "security.scan_vulnerabilities",
                    "halt_on_failure": True
                },
                {
                    "agent": "security",
                    "action": "security.check_dependencies",
                    "halt_on_failure": True
                },
                {
                    "agent": "security",
                    "action": "security.check_compliance",
                    "halt_on_failure": True
                }
            ]
        },
        {
            "name": "comprehensive_testing",
            "description": "Full test suite execution",
            "parallel": False,
            "halt_on_failure": True,
            "timeout_minutes": 25,
            "actions": [
                {
                    "agent": "test",
                    "action": "tests.run_unit",
                    "halt_on_failure": True,
                    "params": {
                        "coverage_threshold": 85.0  # Higher coverage for prod
                    }
                },
                {
                    "agent": "test",
                    "action": "tests.run_integration",
                    "halt_on_failure": True
                },
                {
                    "agent": "test",
                    "action": "tests.run_e2e",
                    "halt_on_failure": True
                },
                {
                    "agent": "test",
                    "action": "tests.run_performance",
                    "halt_on_failure": True
                }
            ]
        },
        {
            "name": "canary_deployment",
            "description": "Canary release validation",
            "parallel": False,
            "halt_on_failure": True,
            "timeout_minutes": 15,
            "actions": [
                {
                    "agent": "deploy",
                    "action": "deploy.canary_release",
                    "halt_on_failure": True,
                    "params": {
                        "traffic_percentage": 5,
                        "duration_minutes": 10
                    }
                },
                {
                    "agent": "monitor",
                    "action": "monitor.detect_anomalies",
                    "halt_on_failure": True,
                    "params": {
                        "environment": "production-canary"
                    }
                }
            ]
        },
        {
            "name": "production_deployment", 
            "description": "Full production deployment",
            "parallel": False,
            "halt_on_failure": True,
            "timeout_minutes": 20,
            "actions": [
                {
                    "agent": "deploy",
                    "action": "deploy.to_production",
                    "halt_on_failure": True
                },
                {
                    "agent": "monitor",
                    "action": "monitor.check_health",
                    "halt_on_failure": True,
                    "params": {
                        "environment": "production"
                    }
                },
                {
                    "agent": "monitor",
                    "action": "monitor.setup_alerts",
                    "halt_on_failure": False,
                    "params": {
                        "environment": "production"
                    }
                }
            ]
        },
        {
            "name": "post_deployment",
            "description": "Post-deployment verification and notification",
            "parallel": True,
            "halt_on_failure": False,
            "timeout_minutes": 10,
            "actions": [
                {
                    "agent": "monitor",
                    "action": "monitor.track_metrics",
                    "halt_on_failure": False,
                    "params": {
                        "environment": "production"
                    }
                },
                {
                    "agent": "notify",
                    "action": "notify.deployment_success",
                    "halt_on_failure": False
                },
                {
                    "agent": "notify",
                    "action": "notify.email_stakeholders",
                    "halt_on_failure": False
                }
            ]
        }
    ]
}

# Microservice pipeline configuration
MICROSERVICE_PIPELINE_CONFIG = {
    "name": "microservice",
    "description": "Lightweight pipeline for microservice deployment",
    "timeout_minutes": 20,
    "stages": [
        {
            "name": "quick_validation",
            "description": "Fast validation checks",
            "parallel": True,
            "halt_on_failure": True,
            "timeout_minutes": 5,
            "actions": [
                {
                    "agent": "code",
                    "action": "code.validate_syntax",
                    "halt_on_failure": True
                },
                {
                    "agent": "security",
                    "action": "security.validate_secrets",
                    "halt_on_failure": True
                }
            ]
        },
        {
            "name": "container_testing",
            "description": "Container-focused testing",
            "parallel": False,
            "halt_on_failure": True,
            "timeout_minutes": 10,
            "actions": [
                {
                    "agent": "test",
                    "action": "tests.run_unit",
                    "halt_on_failure": True,
                    "params": {
                        "coverage_threshold": 75.0
                    }
                },
                {
                    "agent": "security",
                    "action": "security.scan_containers",
                    "halt_on_failure": True
                }
            ]
        },
        {
            "name": "rolling_deployment",
            "description": "Rolling deployment with health checks",
            "parallel": False,
            "halt_on_failure": True,
            "timeout_minutes": 8,
            "actions": [
                {
                    "agent": "deploy",
                    "action": "deploy.to_staging",
                    "halt_on_failure": True
                },
                {
                    "agent": "monitor",
                    "action": "monitor.check_health",
                    "halt_on_failure": True
                }
            ]
        },
        {
            "name": "notification",
            "description": "Quick notification",
            "parallel": False,
            "halt_on_failure": False,
            "timeout_minutes": 2,
            "actions": [
                {
                    "agent": "notify",
                    "action": "notify.slack_team",
                    "halt_on_failure": False
                }
            ]
        }
    ]
}

# Frontend application pipeline
FRONTEND_PIPELINE_CONFIG = {
    "name": "frontend",
    "description": "Frontend application deployment pipeline",
    "timeout_minutes": 25,
    "stages": [
        {
            "name": "code_quality",
            "description": "Frontend code quality checks",
            "parallel": True,
            "halt_on_failure": True,
            "timeout_minutes": 8,
            "actions": [
                {
                    "agent": "code",
                    "action": "code.check_quality",
                    "halt_on_failure": True,
                    "params": {
                        "quality_threshold": 7.5,
                        "linting_rules": "strict"
                    }
                },
                {
                    "agent": "security",
                    "action": "security.check_dependencies",
                    "halt_on_failure": True
                }
            ]
        },
        {
            "name": "frontend_testing",
            "description": "Frontend-specific testing",
            "parallel": False,
            "halt_on_failure": True,
            "timeout_minutes": 12,
            "actions": [
                {
                    "agent": "test",
                    "action": "tests.run_unit",
                    "halt_on_failure": True,
                    "params": {
                        "test_framework": "jest",
                        "coverage_threshold": 80.0
                    }
                },
                {
                    "agent": "test",
                    "action": "tests.run_e2e",
                    "halt_on_failure": True,
                    "params": {
                        "browsers": ["chrome", "firefox", "safari"],
                        "devices": ["desktop", "mobile"]
                    }
                }
            ]
        },
        {
            "name": "build_and_deploy",
            "description": "Build and CDN deployment",
            "parallel": False,
            "halt_on_failure": True,
            "timeout_minutes": 10,
            "actions": [
                {
                    "agent": "deploy",
                    "action": "deploy.to_staging",
                    "halt_on_failure": True,
                    "params": {
