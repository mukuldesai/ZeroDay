from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import sys
from loguru import logger
from datetime import datetime


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from agents.knowledge_agent import KnowledgeAgent


router = APIRouter(prefix="/api", tags=["knowledge"])


try:
    knowledge_agent = KnowledgeAgent()
    logger.info("Knowledge Agent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Knowledge Agent: {str(e)}")
    knowledge_agent = None


class CodeQueryRequest(BaseModel):
    """Request model for code queries"""
    query: str = Field(..., min_length=3, max_length=1000, description="The code-related question or search query")
    file_path: Optional[str] = Field(None, description="Specific file path to search within")
    function_name: Optional[str] = Field(None, description="Specific function or method to search for")
    class_name: Optional[str] = Field(None, description="Specific class to search for")
    language: Optional[str] = Field(None, description="Programming language to filter by")
    include_tests: Optional[bool] = Field(True, description="Whether to include test files in search")
    include_comments: Optional[bool] = Field(True, description="Whether to include code comments in results")
    max_results: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of results to return")

class CodeQueryResponse(BaseModel):
    """Response model for code queries"""
    success: bool
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    response_summary: str
    code_examples: List[Dict[str, str]]
    related_files: List[str]
    suggestions: List[str]
    confidence: float
    timestamp: str
    processing_time_ms: Optional[float]

class CodeSearchRequest(BaseModel):
    """Request model for simple code search"""
    search_term: str = Field(..., min_length=2, max_length=200)
    file_types: Optional[List[str]] = Field(None, description="File extensions to search (e.g., ['.py', '.js'])")
    exclude_paths: Optional[List[str]] = Field(None, description="Paths to exclude from search")

class FunctionLookupRequest(BaseModel):
    """Request model for function/method lookup"""
    function_name: str = Field(..., min_length=1, max_length=100)
    file_path: Optional[str] = Field(None)
    include_usage_examples: Optional[bool] = Field(True)

class CodeExplanationRequest(BaseModel):
    """Request model for code explanation"""
    code_snippet: str = Field(..., min_length=10, max_length=5000, description="Code snippet to explain")
    language: Optional[str] = Field(None, description="Programming language of the snippet")
    context: Optional[str] = Field(None, description="Additional context about the code")

@router.post("/query_code", response_model=CodeQueryResponse)
async def query_code(request: CodeQueryRequest):
    """
    Main endpoint for querying code and documentation
    Provides intelligent code search with contextual understanding
    """
    start_time = datetime.now()
    
    try:
        if not knowledge_agent:
            raise HTTPException(status_code=503, detail="Knowledge Agent not available")
        
        logger.info(f"Processing code query: {request.query[:100]}...")
        
       
        context = {
            "query_type": "code_search",
            "file_path": request.file_path,
            "function_name": request.function_name,
            "class_name": request.class_name,
            "language": request.language,
            "include_tests": request.include_tests,
            "include_comments": request.include_comments,
            "max_results": request.max_results
        }
        
      
        context = {k: v for k, v in context.items() if v is not None}
        
       
        result = await knowledge_agent.query(request.query, context)
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=f"Query failed: {result.get('error', 'Unknown error')}")
        
       
        processed_results = _process_code_results(result, request)
        
       
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return CodeQueryResponse(
            success=True,
            query=request.query,
            results=processed_results["results"],
            total_results=len(processed_results["results"]),
            response_summary=processed_results["summary"],
            code_examples=processed_results["code_examples"],
            related_files=processed_results["related_files"],
            suggestions=result.get("suggestions", []),
            confidence=result.get("confidence", 0.0),
            timestamp=result.get("timestamp", datetime.now().isoformat()),
            processing_time_ms=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in query_code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/search_code")
async def search_code(
    q: str = Query(..., min_length=2, max_length=200, description="Search term"),
    file_types: Optional[str] = Query(None, description="Comma-separated file extensions (e.g., '.py,.js')"),
    exclude_paths: Optional[str] = Query(None, description="Comma-separated paths to exclude"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results to return")
):
    """
    Simple GET endpoint for code search
    Useful for quick searches and external integrations
    """
    try:
        if not knowledge_agent:
            raise HTTPException(status_code=503, detail="Knowledge Agent not available")
        
       
        file_types_list = file_types.split(',') if file_types else None
        exclude_paths_list = exclude_paths.split(',') if exclude_paths else None
        
       
        context = {
            "query_type": "simple_search",
            "file_types": file_types_list,
            "exclude_paths": exclude_paths_list,
            "max_results": limit
        }
        
        
        context = {k: v for k, v in context.items() if v is not None}
        
        
        result = await knowledge_agent.query(q, context)
        
        if not result.get("success", False):
            return JSONResponse(
                status_code=500,
                content={"error": result.get("error", "Search failed")}
            )
        
       
        return {
            "success": True,
            "query": q,
            "results": result.get("sources", []),
            "total_results": len(result.get("sources", [])),
            "confidence": result.get("confidence", 0.0)
        }
        
    except Exception as e:
        logger.error(f"Error in search_code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/lookup_function")
async def lookup_function(request: FunctionLookupRequest):
    """
    Look up specific functions or methods in the codebase
    Provides detailed information about function usage and examples
    """
    try:
        if not knowledge_agent:
            raise HTTPException(status_code=503, detail="Knowledge Agent not available")
        
      
        query = f"function {request.function_name}"
        if request.file_path:
            query += f" in {request.file_path}"
        
        context = {
            "query_type": "function_lookup",
            "function_name": request.function_name,
            "file_path": request.file_path,
            "include_usage_examples": request.include_usage_examples
        }
        
        result = await knowledge_agent.query(query, context)
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Function lookup failed"))
        
       
        function_info = _process_function_results(result, request.function_name)
        
        return {
            "success": True,
            "function_name": request.function_name,
            "function_info": function_info,
            "usage_examples": function_info.get("usage_examples", []),
            "related_functions": function_info.get("related_functions", []),
            "documentation": function_info.get("documentation", ""),
            "confidence": result.get("confidence", 0.0),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in lookup_function: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/explain_code")
async def explain_code(request: CodeExplanationRequest):
    """
    Explain a code snippet with contextual understanding
    Provides detailed explanations of what the code does and how it works
    """
    try:
        if not knowledge_agent:
            raise HTTPException(status_code=503, detail="Knowledge Agent not available")
        
      
        query = f"explain this code: {request.code_snippet[:200]}..."
        
        context = {
            "query_type": "code_explanation",
            "code_snippet": request.code_snippet,
            "language": request.language,
            "context": request.context
        }
        
        result = await knowledge_agent.query(query, context)
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Code explanation failed"))
        
      
        explanation_info = _process_explanation_results(result, request.code_snippet)
        
        return {
            "success": True,
            "code_snippet": request.code_snippet,
            "explanation": explanation_info.get("explanation", ""),
            "key_concepts": explanation_info.get("key_concepts", []),
            "related_patterns": explanation_info.get("related_patterns", []),
            "improvement_suggestions": explanation_info.get("improvements", []),
            "confidence": result.get("confidence", 0.0),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in explain_code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/code_stats")
async def get_code_stats():
    """
    Get statistics about the indexed codebase
    """
    try:
        if not knowledge_agent:
            raise HTTPException(status_code=503, detail="Knowledge Agent not available")
        
        stats = knowledge_agent.get_stats()
        
     
        code_stats = {
            "knowledge_base_stats": stats,
            "indexed_files": stats.get("total_documents", 0),
            "status": stats.get("status", "unknown"),
            "last_updated": datetime.now().isoformat()
        }
        
        return code_stats
        
    except Exception as e:
        logger.error(f"Error getting code stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the query_code service
    """
    try:
        if not knowledge_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "message": "Knowledge Agent not initialized",
                    "timestamp": datetime.now().isoformat()
                }
            )
        
      
        test_result = await knowledge_agent.query("test", {"query_type": "health_check"})
        
        return {
            "status": "healthy",
            "knowledge_agent_available": True,
            "test_query_success": test_result.get("success", False),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


def _process_code_results(result: Dict[str, Any], request: CodeQueryRequest) -> Dict[str, Any]:
    """Process knowledge agent results for code-specific response"""
    
    sources = result.get("sources", [])
    response_text = result.get("response", "")
    
    
    code_examples = []
    related_files = []
    
    for source in sources:
        source_type = source.get("type", "")
        source_path = source.get("path", "")
        
        if source_type == "code" and source_path:
            related_files.append(source_path)
            
            
            if "lines" in source:
                code_examples.append({
                    "file": source_path,
                    "lines": source.get("lines", ""),
                    "context": "Code from " + source_path
                })
    
    
    summary = response_text[:300] + "..." if len(response_text) > 300 else response_text
    
    return {
        "results": sources,
        "summary": summary,
        "code_examples": code_examples[:5],  
        "related_files": list(set(related_files))[:10]  
    }

def _process_function_results(result: Dict[str, Any], function_name: str) -> Dict[str, Any]:
    """Process results specifically for function lookup"""
    
    sources = result.get("sources", [])
    response_text = result.get("response", "")
    
    function_info = {
        "definition": "",
        "documentation": response_text,
        "usage_examples": [],
        "related_functions": [],
        "file_locations": []
    }
    
    for source in sources:
        source_type = source.get("type", "")
        source_path = source.get("path", "")
        
        if source_type == "code" and function_name.lower() in source.get("content", "").lower():
            function_info["file_locations"].append(source_path)
            
          
            if "example" in source.get("content", "").lower():
                function_info["usage_examples"].append({
                    "file": source_path,
                    "context": source.get("content", "")[:200] + "..."
                })
    
    return function_info

def _process_explanation_results(result: Dict[str, Any], code_snippet: str) -> Dict[str, Any]:
    """Process results for code explanation"""
    
    response_text = result.get("response", "")
    sources = result.get("sources", [])
    
 
    explanation_info = {
        "explanation": response_text,
        "key_concepts": [],
        "related_patterns": [],
        "improvements": []
    }
    
   
    programming_concepts = ["function", "class", "method", "variable", "loop", "condition", "array", "object"]
    
    for concept in programming_concepts:
        if concept in response_text.lower():
            explanation_info["key_concepts"].append(concept)
    
    
    for source in sources:
        if source.get("type") == "code":
            explanation_info["related_patterns"].append({
                "file": source.get("path", ""),
                "pattern": "Similar code pattern found"
            })
    
    return explanation_info


__all__ = ["router"]