from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import sys
import traceback
from loguru import logger
import logging
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(tags=["tasks"])

class TaskRequest(BaseModel):
    user_id: Optional[str] = "current_user"
    role: Optional[str] = "developer" 
    skill_level: Optional[str] = "beginner"
    interests: Optional[List[str]] = []
    learning_goals: Optional[List[str]] = []
    time_available: Optional[str] = "2-4 hours"
    user_context: Optional[Dict[str, Any]] = {}

def clean_text_simple(text: str) -> str:
    """Simple, fast text cleaning"""
    if not text:
        return ""
    try:
        text = str(text)[:500]  
        
        text = text.replace('\x8f', '').replace('\x9f', '').replace('\x81', '').replace('\x9d', '')
        
        return ''.join(c for c in text if 32 <= ord(c) <= 126 or c in '\n\r\t')
    except:
        return "cleaned_content"

def clean_list_simple(data: list) -> list:
    """Simple, fast list cleaning"""
    if not isinstance(data, list):
        return []
    return [clean_text_simple(str(item)) for item in data[:5]] 

def clean_dict_simple(data: dict) -> dict:
    """Simple, fast dict cleaning"""
    if not isinstance(data, dict):
        return {}
    
    cleaned = {}
    for key, value in list(data.items())[:5]:  
        try:
            if isinstance(value, str):
                cleaned[str(key)] = clean_text_simple(value)
            elif isinstance(value, list):
                cleaned[str(key)] = clean_list_simple(value)
            elif isinstance(value, (int, float, bool)):
                cleaned[str(key)] = value
            else:
                cleaned[str(key)] = str(value)[:100]
        except:
            cleaned[str(key)] = "error"
    return cleaned

@router.post("/api/suggest_task")
async def suggest_tasks(request_data: dict):
    """Optimized task suggestion endpoint"""
    start_time = datetime.now()
    
    try:
        
        from api.main import get_agent
        task_agent = get_agent("task")
        
        if not task_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "error": "Task agent temporarily unavailable",
                    "task_suggestions": [],
                    "learning_opportunities": [],
                    "next_steps": ["Try again later", "Contact team lead for tasks"],
                    "agent_type": "task",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
       
        user_id = clean_text_simple(request_data.get("user_id", "current_user"))
        role = clean_text_simple(request_data.get("role", "developer"))
        skill_level = clean_text_simple(request_data.get("skill_level", "beginner"))
        interests = clean_list_simple(request_data.get("interests", []))
        learning_goals = clean_list_simple(request_data.get("learning_goals", []))
        time_available = clean_text_simple(request_data.get("time_available", "2-4 hours"))
        user_context = clean_dict_simple(request_data.get("user_context", {}))
        
        
        if not user_id.strip():
            user_id = "current_user"
        if not role.strip():
            role = "developer"
        if skill_level not in ["beginner", "intermediate", "advanced"]:
            skill_level = "beginner"
        
        logger.info(f"Task request for {user_id}: {skill_level} {role}")
        
        
        try:
            result = await task_agent.suggest_tasks(
                user_id=user_id,
                user_role=role,
                skill_level=skill_level,
                interests=interests,
                learning_goals=learning_goals,
                time_available=time_available,
                user_context=user_context
            )
        except Exception as agent_error:
            logger.error(f"Task agent call failed: {agent_error}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Task suggestion temporarily unavailable",
                    "task_suggestions": [],
                    "learning_opportunities": [],
                    "next_steps": ["Try again later", "Contact team lead for tasks"],
                    "agent_type": "task",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
       
        if not isinstance(result, dict):
            logger.error(f"Task agent returned invalid type: {type(result)}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Invalid response format from task agent",
                    "task_suggestions": [],
                    "learning_opportunities": [],
                    "next_steps": ["Try a different request", "Contact support"],
                    "agent_type": "task",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
     
        response = {
            "success": result.get("success", True),
            "task_suggestions": result.get("task_suggestions", []),
            "learning_opportunities": result.get("learning_opportunities", []),
            "next_steps": result.get("next_steps", ["Continue with suggested tasks"]),
            "skill_development_path": result.get("skill_development_path", []),
            "agent_type": "task",
            "user_id": user_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "processing_time": str(datetime.now() - start_time)
        }
        
       
        if "metadata" in result:
            response["metadata"] = clean_dict_simple(result["metadata"])
        if "enriched_context" in result:
            response["enriched_context"] = clean_dict_simple(result["enriched_context"])
        if "confidence" in result:
            response["confidence"] = result["confidence"]
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Task endpoint error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Task service temporarily unavailable",
                "task_suggestions": [],
                "learning_opportunities": [],
                "next_steps": ["Try again later", "Contact team lead for tasks"],
                "agent_type": "task",
                "user_id": request_data.get("user_id", "unknown"),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "processing_time": str(datetime.now() - start_time)
            }
        )

@router.get("/api/task/health")
async def task_health_check():
    """Fast task agent health check"""
    try:
        from api.main import get_agent
        task_agent = get_agent("task")
        
        if not task_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy", 
                    "message": "Task Agent not initialized", 
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        try:
            categories = task_agent.get_task_categories()
            categories_loaded = len(categories.get("categories", {})) > 0
        except Exception as e:
            logger.warning(f"Error checking task categories: {e}")
            categories_loaded = False
            categories = {"supported_roles": []}
        
        return {
            "status": "healthy",
            "task_agent_available": True,
            "categories_loaded": categories_loaded,
            "supported_roles": categories.get("supported_roles", []),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"Task health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy", 
                "error": str(e), 
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

@router.post("/api/quick_task")
async def suggest_quick_task(request_data: dict):
    """Quick task suggestion for immediate use"""
    try:
        from api.main import get_agent
        task_agent = get_agent("task")
        
        if not task_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "message": "Task agent not available",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        user_id = clean_text_simple(request_data.get("user_id", "current_user"))
        role = clean_text_simple(request_data.get("role", "developer"))
        available_time = clean_text_simple(request_data.get("available_time", "1-2 hours"))
        difficulty = clean_text_simple(request_data.get("difficulty", "beginner"))
        
        result = await task_agent.suggest_tasks(
            user_id=user_id,
            user_role=role,
            skill_level=difficulty,
            time_available=available_time
        )
        
        if not result.get("success", False):
            return JSONResponse(
                status_code=500,
                content={
                    "success": False, 
                    "message": "Quick task suggestion failed",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        suggestions = result.get("task_suggestions", [])
        quick_task = suggestions[0] if suggestions else None
        
        if not quick_task:
            return {
                "success": False, 
                "message": "No suitable tasks found",
                "suggestions": ["Try a different skill level", "Check with team lead"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        return {
            "success": True,
            "user_id": user_id,
            "task": {
                "title": quick_task.get("title", quick_task.get("content", "")[:50] + "..."),
                "description": quick_task.get("content", ""),
                "estimated_time": quick_task.get("estimated_time", available_time),
                "difficulty": quick_task.get("estimated_difficulty", difficulty),
                "skills_developed": quick_task.get("skills_developed", []),
                "getting_started": quick_task.get("getting_started_steps", [])
            },
            "why_recommended": quick_task.get("recommendation_reason", "Good match for your skill level"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"Error in suggest_quick_task: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Quick task service error",
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

@router.get("/api/task_categories")
async def get_task_categories():
    """Get available task categories"""
    try:
        from api.main import get_agent
        task_agent = get_agent("task")
        
        if not task_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "message": "Task Agent not available",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        categories = task_agent.get_task_categories()
        
        return {
            "success": True,
            "categories": categories.get("categories", {}),
            "difficulty_levels": categories.get("difficulty_levels", []),
            "task_types": categories.get("task_types", []),
            "supported_roles": categories.get("supported_roles", []),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"Error getting task categories: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )


__all__ = ["router"]