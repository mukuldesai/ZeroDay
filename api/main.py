import chromadb
chromadb.telemetry.capture = lambda *args, **kwargs: None
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import os
from datetime import datetime


from api import chat, suggest_task, ask_mentor, generate_plan, upload, query_code, health, users, auth, demo_data, documents


app = FastAPI(
    title="ZeroDay AI API",
    description="AI-powered developer assistance platform",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://zeroday-frontend.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


agents = {}

def get_agent(agent_type: str):
    """Get an initialized agent"""
    return agents.get(agent_type)

@app.on_event("startup")
async def startup_event():
    """Initialize all agents on startup"""
    try:
        logger.info("Starting ZeroDay API - Loading environment...")
        
       
        required_env = ["OPENAI_API_KEY"]
        missing_env = [var for var in required_env if not os.getenv(var)]
        if missing_env:
            logger.error(f"Missing environment variables: {missing_env}")
            raise RuntimeError(f"Missing required environment variables: {missing_env}")
        
        logger.info("Initializing agents...")
        
        
        from agents.knowledge_agent import KnowledgeAgent
        from agents.guide_agent import GuideAgent  
        from agents.mentor_agent import MentorAgent
        from agents.task_agent import TaskAgent
        
        agents["knowledge"] = KnowledgeAgent()
        agents["guide"] = GuideAgent()
        agents["mentor"] = MentorAgent() 
        agents["task"] = TaskAgent()
        
        logger.info("All agents initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize agents: {e}")
        raise


app.include_router(chat.router, tags=["chat"])
app.include_router(suggest_task.router, tags=["tasks"])  
app.include_router(ask_mentor.router, tags=["mentor"])
app.include_router(generate_plan.router, tags=["guide"])
app.include_router(upload.router, tags=["upload"])
app.include_router(query_code.router, tags=["query"])
app.include_router(health.router, tags=["health"])
app.include_router(users.router, tags=["users"])    
# app.include_router(auth.router, tags=["auth"])
app.include_router(demo_data.router, tags=["demo"])
app.include_router(documents.router, tags=["documents"]) 


@app.post("/api/query/code/")
async def query_knowledge_direct(request_data: dict):
    """Direct knowledge endpoint fallback"""
    try:
        knowledge_agent = get_agent("knowledge")
        if not knowledge_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "response": "Knowledge agent not available",
                    "agent_type": "knowledge",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        question = str(request_data.get("question", "")).strip()
        user_id = str(request_data.get("user_id", "current_user"))
        user_context = request_data.get("user_context", {})
        demo_mode = request_data.get("demo", False)
        
        if not question:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "response": "Please provide a question",
                    "agent_type": "knowledge",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        logger.info(f"Knowledge query from {user_id}: {question[:100]}...")
        
        result = await knowledge_agent.query(
            question=question,
            user_id=user_id,
            user_context=user_context,
            demo_mode=demo_mode
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Knowledge endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "response": "I'm having trouble accessing the knowledge base right now. Please try again.",
                "agent_type": "knowledge",
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

@app.post("/api/query/code")
async def query_knowledge_no_slash(request_data: dict):
    """Knowledge endpoint without trailing slash"""
    return await query_knowledge_direct(request_data)

@app.post("/api/ask_mentor")
async def ask_mentor_direct(request_data: dict):
    """Direct mentor endpoint"""
    try:
        mentor_agent = get_agent("mentor")
        if not mentor_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "response": "Mentor agent not available",
                    "agent_type": "mentor",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        question = str(request_data.get("question", "")).strip()
        user_id = str(request_data.get("user_id", "current_user"))
        user_context = request_data.get("user_context", {})
        
        if not question:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "response": "Please provide a question",
                    "agent_type": "mentor",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        result = await mentor_agent.provide_help(
            question=question,
            user_id=user_id,
            user_context=user_context
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Mentor endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "response": "I'm having trouble right now. Please try again.",
                "agent_type": "mentor",
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

@app.post("/api/generate_plan")  
async def generate_plan_direct(request_data: dict):
    """Direct guide endpoint"""
    try:
        guide_agent = get_agent("guide")
        if not guide_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "learning_path": {},
                    "message": "Guide agent not available",
                    "agent_type": "guide",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
        user_id = str(request_data.get("user_id", "current_user"))
        user_role = str(request_data.get("role", "developer"))
        experience_level = str(request_data.get("experience_level", "beginner"))
        learning_goals = request_data.get("learning_goals", [])
        user_context = request_data.get("user_context", {})
        
        result = await guide_agent.generate_learning_path(
            user_id=user_id,
            user_role=user_role,
            experience_level=experience_level,
            learning_goals=learning_goals,
            user_context=user_context
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Guide endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "learning_path": {},
                "error": "Learning plan generation failed",
                "agent_type": "guide",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

@app.post("/api/suggest_task")
async def suggest_task_direct(request_data: dict):
    """Direct task endpoint"""
    try:
        task_agent = get_agent("task")
        if not task_agent:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "task_suggestions": [],
                    "learning_opportunities": [],
                    "next_steps": ["Try again later"],
                    "agent_type": "task",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        
       
        user_id = str(request_data.get("user_id", "current_user"))
        user_role = str(request_data.get("role", "developer"))
        skill_level = str(request_data.get("skill_level", "beginner"))
        interests = request_data.get("interests", [])
        learning_goals = request_data.get("learning_goals", [])
        time_available = str(request_data.get("time_available", "2-4 hours"))
        user_context = request_data.get("user_context", {})
        
        logger.info(f"Task request: {user_id} - {skill_level} {user_role}")
        
        result = await task_agent.suggest_tasks(
            user_id=user_id,
            user_role=user_role,
            skill_level=skill_level,
            interests=interests,
            learning_goals=learning_goals,
            time_available=time_available,
            user_context=user_context
        )
        
 
        if not isinstance(result, dict):
            result = {
                "success": False,
                "task_suggestions": [],
                "learning_opportunities": [],
                "next_steps": ["Invalid response format"],
                "agent_type": "task"
            }
        
   
        if "agent_type" not in result:
            result["agent_type"] = "task"
        if "user_id" not in result:
            result["user_id"] = user_id
        if "timestamp" not in result:
            result["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Task endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "task_suggestions": [],
                "learning_opportunities": [],
                "next_steps": ["Internal error occurred"],
                "agent_type": "task",
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ZeroDay AI API",
        "version": "1.0.0",
        "status": "running",
        "agents": list(agents.keys()),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/api/auth/me")
async def get_current_user():
    """Get current user info - demo implementation"""
    return {
        "success": True,
        "user": {
            "id": "current_user", 
            "email": "demo@zeroday.ai",
            "name": "Developer",
            "role": "developer",
            "experience_level": "intermediate"
        },
        "authenticated": True,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/agents")
async def list_agents():
    """List available agents with proper status for dashboard"""
    try:
     
        agent_status = {}
        
        for agent_name, agent_instance in agents.items():
            try:
           
                is_available = (agent_instance is not None and 
                              hasattr(agent_instance, 'llm_initialized') and 
                              agent_instance.llm_initialized)
                
                agent_status[agent_name] = {"available": is_available}
                
            except Exception as e:
                logger.error(f"Error checking agent {agent_name}: {e}")
                agent_status[agent_name] = {"available": False}
        
        
        return agent_status
        
    except Exception as e:
        logger.error(f"Error in list_agents: {e}")
        
        return {
            "knowledge": {"available": False},
            "task": {"available": False}, 
            "mentor": {"available": False},
            "guide": {"available": False}
        }

@app.get("/api/debug/agents")
async def debug_agents():
    """Debug agent status"""
    debug_info = {}
    
    for agent_name, agent_instance in agents.items():
        debug_info[agent_name] = {
            "exists": agent_instance is not None,
            "type": str(type(agent_instance)),
            "has_llm_initialized": hasattr(agent_instance, 'llm_initialized') if agent_instance else False,
            "llm_initialized": getattr(agent_instance, 'llm_initialized', False) if agent_instance else False,
            "has_llm_client": hasattr(agent_instance, 'llm_client') if agent_instance else False,
            "llm_client_exists": getattr(agent_instance, 'llm_client', None) is not None if agent_instance else False
        }
    
    return {
        "agents_loaded": list(agents.keys()),
        "agent_details": debug_info,
        "total_agents": len(agents)
    }
    
@app.get("/api/health")
async def api_health_check():
    """API health check for dashboard"""
    try:
        
        active_count = 0
        total_count = len(agents)
        
        for agent_instance in agents.values():
            if (agent_instance and 
                hasattr(agent_instance, 'llm_initialized') and 
                agent_instance.llm_initialized):
                active_count += 1
        
       
        from api.upload import user_documents
        doc_count = sum(len(docs) for docs in user_documents.values())
        
       
        if active_count == total_count and active_count > 0:
            status = "EXCELLENT"
        elif active_count > total_count // 2:
            status = "GOOD" 
        elif active_count > 0:
            status = "FAIR"
        else:
            status = "POOR"
        
        return {
            "status": status,
            "api": "Connected",
            "agents": {
                "active": active_count,
                "total": total_count,
                "status": f"{active_count}/{total_count} Active"
            },
            "documents": doc_count,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "ERROR",
            "api": "Connected", 
            "agents": {"active": 0, "total": 0, "status": "0/0 Active"},
            "documents": 0,
            "error": str(e),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }