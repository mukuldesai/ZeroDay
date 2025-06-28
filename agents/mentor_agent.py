import os
import yaml
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime, timedelta
import json
import openai
from anthropic import Anthropic
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from vector_store.retriever import ContextualRetriever

class MentorAgent:
    """
    Mentor Agent: Provides contextual Q&A, troubleshooting help, and guidance
    Acts as a senior developer mentor with access to team knowledge and context
    """
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.retriever = ContextualRetriever(config_path)
        self.llm_client = None
        self._initialize_llm()
        self.conversation_history = {}
        self.context_window = self.config['agents']['mentor']['context_window']
        self.problem_patterns = self._load_problem_patterns()
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from settings.yaml"""
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "settings.yaml"
            )
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _initialize_llm(self):
        """Initialize LLM client"""
        try:
            if self.config['llm']['provider'] == 'openai':
                self.llm_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            elif self.config['llm']['provider'] == 'anthropic':
                self.llm_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            
            logger.info(f"Mentor Agent initialized with {self.config['llm']['provider']}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Mentor Agent LLM: {str(e)}")
            raise
    
    def _load_problem_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load common problem patterns and their solutions"""
        return {
            "authentication_error": {
                "keywords": ["auth", "login", "token", "unauthorized", "403", "401"],
                "category": "authentication",
                "common_solutions": [
                    "Check API key configuration",
                    "Verify token expiration",
                    "Review authentication headers",
                    "Check user permissions"
                ]
            },
            "database_connection": {
                "keywords": ["database", "db", "connection", "timeout", "pool"],
                "category": "database",
                "common_solutions": [
                    "Check database credentials",
                    "Verify network connectivity",
                    "Review connection pool settings",
                    "Check database server status"
                ]
            },
            "build_failure": {
                "keywords": ["build", "compile", "webpack", "npm", "yarn", "error"],
                "category": "build",
                "common_solutions": [
                    "Clear node_modules and reinstall",
                    "Check package.json dependencies",
                    "Review build configuration",
                    "Check for syntax errors"
                ]
            },
            "deployment_issue": {
                "keywords": ["deploy", "production", "server", "docker", "k8s"],
                "category": "deployment",
                "common_solutions": [
                    "Check deployment configuration",
                    "Review environment variables",
                    "Verify resource allocation",
                    "Check logs for errors"
                ]
            },
            "performance_problem": {
                "keywords": ["slow", "performance", "memory", "cpu", "optimization"],
                "category": "performance",
                "common_solutions": [
                    "Profile application performance",
                    "Check for memory leaks",
                    "Review database queries",
                    "Optimize algorithmic complexity"
                ]
            }
        }
    
    async def provide_help(
        self,
        question: str,
        user_id: str = "default",
        context: Dict[str, Any] = None,
        conversation_id: str = None
    ) -> Dict[str, Any]:
        """
        Main method to provide mentoring help and guidance
        
        Args:
            question: User's question or problem description
            user_id: Unique identifier for the user
            context: Additional context (error messages, code snippets, etc.)
            conversation_id: Optional conversation thread ID
        """
        try:
            logger.info(f"Providing mentor help for user {user_id}: {question[:100]}...")
            
            problem_analysis = self._analyze_problem(question, context)
            relevant_context = await self._get_relevant_context(question, problem_analysis, context)
            conversation_context = self._get_conversation_context(user_id, conversation_id)
            mentor_response = await self._generate_mentor_response(
                question, problem_analysis, relevant_context, conversation_context, context
            )
            
            self._update_conversation_history(user_id, question, mentor_response, conversation_id)
            
            follow_up_suggestions = self._generate_follow_up_suggestions(
                question, mentor_response, problem_analysis
            )
            
            return {
                "success": True,
                "response": mentor_response,
                "problem_analysis": problem_analysis,
                "follow_up_suggestions": follow_up_suggestions,
                "confidence": self._calculate_confidence(relevant_context, problem_analysis),
                "sources": self._format_sources(relevant_context),
                "conversation_id": conversation_id or self._generate_conversation_id(user_id),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error providing mentor help: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error while trying to help. Please try rephrasing your question or contact a team member directly.",
                "follow_up_suggestions": [
                    "Try asking a more specific question",
                    "Include error messages or code snippets",
                    "Check the team documentation",
                    "Ask in the team chat channel"
                ]
            }
    
    def _analyze_problem(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze the type and urgency of the problem"""
        question_lower = question.lower()
        
        analysis = {
            "problem_type": "general_question",
            "urgency": "normal",
            "category": "unknown",
            "keywords": [],
            "potential_patterns": [],
            "suggested_approach": "research_and_explain"
        }
        
        
        urgency_keywords = ["urgent", "critical", "broken", "down", "production", "emergency", "asap"]
        if any(keyword in question_lower for keyword in urgency_keywords):
            analysis["urgency"] = "high"
        
        if any(word in question_lower for word in ["error", "exception", "failed", "broken", "not working"]):
            analysis["problem_type"] = "troubleshooting"
            analysis["suggested_approach"] = "diagnose_and_fix"
        elif any(word in question_lower for word in ["how", "what", "explain", "understand"]):
            analysis["problem_type"] = "knowledge_request"
            analysis["suggested_approach"] = "research_and_explain"
        elif any(word in question_lower for word in ["best practice", "should i", "recommend", "advice"]):
            analysis["problem_type"] = "guidance_request"
            analysis["suggested_approach"] = "advise_and_guide"
        elif any(word in question_lower for word in ["review", "feedback", "opinion", "thoughts"]):
            analysis["problem_type"] = "code_review"
            analysis["suggested_approach"] = "review_and_feedback"
        
        for pattern_name, pattern_info in self.problem_patterns.items():
            if any(keyword in question_lower for keyword in pattern_info["keywords"]):
                analysis["potential_patterns"].append(pattern_name)
                analysis["category"] = pattern_info["category"]
        
        import re
        words = re.findall(r'\b\w+\b', question_lower)
        tech_keywords = [word for word in words if len(word) > 3 and not word in ["that", "this", "with", "from", "what", "how"]]
        analysis["keywords"] = tech_keywords[:10] 
        

        if context:
            if "error_message" in context:
                analysis["has_error_details"] = True
            if "code_snippet" in context:
                analysis["has_code_sample"] = True
            if "stack_trace" in context:
                analysis["has_stack_trace"] = True
        
        return analysis
    
    async def _get_relevant_context(
        self,
        question: str,
        problem_analysis: Dict[str, Any],
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Retrieve relevant context from knowledge base and team resources"""
        
        enhanced_query = question
        if problem_analysis["keywords"]:
            enhanced_query += " " + " ".join(problem_analysis["keywords"][:5])
        
        context_results = await self.retriever.retrieve_for_mentor_agent(
            problem_description=enhanced_query,
            context=user_context
        )
    
        if problem_analysis["potential_patterns"]:
            pattern_context = await self._get_pattern_specific_context(
                problem_analysis["potential_patterns"][0]
            )
            
            if pattern_context and pattern_context.get("results"):
                context_results["results"].extend(pattern_context["results"][:3])
        
        return context_results
    
    async def _get_pattern_specific_context(self, pattern_name: str) -> Dict[str, Any]:
        """Get context specific to a known problem pattern"""
        pattern_info = self.problem_patterns.get(pattern_name, {})
        category = pattern_info.get("category", "")
        
        if category:

            return await self.retriever.retrieve(
                query=f"{category} troubleshooting solutions",
                collection_types=['documentation', 'tickets', 'slack_messages'],
                n_results=5
            )
        
        return {"results": []}
    
    def _get_conversation_context(self, user_id: str, conversation_id: str = None) -> List[Dict[str, Any]]:
        """Get recent conversation history for context"""
        if not conversation_id:
            conversation_id = f"{user_id}_default"
        
        history = self.conversation_history.get(conversation_id, [])
        
        return history[-self.context_window:] if history else []
    
    async def _generate_mentor_response(
        self,
        question: str,
        problem_analysis: Dict[str, Any],
        relevant_context: Dict[str, Any],
        conversation_context: List[Dict[str, Any]],
        user_context: Dict[str, Any] = None
    ) -> str:
        """Generate contextual mentor response using LLM"""
        
   
        prompt_template = self._load_prompt_template("mentor.txt")
        knowledge_context = self._format_knowledge_context(relevant_context.get('results', []))
        conversation_summary = self._format_conversation_context(conversation_context)
        problem_summary = self._format_problem_analysis(problem_analysis)
        
        formatted_prompt = prompt_template.format(
            question=question,
            problem_analysis=problem_summary,
            knowledge_context=knowledge_context,
            conversation_context=conversation_summary,
            user_context=json.dumps(user_context) if user_context else "No additional context",
            urgency=problem_analysis.get("urgency", "normal"),
            problem_type=problem_analysis.get("problem_type", "general_question")
        )
        
        try:

            if self.config['llm']['provider'] == 'openai':
                response = self.llm_client.chat.completions.create(
                    model=self.config['llm']['model'],
                    messages=[
                        {"role": "system", "content": "You are a helpful senior developer mentor who provides guidance, troubleshooting help, and technical advice to junior developers."},
                        {"role": "user", "content": formatted_prompt}
                    ],
                    temperature=self.config['llm']['temperature'],
                    max_tokens=self.config['llm']['max_tokens']
                )
                return response.choices[0].message.content
                
            elif self.config['llm']['provider'] == 'anthropic':
                response = self.llm_client.messages.create(
                    model=self.config['llm']['model'],
                    max_tokens=self.config['llm']['max_tokens'],
                    temperature=self.config['llm']['temperature'],
                    messages=[
                        {"role": "user", "content": formatted_prompt}
                    ]
                )
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"Error generating mentor response with LLM: {str(e)}")
            return self._generate_fallback_response(question, problem_analysis, relevant_context)
    
    def _format_knowledge_context(self, results: List[Dict]) -> str:
        """Format knowledge base results for prompt context"""
        if not results:
            return "No specific documentation found in knowledge base."
        
        context_parts = []
        for i, result in enumerate(results[:3]):  
            metadata = result.get('metadata', {})
            source = f"{metadata.get('source_type', 'unknown')} - {metadata.get('file_path', 'unknown')}"
            
            context_parts.append(f"Source {i+1} ({source}):\n{result['content'][:300]}...")
        
        return "\n\n".join(context_parts)
    
    def _format_conversation_context(self, conversation_context: List[Dict]) -> str:
        """Format recent conversation history"""
        if not conversation_context:
            return "No previous conversation context."
        
        context_parts = []
        for i, exchange in enumerate(conversation_context[-3:]):  
            context_parts.append(f"Previous Q{i+1}: {exchange.get('question', '')[:100]}...")
            context_parts.append(f"Previous A{i+1}: {exchange.get('response', '')[:150]}...")
        
        return "\n".join(context_parts)
    
    def _format_problem_analysis(self, problem_analysis: Dict[str, Any]) -> str:
        """Format problem analysis for prompt"""
        return f"""
        Problem Type: {problem_analysis.get('problem_type', 'unknown')}
        Urgency: {problem_analysis.get('urgency', 'normal')}
        Category: {problem_analysis.get('category', 'unknown')}
        Detected Patterns: {', '.join(problem_analysis.get('potential_patterns', ['none']))}
        Key Keywords: {', '.join(problem_analysis.get('keywords', [])[:5])}
        Suggested Approach: {problem_analysis.get('suggested_approach', 'research_and_explain')}
        """
    
    def _load_prompt_template(self, template_name: str) -> str:
        """Load prompt template from configs/prompts/"""
        template_path = os.path.join(
            os.path.dirname(__file__), "..", "configs", "prompts", template_name
        )
        
        try:
            with open(template_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"Prompt template {template_name} not found, using default")
            return self._get_default_mentor_prompt()
    
    def _get_default_mentor_prompt(self) -> str:
        """Default mentor prompt template"""
        return """
        You are a senior developer mentor helping a team member. Provide helpful, actionable guidance.

        QUESTION: {question}

        PROBLEM ANALYSIS:
        {problem_analysis}

        RELEVANT KNOWLEDGE BASE CONTEXT:
        {knowledge_context}

        CONVERSATION HISTORY:
        {conversation_context}

        USER CONTEXT: {user_context}

        URGENCY LEVEL: {urgency}
        PROBLEM TYPE: {problem_type}

        Provide a helpful response that:
        1. Directly addresses the question
        2. Uses available context and documentation
        3. Provides step-by-step guidance when appropriate
        4. Suggests next steps and resources
        5. Maintains an encouraging, mentoring tone

        If this is a troubleshooting issue, provide:
        - Immediate diagnostic steps
        - Common causes and solutions
        - When to escalate for help

        If this is a learning question, provide:
        - Clear explanations with examples
        - Links to relevant resources
        - Suggestions for further learning
        """
    
    def _generate_fallback_response(
        self,
        question: str,
        problem_analysis: Dict[str, Any],
        relevant_context: Dict[str, Any]
    ) -> str:
        """Generate fallback response when LLM fails"""
        
        problem_type = problem_analysis.get('problem_type', 'general_question')
        
        if problem_type == 'troubleshooting':
            return f"""I understand you're experiencing an issue. Here's how I'd approach this:

1. **Immediate Steps:**
   - Check for any error messages in logs
   - Verify your configuration settings
   - Try reproducing the issue in a clean environment

2. **Common Causes:**
   - Configuration issues
   - Environment differences
   - Dependency conflicts

3. **Next Steps:**
   - Share any error messages you're seeing
   - Check our troubleshooting documentation
   - Ask a team member for a quick pair programming session

Let me know what you discover, and I can provide more specific guidance!"""
        
        elif problem_type == 'knowledge_request':
            context_summary = "Based on our knowledge base, " if relevant_context.get('results') else ""
            return f"""{context_summary}here's what I can tell you about your question:

{question}

For comprehensive information, I recommend:
1. Checking our internal documentation
2. Looking at similar implementations in the codebase
3. Asking team members who have worked on related features

Would you like me to help you find specific resources or examples?"""
        
        else:
            return f"""Thanks for your question about: {question}

I'd be happy to help! To provide the best guidance, could you share:
- More specific details about what you're trying to achieve
- Any error messages or unexpected behavior you're seeing
- What you've already tried

In the meantime, check our documentation and feel free to ask team members in the chat channel."""
    
    def _update_conversation_history(
        self,
        user_id: str,
        question: str,
        response: str,
        conversation_id: str = None
    ):
        """Update conversation history for context continuity"""
        if not conversation_id:
            conversation_id = f"{user_id}_default"
        
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []
        
        
        exchange = {
            "question": question,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
        self.conversation_history[conversation_id].append(exchange)
        
    
        if len(self.conversation_history[conversation_id]) > 50:
            self.conversation_history[conversation_id] = self.conversation_history[conversation_id][-50:]
        

        cutoff_date = datetime.now() - timedelta(days=7)
        for conv_id, history in list(self.conversation_history.items()):
            if history and datetime.fromisoformat(history[-1]["timestamp"]) < cutoff_date:
                del self.conversation_history[conv_id]
    
    def _generate_follow_up_suggestions(
        self,
        question: str,
        response: str,
        problem_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate helpful follow-up suggestions"""
        suggestions = []
        
        problem_type = problem_analysis.get('problem_type', 'general_question')
        urgency = problem_analysis.get('urgency', 'normal')
        
        if problem_type == 'troubleshooting':
            suggestions.extend([
                "Share any error messages or logs you're seeing",
                "Try the suggested diagnostic steps and report back",
                "Check if this issue affects other team members",
                "Consider scheduling a pair programming session"
            ])
            
            if urgency == 'high':
                suggestions.insert(0, "If this is blocking production, escalate to senior team members immediately")
        
        elif problem_type == 'knowledge_request':
            suggestions.extend([
                "Ask for clarification on any concepts that aren't clear",
                "Request examples or code samples",
                "Look for related topics in the documentation",
                "Practice with a small implementation"
            ])
        
        elif problem_type == 'code_review':
            suggestions.extend([
                "Share the specific code you'd like reviewed",
                "Mention any particular areas of concern",
                "Ask about best practices for this use case",
                "Request suggestions for testing approaches"
            ])
        

        suggestions.extend([
            "Document your solution for future reference",
            "Share learnings with the team",
            "Update documentation if needed"
        ])
        
        return suggestions[:5]  
    
    def _calculate_confidence(
        self,
        relevant_context: Dict[str, Any],
        problem_analysis: Dict[str, Any]
    ) -> float:
        """Calculate confidence in the response"""
        base_confidence = 0.7
        

        if relevant_context.get('results'):
            avg_relevance = relevant_context.get('relevance_stats', {}).get('avg_score', 0.0)
            base_confidence += 0.2 * avg_relevance
    
        if problem_analysis.get('potential_patterns'):
            base_confidence += 0.1
        
        if problem_analysis.get('urgency') == 'high':
            base_confidence -= 0.1
        
        return min(1.0, max(0.3, base_confidence))
    
    def _format_sources(self, relevant_context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Format sources from context retrieval"""
        sources = []
        
        for result in relevant_context.get('results', [])[:3]:
            metadata = result.get('metadata', {})
            sources.append({
                "type": metadata.get('source_type', 'unknown'),
                "path": metadata.get('file_path', 'unknown'),
                "section": metadata.get('section', ''),
                "relevance": result.get('relevance_score', 0.0)
            })
        
        return sources
    
    def _generate_conversation_id(self, user_id: str) -> str:
        """Generate a new conversation ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{user_id}_{timestamp}"
    
    async def get_mentor_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get mentoring statistics"""
        stats = {
            "timestamp": datetime.now().isoformat(),
            "total_conversations": len(self.conversation_history),
            "active_conversations": 0,
            "problem_type_distribution": {},
            "common_topics": []
        }
        
        cutoff = datetime.now() - timedelta(hours=24)
        
        problem_types = []
        for conv_history in self.conversation_history.values():
            if conv_history:
                last_exchange = conv_history[-1]
                if datetime.fromisoformat(last_exchange["timestamp"]) > cutoff:
                    stats["active_conversations"] += 1
                
        
        if user_id and f"{user_id}_default" in self.conversation_history:
            user_history = self.conversation_history[f"{user_id}_default"]
            stats["user_conversation_count"] = len(user_history)
            stats["user_last_interaction"] = user_history[-1]["timestamp"] if user_history else None
        
        return stats


def quick_mentor_help(question: str, user_id: str = "test_user") -> Dict[str, Any]:
    """Quick mentor help for testing"""
    mentor = MentorAgent()
    import asyncio
    return asyncio.run(mentor.provide_help(question, user_id))

if __name__ == "__main__":
    
    import sys
    import asyncio
    import json
    
    async def main():
        if len(sys.argv) > 1:
            command = sys.argv[1]
            mentor = MentorAgent()
            
            if command == "help":
                question = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "How do I debug authentication errors?"
                result = await mentor.provide_help(question, "cli_user")
                print("Mentor Response:")
                print(json.dumps(result, indent=2))
                
            elif command == "stats":
                stats = await mentor.get_mentor_stats()
                print("Mentor Statistics:")
                print(json.dumps(stats, indent=2))
                
            else:
                print("Available commands:")
                print("  help [question] - Get mentor help")
                print("  stats - Show mentor statistics")
        else:
            print("Usage: python mentor_agent.py [help|stats] [args...]")
    
    asyncio.run(main())