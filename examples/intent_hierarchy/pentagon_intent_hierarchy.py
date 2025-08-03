# Pentagon Intent Hierarchy System - Full Implementation
from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Set, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import uuid
import logging
from contextlib import asynccontextmanager
import math
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Configure military-grade logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [CLASSIFICATION: RESTRICTED] - %(message)s'
)
logger = logging.getLogger(__name__)

# Enhanced Enums
class SecurityLevel(str, Enum):
    UNCLASSIFIED = "UNCLASSIFIED"
    CONFIDENTIAL = "CONFIDENTIAL"
    SECRET = "SECRET"
    TOP_SECRET = "TOP_SECRET"

class MissionStatus(str, Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    INTENT_ADAPTING = "INTENT_ADAPTING"
    REASSIGNING = "REASSIGNING"
    COMPLETED = "COMPLETED"
    ABORTED = "ABORTED"

class DroneStatus(str, Enum):
    OPERATIONAL = "OPERATIONAL"
    COMM_FAILURE = "COMM_FAILURE"
    DAMAGED = "DAMAGED"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"

class IntentType(str, Enum):
    STRATEGIC = "STRATEGIC"      # High-level mission goals
    TACTICAL = "TACTICAL"        # Mid-level operational objectives
    OPERATIONAL = "OPERATIONAL"  # Specific executable actions
    CONTINGENCY = "CONTINGENCY"  # Backup/failure handling intents

class IntentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ADAPTING = "ADAPTING"

class ContextType(str, Enum):
    ENVIRONMENTAL = "ENVIRONMENTAL"
    TACTICAL = "TACTICAL"
    RESOURCE = "RESOURCE"
    TEMPORAL = "TEMPORAL"
    THREAT = "THREAT"

# Intent Hierarchy Core Models
class IntentNode(BaseModel):
    """Core intent node in the hierarchy"""
    id: str
    name: str
    description: str
    intent_type: IntentType
    status: IntentStatus
    priority: float = Field(..., ge=0.0, le=1.0)
    
    # Hierarchy relationships
    parent_id: Optional[str] = None
    children_ids: List[str] = []
    
    # Intent semantics
    purpose: str = Field(..., description="Why this intent exists")
    success_criteria: Dict[str, Any] = Field(..., description="How to measure success")
    failure_conditions: List[str] = []
    
    # Resource requirements
    required_capabilities: List[str] = []
    resource_constraints: Dict[str, Any] = {}
    
    # Context awareness
    context_dependencies: Dict[ContextType, List[str]] = {}
    adaptation_rules: List[Dict[str, Any]] = []
    
    # Execution details
    assigned_assets: List[str] = []
    estimated_duration: Optional[int] = None
    deadline: Optional[datetime] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    created_by: str

class ContextualState(BaseModel):
    """Current contextual state of the operation"""
    timestamp: datetime
    environmental_conditions: Dict[str, Any] = {}
    threat_assessment: Dict[str, Any] = {}
    resource_availability: Dict[str, Any] = {}
    operational_tempo: str = "NORMAL"  # LOW, NORMAL, HIGH, CRITICAL
    mission_phase: str = "EXECUTION"   # PLANNING, EXECUTION, COMPLETION

class IntentAdaptationPlan(BaseModel):
    """Plan for adapting intent hierarchy due to failures"""
    trigger_event: str
    affected_intent_ids: List[str]
    adaptation_strategy: str
    new_intent_assignments: Dict[str, List[str]]
    resource_reallocation: Dict[str, Any]
    success_probability: float = Field(..., ge=0.0, le=1.0)
    estimated_impact: Dict[str, Any]
    execution_steps: List[Dict[str, Any]]

# Intent Hierarchy Engine
class IntentHierarchyEngine:
    """Core engine for intent-driven mission execution"""
    
    def __init__(self):
        self.intent_nodes: Dict[str, IntentNode] = {}
        self.context_state = ContextualState(timestamp=datetime.utcnow())
        self.adaptation_history: List[IntentAdaptationPlan] = []
        
    def add_intent_node(self, node: IntentNode) -> None:
        """Add a new intent node to the hierarchy"""
        self.intent_nodes[node.id] = node
        
        # Update parent-child relationships
        if node.parent_id and node.parent_id in self.intent_nodes:
            parent = self.intent_nodes[node.parent_id]
            if node.id not in parent.children_ids:
                parent.children_ids.append(node.id)
    
    def get_root_intents(self) -> List[IntentNode]:
        """Get all root-level (strategic) intents"""
        return [node for node in self.intent_nodes.values() if node.parent_id is None]
    
    def get_children(self, intent_id: str) -> List[IntentNode]:
        """Get direct children of an intent"""
        intent = self.intent_nodes.get(intent_id)
        if not intent:
            return []
        return [self.intent_nodes[child_id] for child_id in intent.children_ids if child_id in self.intent_nodes]
    
    def get_descendants(self, intent_id: str) -> List[IntentNode]:
        """Get all descendants of an intent (recursive)"""
        descendants = []
        children = self.get_children(intent_id)
        for child in children:
            descendants.append(child)
            descendants.extend(self.get_descendants(child.id))
        return descendants
    
    def propagate_intent_failure(self, failed_intent_id: str) -> List[str]:
        """Propagate intent failure up and down the hierarchy"""
        affected_intents = [failed_intent_id]
        
        # Mark intent as failed
        if failed_intent_id in self.intent_nodes:
            self.intent_nodes[failed_intent_id].status = IntentStatus.FAILED
            
            # Get all descendants and mark them as suspended
            descendants = self.get_descendants(failed_intent_id)
            for descendant in descendants:
                descendant.status = IntentStatus.SUSPENDED
                affected_intents.append(descendant.id)
            
            # Check if parent intent can still be achieved
            parent_id = self.intent_nodes[failed_intent_id].parent_id
            if parent_id:
                self._evaluate_parent_intent_viability(parent_id)
                affected_intents.append(parent_id)
        
        return affected_intents
    
    def _evaluate_parent_intent_viability(self, parent_id: str) -> None:
        """Evaluate if parent intent can still be achieved"""
        parent = self.intent_nodes.get(parent_id)
        if not parent:
            return
        
        children = self.get_children(parent_id)
        active_children = [child for child in children if child.status == IntentStatus.ACTIVE]
        failed_children = [child for child in children if child.status == IntentStatus.FAILED]
        
        # If more than 50% of critical children failed, mark parent as adapting
        if len(failed_children) > len(children) * 0.5:
            parent.status = IntentStatus.ADAPTING
    
    def find_alternative_intents(self, failed_intent: IntentNode) -> List[IntentNode]:
        """Find alternative ways to achieve the same purpose"""
        alternatives = []
        
        # Look for sibling intents with similar purpose
        if failed_intent.parent_id:
            siblings = self.get_children(failed_intent.parent_id)
            for sibling in siblings:
                if (sibling.id != failed_intent.id and 
                    sibling.status != IntentStatus.FAILED and
                    self._intents_have_similar_purpose(failed_intent, sibling)):
                    alternatives.append(sibling)
        
        # Look for intents at the same level with compatible capabilities
        same_level_intents = [intent for intent in self.intent_nodes.values() 
                             if intent.intent_type == failed_intent.intent_type and
                             intent.status == IntentStatus.ACTIVE and
                             intent.id != failed_intent.id]
        
        for intent in same_level_intents:
            capability_overlap = set(intent.required_capabilities) & set(failed_intent.required_capabilities)
            if len(capability_overlap) > 0:
                alternatives.append(intent)
        
        return alternatives[:3]  # Return top 3 alternatives
    
    def _intents_have_similar_purpose(self, intent1: IntentNode, intent2: IntentNode) -> bool:
        """Check if two intents have similar purposes"""
        # Simple keyword matching - in production would use NLP
        purpose1_words = set(intent1.purpose.lower().split())
        purpose2_words = set(intent2.purpose.lower().split())
        overlap = len(purpose1_words & purpose2_words)
        return overlap > max(len(purpose1_words), len(purpose2_words)) * 0.3
    
    def generate_intent_adaptation_plan(self, trigger_event: str, affected_assets: List[str]) -> IntentAdaptationPlan:
        """Generate comprehensive adaptation plan based on intent hierarchy"""
        affected_intents = []
        
        # Find all intents affected by the asset failure
        for intent in self.intent_nodes.values():
            if any(asset in intent.assigned_assets for asset in affected_assets):
                affected_intents.extend(self.propagate_intent_failure(intent.id))
        
        # Remove duplicates
        affected_intents = list(set(affected_intents))
        
        # Determine adaptation strategy
        strategy = self._determine_adaptation_strategy(affected_intents)
        
        # Generate new intent assignments
        new_assignments = self._generate_new_intent_assignments(affected_intents, affected_assets)
        
        # Calculate success probability
        success_prob = self._calculate_adaptation_success_probability(new_assignments)
        
        # Estimate impact
        impact = self._estimate_adaptation_impact(affected_intents)
        
        # Generate execution steps
        execution_steps = self._generate_execution_steps(new_assignments, strategy)
        
        plan = IntentAdaptationPlan(
            trigger_event=trigger_event,
            affected_intent_ids=affected_intents,
            adaptation_strategy=strategy,
            new_intent_assignments=new_assignments,
            resource_reallocation={},
            success_probability=success_prob,
            estimated_impact=impact,
            execution_steps=execution_steps
        )
        
        self.adaptation_history.append(plan)
        return plan
    
    def _determine_adaptation_strategy(self, affected_intent_ids: List[str]) -> str:
        """Determine the best adaptation strategy"""
        strategic_affected = any(self.intent_nodes[id].intent_type == IntentType.STRATEGIC 
                               for id in affected_intent_ids if id in self.intent_nodes)
        
        if strategic_affected:
            return "MISSION_RESTRUCTURE"
        elif len(affected_intent_ids) > 3:
            return "HIERARCHICAL_REBALANCE"
        else:
            return "TACTICAL_REASSIGNMENT"
    
    def _generate_new_intent_assignments(self, affected_intent_ids: List[str], failed_assets: List[str]) -> Dict[str, List[str]]:
        """Generate new intent-to-asset assignments"""
        assignments = {}
        
        # Get available assets (not failed)
        available_assets = []  # This would be populated from the drone store
        
        for intent_id in affected_intent_ids:
            intent = self.intent_nodes.get(intent_id)
            if intent and intent.status != IntentStatus.FAILED:
                # Find alternative intents or redistribute
                alternatives = self.find_alternative_intents(intent)
                if alternatives:
                    assignments[intent_id] = [alt.id for alt in alternatives[:2]]
                else:
                    # Try to find compatible assets
                    assignments[intent_id] = []  # Would assign based on capabilities
        
        return assignments
    
    def _calculate_adaptation_success_probability(self, assignments: Dict[str, List[str]]) -> float:
        """Calculate probability of successful adaptation"""
        if not assignments:
            return 0.0
        
        total_intents = len(assignments)
        successfully_assigned = sum(1 for intent_assignments in assignments.values() if intent_assignments)
        
        base_probability = successfully_assigned / total_intents if total_intents > 0 else 0.0
        
        # Adjust based on intent types and priorities
        priority_weight = 0.0
        for intent_id in assignments.keys():
            intent = self.intent_nodes.get(intent_id)
            if intent:
                priority_weight += intent.priority
        
        average_priority = priority_weight / len(assignments) if assignments else 0.0
        
        return min(0.95, base_probability * 0.7 + average_priority * 0.3)
    
    def _estimate_adaptation_impact(self, affected_intent_ids: List[str]) -> Dict[str, Any]:
        """Estimate the impact of adaptation"""
        impact = {
            "mission_delay_minutes": 0,
            "capability_degradation": 0.0,
            "resource_utilization_change": 0.0,
            "risk_level_change": "NONE"
        }
        
        for intent_id in affected_intent_ids:
            intent = self.intent_nodes.get(intent_id)
            if intent:
                if intent.intent_type == IntentType.STRATEGIC:
                    impact["mission_delay_minutes"] += 30
                    impact["capability_degradation"] += 0.2
                elif intent.intent_type == IntentType.TACTICAL:
                    impact["mission_delay_minutes"] += 15
                    impact["capability_degradation"] += 0.1
                else:
                    impact["mission_delay_minutes"] += 5
                    impact["capability_degradation"] += 0.05
        
        # Determine risk level change
        if impact["capability_degradation"] > 0.5:
            impact["risk_level_change"] = "HIGH"
        elif impact["capability_degradation"] > 0.2:
            impact["risk_level_change"] = "MODERATE"
        else:
            impact["risk_level_change"] = "LOW"
        
        return impact
    
    def _generate_execution_steps(self, assignments: Dict[str, List[str]], strategy: str) -> List[Dict[str, Any]]:
        """Generate detailed execution steps for adaptation"""
        steps = []
        
        steps.append({
            "step": 1,
            "action": "SUSPEND_AFFECTED_INTENTS",
            "description": "Temporarily suspend affected intents to prevent conflicts",
            "estimated_duration": 30  # seconds
        })
        
        steps.append({
            "step": 2,
            "action": "ANALYZE_INTENT_DEPENDENCIES",
            "description": "Analyze intent hierarchy dependencies for safe reassignment",
            "estimated_duration": 60
        })
        
        steps.append({
            "step": 3,
            "action": "REASSIGN_INTENT_RESPONSIBILITIES",
            "description": f"Execute {strategy} to redistribute intent responsibilities",
            "estimated_duration": 120
        })
        
        steps.append({
            "step": 4,
            "action": "VALIDATE_INTENT_HIERARCHY",
            "description": "Validate that intent hierarchy remains consistent",
            "estimated_duration": 45
        })
        
        steps.append({
            "step": 5,
            "action": "RESUME_MISSION_EXECUTION",
            "description": "Resume mission execution with adapted intent assignments",
            "estimated_duration": 30
        })
        
        return steps

# Enhanced Pentagon Data Store with Intent Integration
class EnhancedPentagonStore:
    def __init__(self):
        self.missions: Dict[str, Any] = {}
        self.drones: Dict[str, Any] = {}
        self.intent_engine = IntentHierarchyEngine()
        self.active_failures: Dict[str, Any] = {}
        self.websocket_connections: Set[WebSocket] = set()
        
    async def broadcast_intent_update(self, message: Dict):
        """Broadcast intent hierarchy updates"""
        if self.websocket_connections:
            disconnected = set()
            for connection in self.websocket_connections:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.add(connection)
            self.websocket_connections -= disconnected

# Initialize enhanced store
enhanced_pentagon_store = EnhancedPentagonStore()

# Intent-Driven PACT Engine
class IntentDrivenPACTEngine:
    def __init__(self, store: EnhancedPentagonStore):
        self.store = store
        
    async def handle_intent_based_failure(self, failed_drone_id: str, mission_id: str) -> IntentAdaptationPlan:
        """Handle failure using intent hierarchy reasoning"""
        logger.info(f"Handling intent-based failure for drone {failed_drone_id}")
        
        # Generate adaptation plan using intent hierarchy
        trigger_event = f"COMMUNICATION_FAILURE:{failed_drone_id}"
        adaptation_plan = self.store.intent_engine.generate_intent_adaptation_plan(
            trigger_event, [failed_drone_id]
        )
        
        # Execute the adaptation plan
        await self._execute_intent_adaptation(adaptation_plan, mission_id)
        
        return adaptation_plan
    
    async def _execute_intent_adaptation(self, plan: IntentAdaptationPlan, mission_id: str):
        """Execute intent-based adaptation plan"""
        try:
            # Broadcast adaptation start
            await self.store.broadcast_intent_update({
                "type": "INTENT_ADAPTATION_STARTED",
                "mission_id": mission_id,
                "strategy": plan.adaptation_strategy,
                "affected_intents": len(plan.affected_intent_ids),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Execute each step
            for step in plan.execution_steps:
                logger.info(f"Executing step {step['step']}: {step['action']}")
                
                # Simulate step execution time
                await asyncio.sleep(step['estimated_duration'] / 10)  # Speed up for demo
                
                # Broadcast step completion
                await self.store.broadcast_intent_update({
                    "type": "ADAPTATION_STEP_COMPLETE",
                    "step": step['step'],
                    "action": step['action'],
                    "description": step['description']
                })
            
            # Mark adaptation as complete
            await self.store.broadcast_intent_update({
                "type": "INTENT_ADAPTATION_COMPLETE",
                "mission_id": mission_id,
                "success_probability": plan.success_probability,
                "impact": plan.estimated_impact,
                "message": "Mission continues with adapted intent hierarchy"
            })
            
            logger.info(f"Intent adaptation completed successfully for mission {mission_id}")
            
        except Exception as e:
            logger.error(f"Error executing intent adaptation: {e}")

# Initialize intent-driven engine
intent_pact_engine = IntentDrivenPACTEngine(enhanced_pentagon_store)

# Sample Intent Hierarchy Creation
def create_sample_intent_hierarchy():
    """Create a comprehensive intent hierarchy for demonstration"""
    
    # Strategic Level Intent
    strategic_intent = IntentNode(
        id="STRATEGIC-001",
        name="Secure Operational Area",
        description="Maintain complete situational awareness and security of designated operational area",
        intent_type=IntentType.STRATEGIC,
        status=IntentStatus.ACTIVE,
        priority=1.0,
        purpose="Ensure mission area remains secure from hostile activities and gather critical intelligence",
        success_criteria={
            "area_coverage": 100.0,
            "threat_detection_capability": 0.95,
            "intelligence_gathering_rate": 0.90
        },
        failure_conditions=["Area coverage drops below 60%", "Multiple sensor failures"],
        required_capabilities=["surveillance", "reconnaissance", "threat_detection"],
        resource_constraints={"minimum_drones": 2, "fuel_reserve": 30.0},
        context_dependencies={
            ContextType.ENVIRONMENTAL: ["weather_clear", "daylight_available"],
            ContextType.THREAT: ["threat_level_moderate_or_below"],
            ContextType.RESOURCE: ["sufficient_fuel", "communication_active"]
        },
        adaptation_rules=[
            {"condition": "drone_failure", "action": "redistribute_coverage"},
            {"condition": "weather_degradation", "action": "adjust_altitude"},
            {"condition": "threat_escalation", "action": "prioritize_defensive_posture"}
        ],
        assigned_assets=[],
        estimated_duration=180,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="COL.SMITH"
    )
    
    # Tactical Level Intents
    tactical_perimeter = IntentNode(
        id="TACTICAL-001",
        name="Monitor Northern Perimeter",
        description="Continuously monitor the northern boundary of the operational area",
        intent_type=IntentType.TACTICAL,
        status=IntentStatus.ACTIVE,
        priority=0.9,
        parent_id="STRATEGIC-001",
        purpose="Detect and track any movement or activity along the northern approach route",
        success_criteria={
            "detection_range": 5000.0,  # meters
            "update_frequency": 30.0,   # seconds
            "false_positive_rate": 0.05
        },
        failure_conditions=["No coverage for >5 minutes", "Detection range <3000m"],
        required_capabilities=["surveillance", "thermal_imaging"],
        resource_constraints={"minimum_drones": 1, "altitude_minimum": 1000.0},
        context_dependencies={
            ContextType.ENVIRONMENTAL: ["visibility_good"],
            ContextType.TACTICAL: ["no_friendly_forces_in_area"]
        },
        adaptation_rules=[
            {"condition": "primary_drone_failure", "action": "assign_backup_drone"},
            {"condition": "weather_poor", "action": "increase_sensor_sensitivity"}
        ],
        assigned_assets=["DRONE-001"],
        estimated_duration=120,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="COL.SMITH"
    )
    
    tactical_intelligence = IntentNode(
        id="TACTICAL-002",
        name="Gather Intelligence on Target Area",
        description="Collect detailed intelligence on specified target coordinates",
        intent_type=IntentType.TACTICAL,
        status=IntentStatus.ACTIVE,
        priority=0.8,
        parent_id="STRATEGIC-001",
        purpose="Gather actionable intelligence on target area activities and infrastructure",
        success_criteria={
            "image_resolution": "high_definition",
            "coverage_completeness": 0.95,
            "intelligence_value": 0.85
        },
        failure_conditions=["Unable to reach target area", "Image quality insufficient"],
        required_capabilities=["reconnaissance", "high_res_imaging", "signals_intelligence"],
        resource_constraints={"minimum_drones": 1, "fuel_for_return": 40.0},
        context_dependencies={
            ContextType.THREAT: ["target_area_accessible"],
            ContextType.ENVIRONMENTAL: ["weather_suitable_for_imaging"]
        },
        adaptation_rules=[
            {"condition": "target_area_hostile", "action": "increase_standoff_distance"},
            {"condition": "weather_poor", "action": "wait_for_better_conditions"}
        ],
        assigned_assets=["DRONE-002"],
        estimated_duration=90,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="COL.SMITH"
    )
    
    # Operational Level Intents
    operational_patrol = IntentNode(
        id="OPERATIONAL-001",
        name="Execute Northern Patrol Pattern",
        description="Fly specific patrol pattern along northern perimeter",
        intent_type=IntentType.OPERATIONAL,
        status=IntentStatus.ACTIVE,
        priority=0.9,
        parent_id="TACTICAL-001",
        purpose="Provide continuous visual and sensor coverage of northern approach",
        success_criteria={
            "pattern_completion_rate": 0.98,
            "sensor_uptime": 0.95,
            "position_accuracy": 5.0  # meters
        },
        failure_conditions=["GPS failure", "Sensor malfunction", "Fuel below 20%"],
        required_capabilities=["flight_control", "navigation", "surveillance"],
        resource_constraints={"fuel_minimum": 20.0, "altitude_range": [800, 1200]},
        context_dependencies={
            ContextType.ENVIRONMENTAL: ["wind_speed_acceptable"],
            ContextType.RESOURCE: ["gps_available", "fuel_sufficient"]
        },
        adaptation_rules=[
            {"condition": "high_winds", "action": "adjust_altitude"},
            {"condition": "fuel_low", "action": "request_replacement"}
        ],
        assigned_assets=["DRONE-001"],
        estimated_duration=60,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="FLIGHT_CONTROLLER"
    )
    
    # Contingency Intent
    contingency_backup = IntentNode(
        id="CONTINGENCY-001",
        name="Backup Perimeter Coverage",
        description="Provide backup coverage in case primary assets fail",
        intent_type=IntentType.CONTINGENCY,
        status=IntentStatus.SUSPENDED,  # Activated only when needed
        priority=0.7,
        parent_id="STRATEGIC-001",
        purpose="Ensure mission continuity when primary assets are compromised",
        success_criteria={
            "activation_time": 120.0,  # seconds
            "coverage_overlap": 0.8,
            "mission_continuity": 0.9
        },
        failure_conditions=["No backup assets available", "Activation time >300s"],
        required_capabilities=["rapid_deployment", "surveillance"],
        resource_constraints={"backup_drones_available": 1},
        context_dependencies={
            ContextType.RESOURCE: ["backup_assets_operational"]
        },
        adaptation_rules=[
            {"condition": "primary_asset_failure", "action": "immediate_activation"},
            {"condition": "multiple_failures", "action": "escalate_to_command"}
        ],
        assigned_assets=["DRONE-003"],
        estimated_duration=None,  # Duration depends on primary failure
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="COL.SMITH"
    )
    
    # Add all intents to the hierarchy
    intents = [strategic_intent, tactical_perimeter, tactical_intelligence, operational_patrol, contingency_backup]
    
    for intent in intents:
        enhanced_pentagon_store.intent_engine.add_intent_node(intent)
    
    logger.info("Sample intent hierarchy created successfully")

# Lifespan manager with intent hierarchy initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Pentagon Intent Hierarchy System starting up...")
    
    # Create sample intent hierarchy
    create_sample_intent_hierarchy()
    
    # Create sample drones (same as before but with intent integration)
    sample_drones = [
        {
            "id": "DRONE-001",
            "call_sign": "EAGLE-1",
            "drone_type": "MQ-9 Reaper",
            "position": {"lat": 38.8977, "lon": -77.0365, "alt": 5000},
            "status": DroneStatus.OPERATIONAL,
            "capabilities": ["surveillance", "strike", "reconnaissance", "thermal_imaging"],
            "fuel_level": 85.0,
            "comm_last_contact": datetime.utcnow(),
            "security_clearance": SecurityLevel.SECRET,
            "assigned_intents": ["TACTICAL-001", "OPERATIONAL-001"]
        },
        {
            "id": "DRONE-002",
            "call_sign": "HAWK-1",
            "drone_type": "RQ-4 Global Hawk",
            "position": {"lat": 38.9072, "lon": -77.0369, "alt": 5200},
            "status": DroneStatus.OPERATIONAL,
            "capabilities": ["surveillance", "reconnaissance", "signals_intelligence", "high_res_imaging"],
            "fuel_level": 92.0,
            "comm_last_contact": datetime.utcnow(),
            "security_clearance": SecurityLevel.TOP_SECRET,
            "assigned_intents": ["TACTICAL-002"]
        },
        {
            "id": "DRONE-003",
            "call_sign": "FALCON-1",
            "drone_type": "MQ-9 Reaper",
            "position": {"lat": 38.8872, "lon": -77.0267, "alt": 4800},
            "status": DroneStatus.OPERATIONAL,
            "capabilities": ["surveillance", "strike", "rapid_deployment"],
            "fuel_level": 78.0,
            "comm_last_contact": datetime.utcnow(),
            "security_clearance": SecurityLevel.SECRET,
            "assigned_intents": ["CONTINGENCY-001"]
        }
    ]
    
    for drone in sample_drones:
        enhanced_pentagon_store.drones[drone["id"]] = drone
    
    logger.info("Pentagon Intent Hierarchy System initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Pentagon Intent Hierarchy System shutting down...")

# Initialize FastAPI app with intent hierarchy
app = FastAPI(
    title="Pentagon Intent Hierarchy System",
    description="CLASSIFIED - Intent-driven drone swarm coordination with hierarchical goal reasoning",
    version="2.0.0-INTENT-HIERARCHY",
    lifespan=lifespan
)

# CORS for secure Pentagon networks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pentagon.mil", "https://defense.gov"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Intent Hierarchy Endpoints
@app.get("/pentagon/intent-hierarchy")
async def get_intent_hierarchy():
    """Get the complete intent hierarchy structure"""
    root_intents = enhanced_pentagon_store.intent_engine.get_root_intents()
    
    def build_hierarchy_tree(intent: IntentNode) -> Dict[str, Any]:
        children = enhanced_pentagon_store.intent_engine.get_children(intent.id)
        return {
            "intent": intent.dict(),
            "children": [build_hierarchy_tree(child) for child in children]
        }
    
    hierarchy_tree = [build_hierarchy_tree(root) for root in root_intents]
    
    return {
        "hierarchy": hierarchy_tree,
        "total_intents": len(enhanced_pentagon_store.intent_engine.intent_nodes),
        "active_intents": len([i for i in enhanced_pentagon_store.intent_engine.intent_nodes.values() if i.status == IntentStatus.ACTIVE]),
        "timestamp": datetime.utcnow()
    }

@app.get("/pentagon/intent-hierarchy/{intent_id}")
async def get_intent_details(intent_id: str):
    """Get detailed information about a specific intent"""
    intent = enhanced_pentagon_store.intent_engine.intent_nodes.get(intent_id)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    # Get related intents
    children = enhanced_pentagon_store.intent_engine.get_children(intent_id)
    descendants = enhanced_pentagon_store.intent_engine.get_descendants(intent_id)
    parent = None
    if intent.parent_id:
        parent = enhanced_pentagon_store.intent_engine.intent_nodes.get(intent.parent_id)
    
    # Get assigned assets details
    assigned_drones = []
    for drone_id in enhanced_pentagon_store.drones:
        drone = enhanced_pentagon_store.drones[drone_id]
        if intent_id in drone.get("assigned_intents", []):
            assigned_drones.append(drone)
    
    return {
        "intent": intent.dict(),
        "parent": parent.dict() if parent else None,
        "children": [child.dict() for child in children],
        "descendants_count": len(descendants),
        "assigned_drones": assigned_drones,
        "effectiveness_score": calculate_intent_effectiveness(intent),
        "adaptation_history": [plan for plan in enhanced_pentagon_store.intent_engine.adaptation_history 
                              if intent_id in plan.affected_intent_ids]
    }

def calculate_intent_effectiveness(intent: IntentNode) -> float:
    """Calculate the effectiveness score of an intent based on current status"""
    base_score = 1.0
    
    # Reduce score based on status
    if intent.status == IntentStatus.FAILED:
        return 0.0
    elif intent.status == IntentStatus.SUSPENDED:
        base_score *= 0.3
    elif intent.status == IntentStatus.ADAPTING:
        base_score *= 0.7
    
    # Adjust based on assigned assets
    assigned_count = len(intent.assigned_assets)
    if assigned_count == 0 and intent.intent_type != IntentType.CONTINGENCY:
        base_score *= 0.5
    
    # Consider priority weight
    base_score *= intent.priority
    
    return min(1.0, base_score)

@app.post("/pentagon/intent-hierarchy/adapt")
async def trigger_intent_adaptation(trigger_event: str, affected_assets: List[str]):
    """Manually trigger intent hierarchy adaptation"""
    try:
        adaptation_plan = enhanced_pentagon_store.intent_engine.generate_intent_adaptation_plan(
            trigger_event, affected_assets
        )
        
        # Execute the adaptation if it looks viable
        if adaptation_plan.success_probability > 0.5:
            await intent_pact_engine._execute_intent_adaptation(adaptation_plan, "MISSION-ALPHA-001")
            
        return {
            "adaptation_triggered": True,
            "plan": adaptation_plan.dict(),
            "execution_started": adaptation_plan.success_probability > 0.5
        }
        
    except Exception as e:
        logger.error(f"Error triggering intent adaptation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pentagon/intent-analytics")
async def get_intent_analytics():
    """Get analytics about intent hierarchy performance"""
    all_intents = list(enhanced_pentagon_store.intent_engine.intent_nodes.values())
    
    # Status distribution
    status_distribution = {}
    for status in IntentStatus:
        status_distribution[status.value] = len([i for i in all_intents if i.status == status])
    
    # Type distribution
    type_distribution = {}
    for intent_type in IntentType:
        type_distribution[intent_type.value] = len([i for i in all_intents if i.intent_type == intent_type])
    
    # Priority analysis
    priority_ranges = {
        "HIGH (0.8-1.0)": len([i for i in all_intents if i.priority >= 0.8]),
        "MEDIUM (0.5-0.8)": len([i for i in all_intents if 0.5 <= i.priority < 0.8]),
        "LOW (0.0-0.5)": len([i for i in all_intents if i.priority < 0.5])
    }
    
    # Adaptation metrics
    adaptation_metrics = {
        "total_adaptations": len(enhanced_pentagon_store.intent_engine.adaptation_history),
        "average_success_probability": sum(plan.success_probability for plan in enhanced_pentagon_store.intent_engine.adaptation_history) / max(1, len(enhanced_pentagon_store.intent_engine.adaptation_history)),
        "most_common_strategy": "TACTICAL_REASSIGNMENT",  # Would calculate this from history
        "adaptation_frequency": "0.5 per hour"  # Would calculate based on timestamps
    }
    
    # Intent effectiveness
    effectiveness_scores = [calculate_intent_effectiveness(intent) for intent in all_intents]
    average_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0.0
    
    return {
        "hierarchy_health": {
            "total_intents": len(all_intents),
            "active_percentage": (status_distribution.get("ACTIVE", 0) / len(all_intents) * 100) if all_intents else 0,
            "average_effectiveness": average_effectiveness,
            "hierarchy_depth": calculate_hierarchy_depth()
        },
        "status_distribution": status_distribution,
        "type_distribution": type_distribution,
        "priority_distribution": priority_ranges,
        "adaptation_metrics": adaptation_metrics,
        "timestamp": datetime.utcnow()
    }

def calculate_hierarchy_depth() -> int:
    """Calculate the maximum depth of the intent hierarchy"""
    def get_depth(intent_id: str, current_depth: int = 0) -> int:
        children = enhanced_pentagon_store.intent_engine.get_children(intent_id)
        if not children:
            return current_depth
        return max(get_depth(child.id, current_depth + 1) for child in children)
    
    root_intents = enhanced_pentagon_store.intent_engine.get_root_intents()
    if not root_intents:
        return 0
    
    return max(get_depth(root.id) for root in root_intents) + 1

@app.post("/pentagon/simulate-intent-failure/{intent_id}")
async def simulate_intent_failure(intent_id: str):
    """Simulate intent failure for testing adaptation"""
    intent = enhanced_pentagon_store.intent_engine.intent_nodes.get(intent_id)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    # Get assigned assets for this intent
    affected_assets = []
    for drone_id, drone in enhanced_pentagon_store.drones.items():
        if intent_id in drone.get("assigned_intents", []):
            affected_assets.append(drone_id)
    
    if not affected_assets:
        return {
            "message": f"Intent {intent_id} has no assigned assets to fail",
            "intent_name": intent.name,
            "adaptation_triggered": False
        }
    
    # Trigger intent-based adaptation
    try:
        adaptation_plan = await intent_pact_engine.handle_intent_based_failure(
            affected_assets[0], "MISSION-ALPHA-001"
        )
        
        return {
            "message": f"Intent failure simulated for {intent.name}",
            "affected_assets": affected_assets,
            "adaptation_plan": adaptation_plan.dict(),
            "adaptation_triggered": True
        }
        
    except Exception as e:
        logger.error(f"Error simulating intent failure: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced Pentagon Status with Intent Integration
@app.get("/pentagon/status")
async def get_enhanced_pentagon_status():
    """Get overall system status including intent hierarchy health"""
    operational_drones = sum(1 for d in enhanced_pentagon_store.drones.values() 
                           if d.get("status") == DroneStatus.OPERATIONAL)
    
    intent_health = {
        "total_intents": len(enhanced_pentagon_store.intent_engine.intent_nodes),
        "active_intents": len([i for i in enhanced_pentagon_store.intent_engine.intent_nodes.values() 
                              if i.status == IntentStatus.ACTIVE]),
        "failed_intents": len([i for i in enhanced_pentagon_store.intent_engine.intent_nodes.values() 
                              if i.status == IntentStatus.FAILED]),
        "adapting_intents": len([i for i in enhanced_pentagon_store.intent_engine.intent_nodes.values() 
                                if i.status == IntentStatus.ADAPTING])
    }
    
    # Calculate overall mission effectiveness
    all_intents = list(enhanced_pentagon_store.intent_engine.intent_nodes.values())
    effectiveness_scores = [calculate_intent_effectiveness(intent) for intent in all_intents]
    overall_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0.0
    
    return {
        "system_status": "OPERATIONAL" if overall_effectiveness > 0.7 else "DEGRADED",
        "classification": "RESTRICTED",
        "timestamp": datetime.utcnow(),
        "drone_metrics": {
            "operational_drones": operational_drones,
            "total_drones": len(enhanced_pentagon_store.drones),
            "active_failures": len(enhanced_pentagon_store.active_failures)
        },
        "intent_hierarchy_health": intent_health,
        "mission_effectiveness": {
            "overall_score": overall_effectiveness,
            "strategic_effectiveness": calculate_strategic_effectiveness(),
            "tactical_effectiveness": calculate_tactical_effectiveness(),
            "operational_effectiveness": calculate_operational_effectiveness()
        },
        "adaptation_status": {
            "total_adaptations": len(enhanced_pentagon_store.intent_engine.adaptation_history),
            "recent_adaptations": len([p for p in enhanced_pentagon_store.intent_engine.adaptation_history 
                                     if (datetime.utcnow() - datetime.fromisoformat(p.trigger_event.split(':')[0] if ':' in p.trigger_event else datetime.utcnow().isoformat())).total_seconds() < 3600])
        }
    }

def calculate_strategic_effectiveness() -> float:
    """Calculate effectiveness of strategic level intents"""
    strategic_intents = [i for i in enhanced_pentagon_store.intent_engine.intent_nodes.values() 
                        if i.intent_type == IntentType.STRATEGIC]
    if not strategic_intents:
        return 1.0
    
    scores = [calculate_intent_effectiveness(intent) for intent in strategic_intents]
    return sum(scores) / len(scores)

def calculate_tactical_effectiveness() -> float:
    """Calculate effectiveness of tactical level intents"""
    tactical_intents = [i for i in enhanced_pentagon_store.intent_engine.intent_nodes.values() 
                       if i.intent_type == IntentType.TACTICAL]
    if not tactical_intents:
        return 1.0
    
    scores = [calculate_intent_effectiveness(intent) for intent in tactical_intents]
    return sum(scores) / len(scores)

def calculate_operational_effectiveness() -> float:
    """Calculate effectiveness of operational level intents"""
    operational_intents = [i for i in enhanced_pentagon_store.intent_engine.intent_nodes.values() 
                          if i.intent_type == IntentType.OPERATIONAL]
    if not operational_intents:
        return 1.0
    
    scores = [calculate_intent_effectiveness(intent) for intent in operational_intents]
    return sum(scores) / len(scores)

# Enhanced WebSocket for Intent Updates
@app.websocket("/pentagon/intent-command-center")
async def intent_command_center_websocket(websocket: WebSocket):
    """WebSocket for real-time intent hierarchy updates"""
    await websocket.accept()
    enhanced_pentagon_store.websocket_connections.add(websocket)
    
    try:
        # Send initial intent hierarchy status
        await websocket.send_json({
            "type": "INTENT_HIERARCHY_STATUS",
            "message": "Connected to Pentagon Intent Command Center",
            "classification": "RESTRICTED",
            "intent_summary": {
                "total_intents": len(enhanced_pentagon_store.intent_engine.intent_nodes),
                "active_intents": len([i for i in enhanced_pentagon_store.intent_engine.intent_nodes.values() if i.status == IntentStatus.ACTIVE]),
                "hierarchy_depth": calculate_hierarchy_depth(),
                "adaptation_readiness": "READY"
            },
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep connection alive and send periodic intent updates
        while True:
            await asyncio.sleep(15)  # Send updates every 15 seconds
            
            # Calculate current intent health metrics
            all_intents = list(enhanced_pentagon_store.intent_engine.intent_nodes.values())
            effectiveness_scores = [calculate_intent_effectiveness(intent) for intent in all_intents]
            avg_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0.0
            
            await websocket.send_json({
                "type": "INTENT_HEALTH_UPDATE",
                "overall_effectiveness": avg_effectiveness,
                "strategic_effectiveness": calculate_strategic_effectiveness(),
                "tactical_effectiveness": calculate_tactical_effectiveness(),
                "operational_effectiveness": calculate_operational_effectiveness(),
                "active_adaptations": len([i for i in all_intents if i.status == IntentStatus.ADAPTING]),
                "timestamp": datetime.utcnow().isoformat()
            })
            
    except WebSocketDisconnect:
        enhanced_pentagon_store.websocket_connections.discard(websocket)
    except Exception as e:
        logger.error(f"Intent WebSocket error: {e}")
        enhanced_pentagon_store.websocket_connections.discard(websocket)

# Background Intent Monitoring
async def monitor_intent_health():
    """Continuously monitor intent hierarchy health and trigger adaptations"""
    while True:
        try:
            current_time = datetime.utcnow()
            
            # Check for intent deadline violations
            for intent in enhanced_pentagon_store.intent_engine.intent_nodes.values():
                if (intent.deadline and 
                    current_time > intent.deadline and 
                    intent.status == IntentStatus.ACTIVE):
                    
                    logger.warning(f"Intent {intent.id} has exceeded deadline")
                    intent.status = IntentStatus.FAILED
                    
                    # Trigger adaptation for deadline violation
                    await enhanced_pentagon_store.broadcast_intent_update({
                        "type": "INTENT_DEADLINE_VIOLATION",
                        "intent_id": intent.id,
                        "intent_name": intent.name,
                        "deadline": intent.deadline.isoformat(),
                        "current_time": current_time.isoformat()
                    })
            
            # Check for intent hierarchy inconsistencies
            await validate_intent_hierarchy_consistency()
            
            await asyncio.sleep(60)  # Check every minute
            
        except Exception as e:
            logger.error(f"Error in intent health monitoring: {e}")
            await asyncio.sleep(120)

async def validate_intent_hierarchy_consistency():
    """Validate that the intent hierarchy is consistent and healthy"""
    issues = []
    
    for intent in enhanced_pentagon_store.intent_engine.intent_nodes.values():
        # Check for orphaned intents
        if intent.parent_id and intent.parent_id not in enhanced_pentagon_store.intent_engine.intent_nodes:
            issues.append(f"Intent {intent.id} has invalid parent {intent.parent_id}")
        
        # Check for circular dependencies
        visited = set()
        current = intent
        while current.parent_id and current.parent_id not in visited:
            visited.add(current.id)
            current = enhanced_pentagon_store.intent_engine.intent_nodes.get(current.parent_id)
            if not current:
                break
            if current.id == intent.id:
                issues.append(f"Circular dependency detected involving intent {intent.id}")
                break
    
    if issues:
        logger.warning(f"Intent hierarchy consistency issues detected: {issues}")
        await enhanced_pentagon_store.broadcast_intent_update({
            "type": "HIERARCHY_CONSISTENCY_WARNING",
            "issues": issues,
            "timestamp": datetime.utcnow().isoformat()
        })

# Start background monitoring on startup
@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(monitor_intent_health())

# Development server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "pentagon_intent_hierarchy:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
