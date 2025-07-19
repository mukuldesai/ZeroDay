from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import os
import sys
from loguru import logger


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from database.setup import get_db
    from database.models import User
    from auth.simple_auth import authenticate_user, create_user_session, logout_user, get_user_by_token
    from auth.middleware import get_current_user
    DB_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Database/Auth modules not available: {e}")
    DB_AVAILABLE = False
    
    def get_db():
        return None

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    isDemo: bool

@router.post("/login")
async def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    try:
        
        if request.email and request.password:
           
            demo_user = {
                "id": 1,
                "name": "Demo Developer",
                "email": request.email,  
                "isDemo": True
            }
            
        
            demo_token = f"demo_token_{request.email.replace('@', '_').replace('.', '_')}"
            
            
            response.set_cookie(key="session_token", value=demo_token, httponly=True)
            
            logger.info(f"Demo login successful for: {request.email}")
            
            return {
                "success": True,
                "token": demo_token,
                "user": demo_user,
                "message": "Demo login successful"
            }
        else:
            raise HTTPException(status_code=400, detail="Email and password required")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    if not DB_AVAILABLE:
        raise HTTPException(status_code=503, detail="Authentication service not available")
    
    try:
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        from auth.simple_auth import hash_password
        hashed_password = hash_password(request.password)
        
        user = User(
            name=request.name,
            email=request.email,
            password_hash=hashed_password,
            is_demo=False
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return {"message": "User created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/logout")
async def logout(response: Response, request: Request):
    try:
       
        token = request.cookies.get("session_token")
        if not token:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "")
        
        if token and DB_AVAILABLE:
            
            try:
                db = next(get_db())
                logout_user(token, db)
            except:
                pass  
        
        response.delete_cookie(key="session_token")
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return {"message": "Logged out successfully"} 

@router.get("/me")
async def get_current_user_info(request: Request):
    if not DB_AVAILABLE:
        
        return {
            "id": 1,
            "name": "Demo User", 
            "email": "demo@example.com",
            "isDemo": True
        }
    
    try:
        
        token = request.cookies.get("session_token")
        if not token:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "")
        
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        db = next(get_db())
        user = get_user_by_token(token, db)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "isDemo": user.is_demo
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        
        return {
            "id": 1,
            "name": "Demo User",
            "email": "demo@example.com", 
            "isDemo": True
        }

@router.get("/health")
async def auth_health():
    return {
        "status": "healthy",
        "database_available": DB_AVAILABLE,
        "auth_enabled": DB_AVAILABLE
    }

__all__ = ["router"]