import os
import yaml
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime
import json
import openai
from anthropic import Anthropic
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from vector_store.retriever import ContextualRetriever

class GuideAgent:
    """
    Guide Agent: Creates personalized learning paths based on role, experience, and goals
    Generates structured roadmaps with resources, milestones, and progress tracking
    """
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.retriever = ContextualRetriever(config_path)
        self.llm_client = None
        self._initialize_llm()
        self.learning_paths = self._load_learning_paths()
        
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
            
            logger.info(f"Guide Agent initialized with {self.config['llm']['provider']}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Guide Agent LLM: {str(e)}")
            raise
    
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
    
    async def generate_learning_path(
        self,
        user_role: str,
        experience_level: str = "beginner",
        learning_goals: List[str] = None,
        time_commitment: str = "part_time",
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate a personalized learning path for the user
        
        Args:
            user_role: Target role (frontend, backend, fullstack, devops, mobile)
            experience_level: beginner, intermediate, advanced
            learning_goals: Specific goals or technologies to focus on
            time_commitment: full_time, part_time, weekend
            context: Additional context about user's background
        """
        try:
            logger.info(f"Generating learning path for {user_role} ({experience_level})")
            
            learning_resources = await self._get_learning_resources(
                user_role, experience_level, learning_goals
            )
            
            learning_path = await self._create_structured_path(
                user_role, experience_level, learning_goals, time_commitment, learning_resources, context
            )
            
            learning_path = self._add_progress_tracking(learning_path)
            recommendations = await self._generate_recommendations(learning_path, context)
            
            return {
                "success": True,
                "learning_path": learning_path,
                "recommendations": recommendations,
                "metadata": {
                    "user_role": user_role,
                    "experience_level": experience_level,
                    "learning_goals": learning_goals or [],
                    "time_commitment": time_commitment,
                    "generated_at": datetime.now().isoformat(),
                    "estimated_duration": learning_path.get("estimated_duration_weeks", 8)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating learning path: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "learning_path": None,
                "recommendations": []
            }
    
    async def _get_learning_resources(
        self,
        user_role: str,
        experience_level: str,
        learning_goals: List[str] = None
    ) -> Dict[str, Any]:
        """Retrieve relevant learning resources from knowledge base"""
        

        query_parts = [user_role, experience_level]
        if learning_goals:
            query_parts.extend(learning_goals)
        
        query = " ".join(query_parts)
        

        resources = await self.retriever.retrieve_for_guide_agent(
            user_role=user_role,
            learning_goal=query,
            experience_level=experience_level
        )
        
        logger.debug(f"Found {len(resources.get('results', []))} learning resources")
        return resources
    
    async def _create_structured_path(
        self,
        user_role: str,
        experience_level: str,
        learning_goals: List[str],
        time_commitment: str,
        learning_resources: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a structured learning path using LLM"""
        
        prompt_template = self._load_prompt_template("guide.txt")
        
        base_path = self.learning_paths.get(user_role, self.learning_paths["fullstack"])
        resources_text = self._format_resources_for_prompt(learning_resources.get('results', []))
        
        formatted_prompt = prompt_template.format(
            user_role=user_role,
            experience_level=experience_level,
            learning_goals=", ".join(learning_goals) if learning_goals else "General proficiency",
            time_commitment=time_commitment,
            base_path=json.dumps(base_path, indent=2),
            available_resources=resources_text,
            user_context=json.dumps(context) if context else "No additional context"
        )
        
        try:
            if self.config['llm']['provider'] == 'openai':
                response = self.llm_client.chat.completions.create(
                    model=self.config['llm']['model'],
                    messages=[
                        {"role": "system", "content": "You are an expert learning path designer who creates structured, actionable learning plans for developers."},
                        {"role": "user", "content": formatted_prompt}
                    ],
                    temperature=self.config['llm']['temperature'],
                    max_tokens=self.config['llm']['max_tokens']
                )
                llm_response = response.choices[0].message.content
                
            elif self.config['llm']['provider'] == 'anthropic':
                response = self.llm_client.messages.create(
                    model=self.config['llm']['model'],
                    max_tokens=self.config['llm']['max_tokens'],
                    temperature=self.config['llm']['temperature'],
                    messages=[
                        {"role": "user", "content": formatted_prompt}
                    ]
                )
                llm_response = response.content[0].text
            

            structured_path = self._parse_llm_response(llm_response, base_path)
            return structured_path
            
        except Exception as e:
            logger.error(f"Error generating structured path with LLM: {str(e)}")
            return self._create_template_path(user_role, experience_level, learning_goals)
    
    def _format_resources_for_prompt(self, resources: List[Dict]) -> str:
        """Format retrieved resources for LLM prompt"""
        if not resources:
            return "No specific resources found in knowledge base."
        
        formatted_resources = []
        for i, resource in enumerate(resources[:5]): 
            metadata = resource.get('metadata', {})
            source_info = f"{metadata.get('source_type', 'unknown')} - {metadata.get('file_path', 'unknown')}"
            
            formatted_resources.append(f"{i+1}. {source_info}\n   Content: {resource['content'][:200]}...")
        
        return "\n".join(formatted_resources)
    
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
            return self._get_default_guide_prompt()
    
    def _get_default_guide_prompt(self) -> str:
        """Default prompt template for guide generation"""
        return """
        Create a comprehensive learning path for a {experience_level} {user_role} developer.

        User Goals: {learning_goals}
        Time Commitment: {time_commitment}
        
        Base Path Template:
        {base_path}
        
        Available Resources in Knowledge Base:
        {available_resources}
        
        User Context: {user_context}
        
        Please create a detailed learning path with the following structure:
        
        1. **Overview**: Brief description and learning objectives
        2. **Prerequisites**: What the user should know before starting
        3. **Phases**: Break learning into 3-5 phases, each with:
           - Phase name and duration
           - Learning objectives
           - Key topics to cover
           - Practical projects/exercises
           - Resources and materials
           - Success criteria/milestones
        4. **Timeline**: Realistic timeline based on time commitment
        5. **Projects**: 2-3 hands-on projects to build
        6. **Assessment**: How to measure progress and success
        
        Format the response as a well-structured learning plan that is actionable and motivating.
        Include specific technologies, tools, and methodologies relevant to the role.
        """
    
    def _parse_llm_response(self, llm_response: str, base_path: Dict) -> Dict[str, Any]:
        """Parse LLM response into structured learning path format"""
        try:
            learning_path = {
                "title": f"{base_path.get('description', 'Custom Learning Path')}",
                "overview": self._extract_section(llm_response, "overview"),
                "prerequisites": self._extract_section(llm_response, "prerequisites"),
                "phases": self._extract_phases(llm_response),
                "timeline": self._extract_section(llm_response, "timeline"),
                "projects": self._extract_projects(llm_response),
                "assessment": self._extract_section(llm_response, "assessment"),
                "estimated_duration_weeks": base_path.get("duration_weeks", 8),
                "difficulty": base_path.get("difficulty", "intermediate"),
                "full_response": llm_response  
            }
            
            return learning_path
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return self._create_template_path_from_response(llm_response, base_path)
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific section from LLM response"""
        import re
        
        pattern = rf"(?i)(?:^|\n)\*?\*?{section_name}[:\s]*\*?\*?(.+?)(?=\n\*?\*?[A-Z]|\n\d+\.|\Z)"
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        return f"Please refer to the full learning plan for {section_name} details."
    
    def _extract_phases(self, text: str) -> List[Dict[str, Any]]:
        """Extract learning phases from LLM response"""
        phases = []
        
        import re
        phase_pattern = r"(?i)(?:phase|week|module|step)\s*(\d+)[:\s]*(.+?)(?=(?:phase|week|module|step)\s*\d+|\n\*?\*?[A-Z]|\Z)"
        matches = re.finditer(phase_pattern, text, re.DOTALL)
        
        for i, match in enumerate(matches):
            phase_number = match.group(1)
            phase_content = match.group(2).strip()
            
            phases.append({
                "phase_number": int(phase_number),
                "title": f"Phase {phase_number}",
                "content": phase_content,
                "duration_weeks": 2,  
                "objectives": [],
                "topics": [],
                "projects": [],
                "milestones": []
            })
        

        if not phases:
            phases = [
                {"phase_number": 1, "title": "Foundation", "duration_weeks": 2},
                {"phase_number": 2, "title": "Core Skills", "duration_weeks": 3},
                {"phase_number": 3, "title": "Advanced Topics", "duration_weeks": 2},
                {"phase_number": 4, "title": "Project & Practice", "duration_weeks": 1}
            ]
        
        return phases
    
    def _extract_projects(self, text: str) -> List[Dict[str, Any]]:
        """Extract project suggestions from LLM response"""
        projects = []
        
      
        import re
        project_pattern = r"(?i)project[s]?[:\s]*(.+?)(?=\n\*?\*?[A-Z]|\Z)"
        match = re.search(project_pattern, text, re.DOTALL)
        
        if match:
            project_text = match.group(1).strip()
      
            project_lines = [line.strip() for line in project_text.split('\n') if line.strip()]
            
            for i, line in enumerate(project_lines[:3]): 
                projects.append({
                    "title": f"Project {i+1}",
                    "description": line,
                    "difficulty": "intermediate",
                    "estimated_hours": 20
                })
        
       
        if not projects:
            projects = [
                {"title": "Starter Project", "description": "Build a simple application using core technologies", "difficulty": "beginner", "estimated_hours": 15},
                {"title": "Intermediate Project", "description": "Create a more complex application with multiple features", "difficulty": "intermediate", "estimated_hours": 30}
            ]
        
        return projects
    
    def _create_template_path(self, user_role: str, experience_level: str, learning_goals: List[str]) -> Dict[str, Any]:
        """Create a template-based learning path as fallback"""
        base_path = self.learning_paths.get(user_role, self.learning_paths["fullstack"])
        
        return {
            "title": f"{user_role.title()} Developer Learning Path",
            "overview": f"A comprehensive {experience_level} to intermediate learning path for {user_role} development.",
            "prerequisites": "Basic programming knowledge and familiarity with web technologies.",
            "phases": self._create_template_phases(base_path["core_skills"]),
            "timeline": f"{base_path['duration_weeks']} weeks with consistent practice",
            "projects": self._create_template_projects(user_role),
            "assessment": "Regular code reviews, project completions, and skill assessments",
            "estimated_duration_weeks": base_path["duration_weeks"],
            "difficulty": base_path["difficulty"]
        }
    
    def _create_template_phases(self, core_skills: List[str]) -> List[Dict[str, Any]]:
        """Create template phases from core skills"""
        phases = []
        skills_per_phase = max(1, len(core_skills) // 3)
        
        for i in range(0, len(core_skills), skills_per_phase):
            phase_skills = core_skills[i:i + skills_per_phase]
            phases.append({
                "phase_number": len(phases) + 1,
                "title": f"Phase {len(phases) + 1}: {' & '.join(phase_skills)}",
                "duration_weeks": 2,
                "topics": phase_skills,
                "objectives": [f"Master {skill}" for skill in phase_skills],
                "projects": [],
                "milestones": [f"Complete {skill} exercises" for skill in phase_skills]
            })
        
        return phases
    
    def _create_template_projects(self, user_role: str) -> List[Dict[str, Any]]:
        """Create template projects based on role"""
        project_templates = {
            "frontend": [
                {"title": "Personal Portfolio", "description": "Build a responsive portfolio website", "difficulty": "beginner"},
                {"title": "Todo Application", "description": "Create a full-featured todo app with React", "difficulty": "intermediate"}
            ],
            "backend": [
                {"title": "REST API", "description": "Build a RESTful API with authentication", "difficulty": "beginner"},
                {"title": "E-commerce Backend", "description": "Create a complete e-commerce backend system", "difficulty": "intermediate"}
            ],
            "fullstack": [
                {"title": "Blog Platform", "description": "Full-stack blog with user authentication", "difficulty": "intermediate"},
                {"title": "Social Media App", "description": "Build a social media platform", "difficulty": "advanced"}
            ]
        }
        
        return project_templates.get(user_role, project_templates["fullstack"])
    
    def _create_template_path_from_response(self, llm_response: str, base_path: Dict) -> Dict[str, Any]:
        """Create structured path from raw LLM response"""
        return {
            "title": f"{base_path.get('description', 'Custom Learning Path')}",
            "overview": llm_response[:300] + "...",
            "prerequisites": "Basic programming knowledge",
            "phases": self._create_template_phases(base_path.get("core_skills", ["Foundation", "Core", "Advanced"])),
            "timeline": f"{base_path.get('duration_weeks', 8)} weeks",
            "projects": self._create_template_projects("fullstack"),
            "assessment": "Project-based evaluation",
            "estimated_duration_weeks": base_path.get("duration_weeks", 8),
            "difficulty": base_path.get("difficulty", "intermediate"),
            "full_response": llm_response
        }
    
    def _add_progress_tracking(self, learning_path: Dict[str, Any]) -> Dict[str, Any]:
        """Add progress tracking structure to learning path"""
        learning_path["progress_tracking"] = {
            "milestones": [],
            "completion_criteria": [],
            "assessment_methods": []
        }
        
        for phase in learning_path.get("phases", []):
            phase_milestones = phase.get("milestones", [])
            if not phase_milestones:
                phase_milestones = [f"Complete Phase {phase.get('phase_number', 1)}"]
            
            learning_path["progress_tracking"]["milestones"].extend(phase_milestones)
        
      
        for project in learning_path.get("projects", []):
            learning_path["progress_tracking"]["milestones"].append(
                f"Complete {project.get('title', 'Project')}"
            )
        
       
        learning_path["progress_tracking"]["completion_criteria"] = [
            "Complete all phases",
            "Finish at least 1 project",
            "Pass skill assessments",
            "Demonstrate practical knowledge"
        ]
        
        learning_path["progress_tracking"]["assessment_methods"] = [
            "Code reviews",
            "Project demonstrations",
            "Peer feedback",
            "Self-assessment quizzes"
        ]
        
        return learning_path
    
    async def _generate_recommendations(self, learning_path: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations based on learning path and context"""
        recommendations = []
        
      
        estimated_weeks = learning_path.get("estimated_duration_weeks", 8)
        if estimated_weeks > 10:
            recommendations.append("Consider breaking this into smaller, focused learning sprints")
        
        if learning_path.get("difficulty") == "beginner":
            recommendations.append("Start with hands-on tutorials before diving into theory")
            recommendations.append("Join beginner-friendly developer communities")
        
        projects = learning_path.get("projects", [])
        if len(projects) < 2:
            recommendations.append("Consider adding more practical projects to reinforce learning")
        
        if context:
            if context.get("time_commitment") == "part_time":
                recommendations.append("Set aside consistent daily practice time, even if just 30 minutes")
            
            if context.get("team"):
                recommendations.append("Ask team members for mentorship and code reviews")
        

        recommendations.extend([
            "Document your learning journey and progress",
            "Build a portfolio of your projects",
            "Practice coding daily, even in small increments",
            "Join developer communities and forums",
            "Seek feedback early and often"
        ])
        
        return recommendations[:5]  
    
    async def update_learning_path(
        self,
        learning_path_id: str,
        progress_update: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update learning path based on user progress"""
        try:
            
            return {
                "success": True,
                "updated_path": "Learning path updated based on progress",
                "next_recommendations": [
                    "Continue with next phase",
                    "Review completed materials",
                    "Start working on projects"
                ],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error updating learning path: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_available_paths(self) -> Dict[str, Any]:
        """Get all available learning path templates"""
        return {
            "learning_paths": self.learning_paths,
            "supported_roles": list(self.learning_paths.keys()),
            "experience_levels": ["beginner", "intermediate", "advanced"],
            "time_commitments": ["full_time", "part_time", "weekend"]
        }


def quick_learning_path(user_role: str, experience_level: str = "beginner") -> Dict[str, Any]:
    """Quick learning path generation"""
    guide = GuideAgent()
    import asyncio
    return asyncio.run(guide.generate_learning_path(user_role, experience_level))

if __name__ == "__main__":
   
    import sys
    import asyncio
    import json
    
    async def main():
        if len(sys.argv) > 1:
            command = sys.argv[1]
            guide = GuideAgent()
            
            if command == "generate":
                user_role = sys.argv[2] if len(sys.argv) > 2 else "fullstack"
                experience_level = sys.argv[3] if len(sys.argv) > 3 else "beginner"
                
                result = await guide.generate_learning_path(user_role, experience_level)
                print("Generated Learning Path:")
                print(json.dumps(result, indent=2))
                
            elif command == "paths":
                paths = guide.get_available_paths()
                print("Available Learning Paths:")
                print(json.dumps(paths, indent=2))
                
            else:
                print("Available commands:")
                print("  generate [role] [level] - Generate learning path")
                print("  paths - Show available path templates")
        else:
            print("Usage: python guide_agent.py [generate|paths] [args...]")
    
    asyncio.run(main())