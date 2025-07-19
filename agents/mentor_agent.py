import os
import sys
import yaml
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime, timedelta
import json
import openai
from openai import OpenAI 
from anthropic import Anthropic
import re
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from vector_store.retriever import ContextualRetriever
from dotenv import load_dotenv
load_dotenv()

class MentorAgent:
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.retriever = ContextualRetriever(config_path)
        self.llm_initialized = False
        self._initialize_llm()
        self.conversation_history = {}
        self.context_window = self.config['agents']['mentor']['context_window']
        self.problem_patterns = self._load_problem_patterns()
        
    def _load_config(self, config_path: str = None) -> Dict:
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "settings.yaml"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _initialize_llm(self):
        """Initialize LLM with fallback support"""
        self.llm_client = None
        self.llm_provider = None
        self.fallback_client = None
        self.fallback_provider = None
        
      
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        primary_provider = self.config['llm']['provider']
        fallback_provider = self.config['llm'].get('fallback_provider', 'anthropic' if primary_provider == 'openai' else 'openai')
        
        try:
            
            if primary_provider == 'openai' and openai_key:
                self.llm_client = openai.OpenAI(api_key=openai_key)
                self.llm_provider = 'openai'
                logger.info(f"Mentor Agent - Primary LLM: OpenAI initialized")
                
            elif primary_provider == 'anthropic' and anthropic_key:
                self.llm_client = Anthropic(api_key=anthropic_key)
                self.llm_provider = 'anthropic'
                logger.info(f"Mentor Agent - Primary LLM: Anthropic initialized")
            
            # Initialize fallback provider
            if fallback_provider == 'openai' and openai_key and self.llm_provider != 'openai':
                self.fallback_client = openai.OpenAI(api_key=openai_key)
                self.fallback_provider = 'openai'
                logger.info(f"Mentor Agent - Fallback LLM: OpenAI ready")
                
            elif fallback_provider == 'anthropic' and anthropic_key and self.llm_provider != 'anthropic':
                self.fallback_client = Anthropic(api_key=anthropic_key)
                self.fallback_provider = 'anthropic'
                logger.info(f"Mentor Agent - Fallback LLM: Anthropic ready")
            
            if self.llm_client:
                self.llm_initialized = True
                logger.info(f"Mentor Agent initialized - Primary: {self.llm_provider}, Fallback: {self.fallback_provider or 'None'}")
            else:
                raise ValueError("No valid API keys found")
                
        except Exception as e:
            logger.error(f"Mentor Agent LLM initialization failed: {e}")
            self.llm_initialized = False
            raise

    def _call_llm_with_fallback(self, messages, **kwargs):
        """Call LLM with automatic fallback"""
        
        # Try primary provider first
        if self.llm_client and self.llm_provider:
            try:
                return self._make_llm_call(self.llm_client, self.llm_provider, messages, **kwargs)
            except Exception as e:
                logger.warning(f"Mentor Agent - Primary LLM ({self.llm_provider}) failed: {e}")
                
                # Try fallback if available
                if self.fallback_client and self.fallback_provider:
                    logger.info(f"Mentor Agent - Switching to fallback LLM: {self.fallback_provider}")
                    try:
                        return self._make_llm_call(self.fallback_client, self.fallback_provider, messages, **kwargs)
                    except Exception as fallback_error:
                        logger.error(f"Mentor Agent - Fallback LLM ({self.fallback_provider}) also failed: {fallback_error}")
                        raise
                else:
                    raise
        else:
            raise RuntimeError("No LLM client available")

    def _make_llm_call(self, client, provider, messages, **kwargs):
        """Make actual LLM API call"""
        if provider == 'openai':
            response = client.chat.completions.create(
                model=self.config['llm']['model'],
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 800),
                timeout=30
            )
            return response.choices[0].message.content.strip()
            
        elif provider == 'anthropic':
            # Convert messages format for Anthropic
            if isinstance(messages, list) and len(messages) > 1:
                system_msg = messages[0]['content'] if messages[0]['role'] == 'system' else ''
                user_msg = messages[1]['content'] if len(messages) > 1 else messages[0]['content']
                combined_prompt = f"{system_msg}\n\n{user_msg}"
            else:
                combined_prompt = messages[0]['content'] if isinstance(messages, list) else str(messages)
                
            response = client.messages.create(
                model=self.config['llm'].get('fallback_model', 'claude-3-haiku-20240307'),
                max_tokens=kwargs.get('max_tokens', 800),
                temperature=kwargs.get('temperature', 0.7),
                messages=[{"role": "user", "content": combined_prompt}]
            )
            return response.content[0].text.strip()
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _load_problem_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load problem patterns for quick categorization"""
        return {
            "authentication_error": {
                "keywords": ["auth", "login", "token", "unauthorized", "403", "401", "session"],
                "category": "authentication",
                "urgency": "high",
                "common_causes": ["expired tokens", "incorrect credentials", "misconfigured auth"]
            },
            "database_connection": {
                "keywords": ["database", "db", "connection", "timeout", "pool", "sql"],
                "category": "database",
                "urgency": "high",
                "common_causes": ["connection limits", "network issues", "invalid credentials"]
            },
            "build_failure": {
                "keywords": ["build", "compile", "webpack", "npm", "yarn", "error", "failed"],
                "category": "build",
                "urgency": "medium",
                "common_causes": ["dependency issues", "version conflicts", "configuration errors"]
            },
            "api_error": {
                "keywords": ["404", "500", "api", "endpoint", "request", "response", "cors"],
                "category": "api",
                "urgency": "medium",
                "common_causes": ["wrong URL", "server issues", "CORS problems"]
            },
            "performance_problem": {
                "keywords": ["slow", "performance", "memory", "cpu", "optimization", "lag"],
                "category": "performance",
                "urgency": "medium",
                "common_causes": ["inefficient queries", "memory leaks", "large datasets"]
            },
            "deployment_issue": {
                "keywords": ["deploy", "deployment", "production", "server", "hosting"],
                "category": "deployment",
                "urgency": "high",
                "common_causes": ["environment differences", "configuration issues", "dependencies"]
            }
        }
    
    def _clean_text_fast(self, text: str) -> str:
        """Fast text cleaning - simplified version"""
        if not text:
            return ""
        
        try:
            text = str(text)[:3000]  
            
            
            text = text.replace('\x8f', '').replace('\x9f', '').replace('\x81', '').replace('\x9d', '')
            
            
            cleaned = ''.join(c for c in text if 32 <= ord(c) <= 126 or c in '\n\r\t')
            
            return cleaned[:2500]  
            
        except Exception:
            return "Content processing error"
    
    def _clean_dict_fast(self, data: dict) -> dict:
        """Fast dictionary cleaning"""
        if not isinstance(data, dict):
            return {}
        
        cleaned = {}
        for key, value in list(data.items())[:10]: 
            try:
                if isinstance(value, str):
                    cleaned[str(key)] = self._clean_text_fast(value)
                elif isinstance(value, (int, float, bool)):
                    cleaned[str(key)] = value
                else:
                    cleaned[str(key)] = str(value)[:200]
            except:
                cleaned[str(key)] = "error"
        
        return cleaned

    def _analyze_problem_comprehensively(self, question: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Comprehensive problem analysis with better categorization"""
        question_lower = question.lower()
        
        analysis = {
            "problem_type": "general_question",
            "urgency": "normal",
            "category": "unknown",
            "keywords": [],
            "detected_patterns": [],
            "complexity": "medium",
            "user_experience_level": "intermediate",
            "requires_immediate_action": False,
            "suggested_approach": "standard_help"
        }
        
       
        urgent_indicators = ["urgent", "critical", "broken", "down", "production", "can't", "stuck", "emergency"]
        high_urgency_count = sum(1 for indicator in urgent_indicators if indicator in question_lower)
        
        if high_urgency_count >= 2:
            analysis["urgency"] = "critical"
            analysis["requires_immediate_action"] = True
        elif high_urgency_count >= 1:
            analysis["urgency"] = "high"
        elif any(word in question_lower for word in ["help", "issue", "problem"]):
            analysis["urgency"] = "medium"
        
        
        if any(word in question_lower for word in ["error", "exception", "failed", "broken", "crash"]):
            analysis["problem_type"] = "troubleshooting"
            analysis["suggested_approach"] = "diagnostic_steps"
        elif any(word in question_lower for word in ["how", "what", "explain", "understand", "learn"]):
            analysis["problem_type"] = "knowledge_request"
            analysis["suggested_approach"] = "educational"
        elif any(word in question_lower for word in ["review", "feedback", "opinion", "advice"]):
            analysis["problem_type"] = "guidance_request"
            analysis["suggested_approach"] = "advisory"
        elif any(word in question_lower for word in ["best", "practice", "recommend", "should"]):
            analysis["problem_type"] = "best_practices"
            analysis["suggested_approach"] = "recommendations"
        
        
        pattern_matches = []
        for pattern_name, pattern_info in self.problem_patterns.items():
            keyword_matches = sum(1 for keyword in pattern_info["keywords"] if keyword in question_lower)
            if keyword_matches > 0:
                confidence = keyword_matches / len(pattern_info["keywords"])
                pattern_matches.append({
                    "pattern": pattern_name,
                    "confidence": confidence,
                    "category": pattern_info["category"],
                    "urgency": pattern_info["urgency"]
                })
        
        
        if pattern_matches:
            best_match = max(pattern_matches, key=lambda x: x["confidence"])
            analysis["detected_patterns"].append(best_match["pattern"])
            analysis["category"] = best_match["category"]
            if best_match["urgency"] == "high" and analysis["urgency"] == "normal":
                analysis["urgency"] = "medium"
        
        
        complexity_indicators = {
            "simple": ["simple", "quick", "basic", "easy"],
            "complex": ["complex", "advanced", "architecture", "system", "multiple", "integration"]
        }
        
        for complexity, indicators in complexity_indicators.items():
            if any(indicator in question_lower for indicator in indicators):
                analysis["complexity"] = complexity
                break
        
       
        beginner_indicators = ["basic", "simple", "new to", "just started", "don't understand"]
        advanced_indicators = ["architecture", "performance", "optimization", "design pattern"]
        
        if any(indicator in question_lower for indicator in beginner_indicators):
            analysis["user_experience_level"] = "beginner"
        elif any(indicator in question_lower for indicator in advanced_indicators):
            analysis["user_experience_level"] = "advanced"
        
       
        technical_terms = re.findall(r'\b(?:react|vue|python|javascript|node|api|database|auth|deploy)\b', question_lower)
        analysis["technical_focus"] = list(set(technical_terms))
        
        return analysis

    async def provide_help(self, question: str, user_id: str = "default", context=None, user_context: Dict[str, Any] = None, conversation_id: str = None) -> Dict[str, Any]:
        """Enhanced mentor help with comprehensive problem analysis"""
        try:
            logger.info(f"Providing mentor help for user {user_id}: {question[:100]}...")
            
            
            question = self._clean_text_fast(question)
            user_id = self._clean_text_fast(user_id)
            user_context = self._clean_dict_fast(user_context or {})
            
            if not question.strip():
                return self._create_helpful_response("I'm here to help! What specific challenge are you facing or what would you like guidance on?", user_id)
            
           
            problem_analysis = self._analyze_problem_comprehensively(question, user_context)
            
            
            try:
                relevant_context = await self._get_enhanced_context(question, problem_analysis)
            except Exception as e:
                logger.warning(f"Context retrieval failed: {e}")
                relevant_context = "Using general mentoring knowledge based on ZeroDay platform experience."
            
           
            try:
                response = await self._generate_contextual_response(question, problem_analysis, relevant_context, user_context)
            except Exception as e:
                logger.error(f"Response generation failed: {e}")
                response = self._generate_intelligent_fallback(question, problem_analysis)
            
            return {
                "success": True,
                "response": response,
                "agent_type": "mentor",
                "user_id": user_id,
                "problem_analysis": problem_analysis,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "confidence": 0.85,
                "follow_up_suggestions": self._generate_follow_up_suggestions(problem_analysis)
            }
            
        except Exception as e:
            logger.error(f"Mentor agent error: {e}")
            return self._create_helpful_response("I'm having some technical difficulties, but I'm still here to help. Could you try rephrasing your question?", user_id)
    
    async def _get_enhanced_context(self, question: str, problem_analysis: Dict[str, Any]) -> str:
        """Get enhanced context based on problem analysis"""
        try:
            
            query_parts = [question]
            
           
            category = problem_analysis.get("category", "general")
            if category != "unknown":
                query_parts.append(category)
            
            
            technical_focus = problem_analysis.get("technical_focus", [])
            query_parts.extend(technical_focus)
            
            enhanced_query = " ".join(query_parts)
            
           
            context_results = await self.retriever.retrieve(
                query=enhanced_query,
                collection_types=['documentation', 'tickets', 'pull_requests'],
                n_results=5
            )

            if context_results and context_results.get('results'):
                context_parts = []
                for result in context_results['results'][:3]:
                    content = result.get('content', '')[:300]
                    source = result.get('metadata', {}).get('source_type', 'team knowledge')
                    context_parts.append(f"From {source}: {content}")
                
                return "\n\n".join(context_parts)
            else:
                return f"General guidance for {category} issues in ZeroDay platform development."

        except Exception as e:
            logger.warning(f"Enhanced context retrieval failed: {e}")
            return "Using general development mentoring knowledge."
    
    async def _generate_contextual_response(self, question: str, problem_analysis: Dict[str, Any], 
                                          relevant_context: str, user_context: Dict[str, Any] = None) -> str:
        """Generate contextual response using enhanced prompting"""
        try:
          
            system_prompt = self._load_enhanced_mentor_prompt()
            
            
            problem_type = problem_analysis.get('problem_type', 'general_question')
            urgency = problem_analysis.get('urgency', 'normal')
            category = problem_analysis.get('category', 'general')
            complexity = problem_analysis.get('complexity', 'medium')
            user_experience = problem_analysis.get('user_experience_level', 'intermediate')
            technical_focus = ', '.join(problem_analysis.get('technical_focus', ['general']))
            
            user_prompt = f"""Question from developer: {question}

Problem Analysis:
- Type: {problem_type}
- Category: {category}  
- Urgency: {urgency}
- Complexity: {complexity}
- User Experience Level: {user_experience}
- Technical Focus: {technical_focus}

Relevant Context from ZeroDay Platform:
{relevant_context}

Please provide helpful, specific guidance that:
1. Addresses their immediate question
2. Provides actionable steps they can take
3. Explains the reasoning behind your advice
4. Considers their experience level
5. Offers follow-up guidance

Be encouraging and practical. If this is urgent, prioritize immediate solutions."""

           
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            return self._call_llm_with_fallback(messages, temperature=0.7, max_tokens=800)
                
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise

    def _load_enhanced_mentor_prompt(self) -> str:
        """Load enhanced mentor prompt template"""
        template_path = os.path.join(
            os.path.dirname(__file__), "..", "configs", "prompts", "mentor.txt"
        )
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"Mentor prompt template not found, using default")
            return """You are Marcus Chen, a senior software engineer with 8+ years of experience. You're known for being practical, patient, and great at explaining complex concepts simply.

Your expertise includes:
- Full-stack development (React, Node.js, Python, FastAPI)
- System architecture and debugging
- Mentoring developers of all levels
- ZeroDay AI platform architecture and best practices

Your communication style:
- Give specific, actionable advice
- Explain the 'why' behind recommendations
- Ask clarifying questions when needed
- Break down complex problems into manageable steps
- Share relevant experience and examples
- Be encouraging and build confidence

Always consider the developer's experience level and provide appropriate guidance. Focus on teaching problem-solving skills, not just solving the immediate problem."""

    def _generate_intelligent_fallback(self, question: str, problem_analysis: Dict[str, Any]) -> str:
        """Generate intelligent fallback response based on problem analysis"""
        problem_type = problem_analysis.get('problem_type', 'general_question')
        urgency = problem_analysis.get('urgency', 'normal')
        category = problem_analysis.get('category', 'general')
        complexity = problem_analysis.get('complexity', 'medium')
        user_experience = problem_analysis.get('user_experience_level', 'intermediate')
        
        if urgency in ['critical', 'high'] and problem_type == 'troubleshooting':
            return f"""I can see this is urgent and you're dealing with a {category} issue. Here's my immediate guidance:

URGENT STEPS:
1. Check for error messages in logs/console - they often point directly to the issue
2. If this is affecting production, consider rolling back recent changes
3. Verify basic connectivity and configuration
4. Check if others are experiencing the same issue

For {category} problems specifically:
- Look for recent changes in related configuration
- Verify environment variables and dependencies
- Check network connectivity if applicable

{f"Since this seems {complexity}, don't hesitate to escalate to senior team members immediately." if complexity == "complex" else ""}

Once stabilized, we can dig into the root cause. What specific error messages are you seeing?"""
        
        elif problem_type == 'knowledge_request':
            return f"""Great question! Understanding {category} concepts is important for your development as a {user_experience} developer.

Here's how I'd approach explaining this:

1. Let me break this down into core concepts first
2. I'll provide practical examples from our ZeroDay platform
3. We'll connect this to what you might already know
4. I'll suggest hands-on ways to practice

{f"Since you're working with {category}, this directly applies to the work you're doing." if category != "general" else ""}

To give you the most helpful explanation, could you tell me:
- What specific aspect are you most curious about?
- What's your current understanding of this topic?
- Are you trying to implement something specific?

This will help me tailor my explanation to be most useful for you."""
        
        elif problem_type == 'guidance_request':
            return f"""I'd be happy to provide guidance on this. As a {user_experience} developer, you're asking good questions about {category}.

My approach to giving you solid advice:

1. Understanding your specific situation and constraints
2. Sharing what's worked well in similar scenarios
3. Explaining trade-offs of different approaches
4. Giving you a practical path forward

For {category} decisions, I typically consider:
- Technical requirements and constraints
- Team practices and standards
- Long-term maintainability
- Performance and scalability needs

To give you the most relevant advice, it would help to know:
- What are you trying to accomplish?
- What constraints or requirements do you have?
- What approaches have you already considered?

This context will help me give you much more targeted and useful guidance."""
        
        else:
            return f"""Thanks for reaching out! I'm here to help with any development challenges you're facing.

I can see you're asking about {category}, which is a great area to get guidance on. As a mentor, I find it most helpful when I understand:

- What you're trying to accomplish
- Where you're getting stuck or what's confusing
- What you've already tried or researched
- Your experience level with this particular topic

This helps me provide advice that's actually useful for your specific situation rather than generic information.

{f"Since this seems like a {complexity} topic, we can break it down step by step." if complexity != "medium" else ""}

What specific aspect would you like to dive into first?"""
    
    def _generate_follow_up_suggestions(self, problem_analysis: Dict[str, Any]) -> List[str]:
        """Generate contextual follow-up suggestions"""
        problem_type = problem_analysis.get('problem_type', 'general_question')
        category = problem_analysis.get('category', 'general')
        complexity = problem_analysis.get('complexity', 'medium')
        
        suggestions = []
        
        if problem_type == 'troubleshooting':
            suggestions.extend([
                "Share any error messages or logs you're seeing",
                "Describe what you were doing when the issue occurred",
                "Let me know what debugging steps you've already tried"
            ])
        elif problem_type == 'knowledge_request':
            suggestions.extend([
                "Ask about specific implementation examples",
                "Request clarification on any confusing parts",
                "Share what you plan to build with this knowledge"
            ])
        elif problem_type == 'guidance_request':
            suggestions.extend([
                "Describe your specific use case or requirements",
                "Share what approaches you've considered",
                "Ask about trade-offs between different solutions"
            ])
        
      
        if category == 'authentication':
            suggestions.append("Check authentication flow and token handling")
        elif category == 'database':
            suggestions.append("Review database connection and query patterns")
        elif category == 'api':
            suggestions.append("Verify API endpoints and request/response format")
        elif category == 'performance':
            suggestions.append("Profile the application to identify bottlenecks")
        
        
        if complexity == 'complex':
            suggestions.append("Consider breaking this into smaller, manageable pieces")
        
        return suggestions[:4]  

    def _create_helpful_response(self, message: str, user_id: str) -> Dict[str, Any]:
        """Create a helpful response structure"""
        return {
            "success": True,
            "response": message,
            "agent_type": "mentor",
            "user_id": user_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "confidence": 0.8,
            "follow_up_suggestions": [
                "Share more details about your specific situation",
                "Describe what you've already tried",
                "Let me know your experience level with this topic"
            ]
        }
    
    def _load_prompt_template(self, template_name: str) -> str:
        """Load prompt template with fallback"""
        template_path = os.path.join(
            os.path.dirname(__file__), "..", "configs", "prompts", template_name
        )
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"Prompt template {template_name} not found, using default")
            return "You are a helpful senior developer mentor. Provide specific, actionable guidance for: {question}"



def quick_mentor_help(question: str, user_id: str = "test_user") -> Dict[str, Any]:
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
            else:
                print("Available commands:")
                print("  help [question] - Get mentor help")
        else:
            print("Usage: python mentor_agent.py help [question]")
    
    asyncio.run(main())