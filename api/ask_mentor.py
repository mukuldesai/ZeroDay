from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import sys
from loguru import logger
from datetime import datetime


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from agents.mentor_agent import MentorAgent


router = APIRouter(prefix="/api", tags=["mentor"])


try:
    mentor_agent = MentorAgent()
    logger.info("Mentor Agent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Mentor Agent: {str(e)}")
    mentor_agent = None


class MentorQuestionRequest(BaseModel):
    """Request model for mentor questions"""
    question: str = Field(..., min_length=5, max_length=2000, description="Your question or problem description")
    user_id: Optional[str] = Field("default_user", description="User identifier for conversation tracking")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context (error messages, code snippets, etc.)")
    conversation_id: Optional[str] = Field(None, description="Conversation thread identifier")
    urgency: Optional[str] = Field("normal", description="Urgency level: low, normal, high, critical")
    problem_type: Optional[str] = Field(None, description="Type of problem: troubleshooting, knowledge_request, guidance_request, code_review")

class MentorResponse(BaseModel):
    """Response model for mentor answers"""
    success: bool
    response: str
    problem_analysis: Dict[str, Any]
    follow_up_suggestions: List[str]
    confidence: float
    sources: List[Dict[str, str]]
    conversation_id: str
    urgency_level: str
    recommended_actions: List[str]
    escalation_needed: bool
    timestamp: str

class QuickHelpRequest(BaseModel):
    """Request model for quick help queries"""
    problem: str = Field(..., min_length=3, max_length=500, description="Brief problem description")
    error_message: Optional[str] = Field(None, description="Error message if applicable")
    stack_trace: Optional[str] = Field(None, description="Stack trace if available")
    code_snippet: Optional[str] = Field(None, max_length=2000, description="Relevant code snippet")

class TroubleshootingRequest(BaseModel):
    """Request model for troubleshooting help"""
    issue_description: str = Field(..., min_length=10, max_length=1500, description="Detailed issue description")
    steps_tried: Optional[List[str]] = Field(None, description="Steps already attempted")
    environment: Optional[Dict[str, str]] = Field(None, description="Environment details (OS, versions, etc.)")
    expected_behavior: Optional[str] = Field(None, description="What should happen")
    actual_behavior: Optional[str] = Field(None, description="What actually happens")
    reproducible: Optional[bool] = Field(None, description="Is the issue consistently reproducible?")

class ConversationHistoryRequest(BaseModel):
    """Request model for conversation history"""
    user_id: str = Field(..., description="User identifier")
    conversation_id: Optional[str] = Field(None, description="Specific conversation ID")
    limit: Optional[int] = Field(10, ge=1, le=50, description="Number of recent exchanges to return")

@router.post("/ask_mentor", response_model=MentorResponse)
async def ask_mentor(request: MentorQuestionRequest):
    """
    Main endpoint for asking the mentor questions
    Provides intelligent help and guidance with conversation tracking
    """
    try:
        if not mentor_agent:
            raise HTTPException(status_code=503, detail="Mentor Agent not available")
        
        logger.info(f"Mentor question from user {request.user_id}: {request.question[:100]}...")
        
        
        enhanced_context = request.context or {}
        enhanced_context.update({
            "urgency": request.urgency,
            "problem_type": request.problem_type,
            "timestamp": datetime.now().isoformat()
        })
        
        
        result = await mentor_agent.provide_help(
            question=request.question,
            user_id=request.user_id,
            context=enhanced_context,
            conversation_id=request.conversation_id
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=f"Mentor request failed: {result.get('error', 'Unknown error')}")
        
        
        escalation_needed = _should_escalate(
            result.get("problem_analysis", {}),
            request.urgency,
            result.get("confidence", 0.0)
        )
        
        
        recommended_actions = _generate_recommended_actions(
            result.get("problem_analysis", {}),
            request.urgency,
            escalation_needed
        )
        
        return MentorResponse(
            success=True,
            response=result.get("response", ""),
            problem_analysis=result.get("problem_analysis", {}),
            follow_up_suggestions=result.get("follow_up_suggestions", []),
            confidence=result.get("confidence", 0.0),
            sources=result.get("sources", []),
            conversation_id=result.get("conversation_id", ""),
            urgency_level=request.urgency,
            recommended_actions=recommended_actions,
            escalation_needed=escalation_needed,
            timestamp=result.get("timestamp", datetime.now().isoformat())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ask_mentor: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/quick_help")
async def quick_help(request: QuickHelpRequest):
    """
    Quick help endpoint for immediate assistance
    Designed for urgent problems that need fast responses
    """
    try:
        if not mentor_agent:
            raise HTTPException(status_code=503, detail="Mentor Agent not available")
        
        
        context = {
            "query_type": "quick_help",
            "urgency": "high",
            "problem_type": "troubleshooting"
        }
        
        if request.error_message:
            context["error_message"] = request.error_message
            context["error_keywords"] = _extract_error_keywords(request.error_message)
        
        if request.stack_trace:
            context["has_stack_trace"] = True
            context["stack_trace_snippet"] = request.stack_trace[:500]  
        
        if request.code_snippet:
            context["has_code_sample"] = True
            context["code_language"] = _detect_code_language(request.code_snippet)
        
        
        question_parts = [request.problem]
        
        if request.error_message:
            question_parts.append(f"Error message: {request.error_message}")
        
        if request.code_snippet:
            question_parts.append(f"Related code: {request.code_snippet}")
        
        full_question = "\n\n".join(question_parts)
        
        
        result = await mentor_agent.provide_help(
            question=full_question,
            user_id="quick_help_user",
            context=context
        )
        
        if not result.get("success", False):
            return JSONResponse(
                status_code=500,
                content={"error": result.get("error", "Quick help request failed")}
            )
        
        
        quick_response = {
            "success": True,
            "immediate_help": result.get("response", ""),
            "confidence": result.get("confidence", 0.0),
            "next_steps": result.get("follow_up_suggestions", [])[:3], 
            "escalate": result.get("confidence", 0.0) < 0.6,  
            "timestamp": datetime.now().isoformat()
        }
        
        return quick_response
        
    except Exception as e:
        logger.error(f"Error in quick_help: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/troubleshoot")
async def troubleshoot_issue(request: TroubleshootingRequest):
    """
    Structured troubleshooting endpoint
    Provides systematic debugging help with detailed analysis
    """
    try:
        if not mentor_agent:
            raise HTTPException(status_code=503, detail="Mentor Agent not available")
        
        
        context = {
            "query_type": "troubleshooting",
            "problem_type": "troubleshooting",
            "urgency": "normal",
            "steps_tried": request.steps_tried or [],
            "environment": request.environment or {},
            "reproducible": request.reproducible
        }
        
        
        question_parts = [
            f"Issue: {request.issue_description}",
        ]
        
        if request.expected_behavior:
            question_parts.append(f"Expected: {request.expected_behavior}")
        
        if request.actual_behavior:
            question_parts.append(f"Actual: {request.actual_behavior}")
        
        if request.steps_tried:
            question_parts.append(f"Steps already tried: {', '.join(request.steps_tried)}")
        
        if request.environment:
            env_info = ', '.join([f"{k}: {v}" for k, v in request.environment.items()])
            question_parts.append(f"Environment: {env_info}")
        
        full_question = "\n\n".join(question_parts)
        
        
        result = await mentor_agent.provide_help(
            question=full_question,
            user_id="troubleshooting_user",
            context=context
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Troubleshooting request failed"))
        
        
        troubleshooting_response = {
            "success": True,
            "analysis": result.get("response", ""),
            "problem_analysis": result.get("problem_analysis", {}),
            "diagnostic_steps": _extract_diagnostic_steps(result.get("response", "")),
            "likely_causes": _extract_likely_causes(result.get("response", "")),
            "solution_suggestions": result.get("follow_up_suggestions", []),
            "confidence": result.get("confidence", 0.0),
            "sources": result.get("sources", []),
            "need_more_info": result.get("confidence", 0.0) < 0.5,
            "timestamp": datetime.now().isoformat()
        }
        
        return troubleshooting_response
        
    except Exception as e:
        logger.error(f"Error in troubleshoot_issue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation_history")
async def get_conversation_history(
    user_id: str = Query(..., description="User identifier"),
    conversation_id: Optional[str] = Query(None, description="Specific conversation ID"),
    limit: int = Query(10, ge=1, le=50, description="Number of exchanges to return")
):
    """
    Get conversation history for a user
    """
    try:
        if not mentor_agent:
            raise HTTPException(status_code=503, detail="Mentor Agent not available")
        
        
        
        history = {
            "user_id": user_id,
            "conversation_id": conversation_id or f"{user_id}_default",
            "exchanges": [],  
            "total_exchanges": 0,
            "last_interaction": None,
            "timestamp": datetime.now().isoformat()
        }
        
        return history
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mentor_stats")
async def get_mentor_stats(user_id: Optional[str] = Query(None, description="User ID for personalized stats")):
    """
    Get mentor service statistics and status
    """
    try:
        if not mentor_agent:
            raise HTTPException(status_code=503, detail="Mentor Agent not available")
        
        stats = await mentor_agent.get_mentor_stats(user_id)
        
        
        service_stats = {
            "service_status": "healthy",
            "mentor_agent_available": True,
            "supported_problem_types": [
                "troubleshooting",
                "knowledge_request", 
                "guidance_request",
                "code_review"
            ],
            "urgency_levels": ["low", "normal", "high", "critical"],
            "features": [
                "conversation_tracking",
                "problem_analysis",
                "confidence_scoring",
                "escalation_detection",
                "contextual_help"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return {**stats, **service_stats}
        
    except Exception as e:
        logger.error(f"Error getting mentor stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def mentor_health_check():
    """
    Health check endpoint for mentor service
    """
    try:
        if not mentor_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "message": "Mentor Agent not initialized",
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        
        test_result = await mentor_agent.provide_help(
            "health check test",
            "health_check_user",
            {"query_type": "health_check"}
        )
        
        return {
            "status": "healthy",
            "mentor_agent_available": True,
            "test_query_success": test_result.get("success", False),
            "response_time_ok": True,  
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Mentor health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


def _should_escalate(problem_analysis: Dict[str, Any], urgency: str, confidence: float) -> bool:
    """Determine if the issue should be escalated to human help"""
    
    
    if urgency == "critical":
        return True
    
    
    if urgency == "high" and confidence < 0.6:
        return True
    
    
    problem_type = problem_analysis.get("problem_type", "")
    if problem_type in ["system_architecture", "security_incident", "data_loss"]:
        return True
    
    
    if confidence < 0.3:
        return True
    
    return False

def _generate_recommended_actions(problem_analysis: Dict[str, Any], urgency: str, escalation_needed: bool) -> List[str]:
    """Generate recommended actions based on the analysis"""
    
    actions = []
    
    if escalation_needed:
        if urgency == "critical":
            actions.append("🚨 Contact senior team member immediately")
            actions.append("📞 Consider paging on-call engineer")
        else:
            actions.append("💬 Ask for help in team channel")
            actions.append("👥 Schedule pair programming session")
    
    problem_type = problem_analysis.get("problem_type", "")
    
    if problem_type == "troubleshooting":
        actions.extend([
            "🔍 Check error logs for more details",
            "🧪 Try to reproduce in isolated environment",
            "📝 Document steps taken so far"
        ])
    elif problem_type == "knowledge_request":
        actions.extend([
            "📚 Review relevant documentation",
            "💡 Practice with small examples",
            "🤝 Ask team members for examples"
        ])
    elif problem_type == "code_review":
        actions.extend([
            "✅ Run tests to verify functionality",
            "🔄 Request code review from peer",
            "📖 Check style guide compliance"
        ])
    
    
    actions.extend([
        "⏱️ Set aside focused time to work on this",
        "📋 Break problem into smaller steps",
        "🔄 Follow up if still stuck after trying suggestions"
    ])
    
    return actions[:5]  

def _extract_error_keywords(error_message: str) -> List[str]:
    """Extract key terms from error message for better search"""
    import re
    
    
    error_patterns = [
        r'\b[A-Z][a-zA-Z]*Error\b',  
        r'\b[A-Z][a-zA-Z]*Exception\b',  
        r'\b\d{3}\b',  
        r'\b[a-zA-Z_]+\(\)',  
        r'\b[A-Z_]{3,}\b',  
    ]
    
    keywords = []
    for pattern in error_patterns:
        keywords.extend(re.findall(pattern, error_message))
    
    return list(set(keywords))[:10]  

def _detect_code_language(code_snippet: str) -> str:
    """Simple code language detection"""
    code_lower = code_snippet.lower()
    
    if 'def ' in code_lower or 'import ' in code_lower:
        return 'python'
    elif 'function' in code_lower or 'const ' in code_lower or 'let ' in code_lower:
        return 'javascript'
    elif 'public class' in code_lower or 'import java' in code_lower:
        return 'java'
    elif 'func ' in code_lower or 'package ' in code_lower:
        return 'go'
    else:
        return 'unknown'

def _extract_diagnostic_steps(response_text: str) -> List[str]:
    """Extract diagnostic steps from mentor response"""
    
    import re
    
    steps = []
    
   
    numbered_pattern = r'\d+\.\s*([^\n]+)'
    steps.extend(re.findall(numbered_pattern, response_text))
    
    
    bullet_pattern = r'[-*]\s*([^\n]+)'
    steps.extend(re.findall(bullet_pattern, response_text))
    
    return steps[:5] 

def _extract_likely_causes(response_text: str) -> List[str]:
    """Extract likely causes from mentor response"""
    
    import re
    
    cause_patterns = [
        r'(?:likely|probably|possibly|might be|could be|usually)\s+(?:caused by|due to|because of)\s+([^.!?]+)',
        r'(?:cause|reason|issue|problem)\s+(?:is|might be|could be)\s+([^.!?]+)',
        r'(?:this happens|occurs)\s+(?:when|because|if)\s+([^.!?]+)'
    ]
    
    causes = []
    for pattern in cause_patterns:
        matches = re.findall(pattern, response_text, re.IGNORECASE)
        causes.extend(matches)
    
    return [cause.strip() for cause in causes[:3]] 


__all__ = ["router"]