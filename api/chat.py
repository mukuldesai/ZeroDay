from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Tuple
import os
import re
from loguru import logger
import asyncio
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix="/api", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    user_role: Optional[str] = "developer"
    context: Optional[Dict[str, Any]] = {}
    agent_type: Optional[str] = "auto"
    user_id: Optional[str] = "current_user"

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    confidence: float
    sources: List[Dict[str, Any]] = [] 
    suggestions: List[str] = []
    timestamp: str
    user_id: str
    metadata: Optional[Dict[str, Any]] = None

def get_agent(agent_name: str):
    try:
        from .main import get_agent as get_shared_agent
        return get_shared_agent(agent_name)
    except Exception as e:
        logger.error(f"Failed to get {agent_name} agent: {str(e)}")
        return None

class EnhancedAgentRouter:
    def __init__(self):
        self.context_patterns = {
            'timeframe_urgent': re.compile(r'\b(1|one)\s*(week|day|month)\b', re.IGNORECASE),
            'timeframe_specific': re.compile(r'\b(\d+)\s*(week|day|month|hour)s?\b', re.IGNORECASE),
            'learning_intent': re.compile(r'\b(learn|study|path|roadmap|plan|course)\b', re.IGNORECASE),
            'help_intent': re.compile(r'\b(help|stuck|problem|issue|error|debug)\b', re.IGNORECASE),
            'task_intent': re.compile(r'\b(task|assignment|work|todo|suggest|project)\b', re.IGNORECASE),
            'knowledge_intent': re.compile(r'\b(how|what|explain|show|find|search)\b', re.IGNORECASE),
            'specific_tech': re.compile(r'\b(react|vue|python|javascript|node|django)\b', re.IGNORECASE)
        }

    def determine_agent_and_context(self, message: str, user_context: Dict[str, Any] = None) -> Tuple[str, Dict[str, Any]]:
        message_lower = message.lower()
        enhanced_context = user_context.copy() if user_context else {}

        timeframe_match = self.context_patterns['timeframe_urgent'].search(message)
        if timeframe_match:
            enhanced_context['urgent_timeframe'] = timeframe_match.group(0)
            enhanced_context['timeframe_priority'] = 'high'

        specific_timeframe = self.context_patterns['timeframe_specific'].search(message)
        if specific_timeframe:
            enhanced_context['specific_timeframe'] = specific_timeframe.group(0)

        tech_match = self.context_patterns['specific_tech'].search(message)
        if tech_match:
            enhanced_context['specific_technology'] = tech_match.group(0)

        learning_signals = len(self.context_patterns['learning_intent'].findall(message))
        help_signals = len(self.context_patterns['help_intent'].findall(message))
        task_signals = len(self.context_patterns['task_intent'].findall(message))
        knowledge_signals = len(self.context_patterns['knowledge_intent'].findall(message))

        if learning_signals > 0 and (timeframe_match or tech_match):
            enhanced_context['intent_confidence'] = 'high'
            enhanced_context['primary_intent'] = 'accelerated_learning'
            return 'guide', enhanced_context
        elif help_signals > task_signals and help_signals > knowledge_signals:
            enhanced_context['primary_intent'] = 'troubleshooting'
            return 'mentor', enhanced_context
        elif task_signals > 0:
            enhanced_context['primary_intent'] = 'task_assignment'
            return 'task', enhanced_context
        else:
            enhanced_context['primary_intent'] = 'information_seeking'
            return 'knowledge', enhanced_context

class AgentSystem:
    def __init__(self):
        self.router = EnhancedAgentRouter()
        
    async def route_query(self, message: str, user_role: str, context: Dict, agent_type: str, user_id: str) -> ChatResponse:
        if agent_type == "auto":
            agent_type, enriched = self.router.determine_agent_and_context(message, context)
            context.update(enriched)

        try:
            if agent_type == "knowledge":
                knowledge_agent = get_agent("knowledge")
                if knowledge_agent:
                    try:
                        result = await knowledge_agent.query(message, user_id, context)

                        formatted_sources = []
                        for source in result.get("sources", [])[:3]:  
                            if isinstance(source, dict):
                                
                                formatted_source = {
                                    "content": str(source.get("content", ""))[:200] + "..." if len(str(source.get("content", ""))) > 200 else str(source.get("content", "")),
                                    "metadata": source.get("metadata", {}),
                                    "relevance_score": source.get("relevance_score", 0.0),
                                    "collection_type": source.get("collection_type", "unknown")
                                }
                            else:
                               
                                formatted_source = {
                                    "content": str(source)[:200] + "..." if len(str(source)) > 200 else str(source),
                                    "metadata": {},
                                    "relevance_score": 1.0,
                                    "collection_type": "unknown"
                                }
                            formatted_sources.append(formatted_source)

                        return ChatResponse(
                            response=result.get("response", ""),
                            agent_used="knowledge",
                            confidence=result.get("confidence", 0.8),
                            sources=formatted_sources, 
                            suggestions=result.get("suggestions", [])[:4],  
                            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            user_id=user_id,
                            metadata={ 
                                "llm_available": result.get("llm_available", False),
                                "enriched_context": result.get("enriched_context", {}),
                                "processing_details": {
                                    "collections_searched": len(result.get("sources", [])),
                                    "demo_mode": context.get("demo_mode", True)
                                }
                            }
                        )
                    except Exception as e:
                        logger.error(f"Knowledge agent error: {e}")
                        
                        return await self._mock_response(message, agent_type, user_role, context, user_id)
                else:
                    return await self._mock_response(message, agent_type, user_role, context, user_id)

            elif agent_type == "guide":
                guide_agent = get_agent("guide")
                if guide_agent:
                    try:
                        result = await guide_agent.generate_learning_path(
                            user_id=user_id,
                            user_role=user_role,
                            experience_level="beginner",
                            learning_goals=[message]
                        )
                        return ChatResponse(
                            response=f"I've created a learning path for you. Here's an overview: {result.get('learning_path', {}).get('overview', 'Learning path generated successfully!')}",
                            agent_used="guide",
                            confidence=0.9,
                            sources=[],
                            suggestions=result.get("recommendations", [])[:3],
                            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            user_id=user_id
                        )
                    except Exception as e:
                        logger.error(f"Guide agent error: {e}")
                        return await self._mock_response(message, agent_type, user_role, context, user_id)
                else:
                    return await self._mock_response(message, agent_type, user_role, context, user_id)

            elif agent_type == "mentor":
                mentor_agent = get_agent("mentor")
                if mentor_agent:
                    try:
                        result = await mentor_agent.provide_help(message, user_id, context)
                        return ChatResponse(
                            response=result.get("response", ""),
                            agent_used="mentor",
                            confidence=result.get("confidence", 0.75),
                            sources=[],
                            suggestions=result.get("follow_up_suggestions", [])[:3],
                            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            user_id=user_id
                        )
                    except Exception as e:
                        logger.error(f"Mentor agent error: {e}")
                        return await self._mock_response(message, agent_type, user_role, context, user_id)
                else:
                    return await self._mock_response(message, agent_type, user_role, context, user_id)

            elif agent_type == "task":
                task_agent = get_agent("task")
                if task_agent:
                    try:
                        result = await task_agent.suggest_tasks(
                            user_id=user_id,
                            user_role=user_role,
                            skill_level="beginner"
                        )
                        tasks = result.get("task_suggestions", [])
                        if tasks:
                            task_desc = tasks[0].get("content", "No tasks available")
                            return ChatResponse(
                                response=f"Here's a task suggestion for you: {task_desc}",
                                agent_used="task",
                                confidence=0.8,
                                sources=[],
                                suggestions=result.get("next_steps", [])[:3],
                                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                user_id=user_id,
                                metadata={
                                "task_suggestions": tasks[:3],  
                                "user_role": user_role
                                }
                            )
                        else:
                            return ChatResponse(
                                response="No suitable tasks found. Try asking for a different type of task or specify your skill level.",
                                agent_used="task",
                                confidence=0.6,
                                sources=[],
                                suggestions=["Ask for beginner tasks", "Specify your interests", "Request learning resources"],
                                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                user_id=user_id
                            )
                    except Exception as e:
                        logger.error(f"Task agent error: {e}")
                        return await self._mock_response(message, agent_type, user_role, context, user_id)
                else:
                    return await self._mock_response(message, agent_type, user_role, context, user_id)

            else:
                return await self._mock_response(message, agent_type, user_role, context, user_id)

        except Exception as e:
            logger.error(f"Error in agent routing: {str(e)}")
            return ChatResponse(
                response=f"I encountered an error while processing your request. The {agent_type} agent is currently having issues. Please try again or contact support.",
                agent_used=agent_type,
                confidence=0.3,
                sources=[],
                suggestions=["Try rephrasing your question", "Check system status", "Contact support"],
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user_id=user_id
            )

    async def _mock_response(self, message: str, agent_type: str, user_role: str, context: Dict, user_id: str) -> ChatResponse:
        await asyncio.sleep(0.1)

        mock_responses = {
            "knowledge": f"**[Knowledge Agent - Demo Mode]** I would search the codebase for information about '{message}'. In a real deployment, I'd analyze your code, documentation, and provide specific file references and explanations.",
            "guide": f"**[Guide Agent - Demo Mode]** I would create a personalized learning path for a {user_role} developer. This would include structured phases, resources, and milestone tracking based on your experience level.",
            "mentor": f"**[Mentor Agent - Demo Mode]** I understand you need help with '{message}'. In a real deployment, I'd provide contextual guidance, debugging help, and connect you with relevant team resources.",
            "task": f"**[Task Agent - Demo Mode]** I would suggest appropriate tasks for a {user_role} developer. These would be matched to your skill level and help you make meaningful contributions to the codebase."
        }

        return ChatResponse(
            response=mock_responses.get(agent_type, f"I received your message about '{message}'. The agents are in demo mode."),
            agent_used=agent_type,
            confidence=0.7,
            sources=[{"type": "demo", "path": "Mock response", "section": "Demo mode"}],
            suggestions=[
                "Set up API keys (OpenAI/Anthropic)",
                "Upload team data",
                "Configure vector store",
                "Check system documentation"
            ],
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_id=user_id
        )

agent_system = AgentSystem()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"Received chat request from {request.user_id}: {request.message[:50]}...")

        enhanced_context = request.context.copy() if request.context else {}
        enhanced_context.update({
            "chat_mode": True,
            "user_role": request.user_role,
            "timestamp": datetime.now().isoformat()
        })

        message_lower = request.message.lower()
        if "react" in message_lower and "week" in message_lower:
            enhanced_context["timeframe"] = "1 week"
            enhanced_context["specific_technology"] = "React"
        elif "react" in message_lower:
            enhanced_context["specific_technology"] = "React"

        response = await agent_system.route_query(
            message=request.message,
            user_role=request.user_role,
            context=enhanced_context,
            agent_type=request.agent_type,
            user_id=request.user_id
        )

        logger.info(f"Response generated by {response.agent_used} agent for user {request.user_id}")
        return response

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return ChatResponse(
            response="I'm experiencing technical difficulties. Please try again.",
            agent_used="fallback",
            confidence=0.3,
            sources=[],
            suggestions=["Try rephrasing your question", "Check your connection"],
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_id=request.user_id
        )

@router.get("/messages")
async def get_messages(user_id: Optional[str] = "current_user"):
    try:
        messages = [
            {
                "id": "msg_1",
                "content": "Hello! How can I help you today?",
                "agent": "system",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
        return {
            "success": True,
            "messages": messages,
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
