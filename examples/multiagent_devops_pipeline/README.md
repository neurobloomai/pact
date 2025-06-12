# PACT DevOps Pipeline

Multi-agent DevOps orchestration using the PACT protocol for intelligent, coordinated deployments.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/neurobloomai/pact
cd pact/examples/devops_pipeline

# Install dependencies
pip install -r requirements.txt

# Start with Docker (recommended)
docker-compose up -d

# Or run locally
python example_usage_devops.py
```

## 📁 File Structure

```
devops_pipeline/
├── requirements.txt                 # Python dependencies
├── core_pipeline_orchestrator.py    # Main orchestration engine
├── agent_implementations.py         # PACT agent implementations  
├── pipeline_configs.py             # Pipeline configurations
├── devops_web_server.py            # FastAPI web server
├── example_usage_devops.py         # Usage examples
├── docker-compose.yml              # Complete Docker setup
├── Dockerfile                      # Container configuration
└── README.md                       # This file
```

## 🎯 What It Does

Transform traditional CI/CD into intelligent agent coordination:

```python
# Traditional CI/CD: Rigid, monolithic pipelines
git push → jenkins → tests → deploy → pray 🤞

# PACT DevOps: Intelligent agent coordination
git push → PACT Gateway → [CodeAgent || TestAgent || SecurityAgent] 
         → DeployAgent → MonitorAgent → NotifyAgent ✨
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 PACT Orchestrator                       │
├─────────────────────────────────────────────────────────┤
│  CodeAgent → TestAgent → SecurityAgent → DeployAgent   │
│       ↓           ↓            ↓             ↓         │
│  QualityAgent → MonitorAgent → NotifyAgent             │
└─────────────────────────────────────────────────────────┘
```

### **Agents & Capabilities**

| Agent | Purpose | PACT Actions |
|-------|---------|--------------|
| **CodeAgent** | Code analysis & quality | `code.analyze_changes`, `code.check_quality`, `code.validate_syntax` |
| **TestAgent** | Testing orchestration | `tests.run_unit`, `tests.run_integration`, `tests.run_e2e` |
| **SecurityAgent** | Security scanning | `security.scan_vulnerabilities`, `security.check_dependencies` |
| **DeployAgent** | Deployment management | `deploy.to_staging`, `deploy.to_production`, `deploy.rollback` |
| **MonitorAgent** | Health monitoring | `monitor.check_health`, `monitor.track_metrics`, `monitor.detect_anomalies` |
| **NotifyAgent** | Communication | `notify.slack_team`, `notify.email_stakeholders`, `notify.update_jira` |

## 🔧 Usage Examples

### **1. Basic Deployment**

```python
from core_pipeline_orchestrator import PACTDevOpsPipeline

# Initialize orchestrator
pipeline = PACTDevOpsPipeline()
await pipeline.initialize()

# Trigger deployment
trigger_event = {
    "repository": "company/awesome-app",
    "branch": "feature/new-feature",
    "commit_hash": "abc123def456",
    "author": "developer@company.com",
    "environment": "staging"
}

pipeline_id = await pipeline.execute_pipeline(trigger_event, "default")
```

### **2. Production Deployment**

```python
# Production pipeline with comprehensive checks
pipeline_id = await pipeline.execute_pipeline(trigger_event, "production")
```

### **3. Emergency Hotfix**

```python
# Fast emergency deployment
pipeline_id = await pipeline.execute_pipeline(trigger_event, "hotfix")
```

### **4. Web API Integration**

```bash
# Start web server
python devops_web_server.py

# Trigger via API
curl -X POST http://localhost:8000/api/v1/pipeline/trigger \
  -H "Content-Type: application/json" \
  -d '{
    "repository": "company/app",
    "branch": "main", 
    "commit_hash": "abc123",
    "author": "dev@company.com",
    "environment": "production"
  }'
```

## 📊 Pipeline Configurations

### **Available Configs**

| Config | Purpose | Duration | Use Case |
|--------|---------|----------|----------|
| `default` | Standard web app | ~15 min | Feature branches, staging |
| `production` | Comprehensive checks | ~30 min | Production releases |
| `microservice` | Lightweight deployment | ~8 min | Microservices, quick deploys |
| `frontend` | Frontend-specific | ~12 min | React/Vue/Angular apps |
| `ml_model` | ML model deployment | ~45 min | Machine learning models |
| `hotfix` | Emergency deployment | ~5 min | Critical fixes |

### **Pipeline Stages**

```python
# Example: Default pipeline stages
{
    "stages": [
        {
            "name": "code_analysis",
            "parallel": True,
            "actions": ["code.analyze_changes", "code.check_quality"]
        },
        {
            "name": "security_scan", 
            "parallel": True,
            "actions": ["security.scan_vulnerabilities", "security.check_dependencies"]
        },
        {
            "name": "testing",
            "parallel": False,
            "actions": ["tests.run_unit", "tests.run_integration"]
        },
        {
            "name": "deployment",
            "parallel": False, 
            "actions": ["deploy.to_staging", "monitor.check_health"]
        }
    ]
}
```

## 🌐 Web Interface

The FastAPI server provides:

- **REST API** for pipeline management
- **Webhook endpoints** for GitHub/GitLab integration
- **Real-time monitoring** of active pipelines
- **Prometheus metrics** for observability

### **Key Endpoints**

```
POST /api/v1/pipeline/trigger          # Trigger new pipeline
GET  /api/v1/pipeline/{id}/status      # Get pipeline status
GET  /api/v1/pipelines/active          # List active pipelines
POST /api/v1/webhooks/github           # GitHub webhook
GET  /health                           # Health check
GET  /metrics                          # Prometheus metrics
```

## 🐳 Docker Deployment

### **Quick Start**

```bash
# Start complete stack
docker-compose up -d

# Services available:
# - PACT Pipeline: http://localhost:8000
# - Grafana: http://localhost:3000 (admin/admin)
# - Prometheus: http://localhost:9090
# - Redis: localhost:6379
```

### **Services Included**

- **PACT Pipeline Server** - Main orchestration engine
- **Redis** - Pipeline state management
- **Prometheus** - Metrics collection  
- **Grafana** - Monitoring dashboards
- **PostgreSQL** - Optional persistent storage

## 📈 Monitoring & Metrics

### **Built-in Metrics**

- Pipeline execution times
- Agent performance
- Success/failure rates
- Active pipeline count
- Resource utilization

### **Grafana Dashboards**

- Pipeline overview
- Agent performance
- Deployment trends
- Error tracking

## ⚙️ Configuration

### **Environment Variables**

```bash
# Required
REDIS_URL=redis://localhost:6379

# Optional
LOG_LEVEL=info
ENVIRONMENT=production
PROMETHEUS_ENABLED=true
```

### **Custom Pipeline Configs**

```python
# Add custom pipeline configuration
CUSTOM_CONFIG = {
    "name": "my_custom_pipeline",
    "timeout_minutes": 20,
    "stages": [
        {
            "name": "custom_stage",
            "actions": [
                {"agent": "code", "action": "code.analyze_changes"}
            ]
        }
    ]
}

pipeline.register_pipeline_config("custom", CUSTOM_CONFIG)
```

## 🔌 CI/CD Integration

### **GitHub Actions**

```yaml
# .github/workflows/pact-pipeline.yml
name: PACT Pipeline
on: [push]

jobs:
  trigger-pact:
    runs-on: ubuntu-latest
    steps:
    - name: Trigger PACT Pipeline
      run: |
        curl -X POST ${{ secrets.PACT_PIPELINE_URL }
