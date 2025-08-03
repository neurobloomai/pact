# Pentagon-Ready Drone Swarm Coordination Backend
from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Set
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import uuid
import logging
from contextlib import asynccontextmanager
import math

# Configure military-grade logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [CLASSIFICATION: RESTRICTED] - %(message)s'
)
logger = logging.getLogger(__name__)

# Security Classifications
class SecurityLevel(str, Enum):
    UNCLASSIFIED = "UNCLASSIFIED"
    CONFIDENTIAL = "CONFIDENTIAL"
    SECRET = "SECRET"
    TOP_SECRET = "TOP_SECRET"

# Mission Status Enums
class MissionStatus(str, Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPROMISED = "COMPROMISED"
    REASSIGNING = "REASSIGNING"
    COMPLETED = "COMPLETED"
    ABORTED = "ABORTED"

class DroneStatus(str, Enum):
    OPERATIONAL = "OPERATIONAL"
    COMM_FAILURE = "COMM_FAILURE"
    DAMAGED = "DAMAGED"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"

class TaskPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

# Pydantic Models for Defense Operations
class DroneUnit(BaseModel):
    id: str
    call_sign: str
    drone_type: str = Field(..., description="Type of drone (e.g., MQ-9, RQ-4)")
    position: Dict[str, float] = Field(..., description="GPS coordinates {lat, lon, alt}")
    status: DroneStatus
    capabilities: List[str] = Field(..., description="Mission capabilities")
    fuel_level: float = Field(..., ge=0.0, le=100.0)
    comm_last_contact: datetime
    assigned_tasks: List[str] = []
    security_clearance: SecurityLevel

class MissionObjective(BaseModel):
    id: str
    name: str
    description: str
    priority: TaskPriority
    required_capabilities: List[str]
    target_coordinates: Dict[str, float]
    estimated_duration: int = Field(..., description="Duration in minutes")
    security_classification: SecurityLevel
    deadline: Optional[datetime] = None

class SwarmConfiguration(BaseModel):
    formation_type: str = Field(..., regex=r'^(diamond|wedge|line|circle|grid)$')
    spacing_meters: float = Field(..., ge=10.0, le=1000.0)
    altitude_agl: float = Field(..., ge=50.0, le=15000.0)
    communication_frequency: str
    backup_frequency: str

class MissionPACT(BaseModel):
    mission_id: str
    title: str
    description: str
    security_classification: SecurityLevel
    status: MissionStatus
    primary_objectives: List[MissionObjective]
    backup_objectives: List[MissionObjective]
    assigned_drones: List[str]
    swarm_config: SwarmConfiguration
    intent_hierarchy: Dict[str, Any]
    failure_protocols: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    mission_commander: str

class CommunicationFailure(BaseModel):
    drone_id: str
    failure_time: datetime
    last_known_position: Dict[str, float]
    last_known_status: str
    estimated_fuel_remaining: float
    assigned_objectives: List[str]

class ReassignmentPlan(BaseModel):
    failed_drone_id: str
    replacement_drones: List[str]
    objective_redistribution: Dict[str, List[str]]
    formation_adjustment: SwarmConfiguration
    estimated_delay: int = Field(..., description="Delay in minutes")
    confidence_score: float = Field(..., ge=0.0, le=1.0)

# Pentagon Command Center Data Store
class PentagonDataStore:
    def __init__(self):
        self.missions: Dict[str, MissionPACT] = {}
        self.drones: Dict[str, DroneUnit] = {}
        self.active_failures: Dict[str, CommunicationFailure] = {}
        self.reassignment_history: List[Dict] = []
        self.websocket_connections: Set[WebSocket] = set()
        
    async def broadcast_status_update(self, message: Dict):
        """Broadcast status updates to all connected command centers"""
        if self.websocket_connections:
            disconnected = set()
            for connection in self.websocket_connections:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.add(connection)
            
            # Remove disconnected connections
            self.websocket_connections -= disconnected

# Initialize Pentagon-grade data store
pentagon_store = PentagonDataStore()

# PACT Reassignment Engine
class PACTReassignmentEngine:
    def __init__(self, store: PentagonDataStore):
        self.store = store
        
    async def detect_communication_failure(self, drone_id: str) -> bool:
        """Detect if a drone has lost communication"""
        drone = self.store.drones.get(drone_id)
        if not drone:
            return False
            
        time_since_contact = datetime.utcnow() - drone.comm_last_contact
        return time_since_contact > timedelta(minutes=2)  # 2-minute threshold
    
    async def calculate_mission_impact(self, failed_drone: DroneUnit) -> Dict[str, Any]:
        """Calculate the impact of drone failure on mission objectives"""
        impact = {
            "affected_objectives": [],
            "critical_capabilities_lost": [],
            "mission_delay_estimate": 0,
            "success_probability_reduction": 0.0
        }
        
        # Find missions with this drone
        for mission in self.store.missions.values():
            if failed_drone.id in mission.assigned_drones:
                for objective in mission.primary_objectives:
                    # Check if drone capabilities match objective requirements
                    if any(cap in failed_drone.capabilities for cap in objective.required_capabilities):
                        impact["affected_objectives"].append(objective.id)
                        impact["mission_delay_estimate"] += 15  # Base 15-minute delay per objective
                        
                        if objective.priority == TaskPriority.CRITICAL:
                            impact["success_probability_reduction"] += 0.25
        
        return impact
    
    async def find_replacement_drones(self, failed_drone: DroneUnit, mission_id: str) -> List[DroneUnit]:
        """Find suitable replacement drones for failed unit"""
        mission = self.store.missions.get(mission_id)
        if not mission:
            return []
        
        candidates = []
        for drone in self.store.drones.values():
            if (drone.status == DroneStatus.OPERATIONAL and 
                drone.id != failed_drone.id and
                drone.id not in mission.assigned_drones and
                drone.fuel_level > 30.0):  # Minimum fuel requirement
                
                # Check capability overlap
                capability_match = len(set(drone.capabilities) & set(failed_drone.capabilities))
                if capability_match > 0:
                    candidates.append((drone, capability_match))
        
        # Sort by capability match and fuel level
        candidates.sort(key=lambda x: (x[1], x[0].fuel_level), reverse=True)
        return [drone for drone, _ in candidates[:3]]  # Top 3 candidates
    
    async def generate_reassignment_plan(self, failure: CommunicationFailure, mission_id: str) -> ReassignmentPlan:
        """Generate comprehensive reassignment plan using PACT hierarchy"""
        failed_drone = self.store.drones.get(failure.drone_id)
        if not failed_drone:
            raise ValueError(f"Failed drone {failure.drone_id} not found")
        
        replacement_candidates = await self.find_replacement_drones(failed_drone, mission_id)
        
        if not replacement_candidates:
            logger.warning(f"No suitable replacement drones found for {failure.drone_id}")
            return None
        
        # Select best replacement(s)
        selected_replacements = replacement_candidates[:min(2, len(replacement_candidates))]
        
        # Redistribute objectives
        mission = self.store.missions[mission_id]
        objective_redistribution = {}
        
        for replacement in selected_replacements:
            objective_redistribution[replacement.id] = []
            
        # Distribute failed drone's objectives among replacements
        failed_objectives = failure.assigned_objectives
        for i, obj_id in enumerate(failed_objectives):
            replacement_idx = i % len(selected_replacements)
            replacement_id = selected_replacements[replacement_idx].id
            objective_redistribution[replacement_id].append(obj_id)
        
        # Adjust swarm formation
        new_formation = SwarmConfiguration(
            formation_type=mission.swarm_config.formation_type,
            spacing_meters=mission.swarm_config.spacing_meters * 1.2,  # Increase spacing
            altitude_agl=mission.swarm_config.altitude_agl,
            communication_frequency=mission.swarm_config.backup_frequency,  # Switch to backup freq
            backup_frequency=mission.swarm_config.communication_frequency
        )
        
        confidence_score = min(0.95, len(selected_replacements) * 0.4 + 0.3)
        estimated_delay = max(10, 30 - (len(selected_replacements) * 10))
        
        return ReassignmentPlan(
            failed_drone_id=failure.drone_id,
            replacement_drones=[d.id for d in selected_replacements],
            objective_redistribution=objective_redistribution,
            formation_adjustment=new_formation,
            estimated_delay=estimated_delay,
            confidence_score=confidence_score
        )
    
    async def execute_reassignment(self, plan: ReassignmentPlan, mission_id: str) -> bool:
        """Execute the reassignment plan"""
        try:
            mission = self.store.missions[mission_id]
            
            # Remove failed drone from mission
            if plan.failed_drone_id in mission.assigned_drones:
                mission.assigned_drones.remove(plan.failed_drone_id)
            
            # Add replacement drones
            for drone_id in plan.replacement_drones:
                if drone_id not in mission.assigned_drones:
                    mission.assigned_drones.append(drone_id)
                    
                # Update drone assignments
                drone = self.store.drones[drone_id]
                new_objectives = plan.objective_redistribution.get(drone_id, [])
                drone.assigned_tasks.extend(new_objectives)
            
            # Update swarm configuration
            mission.swarm_config = plan.formation_adjustment
            mission.status = MissionStatus.ACTIVE  # Resume active status
            mission.updated_at = datetime.utcnow()
            
            # Log reassignment
            self.store.reassignment_history.append({
                "timestamp": datetime.utcnow(),
                "mission_id": mission_id,
                "failed_drone": plan.failed_drone_id,
                "replacements": plan.replacement_drones,
                "confidence": plan.confidence_score
            })
            
            logger.info(f"Successfully executed reassignment plan for mission {mission_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute reassignment plan: {e}")
            return False

# Initialize PACT engine
pact_engine = PACTReassignmentEngine(pentagon_store)

# Background monitoring task
async def monitor_drone_communications():
    """Continuously monitor drone communications and trigger reassignments"""
    while True:
        try:
            for mission_id, mission in pentagon_store.missions.items():
                if mission.status != MissionStatus.ACTIVE:
                    continue
                    
                for drone_id in mission.assigned_drones:
                    if await pact_engine.detect_communication_failure(drone_id):
                        drone = pentagon_store.drones.get(drone_id)
                        if drone and drone.status != DroneStatus.COMM_FAILURE:
                            # Mark drone as communication failure
                            drone.status = DroneStatus.COMM_FAILURE
                            mission.status = MissionStatus.COMPROMISED
                            
                            # Create failure record
                            failure = CommunicationFailure(
                                drone_id=drone_id,
                                failure_time=datetime.utcnow(),
                                last_known_position=drone.position,
                                last_known_status=drone.status.value,
                                estimated_fuel_remaining=drone.fuel_level,
                                assigned_objectives=drone.assigned_tasks.copy()
                            )
                            
                            pentagon_store.active_failures[drone_id] = failure
                            
                            # Trigger automatic reassignment
                            await trigger_automatic_reassignment(failure, mission_id)
            
            await asyncio.sleep(30)  # Monitor every 30 seconds
            
        except Exception as e:
            logger.error(f"Error in communication monitoring: {e}")
            await asyncio.sleep(60)

async def trigger_automatic_reassignment(failure: CommunicationFailure, mission_id: str):
    """Trigger automatic PACT-based reassignment"""
    try:
        logger.warning(f"Communication failure detected for drone {failure.drone_id}")
        
        # Update mission status
        mission = pentagon_store.missions[mission_id]
        mission.status = MissionStatus.REASSIGNING
        
        # Broadcast failure notification
        await pentagon_store.broadcast_status_update({
            "type": "COMMUNICATION_FAILURE",
            "mission_id": mission_id,
            "failed_drone": failure.drone_id,
            "timestamp": failure.failure_time.isoformat(),
            "classification": mission.security_classification
        })
        
        # Generate reassignment plan
        plan = await pact_engine.generate_reassignment_plan(failure, mission_id)
        
        if plan:
            # Execute reassignment
            success = await pact_engine.execute_reassignment(plan, mission_id)
            
            if success:
                # Broadcast successful reassignment
                await pentagon_store.broadcast_status_update({
                    "type": "REASSIGNMENT_COMPLETE",
                    "mission_id": mission_id,
                    "plan": plan.dict(),
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "Mission continues seamlessly"
                })
                
                logger.info(f"Mission {mission_id} reassignment completed successfully")
            else:
                logger.error(f"Failed to execute reassignment for mission {mission_id}")
        else:
            logger.error(f"Could not generate reassignment plan for mission {mission_id}")
            
    except Exception as e:
        logger.error(f"Error in automatic reassignment: {e}")

# Lifespan manager with Pentagon initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - Initialize Pentagon systems
    logger.info("Pentagon Drone Swarm Coordination System starting up...")
    
    # Create sample drone fleet
    sample_drones = [
        DroneUnit(
            id="DRONE-001",
            call_sign="EAGLE-1",
            drone_type="MQ-9 Reaper",
            position={"lat": 38.8977, "lon": -77.0365, "alt": 5000},
            status=DroneStatus.OPERATIONAL,
            capabilities=["surveillance", "strike", "reconnaissance"],
            fuel_level=85.0,
            comm_last_contact=datetime.utcnow(),
            security_clearance=SecurityLevel.SECRET
        ),
        DroneUnit(
            id="DRONE-002",
            call_sign="HAWK-1",
            drone_type="RQ-4 Global Hawk",
            position={"lat": 38.9072, "lon": -77.0369, "alt": 5200},
            status=DroneStatus.OPERATIONAL,
            capabilities=["surveillance", "reconnaissance", "signals_intelligence"],
            fuel_level=92.0,
            comm_last_contact=datetime.utcnow(),
            security_clearance=SecurityLevel.TOP_SECRET
        ),
        DroneUnit(
            id="DRONE-003",
            call_sign="FALCON-1",
            drone_type="MQ-9 Reaper",
            position={"lat": 38.8872, "lon": -77.0267, "alt": 4800},
            status=DroneStatus.OPERATIONAL,
            capabilities=["surveillance", "strike"],
            fuel_level=78.0,
            comm_last_contact=datetime.utcnow(),
            security_clearance=SecurityLevel.SECRET
        )
    ]
    
    for drone in sample_drones:
        pentagon_store.drones[drone.id] = drone
    
    # Create sample mission
    sample_mission = MissionPACT(
        mission_id="MISSION-ALPHA-001",
        title="Operation Watchful Eye",
        description="High-priority surveillance mission in designated AOR",
        security_classification=SecurityLevel.SECRET,
        status=MissionStatus.ACTIVE,
        primary_objectives=[
            MissionObjective(
                id="OBJ-001",
                name="Perimeter Surveillance",
                description="Monitor designated perimeter for hostile activity",
                priority=TaskPriority.CRITICAL,
                required_capabilities=["surveillance"],
                target_coordinates={"lat": 38.9000, "lon": -77.0300, "alt": 0},
                estimated_duration=120,
                security_classification=SecurityLevel.SECRET
            )
        ],
        backup_objectives=[],
        assigned_drones=["DRONE-001", "DRONE-002"],
        swarm_config=SwarmConfiguration(
            formation_type="diamond",
            spacing_meters=200.0,
            altitude_agl=5000.0,
            communication_frequency="251.0",
            backup_frequency="243.0"
        ),
        intent_hierarchy={
            "mission_goal": "maintain_surveillance",
            "critical_tasks": ["perimeter_monitoring", "threat_detection"],
            "failure_protocols": ["automatic_reassignment", "backup_frequency_switch"]
        },
        failure_protocols={
            "comm_failure_threshold": 120,
            "auto_reassignment": True,
            "backup_procedures": ["frequency_switch", "formation_adjustment"]
        },
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        mission_commander="COL.SMITH"
    )
    
    pentagon_store.missions[sample_mission.mission_id] = sample_mission
    
    # Start background monitoring
    asyncio.create_task(monitor_drone_communications())
    
    logger.info("Pentagon systems initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Pentagon Drone Swarm Coordination System shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Pentagon Drone Swarm Coordination API",
    description="CLASSIFIED - Defense-grade drone swarm coordination with PACT failure handling",
    version="1.0.0-PENTAGON",
    lifespan=lifespan
)

# CORS for secure Pentagon networks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pentagon.mil", "https://defense.gov"],  # Restrict to defense domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Pentagon Command Center Endpoints
@app.get("/pentagon/status")
async def get_pentagon_status():
    """Get overall system status"""
    operational_drones = sum(1 for d in pentagon_store.drones.values() if d.status == DroneStatus.OPERATIONAL)
    active_missions = sum(1 for m in pentagon_store.missions.values() if m.status == MissionStatus.ACTIVE)
    active_failures = len(pentagon_store.active_failures)
    
    return {
        "system_status": "OPERATIONAL",
        "classification": "RESTRICTED",
        "timestamp": datetime.utcnow(),
        "metrics": {
            "operational_drones": operational_drones,
            "total_drones": len(pentagon_store.drones),
            "active_missions": active_missions,
            "active_failures": active_failures,
            "reassignments_completed": len(pentagon_store.reassignment_history)
        }
    }

@app.get("/pentagon/missions", response_model=List[MissionPACT])
async def get_active_missions():
    """Get all active missions"""
    return list(pentagon_store.missions.values())

@app.get("/pentagon/missions/{mission_id}", response_model=MissionPACT)
async def get_mission_details(mission_id: str):
    """Get detailed mission information"""
    mission = pentagon_store.missions.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission

@app.get("/pentagon/drones")
async def get_drone_fleet():
    """Get current drone fleet status"""
    return {
        "drones": list(pentagon_store.drones.values()),
        "summary": {
            "total": len(pentagon_store.drones),
            "operational": sum(1 for d in pentagon_store.drones.values() if d.status == DroneStatus.OPERATIONAL),
            "comm_failure": sum(1 for d in pentagon_store.drones.values() if d.status == DroneStatus.COMM_FAILURE),
            "offline": sum(1 for d in pentagon_store.drones.values() if d.status == DroneStatus.OFFLINE)
        }
    }

@app.post("/pentagon/simulate-failure/{drone_id}")
async def simulate_communication_failure(drone_id: str):
    """Simulate communication failure for testing PACT reassignment"""
    drone = pentagon_store.drones.get(drone_id)
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")
    
    # Simulate communication failure
    drone.status = DroneStatus.COMM_FAILURE
    drone.comm_last_contact = datetime.utcnow() - timedelta(minutes=5)
    
    # Find mission with this drone
    mission_id = None
    for mid, mission in pentagon_store.missions.items():
        if drone_id in mission.assigned_drones and mission.status == MissionStatus.ACTIVE:
            mission_id = mid
            break
    
    if mission_id:
        # Create failure record
        failure = CommunicationFailure(
            drone_id=drone_id,
            failure_time=datetime.utcnow(),
            last_known_position=drone.position,
            last_known_status="OPERATIONAL",
            estimated_fuel_remaining=drone.fuel_level,
            assigned_objectives=drone.assigned_tasks.copy()
        )
        
        pentagon_store.active_failures[drone_id] = failure
        
        # Trigger reassignment
        await trigger_automatic_reassignment(failure, mission_id)
        
        return {
            "message": f"Communication failure simulated for {drone_id}",
            "reassignment_triggered": True,
            "mission_affected": mission_id
        }
    
    return {
        "message": f"Communication failure simulated for {drone_id}",
        "reassignment_triggered": False,
        "reason": "Drone not assigned to active mission"
    }

@app.get("/pentagon/failures")
async def get_active_failures():
    """Get all active communication failures"""
    return {
        "active_failures": list(pentagon_store.active_failures.values()),
        "count": len(pentagon_store.active_failures)
    }

@app.get("/pentagon/reassignment-history")
async def get_reassignment_history():
    """Get history of PACT reassignments"""
    return {
        "reassignments": pentagon_store.reassignment_history,
        "total_reassignments": len(pentagon_store.reassignment_history),
        "success_rate": 100.0  # In this demo, all succeed
    }

@app.websocket("/pentagon/command-center")
async def command_center_websocket(websocket: WebSocket):
    """WebSocket for real-time Pentagon command center updates"""
    await websocket.accept()
    pentagon_store.websocket_connections.add(websocket)
    
    try:
        # Send initial status
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "message": "Connected to Pentagon Command Center",
            "classification": "RESTRICTED",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep connection alive and send periodic updates
        while True:
            await asyncio.sleep(10)
            
            # Send periodic status update
            await websocket.send_json({
                "type": "STATUS_UPDATE",
                "operational_drones": sum(1 for d in pentagon_store.drones.values() if d.status == DroneStatus.OPERATIONAL),
                "active_missions": sum(1 for m in pentagon_store.missions.values() if m.status == MissionStatus.ACTIVE),
                "timestamp": datetime.utcnow().isoformat()
            })
            
    except WebSocketDisconnect:
        pentagon_store.websocket_connections.discard(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        pentagon_store.websocket_connections.discard(websocket)

# Development server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "pentagon_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
