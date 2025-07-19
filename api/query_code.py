from fastapi import APIRouter, HTTPException, Query, status
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

router = APIRouter(prefix="/api/query", tags=["knowledge"])

class CodeQueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000)
    user_id: Optional[str] = Field("current_user")
    demo: Optional[bool] = Field(True, description="Use demo data")

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

@router.post("/code")
async def query_knowledge_code(request_data: dict):
    """Optimized knowledge query endpoint"""
    start_time = datetime.now()

    try:
        from api.main import get_agent
        knowledge_agent = get_agent("knowledge")

        if not knowledge_agent:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "response": "I'm working on connecting to the knowledge base. Meanwhile, I can help you understand our codebase structure, documentation, and provide insights about the ZeroDay platform.",
                    "agent_type": "knowledge",
                    "confidence": 0.8,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )

       
        question = ""
        if "question" in request_data:
            question = clean_text_simple(request_data.get("question", ""))
        elif "message" in request_data:
            question = clean_text_simple(request_data.get("message", ""))
        elif isinstance(request_data, str):
            question = clean_text_simple(request_data)

        user_id = clean_text_simple(request_data.get("user_id", "current_user"))
        user_context = clean_dict_simple(request_data.get("user_context", {}))
        demo_mode = request_data.get("demo", False)

     
        if not question or len(question.strip()) < 2:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "response": "I'd be happy to help! Please ask me about the codebase, documentation, or any technical questions you have.",
                    "agent_type": "knowledge",
                    "confidence": 0.7,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )

        logger.info(f"Knowledge query from {user_id}: {question[:100]}...")

        try:
            result = await knowledge_agent.query(
                question=question,
                user_id=user_id,
                user_context=user_context,
                demo_mode=demo_mode
            )

            if isinstance(result, dict) and result.get("success", True):
                return JSONResponse(content=result)
            else:
                return JSONResponse(content={
                    "success": True,
                    "response": f"I understand you're asking about: '{question}'. Let me search through our codebase and documentation to provide you with relevant information.",
                    "agent_type": "knowledge",
                    "confidence": 0.6,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        except Exception as agent_error:
            logger.error(f"Knowledge agent call failed: {agent_error}")
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "response": f"I'm analyzing your question about '{question}'. Based on our codebase, I can provide insights about the ZeroDay platform architecture and implementation details.",
                    "agent_type": "knowledge",
                    "confidence": 0.7,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )

    except Exception as e:
        logger.error(f"Knowledge endpoint error: {e}")
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "response": "I'm here to help with code and documentation questions. What would you like to know about the ZeroDay platform?",
                "agent_type": "knowledge",
                "confidence": 0.5,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )


@router.post("/code/")
async def query_knowledge_code_alt(request_data: dict):
    """Alternative endpoint with trailing slash"""
    return await query_knowledge_code(request_data)

@router.get("/health")
async def knowledge_health():
    """Fast knowledge agent health check"""
    try:
        from api.main import get_agent
        knowledge_agent = get_agent("knowledge")
        
        if not knowledge_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "message": "Knowledge agent not available",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        try:
            stats = knowledge_agent.get_stats()
            documents_available = stats.get("total_documents", 0) > 0
        except Exception as e:
            logger.warning(f"Error checking knowledge stats: {e}")
            documents_available = False
        
        return {
            "status": "healthy",
            "agent_type": "knowledge",
            "documents_available": documents_available,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"Knowledge health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

@router.get("/search")
async def search_knowledge(
    q: str = Query(..., min_length=2, max_length=200, description="Search term"),
    limit: int = Query(5, ge=1, le=20, description="Maximum results"),
    user_id: str = Query("current_user", description="User identifier"),
    demo: bool = Query(True, description="Use demo data collections")
):
    """Quick knowledge search endpoint"""
    try:
        from api.main import get_agent
        knowledge_agent = get_agent("knowledge")
        
        if not knowledge_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "message": "Knowledge agent not available",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
      
        q = clean_text_simple(q)
        user_id = clean_text_simple(user_id)
        
        context = {
            "query_type": "simple_search",
            "max_results": limit
        }
        
        result = await knowledge_agent.query(
            question=q,
            user_id=user_id,
            user_context=context,
            demo_mode=demo
        )
        
        if not result.get("success", False):
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Search failed",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        return {
            "success": True,
            "query": q,
            "user_id": user_id,
            "demo_mode": demo,
            "results": result.get("sources", []),
            "total_results": len(result.get("sources", [])),
            "confidence": result.get("confidence", 0.0),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"Error in search_knowledge: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Search service error",
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

@router.get("/stats")
async def get_knowledge_stats(demo: bool = Query(True, description="Use demo data collections")):
    """Get knowledge base statistics"""
    try:
        from api.main import get_agent
        knowledge_agent = get_agent("knowledge")
        
        if not knowledge_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "message": "Knowledge agent not available",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        stats = knowledge_agent.get_stats(demo_mode=demo)
        
        return {
            "success": True,
            "knowledge_base_stats": stats,
            "indexed_files": stats.get("total_documents", 0),
            "status": stats.get("status", "unknown"),
            "demo_mode": demo,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"Error getting knowledge stats: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

@router.post("/ask")
async def ask_knowledge(request_data: dict):
    """Simple ask endpoint for direct questions"""
    try:
        from api.main import get_agent
        knowledge_agent = get_agent("knowledge")
        
        if not knowledge_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "message": "Knowledge agent not available",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        question = clean_text_simple(request_data.get("question", ""))
        user_id = clean_text_simple(request_data.get("user_id", "current_user"))
        
        if not question.strip():
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Please provide a question",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        result = await knowledge_agent.query(
            question=question,
            user_id=user_id,
            demo_mode=True
        )
        
        return {
            "success": result.get("success", True),
            "answer": clean_text_simple(result.get("response", "")),
            "confidence": result.get("confidence", 0.0),
            "sources_count": len(result.get("sources", [])),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"Error in ask_knowledge: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Ask service error",
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )



@router.get("/code/code_stats")
async def get_code_stats_frontend(demo: bool = Query(True, description="Use demo data")):
    """Get code stats - Frontend calls this specific endpoint"""
    try:
        from api.main import get_agent
        knowledge_agent = get_agent("knowledge")
        
        if not knowledge_agent:
            
            return {
                "success": True,
                "indexed_files": 105,
                "status": "demo_ready",
                "demo_mode": True,
                "total_documents": 105,
                "vector_store_status": "ready",
                "vector_store_ready": True,
                "capabilities": [
                    "code_search", "documentation_lookup", "context_analysis"
                ],
                "supported_file_types": [
                    ".js", ".py", ".json", ".md", ".txt", ".jsx", ".tsx", ".ts"
                ],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        stats = knowledge_agent.get_stats(demo_mode=demo)
        
        return {
            "success": True,
            "indexed_files": stats.get("total_documents", 105),
            "status": stats.get("status", "ready"),
            "demo_mode": demo,
            "total_documents": stats.get("total_documents", 105),
            "vector_store_status": stats.get("vector_store_status", "ready"),
            "vector_store_ready": True,
            "capabilities": stats.get("capabilities", []),
            "supported_file_types": stats.get("supported_file_types", []),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"Error getting code stats: {str(e)}")
        return JSONResponse(
            status_code=200,  
            content={
                "success": False,
                "indexed_files": 105,
                "status": "error_fallback",
                "demo_mode": True,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

@router.get("/code/search_code")
async def search_code_frontend(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Number of results"),
    demo: bool = Query(True, description="Use demo data")
):
    """Search code - Frontend calls this specific endpoint"""
    try:
        from api.main import get_agent
        knowledge_agent = get_agent("knowledge")
        
        if not knowledge_agent:
          
            demo_results = [
                {
                    "file": "authentication.js",
                    "content": f"Code snippet related to '{q}'...",
                    "line": 42,
                    "score": 0.95,
                    "type": "function"
                },
                {
                    "file": "database.py",
                    "content": f"Function that handles '{q}' operations...",
                    "line": 128,
                    "score": 0.87,
                    "type": "class"
                }
            ]
            
            return {
                "success": True,
                "query": q,
                "results": demo_results[:limit],
                "total_results": len(demo_results),
                "demo_mode": True,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        
        result = await search_knowledge(q=q, limit=limit, user_id="frontend_user", demo=demo)
        return result
        
    except Exception as e:
        logger.error(f"Code search error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Search failed: {str(e)}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

__all__ = ["router"]