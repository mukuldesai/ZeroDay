from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api", tags=["users"])


users_db = {}

class UserCreate(BaseModel):
    name: str
    email: str
    role: str
    experience_level: str
    team: str

class UserSetup(BaseModel):
    name: str
    email: str
    role: str
    experience_level: str
    team: str
    preferences: Optional[Dict[str, Any]] = {}
    demo_mode: Optional[bool] = False

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    experience_level: Optional[str] = None
    team: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    experience_level: str
    team: str
    joined_date: str
    avatar: Optional[str] = None
    is_demo: bool = False
    preferences: Dict[str, Any] = {}

@router.post("/setup")
async def setup_user(user_setup: UserSetup):
    """Setup a new user or update existing user setup"""
    try:
        user_id = str(uuid.uuid4())
        
        user_data = {
            "id": user_id,
            "name": user_setup.name,
            "email": user_setup.email,
            "role": user_setup.role,
            "experience_level": user_setup.experience_level,
            "team": user_setup.team,
            "joined_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "avatar": None,
            "is_demo": user_setup.demo_mode or False,
            "preferences": user_setup.preferences or {
                "theme": "light",
                "notifications": True,
                "auto_save": True,
                "language": "en"
            }
        }
        
        
        users_db[user_id] = user_data
        
        return {
            "success": True,
            "message": "User setup completed successfully",
            "user": user_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User setup failed: {str(e)}")

@router.get("/user")
async def get_current_user_api():
    """Get current user - Frontend compatibility endpoint"""
    try:
        
        demo_user = {
            "id": "demo_user_123",
            "name": "Demo Developer",
            "email": "demo@zeroday.ai",
            "role": "Full Stack Developer",
            "experience_level": "intermediate",
            "team": "Demo Team",
            "joined_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "avatar": None,
            "is_demo": True,
            "preferences": {
                "theme": "dark",
                "notifications": True,
                "auto_save": True,
                "language": "en"
            }
        }
        
        return {
            "success": True,
            "user": demo_user,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to get user: {str(e)}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

@router.put("/user")
async def update_current_user_api(request_data: dict):
    """Update current user - Frontend compatibility endpoint"""
    try:
   
        return {
            "success": True,
            "message": "User updated successfully",
            "user": {
                "id": "demo_user_123",
                "name": request_data.get("name", "Demo Developer"),
                "email": request_data.get("email", "demo@zeroday.ai"),
                "role": request_data.get("role", "Full Stack Developer"),
                "experience_level": request_data.get("experience_level", "intermediate"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to update user: {str(e)}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

@router.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile by ID"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    return users_db[user_id]

@router.put("/profile/{user_id}")
async def update_user_profile(user_id: str, user_update: UserUpdate):
    """Update user profile"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = users_db[user_id]
    
   
    if user_update.name is not None:
        user_data["name"] = user_update.name
    if user_update.role is not None:
        user_data["role"] = user_update.role
    if user_update.experience_level is not None:
        user_data["experience_level"] = user_update.experience_level
    if user_update.team is not None:
        user_data["team"] = user_update.team
    if user_update.preferences is not None:
        user_data["preferences"].update(user_update.preferences)
    
    users_db[user_id] = user_data
    
    return {
        "success": True,
        "message": "Profile updated successfully",
        "user": user_data
    }

@router.get("/preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """Get user preferences"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    return users_db[user_id].get("preferences", {})

@router.put("/preferences/{user_id}")
async def update_user_preferences(user_id: str, preferences: Dict[str, Any]):
    """Update user preferences"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    users_db[user_id]["preferences"].update(preferences)
    
    return {
        "success": True,
        "message": "Preferences updated successfully",
        "preferences": users_db[user_id]["preferences"]
    }

@router.get("/stats/{user_id}")
async def get_user_stats(user_id: str):
    """Get user statistics and progress"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = users_db[user_id]
    
    
    stats = {
        "total_tasks": 12,
        "completed_tasks": 8,
        "in_progress_tasks": 3,
        "pending_tasks": 1,
        "learning_paths_active": 2,
        "learning_paths_completed": 1,
        "total_interactions": 45,
        "avg_response_time": "2.3s",
        "completion_rate": 67,
        "learning_streak": 5,
        "documents_read": 23,
        "questions_asked": 18,
        "milestones_met": 4,
        "join_date": user_data["joined_date"],
        "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return stats

@router.get("/activity/{user_id}")
async def get_user_activity(user_id: str, limit: int = 10):
    """Get user recent activity"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    
    activities = [
        {
            "id": 1,
            "type": "task",
            "title": "Completed authentication setup",
            "description": "Successfully implemented JWT authentication",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "completed"
        },
        {
            "id": 2,
            "type": "learning",
            "title": "Finished React Hooks module",
            "description": "Completed advanced React Hooks learning path",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "completed"
        },
        {
            "id": 3,
            "type": "chat",
            "title": "Asked about API design",
            "description": "Discussed REST API best practices with mentor",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "completed"
        }
    ]
    
    return activities[:limit]

@router.delete("/profile/{user_id}")
async def delete_user(user_id: str):
    """Delete user account"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    del users_db[user_id]
    
    return {
        "success": True,
        "message": "User account deleted successfully"
    }

@router.get("/list")
async def list_users(limit: int = 50):
    """List all users (admin endpoint)"""
    users_list = list(users_db.values())[:limit]
    
    return {
        "users": users_list,
        "total": len(users_db),
        "limit": limit
    }

@router.post("/demo")
async def create_demo_user():
    """Create a demo user for testing"""
    demo_user = UserSetup(
        name="Demo User",
        email="demo@zeroday.ai",
        role="Full Stack Developer",
        experience_level="intermediate",
        team="Demo Team",
        demo_mode=True,
        preferences={
            "theme": "light",
            "notifications": True,
            "auto_save": True,
            "language": "en",
            "demo_scenario": "startup"
        }
    )
    
    return await setup_user(demo_user)