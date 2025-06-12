#!/usr/bin/env python3
"""
PACT DevOps Pipeline - Web Server

FastAPI web server that provides REST APIs for pipeline management,
webhook endpoints for CI/CD integration, and real-time pipeline monitoring.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import structlog

from core_pipeline_orchestrator import (
    PACTDevOpsPipeline, 
    PipelineStatus, 
    PipelineContext
)
from agent_implementations import (
    CodeAgent, 
    TestAgent, 
    SecurityAgent, 
    DeployAgent, 
    MonitorAgent, 
    NotifyAgent
)
from pipeline_configs import (
    PIPELINE_CONFIGS,
    get_pipeline_config,
    list_available_configs,
    apply_environment_overrides
)

# Configure logging
logger = structlog.get_logger(__name__)

# Global pipeline orchestrator instance
pipeline_orchestrator: Optional[PACTDevOpsPipeline] = None

# Pydantic models for API requests/responses
class TriggerPipelineRequest(BaseModel):
    """Request model for triggering a pipeline"""
    repository: str = Field(..., description="Repository identifier")
    branch: str = Field(..., description="Git branch name")
    commit_hash: str = Field(..., description="Git commit hash")
    author: str = Field(..., description="Commit author")
    environment: str = Field(default="staging", description="Target environment")
    config_name: str = Field(default="default", description="Pipeline configuration to use")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class PipelineResponse(BaseModel):
    """Response model for pipeline operations"""
    success: bool
    pipeline_id: Optional[str] = None
    message: str
    data: Optional[Dict[str, Any]] = None

class PipelineStatusResponse(BaseModel):
    """Response model for pipeline status"""
    pipeline_id: str
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: Optional[int] = None
    environment: str
    repository: str
    branch: str

class HealthCheckResponse(BaseModel):
    """Response model for health checks"""
    status: str
    timestamp: str
    version: str
    agents: Dict[str, str]
    active_pipelines: int

# Webhook models for various CI/CD platforms
class GitHubWebhookPayload(BaseModel):
    """GitHub webhook payload model"""
    ref: str
    repository: Dict[str, Any]
    pusher: Dict[str, Any]
    head_commit: Dict[str, Any]

class GitLabWebhookPayload(BaseModel):
    """GitLab webhook payload model"""
    ref: str
    project: Dict[str, Any]
    user_name: str
    commits: List[Dict[str, Any]]

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    # Startup
    global pipeline_orchestrator
    
    logger.info("Starting PACT DevOps Pipeline server")
    
    # Initialize pipeline orchestrator
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    pipeline_orchestrator = PACTDevOpsPipeline(redis_url=redis_url)
    await pipeline_orchestrator.initialize()
    
    # Register agents
    pipeline_orchestrator.register_agent(CodeAgent())
    pipeline_orchestrator.register_agent(TestAgent())
    pipeline_orchestrator.register_agent(SecurityAgent())
    pipeline_orchestrator.register_agent(DeployAgent())
    pipeline_orchestrator.register_agent(MonitorAgent())
    pipeline_orchestrator.register_agent(NotifyAgent())
    
    # Register pipeline configurations
    for config_name, config in PIPELINE_CONFIGS.items():
        pipeline_orchestrator.register_pipeline_config(config_name, config)
    
    logger.info("PACT DevOps Pipeline server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down PACT DevOps Pipeline server")
    if pipeline_orchestrator:
        await pipeline_orchestrator.shutdown()
    logger.info("PACT DevOps Pipeline server shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="PACT DevOps Pipeline",
    description="Multi-agent DevOps pipeline orchestration via PACT protocol",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get pipeline orchestrator
async def get_pipeline_orchestrator() -> PACTDevOpsPipeline:
    """Dependency to get the pipeline orchestrator instance"""
    if pipeline_orchestrator is None:
        raise HTTPException(status_code=500, detail="Pipeline orchestrator not initialized")
    return pipeline_orchestrator

# API Routes

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic HTML dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PACT DevOps Pipeline</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { background: #2563eb; color: white; padding: 20px; border-radius: 8px; }
            .section { margin: 20px 0; padding: 15px; border: 1px solid #e5e7eb; border-radius: 8px; }
            .endpoint { margin: 10px 0; padding: 10px; background: #f3f4f6; border-radius: 4px; }
            .method { font-weight: bold; color: #059669; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 PACT DevOps Pipeline</h1>
            <p>Multi-agent DevOps orchestration via PACT protocol</p>
        </div>
        
        <div class="section">
            <h2>📋 Available Endpoints</h2>
            <div class="endpoint">
                <span class="method">POST</span> /api/v1/pipeline/trigger - Trigger a new pipeline
            </div>
            <div class="endpoint">
                <span class="method">GET</span> /api/v1/pipeline/{pipeline_id}/status - Get pipeline status
            </div>
            <div class="endpoint">
                <span class="method">GET</span> /api/v1/pipelines/active - List active pipelines
            </div>
            <div class="endpoint">
                <span class="method">POST</span> /api/v1/webhooks/github - GitHub webhook endpoint
            </div>
            <div class="endpoint">
                <span class="method">GET</span> /health - Health check
            </div>
            <div class="endpoint">
                <span class="method">GET</span> /metrics - Prometheus metrics
            </div>
        </div>
        
        <div class="section">
            <h2>📚 Documentation</h2>
            <p><a href="/docs">Interactive API Documentation (Swagger UI)</a></p>
            <p><a href="/redoc">Alternative API Documentation (ReDoc)</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health", response_model=HealthCheckResponse)
async def health_check(orchestrator: PACTDevOpsPipeline = Depends(get_pipeline_orchestrator)):
    """Health check endpoint"""
    
    # Check agent health
    agent_health = {}
    for agent_name, agent in orchestrator.agents.items():
        try:
            health = await agent.health_check()
            agent_health[agent_name] = health.get("status", "unknown")
        except Exception as e:
            agent_health[agent_name] = f"error: {str(e)}"
    
    active_pipeline_count = len(await orchestrator.list_active_pipelines())
    
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        agents=agent_health,
        active_pipelines=active_pipeline_count
    )

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest().decode('utf-8'), {"Content-Type": CONTENT_TYPE_LATEST}

@app.post("/api/v1/pipeline/trigger", response_model=PipelineResponse)
async def trigger_pipeline(
    request: TriggerPipelineRequest,
    background_tasks: BackgroundTasks,
    orchestrator: PACTDevOpsPipeline = Depends(get_pipeline_orchestrator)
):
    """Trigger a new pipeline execution"""
    
    try:
        # Validate pipeline configuration exists
        if request.config_name not in PIPELINE_CONFIGS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown pipeline configuration: {request.config_name}"
            )
        
        # Prepare trigger event
        trigger_event = {
            "repository": request.repository,
            "branch": request.branch,
            "commit_hash": request.commit_hash,
            "author": request.author,
            "environment": request.environment,
            "metadata": request.metadata,
            "triggered_via": "api",
            "timestamp": datetime.now().isoformat()
        }
        
        # Apply environment-specific overrides to configuration
        base_config = get_pipeline_config(request.config_name)
        config = apply_environment_overrides(base_config, request.environment)
        
        # Register the modified configuration temporarily
        temp_config_name = f"{request.config_name}_{request.environment}"
        orchestrator.register_pipeline_config(temp_config_name, config)
        
        # Execute pipeline in background
        background_tasks.add_task(
            orchestrator.execute_pipeline,
            trigger_event,
            temp_config_name
        )
        
        # Note: We can't get the actual pipeline_id here since it's async
        # In a real implementation, you'd want to restructure this
        
        logger.info(
            "Pipeline triggered",
            repository=request.repository,
            branch=request.branch,
            environment=request.environment,
            config=request.config_name
        )
        
        return PipelineResponse(
            success=True,
            message="Pipeline triggered successfully",
            data={
                "repository": request.repository,
                "branch": request.branch,
                "environment": request.environment,
                "config": request.config_name
            }
        )
        
    except Exception as e:
        logger.error("Failed to trigger pipeline", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/pipeline/{pipeline_id}/status", response_model=PipelineStatusResponse)
async def get_pipeline_status(
    pipeline_id: str,
    orchestrator: PACTDevOpsPipeline = Depends(get_pipeline_orchestrator)
):
    """Get the status of a specific pipeline"""
    
    try:
        status_data = await orchestrator.get_pipeline_status(pipeline_id)
        
        if not status_data:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        # Parse context from stored data
        context_data = json.loads(status_data.get("context", "{}"))
        
        return PipelineStatusResponse(
            pipeline_id=pipeline_id,
            status=status_data.get("status", "unknown"),
            started_at=status_data.get("started_at"),
            completed_at=status_data.get("completed_at"),
            duration_ms=int(status_data.get("duration_ms", 0)) if status_data.get("duration_ms") else None,
            environment=context_data.get("environment", "unknown"),
            repository=context_data.get("repository", "unknown"),
            branch=context_data.get("branch", "unknown")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get pipeline status", pipeline_id=pipeline_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/pipelines/active")
async def list_active_pipelines(
    orchestrator: PACTDevOpsPipeline = Depends(get_pipeline_orchestrator)
):
    """List all active pipelines"""
    
    try:
        active_pipelines = await orchestrator.list_active_pipelines()
        
        # Get detailed status for each active pipeline
        pipeline_details = []
        for pipeline_id in active_pipelines:
            try:
                status_data = await orchestrator.get_pipeline_status(pipeline_id)
                if status_data:
                    context_data = json.loads(status_data.get("context", "{}"))
                    pipeline_details.append({
                        "pipeline_id": pipeline_id,
                        "status": status_data.get("status"),
                        "repository": context_data.get("repository"),
                        "branch": context_data.get("branch"),
                        "environment": context_data.get("environment"),
                        "started_at": status_data.get("started_at")
                    })
            except Exception as e:
                logger.warning("Failed to get details for pipeline", pipeline_id=pipeline_id, error=str(e))
        
        return {
            "active_pipelines": len(pipeline_details),
            "pipelines": pipeline_details
        }
        
    except Exception as e:
        logger.error("Failed to list active pipelines", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/pipeline/{pipeline_id}/cancel")
async def cancel_pipeline(
    pipeline_id: str,
    orchestrator: PACTDevOpsPipeline = Depends(get_pipeline_orchestrator)
):
    """Cancel a running pipeline"""
    
    try:
        await orchestrator.cancel_pipeline(pipeline_id, reason="User requested cancellation")
        
        return PipelineResponse(
            success=True,
            pipeline_id=pipeline_id,
            message="Pipeline cancelled successfully"
        )
        
    except Exception as e:
        logger.error("Failed to cancel pipeline", pipeline_id=pipeline_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/configs")
async def list_pipeline_configs():
    """List available pipeline configurations"""
    
    configs = []
    for config_name, config in PIPELINE_CONFIGS.items():
        configs.append({
            "name": config_name,
            "description": config.get("description", ""),
            "timeout_minutes": config.get("timeout_minutes", 30),
            "stages": len(config.get("stages", []))
        })
    
    return {
        "available_configs": configs,
        "total_configs": len(configs)
    }

# Webhook endpoints for CI/CD integration

@app.post("/api/v1/webhooks/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    orchestrator: PACTDevOpsPipeline = Depends(get_pipeline_orchestrator)
):
    """GitHub webhook endpoint"""
    
    try:
        payload = await request.json()
        
        # Only process push events
        if payload.get("ref", "").startswith("refs/heads/"):
            branch = payload["ref"].replace("refs/heads/", "")
            repository = payload["repository"]["full_name"]
            
            if payload.get("head_commit"):
                commit = payload["head_commit"]
                
                trigger_event = {
                    "repository": repository,
                    "branch": branch,
                    "commit_hash": commit["id"],
                    "author": commit["author"]["email"],
                    "environment": "staging" if branch != "main" else "production",
                    "metadata": {
                        "webhook_source": "github",
                        "commit_message": commit["message"],
                        "commit_url": commit["url"]
                    },
                    "triggered_via": "github_webhook"
                }
                
                # Determine pipeline config based on branch
                config_name = "production" if branch == "main" else "default"
                
                # Execute pipeline in background
                background_tasks.add_task(
                    orchestrator.execute_pipeline,
                    trigger_event,
                    config_name
                )
                
                logger.info(
                    "GitHub webhook triggered pipeline",
                    repository=repository,
                    branch=branch,
                    commit=commit["id"][:8]
                )
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error("GitHub webhook processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/webhooks/gitlab")
async def gitlab_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    orchestrator: PACTDevOpsPipeline = Depends(get_pipeline_orchestrator)
):
    """GitLab webhook endpoint"""
    
    try:
        payload = await request.json()
        
        # Only process push events
        if payload.get("object_kind") == "push" and payload.get("ref", "").startswith("refs/heads/"):
            branch = payload["ref"].replace("refs/heads/", "")
            repository = payload["project"]["path_with_namespace"]
            
            if payload.get("commits") and len(payload["commits"]) > 0:
                commit = payload["commits"][-1]  # Latest commit
                
                trigger_event = {
                    "repository": repository,
                    "branch": branch,
                    "commit_hash": commit["id"],
                    "author": commit["author"]["email"],
                    "environment": "staging" if branch != "main" else "production",
                    "metadata": {
                        "webhook_source": "gitlab",
                        "commit_message": commit["message"],
                        "commit_url": commit["url"]
                    },
                    "triggered_via": "gitlab_webhook"
                }
                
                # Determine pipeline config based on branch
                config_name = "production" if branch == "main" else "default"
                
                # Execute pipeline in background
                background_tasks.add_task(
                    orchestrator.execute_pipeline,
                    trigger_event,
                    config_name
                )
                
                logger.info(
                    "GitLab webhook triggered pipeline",
                    repository=repository,
                    branch=branch,
                    commit=commit["id"][:8]
                )
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error("GitLab webhook processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Development server
if __name__ == "__main__":
    uvicorn.run(
        "devops_web_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
