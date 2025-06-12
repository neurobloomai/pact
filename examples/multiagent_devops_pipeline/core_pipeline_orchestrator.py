#!/usr/bin/env python3
"""
PACT DevOps Pipeline - Core Orchestrator

This module provides the main pipeline orchestration logic, coordinating
multiple PACT agents to execute complex DevOps workflows.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging

import structlog
from prometheus_client import Counter, Histogram, Gauge
import redis.asyncio as redis

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Prometheus metrics
PIPELINE_COUNTER = Counter('pact_pipelines_total', 'Total pipelines executed', ['status'])
PIPELINE_DURATION = Histogram('pact_pipeline_duration_seconds', 'Pipeline execution time')
ACTIVE_PIPELINES = Gauge('pact_active_pipelines', 'Currently active pipelines')
AGENT_ACTION_COUNTER = Counter('pact_agent_actions_total', 'Agent actions executed', ['agent', 'action', 'status'])
AGENT_ACTION_DURATION = Histogram('pact_agent_action_duration_seconds', 'Agent action execution time', ['agent', 'action'])


class PipelineStatus(Enum):
    """Pipeline execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class AgentActionStatus(Enum):
    """Individual agent action status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"


@dataclass
class PipelineContext:
    """Context shared across all pipeline stages"""
    pipeline_id: str
    repository: str
    branch: str
    commit_hash: str
    author: str
    environment: str
    started_at: datetime
    trigger_event: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['started_at'] = self.started_at.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineContext':
        """Create from dictionary"""
        data['started_at'] = datetime.fromisoformat(data['started_at'])
        return cls(**data)


@dataclass
class AgentResult:
    """Result from an agent action execution"""
    agent_name: str
    action: str
    status: AgentActionStatus
    started_at: datetime
    completed_at: Optional[datetime]
    duration_ms: int
    output: Dict[str, Any]
    errors: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['status'] = self.status.value
        result['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            result['completed_at'] = self.completed_at.isoformat()
        return result


@dataclass
class PipelineResult:
    """Complete pipeline execution result"""
    pipeline_id: str
    context: PipelineContext
    status: PipelineStatus
    started_at: datetime
    completed_at: Optional[datetime]
    duration_ms: int
    stage_results: List[Dict[str, Any]]
    agent_results: List[AgentResult]
    errors: List[str]
    metadata: Dict[str, Any]


class PipelineAgent:
    """Abstract base class for PACT pipeline agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = structlog.get_logger(__name__, agent=name)
    
    async def execute_pact_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a PACT action - to be implemented by specific agents"""
        raise NotImplementedError("Agents must implement execute_pact_action")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check agent health status"""
        return {
            "agent": self.name,
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }


class PACTDevOpsPipeline:
    """Main PACT DevOps Pipeline orchestrator"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.agents: Dict[str, PipelineAgent] = {}
        self.pipeline_configs: Dict[str, Dict] = {}
        self.redis_client = redis.from_url(redis_url)
        self.active_pipelines: Dict[str, Dict] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.logger = structlog.get_logger(__name__)
        
    async def initialize(self):
        """Initialize the pipeline orchestrator"""
        await self.redis_client.ping()
        self.logger.info("Pipeline orchestrator initialized")
    
    async def shutdown(self):
        """Gracefully shutdown the orchestrator"""
        # Cancel active pipelines
        for pipeline_id in list(self.active_pipelines.keys()):
            await self.cancel_pipeline(pipeline_id, reason="Orchestrator shutdown")
        
        await self.redis_client.close()
        self.logger.info("Pipeline orchestrator shutdown complete")
    
    def register_agent(self, agent: PipelineAgent):
        """Register a PACT agent for pipeline use"""
        self.agents[agent.name] = agent
        self.logger.info("Agent registered", agent=agent.name)
    
    def unregister_agent(self, agent_name: str):
        """Unregister an agent"""
        if agent_name in self.agents:
            del self.agents[agent_name]
            self.logger.info("Agent unregistered", agent=agent_name)
    
    def register_pipeline_config(self, name: str, config: Dict):
        """Register a pipeline configuration"""
        self.pipeline_configs[name] = config
        self.logger.info("Pipeline config registered", config_name=name)
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit an event to registered handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    await handler(data)
                except Exception as e:
                    self.logger.error("Event handler failed", event_type=event_type, error=str(e))
    
    async def execute_pipeline(self, trigger_event: Dict, config_name: str = "default") -> str:
        """Execute a complete DevOps pipeline"""
        pipeline_id = f"pipe_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
        
        with PIPELINE_DURATION.time():
            try:
                # Create pipeline context
                context = self._create_pipeline_context(pipeline_id, trigger_event)
                
                # Get pipeline configuration
                config = self.pipeline_configs.get(config_name)
                if not config:
                    raise ValueError(f"Pipeline configuration '{config_name}' not found")
                
                # Initialize pipeline tracking
                await self._initialize_pipeline_tracking(pipeline_id, context, config)
                
                # Emit pipeline started event
                await self.emit_event("pipeline.started", {
                    "pipeline_id": pipeline_id,
                    "context": context.to_dict()
                })
                
                # Execute pipeline stages
                stage_results, agent_results = await self._execute_stages(context, config)
                
                # Determine overall status
                overall_status = self._calculate_pipeline_status(agent_results)
                
                # Create pipeline result
                completed_at = datetime.now()
                duration_ms = int((completed_at - context.started_at).total_seconds() * 1000)
                
                pipeline_result = PipelineResult(
                    pipeline_id=pipeline_id,
                    context=context,
                    status=overall_status,
                    started_at=context.started_at,
                    completed_at=completed_at,
                    duration_ms=duration_ms,
                    stage_results=stage_results,
                    agent_results=agent_results,
                    errors=[],
                    metadata={}
                )
                
                # Store final result
                await self._store_pipeline_result(pipeline_result)
                
                # Update metrics
                PIPELINE_COUNTER.labels(status=overall_status.value).inc()
                ACTIVE_PIPELINES.dec()
                
                # Emit pipeline completed event
                await self.emit_event("pipeline.completed", {
                    "pipeline_id": pipeline_id,
                    "status": overall_status.value,
                    "duration_ms": duration_ms
                })
                
                self.logger.info(
                    "Pipeline execution completed",
                    pipeline_id=pipeline_id,
                    status=overall_status.value,
                    duration_ms=duration_ms
                )
                
                return pipeline_id
                
            except Exception as e:
                # Handle pipeline failure
                await self._handle_pipeline_failure(pipeline_id, str(e))
                PIPELINE_COUNTER.labels(status="failed").inc()
                ACTIVE_PIPELINES.dec()
                raise
    
    async def cancel_pipeline(self, pipeline_id: str, reason: str = "User requested"):
        """Cancel a running pipeline"""
        if pipeline_id in self.active_pipelines:
            self.active_pipelines[pipeline_id]["status"] = PipelineStatus.CANCELLED
            await self.redis_client.hset(
                f"pipeline:{pipeline_id}",
                "status", PipelineStatus.CANCELLED.value
            )
            
            await self.emit_event("pipeline.cancelled", {
                "pipeline_id": pipeline_id,
                "reason": reason
            })
            
            self.logger.info("Pipeline cancelled", pipeline_id=pipeline_id, reason=reason)
    
    async def get_pipeline_status(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get current pipeline status"""
        pipeline_data = await self.redis_client.hgetall(f"pipeline:{pipeline_id}")
        if pipeline_data:
            return {k.decode(): v.decode() for k, v in pipeline_data.items()}
        return None
    
    async def list_active_pipelines(self) -> List[str]:
        """List all active pipeline IDs"""
        return list(self.active_pipelines.keys())
    
    def _create_pipeline_context(self, pipeline_id: str, trigger_event: Dict) -> PipelineContext:
        """Create pipeline context from trigger event"""
        return PipelineContext(
            pipeline_id=pipeline_id,
            repository=trigger_event.get("repository", "unknown"),
            branch=trigger_event.get("branch", "unknown"),
            commit_hash=trigger_event.get("commit_hash", "unknown"),
            author=trigger_event.get("author", "unknown"),
            environment=trigger_event.get("environment", "staging"),
            started_at=datetime.now(),
            trigger_event=trigger_event,
            metadata=trigger_event.get("metadata", {})
        )
    
    async def _initialize_pipeline_tracking(self, pipeline_id: str, context: PipelineContext, config: Dict):
        """Initialize pipeline tracking in Redis"""
        pipeline_data = {
            "status": PipelineStatus.RUNNING.value,
            "context": json.dumps(context.to_dict()),
            "config": json.dumps(config),
            "started_at": context.started_at.isoformat()
        }
        
        await self.redis_client.hset(f"pipeline:{pipeline_id}", mapping=pipeline_data)
        self.active_pipelines[pipeline_id] = pipeline_data
        ACTIVE_PIPELINES.inc()
    
    async def _execute_stages(self, context: PipelineContext, config: Dict) -> tuple[List[Dict], List[AgentResult]]:
        """Execute all pipeline stages"""
        stage_results = []
        all_agent_results = []
        
        for stage_index, stage in enumerate(config.get("stages", [])):
            stage_name = stage.get("name", f"stage_{stage_index}")
            
            self.logger.info("Starting stage", pipeline_id=context.pipeline_id, stage=stage_name)
            
            try:
                # Check if pipeline was cancelled
                if context.pipeline_id in self.active_pipelines:
                    if self.active_pipelines[context.pipeline_id].get("status") == PipelineStatus.CANCELLED.value:
                        break
                
                # Execute stage
                stage_result, agent_results = await self._execute_stage(context, stage, all_agent_results)
                
                stage_results.append(stage_result)
                all_agent_results.extend(agent_results)
                
                # Check for stage failure and halt condition
                if stage_result["status"] == "failed" and stage.get("halt_on_failure", True):
                    self.logger.warning(
                        "Stage failed, halting pipeline",
                        pipeline_id=context.pipeline_id,
                        stage=stage_name
                    )
                    break
                    
            except Exception as e:
                stage_result = {
                    "stage": stage_name,
                    "status": "failed",
                    "error": str(e),
                    "duration_ms": 0
                }
                stage_results.append(stage_result)
                
                if stage.get("halt_on_failure", True):
                    break
        
        return stage_results, all_agent_results
    
    async def _execute_stage(self, context: PipelineContext, stage: Dict, previous_results: List[AgentResult]) -> tuple[Dict, List[AgentResult]]:
        """Execute a single pipeline stage"""
        stage_name = stage.get("name", "unnamed_stage")
        stage_start = datetime.now()
        stage_results = []
        
        try:
            actions = stage.get("actions", [])
            
            # Execute actions (parallel or sequential)
            if stage.get("parallel", False):
                # Execute actions in parallel
                tasks = [
                    self._execute_action(context, action, previous_results)
                    for action in actions
                ]
                stage_results = await asyncio.gather(*tasks, return_exceptions=True)
            else:
                # Execute actions sequentially
                for action in actions:
                    result = await self._execute_action(context, action, previous_results)
                    stage_results.append(result)
                    
                    # Check for failure and halt condition
                    if (result.status == AgentActionStatus.FAILED and 
                        action.get("halt_on_failure", True)):
                        break
            
            # Calculate stage status
            failed_results = [r for r in stage_results 
                            if isinstance(r, AgentResult) and r.status == AgentActionStatus.FAILED]
            stage_status = "failed" if failed_results else "success"
            
            stage_duration = int((datetime.now() - stage_start).total_seconds() * 1000)
            
            stage_result = {
                "stage": stage_name,
                "status": stage_status,
                "duration_ms": stage_duration,
                "actions_executed": len([r for r in stage_results if isinstance(r, AgentResult)]),
                "actions_failed": len(failed_results)
            }
            
            return stage_result, [r for r in stage_results if isinstance(r, AgentResult)]
            
        except Exception as e:
            stage_duration = int((datetime.now() - stage_start).total_seconds() * 1000)
            stage_result = {
                "stage": stage_name,
                "status": "failed",
                "error": str(e),
                "duration_ms": stage_duration
            }
            return stage_result, []
    
    async def _execute_action(self, context: PipelineContext, action: Dict, previous_results: List[AgentResult]) -> AgentResult:
        """Execute a single agent action"""
        agent_name = action["agent"]
        pact_action = action["action"]
        
        start_time = datetime.now()
        
        # Check if agent exists
        if agent_name not in self.agents:
            return AgentResult(
                agent_name=agent_name,
                action=pact_action,
                status=AgentActionStatus.FAILED,
                started_at=start_time,
                completed_at=datetime.now(),
                duration_ms=0,
                output={},
                errors=[f"Agent '{agent_name}' not found"],
                metadata={}
            )
        
        try:
            agent = self.agents[agent_name]
            
            # Prepare action parameters
            params = self._prepare_action_params(context, action, previous_results)
            
            # Record action start
            with AGENT_ACTION_DURATION.labels(agent=agent_name, action=pact_action).time():
                # Execute PACT action
                output = await agent.execute_pact_action(pact_action, params)
            
            completed_at = datetime.now()
            duration_ms = int((completed_at - start_time).total_seconds() * 1000)
            
            # Determine status from output
            success = output.get("success", True)
            status = AgentActionStatus.SUCCESS if success else AgentActionStatus.FAILED
            
            # Record metrics
            AGENT_ACTION_COUNTER.labels(
                agent=agent_name,
                action=pact_action,
                status=status.value
            ).inc()
            
            result = AgentResult(
                agent_name=agent_name,
                action=pact_action,
                status=status,
                started_at=start_time,
                completed_at=completed_at,
                duration_ms=duration_ms,
                output=output,
                errors=output.get("errors", []),
                metadata=output.get("metadata", {})
            )
            
            self.logger.info(
                "Agent action completed",
                pipeline_id=context.pipeline_id,
                agent=agent_name,
                action=pact_action,
                status=status.value,
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            completed_at = datetime.now()
            duration_ms = int((completed_at - start_time).total_seconds() * 1000)
            
            # Record failed metric
            AGENT_ACTION_COUNTER.labels(
                agent=agent_name,
                action=pact_action,
                status="failed"
            ).inc()
            
            result = AgentResult(
                agent_name=agent_name,
                action=pact_action,
                status=AgentActionStatus.FAILED,
                started_at=start_time,
                completed_at=completed_at,
                duration_ms=duration_ms,
                output={},
                errors=[str(e)],
                metadata={}
            )
            
            self.logger.error(
                "Agent action failed",
                pipeline_id=context.pipeline_id,
                agent=agent_name,
                action=pact_action,
                error=str(e),
                duration_ms=duration_ms
            )
            
            return result
    
    def _prepare_action_params(self, context: PipelineContext, action: Dict, previous_results: List[AgentResult]) -> Dict:
        """Prepare parameters for agent action execution"""
        params = {
            "pipeline_id": context.pipeline_id,
            "repository": context.repository,
            "branch": context.branch,
            "commit_hash": context.commit_hash,
            "environment": context.environment,
            "author": context.author,
            "trigger_event": context.trigger_event,
            "previous_results": [r.to_dict() for r in previous_results],
            "context": context.to_dict()
        }
        
        # Add action-specific parameters
        params.update(action.get("params", {}))
        
        return params
    
    def _calculate_pipeline_status(self, results: List[AgentResult]) -> PipelineStatus:
        """Calculate overall pipeline status from agent results"""
        if not results:
            return PipelineStatus.FAILED
        
        failed_results = [r for r in results if r.status == AgentActionStatus.FAILED]
        if failed_results:
            return PipelineStatus.FAILED
        
        return PipelineStatus.SUCCESS
    
    async def _store_pipeline_result(self, result: PipelineResult):
        """Store final pipeline result"""
        # Update Redis with final status
        await self.redis_client.hset(
            f"pipeline:{result.pipeline_id}",
            mapping={
                "status": result.status.value,
                "completed_at": result.completed_at.isoformat() if result.completed_at else "",
                "duration_ms": str(result.duration_ms)
            }
        )
        
        # Store detailed results (with expiration)
        await self.redis_client.setex(
            f"pipeline:{result.pipeline_id}:result",
            86400,  # 24 hours
            json.dumps({
                "pipeline_id": result.pipeline_id,
                "status": result.status.value,
                "duration_ms": result.duration_ms,
                "stage_results": result.stage_results,
                "agent_results": [r.to_dict() for r in result.agent_results]
            })
        )
        
        # Clean up from active pipelines
        if result.pipeline_id in self.active_pipelines:
            del self.active_pipelines[result.pipeline_id]
    
    async def _handle_pipeline_failure(self, pipeline_id: str, error: str):
        """Handle pipeline failure"""
        self.logger.error("Pipeline failed", pipeline_id=pipeline_id, error=error)
        
        # Update status in Redis
        await self.redis_client.hset(
            f"pipeline:{pipeline_id}",
            mapping={
                "status": PipelineStatus.FAILED.value,
                "error": error,
                "completed_at": datetime.now().isoformat()
            }
        )
        
        # Emit failure event
        await self.emit_event("pipeline.failed", {
            "pipeline_id": pipeline_id,
            "error": error
        })
        
        # Clean up from active pipelines
        if pipeline_id in self.active_pipelines:
            del self.active_pipelines[pipeline_id]
