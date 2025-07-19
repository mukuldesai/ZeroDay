from fastapi import APIRouter, HTTPException, status, Query
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

router = APIRouter(tags=["learning"])

class LearningPlanRequest(BaseModel):
    user_role: str = Field(..., description="Target role (frontend, backend, fullstack, devops, mobile)")
    experience_level: str = Field("beginner", description="Current experience level")
    learning_goals: Optional[List[str]] = Field(None, description="Specific learning objectives")
    time_commitment: str = Field("part_time", description="Time availability")
    user_id: Optional[str] = Field("current_user", description="User identifier")

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

@router.post("/api/generate_plan")
async def generate_learning_plan(request_data: dict):
    """Optimized learning plan generation endpoint"""
    start_time = datetime.now()
    
    try:
        
        from api.main import get_agent
        guide_agent = get_agent("guide")
        
        if not guide_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "learning_path": {},
                    "message": "Guide agent temporarily unavailable",
                    "agent_type": "guide",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
      
        user_id = clean_text_simple(request_data.get("user_id", "current_user"))
        user_role = clean_text_simple(request_data.get("role", "developer"))
        experience_level = clean_text_simple(request_data.get("experience_level", "beginner"))
        learning_goals = clean_list_simple(request_data.get("learning_goals", []))
        time_commitment = clean_text_simple(request_data.get("time_commitment", "part_time"))
        user_context = clean_dict_simple(request_data.get("user_context", {}))
        
        if not user_id.strip():
            user_id = "current_user"
        if not user_role.strip():
            user_role = "developer"
        if experience_level not in ["beginner", "intermediate", "advanced"]:
            experience_level = "beginner"
        if time_commitment not in ["full_time", "part_time", "weekend"]:
            time_commitment = "part_time"
        
        logger.info(f"Generating learning plan for user {user_id}: {experience_level} {user_role}")
        
      
        try:
            result = await guide_agent.generate_learning_path(
                user_id=user_id,
                user_role=user_role,
                experience_level=experience_level,
                learning_goals=learning_goals,
                time_commitment=time_commitment,
                user_context=user_context
            )
        except Exception as agent_error:
            logger.error(f"Guide agent call failed: {agent_error}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "learning_path": {},
                    "error": "Learning plan generation temporarily unavailable",
                    "agent_type": "guide",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
      
        if not isinstance(result, dict):
            logger.error(f"Guide agent returned invalid type: {type(result)}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "learning_path": {},
                    "error": "Invalid response format from guide agent",
                    "agent_type": "guide",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        
        response = {
            "success": result.get("success", True),
            "learning_path": result.get("learning_path", {}),
            "agent_type": "guide",
            "user_id": user_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "processing_time": str(datetime.now() - start_time)
        }
        
       
        if "recommendations" in result:
            response["recommendations"] = result["recommendations"]
        if "confidence" in result:
            response["confidence"] = result["confidence"]
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Guide endpoint error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "learning_path": {},
                "error": "Learning plan service temporarily unavailable",
                "agent_type": "guide",
                "user_id": request_data.get("user_id", "unknown"),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "processing_time": str(datetime.now() - start_time)
            }
        )

@router.get("/api/guide/health")
async def guide_health_check():
    """Fast guide agent health check"""
    try:
        from api.main import get_agent
        guide_agent = get_agent("guide")
        
        if not guide_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "message": "Guide Agent not initialized",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        try:
            available_paths = guide_agent.get_available_paths()
            paths_loaded = len(available_paths.get("learning_paths", {})) > 0
        except Exception as e:
            logger.warning(f"Error checking available paths: {e}")
            paths_loaded = False
            available_paths = {"supported_roles": []}
        
        return {
            "status": "healthy",
            "guide_agent_available": True,
            "paths_loaded": paths_loaded,
            "supported_roles": available_paths.get("supported_roles", []),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"Guide health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

@router.post("/api/quick_plan")
async def generate_quick_plan(request_data: dict):
    """Quick learning plan for immediate use"""
    try:
        from api.main import get_agent
        guide_agent = get_agent("guide")
        
        if not guide_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "message": "Guide agent not available",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        user_id = clean_text_simple(request_data.get("user_id", "current_user"))
        role = clean_text_simple(request_data.get("role", "developer"))
        goal = clean_text_simple(request_data.get("goal", "Learn development"))
        timeframe = clean_text_simple(request_data.get("timeframe", "1 month"))
        
      
        context = {
            "quick_mode": True,
            "timeframe": timeframe
        }
        
        result = await guide_agent.generate_learning_path(
            user_id=user_id,
            user_role=role,
            experience_level="beginner",
            learning_goals=[goal],
            time_commitment="part_time",
            user_context=context
        )
        
        if not result.get("success", False):
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Quick plan generation failed",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        learning_path = result.get("learning_path", {})
        
        return {
            "success": True,
            "user_id": user_id,
            "goal": goal,
            "timeframe": timeframe,
            "overview": learning_path.get("overview", ""),
            "key_phases": learning_path.get("phases", [])[:3],  
            "estimated_hours": learning_path.get("estimated_duration_weeks", 4) * 10,  
            "difficulty": learning_path.get("difficulty", "intermediate"),
            "next_steps": [
                "Start with the foundation phase",
                "Set up your development environment",
                "Begin with the first project"
            ],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"Error in generate_quick_plan: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Quick plan service error",
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

@router.get("/api/plan_templates")
async def get_plan_templates(
    role: Optional[str] = None,
    experience_level: Optional[str] = None
):
    """Get available learning plan templates"""
    try:
        from api.main import get_agent
        guide_agent = get_agent("guide")
        
        if not guide_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "message": "Guide Agent not available",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        available_paths = guide_agent.get_available_paths()
        templates = available_paths.get("learning_paths", {})
        
       
        if role and role in templates:
            templates = {role: templates[role]}
        
        
        formatted_templates = []
        for path_name, path_info in templates.items():
            template = {
                "name": path_name,
                "description": path_info.get("description", ""),
                "duration_weeks": path_info.get("duration_weeks", 8),
                "difficulty": path_info.get("difficulty", "intermediate"),
                "core_skills": path_info.get("core_skills", []),
                "suitable_for": ["beginner", "intermediate", "advanced"]
            }
            formatted_templates.append(template)
        
        return {
            "success": True,
            "templates": formatted_templates,
            "supported_roles": available_paths.get("supported_roles", []),
            "experience_levels": available_paths.get("experience_levels", []),
            "time_commitments": available_paths.get("time_commitments", []),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"Error getting plan templates: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

@router.get("/api/learning_stats")
async def get_learning_stats(user_id: str = Query("current_user", description="User ID")):
    """Get learning statistics - Frontend endpoint"""
    try:
        
        stats = {
            "active_learning_paths": 2,
            "completed_modules": 12,
            "total_modules": 18,
            "completion_percentage": 67,
            "learning_streak": 5,
            "total_learning_hours": 45.5,
            "avg_session_time": "2.3 hours",
            "skill_improvements": [
                {"skill": "React", "progress": 75, "change": "+15%"},
                {"skill": "Node.js", "progress": 60, "change": "+10%"},
                {"skill": "Python", "progress": 45, "change": "+8%"}
            ],
            "recent_achievements": [
                "Completed React Hooks module",
                "Finished Node.js fundamentals",
                "Passed API design assessment"
            ],
            "upcoming_milestones": [
                "Complete backend development path",
                "Start system design module",
                "Begin advanced React patterns"
            ]
        }
        
        return {
            "success": True,
            "user_id": user_id,
            "stats": stats,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"Error getting learning stats: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

@router.post("/api/update_plan")
async def update_learning_plan(request_data: dict):
    """Update learning plan based on user progress"""
    try:
        from api.main import get_agent
        guide_agent = get_agent("guide")
        
        if not guide_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "message": "Guide agent not available",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        user_id = clean_text_simple(request_data.get("user_id", "current_user"))
        learning_path_id = clean_text_simple(request_data.get("learning_path_id", "default"))
        progress_update = clean_dict_simple(request_data.get("progress_update", {}))
        
        result = await guide_agent.update_learning_path(
            user_id=user_id,
            learning_path_id=learning_path_id,
            progress_update=progress_update
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error updating learning plan: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

__all__ = ["router"]