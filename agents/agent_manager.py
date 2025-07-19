import os
import yaml
from typing import List, Dict, Any, Optional, Union
from loguru import logger
from datetime import datetime
import asyncio
from enum import Enum
import re

from .guide_agent import GuideAgent
from .knowledge_agent import KnowledgeAgent
from .mentor_agent import MentorAgent
from .task_agent import TaskAgent

from dotenv import load_dotenv
load_dotenv()

class AgentType(Enum):
    GUIDE = "guide"
    KNOWLEDGE = "knowledge"
    MENTOR = "mentor"
    TASK = "task"

class AgentManager:
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.agents = {}
        self._initialize_agents()
        
    def _load_config(self, config_path: str = None) -> Dict:
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "settings.yaml"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _initialize_agents(self):
        try:
            self.agents[AgentType.GUIDE] = GuideAgent()
            self.agents[AgentType.KNOWLEDGE] = KnowledgeAgent()
            self.agents[AgentType.MENTOR] = MentorAgent()
            self.agents[AgentType.TASK] = TaskAgent()
            
            logger.info("All agents initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {str(e)}")
            raise
    
    def _enrich_user_context(self, content: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enrich user context with inferred information from the query"""
        enriched = user_context.copy() if user_context else {}
        content_lower = content.lower()
        
       
        technical_terms = ["function", "class", "method", "api", "database", "algorithm", "deployment", "architecture"]
        tech_count = sum(1 for term in technical_terms if term in content_lower)
        
        if tech_count >= 3:
            enriched["inferred_complexity"] = "high"
        elif tech_count >= 1:
            enriched["inferred_complexity"] = "medium"
        else:
            enriched["inferred_complexity"] = "low"
        
        
        urgent_terms = ["urgent", "critical", "broken", "down", "production", "emergency", "asap", "immediately"]
        urgency_count = sum(1 for term in urgent_terms if term in content_lower)
        
        if urgency_count > 0:
            enriched["urgency_level"] = "high"
        elif any(word in content_lower for word in ["help", "stuck", "problem"]):
            enriched["urgency_level"] = "medium"
        else:
            enriched["urgency_level"] = "low"
        
        
        tech_stack = []
        technologies = ["react", "python", "javascript", "node", "docker", "kubernetes", "aws", "sql", "mongodb"]
        for tech in technologies:
            if tech in content_lower:
                tech_stack.append(tech)
        
        if tech_stack:
            enriched["detected_tech_stack"] = tech_stack
        
        
        if re.search(r'\b(how to|how do i|how can i)\b', content_lower):
            enriched["query_pattern"] = "how_to"
        elif re.search(r'\b(what is|what are|explain)\b', content_lower):
            enriched["query_pattern"] = "explanation"
        elif re.search(r'\b(error|exception|bug|fail|broken)\b', content_lower):
            enriched["query_pattern"] = "troubleshooting"
        elif re.search(r'\b(learn|study|tutorial|guide)\b', content_lower):
            enriched["query_pattern"] = "learning"
        else:
            enriched["query_pattern"] = "general"
            
        return enriched
    
    def _determine_agent_with_confidence(self, request_type: str, content: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhanced agent determination with confidence scoring"""
        content_lower = content.lower()
        scores = {}
        
        
        guide_patterns = [
            ("learning path", 3), ("roadmap", 3), ("curriculum", 3), ("study plan", 3),
            ("skill development", 2), ("how should i learn", 2), ("what should i study", 2),
            ("career", 2), ("progression", 2)
        ]
        guide_score = sum(weight for pattern, weight in guide_patterns if pattern in content_lower)
        
        
        if user_context and user_context.get("query_pattern") == "learning":
            guide_score += 2
        if request_type == "learning_path":
            guide_score += 3
            
        scores[AgentType.GUIDE] = min(1.0, guide_score / 10)
        
       
        knowledge_patterns = [
            ("how to", 2), ("what is", 2), ("explain", 2), ("documentation", 2),
            ("search", 1), ("find", 1), ("understand", 2), ("definition", 2),
            ("syntax", 2), ("example", 2)
        ]
        knowledge_score = sum(weight for pattern, weight in knowledge_patterns if pattern in content_lower)
        
        
        if user_context and user_context.get("query_pattern") in ["how_to", "explanation"]:
            knowledge_score += 2
        if request_type == "knowledge_query":
            knowledge_score += 3
            
        scores[AgentType.KNOWLEDGE] = min(1.0, knowledge_score / 12)
        
        
        mentor_patterns = [
            ("help", 2), ("stuck", 3), ("problem", 3), ("error", 3),
            ("debug", 3), ("troubleshoot", 3), ("guidance", 2), ("issue", 2),
            ("broken", 3), ("not working", 3), ("failed", 2)
        ]
        mentor_score = sum(weight for pattern, weight in mentor_patterns if pattern in content_lower)
        
        
        if user_context:
            if user_context.get("urgency_level") == "high":
                mentor_score += 3
            if user_context.get("query_pattern") == "troubleshooting":
                mentor_score += 3
                
        if request_type == "help":
            mentor_score += 3
            
        scores[AgentType.MENTOR] = min(1.0, mentor_score / 15)
        
       
        task_patterns = [
            ("task", 2), ("assignment", 2), ("work on", 2), ("project", 2),
            ("todo", 2), ("recommend", 2), ("suggest", 2), ("practice", 2),
            ("exercise", 2)
        ]
        task_score = sum(weight for pattern, weight in task_patterns if pattern in content_lower)
        
        if request_type == "task_suggestion":
            task_score += 3
            
        scores[AgentType.TASK] = min(1.0, task_score / 10)
        
        
        best_agent = max(scores.items(), key=lambda x: x[1])
        confidence = best_agent[1]
        
        
        sorted_scores = sorted(scores.values(), reverse=True)
        is_ambiguous = len(sorted_scores) > 1 and sorted_scores[0] - sorted_scores[1] < 0.2
        
        return {
            "agent_type": best_agent[0],
            "confidence": confidence,
            "all_scores": scores,
            "is_ambiguous": is_ambiguous,
            "reasoning": f"Selected {best_agent[0].value} with {confidence:.2f} confidence"
        }
    
    def _validate_agent_response(self, response: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """Validate agent response quality and detect hallucinations"""
        validation = {
            "is_valid": True,
            "confidence_score": response.get("confidence", 0.5),
            "issues": [],
            "hallucination_detected": False
        }
        
        agent_response = response.get("response", "")
        
        if not agent_response or len(agent_response.strip()) < 10:
            validation["is_valid"] = False
            validation["issues"].append("empty_or_too_short")
            return validation
        
        
        hallucination_patterns = [
            "i don't have access to",
            "i cannot access",
            "based on my training data",
            "i'm not able to access",
            "i don't have specific information about",
            "i cannot provide real-time",
            "as an ai language model"
        ]
        
        response_lower = agent_response.lower()
        for pattern in hallucination_patterns:
            if pattern in response_lower:
                validation["hallucination_detected"] = True
                validation["issues"].append("hallucination_pattern")
                validation["confidence_score"] *= 0.3
                break
        
       
        generic_patterns = [
            "here are some general steps",
            "this is a common issue",
            "you might want to try",
            "generally speaking",
            "in most cases",
            "typically you would"
        ]
        
        generic_count = sum(1 for pattern in generic_patterns if pattern in response_lower)
        if generic_count >= 2:
            validation["issues"].append("too_generic")
            validation["confidence_score"] *= 0.7
        
        
        query_words = set(original_query.lower().split())
        response_words = set(response_lower.split())
        
       
        common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "can", "may", "might"}
        query_words -= common_words
        response_words -= common_words
        
        if len(query_words) > 0:
            overlap = len(query_words.intersection(response_words)) / len(query_words)
            if overlap < 0.1:
                validation["issues"].append("low_relevance")
                validation["confidence_score"] *= 0.6
        
       
        if len(validation["issues"]) >= 2 or validation["hallucination_detected"]:
            validation["is_valid"] = False
            
        return validation
    
    async def route_request(
        self,
        request_type: str,
        user_id: str,
        content: str,
        user_context: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        try:
            
            enriched_context = self._enrich_user_context(content, user_context)
            
            
            agent_selection = self._determine_agent_with_confidence(request_type, content, enriched_context)
            
            
            if agent_selection["confidence"] < 0.3:
                return await self._handle_ambiguous_request(user_id, content, enriched_context, agent_selection)
            
            agent_type = agent_selection["agent_type"]
            
           
            if agent_type == AgentType.GUIDE:
                result = await self._handle_guide_request(user_id, content, enriched_context, **kwargs)
            elif agent_type == AgentType.KNOWLEDGE:
                result = await self._handle_knowledge_request(user_id, content, enriched_context, **kwargs)
            elif agent_type == AgentType.MENTOR:
                result = await self._handle_mentor_request(user_id, content, enriched_context, **kwargs)
            elif agent_type == AgentType.TASK:
                result = await self._handle_task_request(user_id, content, enriched_context, **kwargs)
            else:
                result = await self._handle_general_request(user_id, content, enriched_context)
            
            
            validation = self._validate_agent_response(result, content)
            
            
            if not validation["is_valid"]:
                return await self._handle_invalid_response(user_id, content, enriched_context, result, validation)
            
            
            result["agent_selection"] = agent_selection
            result["validation"] = validation
            result["enriched_context"] = enriched_context
            
            return result
                
        except Exception as e:
            logger.error(f"Error routing request: {str(e)}")
            return await self._generate_contextual_error(user_id, content, str(e), user_context)
    
    async def _handle_ambiguous_request(
        self,
        user_id: str,
        content: str,
        enriched_context: Dict[str, Any],
        agent_selection: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle requests where intent is unclear"""
        user_name = enriched_context.get("name", "user")
        
        top_agents = sorted(agent_selection["all_scores"].items(), key=lambda x: x[1], reverse=True)[:2]
        
        clarifying_response = f"""I want to give you the most helpful response, {user_name}. Your question could be interpreted in a few ways:

"""
        
        if top_agents[0][0] == AgentType.KNOWLEDGE and top_agents[0][1] > 0.2:
            clarifying_response += "- If you're looking for **information or explanation**, I can search our knowledge base and documentation\n"
        
        if top_agents[0][0] == AgentType.MENTOR or (len(top_agents) > 1 and top_agents[1][0] == AgentType.MENTOR):
            clarifying_response += "- If you're **stuck or having problems**, I can provide troubleshooting guidance\n"
            
        if any(agent[0] == AgentType.GUIDE for agent in top_agents):
            clarifying_response += "- If you want to **learn something new**, I can create a personalized learning path\n"
            
        if any(agent[0] == AgentType.TASK for agent in top_agents):
            clarifying_response += "- If you need **tasks or practice exercises**, I can suggest appropriate work\n"
        
        clarifying_response += f"\nCould you be more specific about what you're looking for? For example:\n"
        clarifying_response += f"- Share more details about your specific situation\n"
        clarifying_response += f"- Mention what you've already tried\n"
        clarifying_response += f"- Let me know your experience level with this topic"
        
        return {
            "success": True,
            "response": clarifying_response,
            "agent_type": "clarification",
            "confidence": 0.8,
            "user_id": user_id,
            "needs_clarification": True,
            "suggested_agents": [agent[0].value for agent in top_agents],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    async def _handle_invalid_response(
        self,
        user_id: str,
        content: str,
        enriched_context: Dict[str, Any],
        original_result: Dict[str, Any],
        validation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle cases where agent response is invalid or hallucinated"""
        user_name = enriched_context.get("name", "user")
        issues = validation["issues"]
        
        if validation["hallucination_detected"]:
            fallback_response = f"""I want to give you accurate information, {user_name}, but I don't have enough reliable context about your specific question.

To help you better, could you provide:
- More specific details about what you're trying to accomplish
- Your current environment or setup
- Any error messages or symptoms you're seeing
- What you've already attempted

This will help me give you more precise and reliable guidance."""

        elif "too_generic" in issues:
            fallback_response = f"""I can see you're asking about something specific, {user_name}, but I'd like to give you more targeted help.

Could you share:
- The specific technology or framework you're working with
- Your exact use case or what you're building
- Any constraints or requirements you have

This will help me provide more relevant and actionable guidance."""

        elif "low_relevance" in issues:
            fallback_response = f"""I want to make sure I understand your question correctly, {user_name}.

Could you rephrase or expand on:
- What specific outcome you're trying to achieve
- The context of your project or situation
- Any particular challenges you're facing

This will help me focus on exactly what you need."""

        else:
            fallback_response = f"""I'm having trouble providing a complete answer to your question, {user_name}.

To give you better help:
- Try breaking your question into smaller, more specific parts
- Share more context about your situation
- Let me know what you've already tried

What specific aspect would you like me to focus on first?"""
        
        return {
            "success": True,
            "response": fallback_response,
            "agent_type": "fallback",
            "confidence": 0.6,
            "user_id": user_id,
            "original_issues": issues,
            "validation_failed": True,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    async def _generate_contextual_error(
        self,
        user_id: str,
        content: str,
        error: str,
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate contextual error messages instead of generic ones"""
        user_name = user_context.get("name", "user") if user_context else "user"
        
        if "timeout" in error.lower():
            error_response = f"I'm taking longer than expected to process your request, {user_name}. This sometimes happens with complex queries. Could you try asking a more specific question, or break down your request into smaller parts?"
        elif "connection" in error.lower() or "network" in error.lower():
            error_response = f"I'm having trouble accessing some resources right now, {user_name}. You might want to try again in a moment, or ask a team member who might have direct access to what you need."
        else:
            error_response = f"I encountered an issue processing your request, {user_name}. This might help:\n- Try rephrasing your question\n- Be more specific about what you're looking for\n- Check if you can break this into smaller questions\n\nWhat specific part of your question is most important right now?"
        
        return {
            "success": False,
            "error": error,
            "agent_type": "error_handler",
            "response": error_response,
            "user_id": user_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    async def _handle_guide_request(
        self,
        user_id: str,
        content: str,
        user_context: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        guide_agent = self.agents[AgentType.GUIDE]
        
        user_role = kwargs.get('user_role', user_context.get('role', 'fullstack') if user_context else 'fullstack')
        experience_level = kwargs.get('experience_level', user_context.get('experience_level', 'beginner') if user_context else 'beginner')
        learning_goals = kwargs.get('learning_goals', user_context.get('learning_goals', []) if user_context else [])
        time_commitment = kwargs.get('time_commitment', 'part_time')
        
        result = await guide_agent.generate_learning_path(
            user_id=user_id,
            user_role=user_role,
            experience_level=experience_level,
            learning_goals=learning_goals,
            time_commitment=time_commitment,
            user_context=user_context
        )
        
        result["agent_type"] = AgentType.GUIDE.value
        return result
    
    async def _handle_knowledge_request(
        self,
        user_id: str,
        content: str,
        user_context: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        knowledge_agent = self.agents[AgentType.KNOWLEDGE]
        
        result = await knowledge_agent.query(
            question=content,
            user_id=user_id,
            user_context=user_context
        )
        
        result["agent_type"] = AgentType.KNOWLEDGE.value
        return result
    
    async def _handle_mentor_request(
        self,
        user_id: str,
        content: str,
        user_context: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        mentor_agent = self.agents[AgentType.MENTOR]
        
        conversation_id = kwargs.get('conversation_id')
        
        result = await mentor_agent.provide_help(
            question=content,
            user_id=user_id,
            user_context=user_context,
            conversation_id=conversation_id
        )
        
        result["agent_type"] = AgentType.MENTOR.value
        return result
    
    async def _handle_task_request(
        self,
        user_id: str,
        content: str,
        user_context: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        task_agent = self.agents[AgentType.TASK]
        
        user_role = kwargs.get('user_role', user_context.get('role', 'fullstack') if user_context else 'fullstack')
        skill_level = kwargs.get('skill_level', user_context.get('experience_level', 'beginner') if user_context else 'beginner')
        interests = kwargs.get('interests', user_context.get('interests', []) if user_context else [])
        learning_goals = kwargs.get('learning_goals', user_context.get('learning_goals', []) if user_context else [])
        time_available = kwargs.get('time_available', '2-4 hours')
        
        result = await task_agent.suggest_tasks(
            user_id=user_id,
            user_role=user_role,
            skill_level=skill_level,
            interests=interests,
            learning_goals=learning_goals,
            time_available=time_available,
            user_context=user_context
        )
        
        result["agent_type"] = AgentType.TASK.value
        return result
    
    async def _handle_general_request(
        self,
        user_id: str,
        content: str,
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        knowledge_agent = self.agents[AgentType.KNOWLEDGE]
        
        result = await knowledge_agent.query(
            question=content,
            user_id=user_id,
            user_context=user_context
        )
        
        result["agent_type"] = AgentType.KNOWLEDGE.value
        result["fallback"] = True
        return result
    
    async def chat_with_agents(
        self,
        user_id: str,
        message: str,
        user_context: Dict[str, Any] = None,
        conversation_history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        try:
            
            intent = self._analyze_intent(message, conversation_history, user_context)
            
            if intent["type"] == "multi_agent":
                return await self._handle_multi_agent_request(user_id, message, user_context, intent)
            else:
                return await self.route_request(
                    request_type=intent["type"],
                    user_id=user_id,
                    content=message,
                    user_context=user_context,
                    **intent.get("parameters", {})
                )
                
        except Exception as e:
            logger.error(f"Error in chat_with_agents: {str(e)}")
            return await self._generate_contextual_error(user_id, message, str(e), user_context)
    
    def _analyze_intent(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]] = None,
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        message_lower = message.lower()
        
        
        intent_patterns = {
            "learning_path": [
                ("learning path", 0.9), ("roadmap", 0.8), ("curriculum", 0.8), 
                ("study plan", 0.8), ("how should i learn", 0.7), ("what should i study", 0.7), 
                ("skill development", 0.6), ("career path", 0.7)
            ],
            "task_suggestion": [
                ("task", 0.6), ("assignment", 0.7), ("work on", 0.6), ("what should i work on", 0.8),
                ("recommend", 0.5), ("suggest", 0.5), ("project", 0.4), ("practice", 0.6),
                ("exercise", 0.6)
            ],
            "help": [
                ("help", 0.5), ("stuck", 0.8), ("problem", 0.7), ("error", 0.8), 
                ("debug", 0.8), ("issue", 0.7), ("troubleshoot", 0.8), ("not working", 0.8), 
                ("broken", 0.8), ("failed", 0.7)
            ],
            "knowledge_query": [
                ("how to", 0.7), ("what is", 0.8), ("explain", 0.8), ("tell me about", 0.7),
                ("documentation", 0.6), ("search", 0.4), ("find", 0.4), ("understand", 0.6),
                ("definition", 0.8), ("meaning", 0.7)
            ]
        }
        
        scores = {}
        for intent_type, patterns in intent_patterns.items():
            score = 0
            for pattern, weight in patterns:
                if pattern in message_lower:
                    score = max(score, weight)
            scores[intent_type] = score
        
        
        if conversation_history and len(conversation_history) > 0:
            last_response = conversation_history[-1]
            last_agent = last_response.get("agent_type")
            
            
            if last_agent == "mentor" and scores.get("help", 0) > 0.3:
                scores["help"] += 0.2
            elif last_agent == "guide" and scores.get("learning_path", 0) > 0.3:
                scores["learning_path"] += 0.2
        
        
        if user_context:
            query_pattern = user_context.get("query_pattern")
            if query_pattern == "troubleshooting":
                scores["help"] += 0.3
            elif query_pattern == "learning":
                scores["learning_path"] += 0.3
        
        
        best_intent = max(scores.items(), key=lambda x: x[1]) if scores else ("knowledge_query", 0.5)
        confidence = best_intent[1]
        
        return {
            "type": best_intent[0],
            "confidence": confidence,
            "all_scores": scores,
            "parameters": self._extract_parameters(message_lower, best_intent[0])
        }
    
    def _extract_parameters(self, message: str, intent_type: str) -> Dict[str, Any]:
        parameters = {}
        
        if intent_type == "learning_path":
            roles = ["frontend", "backend", "fullstack", "devops", "mobile", "data"]
            for role in roles:
                if role in message:
                    parameters["user_role"] = role
                    break
            
            levels = ["beginner", "intermediate", "advanced", "expert"]
            for level in levels:
                if level in message:
                    parameters["experience_level"] = level
                    break
                    
            
            if any(word in message for word in ["full time", "full-time", "intensive"]):
                parameters["time_commitment"] = "full_time"
            elif any(word in message for word in ["weekend", "weekends"]):
                parameters["time_commitment"] = "weekend"
        
        elif intent_type == "task_suggestion":
            if "easy" in message or "simple" in message or "basic" in message:
                parameters["skill_level"] = "beginner"
            elif "hard" in message or "challenging" in message or "advanced" in message:
                parameters["skill_level"] = "advanced"
            elif "medium" in message or "intermediate" in message:
                parameters["skill_level"] = "intermediate"
            
            if "quick" in message or "short" in message:
                parameters["time_available"] = "1-2 hours"
            elif "long" in message or "project" in message or "extended" in message:
                parameters["time_available"] = "1+ days"
        
        return parameters
    
    async def _handle_multi_agent_request(
        self,
        user_id: str,
        message: str,
        user_context: Dict[str, Any],
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        results = {}
        
        for agent_type in intent.get("agents", []):
            try:
                result = await self.route_request(
                    request_type=agent_type,
                    user_id=user_id,
                    content=message,
                    user_context=user_context
                )
                results[agent_type] = result
            except Exception as e:
                logger.error(f"Error with {agent_type} agent: {str(e)}")
                results[agent_type] = {"success": False, "error": str(e)}
        
        return {
            "success": True,
            "multi_agent_response": results,
            "primary_response": results.get(intent.get("primary_agent", "knowledge"), {}),
            "user_id": user_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    async def get_agent_status(self) -> Dict[str, Any]:
        status = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "agents": {},
            "overall_health": "healthy"
        }
        
        for agent_type, agent in self.agents.items():
            try:
                if hasattr(agent, 'get_stats'):
                    agent_stats = await agent.get_stats() if asyncio.iscoroutinefunction(agent.get_stats) else agent.get_stats()
                else:
                    agent_stats = {"status": "active"}
                
                status["agents"][agent_type.value] = {
                   "status": "healthy",
                   "stats": agent_stats
               }
           except Exception as e:
               status["agents"][agent_type.value] = {
                   "status": "error",
                   "error": str(e)
               }
               status["overall_health"] = "degraded"
       
       return status
   
   async def update_user_progress(
       self,
       user_id: str,
       progress_data: Dict[str, Any]
   ) -> Dict[str, Any]:
       try:
           results = {}
           
           if "learning_path" in progress_data:
               guide_agent = self.agents[AgentType.GUIDE]
               if hasattr(guide_agent, 'update_learning_path'):
                   results["learning_path"] = await guide_agent.update_learning_path(
                       user_id=user_id,
                       learning_path_id=progress_data["learning_path"].get("id"),
                       progress_update=progress_data["learning_path"]
                   )
           
           if "task_progress" in progress_data:
               task_agent = self.agents[AgentType.TASK]
               if hasattr(task_agent, 'update_task_progress'):
                   results["task_progress"] = await task_agent.update_task_progress(
                       user_id=user_id,
                       task_id=progress_data["task_progress"].get("task_id"),
                       progress_update=progress_data["task_progress"]
                   )
           
           return {
               "success": True,
               "user_id": user_id,
               "updates": results,
               "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
           }
           
       except Exception as e:
           logger.error(f"Error updating user progress: {str(e)}")
           return {
               "success": False,
               "error": str(e),
               "user_id": user_id
           }
   
   def get_available_capabilities(self) -> Dict[str, Any]:
       return {
           "agents": {
               AgentType.GUIDE.value: {
                   "description": "Creates personalized learning paths and roadmaps",
                   "capabilities": [
                       "Generate learning paths",
                       "Skill progression tracking",
                       "Resource recommendations",
                       "Timeline planning"
                   ]
               },
               AgentType.KNOWLEDGE.value: {
                   "description": "Searches and retrieves information from knowledge base",
                   "capabilities": [
                       "Answer technical questions",
                       "Search documentation",
                       "Code examples",
                       "Best practices"
                   ]
               },
               AgentType.MENTOR.value: {
                   "description": "Provides guidance and troubleshooting help",
                   "capabilities": [
                       "Problem solving",
                       "Code review",
                       "Debugging help",
                       "Career guidance"
                   ]
               },
               AgentType.TASK.value: {
                   "description": "Recommends appropriate tasks and assignments",
                   "capabilities": [
                       "Task matching",
                       "Skill-based recommendations",
                       "Progress tracking",
                       "Learning exercises"
                   ]
               }
           },
           "request_types": [
               "learning_path",
               "knowledge_query", 
               "help",
               "task_suggestion",
               "chat"
           ],
           "supported_roles": ["frontend", "backend", "fullstack", "devops", "mobile"],
           "experience_levels": ["beginner", "intermediate", "advanced"]
       }


async def quick_agent_test(user_id: str = "test_user", message: str = "Help me learn React") -> Dict[str, Any]:
   manager = AgentManager()
   return await manager.chat_with_agents(user_id, message)

if __name__ == "__main__":
   import sys
   import json
   
   async def main():
       if len(sys.argv) > 1:
           command = sys.argv[1]
           manager = AgentManager()
           
           if command == "chat":
               user_id = sys.argv[2] if len(sys.argv) > 2 else "cli_user"
               message = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "Help me learn programming"
               
               result = await manager.chat_with_agents(user_id, message)
               print("Agent Response:")
               print(json.dumps(result, indent=2))
               
           elif command == "status":
               status = await manager.get_agent_status()
               print("Agent Status:")
               print(json.dumps(status, indent=2))
               
           elif command == "capabilities":
               capabilities = manager.get_available_capabilities()
               print("Available Capabilities:")
               print(json.dumps(capabilities, indent=2))
               
           else:
               print("Available commands:")
               print("  chat [user_id] [message] - Chat with agents")
               print("  status - Check agent status")
               print("  capabilities - Show available capabilities")
       else:
           print("Usage: python agent_manager.py [chat|status|capabilities] [args...]")
   
   asyncio.run(main())