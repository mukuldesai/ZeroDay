import os
import sys
import yaml
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime
import json
import openai
from anthropic import Anthropic
import re
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from vector_store.retriever import ContextualRetriever
from dotenv import load_dotenv
load_dotenv()

class GuideAgent:
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.retriever = ContextualRetriever(config_path)
        self.llm_client = None
        self.llm_initialized = False
        self._initialize_llm()
        self.learning_paths = self._load_learning_paths()
        
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
                logger.info(f"Guide Agent - Primary LLM: OpenAI initialized")
                
            elif primary_provider == 'anthropic' and anthropic_key:
                self.llm_client = Anthropic(api_key=anthropic_key)
                self.llm_provider = 'anthropic'
                logger.info(f"Guide Agent - Primary LLM: Anthropic initialized")
            
            
            if fallback_provider == 'openai' and openai_key and self.llm_provider != 'openai':
                self.fallback_client = openai.OpenAI(api_key=openai_key)
                self.fallback_provider = 'openai'
                logger.info(f"Guide Agent - Fallback LLM: OpenAI ready")
                
            elif fallback_provider == 'anthropic' and anthropic_key and self.llm_provider != 'anthropic':
                self.fallback_client = Anthropic(api_key=anthropic_key)
                self.fallback_provider = 'anthropic'
                logger.info(f"Guide Agent - Fallback LLM: Anthropic ready")
            
            if self.llm_client:
                self.llm_initialized = True
                logger.info(f"Guide Agent initialized - Primary: {self.llm_provider}, Fallback: {self.fallback_provider or 'None'}")
            else:
                raise ValueError("No valid API keys found")
                
        except Exception as e:
            logger.error(f"Guide Agent LLM initialization failed: {e}")
            self.llm_initialized = False
            raise

    def _call_llm_with_fallback(self, messages, **kwargs):
        """Call LLM with automatic fallback"""
        
       
        if self.llm_client and self.llm_provider:
            try:
                return self._make_llm_call(self.llm_client, self.llm_provider, messages, **kwargs)
            except Exception as e:
                logger.warning(f"Guide Agent - Primary LLM ({self.llm_provider}) failed: {e}")
                
                
                if self.fallback_client and self.fallback_provider:
                    logger.info(f"Guide Agent - Switching to fallback LLM: {self.fallback_provider}")
                    try:
                        return self._make_llm_call(self.fallback_client, self.fallback_provider, messages, **kwargs)
                    except Exception as fallback_error:
                        logger.error(f"Guide Agent - Fallback LLM ({self.fallback_provider}) also failed: {fallback_error}")
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
    
    def _load_learning_paths(self) -> Dict[str, Any]:
        """Load predefined learning path templates"""
        return {
            "frontend": {
                "description": "Frontend development with modern frameworks",
                "core_skills": ["HTML/CSS", "JavaScript", "React/Vue", "State Management", "Testing"],
                "duration_weeks": 8,
                "difficulty": "beginner_to_intermediate"
            },
            "backend": {
                "description": "Backend development and API design",
                "core_skills": ["Python/Node.js", "Databases", "APIs", "Authentication", "Testing", "Deployment"],
                "duration_weeks": 10,
                "difficulty": "beginner_to_intermediate"
            },
            "fullstack": {
                "description": "Full-stack development combining frontend and backend",
                "core_skills": ["Frontend Basics", "Backend APIs", "Database Design", "Authentication", "Deployment"],
                "duration_weeks": 12,
                "difficulty": "intermediate"
            },
            "devops": {
                "description": "DevOps and infrastructure management",
                "core_skills": ["Docker", "CI/CD", "Cloud Platforms", "Monitoring", "Security"],
                "duration_weeks": 8,
                "difficulty": "intermediate_to_advanced"
            },
            "mobile": {
                "description": "Mobile app development",
                "core_skills": ["React Native/Flutter", "Mobile UI/UX", "App Store", "Device APIs"],
                "duration_weeks": 10,
                "difficulty": "intermediate"
            }
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

    def _extract_learning_context(self, learning_goals: list = None, user_context: dict = None) -> Dict[str, Any]:
        """Enhanced context extraction from multiple sources"""
        context = {
            "specific_technology": None,
            "timeframe": None,
            "urgency": "normal",
            "intensity": "normal",
            "specific_goal": None
        }
        
       
        if user_context:
            context["specific_technology"] = user_context.get("specific_technology")
            context["timeframe"] = user_context.get("urgent_timeframe") or user_context.get("specific_timeframe")
            if user_context.get("timeframe_priority") == "high":
                context["urgency"] = "high"
                context["intensity"] = "intensive"
        
       
        if learning_goals:
            goals_text = " ".join(learning_goals).lower()
            context["specific_goal"] = learning_goals[0] if learning_goals else None
            
           
            if not context["specific_technology"]:
                tech_patterns = {
                    "react": r'\b(react|jsx|hooks)\b',
                    "vue": r'\b(vue|vuejs)\b',
                    "python": r'\b(python|django|flask)\b',
                    "javascript": r'\b(javascript|js|node)\b',
                    "typescript": r'\b(typescript|ts)\b'
                }
                
                for tech, pattern in tech_patterns.items():
                    if re.search(pattern, goals_text):
                        context["specific_technology"] = tech
                        break
            
           
            if not context["timeframe"]:
                time_patterns = [
                    r'\b(1|one)\s*week\b',
                    r'\b(\d+)\s*weeks?\b',
                    r'\b(\d+)\s*days?\b',
                    r'\b(\d+)\s*months?\b'
                ]
                
                for pattern in time_patterns:
                    match = re.search(pattern, goals_text)
                    if match:
                        context["timeframe"] = match.group(0)
                        if "1 week" in match.group(0) or "one week" in match.group(0):
                            context["urgency"] = "high"
                            context["intensity"] = "intensive"
                        elif any(word in match.group(0) for word in ["1", "2", "3"]) and "week" in match.group(0):
                            context["urgency"] = "medium"
                            context["intensity"] = "accelerated"
                        break
            
            
            urgency_keywords = ["urgent", "quickly", "asap", "fast", "crash", "intensive", "bootcamp"]
            if any(keyword in goals_text for keyword in urgency_keywords):
                context["urgency"] = "high"
                context["intensity"] = "intensive"
        
        return context

    async def generate_learning_path(self, user_id: str, user_role: str, experience_level: str = "beginner", 
                                learning_goals: list = None, time_commitment: str = "part_time", 
                                user_context: dict = None):
        """Generate a personalized learning path with enhanced context awareness"""
        try:
            logger.info(f"Generating learning path for user {user_id}: {user_role} ({experience_level})")
            
           
            learning_context = self._extract_learning_context(learning_goals, user_context)
            specific_technology = learning_context["specific_technology"]
            timeframe = learning_context["timeframe"]
            urgency = learning_context["urgency"]
            intensity = learning_context["intensity"]
            
            logger.info(f"Detected context - Tech: {specific_technology}, Timeframe: {timeframe}, Urgency: {urgency}")
            
          
            if specific_technology == "react" and urgency == "high":
                return await self._create_react_intensive_path(user_id, timeframe, experience_level, learning_context)
            
           
            if specific_technology:
                return await self._create_technology_specific_path(
                    user_id, user_role, specific_technology, experience_level, learning_context
                )
            
           
            if urgency == "high" or intensity == "intensive":
                return await self._create_accelerated_path(
                    user_id, user_role, experience_level, timeframe, learning_context
                )
            
            
            return await self._create_standard_path(user_id, user_role, experience_level, time_commitment, learning_context)
            
        except Exception as e:
            logger.error(f"Error generating learning path: {e}")
            return {
                "success": False,
                "learning_path": {},
                "error": "Failed to generate learning path"
            }

    async def _create_react_intensive_path(self, user_id: str, timeframe: str, experience_level: str, context: Dict[str, Any]):
        """Create intensive React learning path for urgent needs"""
        
        duration = timeframe or "1 week"
        daily_hours = "6-8 hours" if "1 week" in duration else "4-5 hours"
        
        return {
            "success": True,
            "learning_path": {
                "title": f"React Intensive - {duration.title()}",
                "overview": f"An accelerated, hands-on React bootcamp designed to get you productive in {duration}. This is intensive but highly effective - you'll build real projects and learn by doing.",
                "duration": f"{duration} ({35 if '1 week' in duration else 50} total hours)",
                "urgency_level": "high_intensity",
                "daily_commitment": daily_hours,
                "approach": "Project-based learning with minimal theory",
                "phases": [
                    {
                        "name": "Days 1-2: React Foundation",
                        "duration": "2 days",
                        "daily_hours": daily_hours.split('-')[0],
                        "focus": "Get React running and understand core concepts",
                        "topics": [
                            "Environment setup (Create React App)",
                            "JSX syntax and components",
                            "Props and basic state",
                            "Event handling basics"
                        ],
                        "hands_on": "Build a personal portfolio page with multiple components",
                        "milestone": "Working React app deployed to Netlify/Vercel",
                        "success_check": [
                            "App runs without errors",
                            "Has at least 4 components",
                            "Shows understanding of props"
                        ]
                    },
                    {
                        "name": "Days 3-4: State and Effects",
                        "duration": "2 days", 
                        "daily_hours": daily_hours.split('-')[0],
                        "focus": "Master React hooks and side effects",
                        "topics": [
                            "useState for interactive components",
                            "useEffect for data fetching",
                            "Conditional rendering",
                            "Lists and forms"
                        ],
                        "hands_on": "Build an interactive todo app with local storage",
                        "milestone": "Full CRUD functionality working",
                        "success_check": [
                            "Add, edit, delete todos",
                            "Data persists on reload",
                            "Clean, responsive interface"
                        ]
                    },
                    {
                        "name": "Days 5-7: Real-World React",
                        "duration": "3 days",
                        "daily_hours": "5-6 hours",
                        "focus": "Build production-ready features",
                        "topics": [
                            "API integration with fetch",
                            "React Router for navigation", 
                            "Custom hooks",
                            "Error handling and loading states"
                        ],
                        "hands_on": "Weather dashboard with multiple pages and API data",
                        "milestone": "Multi-page app with external data",
                        "success_check": [
                            "Multiple routes working",
                            "Successful API calls",
                            "Proper error handling",
                            "Loading states implemented"
                        ]
                    }
                ],
                "daily_schedule": {
                    "morning": "2-3 hours: Core concepts and tutorials",
                    "afternoon": "3-4 hours: Hands-on project building",
                    "evening": "30 minutes: Review and plan next day"
                },
                "survival_tips": [
                    "Focus on building, not perfection",
                    "Use React DevTools from day 1",
                    "Don't get stuck on styling - use CSS frameworks",
                    "Google errors immediately - don't struggle alone",
                    "Join React Discord for quick help"
                ],
                "resources": [
                    "React official tutorial (skip theory, do hands-on)",
                    "Scrimba React course (interactive)",
                    "React DevTools browser extension",
                    "Vite for faster development (alternative to CRA)"
                ]
            },
            "confidence": 0.95,
            "recommendations": [
                f"Clear your calendar - {duration} of focused learning",
                "Set up development environment before you start",
                "Have backup plans for when you get stuck",
                "Document your progress daily",
                "Build something new each day, don't just follow tutorials"
            ],
            "next_steps": [
                "Set up React development environment",
                "Join React community Discord/Slack",
                "Plan your first portfolio project",
                "Schedule daily check-ins with a mentor if possible"
            ]
        }

    async def _create_technology_specific_path(self, user_id: str, user_role: str, technology: str, 
                                             experience_level: str, context: Dict[str, Any]):
        """Create technology-specific learning paths"""
        
        intensity = context.get("intensity", "normal")
        timeframe = context.get("timeframe", "8-12 weeks")
        
        tech_paths = {
            "python": {
                "title": f"Python Development Path{' - Intensive' if intensity == 'intensive' else ''}",
                "overview": f"Master Python for {user_role} development with practical projects and real-world applications.",
                "core_phases": [
                    "Python Fundamentals & Syntax",
                    "Web Development with Flask/Django",
                    "Database Integration & APIs",
                    "Testing & Deployment"
                ]
            },
            "javascript": {
                "title": f"JavaScript Mastery Path{' - Accelerated' if intensity == 'intensive' else ''}",
                "overview": f"Complete JavaScript learning from basics to advanced concepts for {user_role} roles.",
                "core_phases": [
                    "Modern JavaScript (ES6+)",
                    "DOM Manipulation & Events", 
                    "Async Programming & APIs",
                    "Node.js & Backend Development"
                ]
            },
            "vue": {
                "title": f"Vue.js Development Track{' - Fast Track' if intensity == 'intensive' else ''}",
                "overview": f"Learn Vue.js ecosystem for modern frontend development in {user_role} positions.",
                "core_phases": [
                    "Vue.js Fundamentals",
                    "Component Architecture",
                    "State Management (Vuex/Pinia)",
                    "Production Deployment"
                ]
            }
        }
        
        tech_config = tech_paths.get(technology, tech_paths["javascript"])
        duration_multiplier = 0.6 if intensity == "intensive" else 1.0
        estimated_weeks = int(8 * duration_multiplier)
        
        return {
            "success": True,
            "learning_path": {
                "title": tech_config["title"],
                "overview": tech_config["overview"],
                "duration": f"{estimated_weeks} weeks" if not timeframe else timeframe,
                "technology_focus": technology,
                "intensity_level": intensity,
                "phases": self._generate_tech_phases(technology, tech_config["core_phases"], intensity),
                "projects": self._generate_tech_projects(technology, experience_level),
                "resources": self._get_tech_resources(technology),
                "assessment": f"Project-based evaluation with {technology} best practices"
            },
            "confidence": 0.9,
            "recommendations": self._get_tech_recommendations(technology, intensity)
        }

    async def _create_accelerated_path(self, user_id: str, user_role: str, experience_level: str, 
                                     timeframe: str, context: Dict[str, Any]):
        """Create accelerated learning path for urgent needs"""
        
        base_path = self.learning_paths.get(user_role, self.learning_paths["fullstack"])
        duration_weeks = 6  
        
        
        return {
            "success": True,
            "learning_path": {
                "title": f"Accelerated {user_role.title()} Bootcamp",
                "overview": f"Intensive {duration_weeks}-week program to quickly develop {user_role} skills. Perfect for career transitions or urgent skill building.",
                "duration": f"{duration_weeks} weeks intensive",
                "daily_commitment": "4-6 hours per day",
                "approach": "Project-heavy with minimal theory",
                "phases": [
                    {
                        "name": "Week 1-2: Core Foundation",
                        "focus": "Essential skills only",
                        "intensity": "High",
                        "topics": base_path["core_skills"][:3],
                        "project": "Basic functional application"
                    },
                    {
                        "name": "Week 3-4: Integration Skills", 
                        "focus": "Connecting technologies",
                        "intensity": "High",
                        "topics": base_path["core_skills"][3:],
                        "project": "Integrated application with database"
                    },
                    {
                        "name": "Week 5-6: Production Ready",
                        "focus": "Deployment and best practices",
                        "intensity": "Medium",
                        "topics": ["Testing", "Deployment", "Code Quality"],
                        "project": "Portfolio-worthy application"
                    }
                ],
                "survival_strategy": [
                    "Focus on building, skip excessive theory",
                    "Use templates and boilerplates to move fast",
                    "Get help immediately when stuck",
                    "Build something every single day"
                ]
            },
            "confidence": 0.85
        }

    async def _create_standard_path(self, user_id: str, user_role: str, experience_level: str, 
                                  time_commitment: str, context: Dict[str, Any]):
        """Create standard learning path with good customization"""
        
        base_path = self.learning_paths.get(user_role, self.learning_paths["fullstack"])
        
        
        timeline_multiplier = {
            "full_time": 0.7,
            "part_time": 1.0,
            "weekend": 1.4
        }
        
        adjusted_weeks = int(base_path["duration_weeks"] * timeline_multiplier.get(time_commitment, 1.0))
        
        return {
            "success": True,
            "learning_path": {
                "title": f"{user_role.title()} Developer Learning Journey",
                "overview": f"A comprehensive {experience_level} to advanced learning path for {user_role} development. Balanced approach with theory and hands-on practice.",
                "duration": f"{adjusted_weeks} weeks",
                "time_commitment": time_commitment,
                "phases": self._create_phases_enhanced(base_path["core_skills"], experience_level, adjusted_weeks),
                "projects": self._create_projects_enhanced(user_role, experience_level),
                "assessment": "Project portfolio with peer review",
                "prerequisites": self._get_prerequisites_enhanced(user_role, experience_level),
                "career_outcomes": f"Ready for {user_role} positions at junior to mid-level"
            },
            "confidence": 0.9
        }

    def _generate_tech_phases(self, technology: str, core_phases: List[str], intensity: str) -> List[Dict]:
        """Generate technology-specific phases"""
        phases = []
        weeks_per_phase = 2 if intensity == "intensive" else 3
        
        for i, phase_name in enumerate(core_phases):
            phases.append({
                "phase_number": i + 1,
                "title": f"Phase {i + 1}: {phase_name}",
                "duration_weeks": weeks_per_phase,
                "intensity": intensity,
                "focus": f"Master {phase_name.lower()} with practical applications",
                "projects": [f"Build project demonstrating {phase_name.lower()}"],
                "milestones": [f"Complete {phase_name.lower()} fundamentals"]
            })
        
        return phases

    def _generate_tech_projects(self, technology: str, experience_level: str) -> List[Dict]:
        """Generate technology-specific projects"""
        project_templates = {
            "react": [
                {"title": "Interactive Todo App", "skills": ["Components", "State", "Events"]},
                {"title": "Weather Dashboard", "skills": ["API Integration", "Routing", "Hooks"]},
                {"title": "E-commerce Frontend", "skills": ["Complex State", "Context", "Performance"]}
            ],
            "python": [
                {"title": "Web Scraper", "skills": ["APIs", "Data Processing", "File Handling"]},
                {"title": "Flask/Django App", "skills": ["Web Framework", "Database", "Authentication"]},
                {"title": "Data Analysis Tool", "skills": ["Data Science Libraries", "Visualization"]}
            ],
            "javascript": [
                {"title": "DOM Manipulation Game", "skills": ["DOM", "Events", "Local Storage"]},
                {"title": "Node.js API Server", "skills": ["Backend", "Express", "Database"]},
                {"title": "Full-Stack Application", "skills": ["Frontend + Backend", "Deployment"]}
            ]
        }
        
        return project_templates.get(technology, project_templates["javascript"])

    def _get_tech_resources(self, technology: str) -> List[str]:
        """Get technology-specific resources"""
        resources = {
            "react": [
                "React Official Documentation",
                "React DevTools",
                "Create React App",
                "React Router Official Guide"
            ],
            "python": [
                "Python.org Official Tutorial",
                "Flask/Django Documentation", 
                "Python Package Index (PyPI)",
                "Python testing frameworks"
            ],
            "javascript": [
                "MDN Web Docs",
                "Node.js Documentation",
                "Express.js Guide",
                "JavaScript testing frameworks"
            ]
        }
        
        return resources.get(technology, resources["javascript"])

    def _get_tech_recommendations(self, technology: str, intensity: str) -> List[str]:
        """Get technology-specific recommendations"""
        base_recommendations = [
            f"Focus on {technology} fundamentals first",
            "Build projects to reinforce learning",
            "Join the {technology} community"
        ]
        
        if intensity == "intensive":
            base_recommendations.extend([
                "Dedicate full-time hours to learning",
                "Have backup resources ready when stuck",
                "Document your daily progress"
            ])
        
        return base_recommendations

    def _create_phases_enhanced(self, core_skills: List[str], experience_level: str, total_weeks: int) -> List[Dict[str, Any]]:
        """Create enhanced phases with better structure"""
        phases = []
        skills_per_phase = 2 if experience_level == "beginner" else 3
        weeks_per_phase = max(2, total_weeks // len(core_skills))
        
        for i in range(0, len(core_skills), skills_per_phase):
            phase_skills = core_skills[i:i + skills_per_phase]
            phase_number = len(phases) + 1
            
            phases.append({
                "phase_number": phase_number,
                "title": f"Phase {phase_number}: {' & '.join(phase_skills)}",
                "duration_weeks": weeks_per_phase,
                "objectives": [f"Understand and apply {skill}" for skill in phase_skills],
                "topics": phase_skills,
                "practical_focus": f"Build working examples using {', '.join(phase_skills)}",
                "deliverables": [f"Completed project demonstrating {skill}" for skill in phase_skills[:1]],
                "success_criteria": [f"Can explain and implement {skill}" for skill in phase_skills]
            })
        
        return phases

    def _create_projects_enhanced(self, user_role: str, experience_level: str) -> List[Dict[str, Any]]:
        """Create enhanced project suggestions"""
        project_templates = {
            "frontend": {
                "beginner": [
                    {
                        "title": "Responsive Portfolio Website",
                        "description": "Build your professional portfolio with modern design",
                        "skills": ["HTML/CSS", "JavaScript", "Responsive Design"],
                        "estimated_hours": 20,
                        "portfolio_ready": True
                    },
                    {
                        "title": "Interactive Web Application",
                        "description": "Create a dynamic app with user interactions",
                        "skills": ["Framework", "State Management", "API Integration"],
                        "estimated_hours": 35,
                        "portfolio_ready": True
                    }
                ],
                "intermediate": [
                    {
                        "title": "E-commerce Frontend",
                        "description": "Complete shopping interface with modern UX",
                        "skills": ["Complex State", "Payment Integration", "Performance"],
                        "estimated_hours": 50,
                        "portfolio_ready": True
                    }
                ]
            },
            "backend": {
                "beginner": [
                    {
                        "title": "RESTful API Service",
                        "description": "Build a complete API with authentication",
                        "skills": ["API Design", "Database", "Authentication"],
                        "estimated_hours": 30,
                        "portfolio_ready": True
                    }
                ],
                "intermediate": [
                    {
                        "title": "Microservice Architecture",
                        "description": "Design distributed system with multiple services",
                        "skills": ["Microservices", "Docker", "Message Queues"],
                        "estimated_hours": 60,
                        "portfolio_ready": True
                    }
                ]
            }
        }
        
        role_projects = project_templates.get(user_role, project_templates["frontend"])
        level_projects = role_projects.get(experience_level, role_projects.get("beginner", []))
        
        return level_projects

    def _get_prerequisites_enhanced(self, user_role: str, experience_level: str) -> str:
        """Get enhanced prerequisites"""
        prerequisites = {
            "frontend": {
                "beginner": "Comfortable with basic computer usage. Some exposure to HTML recommended but not required.",
                "intermediate": "Solid HTML/CSS foundation. Basic JavaScript knowledge. Familiarity with developer tools.",
                "advanced": "Strong JavaScript skills. Experience with at least one modern framework. Understanding of build tools."
            },
            "backend": {
                "beginner": "Basic programming concepts in any language. Understanding of how websites work.",
                "intermediate": "Programming experience in Python, JavaScript, or similar. Basic database concepts.",
                "advanced": "Strong programming foundation. Experience with web frameworks and databases."
            }
        }
        
        role_prereqs = prerequisites.get(user_role, prerequisites["frontend"])
        return role_prereqs.get(experience_level, "Basic computer skills and willingness to learn.")

    async def update_learning_path(self, user_id: str, learning_path_id: str, progress_update: Dict[str, Any]) -> Dict[str, Any]:
        """Update learning path based on user progress"""
        try:
            completed_phases = progress_update.get("completed_phases", [])
            current_phase = progress_update.get("current_phase", 1)
            struggles = progress_update.get("struggles", [])
            
            recommendations = []
            
            if completed_phases:
                recommendations.append(f"Great progress completing {len(completed_phases)} phases!")
                recommendations.append("You're building solid momentum - keep it up")
            
            if struggles:
                recommendations.extend([
                    "Focus extra time on challenging areas",
                    "Consider additional resources for difficult topics",
                    "Connect with mentors or study groups for support"
                ])
            else:
                recommendations.append("You're progressing well - maintain your current approach")
            
            recommendations.extend([
                "Update your portfolio with new projects",
                "Share your learning wins with the community",
                "Plan your next learning milestone"
            ])
            
            return {
                "success": True,
                "updated_path": "Learning path updated based on your progress",
                "next_recommendations": recommendations[:5],
                "progress_summary": {
                    "completed_phases": len(completed_phases),
                    "current_phase": current_phase,
                    "areas_of_struggle": struggles,
                    "overall_progress": f"{(len(completed_phases) / max(current_phase, 1)) * 100:.0f}%"
                },
                "confidence": 0.8,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Error updating learning path: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "Failed to update learning path. Please try again with progress details.",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def get_available_paths(self) -> Dict[str, Any]:
        """Get available learning path templates"""
        return {
            "learning_paths": self.learning_paths,
            "supported_roles": list(self.learning_paths.keys()),
            "experience_levels": ["beginner", "intermediate", "advanced"],
            "time_commitments": ["full_time", "part_time", "weekend"],
            "supported_technologies": ["react", "vue", "python", "javascript", "typescript"],
            "intensity_levels": ["normal", "accelerated", "intensive"]
        }



def quick_learning_path(user_id: str, user_role: str, experience_level: str = "beginner") -> Dict[str, Any]:
    guide = GuideAgent()
    import asyncio
    return asyncio.run(guide.generate_learning_path(user_id, user_role, experience_level))


if __name__ == "__main__":
    import sys
    import asyncio
    import json
    
    async def main():
        if len(sys.argv) > 1:
            command = sys.argv[1]
            guide = GuideAgent()
            
            if command == "generate":
                user_id = sys.argv[2] if len(sys.argv) > 2 else "demo_user"
                user_role = sys.argv[3] if len(sys.argv) > 3 else "fullstack"
                experience_level = sys.argv[4] if len(sys.argv) > 4 else "beginner"
                
                result = await guide.generate_learning_path(user_id, user_role, experience_level)
                print("Generated Learning Path:")
                print(json.dumps(result, indent=2))
                
            elif command == "paths":
                paths = guide.get_available_paths()
                print("Available Learning Paths:")
                print(json.dumps(paths, indent=2))
                
            else:
                print("Available commands:")
                print("  generate [user_id] [role] [level] - Generate learning path")
                print("  paths - Show available path templates")
        else:
            print("Usage: python guide_agent.py [generate|paths] [args...]")
    
    asyncio.run(main())