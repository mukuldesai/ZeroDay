from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import yaml
import os
from loguru import logger
import asyncio
from datetime import datetime
import copy


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "settings.yaml")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

config = load_config()

log_dir = config['logging'].get('log_dir', 'logs')
log_file = os.path.join(log_dir, "zeroday.log")
os.makedirs(log_dir, exist_ok=True)
logger.add(log_file, rotation="1 MB", retention="10 days", level=config['logging']['level'])

app = FastAPI(
    title="ZeroDay API",
    description="Agentic AI system for developer onboarding",
    version=config['app']['version']
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    user_role: Optional[str] = "developer"
    context: Optional[Dict[str, Any]] = {}
    agent_type: Optional[str] = "auto"  

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    confidence: float
    sources: List[Dict[str, str]] = []
    suggestions: List[str] = []
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    version: str
    agents_status: Dict[str, bool]


class MockAgentSystem:
    def __init__(self, config):
        self.config = config
        
    async def route_query(self, message: str, user_role: str, context: Dict, agent_type: str) -> ChatResponse:
        """Route query to appropriate agent"""
        
        
        if agent_type == "auto":
            agent_type = self._determine_agent_type(message)
        
        if agent_type == "knowledge":
            return await self._knowledge_agent(message, context)
        elif agent_type == "guide":
            return await self._guide_agent(message, user_role, context)
        elif agent_type == "mentor":
            return await self._mentor_agent(message, context)
        elif agent_type == "task":
            return await self._task_agent(message, user_role, context)
        else:
            return await self._general_agent(message, context)
    
    def _determine_agent_type(self, message: str) -> str:
        """Determine which agent should handle the query"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["how", "what", "explain", "documentation", "code"]):
            return "knowledge"
        elif any(word in message_lower for word in ["learn", "path", "roadmap", "start", "begin"]):
            return "guide"
        elif any(word in message_lower for word in ["help", "stuck", "problem", "debug", "error"]):
            return "mentor"
        elif any(word in message_lower for word in ["task", "todo", "assignment", "practice", "work"]):
            return "task"
        else:
            return "knowledge"
    
    async def _knowledge_agent(self, message: str, context: Dict) -> ChatResponse:
        """Mock knowledge agent - searches codebase/docs"""
        await asyncio.sleep(0.1)  
        
        return ChatResponse(
            response=f"Based on the codebase analysis, here's what I found about '{message}': This appears to be related to our authentication system. Check the `/auth` module for implementation details.",
            agent_used="knowledge",
            confidence=0.85,
            sources=[
                {"type": "code", "path": "/src/auth/login.py", "lines": "15-30"},
                {"type": "docs", "path": "/docs/authentication.md", "section": "OAuth Setup"}
            ],
            suggestions=[
                "Check the related test files",
                "Review the API documentation",
                "Look at recent PRs for this module"
            ],
            timestamp=datetime.now().isoformat()
        )
    
    async def _guide_agent(self, message: str, user_role: str, context: Dict) -> ChatResponse:
        """Mock guide agent - creates learning paths"""
        await asyncio.sleep(0.1)
        
        paths = {
            "frontend": ["React basics", "Component architecture", "State management", "API integration"],
            "backend": ["FastAPI fundamentals", "Database design", "Authentication", "Testing"],
            "fullstack": ["Frontend basics", "Backend setup", "Database integration", "Deployment"]
        }
        
        suggested_path = paths.get(user_role, paths["fullstack"])
        
        return ChatResponse(
            response=f"Here's your personalized learning path for {user_role}: {', '.join(suggested_path)}. Start with the first item and work through systematically.",
            agent_used="guide",
            confidence=0.90,
            sources=[
                {"type": "curriculum", "path": f"/learning/{user_role}.md", "section": "Core Path"}
            ],
            suggestions=[
                "Set up your development environment first",
                "Join the team Slack channels",
                "Schedule a 1:1 with your mentor"
            ],
            timestamp=datetime.now().isoformat()
        )
    
    async def _mentor_agent(self, message: str, context: Dict) -> ChatResponse:
        """Mock mentor agent - contextual Q&A"""
        await asyncio.sleep(0.1)
        
        return ChatResponse(
            response=f"I understand you're facing challenges with '{message}'. Here's my guidance: Start by checking the error logs, then review the relevant documentation. If you're still stuck, don't hesitate to ask a senior developer for a quick pair programming session.",
            agent_used="mentor",
            confidence=0.75,
            sources=[
                {"type": "troubleshooting", "path": "/docs/common-issues.md", "section": "Debug Guide"}
            ],
            suggestions=[
                "Enable debug logging",
                "Check the team's troubleshooting guide",
                "Ask in the #help Slack channel"
            ],
            timestamp=datetime.now().isoformat()
        )
    
    async def _task_agent(self, message: str, user_role: str, context: Dict) -> ChatResponse:
        """Mock task agent - recommends appropriate tasks"""
        await asyncio.sleep(0.1)
        
        beginner_tasks = [
            "Fix typo in user documentation",
            "Add unit test for utility function",
            "Update README with installation steps"
        ]
        
        return ChatResponse(
            response=f"Here are some beginner-friendly tasks perfect for your skill level: {', '.join(beginner_tasks[:2])}. These will help you get familiar with our codebase while making meaningful contributions.",
            agent_used="task",
            confidence=0.80,
            sources=[
                {"type": "issues", "path": "github.com/repo/issues", "section": "good-first-issue"}
            ],
            suggestions=[
                "Start with the documentation task",
                "Ask for code review when ready",
                "Check if tests pass locally"
            ],
            timestamp=datetime.now().isoformat()
        )
    
    async def _general_agent(self, message: str, context: Dict) -> ChatResponse:
        """Fallback general agent"""
        return ChatResponse(
            response=f"I received your message: '{message}'. I'm here to help with onboarding questions, learning paths, code explanations, and task recommendations. Could you be more specific about what you need help with?",
            agent_used="general",
            confidence=0.60,
            sources=[],
            suggestions=[
                "Ask about specific code or documentation",
                "Request a learning path for your role",
                "Ask for help with a technical problem",
                "Request task recommendations"
            ],
            timestamp=datetime.now().isoformat()
        )


agent_system = MockAgentSystem(config)

@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=config['app']['version'],
        agents_status={
            "knowledge": config['agents']['knowledge']['enabled'],
            "guide": config['agents']['guide']['enabled'],
            "mentor": config['agents']['mentor']['enabled'],
            "task": config['agents']['task']['enabled']
        }
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint - routes to appropriate agent"""
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")
        
        response = await agent_system.route_query(
            message=request.message,
            user_role=request.user_role,
            context=request.context,
            agent_type=request.agent_type
        )
        
        logger.info(f"Response generated by {response.agent_used} agent")
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/agents")
async def list_agents():
    """List available agents and their status"""
    return {
        "agents": {
            "knowledge": {
                "description": "Searches codebase, docs, PRs for relevant information",
                "enabled": config['agents']['knowledge']['enabled']
            },
            "guide": {
                "description": "Creates personalized learning paths based on role",
                "enabled": config['agents']['guide']['enabled']
            },
            "mentor": {
                "description": "Provides contextual help and guidance",
                "enabled": config['agents']['mentor']['enabled']
            },
            "task": {
                "description": "Recommends appropriate starter tasks",
                "enabled": config['agents']['task']['enabled']
            }
        }
    }

@app.get("/config")
async def get_config():
    """Get current configuration (excluding API keys)"""
    safe_config = copy.deepcopy(config)
    safe_config['api_keys'] = "**** hidden ****"
    return safe_config

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "chat:app",
        host=config['server']['host'],
        port=config['server']['port'],
        reload=config['server']['reload']
    )