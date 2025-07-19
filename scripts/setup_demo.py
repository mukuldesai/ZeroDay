#!/usr/bin/env python3

import os
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv
load_dotenv()

sys.path.append(str(Path(__file__).parent.parent))

from database.setup import DatabaseSetup
from database.seed_demo_data import seed_demo_users
from vector_store.chromadb_setup import ChromaDBSetup
from vector_store.demo_vectorstore import DemoVectorStore
from auth.simple_auth import AuthManager
from demo.scenarios.generate_scenarios import generate_all_scenarios

def setup_environment():
    env_file = Path('.env')
    if not env_file.exists():
        logger.error("Environment file .env not found")
        return False
    
    required_vars = [
        'OPENAI_API_KEY',
        'DATABASE_URL',
        'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing environment variables: {missing_vars}")
        return False
    
    logger.info("Environment configuration validated")
    return True

def setup_database():
    logger.info("Setting up database...")
    
    db_setup = DatabaseSetup()
    
    if not db_setup.initialize_database():
        logger.error("Failed to initialize database")
        return False
    
    if not db_setup.create_tables():
        logger.error("Failed to create database tables")
        return False
    
    logger.info("Database setup completed")
    return True

def create_demo_users():
    logger.info("Creating demo users...")
    
    demo_users = [
        {
            "email": "demo@example.com",
            "password": "demo123",
            "role": "owner",
            "org_name": "Demo Organization"
        },
        {
            "email": "developer@demo.com", 
            "password": "dev123",
            "role": "member",
            "org_name": "Demo Organization"
        },
        {
            "email": "admin@demo.com",
            "password": "admin123", 
            "role": "admin",
            "org_name": "Demo Organization"
        }
    ]
    
    auth_manager = AuthManager()
    
    for user_data in demo_users:
        result = auth_manager.create_user(
            email=user_data["email"],
            password=user_data["password"],
            role=user_data["role"],
            org_name=user_data["org_name"]
        )
        
        if result.get("success"):
            logger.info(f"Created demo user: {user_data['email']}")
        else:
            logger.warning(f"Failed to create user {user_data['email']}: {result.get('error')}")
    
    return True

def setup_vector_store():
    logger.info("Setting up vector store...")
    
    demo_vector_store = DemoVectorStore()
    
    init_result = demo_vector_store.initialize_demo_collections()
    if not init_result.get("success"):
        logger.error(f"Failed to initialize demo collections: {init_result.get('error')}")
        return False
    
    logger.info("Vector store setup completed")
    return True

def generate_demo_scenarios():
    logger.info("Generating demo scenarios...")
    
    scenarios_dir = Path("demo/scenarios")
    scenarios_dir.mkdir(parents=True, exist_ok=True)
    
    startup_scenario = {
        "company": {
            "name": "TechStart Inc",
            "industry": "Software Development",
            "size": "15-30 employees",
            "description": "Fast-growing startup building SaaS solutions",
            "mission": "Democratize access to enterprise software tools",
            "tech_stack": ["React", "Node.js", "Python", "PostgreSQL", "AWS"],
            "current_projects": ["Customer Dashboard", "Mobile App", "API Gateway"]
        },
        "codebase": {
            "repositories": [
                {
                    "name": "customer-dashboard",
                    "description": "React-based customer portal",
                    "technologies": ["React", "TypeScript", "Tailwind"],
                    "primary_language": "typescript",
                    "features": ["User Authentication", "Data Visualization", "Real-time Updates"],
                    "sample_files": [
                        {
                            "path": "src/components/Dashboard.tsx",
                            "language": "typescript",
                            "content": "import React from 'react';\n\nconst Dashboard: React.FC = () => {\n  return (\n    <div className=\"dashboard\">\n      <h1>Customer Dashboard</h1>\n    </div>\n  );\n};\n\nexport default Dashboard;"
                        }
                    ]
                }
            ]
        },
        "documentation": {
            "guides": [
                {
                    "title": "Getting Started",
                    "overview": "Quick setup guide for new developers",
                    "category": "setup",
                    "difficulty": "beginner",
                    "prerequisites": ["Node.js 16+", "Git", "VS Code"],
                    "steps": [
                        "Clone the repository",
                        "Install dependencies with npm install",
                        "Set up environment variables",
                        "Start development server"
                    ],
                    "common_issues": [
                        {
                            "problem": "Port already in use",
                            "solution": "Kill process using port 3000 or use different port"
                        }
                    ],
                    "next_steps": ["Read API documentation", "Set up debugging"]
                }
            ]
        },
        "slack_data": {
            "channels": [
                {
                    "name": "general",
                    "conversations": [
                        {
                            "date": "2024-01-15",
                            "messages": [
                                {"user": "john_dev", "message": "Good morning team! Ready for sprint planning today?"},
                                {"user": "sarah_pm", "message": "Yes! We have some exciting features to discuss"},
                                {"user": "mike_design", "message": "Looking forward to reviewing the new mockups"}
                            ],
                            "participants": ["john_dev", "sarah_pm", "mike_design"]
                        }
                    ]
                }
            ]
        },
        "pull_requests": {
            "examples": [
                {
                    "number": 42,
                    "title": "Add user authentication to dashboard",
                    "description": "Implements JWT-based authentication for the customer dashboard",
                    "author": "john_dev",
                    "status": "open",
                    "repository": "customer-dashboard",
                    "changes": ["Added login component", "Implemented JWT validation", "Added protected routes"],
                    "testing": ["Unit tests for auth functions", "E2E tests for login flow"],
                    "review_notes": "Please review security implementation",
                    "files_changed": ["src/auth/Login.tsx", "src/utils/auth.ts", "tests/auth.test.ts"]
                }
            ]
        },
        "tickets": {
            "examples": [
                {
                    "id": "START-001",
                    "type": "bug",
                    "title": "Login form validation not working",
                    "description": "Email validation allows invalid email formats",
                    "priority": "high",
                    "status": "open",
                    "assignee": "john_dev",
                    "steps": ["Navigate to login page", "Enter invalid email", "Click submit"],
                    "expected": "Should show validation error",
                    "actual": "Form submits with invalid email",
                    "notes": "Affects user experience on signup flow",
                    "labels": ["bug", "frontend", "validation"]
                }
            ]
        }
    }
    
    enterprise_scenario = {
        "company": {
            "name": "GlobalTech Solutions",
            "industry": "Enterprise Software",
            "size": "500+ employees",
            "description": "Leading provider of enterprise cloud solutions",
            "mission": "Transform business operations through intelligent automation",
            "tech_stack": ["Java", "Spring", "React", "Kubernetes", "AWS", "Microservices"],
            "current_projects": ["Cloud Migration", "AI Analytics Platform", "Security Enhancement"]
        },
        "codebase": {
            "repositories": [
                {
                    "name": "user-service",
                    "description": "Microservice for user management",
                    "technologies": ["Java", "Spring Boot", "PostgreSQL"],
                    "primary_language": "java",
                    "features": ["User CRUD operations", "Authentication", "Role management"],
                    "sample_files": [
                        {
                            "path": "src/main/java/com/globaltech/UserController.java",
                            "language": "java",
                            "content": "@RestController\n@RequestMapping(\"/api/users\")\npublic class UserController {\n    \n    @Autowired\n    private UserService userService;\n    \n    @GetMapping(\"/{id}\")\n    public ResponseEntity<User> getUser(@PathVariable Long id) {\n        return ResponseEntity.ok(userService.findById(id));\n    }\n}"
                        }
                    ]
                }
            ]
        }
    }
    
    freelancer_scenario = {
        "company": {
            "name": "DevCraft Solutions",
            "industry": "Software Consulting",
            "size": "1-5 employees",
            "description": "Independent software development consultancy",
            "mission": "Deliver high-quality custom software solutions",
            "tech_stack": ["Full-stack JavaScript", "Python", "React", "Node.js"],
            "current_projects": ["E-commerce Platform", "CRM System", "Mobile App"]
        }
    }
    
    scenarios = {
        "startup_scenario.json": startup_scenario,
        "enterprise_scenario.json": enterprise_scenario,
        "freelancer_scenario.json": freelancer_scenario
    }
    
    for filename, scenario_data in scenarios.items():
        scenario_file = scenarios_dir / filename
        with open(scenario_file, 'w', encoding='utf-8') as f:
            json.dump(scenario_data, f, indent=2)
        logger.info(f"Generated scenario: {filename}")
    
    return True

def populate_demo_data():
    logger.info("Populating demo data...")
    
    demo_vector_store = DemoVectorStore()
    
    result = demo_vector_store.populate_all_scenarios()
    
    if result.get("success"):
        logger.info(f"Demo data populated: {result.get('total_documents')} documents, {result.get('total_chunks')} chunks")
        return True
    else:
        logger.error(f"Failed to populate demo data: {result.get('error')}")
        return False

def verify_setup():
    logger.info("Verifying demo setup...")
    
    checks = {
        "database": False,
        "vector_store": False,
        "demo_data": False
    }
    
    try:
        db_setup = DatabaseSetup()
        checks["database"] = db_setup.check_connection()
    except Exception as e:
        logger.error(f"Database check failed: {e}")
    
    try:
        vector_store = ChromaDBSetup(user_id="demo_user", org_id="demo_org")
        health = vector_store.health_check()
        checks["vector_store"] = health.get("status") == "healthy"
    except Exception as e:
        logger.error(f"Vector store check failed: {e}")
    
    try:
        demo_vector_store = DemoVectorStore()
        stats = demo_vector_store.get_demo_stats()
        checks["demo_data"] = stats.get("total_documents", 0) > 0
    except Exception as e:
        logger.error(f"Demo data check failed: {e}")
    
    all_checks_passed = all(checks.values())
    
    if all_checks_passed:
        logger.success("All verification checks passed!")
    else:
        logger.warning(f"Some checks failed: {checks}")
    
    return all_checks_passed

def print_setup_summary():
    logger.info("Demo setup completed successfully!")
    print("\n" + "="*60)
    print("ZeroDay Demo Setup Complete!")
    print("="*60)
    print("\nDemo Users Created:")
    print("  • demo@example.com (Owner) - Password: demo123")
    print("  • developer@demo.com (Member) - Password: dev123") 
    print("  • admin@demo.com (Admin) - Password: admin123")
    print("\nDemo Scenarios Available:")
    print("  • Startup - Fast-growing tech startup")
    print("  • Enterprise - Large corporation environment")
    print("  • Freelancer - Independent consultant setup")
    print("\nNext Steps:")
    print("  1. Start the backend: python api/main.py")
    print("  2. Start the frontend: cd frontend && npm run dev")
    print("  3. Access the application: http://localhost:3000")
    print("  4. Login with demo credentials")
    print("\n" + "="*60)

def main():
    logger.info("Starting ZeroDay demo setup...")
    
    setup_steps = [
        ("Environment", setup_environment),
        ("Database", setup_database),
        ("Demo Users", create_demo_users),
        ("Vector Store", setup_vector_store),
        ("Demo Scenarios", generate_demo_scenarios),
        ("Demo Data", populate_demo_data),
        ("Verification", verify_setup)
    ]
    
    for step_name, step_function in setup_steps:
        logger.info(f"Executing step: {step_name}")
        
        try:
            if not step_function():
                logger.error(f"Step failed: {step_name}")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Step {step_name} failed with exception: {e}")
            sys.exit(1)
        
        logger.success(f"Step completed: {step_name}")
    
    print_setup_summary()

if __name__ == "__main__":
    main()