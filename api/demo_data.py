from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
import json
import os
from pathlib import Path

router = APIRouter(prefix="/demo", tags=["demo"])

def get_demo_dir():
    """Get the demo directory path"""
    current_dir = Path(__file__).parent
    demo_dir = current_dir.parent / "demo" / "scenarios"
    return demo_dir

def load_scenario(scenario_id: str) -> Dict[str, Any]:
    """Load scenario data, with fallback to hardcoded data if file not found"""
    demo_dir = get_demo_dir()
    scenario_path = demo_dir / f"{scenario_id}_scenario.json"
    
    
    if scenario_path.exists():
        try:
            with open(scenario_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading scenario file: {e}")
    
    
    scenarios = {
        "startup": {
            "scenario_name": "Tech Startup",
            "company_type": "startup",
            "team_size": 8,
            "industry": "SaaS",
            "user_profile": {
                "name": "Alex Developer",
                "role": "Full Stack Developer",
                "experience": "2 years"
            },
            "projects": [
                {
                    "name": "User Authentication System",
                    "status": "in_progress",
                    "priority": "high",
                    "deadline": "2025-08-15",
                    "technologies": ["React", "Node.js", "JWT"]
                },
                {
                    "name": "Dashboard Analytics",
                    "status": "todo",
                    "priority": "medium",
                    "deadline": "2025-09-01",
                    "technologies": ["React", "Chart.js", "API"]
                }
            ],
            "learning_goals": [
                "Master React hooks",
                "Learn Node.js best practices",
                "Understand JWT authentication"
            ],
            "recent_activities": [
                "Completed onboarding process",
                "Set up development environment",
                "Started working on authentication"
            ],
            "tech_stack": ["React", "Node.js", "MongoDB", "Express"]
        },
        "enterprise": {
            "scenario_name": "Enterprise Corporation",
            "company_type": "enterprise",
            "team_size": 50,
            "industry": "Finance",
            "user_profile": {
                "name": "Jordan Senior",
                "role": "Senior Software Engineer",
                "experience": "5 years"
            },
            "projects": [
                {
                    "name": "Legacy System Migration",
                    "status": "in_progress",
                    "priority": "critical",
                    "deadline": "2025-12-31",
                    "technologies": ["Java", "Spring", "PostgreSQL"]
                },
                {
                    "name": "API Modernization",
                    "status": "completed",
                    "priority": "high",
                    "deadline": "2025-07-30",
                    "technologies": ["REST API", "OpenAPI", "Docker"]
                }
            ],
            "learning_goals": [
                "Microservices architecture",
                "Cloud deployment strategies",
                "Enterprise security patterns"
            ],
            "recent_activities": [
                "Led architecture review",
                "Mentored junior developers",
                "Completed security training"
            ],
            "tech_stack": ["Java", "Spring Boot", "PostgreSQL", "Docker", "Kubernetes"]
        },
        "freelancer": {
            "scenario_name": "Freelance Project",
            "company_type": "freelancer",
            "team_size": 1,
            "industry": "Various",
            "user_profile": {
                "name": "Sam Freelancer",
                "role": "Freelance Developer",
                "experience": "3 years"
            },
            "projects": [
                {
                    "name": "E-commerce Website",
                    "status": "in_progress",
                    "priority": "high",
                    "deadline": "2025-08-20",
                    "technologies": ["Next.js", "Stripe", "Tailwind"]
                },
                {
                    "name": "Blog Platform",
                    "status": "completed",
                    "priority": "medium",
                    "deadline": "2025-07-15",
                    "technologies": ["Gatsby", "Contentful", "Netlify"]
                }
            ],
            "learning_goals": [
                "E-commerce best practices",
                "Payment integration",
                "SEO optimization"
            ],
            "recent_activities": [
                "Client consultation completed",
                "Project scope defined",
                "Started development phase"
            ],
            "tech_stack": ["Next.js", "React", "Tailwind CSS", "Stripe", "Vercel"]
        }
    }
    
    if scenario_id not in scenarios:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    return scenarios[scenario_id]

@router.get("/scenarios")
async def get_demo_scenarios():
    """Get all available demo scenarios"""
    scenarios = []
    scenario_files = ['startup', 'enterprise', 'freelancer']
    
    for scenario_id in scenario_files:
        try:
            scenario_data = load_scenario(scenario_id)
            scenarios.append({
                "id": scenario_id,
                "name": scenario_data["scenario_name"],
                "company_type": scenario_data["company_type"],
                "team_size": scenario_data["team_size"],
                "industry": scenario_data["industry"],
                "user_profile": scenario_data["user_profile"]
            })
        except Exception as e:
            print(f"Error loading scenario {scenario_id}: {e}")
            continue
    
    return scenarios

@router.get("/scenarios/{scenario_id}")
async def get_demo_scenario(scenario_id: str):
    """Get specific demo scenario details"""
    return load_scenario(scenario_id)

@router.get("/chat/messages/{scenario_id}")
async def get_demo_chat_messages(scenario_id: str):
    """Get demo chat messages for a scenario"""
    scenario_data = load_scenario(scenario_id)
    
    demo_messages = [
        {
            "id": 1,
            "content": f"Hi! I'm the AI assistant for {scenario_data['scenario_name']}. How can I help you today?",
            "sender": "ai",
            "timestamp": "2025-07-10T09:00:00Z",
            "agent": "knowledge"
        },
        {
            "id": 2,
            "content": "Can you help me understand our current project priorities?",
            "sender": "user",
            "timestamp": "2025-07-10T09:01:00Z"
        },
        {
            "id": 3,
            "content": f"Based on your role as {scenario_data['user_profile']['role']}, here are your current high-priority projects:",
            "sender": "ai",
            "timestamp": "2025-07-10T09:01:30Z",
            "agent": "guide"
        }
    ]
    
    for project in scenario_data.get("projects", [])[:2]:
        demo_messages.append({
            "id": len(demo_messages) + 1,
            "content": f"• {project['name']} (Status: {project['status']}, Priority: {project['priority']})",
            "sender": "ai",
            "timestamp": "2025-07-10T09:02:00Z",
            "agent": "task"
        })
    
    return demo_messages

@router.get("/tasks/{scenario_id}")
async def get_demo_tasks(scenario_id: str):
    """Get demo tasks for a scenario"""
    scenario_data = load_scenario(scenario_id)
    
    tasks = []
    for i, project in enumerate(scenario_data.get("projects", [])):
        
        tasks.extend([
            {
                "id": f"task_{i+1}_1",
                "title": f"Set up {project['name']} environment",
                "description": f"Initialize development environment for {project['name']}",
                "status": "completed" if project["status"] == "completed" else "todo",
                "priority": project["priority"],
                "difficulty": "easy",
                "deadline": project.get("deadline", "2025-08-30"),
                "assignee": scenario_data["user_profile"]["name"],
                "tags": project.get("technologies", []),
                "estimatedTime": "2 hours",
                "progress": 100 if project["status"] == "completed" else 0
            },
            {
                "id": f"task_{i+1}_2", 
                "title": f"Implement core features for {project['name']}",
                "description": f"Develop main functionality using {', '.join(project.get('technologies', []))}",
                "status": project["status"],
                "priority": project["priority"],
                "difficulty": "medium",
                "deadline": project.get("deadline", "2025-08-30"),
                "assignee": scenario_data["user_profile"]["name"],
                "tags": project.get("technologies", []),
                "estimatedTime": "1 day",
                "progress": 75 if project["status"] == "in_progress" else (100 if project["status"] == "completed" else 0)
            }
        ])
    
    return tasks

@router.get("/analytics/{scenario_id}")
async def get_demo_analytics(scenario_id: str):
    """Get demo analytics data for a scenario"""
    scenario_data = load_scenario(scenario_id)
    
    return {
        "projects_completed": len([p for p in scenario_data.get("projects", []) if p["status"] == "completed"]),
        "projects_in_progress": len([p for p in scenario_data.get("projects", []) if p["status"] == "in_progress"]),
        "team_size": scenario_data["team_size"],
        "learning_goals_count": len(scenario_data.get("learning_goals", [])),
        "recent_activities": scenario_data.get("recent_activities", []),
        "tech_stack": scenario_data.get("tech_stack", []),
        "company_type": scenario_data["company_type"],
        "user_profile": scenario_data["user_profile"]
    }

@router.get("/learning-paths/{scenario_id}")
async def get_demo_learning_paths(scenario_id: str):
    """Get demo learning paths for a scenario"""
    scenario_data = load_scenario(scenario_id)
    
    learning_paths = []
    for i, goal in enumerate(scenario_data.get("learning_goals", [])):
        learning_paths.append({
            "id": f"path_{i+1}",
            "title": goal,
            "description": f"Complete learning path for {goal}",
            "progress": 30 + (i * 20),  
            "totalModules": 8,
            "completedModules": 2 + i,
            "estimatedTime": f"{4 + i} weeks",
            "difficulty": ["easy", "medium", "hard"][i % 3],
            "category": scenario_data["company_type"]
        })
    
    return learning_paths