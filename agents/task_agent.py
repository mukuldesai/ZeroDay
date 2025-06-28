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

class TaskAgent:
    """
    Task Agent: Recommends appropriate starter tasks and assignments
    Matches developers with suitable work based on skill level, interests, and learning goals
    """
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.retriever = ContextualRetriever(config_path)
        self.llm_client = None
        self._initialize_llm()
        
        
        self.task_categories = self._load_task_categories()
        self.skill_progression = self._load_skill_progression()
        
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
            
            logger.info(f"Task Agent initialized with {self.config['llm']['provider']}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Task Agent LLM: {str(e)}")
            raise
    
    def _load_task_categories(self) -> Dict[str, Dict[str, Any]]:
        """Load task categories with difficulty and skill mappings"""
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
            "setup": {
                "description": "Environment setup and configuration tasks",
                "skills": ["devops", "configuration", "tooling"],
                "difficulty_range": ["beginner", "intermediate"],
                "time_estimate": {"beginner": "1-3 hours", "intermediate": "3-6 hours"}
            }
        }
    
    def _load_skill_progression(self) -> Dict[str, List[str]]:
        """Load skill progression paths for different roles"""
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
            ],
            "mobile": [
                "Mobile UI basics", "Navigation", "State management", "API integration",
                "Device features", "Performance", "App store deployment"
            ]
        }
    
    async def suggest_tasks(
        self,
        user_role: str,
        skill_level: str = "beginner",
        interests: List[str] = None,
        learning_goals: List[str] = None,
        time_available: str = "2-4 hours",
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Suggest appropriate tasks for the user
        
        Args:
            user_role: Target role (frontend, backend, fullstack, devops, mobile)
            skill_level: Current skill level (beginner, intermediate, advanced)
            interests: Areas of interest or preferred technologies
            learning_goals: Specific skills they want to develop
            time_available: Available time commitment
            context: Additional context (current project, team preferences, etc.)
        """
        try:
            logger.info(f"Suggesting tasks for {skill_level} {user_role} developer")
            
            
            available_tasks = await self._get_available_tasks(
                user_role, skill_level, interests, context
            )
            
            
            filtered_tasks = self._filter_tasks_by_criteria(
                available_tasks, skill_level, interests, learning_goals, time_available
            )
            
            
            task_recommendations = await self._generate_task_recommendations(
                filtered_tasks, user_role, skill_level, learning_goals, context
            )
            
            
            learning_tasks = self._suggest_learning_tasks(
                user_role, skill_level, learning_goals
            )
            
           
            final_suggestions = self._prioritize_suggestions(
                task_recommendations, learning_tasks, skill_level, time_available
            )
            
            return {
                "success": True,
                "task_suggestions": final_suggestions,
                "learning_opportunities": learning_tasks,
                "next_steps": self._generate_next_steps(final_suggestions, user_role, skill_level),
                "skill_development_path": self._get_skill_development_suggestions(user_role, skill_level),
                "metadata": {
                    "user_role": user_role,
                    "skill_level": skill_level,
                    "interests": interests or [],
                    "learning_goals": learning_goals or [],
                    "time_available": time_available,
                    "generated_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error suggesting tasks: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "task_suggestions": [],
                "learning_opportunities": [],
                "next_steps": []
            }
    
    async def _get_available_tasks(
        self,
        user_role: str,
        skill_level: str,
        interests: List[str] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Retrieve available tasks from knowledge base"""
        
        
        tasks_results = await self.retriever.retrieve_for_task_agent(
            user_role=user_role,
            skill_level=skill_level,
            interests=interests
        )
        
        logger.debug(f"Found {len(tasks_results.get('results', []))} potential tasks")
        return tasks_results
    
    def _filter_tasks_by_criteria(
        self,
        available_tasks: Dict[str, Any],
        skill_level: str,
        interests: List[str] = None,
        learning_goals: List[str] = None,
        time_available: str = "2-4 hours"
    ) -> List[Dict[str, Any]]:
        """Filter and score tasks based on user criteria"""
        
        filtered_tasks = []
        
        for task_result in available_tasks.get('results', []):
            task_score = self._calculate_task_score(
                task_result, skill_level, interests, learning_goals, time_available
            )
            
            if task_score > 0.3:  
                task_info = {
                    "content": task_result['content'],
                    "metadata": task_result.get('metadata', {}),
                    "relevance_score": task_score,
                    "estimated_difficulty": self._estimate_task_difficulty(task_result),
                    "estimated_time": self._estimate_task_time(task_result, skill_level),
                    "skills_developed": self._identify_skills_developed(task_result)
                }
                filtered_tasks.append(task_info)
        
       
        filtered_tasks.sort(key=lambda x: x['relevance_score'], reverse=True)
        return filtered_tasks[:10]  
    
    def _calculate_task_score(
        self,
        task_result: Dict[str, Any],
        skill_level: str,
        interests: List[str] = None,
        learning_goals: List[str] = None,
        time_available: str = "2-4 hours"
    ) -> float:
        """Calculate relevance score for a task"""
        
        base_score = task_result.get('relevance_score', 0.5)
        metadata = task_result.get('metadata', {})
        content = task_result.get('content', '').lower()
        
       
        task_difficulty = metadata.get('difficulty', 'intermediate')
        if task_difficulty == skill_level:
            skill_match_boost = 1.2
        elif (skill_level == 'beginner' and task_difficulty == 'intermediate') or \
             (skill_level == 'intermediate' and task_difficulty in ['beginner', 'advanced']):
            skill_match_boost = 1.0
        else:
            skill_match_boost = 0.8
        
       
        interest_boost = 1.0
        if interests:
            for interest in interests:
                if interest.lower() in content:
                    interest_boost += 0.1
        
        
        goal_boost = 1.0
        if learning_goals:
            for goal in learning_goals:
                if goal.lower() in content:
                    goal_boost += 0.15
        
        
        time_boost = 1.0
        estimated_time = self._estimate_task_time_hours(content, skill_level)
        available_hours = self._parse_time_available(time_available)
        
        if estimated_time <= available_hours:
            time_boost = 1.1
        elif estimated_time > available_hours * 2:
            time_boost = 0.7
        
        
        freshness_boost = 1.0
        created_at = metadata.get('created_at')
        if created_at:
            try:
                from dateutil.parser import parse
                created_date = parse(created_at)
                days_old = (datetime.now() - created_date).days
                if days_old < 30:
                    freshness_boost = 1.1
            except:
                pass
        
        final_score = base_score * skill_match_boost * interest_boost * goal_boost * time_boost * freshness_boost
        return min(1.0, final_score)
    
    def _estimate_task_difficulty(self, task_result: Dict[str, Any]) -> str:
        """Estimate task difficulty based on content and metadata"""
        metadata = task_result.get('metadata', {})
        content = task_result.get('content', '').lower()
        
      
        if 'difficulty' in metadata:
            return metadata['difficulty']
        
        
        beginner_indicators = ['fix typo', 'update readme', 'add comment', 'simple', 'basic']
        advanced_indicators = ['architecture', 'performance', 'security', 'scalability', 'complex']
        
        if any(indicator in content for indicator in advanced_indicators):
            return 'advanced'
        elif any(indicator in content for indicator in beginner_indicators):
            return 'beginner'
        else:
            return 'intermediate'
    
    def _estimate_task_time(self, task_result: Dict[str, Any], skill_level: str) -> str:
        """Estimate time required for task"""
        content = task_result.get('content', '').lower()
        estimated_hours = self._estimate_task_time_hours(content, skill_level)
        
        if estimated_hours <= 2:
            return "1-2 hours"
        elif estimated_hours <= 4:
            return "2-4 hours"
        elif estimated_hours <= 8:
            return "4-8 hours"
        else:
            return "1+ days"
    
    def _estimate_task_time_hours(self, content: str, skill_level: str) -> float:
        """Estimate task time in hours"""
        base_hours = 2.0  
        
       
        if any(word in content for word in ['fix', 'bug', 'simple']):
            base_hours = 1.5
        elif any(word in content for word in ['implement', 'feature', 'new']):
            base_hours = 4.0
        elif any(word in content for word in ['refactor', 'optimize', 'redesign']):
            base_hours = 6.0
        
       
        skill_multipliers = {
            'beginner': 1.5,
            'intermediate': 1.0,
            'advanced': 0.8
        }
        
        return base_hours * skill_multipliers.get(skill_level, 1.0)
    
    def _parse_time_available(self, time_available: str) -> float:
        """Parse time available string to hours"""
        if "1-2" in time_available:
            return 1.5
        elif "2-4" in time_available:
            return 3.0
        elif "4-8" in time_available:
            return 6.0
        elif "day" in time_available:
            return 8.0
        else:
            return 3.0  
    
    def _identify_skills_developed(self, task_result: Dict[str, Any]) -> List[str]:
        """Identify skills that would be developed by this task"""
        content = task_result.get('content', '').lower()
        metadata = task_result.get('metadata', {})
        
        skills = []
        
   
        skill_keywords = {
            'debugging': ['bug', 'fix', 'error', 'debug'],
            'testing': ['test', 'unit test', 'integration', 'qa'],
            'documentation': ['readme', 'docs', 'documentation', 'guide'],
            'frontend': ['ui', 'react', 'vue', 'css', 'html', 'frontend'],
            'backend': ['api', 'server', 'database', 'backend'],
            'devops': ['deploy', 'ci/cd', 'docker', 'kubernetes'],
            'design': ['design', 'ux', 'ui', 'mockup', 'wireframe']
        }
        
        for skill, keywords in skill_keywords.items():
            if any(keyword in content for keyword in keywords):
                skills.append(skill)
        
      
        if 'skills' in metadata:
            skills.extend(metadata['skills'])
        
        return list(set(skills))  
    
    async def _generate_task_recommendations(
        self,
        filtered_tasks: List[Dict[str, Any]],
        user_role: str,
        skill_level: str,
        learning_goals: List[str] = None,
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Generate enhanced task recommendations using LLM"""
        
        if not filtered_tasks:
            return []
        
   
        prompt_template = self._load_prompt_template("task.txt")
        
      
        tasks_context = self._format_tasks_for_prompt(filtered_tasks[:5])
        
       
        formatted_prompt = prompt_template.format(
            user_role=user_role,
            skill_level=skill_level,
            learning_goals=", ".join(learning_goals) if learning_goals else "General skill development",
            available_tasks=tasks_context,
            user_context=json.dumps(context) if context else "No additional context"
        )
        
        try:
         
            if self.config['llm']['provider'] == 'openai':
                response = self.llm_client.chat.completions.create(
                    model=self.config['llm']['model'],
                    messages=[
                        {"role": "system", "content": "You are an expert task coordinator who matches developers with appropriate work based on their skills and learning goals."},
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
            
          
            enhanced_tasks = self._parse_task_recommendations(llm_response, filtered_tasks)
            return enhanced_tasks
            
        except Exception as e:
            logger.error(f"Error generating task recommendations with LLM: {str(e)}")
       
            return self._create_fallback_recommendations(filtered_tasks)
    
    def _format_tasks_for_prompt(self, tasks: List[Dict[str, Any]]) -> str:
        """Format tasks for LLM prompt"""
        formatted_tasks = []
        
        for i, task in enumerate(tasks):
            metadata = task.get('metadata', {})
            task_info = f"""
            Task {i+1}:
            Description: {task['content'][:200]}...
            Difficulty: {task['estimated_difficulty']}
            Time Estimate: {task['estimated_time']}
            Skills Developed: {', '.join(task['skills_developed'])}
            Source: {metadata.get('source_type', 'unknown')} - {metadata.get('file_path', 'unknown')}
            """
            formatted_tasks.append(task_info)
        
        return "\n".join(formatted_tasks)
    
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
            return self._get_default_task_prompt()
    
    def _get_default_task_prompt(self) -> str:
        """Default task recommendation prompt"""
        return """
        Recommend appropriate tasks for a {skill_level} {user_role} developer.

        Learning Goals: {learning_goals}
        Available Tasks: {available_tasks}
        User Context: {user_context}

        For each recommended task, provide:
        1. Clear task description and objectives
        2. Why this task is suitable for their skill level
        3. What they'll learn from completing it
        4. Step-by-step approach to get started
        5. Success criteria and deliverables
        6. How this connects to their learning goals

        Format as a prioritized list of 3-5 tasks with detailed guidance for each.
        """
    
    def _parse_task_recommendations(self, llm_response: str, original_tasks: List[Dict]) -> List[Dict[str, Any]]:
        """Parse LLM response into structured task recommendations"""
      
        recommendations = []
        
        for i, original_task in enumerate(original_tasks[:3]):
            enhanced_task = original_task.copy()
            enhanced_task.update({
                "recommendation_reason": f"Suitable for {enhanced_task['estimated_difficulty']} level development",
                "learning_outcomes": enhanced_task['skills_developed'],
                "success_criteria": ["Complete the task", "Test the implementation", "Document the solution"],
                "getting_started_steps": [
                    "Review the task requirements",
                    "Set up your development environment", 
                    "Break down the task into smaller steps",
                    "Start with the core functionality"
                ]
            })
            recommendations.append(enhanced_task)
        
        return recommendations
    
    def _create_fallback_recommendations(self, filtered_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create fallback recommendations when LLM fails"""
        recommendations = []
        
        for task in filtered_tasks[:3]:
            enhanced_task = task.copy()
            enhanced_task.update({
                "recommendation_reason": f"Good match for your skill level and interests",
                "learning_outcomes": task['skills_developed'],
                "success_criteria": ["Complete the task successfully", "Follow best practices", "Test your solution"],
                "getting_started_steps": [
                    "Read the task description carefully",
                    "Ask questions if anything is unclear", 
                    "Plan your approach",
                    "Start with small, testable changes"
                ]
            })
            recommendations.append(enhanced_task)
        
        return recommendations
    
    def _suggest_learning_tasks(
        self,
        user_role: str,
        skill_level: str,
        learning_goals: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Suggest practice/learning tasks based on skill progression"""
        
        progression = self.skill_progression.get(user_role, self.skill_progression["fullstack"])
        
  
        current_index = 0
        if skill_level == "intermediate":
            current_index = len(progression) // 2
        elif skill_level == "advanced":
            current_index = len(progression) - 2
        
     
        next_skills = progression[current_index:current_index + 3]
        
        learning_tasks = []
        for skill in next_skills:
            task = {
                "title": f"Practice: {skill}",
                "description": f"Build a small project to practice {skill}",
                "type": "learning_exercise",
                "estimated_time": "2-4 hours",
                "difficulty": skill_level,
                "skills_developed": [skill],
                "learning_outcomes": [f"Understand {skill} fundamentals", f"Apply {skill} in practice"]
            }
            learning_tasks.append(task)
        
        return learning_tasks
    
    def _prioritize_suggestions(
        self,
        task_recommendations: List[Dict[str, Any]],
        learning_tasks: List[Dict[str, Any]],
        skill_level: str,
        time_available: str
    ) -> List[Dict[str, Any]]:
        """Prioritize and combine all task suggestions"""
        
        all_suggestions = []
        
     
        for i, task in enumerate(task_recommendations[:3]):
            task['priority'] = 'high' if i == 0 else 'medium'
            task['type'] = 'real_task'
            all_suggestions.append(task)
        
       
        for task in learning_tasks[:2]:
            task['priority'] = 'medium'
            all_suggestions.append(task)
        
     
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        all_suggestions.sort(
            key=lambda x: (priority_order.get(x.get('priority', 'low'), 1), 
                          x.get('relevance_score', 0.5)), 
            reverse=True
        )
        
        return all_suggestions[:5]  
    
    def _generate_next_steps(
        self,
        suggestions: List[Dict[str, Any]],
        user_role: str,
        skill_level: str
    ) -> List[str]:
        """Generate actionable next steps"""
        
        if not suggestions:
            return [
                "Check with your team lead for available tasks",
                "Review the codebase to understand current projects",
                "Set up your development environment",
                "Join team communication channels"
            ]
        
        next_steps = []
        
     
        if suggestions:
            first_task = suggestions[0]
            next_steps.extend([
                f"Start with: {first_task.get('title', first_task.get('content', 'the first recommended task')[:50])+'...'}",
                "Read the task requirements thoroughly",
                "Ask clarifying questions if needed"
            ])
        
    
        next_steps.extend([
            "Set up a regular check-in schedule with a mentor",
            "Document your progress and learnings",
            "Join code review sessions to learn from others"
        ])
        
        return next_steps[:5]
    
    def _get_skill_development_suggestions(self, user_role: str, skill_level: str) -> List[str]:
        """Get suggestions for skill development"""
        
        progression = self.skill_progression.get(user_role, self.skill_progression["fullstack"])
        
        suggestions = []
        
        if skill_level == "beginner":
            suggestions.extend([
                f"Focus on mastering: {', '.join(progression[:3])}",
                "Practice coding daily, even if just 30 minutes",
                "Build small projects to reinforce learning"
            ])
        elif skill_level == "intermediate":
            suggestions.extend([
                f"Develop expertise in: {', '.join(progression[3:5])}",
                "Contribute to code reviews",
                "Take on more complex tasks gradually"
            ])
        else:  
            suggestions.extend([
                f"Lead initiatives in: {', '.join(progression[-2:])}",
                "Mentor junior developers",
                "Design system architecture"
            ])
        
        return suggestions
    
    async def update_task_progress(
        self,
        task_id: str,
        progress_update: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update progress on a task and suggest next actions"""
        try:
           
            
            status = progress_update.get('status', 'in_progress')
            completion_percentage = progress_update.get('completion_percentage', 0)
            
            response = {
                "success": True,
                "task_id": task_id,
                "updated_status": status,
                "completion_percentage": completion_percentage,
                "timestamp": datetime.now().isoformat()
            }
            
           
            if status == 'completed':
                response["next_suggestions"] = [
                    "Request code review from a team member",
                    "Update documentation if needed",
                    "Ask for feedback on your approach",
                    "Look for a similar but more challenging task"
                ]
            elif status == 'blocked':
                response["next_suggestions"] = [
                    "Clearly document what's blocking you",
                    "Ask for help in the team channel",
                    "Schedule time with a mentor",
                    "Look for alternative approaches"
                ]
            else:  
                response["next_suggestions"] = [
                    "Break remaining work into smaller steps",
                    "Test your current implementation",
                    "Check in with mentor if you have questions",
                    "Document your approach so far"
                ]
            
            return response
            
        except Exception as e:
            logger.error(f"Error updating task progress: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_task_categories(self) -> Dict[str, Any]:
        """Get available task categories and their details"""
        return {
            "categories": self.task_categories,
            "difficulty_levels": self.config['agents']['task']['difficulty_levels'],
            "task_types": self.config['agents']['task']['task_types'],
            "supported_roles": list(self.skill_progression.keys())
        }


def quick_task_suggestions(user_role: str, skill_level: str = "beginner") -> Dict[str, Any]:
    """Quick task suggestions for testing"""
    agent = TaskAgent()
    import asyncio
    return asyncio.run(agent.suggest_tasks(user_role, skill_level))

if __name__ == "__main__":
   
    import sys
    import asyncio
    import json
    
    async def main():
        if len(sys.argv) > 1:
            command = sys.argv[1]
            agent = TaskAgent()
            
            if command == "suggest":
                user_role = sys.argv[2] if len(sys.argv) > 2 else "fullstack"
                skill_level = sys.argv[3] if len(sys.argv) > 3 else "beginner"
                
                result = await agent.suggest_tasks(user_role, skill_level)
                print("Task Suggestions:")
                print(json.dumps(result, indent=2))
                
            elif command == "categories":
                categories = agent.get_task_categories()
                print("Task Categories:")
                print(json.dumps(categories, indent=2))
                
            elif command == "progress":
                task_id = sys.argv[2] if len(sys.argv) > 2 else "test_task_1"
                status = sys.argv[3] if len(sys.argv) > 3 else "in_progress"
                
                progress_update = {"status": status, "completion_percentage": 50}
                result = await agent.update_task_progress(task_id, progress_update)
                print("Progress Update Result:")
                print(json.dumps(result, indent=2))
                
            else:
                print("Available commands:")
                print("  suggest [role] [level] - Suggest tasks for user")
                print("  categories - Show available task categories")
                print("  progress [task_id] [status] - Update task progress")
        else:
            print("Usage: python task_agent.py [suggest|categories|progress] [args...]")
    
    asyncio.run(main())