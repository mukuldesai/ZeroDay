import os
import sys
import yaml
from typing import Union, Dict, Any, List, Optional
from loguru import logger
from datetime import datetime, timedelta
import json
import openai
from anthropic import Anthropic
from vector_store.retriever import ContextualRetriever
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class TaskAgent:
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.retriever = ContextualRetriever(config_path)
        self.llm_client = None
        self.llm_initialized = False 
        self._initialize_llm()
        
        self.task_categories = self._load_task_categories()
        self.skill_progression = self._load_skill_progression()
        
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
                logger.info(f"Task Agent - Primary LLM: OpenAI initialized")
                
            elif primary_provider == 'anthropic' and anthropic_key:
                self.llm_client = Anthropic(api_key=anthropic_key)
                self.llm_provider = 'anthropic'
                logger.info(f"Task Agent - Primary LLM: Anthropic initialized")
            
            
            if fallback_provider == 'openai' and openai_key and self.llm_provider != 'openai':
                self.fallback_client = openai.OpenAI(api_key=openai_key)
                self.fallback_provider = 'openai'
                logger.info(f"Task Agent - Fallback LLM: OpenAI ready")
                
            elif fallback_provider == 'anthropic' and anthropic_key and self.llm_provider != 'anthropic':
                self.fallback_client = Anthropic(api_key=anthropic_key)
                self.fallback_provider = 'anthropic'
                logger.info(f"Task Agent - Fallback LLM: Anthropic ready")
            
            if self.llm_client:
                self.llm_initialized = True
                logger.info(f"Task Agent initialized - Primary: {self.llm_provider}, Fallback: {self.fallback_provider or 'None'}")
            else:
                raise ValueError("No valid API keys found")
                
        except Exception as e:
            logger.error(f"Task Agent LLM initialization failed: {e}")
            self.llm_initialized = False
            raise

    def _call_llm_with_fallback(self, messages, **kwargs):
        """Call LLM with automatic fallback"""
        
       
        if self.llm_client and self.llm_provider:
            try:
                return self._make_llm_call(self.llm_client, self.llm_provider, messages, **kwargs)
            except Exception as e:
                logger.warning(f"Task Agent - Primary LLM ({self.llm_provider}) failed: {e}")
                
                
                if self.fallback_client and self.fallback_provider:
                    logger.info(f"Task Agent - Switching to fallback LLM: {self.fallback_provider}")
                    try:
                        return self._make_llm_call(self.fallback_client, self.fallback_provider, messages, **kwargs)
                    except Exception as fallback_error:
                        logger.error(f"Task Agent - Fallback LLM ({self.fallback_provider}) also failed: {fallback_error}")
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
    
    def _load_task_categories(self) -> Dict[str, Dict[str, Any]]:
        """Load task categories for quick categorization"""
        return {
            "bug_fix": {
                "description": "Fix existing bugs and issues",
                "skills": ["debugging", "testing", "problem_solving"],
                "difficulty_range": ["beginner", "intermediate", "advanced"],
                "time_estimate": {"beginner": "2-4 hours", "intermediate": "4-8 hours", "advanced": "1-3 days"}
            },
            "feature": {
                "description": "Implement new features or functionality",
                "skills": ["design", "implementation", "testing", "documentation"],
                "difficulty_range": ["intermediate", "advanced"],
                "time_estimate": {"intermediate": "1-3 days", "advanced": "3-7 days"}
            },
            "refactor": {
                "description": "Improve code quality and structure",
                "skills": ["code_review", "architecture", "best_practices"],
                "difficulty_range": ["intermediate", "advanced"],
                "time_estimate": {"intermediate": "4-8 hours", "advanced": "1-2 days"}
            },
            "test": {
                "description": "Write tests for existing functionality",
                "skills": ["testing", "test_design", "automation"],
                "difficulty_range": ["beginner", "intermediate"],
                "time_estimate": {"beginner": "1-3 hours", "intermediate": "3-6 hours"}
            },
            "docs": {
                "description": "Improve documentation and guides",
                "skills": ["writing", "documentation", "user_experience"],
                "difficulty_range": ["beginner", "intermediate"],
                "time_estimate": {"beginner": "1-2 hours", "intermediate": "2-4 hours"}
            },
            "learning": {
                "description": "Learning exercises and skill building",
                "skills": ["research", "practice", "experimentation"],
                "difficulty_range": ["beginner", "intermediate", "advanced"],
                "time_estimate": {"beginner": "2-4 hours", "intermediate": "4-6 hours", "advanced": "6-8 hours"}
            }
        }
    
    def _load_skill_progression(self) -> Dict[str, List[str]]:
        """Load skill progression paths"""
        return {
            "frontend": [
                "HTML/CSS basics", "JavaScript fundamentals", "React components", 
                "State management", "API integration", "Testing", "Performance optimization"
            ],
            "backend": [
                "API basics", "Database queries", "Authentication", "Business logic",
                "Performance optimization", "System design", "Security"
            ],
            "fullstack": [
                "Frontend basics", "Backend APIs", "Database integration", 
                "Authentication flow", "Testing", "Deployment", "System architecture"
            ],
            "devops": [
                "Environment setup", "CI/CD basics", "Containerization", 
                "Cloud deployment", "Monitoring", "Security", "Infrastructure as code"
            ]
        }
    
    def _clean_text_fast(self, text: str) -> str:
        """Fast text cleaning"""
        if not text:
            return ""
        
        try:
            text = str(text)[:2000]
            
            text = text.replace('\x8f', '').replace('\x9f', '').replace('\x81', '').replace('\x9d', '')
            
            return ''.join(c for c in text if 32 <= ord(c) <= 126 or c in '\n\r\t')
        except:
            return "Content processing error"
    
    def _clean_dict_fast(self, data: dict) -> dict:
        """Fast dictionary cleaning"""
        if not isinstance(data, dict):
            return {}
        
        cleaned = {}
        for key, value in list(data.items())[:5]: 
            try:
                if isinstance(value, str):
                    cleaned[str(key)] = self._clean_text_fast(value)
                elif isinstance(value, (int, float, bool)):
                    cleaned[str(key)] = value
                else:
                    cleaned[str(key)] = str(value)[:100]
            except:
                cleaned[str(key)] = "error"
        
        return cleaned

    def _analyze_user_profile(self, user_role: str, skill_level: str, interests: List[str], 
                            learning_goals: List[str], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user profile for better task matching"""
        profile = {
            "primary_focus": user_role,
            "skill_level": skill_level,
            "preferred_tasks": [],
            "learning_priority": "skill_building",
            "time_preference": "medium",
            "challenge_level": "appropriate"
        }
        
        
        if interests:
            interests_text = " ".join(interests).lower()
            if any(word in interests_text for word in ["bug", "fix", "debug"]):
                profile["preferred_tasks"].append("bug_fix")
            if any(word in interests_text for word in ["feature", "new", "build"]):
                profile["preferred_tasks"].append("feature")
            if any(word in interests_text for word in ["test", "quality"]):
                profile["preferred_tasks"].append("test")
            if any(word in interests_text for word in ["doc", "write", "explain"]):
                profile["preferred_tasks"].append("docs")
        
        
        if learning_goals:
            goals_text = " ".join(learning_goals).lower()
            if any(word in goals_text for word in ["quick", "fast", "urgent"]):
                profile["time_preference"] = "short"
                profile["challenge_level"] = "focused"
            elif any(word in goals_text for word in ["deep", "thorough", "master"]):
                profile["time_preference"] = "long"
                profile["challenge_level"] = "comprehensive"
            
            
            if any(word in goals_text for word in ["practice", "hands-on", "build"]):
                profile["learning_priority"] = "practical"
            elif any(word in goals_text for word in ["understand", "learn", "theory"]):
                profile["learning_priority"] = "conceptual"
        
        
        if skill_level == "beginner":
            profile["challenge_level"] = "gentle"
            profile["learning_priority"] = "fundamentals"
        elif skill_level == "advanced":
            profile["challenge_level"] = "stretch"
            profile["learning_priority"] = "leadership"
        
        return profile

    async def suggest_tasks(
        self,
        user_id: str,
        user_role: str,
        skill_level: str = "beginner",
        interests: List[str] = None,
        learning_goals: List[str] = None,
        time_available: str = "2-4 hours",
        context=None,
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Enhanced task suggestion with better personalization"""
        try:
            logger.info(f"Suggesting tasks for user {user_id}: {skill_level} {user_role} developer")
            
            
            user_id = self._clean_text_fast(user_id)
            user_role = self._clean_text_fast(user_role)
            skill_level = self._clean_text_fast(skill_level)
            time_available = self._clean_text_fast(time_available)
            
            if interests:
                interests = [self._clean_text_fast(interest) for interest in interests[:3]]
            
            if learning_goals:
                learning_goals = [self._clean_text_fast(goal) for goal in learning_goals[:3]]
            
            if user_context:
                user_context = self._clean_dict_fast(user_context)
            
            
            user_profile = self._analyze_user_profile(user_role, skill_level, interests, learning_goals, user_context or {})
            
            
            try:
                available_tasks = await self._get_personalized_tasks(user_id, user_role, skill_level, user_profile)
            except Exception as e:
                logger.warning(f"Task retrieval failed: {e}")
                available_tasks = self._create_smart_fallback_tasks(user_role, skill_level, user_profile)
            
            
            task_recommendations = await self._generate_personalized_recommendations(
                available_tasks, user_profile, time_available
            )
            
            
            learning_tasks = self._suggest_contextual_learning_tasks(user_role, skill_level, user_profile)
            
           
            next_steps = self._generate_actionable_next_steps(task_recommendations, user_profile)
            
            return {
                "success": True,
                "task_suggestions": task_recommendations,
                "learning_opportunities": learning_tasks,
                "next_steps": next_steps,
                "skill_development_path": self._get_personalized_skill_development(user_role, skill_level, user_profile),
                "user_profile": user_profile,
                "metadata": {
                    "user_id": user_id,
                    "user_role": user_role,
                    "skill_level": skill_level,
                    "interests": interests or [],
                    "learning_goals": learning_goals or [],
                    "time_available": time_available,
                    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "agent_type": "task",
                "confidence": 0.85
            }
            
        except Exception as e:
            logger.error(f"Error suggesting tasks: {str(e)}")
            return self._create_error_response(user_id, str(e))

    async def _get_personalized_tasks(self, user_id: str, user_role: str, skill_level: str, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get personalized tasks based on user profile"""
        try:
            logger.debug(f"Getting personalized tasks for {user_role} ({skill_level})")
            
            
            query_parts = [user_role, skill_level, "developer tasks"]
            
           
            if user_profile.get("preferred_tasks"):
                query_parts.extend(user_profile["preferred_tasks"])
            
            query = " ".join(query_parts)
            
            
            context_results = await self.retriever.retrieve(
                query=query,
                collection_types=['tickets', 'pull_requests', 'main'],
                n_results=8  
            )
            
            if context_results and context_results.get('results'):
               
                tasks = []
                for result in context_results['results'][:6]:  
                    task = self._enhance_task_data(result, skill_level, user_profile)
                    if self._is_task_suitable(task, user_profile):
                        tasks.append(task)
                
                logger.debug(f"Retrieved {len(tasks)} suitable tasks from database")
                return tasks
            
            else:
                logger.info("No tasks from retriever, using smart fallback")
                return self._create_smart_fallback_tasks(user_role, skill_level, user_profile)
                
        except Exception as e:
            logger.warning(f"Task retrieval error: {e}")
            return self._create_smart_fallback_tasks(user_role, skill_level, user_profile)

    def _enhance_task_data(self, result: Dict, skill_level: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance task data with better metadata"""
        content = self._clean_text_fast(result.get('content', ''))
        metadata = self._clean_dict_fast(result.get('metadata', {}))
        
        
        task_type = self._classify_task_type(content)
        complexity = self._estimate_task_complexity(content, skill_level)
        skills_required = self._extract_required_skills(content)
        
        return {
            'content': content[:400],
            'metadata': metadata,
            'relevance_score': result.get('relevance_score', 0.5),
            'task_type': task_type,
            'estimated_difficulty': complexity,
            'estimated_time': self._estimate_realistic_time(complexity, skill_level),
            'skills_developed': skills_required,
            'learning_value': self._calculate_learning_value(task_type, skills_required, user_profile),
            'confidence_level': self._calculate_confidence_level(complexity, skill_level)
        }

    def _classify_task_type(self, content: str) -> str:
        """Classify task type based on content analysis"""
        content_lower = content.lower()
        
        type_keywords = {
            'bug_fix': ['bug', 'fix', 'error', 'issue', 'broken', 'debug'],
            'feature': ['feature', 'implement', 'add', 'create', 'build', 'new'],
            'test': ['test', 'testing', 'unit', 'integration', 'spec'],
            'docs': ['document', 'readme', 'guide', 'explanation', 'docs'],
            'refactor': ['refactor', 'improve', 'optimize', 'clean', 'restructure']
        }
        
        for task_type, keywords in type_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return task_type
        
        return 'general'

    def _estimate_task_complexity(self, content: str, skill_level: str) -> str:
        """Estimate task complexity more accurately"""
        content_lower = content.lower()
        
        complexity_indicators = {
            'high': ['architecture', 'system', 'complex', 'advanced', 'performance', 'scale'],
            'medium': ['integrate', 'api', 'database', 'component', 'feature'],
            'low': ['simple', 'basic', 'small', 'quick', 'minor', 'update']
        }
        
        for complexity, indicators in complexity_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                return complexity
        
        
        return 'low' if skill_level == 'beginner' else 'medium'

    def _extract_required_skills(self, content: str) -> List[str]:
        """Extract required skills from task content"""
        content_lower = content.lower()
        skills = []
        
        skill_keywords = {
            'frontend': ['react', 'vue', 'css', 'html', 'javascript', 'ui', 'component'],
            'backend': ['api', 'server', 'database', 'python', 'node', 'express'],
            'testing': ['test', 'unit', 'integration', 'cypress', 'jest'],
            'debugging': ['debug', 'fix', 'error', 'issue', 'troubleshoot'],
            'documentation': ['docs', 'readme', 'guide', 'document'],
            'deployment': ['deploy', 'production', 'server', 'hosting']
        }
        
        for skill, keywords in skill_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                skills.append(skill)
        
        return skills[:3]  

    def _estimate_realistic_time(self, complexity: str, skill_level: str) -> str:
        """Estimate realistic time based on complexity and skill level"""
        time_matrix = {
            'beginner': {'low': '2-3 hours', 'medium': '4-6 hours', 'high': '1-2 days'},
            'intermediate': {'low': '1-2 hours', 'medium': '3-4 hours', 'high': '6-8 hours'},
            'advanced': {'low': '1 hour', 'medium': '2-3 hours', 'high': '4-6 hours'}
        }
        
        return time_matrix.get(skill_level, time_matrix['intermediate']).get(complexity, '2-4 hours')

    def _calculate_learning_value(self, task_type: str, skills: List[str], user_profile: Dict[str, Any]) -> float:
        """Calculate learning value of a task for the user"""
        base_value = 0.5
        
        
        if task_type in user_profile.get('preferred_tasks', []):
            base_value += 0.2
        
        
        user_role = user_profile.get('primary_focus', '')
        role_skills = self.skill_progression.get(user_role, [])
        skill_overlap = len(set(skills) & set([s.lower().replace(' ', '_') for s in role_skills]))
        base_value += skill_overlap * 0.1
        
        
        learning_priority = user_profile.get('learning_priority', 'skill_building')
        if learning_priority == 'practical' and task_type in ['feature', 'bug_fix']:
            base_value += 0.15
        elif learning_priority == 'conceptual' and task_type in ['docs', 'refactor']:
            base_value += 0.15
        
        return min(1.0, base_value)

    def _calculate_confidence_level(self, complexity: str, skill_level: str) -> str:
        """Calculate confidence level for task completion"""
        confidence_matrix = {
            'beginner': {'low': 'high', 'medium': 'medium', 'high': 'low'},
            'intermediate': {'low': 'high', 'medium': 'high', 'high': 'medium'},
            'advanced': {'low': 'high', 'medium': 'high', 'high': 'high'}
        }
        
        return confidence_matrix.get(skill_level, confidence_matrix['intermediate']).get(complexity, 'medium')

    def _is_task_suitable(self, task: Dict[str, Any], user_profile: Dict[str, Any]) -> bool:
        """Check if task is suitable for user"""
        
        challenge_level = user_profile.get('challenge_level', 'appropriate')
        task_difficulty = task.get('estimated_difficulty', 'medium')
        
        if challenge_level == 'gentle' and task_difficulty == 'high':
            return False
        if challenge_level == 'stretch' and task_difficulty == 'low':
            return False
        
        
        if task.get('learning_value', 0) < 0.3:
            return False
        
        return True

    def _create_smart_fallback_tasks(self, user_role: str, skill_level: str, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create smart fallback tasks based on user profile"""
        
        
        preferred_types = user_profile.get('preferred_tasks', ['feature', 'learning', 'docs'])
        if not preferred_types:
            preferred_types = ['learning', 'feature', 'docs']
        
        fallback_tasks = []
        
        
        for task_type in preferred_types[:3]:
            task = self._generate_task_by_type(task_type, user_role, skill_level, user_profile)
            if task:
                fallback_tasks.append(task)
        
        logger.info(f"Created {len(fallback_tasks)} smart fallback tasks for {user_role} ({skill_level})")
        return fallback_tasks

    def _generate_task_by_type(self, task_type: str, user_role: str, skill_level: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a specific task by type"""
        
        task_templates = {
            'learning': {
                'content': f"Explore and practice {user_role} fundamentals through hands-on exercises and small projects",
                'description': f"Build your {user_role} skills with targeted practice exercises"
            },
            'feature': {
                'content': f"Implement a new feature for the ZeroDay {user_role} codebase that demonstrates your growing skills",
                'description': f"Add meaningful functionality to showcase your {user_role} development"
            },
            'docs': {
                'content': f"Improve documentation and create guides for {user_role} development processes",
                'description': f"Help other developers by documenting {user_role} best practices"
            },
            'bug_fix': {
                'content': f"Identify and fix issues in the {user_role} codebase to improve system reliability",
                'description': f"Debug and resolve {user_role}-related issues"
            },
            'test': {
                'content': f"Write comprehensive tests for {user_role} functionality to ensure code quality",
                'description': f"Create test coverage for {user_role} components"
            }
        }
        
        template = task_templates.get(task_type, task_templates['learning'])
        skills = self.skill_progression.get(user_role, self.skill_progression['fullstack'])
        
        return {
            'content': template['content'],
            'description': template['description'],
            'metadata': {'source_type': 'generated', 'task_type': task_type},
            'relevance_score': 0.8,
            'task_type': task_type,
            'estimated_difficulty': skill_level,
            'estimated_time': self._estimate_realistic_time('medium', skill_level),
            'skills_developed': skills[:3],
            'learning_value': 0.7,
            'confidence_level': 'high' if skill_level != 'advanced' else 'medium'
        }

    async def _generate_personalized_recommendations(
        self,
        available_tasks: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        time_available: str
    ) -> List[Dict[str, Any]]:
        """Generate personalized task recommendations"""
        
        if not available_tasks:
            return []
        
        
        sorted_tasks = sorted(
            available_tasks,
            key=lambda x: (x.get('learning_value', 0), x.get('relevance_score', 0)),
            reverse=True
        )
        
        recommendations = []
        
        for i, task in enumerate(sorted_tasks[:3]):
            try:
                recommendation = self._create_enhanced_recommendation(task, i + 1, user_profile, time_available)
                recommendations.append(recommendation)
            except Exception as e:
                logger.warning(f"Error creating recommendation {i}: {e}")
                continue
        
        return recommendations

    def _create_enhanced_recommendation(self, task: Dict[str, Any], priority: int, 
                                      user_profile: Dict[str, Any], time_available: str) -> Dict[str, Any]:
        """Create enhanced task recommendation"""
        
        task_type = task.get('task_type', 'general')
        confidence = task.get('confidence_level', 'medium')
        skills = task.get('skills_developed', [])
        
        
        title = f"Priority {priority}: {task['content'][:50]}..."
        if len(task['content']) <= 50:
            title = f"Priority {priority}: {task['content']}"
        
        
        why_good = self._explain_task_value(task, user_profile)
        
       
        getting_started = self._create_getting_started_guide(task, user_profile)
        
        return {
            "title": title,
            "description": task.get('description', task['content']),
            "task_type": task_type,
            "estimated_difficulty": task.get('estimated_difficulty', 'medium'),
            "estimated_time": task.get('estimated_time', '2-4 hours'),
            "confidence_level": confidence,
            "skills_developed": skills,
            "learning_value": task.get('learning_value', 0.5),
            "why_recommended": why_good,
            "priority": "high" if priority == 1 else "medium",
            "getting_started_steps": getting_started,
            "success_criteria": self._generate_success_criteria(task, user_profile),
            "learning_outcomes": self._generate_learning_outcomes(task, user_profile),
            "metadata": task.get('metadata', {}),
            "relevance_score": task.get('relevance_score', 0.5)
        }

    def _explain_task_value(self, task: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """Explain why this task is valuable for the user"""
        
        skill_level = user_profile.get('skill_level', 'beginner')
        primary_focus = user_profile.get('primary_focus', 'developer')
        task_type = task.get('task_type', 'general')
        confidence = task.get('confidence_level', 'medium')
        
        explanations = []
        
        
        if confidence == 'high':
            explanations.append(f"This task is well-suited for your {skill_level} level")
        elif confidence == 'medium':
            explanations.append(f"This task will challenge you appropriately as a {skill_level}")
        else:
            explanations.append(f"This task will stretch your abilities and accelerate growth")
        
        
        if task_type == 'learning':
            explanations.append("Perfect for building foundational skills")
        elif task_type == 'feature':
            explanations.append("Great for practical development experience")
        elif task_type == 'bug_fix':
            explanations.append("Excellent for debugging and problem-solving skills")
        elif task_type == 'docs':
            explanations.append("Helps you understand the codebase deeply")
        
        
        skills = task.get('skills_developed', [])
        if primary_focus in ' '.join(skills):
            explanations.append(f"Directly relevant to your {primary_focus} role")
        
        return '. '.join(explanations) + '.'

    def _create_getting_started_guide(self, task: Dict[str, Any], user_profile: Dict[str, Any]) -> List[str]:
        """Create getting started guide for the task"""
        
        task_type = task.get('task_type', 'general')
        skill_level = user_profile.get('skill_level', 'beginner')
        
        guides = {
            'learning': [
                "Set up a dedicated practice environment",
                "Review relevant documentation first",
                "Start with simple examples and build up",
                "Ask questions when you get stuck"
            ],
            'feature': [
                "Understand the requirements clearly",
                "Review existing similar features",
                "Break the work into small steps",
                "Write tests as you develop"
            ],
            'bug_fix': [
                "Reproduce the issue consistently",
                "Check logs and error messages",
                "Use debugging tools to investigate",
                "Test your fix thoroughly"
            ],
            'docs': [
                "Read existing documentation first",
                "Understand your audience",
                "Use clear examples and explanations",
                "Get feedback from potential users"
            ]
        }
        
        base_guide = guides.get(task_type, guides['learning'])
        
        
        if skill_level == 'beginner':
            base_guide.insert(0, "Don't hesitate to ask for help early")
        elif skill_level == 'advanced':
            base_guide.append("Consider mentoring others through this work")
        
        return base_guide

    def _generate_success_criteria(self, task: Dict[str, Any], user_profile: Dict[str, Any]) -> List[str]:
        """Generate success criteria for the task"""
        
        task_type = task.get('task_type', 'general')
        
        criteria_templates = {
            'learning': [
                "Can explain the concepts clearly",
                "Successfully completed practice exercises",
                "Applied knowledge in a small project"
            ],
            'feature': [
                "Feature works as specified",
                "Code follows team standards",
                "Includes appropriate tests",
                "Documentation is updated"
            ],
            'bug_fix': [
                "Issue is completely resolved",
                "Fix doesn't break other functionality",
                "Root cause is understood",
                "Prevention measures considered"
            ],
            'docs': [
                "Documentation is clear and accurate",
                "Examples work as described",
                "Peer review feedback addressed",
                "Integrates well with existing docs"
            ]
        }
        
        return criteria_templates.get(task_type, criteria_templates['learning'])

    def _generate_learning_outcomes(self, task: Dict[str, Any], user_profile: Dict[str, Any]) -> List[str]:
        """Generate learning outcomes for the task"""
        
        skills = task.get('skills_developed', [])
        primary_focus = user_profile.get('primary_focus', 'developer')
        
        outcomes = []
        
        for skill in skills[:3]:
            outcomes.append(f"Improved {skill} capabilities")
        
        
        if primary_focus in ['frontend', 'backend', 'fullstack']:
            outcomes.append(f"Enhanced {primary_focus} development skills")
        
        
        outcomes.append("Better problem-solving approach")
        outcomes.append("Increased confidence in similar tasks")
        
        return outcomes[:4]  

    def _suggest_contextual_learning_tasks(self, user_role: str, skill_level: str, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest contextual learning tasks based on user profile"""
        
        progression = self.skill_progression.get(user_role, self.skill_progression["fullstack"])
        learning_priority = user_profile.get('learning_priority', 'skill_building')
        
        
        if skill_level == "beginner":
            target_skills = progression[:3]
        elif skill_level == "intermediate":
            start_idx = len(progression) // 2
            target_skills = progression[start_idx:start_idx + 2]
        else:
            target_skills = progression[-2:]
        
        learning_tasks = []
        for skill in target_skills:
            
            
            if learning_priority == 'practical':
                task_desc = f"Build a small project demonstrating {skill}"
                task_type = "hands-on project"
            elif learning_priority == 'conceptual':
                task_desc = f"Research and understand {skill} principles"
                task_type = "research and study"
            else:
                task_desc = f"Learn and practice {skill} through guided exercises"
                task_type = "guided learning"
            
            task = {
                "title": f"Learn: {skill}",
                "description": task_desc,
                "type": task_type,
                "estimated_time": "3-5 hours",
                "difficulty": skill_level,
                "skills_developed": [skill.lower().replace(' ', '_')],
                "priority": "medium",
                "status": "available",
                "learning_approach": learning_priority
            }
            learning_tasks.append(task)
        
        return learning_tasks

    def _generate_actionable_next_steps(self, suggestions: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> List[str]:
        """Generate actionable next steps based on suggestions and user profile"""
        
        if not suggestions:
            return [
                "Connect with your team lead to discuss available work",
                "Review the project documentation and codebase",
                "Set up your development environment if needed",
                "Join relevant team communication channels"
            ]
        
        first_task = suggestions[0]
        skill_level = user_profile.get('skill_level', 'beginner')
        time_preference = user_profile.get('time_preference', 'medium')
        
        steps = []
        
        
        steps.append(f"Start with: {first_task.get('title', 'the highest priority task')}")
        
        
        if skill_level == 'beginner':
            steps.extend([
                "Read through all requirements carefully before starting",
                "Set up regular check-ins with a mentor or senior developer",
                "Don't hesitate to ask questions early and often"
            ])
        elif skill_level == 'intermediate':
            steps.extend([
                "Review the codebase areas you'll be working in",
                "Plan your approach and break down the work",
                "Consider how this work fits into larger system goals"
            ])
        else:
            steps.extend([
                "Consider the architectural implications of your work",
                "Look for opportunities to mentor others",
                "Plan for knowledge sharing with the team"
            ])
        
       
        if time_preference == 'short':
            steps.append("Focus on quick wins and incremental progress")
        elif time_preference == 'long':
            steps.append("Take time to understand the deeper context and implications")
        
        return steps[:5]  

    def _get_personalized_skill_development(self, user_role: str, skill_level: str, user_profile: Dict[str, Any]) -> List[str]:
        """Get personalized skill development suggestions"""
        
        progression = self.skill_progression.get(user_role, self.skill_progression["fullstack"])
        learning_priority = user_profile.get('learning_priority', 'skill_building')
        
        suggestions = []
        
        if skill_level == "beginner":
            focus_skills = progression[:3]
            suggestions.append(f"Focus on mastering: {', '.join(focus_skills)}")
            suggestions.append("Build small projects daily to reinforce learning")
            suggestions.append("Document your learning journey and progress")
        elif skill_level == "intermediate":
            focus_skills = progression[3:5] if len(progression) > 3 else progression[-2:]
            suggestions.append(f"Develop expertise in: {', '.join(focus_skills)}")
            suggestions.append("Contribute to code reviews and team discussions")
            suggestions.append("Take on tasks that stretch your current abilities")
        else:
            focus_skills = progression[-2:]
            suggestions.append(f"Lead initiatives in: {', '.join(focus_skills)}")
            suggestions.append("Mentor junior developers and share knowledge")
            suggestions.append("Focus on system design and architectural decisions")
        
        
        if learning_priority == 'practical':
            suggestions.append("Prioritize hands-on projects over theoretical study")
        elif learning_priority == 'conceptual':
            suggestions.append("Deep dive into underlying principles and patterns")
        
        return suggestions[:4]  

    def _create_error_response(self, user_id: str, error_msg: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "success": False,
            "error": error_msg,
            "task_suggestions": [],
            "learning_opportunities": [],
            "next_steps": ["Try again later", "Contact team lead for available tasks"],
            "user_id": user_id,
            "agent_type": "task",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_task_categories(self) -> Dict[str, Any]:
        """Get task categories and metadata"""
        return {
            "categories": self.task_categories,
            "difficulty_levels": ["beginner", "intermediate", "advanced"],
            "task_types": ["bug_fix", "feature", "refactor", "test", "docs", "learning"],
            "supported_roles": list(self.skill_progression.keys()),
            "learning_priorities": ["practical", "conceptual", "skill_building"],
            "challenge_levels": ["gentle", "appropriate", "stretch"]
        }



def quick_task_suggestions(user_id: str, user_role: str, skill_level: str = "beginner") -> Dict[str, Any]:
    agent = TaskAgent()
    import asyncio
    return asyncio.run(agent.suggest_tasks(user_id, user_role, skill_level))


if __name__ == "__main__":
    import sys
    import asyncio
    import json
    
    async def main():
        if len(sys.argv) > 1:
            command = sys.argv[1]
            agent = TaskAgent()
            
            if command == "suggest":
                user_id = sys.argv[2] if len(sys.argv) > 2 else "test_user"
                user_role = sys.argv[3] if len(sys.argv) > 3 else "fullstack"
                skill_level = sys.argv[4] if len(sys.argv) > 4 else "beginner"
                
                result = await agent.suggest_tasks(user_id, user_role, skill_level)
                print("Task Suggestions:")
                print(json.dumps(result, indent=2))
                
            elif command == "categories":
                categories = agent.get_task_categories()
                print("Task Categories:")
                print(json.dumps(categories, indent=2))
                
            else:
                print("Available commands:")
                print("  suggest [user_id] [role] [level] - Suggest tasks for user")
                print("  categories - Show available task categories")
        else:
            print("Usage: python task_agent.py [suggest|categories] [args...]")
    
    asyncio.run(main())