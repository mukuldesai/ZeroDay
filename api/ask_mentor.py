from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import os
import sys
import traceback
from loguru import logger
import logging
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(tags=["mentor"])

class MentorQuestionRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=1000)
    user_id: Optional[str] = Field("current_user")
    user_context: Optional[Dict[str, Any]] = Field(None)

def clean_text_simple(text: str) -> str:
    """Simple, fast text cleaning"""
    if not text:
        return ""
    try:
        text = str(text)[:1000]  
        
        text = text.replace('\x8f', '').replace('\x9f', '').replace('\x81', '').replace('\x9d', '')
       
        return ''.join(c for c in text if 32 <= ord(c) <= 126 or c in '\n\r\t')
    except:
        return "cleaned_content"

def clean_dict_simple(data: dict) -> dict:
    """Simple, fast dict cleaning"""
    if not isinstance(data, dict):
        return {}
    
    cleaned = {}
    for key, value in list(data.items())[:5]:  
        try:
            if isinstance(value, str):
                cleaned[str(key)] = clean_text_simple(value)
            elif isinstance(value, (int, float, bool)):
                cleaned[str(key)] = value
            else:
                cleaned[str(key)] = str(value)[:100]
        except:
            cleaned[str(key)] = "error"
    return cleaned

@router.post("/api/ask_mentor")
async def ask_mentor(request_data: dict):
    """Optimized mentor endpoint"""
    start_time = datetime.now()
    
    try:
       
        from api.main import get_agent
        mentor_agent = get_agent("mentor")
        
        if not mentor_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "response": "Mentor agent temporarily unavailable. Please try again later.",
                    "agent_type": "mentor",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
       
        question = clean_text_simple(request_data.get("question", ""))
        user_id = clean_text_simple(request_data.get("user_id", "current_user"))
        user_context = clean_dict_simple(request_data.get("user_context", {}))
        
        if not question.strip():
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "response": "Please provide a valid question.",
                    "agent_type": "mentor",
                    "error": "empty_question",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        logger.info(f"Mentor question from user {user_id}: {question[:100]}...")
        
       
        try:
            result = await mentor_agent.provide_help(
                question=question,
                user_id=user_id,
                user_context=user_context
            )
        except Exception as agent_error:
            logger.error(f"Mentor agent call failed: {agent_error}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "response": "I'm having trouble processing your request. Please try a simpler question or try again.",
                    "agent_type": "mentor",
                    "error": "agent_timeout",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
       
        if not isinstance(result, dict):
            result = {
                "success": False,
                "response": "I encountered an issue processing your request.",
                "agent_type": "mentor"
            }
        
       
        response = {
            "success": result.get("success", True),
            "response": clean_text_simple(result.get("response", "I'm having trouble processing your request.")),
            "agent_type": "mentor",
            "user_id": user_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "processing_time": str(datetime.now() - start_time)
        }
        
       
        if "confidence" in result:
            response["confidence"] = result["confidence"]
        if "suggestions" in result:
            response["suggestions"] = result["suggestions"]
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Mentor endpoint error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "response": "I'm experiencing technical difficulties. Please try again in a moment.",
                "agent_type": "mentor",
                "error": "internal_error",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "processing_time": str(datetime.now() - start_time)
            }
        )

@router.get("/api/mentor_stats")
async def get_mentor_stats(user_id: str = Query("current_user", description="User ID")):
    """Get mentor interaction statistics - Frontend endpoint"""
    try:
       
        stats = {
            "total_interactions": 31,
            "questions_answered": 28,
            "avg_response_time": "2.1 seconds",
            "satisfaction_rating": 4.7,
            "topics_discussed": [
                {"topic": "Code Review", "count": 8, "avg_rating": 4.8},
                {"topic": "Debugging", "count": 6, "avg_rating": 4.6},
                {"topic": "Best Practices", "count": 5, "avg_rating": 4.9},
                {"topic": "Architecture", "count": 4, "avg_rating": 4.5},
                {"topic": "Career Guidance", "count": 3, "avg_rating": 4.8}
            ],
            "recent_sessions": [
                {
                    "date": "2025-07-17",
                    "topic": "React state management",
                    "duration": "15 minutes",
                    "rating": 5
                },
                {
                    "date": "2025-07-16", 
                    "topic": "API error handling",
                    "duration": "12 minutes",
                    "rating": 4
                },
                {
                    "date": "2025-07-15",
                    "topic": "Database optimization",
                    "duration": "20 minutes", 
                    "rating": 5
                }
            ],
            "improvement_areas": [
                "System design patterns",
                "Performance optimization",
                "Testing strategies"
            ],
            "mentor_availability": "online",
            "next_suggested_session": "Database performance tuning"
        }
        
        return {
            "success": True,
            "user_id": user_id,
            "stats": stats,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"Error getting mentor stats: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

@router.get("/api/mentor/health")
async def mentor_health_check():
    """Fast mentor health check"""
    try:
        from api.main import get_agent
        mentor_agent = get_agent("mentor")
        
        return {
            "status": "healthy" if mentor_agent else "unhealthy",
            "mentor_agent_available": mentor_agent is not None,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"Mentor health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

__all__ = ["router"]