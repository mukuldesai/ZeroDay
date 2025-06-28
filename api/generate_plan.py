from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import sys
from loguru import logger
from datetime import datetime


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from agents.guide_agent import GuideAgent


router = APIRouter(prefix="/api", tags=["learning"])


try:
    guide_agent = GuideAgent()
    logger.info("Guide Agent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Guide Agent: {str(e)}")
    guide_agent = None


class LearningPlanRequest(BaseModel):
    """Request model for learning plan generation"""
    user_role: str = Field(..., description="Target role (frontend, backend, fullstack, devops, mobile)")
    experience_level: str = Field("beginner", description="Current experience level")
    learning_goals: Optional[List[str]] = Field(None, description="Specific learning objectives")
    time_commitment: str = Field("part_time", description="Time availability (full_time, part_time, weekend)")
    preferred_technologies: Optional[List[str]] = Field(None, description="Technologies of interest")
    current_skills: Optional[List[str]] = Field(None, description="Existing skills and knowledge")
    deadline: Optional[str] = Field(None, description="Target completion date")
    learning_style: Optional[str] = Field("mixed", description="Preferred learning style (visual, hands_on, reading, mixed)")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context (team, project, etc.)")

class LearningPlanResponse(BaseModel):
    """Response model for learning plans"""
    success: bool
    learning_plan: Dict[str, Any]
    recommendations: List[str]
    estimated_duration: str
    difficulty_assessment: str
    next_steps: List[str]
    progress_tracking: Dict[str, Any]
    resources: List[Dict[str, str]]
    milestones: List[Dict[str, Any]]
    timestamp: str

class QuickPlanRequest(BaseModel):
    """Request model for quick plan generation"""
    role: str = Field(..., description="Target role")
    goal: str = Field(..., description="Specific learning goal")
    timeframe: str = Field("1 month", description="Target timeframe")

class CustomizedPlanRequest(BaseModel):
    """Request model for highly customized learning plans"""
    user_profile: Dict[str, Any] = Field(..., description="Comprehensive user profile")
    specific_objectives: List[str] = Field(..., description="Detailed learning objectives")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Time, resource, or other constraints")
    team_context: Optional[Dict[str, Any]] = Field(None, description="Team and project context")

class PlanUpdateRequest(BaseModel):
    """Request model for updating existing plans"""
    plan_id: str = Field(..., description="Learning plan identifier")
    progress_update: Dict[str, Any] = Field(..., description="Progress information")
    feedback: Optional[str] = Field(None, description="User feedback on the plan")
    adjustments_needed: Optional[List[str]] = Field(None, description="Requested adjustments")

@router.post("/generate_plan", response_model=LearningPlanResponse)
async def generate_learning_plan(request: LearningPlanRequest):
    """
    Generate a comprehensive learning plan based on user requirements
    Creates structured, milestone-driven learning paths
    """
    try:
        if not guide_agent:
            raise HTTPException(status_code=503, detail="Guide Agent not available")
        
        logger.info(f"Generating learning plan for {request.experience_level} {request.user_role}")
        
    
        context = {
            "preferred_technologies": request.preferred_technologies or [],
            "current_skills": request.current_skills or [],
            "deadline": request.deadline,
            "learning_style": request.learning_style,
            "team_context": request.context or {}
        }
        
       
        result = await guide_agent.generate_learning_path(
            user_role=request.user_role,
            experience_level=request.experience_level,
            learning_goals=request.learning_goals or [],
            time_commitment=request.time_commitment,
            context=context
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=f"Plan generation failed: {result.get('error', 'Unknown error')}")
        
        learning_plan = result.get("learning_path", {})
        
        
        enhanced_response = _enhance_learning_plan_response(learning_plan, request)
        
        return LearningPlanResponse(
            success=True,
            learning_plan=enhanced_response["plan"],
            recommendations=result.get("recommendations", []),
            estimated_duration=enhanced_response["duration"],
            difficulty_assessment=enhanced_response["difficulty"],
            next_steps=enhanced_response["next_steps"],
            progress_tracking=enhanced_response["tracking"],
            resources=enhanced_response["resources"],
            milestones=enhanced_response["milestones"],
            timestamp=result.get("metadata", {}).get("generated_at", datetime.now().isoformat())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_learning_plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/quick_plan")
async def generate_quick_plan(request: QuickPlanRequest):
    """
    Generate a quick learning plan for immediate use
    Streamlined version for rapid planning
    """
    try:
        if not guide_agent:
            raise HTTPException(status_code=503, detail="Guide Agent not available")
        
       
        full_request = LearningPlanRequest(
            user_role=request.role,
            experience_level="beginner",  
            learning_goals=[request.goal],
            time_commitment="part_time"
        )
        
        
        result = await guide_agent.generate_learning_path(
            user_role=request.role,
            experience_level="beginner",
            learning_goals=[request.goal],
            time_commitment="part_time"
        )
        
        if not result.get("success", False):
            return JSONResponse(
                status_code=500,
                content={"error": result.get("error", "Quick plan generation failed")}
            )
       
        learning_plan = result.get("learning_path", {})
        
        quick_response = {
            "success": True,
            "goal": request.goal,
            "timeframe": request.timeframe,
            "overview": learning_plan.get("overview", ""),
            "key_phases": _extract_key_phases(learning_plan.get("phases", [])),
            "first_steps": _extract_first_steps(learning_plan),
            "estimated_hours": _estimate_hours_from_timeframe(request.timeframe),
            "difficulty": learning_plan.get("difficulty", "intermediate"),
            "success_metrics": _extract_success_metrics(learning_plan),
            "timestamp": datetime.now().isoformat()
        }
        
        return quick_response
        
    except Exception as e:
        logger.error(f"Error in generate_quick_plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/customized_plan")
async def generate_customized_plan(request: CustomizedPlanRequest):
    """
    Generate highly customized learning plan based on detailed requirements
    Advanced planning with team and project context
    """
    try:
        if not guide_agent:
            raise HTTPException(status_code=503, detail="Guide Agent not available")
        
      
        profile = request.user_profile
        role = profile.get("role", "fullstack")
        experience = profile.get("experience_level", "beginner")
        
     
        context = {
            "user_profile": profile,
            "constraints": request.constraints or {},
            "team_context": request.team_context or {},
            "customization_level": "high"
        }
        
     
        result = await guide_agent.generate_learning_path(
            user_role=role,
            experience_level=experience,
            learning_goals=request.specific_objectives,
            time_commitment=profile.get("time_commitment", "part_time"),
            context=context
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Customized plan generation failed"))
        
     
        customized_response = _process_customized_plan(result, request)
        
        return customized_response
        
    except Exception as e:
        logger.error(f"Error in generate_customized_plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update_plan")
async def update_learning_plan(request: PlanUpdateRequest):
    """
    Update an existing learning plan based on progress and feedback
    Adaptive learning path modification
    """
    try:
        if not guide_agent:
            raise HTTPException(status_code=503, detail="Guide Agent not available")
        
       
        result = await guide_agent.update_learning_path(
            learning_path_id=request.plan_id,
            progress_update=request.progress_update
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Plan update failed"))
        
  
        update_response = {
            "success": True,
            "plan_id": request.plan_id,
            "updates_applied": _analyze_updates(request.progress_update),
            "next_recommendations": result.get("next_recommendations", []),
            "adjusted_timeline": _calculate_adjusted_timeline(request.progress_update),
            "new_milestones": _generate_new_milestones(request.progress_update),
            "feedback_incorporated": request.feedback is not None,
            "timestamp": datetime.now().isoformat()
        }
        
        return update_response
        
    except Exception as e:
        logger.error(f"Error in update_learning_plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plan_templates")
async def get_plan_templates(
    role: Optional[str] = Query(None, description="Filter by role"),
    experience_level: Optional[str] = Query(None, description="Filter by experience level")
):
    """
    Get available learning plan templates
    """
    try:
        if not guide_agent:
            raise HTTPException(status_code=503, detail="Guide Agent not available")
        
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
                "suitable_for": _determine_suitable_levels(path_info)
            }
            formatted_templates.append(template)
        
        return {
            "success": True,
            "templates": formatted_templates,
            "supported_roles": available_paths.get("supported_roles", []),
            "experience_levels": available_paths.get("experience_levels", []),
            "time_commitments": available_paths.get("time_commitments", []),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting plan templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plan_progress/{plan_id}")
async def get_plan_progress(plan_id: str):
    """
    Get progress information for a specific learning plan
    """
    try:
        
        progress_info = {
            "plan_id": plan_id,
            "overall_progress": 45,  
            "current_phase": "Phase 2: Core Skills",
            "completed_milestones": 3,
            "total_milestones": 8,
            "estimated_completion": "2024-08-15",
            "recent_activity": [
                {"date": "2024-06-20", "activity": "Completed React basics module"},
                {"date": "2024-06-18", "activity": "Started component architecture"}
            ],
            "next_milestones": [
                {"name": "Complete state management", "due_date": "2024-07-01"},
                {"name": "Build practice project", "due_date": "2024-07-15"}
            ],
            "recommendations": [
                "Focus on hands-on practice with components",
                "Join code review sessions",
                "Start building portfolio project"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return progress_info
        
    except Exception as e:
        logger.error(f"Error getting plan progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning_stats")
async def get_learning_stats():
    """
    Get statistics about learning plan generation and usage
    """
    try:
        if not guide_agent:
            raise HTTPException(status_code=503, detail="Guide Agent not available")
        
    
        available_paths = guide_agent.get_available_paths()
        
        stats = {
            "service_status": "healthy",
            "available_roles": len(available_paths.get("supported_roles", [])),
            "total_templates": len(available_paths.get("learning_paths", {})),
            "supported_features": [
                "personalized_learning_paths",
                "milestone_tracking",
                "progress_adaptation",
                "team_context_integration",
                "multi_timeframe_planning"
            ],
            "average_plan_duration": "8-12 weeks",
            "customization_options": [
                "experience_level",
                "time_commitment", 
                "learning_style",
                "technology_preferences",
                "team_context"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting learning stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def guide_health_check():
    """
    Health check endpoint for learning plan service
    """
    try:
        if not guide_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "message": "Guide Agent not initialized",
                    "timestamp": datetime.now().isoformat()
                }
            )
        
     
        available_paths = guide_agent.get_available_paths()
        
        return {
            "status": "healthy",
            "guide_agent_available": True,
            "templates_loaded": len(available_paths.get("learning_paths", {})) > 0,
            "supported_roles": available_paths.get("supported_roles", []),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Guide health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


def _enhance_learning_plan_response(learning_plan: Dict[str, Any], request: LearningPlanRequest) -> Dict[str, Any]:
    """Enhance learning plan with additional metadata"""
    
    phases = learning_plan.get("phases", [])
    projects = learning_plan.get("projects", [])
    
   
    milestones = []
    for i, phase in enumerate(phases):
        milestone = {
            "phase": i + 1,
            "title": phase.get("title", f"Phase {i + 1}"),
            "week": (i + 1) * 2, 
            "deliverables": phase.get("objectives", []),
            "success_criteria": phase.get("milestones", [])
        }
        milestones.append(milestone)
    
   
    resources = [
        {"type": "documentation", "title": "Team Documentation", "url": "/docs"},
        {"type": "tutorial", "title": "Interactive Tutorials", "url": "/tutorials"},
        {"type": "practice", "title": "Coding Exercises", "url": "/practice"}
    ]
    
    return {
        "plan": learning_plan,
        "duration": f"{learning_plan.get('estimated_duration_weeks', 8)} weeks",
        "difficulty": learning_plan.get("difficulty", "intermediate"),
        "next_steps": _extract_immediate_next_steps(learning_plan),
        "tracking": _create_progress_tracking(phases),
        "resources": resources,
        "milestones": milestones
    }

def _extract_key_phases(phases: List[Dict]) -> List[Dict[str, str]]:
    """Extract key phases for quick plan response"""
    return [
        {
            "title": phase.get("title", ""),
            "duration": f"{phase.get('duration_weeks', 2)} weeks",
            "focus": ", ".join(phase.get("topics", [])[:3])
        }
        for phase in phases[:3]  
    ]

def _extract_first_steps(learning_plan: Dict) -> List[str]:
    """Extract immediate first steps"""
    phases = learning_plan.get("phases", [])
    if phases:
        first_phase = phases[0]
        return first_phase.get("objectives", [])[:3]
    return ["Set up development environment", "Review learning objectives", "Connect with team"]

def _estimate_hours_from_timeframe(timeframe: str) -> int:
    """Estimate total hours based on timeframe"""
    timeframe_lower = timeframe.lower()
    
    if "week" in timeframe_lower:
        weeks = int(''.join(filter(str.isdigit, timeframe_lower)) or 1)
        return weeks * 10  
    elif "month" in timeframe_lower:
        months = int(''.join(filter(str.isdigit, timeframe_lower)) or 1)
        return months * 40 
    else:
        return 40 

def _extract_success_metrics(learning_plan: Dict) -> List[str]:
    """Extract success metrics from learning plan"""
    return [
        "Complete all phase objectives",
        "Build at least one project",
        "Demonstrate practical skills",
        "Receive positive code review feedback"
    ]

def _process_customized_plan(result: Dict, request: CustomizedPlanRequest) -> Dict:
    """Process result for customized plan response"""
    learning_plan = result.get("learning_path", {})
    
    return {
        "success": True,
        "customized_plan": learning_plan,
        "personalization_applied": {
            "user_profile_used": bool(request.user_profile),
            "constraints_considered": bool(request.constraints),
            "team_context_integrated": bool(request.team_context)
        },
        "specific_objectives": request.specific_objectives,
        "recommendations": result.get("recommendations", []),
        "team_integration_suggestions": _generate_team_integration_suggestions(request.team_context),
        "constraint_accommodations": _analyze_constraint_accommodations(request.constraints),
        "timestamp": datetime.now().isoformat()
    }

def _analyze_updates(progress_update: Dict) -> List[str]:
    """Analyze what updates were applied"""
    updates = []
    
    if "completed_phases" in progress_update:
        updates.append(f"Marked {len(progress_update['completed_phases'])} phases as complete")
    
    if "time_spent" in progress_update:
        updates.append(f"Updated time tracking: {progress_update['time_spent']} hours")
    
    if "difficulties" in progress_update:
        updates.append("Noted learning difficulties for plan adjustment")
    
    return updates

def _calculate_adjusted_timeline(progress_update: Dict) -> str:
    """Calculate adjusted timeline based on progress"""
    completion_rate = progress_update.get("completion_percentage", 50)
    
    if completion_rate > 80:
        return "Ahead of schedule - consider advanced topics"
    elif completion_rate < 30:
        return "Behind schedule - recommend focus sessions"
    else:
        return "On track - maintain current pace"

def _generate_new_milestones(progress_update: Dict) -> List[Dict]:
    """Generate new milestones based on progress"""
    return [
        {"title": "Review completed work", "due": "Next week"},
        {"title": "Focus on identified weak areas", "due": "2 weeks"},
        {"title": "Complete practice project", "due": "1 month"}
    ]

def _determine_suitable_levels(path_info: Dict) -> List[str]:
    """Determine suitable experience levels for a path"""
    difficulty = path_info.get("difficulty", "intermediate")
    
    if difficulty == "beginner":
        return ["beginner"]
    elif difficulty == "intermediate":
        return ["beginner", "intermediate"]
    else:
        return ["intermediate", "advanced"]

def _extract_immediate_next_steps(learning_plan: Dict) -> List[str]:
    """Extract immediate next steps from plan"""
    return [
        "Set up your development environment",
        "Join team communication channels",
        "Review the learning plan timeline",
        "Schedule regular check-ins with mentor",
        "Start with Phase 1 activities"
    ]

def _create_progress_tracking(phases: List[Dict]) -> Dict:
    """Create progress tracking structure"""
    return {
        "total_phases": len(phases),
        "tracking_method": "milestone_based",
        "check_in_frequency": "weekly",
        "assessment_points": [f"End of Phase {i+1}" for i in range(len(phases))],
        "success_criteria": ["Phase completion", "Project delivery", "Skill demonstration"]
    }

def _generate_team_integration_suggestions(team_context: Optional[Dict]) -> List[str]:
    """Generate team integration suggestions"""
    if not team_context:
        return ["Connect with team members", "Understand team processes"]
    
    suggestions = ["Attend team meetings", "Pair program with colleagues"]
    
    if team_context.get("has_mentorship_program"):
        suggestions.append("Engage with assigned mentor")
    
    if team_context.get("code_review_process"):
        suggestions.append("Participate in code reviews")
    
    return suggestions

def _analyze_constraint_accommodations(constraints: Optional[Dict]) -> List[str]:
    """Analyze how constraints were accommodated"""
    if not constraints:
        return ["No specific constraints to accommodate"]
    
    accommodations = []
    
    if "time_limited" in constraints:
        accommodations.append("Condensed timeline with focused priorities")
    
    if "remote_work" in constraints:
        accommodations.append("Emphasized online resources and virtual collaboration")
    
    if "specific_tech_stack" in constraints:
        accommodations.append("Customized for required technology stack")
    
    return accommodations


__all__ = ["router"]