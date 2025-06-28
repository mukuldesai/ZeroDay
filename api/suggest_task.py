from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import sys
from loguru import logger
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from agents.task_agent import TaskAgent

router = APIRouter(prefix="/api", tags=["tasks"])

try:
    task_agent = TaskAgent()
    logger.info("Task Agent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Task Agent: {str(e)}")
    task_agent = None

class TaskSuggestionRequest(BaseModel):
    user_role: str = Field(..., description="Target role (frontend, backend, fullstack, devops, mobile)")
    skill_level: str = Field("beginner", description="Current skill level")
    interests: Optional[List[str]] = Field(None, description="Areas of interest")
    learning_goals: Optional[List[str]] = Field(None, description="Specific learning objectives")
    time_available: str = Field("2-4 hours", description="Available time commitment")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class TaskSuggestionResponse(BaseModel):
    success: bool
    task_suggestions: List[Dict[str, Any]]
    learning_opportunities: List[Dict[str, Any]]
    next_steps: List[str]
    skill_development_path: List[str]
    recommended_focus: str
    estimated_completion_time: str
    timestamp: str

class QuickTaskRequest(BaseModel):
    role: str = Field(..., description="User role")
    available_time: str = Field("1-2 hours", description="Time available")
    difficulty: str = Field("beginner", description="Preferred difficulty")

class TaskProgressRequest(BaseModel):
    task_id: str = Field(..., description="Task identifier")
    status: str = Field(..., description="Task status (in_progress, completed, blocked)")
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    feedback: Optional[str] = Field(None, description="User feedback")
    time_spent: Optional[float] = Field(None, description="Time spent in hours")

@router.post("/suggest_task", response_model=TaskSuggestionResponse)
async def suggest_tasks(request: TaskSuggestionRequest):
    try:
        if not task_agent:
            raise HTTPException(status_code=503, detail="Task Agent not available")
        
        logger.info(f"Suggesting tasks for {request.skill_level} {request.user_role}")
        
        result = await task_agent.suggest_tasks(
            user_role=request.user_role,
            skill_level=request.skill_level,
            interests=request.interests,
            learning_goals=request.learning_goals,
            time_available=request.time_available,
            context=request.context
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=f"Task suggestion failed: {result.get('error', 'Unknown error')}")
        
        return TaskSuggestionResponse(
            success=True,
            task_suggestions=result.get("task_suggestions", []),
            learning_opportunities=result.get("learning_opportunities", []),
            next_steps=result.get("next_steps", []),
            skill_development_path=result.get("skill_development_path", []),
            recommended_focus=_determine_recommended_focus(result.get("task_suggestions", [])),
            estimated_completion_time=_calculate_total_time(result.get("task_suggestions", [])),
            timestamp=result.get("metadata", {}).get("generated_at", datetime.now().isoformat())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in suggest_tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/quick_task")
async def suggest_quick_task(request: QuickTaskRequest):
    try:
        if not task_agent:
            raise HTTPException(status_code=503, detail="Task Agent not available")
        
        result = await task_agent.suggest_tasks(
            user_role=request.role,
            skill_level=request.difficulty,
            time_available=request.available_time
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail="Quick task suggestion failed")
        
        suggestions = result.get("task_suggestions", [])
        quick_task = suggestions[0] if suggestions else None
        
        if not quick_task:
            return {"success": False, "message": "No suitable tasks found"}
        
        return {
            "success": True,
            "task": {
                "title": quick_task.get("title", quick_task.get("content", "")[:50] + "..."),
                "description": quick_task.get("content", ""),
                "estimated_time": quick_task.get("estimated_time", request.available_time),
                "difficulty": quick_task.get("estimated_difficulty", request.difficulty),
                "skills_developed": quick_task.get("skills_developed", []),
                "getting_started": quick_task.get("getting_started_steps", [])
            },
            "why_recommended": quick_task.get("recommendation_reason", "Good match for your skill level"),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in suggest_quick_task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_task_progress")
async def update_task_progress(request: TaskProgressRequest):
    try:
        if not task_agent:
            raise HTTPException(status_code=503, detail="Task Agent not available")
        
        progress_update = {
            "status": request.status,
            "completion_percentage": request.completion_percentage,
            "feedback": request.feedback,
            "time_spent": request.time_spent
        }
        
        result = await task_agent.update_task_progress(
            task_id=request.task_id,
            progress_update=progress_update
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Progress update failed"))
        
        return {
            "success": True,
            "task_id": request.task_id,
            "status_updated": request.status,
            "next_suggestions": result.get("next_suggestions", []),
            "achievement_unlocked": _check_achievements(request.status, request.completion_percentage),
            "recommended_next_task": _suggest_next_task_type(request.status),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating task progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task_categories")
async def get_task_categories():
    try:
        if not task_agent:
            raise HTTPException(status_code=503, detail="Task Agent not available")
        
        categories = task_agent.get_task_categories()
        
        return {
            "success": True,
            "categories": categories.get("categories", {}),
            "difficulty_levels": categories.get("difficulty_levels", []),
            "task_types": categories.get("task_types", []),
            "supported_roles": categories.get("supported_roles", []),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting task categories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/personalized_suggestions")
async def get_personalized_suggestions(
    role: str = Query(..., description="User role"),
    skill_level: str = Query("beginner", description="Skill level"),
    focus_area: Optional[str] = Query(None, description="Area to focus on"),
    previous_tasks: Optional[str] = Query(None, description="Comma-separated completed task types")
):
    try:
        if not task_agent:
            raise HTTPException(status_code=503, detail="Task Agent not available")
        
       
        completed_tasks = previous_tasks.split(",") if previous_tasks else []
        
       
        context = {
            "focus_area": focus_area,
            "completed_task_types": completed_tasks,
            "personalization_level": "high"
        }
        
        result = await task_agent.suggest_tasks(
            user_role=role,
            skill_level=skill_level,
            context=context
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail="Personalized suggestions failed")
        
        suggestions = result.get("task_suggestions", [])
        
        return {
            "success": True,
            "personalized_tasks": suggestions[:3],
            "progression_path": _create_progression_path(suggestions, skill_level),
            "skill_gaps": _identify_skill_gaps(completed_tasks, role),
            "recommended_focus": focus_area or _suggest_focus_area(completed_tasks, role),
            "next_milestone": _determine_next_milestone(skill_level, completed_tasks),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in personalized suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task_recommendations/{user_id}")
async def get_task_recommendations(
    user_id: str,
    limit: int = Query(5, ge=1, le=20, description="Number of recommendations")
):
    try:
        
        
        recommendations = {
            "user_id": user_id,
            "recommendations": [
                {
                    "task_id": f"task_{i+1}",
                    "title": f"Recommended Task {i+1}",
                    "reason": "Based on your recent activity",
                    "priority": "high" if i < 2 else "medium",
                    "estimated_time": "2-3 hours",
                    "skills_developed": ["problem_solving", "implementation"]
                }
                for i in range(min(limit, 5))
            ],
            "recommendation_basis": [
                "Recent completed tasks",
                "Identified skill gaps", 
                "Learning goals alignment",
                "Time availability patterns"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting recommendations for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def task_health_check():
    try:
        if not task_agent:
            return {"status": "unhealthy", "message": "Task Agent not initialized", "timestamp": datetime.now().isoformat()}
        
        categories = task_agent.get_task_categories()
        
        return {
            "status": "healthy",
            "task_agent_available": True,
            "categories_loaded": len(categories.get("categories", {})) > 0,
            "supported_roles": categories.get("supported_roles", []),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Task health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}


def _determine_recommended_focus(suggestions: List[Dict]) -> str:
    if not suggestions:
        return "General skill development"
    
    skills = []
    for task in suggestions:
        skills.extend(task.get("skills_developed", []))
    
    skill_counts = {}
    for skill in skills:
        skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    if skill_counts:
        top_skill = max(skill_counts, key=skill_counts.get)
        return f"Focus on {top_skill} development"
    
    return "Balanced skill development"

def _calculate_total_time(suggestions: List[Dict]) -> str:
    if not suggestions:
        return "No tasks available"
    
    total_hours = 0
    for task in suggestions:
        time_str = task.get("estimated_time", "2 hours")
        
        if "hour" in time_str:
            hours = int(''.join(filter(str.isdigit, time_str.split()[0])) or 2)
            total_hours += hours
    
    return f"Approximately {total_hours} hours total"

def _check_achievements(status: str, completion_percentage: Optional[int]) -> Optional[str]:
    if status == "completed":
        return "🎉 Task Completed!"
    elif completion_percentage and completion_percentage >= 75:
        return "⭐ Almost There!"
    elif completion_percentage and completion_percentage >= 50:
        return "🚀 Halfway Done!"
    return None

def _suggest_next_task_type(status: str) -> str:
    if status == "completed":
        return "Consider a slightly more challenging task"
    elif status == "blocked":
        return "Try a different type of task or ask for help"
    else:
        return "Continue with current focus area"

def _create_progression_path(suggestions: List[Dict], skill_level: str) -> List[str]:
    if skill_level == "beginner":
        return ["Start with simple tasks", "Build confidence", "Try intermediate challenges"]
    elif skill_level == "intermediate":
        return ["Tackle complex problems", "Lead small features", "Mentor beginners"]
    else:
        return ["Design systems", "Lead projects", "Teach advanced concepts"]

def _identify_skill_gaps(completed_tasks: List[str], role: str) -> List[str]:
    role_skills = {
        "frontend": ["html", "css", "javascript", "react", "testing"],
        "backend": ["apis", "databases", "authentication", "testing", "deployment"],
        "fullstack": ["frontend", "backend", "integration", "deployment"],
        "devops": ["ci/cd", "containerization", "monitoring", "security"],
        "mobile": ["ui/ux", "platform_apis", "performance", "app_store"]
    }
    
    expected_skills = role_skills.get(role, [])
    completed_skill_areas = set(completed_tasks)
    
    gaps = [skill for skill in expected_skills if skill not in completed_skill_areas]
    return gaps[:3]  

def _suggest_focus_area(completed_tasks: List[str], role: str) -> str:
    gaps = _identify_skill_gaps(completed_tasks, role)
    return gaps[0] if gaps else "Advanced development practices"

def _determine_next_milestone(skill_level: str, completed_tasks: List[str]) -> str:
    task_count = len(completed_tasks)
    
    if skill_level == "beginner":
        if task_count < 3:
            return "Complete 3 basic tasks"
        else:
            return "Build first project"
    elif skill_level == "intermediate":
        return "Lead a feature implementation"
    else:
        return "Mentor junior developers"

__all__ = ["router"]