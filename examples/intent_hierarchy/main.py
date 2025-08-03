# FastAPI Demo Backend - Complete Implementation
from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import jwt
import hashlib
import uuid
import asyncio
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

# Pydantic Models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=8)
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime
    is_active: bool

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class PactCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    intent_hierarchy: Dict[str, Any] = Field(..., description="Intent hierarchy structure")
    priority: int = Field(1, ge=1, le=5)
    status: str = Field("draft", regex=r'^(draft|active|completed|archived)$')

class PactUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    intent_hierarchy: Optional[Dict[str, Any]] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[str] = Field(None, regex=r'^(draft|active|completed|archived)$')

class PactResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    intent_hierarchy: Dict[str, Any]
    priority: int
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: str

class IntentNode(BaseModel):
    id: str
    name: str
    type: str = Field(..., regex=r'^(goal|action|condition|milestone)$')
    parent_id: Optional[str] = None
    children: List[str] = []
    properties: Dict[str, Any] = {}
    completion_status: float = Field(0.0, ge=0.0, le=1.0)

# In-memory storage (replace with database in production)
class DataStore:
    def __init__(self):
        self.users: Dict[str, Dict] = {}
        self.pacts: Dict[str, Dict] = {}
        self.user_tokens: Dict[str, str] = {}
        
    def create_user(self, user_data: UserCreate) -> Dict:
        user_id = str(uuid.uuid4())
        hashed_password = hashlib.sha256(user_data.password.encode()).hexdigest()
        
        user = {
            "id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "password_hash": hashed_password,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        self.users[user_id] = user
        return user
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        for user in self.users.values():
            if user["username"] == username:
                return user
        return None
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        return hashlib.sha256(password.encode()).hexdigest() == password_hash

# Initialize data store
store = DataStore()

# Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("FastAPI Demo Backend starting up...")
    
    # Create sample data
    sample_user = UserCreate(
        username="demo_user",
        email="demo@example.com",
        password="demo_password123"
    )
    store.create_user(sample_user)
    logger.info("Sample user created: demo_user")
    
    yield
    
    # Shutdown
    logger.info("FastAPI Demo Backend shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Pact Intent Hierarchy API",
    description="Demo backend for managing pacts with intent hierarchies",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth utilities
def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode = {"sub": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user = store.users.get(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    # Check if username already exists
    if store.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create user
    user = store.create_user(user_data)
    
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        created_at=user["created_at"],
        is_active=user["is_active"]
    )

@app.post("/auth/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    user = store.get_user_by_username(login_data.username)
    
    if not user or not store.verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(user["id"])
    
    return TokenResponse(
        access_token=access_token,
        expires_in=86400  # 24 hours in seconds
    )

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        created_at=current_user["created_at"],
        is_active=current_user["is_active"]
    )

# Pact endpoints
@app.post("/pacts", response_model=PactResponse)
async def create_pact(pact_data: PactCreate, current_user: Dict = Depends(get_current_user)):
    pact_id = str(uuid.uuid4())
    
    pact = {
        "id": pact_id,
        "title": pact_data.title,
        "description": pact_data.description,
        "intent_hierarchy": pact_data.intent_hierarchy,
        "priority": pact_data.priority,
        "status": pact_data.status,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by": current_user["id"]
    }
    
    store.pacts[pact_id] = pact
    
    return PactResponse(**pact)

@app.get("/pacts", response_model=List[PactResponse])
async def get_pacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, regex=r'^(draft|active|completed|archived)$'),
    current_user: Dict = Depends(get_current_user)
):
    # Filter pacts by current user
    user_pacts = [pact for pact in store.pacts.values() if pact["created_by"] == current_user["id"]]
    
    # Filter by status if provided
    if status:
        user_pacts = [pact for pact in user_pacts if pact["status"] == status]
    
    # Apply pagination
    paginated_pacts = user_pacts[skip:skip + limit]
    
    return [PactResponse(**pact) for pact in paginated_pacts]

@app.get("/pacts/{pact_id}", response_model=PactResponse)
async def get_pact(pact_id: str, current_user: Dict = Depends(get_current_user)):
    pact = store.pacts.get(pact_id)
    
    if not pact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pact not found"
        )
    
    if pact["created_by"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return PactResponse(**pact)

@app.put("/pacts/{pact_id}", response_model=PactResponse)
async def update_pact(
    pact_id: str,
    pact_update: PactUpdate,
    current_user: Dict = Depends(get_current_user)
):
    pact = store.pacts.get(pact_id)
    
    if not pact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pact not found"
        )
    
    if pact["created_by"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update fields
    update_data = pact_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        pact[field] = value
    
    pact["updated_at"] = datetime.utcnow()
    
    return PactResponse(**pact)

@app.delete("/pacts/{pact_id}")
async def delete_pact(pact_id: str, current_user: Dict = Depends(get_current_user)):
    pact = store.pacts.get(pact_id)
    
    if not pact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pact not found"
        )
    
    if pact["created_by"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    del store.pacts[pact_id]
    
    return {"message": "Pact deleted successfully"}

# Intent hierarchy endpoints
@app.get("/pacts/{pact_id}/intent-hierarchy")
async def get_intent_hierarchy(pact_id: str, current_user: Dict = Depends(get_current_user)):
    pact = store.pacts.get(pact_id)
    
    if not pact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pact not found"
        )
    
    if pact["created_by"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return pact["intent_hierarchy"]

@app.put("/pacts/{pact_id}/intent-hierarchy")
async def update_intent_hierarchy(
    pact_id: str,
    hierarchy: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    pact = store.pacts.get(pact_id)
    
    if not pact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pact not found"
        )
    
    if pact["created_by"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    pact["intent_hierarchy"] = hierarchy
    pact["updated_at"] = datetime.utcnow()
    
    return {"message": "Intent hierarchy updated successfully", "hierarchy": hierarchy}

# Analytics endpoints
@app.get("/analytics/pacts/summary")
async def get_pacts_summary(current_user: Dict = Depends(get_current_user)):
    user_pacts = [pact for pact in store.pacts.values() if pact["created_by"] == current_user["id"]]
    
    summary = {
        "total_pacts": len(user_pacts),
        "status_breakdown": {},
        "priority_breakdown": {},
        "recent_activity": []
    }
    
    # Status breakdown
    for pact in user_pacts:
        status = pact["status"]
        summary["status_breakdown"][status] = summary["status_breakdown"].get(status, 0) + 1
    
    # Priority breakdown
    for pact in user_pacts:
        priority = pact["priority"]
        summary["priority_breakdown"][str(priority)] = summary["priority_breakdown"].get(str(priority), 0) + 1
    
    # Recent activity (last 5 updated pacts)
    recent_pacts = sorted(user_pacts, key=lambda x: x["updated_at"], reverse=True)[:5]
    summary["recent_activity"] = [
        {
            "id": pact["id"],
            "title": pact["title"],
            "status": pact["status"],
            "updated_at": pact["updated_at"]
        }
        for pact in recent_pacts
    ]
    
    return summary

# WebSocket endpoint for real-time updates (basic implementation)
@app.websocket("/ws")
async def websocket_endpoint(websocket):
    await websocket.accept()
    try:
        while True:
            # Keep connection alive and send periodic updates
            await asyncio.sleep(30)
            await websocket.send_json({"type": "ping", "timestamp": datetime.utcnow().isoformat()})
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "timestamp": datetime.utcnow().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "timestamp": datetime.utcnow().isoformat()}
    )

# Development server runner
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
