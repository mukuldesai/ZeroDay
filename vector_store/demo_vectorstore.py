import os
import yaml
import json
from typing import Dict, List, Any, Optional
from loguru import logger
from datetime import datetime, timedelta
from vector_store.chromadb_setup import ChromaDBSetup
from vector_store.index_builder import IndexBuilder
import random
from dotenv import load_dotenv
load_dotenv()

class DemoVectorStore:
    """
    Demo Vector Store: Pre-built collections with synthetic data
    Handles demo scenarios and sample data generation
    """
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.demo_db_setup = ChromaDBSetup(config_path, user_id="demo_user", org_id="demo_org")
        self.demo_indexer = IndexBuilder(config_path, user_id="demo_user", org_id="demo_org")
        self.scenarios_path = os.path.join(os.path.dirname(__file__), "..", "demo", "scenarios")
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from settings.yaml"""
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "demo_settings.yaml"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def initialize_demo_collections(self) -> Dict[str, Any]:
        """Initialize demo collections with pre-built data"""
        try:
            self.demo_db_setup.initialize_client()
            collections = self.demo_db_setup.setup_collections()
            
            result = {
                "success": True,
                "collections_created": list(collections.keys()),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info(f"Initialized {len(collections)} demo collections")
            return result
            
        except Exception as e:
            logger.error(f"Error initializing demo collections: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def load_scenario_data(self, scenario_type: str = "startup") -> Dict[str, Any]:
        """Load and index data for a specific demo scenario"""
        try:
            scenario_file = os.path.join(self.scenarios_path, f"{scenario_type}_scenario.json")
            
            if not os.path.exists(scenario_file):
                return {
                    "success": False,
                    "error": f"Scenario file not found: {scenario_type}"
                }
            
            with open(scenario_file, 'r', encoding='utf-8') as f:
                scenario_data = json.load(f)
            
            documents = self._generate_scenario_documents(scenario_data)
            
            total_indexed = 0
            results_by_collection = {}
            
            for collection_type, docs in documents.items():
                if docs:
                    result = self.demo_indexer.add_documents(docs, collection_type)
                    results_by_collection[collection_type] = result
                    if result.get("success"):
                        total_indexed += result.get("chunks_created", 0)
            
            return {
                "success": True,
                "scenario_type": scenario_type,
                "total_documents": sum(len(docs) for docs in documents.values()),
                "total_chunks": total_indexed,
                "collections": results_by_collection,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Error loading scenario data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_scenario_documents(self, scenario_data: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Generate documents from scenario data - Updated to work with actual scenario structure"""
        documents = {
            "main": [],
            "code": [],
            "documentation": [],
            "slack_messages": [],
            "pull_requests": [],
            "tickets": []
        }
        
    
        documents["main"].extend(self._create_company_overview(scenario_data))
        
        
        documents["code"].extend(self._create_project_code_docs(scenario_data))
        documents["documentation"].extend(self._create_project_documentation(scenario_data))
        documents["tickets"].extend(self._create_project_tickets(scenario_data))
        documents["pull_requests"].extend(self._create_project_prs(scenario_data))
        
        
        documents["slack_messages"].extend(self._create_team_communications(scenario_data))
        
        return documents

    def _create_company_overview(self, scenario_data: Dict[str, Any]) -> List[Dict]:
        """Create company overview documents from scenario data"""
        docs = []
        
        
        overview_content = f"""
# {scenario_data.get('scenario_name', 'Demo Company')}

## Company Profile
- **Type**: {scenario_data.get('company_type', 'startup').replace('_', ' ').title()}
- **Industry**: {scenario_data.get('industry', 'technology').title()}
- **Team Size**: {scenario_data.get('team_size', 10)} employees

## Technology Stack
{chr(10).join(f"- {tech}" for tech in scenario_data.get('tech_stack', ['React', 'Node.js']))}

## Development Tools
{chr(10).join(f"- {tool}" for tool in scenario_data.get('tools', ['GitHub', 'Slack']))}

## Team Structure
"""
        
        
        team_structure = scenario_data.get('team_structure', {})
        if team_structure:
            if isinstance(team_structure, dict):
                for role, count in team_structure.items():
                    overview_content += f"- {role.replace('_', ' ').title()}: {count}\n"
            else:
                overview_content += f"- Total team members: {scenario_data.get('team_size', 'Unknown')}\n"
        
        
        compliance = scenario_data.get('compliance', [])
        if compliance:
            overview_content += f"\n## Compliance Requirements\n"
            overview_content += chr(10).join(f"- {comp}" for comp in compliance)
        
        
        business_metrics = scenario_data.get('business_metrics', {})
        if business_metrics:
            overview_content += f"\n## Business Metrics\n"
            for metric, value in business_metrics.items():
                overview_content += f"- {metric.replace('_', ' ').title()}: {value}\n"
        
        docs.append({
            "content": overview_content.strip(),
            "metadata": {
                "source_type": "company_overview",
                "file_path": "company/overview.md",
                "scenario_type": scenario_data.get('company_type', 'startup'),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tags": "company,overview,team"
            }
        })
        
        
        user_profile = scenario_data.get('user_profile', {})
        if user_profile:
            profile_content = f"""
# Team Member Profile: {user_profile.get('name', 'Team Member')}

## Role Information
- **Position**: {user_profile.get('role', 'Developer')}
- **Experience**: {user_profile.get('experience', 'N/A')}
- **Team**: {user_profile.get('team', 'Development')}

## Background
"""
            
            if user_profile.get('joining_date'):
                profile_content += f"- **Joined**: {user_profile.get('joining_date')}\n"
            if user_profile.get('specialization'):
                profile_content += f"- **Specialization**: {user_profile.get('specialization')}\n"
            if user_profile.get('location'):
                profile_content += f"- **Location**: {user_profile.get('location')}\n"
            
           
            recent_activities = scenario_data.get('recent_activities', [])
            if recent_activities:
                profile_content += f"\n## Recent Activities\n"
                profile_content += chr(10).join(f"- {activity}" for activity in recent_activities)
            
            
            learning_goals = scenario_data.get('learning_goals', [])
            if learning_goals:
                profile_content += f"\n## Learning Goals\n"
                profile_content += chr(10).join(f"- {goal}" for goal in learning_goals)
            
            docs.append({
                "content": profile_content.strip(),
                "metadata": {
                    "source_type": "team_member",
                    "file_path": f"team/{user_profile.get('name', 'member').lower().replace(' ', '_')}.md",
                    "role": user_profile.get('role', 'developer'),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tags": "team,profile,member"
                }
            })
        
        return docs

    def _create_project_code_docs(self, scenario_data: Dict[str, Any]) -> List[Dict]:
        """Create code-related documents from project data"""
        docs = []
        projects = scenario_data.get('projects', [])
        tech_stack = scenario_data.get('tech_stack', ['JavaScript'])
        
        for project in projects:
            project_name = project.get('name', 'Unnamed Project')
            technologies = project.get('technologies', tech_stack[:2])  
            
            
            readme_content = f"""
# {project_name}

## Overview
{self._generate_project_description(project, scenario_data)}

## Status
- **Current Status**: {project.get('status', 'unknown').replace('_', ' ').title()}
- **Priority**: {project.get('priority', 'medium').title()}
"""
            
            if project.get('deadline'):
                readme_content += f"- **Deadline**: {project.get('deadline')}\n"
            if project.get('completion_date'):
                readme_content += f"- **Completed**: {project.get('completion_date')}\n"
            if project.get('budget'):
                readme_content += f"- **Budget**: {project.get('budget')}\n"
            if project.get('client'):
                readme_content += f"- **Client**: {project.get('client')}\n"
            
            readme_content += f"""

## Technologies Used
{chr(10).join(f"- {tech}" for tech in technologies)}

## Project Structure
```
{project_name.lower().replace(' ', '-')}/
├── src/
│   ├── components/
│   ├── services/
│   ├── utils/
│   └── tests/
├── docs/
├── package.json
└── README.md
```

## Getting Started
1. Clone the repository
2. Install dependencies
3. Configure environment variables
4. Run development server
5. Run tests

## Key Features
{self._generate_project_features(project, technologies)}
"""
            
            docs.append({
                "content": readme_content.strip(),
                "metadata": {
                    "source_type": "code",
                    "file_path": f"projects/{project_name.lower().replace(' ', '-')}/README.md",
                    "project": project_name,
                    "status": project.get('status', 'unknown'),
                    "technologies": ",".join(technologies),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tags": "project,readme,setup"
                }
            })
            
            
            for tech in technologies[:2]:  
                sample_code = self._generate_sample_code(tech, project_name)
                if sample_code:
                    docs.append({
                        "content": sample_code['content'],
                        "metadata": {
                            "source_type": "code",
                            "file_path": sample_code['file_path'],
                            "project": project_name,
                            "language": sample_code['language'],
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "tags": f"code,implementation,{tech.lower()}"
                        }
                    })
        
        return docs

    def _create_project_documentation(self, scenario_data: Dict[str, Any]) -> List[Dict]:
        """Create documentation from scenario data"""
        docs = []
        company_type = scenario_data.get('company_type', 'startup')
        
        
        setup_guide = f"""
# Development Environment Setup

## Prerequisites
{self._get_prerequisites_for_stack(scenario_data.get('tech_stack', []))}

## Installation Steps

### 1. Repository Setup
```bash
git clone https://github.com/company/main-repo.git
cd main-repo
```

### 2. Environment Configuration
Copy the environment template:
```bash
cp .env.example .env
```

Update the following variables:
- Database connection strings
- API keys and secrets
- External service endpoints

### 3. Dependencies
{self._get_install_commands_for_stack(scenario_data.get('tech_stack', []))}

### 4. Database Setup
{self._get_database_setup(scenario_data.get('tech_stack', []))}

### 5. Development Server
{self._get_dev_server_commands(scenario_data.get('tech_stack', []))}

## Common Issues

**Database Connection Errors**
- Ensure PostgreSQL/database service is running
- Check connection string in .env file
- Verify database exists and user has permissions

**Port Already in Use**
- Check if another instance is running
- Use different port: `PORT=3001 npm start`

**Missing Environment Variables**
- Copy .env.example to .env
- Ask team lead for production values
- Check documentation for required variables

## Next Steps
- Review coding standards document
- Join team Slack channels
- Set up development branch
- Run test suite to verify setup
"""
        
        docs.append({
            "content": setup_guide.strip(),
            "metadata": {
                "source_type": "documentation",
                "file_path": "docs/setup-guide.md",
                "category": "onboarding",
                "difficulty": "beginner",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tags": "setup,guide,development"
            }
        })
        
        
        if any(tech in ['Node.js', 'FastAPI', 'Spring Boot', 'Python'] for tech in scenario_data.get('tech_stack', [])):
            api_docs = f"""
# API Documentation

## Authentication
All API requests require authentication using JWT tokens.

### Login
```
POST /api/auth/login
Content-Type: application/json

{{
  "email": "user@example.com",
  "password": "password"
}}
```

### Response
```json
{{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {{
    "id": 1,
    "email": "user@example.com",
    "role": "user"
  }}
}}
```

## Core Endpoints

### Users
- `GET /api/users` - List users
- `GET /api/users/:id` - Get user details
- `POST /api/users` - Create user
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user

### Projects
- `GET /api/projects` - List projects
- `GET /api/projects/:id` - Get project details
- `POST /api/projects` - Create project
- `PUT /api/projects/:id` - Update project

## Error Responses
All endpoints return standardized error responses:

```json
{{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {{}}
}}
```

## Rate Limiting
- 100 requests per minute per IP
- 1000 requests per hour per authenticated user
"""
            
            docs.append({
                "content": api_docs.strip(),
                "metadata": {
                    "source_type": "documentation",
                    "file_path": "docs/api-reference.md",
                    "category": "api",
                    "difficulty": "intermediate",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tags": "api,reference,endpoints"
                }
            })
        
        return docs

    def _create_project_tickets(self, scenario_data: Dict[str, Any]) -> List[Dict]:
        """Create tickets/issues from project data"""
        docs = []
        projects = scenario_data.get('projects', [])
        user_profile = scenario_data.get('user_profile', {})
        
        ticket_counter = 1
        
        for project in projects:
            project_name = project.get('name', 'Unnamed Project')
            status = project.get('status', 'unknown')
            
           
            if status == 'in_progress':
                
                ticket = f"""
# BUG-{ticket_counter:03d}: Performance Issue in {project_name}

## Description
Users are experiencing slow loading times when accessing the main dashboard. Response times are averaging 5-8 seconds instead of the expected 1-2 seconds.

## Priority: High
## Status: Open
## Assignee: {user_profile.get('name', 'Unassigned')}
## Reporter: QA Team

## Steps to Reproduce
1. Log into the application
2. Navigate to main dashboard
3. Observe loading time
4. Check browser network tab

## Expected Behavior
Dashboard should load within 1-2 seconds

## Actual Behavior
Dashboard takes 5-8 seconds to load, causing poor user experience

## Environment
- Browser: Chrome 120+
- Environment: Staging
- Database: PostgreSQL

## Additional Notes
This issue started appearing after the recent deployment. May be related to new database queries or API changes.

## Labels
performance, bug, high-priority, {project_name.lower().replace(' ', '-')}
"""
                
                docs.append({
                    "content": ticket.strip(),
                    "metadata": {
                        "source_type": "ticket",
                        "ticket_id": f"BUG-{ticket_counter:03d}",
                        "type": "bug",
                        "priority": "high",
                        "status": "open",
                        "project": project_name,
                        "assignee": user_profile.get('name', 'unassigned'),
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "tags": "ticket,bug,performance"
                    }
                })
                ticket_counter += 1
                
            elif status == 'planning':
                
                ticket = f"""
# FEATURE-{ticket_counter:03d}: Implement {project_name} Core Features

## Description
Implement the core functionality for {project_name} including user authentication, data processing, and API endpoints.

## Priority: Medium
## Status: Planning
## Assignee: {user_profile.get('name', 'Unassigned')}
## Reporter: Product Manager

## Requirements
- User registration and login system
- Data validation and processing
- RESTful API endpoints
- Unit test coverage (>80%)
- Documentation updates

## Acceptance Criteria
- [ ] Users can register with email/password
- [ ] Login system with JWT tokens
- [ ] API endpoints follow REST conventions
- [ ] All endpoints have proper error handling
- [ ] Tests cover critical paths
- [ ] Documentation is updated

## Technical Notes
Technologies to use: {', '.join(project.get('technologies', ['To be determined']))}

## Deadline
{project.get('deadline', 'To be determined')}

## Labels
feature, planning, {project_name.lower().replace(' ', '-')}
"""
                
                docs.append({
                    "content": ticket.strip(),
                    "metadata": {
                        "source_type": "ticket",
                        "ticket_id": f"FEATURE-{ticket_counter:03d}",
                        "type": "feature",
                        "priority": "medium",
                        "status": "planning",
                        "project": project_name,
                        "assignee": user_profile.get('name', 'unassigned'),
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "tags": "ticket,feature,planning"
                    }
                })
                ticket_counter += 1
        
        return docs

    def _create_project_prs(self, scenario_data: Dict[str, Any]) -> List[Dict]:
        """Create pull request documents from project data"""
        docs = []
        projects = scenario_data.get('projects', [])
        user_profile = scenario_data.get('user_profile', {})
        
        pr_counter = 1
        
        for project in projects:
            if project.get('status') in ['in_progress', 'completed']:
                project_name = project.get('name', 'Unnamed Project')
                technologies = project.get('technologies', ['JavaScript'])
                
                pr_content = f"""
# Pull Request #{pr_counter}: Implement {project_name} Authentication System

## Description
This PR implements the user authentication system for {project_name}, including login, registration, and JWT token management.

## Changes Made
- Added user registration endpoint with email validation
- Implemented JWT-based authentication system
- Created login/logout functionality
- Added password hashing with bcrypt
- Implemented middleware for protected routes
- Added input validation and error handling

## Technologies Used
{chr(10).join(f"- {tech}" for tech in technologies)}

## Testing
- [x] Unit tests for auth endpoints (95% coverage)
- [x] Integration tests for login flow
- [x] Manual testing on staging environment
- [x] Security review completed
- [x] Performance testing passed

## Security Considerations
- Passwords are hashed using bcrypt
- JWT tokens have expiration time
- Input validation prevents injection attacks
- Rate limiting implemented for auth endpoints

## Files Changed
- `src/auth/authController.js` - Authentication logic
- `src/auth/authMiddleware.js` - JWT verification
- `src/models/User.js` - User model with validation
- `src/routes/auth.js` - Authentication routes
- `tests/auth.test.js` - Comprehensive test suite
- `docs/auth-api.md` - API documentation

## Database Changes
- Created `users` table with proper indexes
- Added migration for user authentication
- Updated database schema documentation

## Deployment Notes
- Environment variables for JWT secret required
- Database migration needs to run before deployment
- Update nginx config for new auth endpoints

## Review Checklist
- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Security review completed
- [ ] Performance impact assessed

Author: {user_profile.get('name', 'Developer')}
Reviewers: @tech-lead @security-team
"""
                
                docs.append({
                    "content": pr_content.strip(),
                    "metadata": {
                        "source_type": "pr_description",
                        "pr_number": pr_counter,
                        "project": project_name,
                        "author": user_profile.get('name', 'developer'),
                        "status": "open" if project.get('status') == 'in_progress' else "merged",
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "tags": "pull-request,authentication,code-review"
                    }
                })
                pr_counter += 1
        
        return docs

    def _create_team_communications(self, scenario_data: Dict[str, Any]) -> List[Dict]:
        """Create team communication documents (Slack-like)"""
        docs = []
        user_profile = scenario_data.get('user_profile', {})
        projects = scenario_data.get('projects', [])
        recent_activities = scenario_data.get('recent_activities', [])
        company_type = scenario_data.get('company_type', 'startup')
        
        
        standup_content = f"""
Channel: #daily-standup
Date: {datetime.now().strftime('%Y-%m-%d')}

@channel Good morning team! Time for our daily standup 🌅

{user_profile.get('name', 'TeamMember')}: Hey everyone! 
Yesterday: {recent_activities[0] if recent_activities else 'Worked on bug fixes'}
Today: Working on the authentication module for our main project
Blockers: None at the moment, but might need help with JWT implementation later

@tech-lead: Thanks {user_profile.get('name', 'TeamMember')}! For JWT, I'd recommend using the standard library we discussed. DM me if you need the documentation link.

@designer: Morning! Yesterday I finished the new login screen mockups. Today I'll be working on the dashboard wireframes. No blockers.

@product-manager: Great work everyone! Just a reminder that our sprint review is Friday. Please update your tickets in Jira.

{user_profile.get('name', 'TeamMember')}: Will do! Looking forward to showing the auth progress 🚀
"""
        
        docs.append({
            "content": standup_content.strip(),
            "metadata": {
                "source_type": "slack",
                "channel": "daily-standup",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "participants": ",".join([user_profile.get('name', 'TeamMember'), "tech-lead", "designer", "product-manager"]),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tags": "standup,team,daily,communication"
            }
        })
        
        
        if projects:
            project = projects[0]
            tech_discussion = f"""
Channel: #tech-discussion
Date: {datetime.now().strftime('%Y-%m-%d')}

{user_profile.get('name', 'TeamMember')}: Hey team, I'm working on {project.get('name', 'the main project')} and wondering about our database schema approach. Should we normalize the user preferences table or keep it as JSON?

@senior-dev: Good question! For {project.get('name', 'this project')}, I'd lean toward JSON for flexibility since user preferences can vary a lot. But what's your use case?

{user_profile.get('name', 'TeamMember')}: We need to store user dashboard configurations, notification settings, and theme preferences. Some users might have custom widgets.

@database-expert: JSON works well for that. Just make sure to validate the structure and consider indexing if you need to query specific preference fields.

@tech-lead: Agreed. PostgreSQL's JSONB type would be perfect here. You get flexibility plus performance for queries when needed.

{user_profile.get('name', 'TeamMember')}: Perfect! I'll go with JSONB then. Thanks everyone! 🙏

@senior-dev: Don't forget to add proper TypeScript types for the preference structure too!
"""
            
            docs.append({
                "content": tech_discussion.strip(),
                "metadata": {
                    "source_type": "slack",
                    "channel": "tech-discussion",
                    "date": datetime.now().strftime('%Y-%m-%d'),
                    "participants": ",".join([user_profile.get('name', 'TeamMember'), "senior-dev", "database-expert", "tech-lead"]),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tags": "technical,database,discussion,architecture"
                }
            })
        
        return docs

    

    def _generate_project_description(self, project: Dict[str, Any], scenario_data: Dict[str, Any]) -> str:
        """Generate a realistic project description"""
        project_name = project.get('name', 'Project')
        company_type = scenario_data.get('company_type', 'startup')
        
        descriptions = {
            'Payment Gateway Integration': 'A secure payment processing system that integrates with multiple payment providers to handle transactions, subscriptions, and refunds.',
            'User Dashboard Redesign': 'A modern, responsive dashboard interface that provides users with real-time analytics, customizable widgets, and improved user experience.',
            'HIPAA Compliance Upgrade': 'Critical security and compliance updates to ensure all patient data handling meets HIPAA requirements and industry standards.',
            'Microservices Migration': 'Architectural transformation from monolithic to microservices architecture to improve scalability, maintainability, and deployment flexibility.',
            'E-commerce Platform': 'A full-featured online store with product catalog, shopping cart, payment processing, and inventory management.',
            'AI Content Generator': 'An intelligent content creation tool that uses machine learning to generate high-quality marketing copy, blog posts, and social media content.'
        }
        
        return descriptions.get(project_name, f'A {company_type} project focused on delivering high-quality software solutions using modern technologies and best practices.')

    def _generate_project_features(self, project: Dict[str, Any], technologies: List[str]) -> str:
        """Generate realistic project features"""
        base_features = [
            'User authentication and authorization',
            'Responsive web interface',
            'RESTful API endpoints',
            'Database integration',
            'Error handling and logging'
        ]
        
        tech_features = {
            'React': '- Interactive user interface components',
            'Node.js': '- Server-side JavaScript runtime',
            'Python': '- Data processing and analysis capabilities',
            'FastAPI': '- High-performance API with automatic documentation',
            'PostgreSQL': '- Relational database with advanced querying',
            'Stripe': '- Secure payment processing integration',
            'AWS': '- Cloud deployment and scaling',
            'Docker': '- Containerized deployment'
        }
        
        features = base_features.copy()
        for tech in technologies:
            if tech in tech_features:
                features.append(tech_features[tech])
        
        return chr(10).join(f"- {feature}" for feature in features[:6])

    def _generate_sample_code(self, technology: str, project_name: str) -> Optional[Dict[str, str]]:
        """Generate sample code for different technologies"""
        project_slug = project_name.lower().replace(' ', '_')
        
        code_samples = {
            'React': {
                'content': f'''import React, {{ useState, useEffect }} from 'react';
import {{ {project_slug.title()}API }} from '../services/api';

const {project_slug.title()}Component = () => {{
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {{
    const fetchData = async () => {{
      try {{
        const result = await {project_slug.title()}API.getData();
        setData(result);
      }} catch (err) {{
        setError(err.message);
      }} finally {{
        setLoading(false);
      }}
    }};

    fetchData();
  }}, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {{error}}</div>;

  return (
    <div className="{project_slug}-container">
      <h1>{project_name}</h1>
      <div className="data-list">
        {{data.map(item => (
          <div key={{item.id}} className="data-item">
            {{item.title}}
          </div>
        ))}}
      </div>
    </div>
  );
}};

export default {project_slug.title()}Component;''',
                'file_path': f'src/components/{project_slug.title()}Component.jsx',
                'language': 'javascript'
            },
            'Node.js': {
                'content': f'''const express = require('express');
const {{ body, validationResult }} = require('express-validator');
const {{ {project_slug.title()}Service }} = require('../services/{project_slug}Service');

const router = express.Router();

// Get all {project_slug} items
router.get('/', async (req, res) => {{
  try {{
    const items = await {project_slug.title()}Service.getAll();
    res.json({{ success: true, data: items }});
  }} catch (error) {{
    res.status(500).json({{ success: false, error: error.message }});
  }}
}});

// Create new {project_slug} item
router.post('/',
  [
    body('title').isLength({{ min: 1 }}).withMessage('Title is required'),
    body('description').optional().isLength({{ max: 500 }})
  ],
  async (req, res) => {{
    const errors = validationResult(req);
    if (!errors.isEmpty()) {{
      return res.status(400).json({{ success: false, errors: errors.array() }});
    }}

    try {{
      const newItem = await {project_slug.title()}Service.create(req.body);
      res.status(201).json({{ success: true, data: newItem }});
    }} catch (error) {{
      res.status(500).json({{ success: false, error: error.message }});
    }}
  }}
);

module.exports = router;''',
                'file_path': f'src/routes/{project_slug}Routes.js',
                'language': 'javascript'
            },
            'Python': {
                'content': f'''from typing import List, Optional
from datetime import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class {project_slug.title()}Item:
    id: Optional[int] = None
    title: str = ""
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class {project_slug.title()}Service:
    """Service class for {project_name} operations"""
    
    def __init__(self, database_connection):
        self.db = database_connection
    
    async def get_all(self) -> List[{project_slug.title()}Item]:
        """Retrieve all {project_slug} items"""
        try:
            query = "SELECT * FROM {project_slug}_items ORDER BY created_at DESC"
            results = await self.db.fetch_all(query)
            
            return [
                {project_slug.title()}Item(
                    id=row['id'],
                    title=row['title'],
                    description=row['description'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                for row in results
            ]
        except Exception as e:
            logger.error(f"Error retrieving {project_slug} items: {{e}}")
            raise
    
    async def create(self, item_data: dict) -> {project_slug.title()}Item:
        """Create a new {project_slug} item"""
        try:
            query = """
                INSERT INTO {project_slug}_items (title, description, created_at, updated_at)
                VALUES ($1, $2, $3, $4)
                RETURNING *
            """
            now = datetime.utcnow()
            
            result = await self.db.fetch_one(
                query,
                item_data['title'],
                item_data.get('description'),
                now,
                now
            )
            
            logger.info(f"Created new {project_slug} item: {{result['id']}}")
            
            return {project_slug.title()}Item(
                id=result['id'],
                title=result['title'],
                description=result['description'],
                created_at=result['created_at'],
                updated_at=result['updated_at']
            )
        except Exception as e:
            logger.error(f"Error creating {project_slug} item: {{e}}")
            raise''',
                'file_path': f'src/services/{project_slug}_service.py',
                'language': 'python'
            }
        }
        
        return code_samples.get(technology)

    def _get_prerequisites_for_stack(self, tech_stack: List[str]) -> str:
        """Generate prerequisites based on tech stack"""
        prereqs = set()
        
        prereq_mapping = {
            'React': 'Node.js 16+ and npm',
            'Node.js': 'Node.js 16+ and npm',
            'Python': 'Python 3.8+ and pip',
            'FastAPI': 'Python 3.8+ and pip',
            'Java': 'Java 11+ and Maven',
            'Spring Boot': 'Java 11+ and Maven',
            'PostgreSQL': 'PostgreSQL 12+',
            'AWS': 'AWS CLI configured',
            'Docker': 'Docker and Docker Compose'
        }
        
        for tech in tech_stack:
            if tech in prereq_mapping:
                prereqs.add(prereq_mapping[tech])
        
        if not prereqs:
            prereqs.add('Basic development environment')
        
        return chr(10).join(f"- {prereq}" for prereq in sorted(prereqs))

    def _get_install_commands_for_stack(self, tech_stack: List[str]) -> str:
        """Generate install commands based on tech stack"""
        commands = []
        
        if any(tech in ['React', 'Node.js'] for tech in tech_stack):
            commands.append("```bash\nnpm install\n```")
        
        if any(tech in ['Python', 'FastAPI'] for tech in tech_stack):
            commands.append("```bash\npip install -r requirements.txt\n```")
        
        if any(tech in ['Java', 'Spring Boot'] for tech in tech_stack):
            commands.append("```bash\nmvn install\n```")
        
        return chr(10).join(commands) if commands else "```bash\n# Follow technology-specific setup\n```"

    def _get_database_setup(self, tech_stack: List[str]) -> str:
        """Generate database setup instructions"""
        if 'PostgreSQL' in tech_stack:
            return """```bash
# Create database
createdb project_db

# Run migrations
npm run migrate
# or
python manage.py migrate
```"""
        elif 'Oracle' in tech_stack:
            return """```bash
# Connect to Oracle database
# Run migration scripts in order
sqlplus user/password@database @migrations/001_initial.sql
```"""
        else:
            return """```bash
# Set up database according to project requirements
# Run any migration scripts
```"""

    def _get_dev_server_commands(self, tech_stack: List[str]) -> str:
        """Generate development server commands"""
        commands = []
        
        if 'React' in tech_stack:
            commands.append("```bash\n# Frontend\nnpm start\n```")
        
        if 'Node.js' in tech_stack:
            commands.append("```bash\n# Backend\nnpm run dev\n```")
        
        if any(tech in ['Python', 'FastAPI'] for tech in tech_stack):
            commands.append("```bash\n# API Server\nuvicorn main:app --reload\n# or\npython manage.py runserver\n```")
        
        return chr(10).join(commands) if commands else "```bash\n# Start development server\nnpm start\n```"

    def populate_all_scenarios(self) -> Dict[str, Any]:
        """Populate demo collections with all available scenarios"""
        try:
            self.initialize_demo_collections()
            
            scenarios = ["startup", "enterprise", "freelancer"]
            results = {}
            total_documents = 0
            total_chunks = 0
            
            for scenario in scenarios:
                result = self.load_scenario_data(scenario)
                results[scenario] = result
                
                if result.get("success"):
                    total_documents += result.get("total_documents", 0)
                    total_chunks += result.get("total_chunks", 0)
            
            return {
                "success": True,
                "scenarios_loaded": scenarios,
                "total_documents": total_documents,
                "total_chunks": total_chunks,
                "results": results,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Error populating all scenarios: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def reset_demo_data(self) -> Dict[str, Any]:
        """Reset demo collections and clear all data"""
        try:
            collections = self.demo_db_setup.collections
            reset_results = {}
            
            for collection_name in collections.keys():
                success = self.demo_db_setup.reset_collection(collection_name)
                reset_results[collection_name] = success
            
            return {
                "success": all(reset_results.values()),
                "collections_reset": reset_results,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Error resetting demo data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_demo_stats(self) -> Dict[str, Any]:
        """Get statistics about demo collections"""
        try:
            stats = self.demo_db_setup.get_collection_stats()
            
            total_docs = sum(
                collection.get("count", 0) 
                for collection in stats.values() 
                if isinstance(collection, dict)
            )
            
            return {
                "success": True,
                "total_documents": total_docs,
                "collections": stats,
                "demo_mode": True,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Error getting demo stats: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_sample_search_queries(self) -> List[Dict[str, Any]]:
        """Create sample search queries for demo purposes"""
        queries = [
            {
                "query": "How do I set up the development environment?",
                "category": "getting_started",
                "expected_collections": ["documentation", "main"]
            },
            {
                "query": "authentication system implementation",
                "category": "technical",
                "expected_collections": ["code", "documentation"]
            },
            {
                "query": "bug reports and issues",
                "category": "troubleshooting",
                "expected_collections": ["tickets", "slack_messages"]
            },
            {
                "query": "code review feedback",
                "category": "development",
                "expected_collections": ["pull_requests", "slack_messages"]
            },
            {
                "query": "deployment and production issues",
                "category": "operations",
                "expected_collections": ["tickets", "documentation"]
            }
        ]
        
        return queries
    
    def generate_demo_context(self, user_role: str = "developer") -> Dict[str, Any]:
        """Generate contextual information for demo users"""
        contexts = {
            "developer": {
                "recent_activity": ["Worked on authentication feature", "Fixed login bug", "Updated documentation"],
                "current_tasks": ["Implement user dashboard", "Write unit tests", "Review pull requests"],
                "interests": ["React", "Node.js", "Testing", "API Design"],
                "skill_level": "intermediate"
            },
            "designer": {
                "recent_activity": ["Created new UI mockups", "Updated design system", "User research session"],
                "current_tasks": ["Design mobile interface", "Create prototypes", "Conduct usability tests"],
                "interests": ["UI/UX", "Prototyping", "User Research", "Design Systems"],
                "skill_level": "advanced"
            },
            "manager": {
                "recent_activity": ["Sprint planning", "Team retrospective", "Stakeholder meetings"],
                "current_tasks": ["Resource planning", "Performance reviews", "Project coordination"],
                "interests": ["Project Management", "Team Leadership", "Agile", "Strategy"],
                "skill_level": "expert"
            }
        }
        
        return contexts.get(user_role, contexts["developer"])

def initialize_demo() -> Dict[str, Any]:
    """Quick demo initialization"""
    demo_store = DemoVectorStore()
    return demo_store.populate_all_scenarios()

def reset_demo() -> Dict[str, Any]:
    """Quick demo reset"""
    demo_store = DemoVectorStore()
    return demo_store.reset_demo_data()

def get_sample_queries() -> List[Dict[str, Any]]:
    """Get sample queries for testing"""
    demo_store = DemoVectorStore()
    return demo_store.create_sample_search_queries()

if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        demo_store = DemoVectorStore()
        
        if command == "init":
            result = demo_store.initialize_demo_collections()
            print(json.dumps(result, indent=2))
            
        elif command == "populate":
            scenario = sys.argv[2] if len(sys.argv) > 2 else "startup"
            result = demo_store.load_scenario_data(scenario)
            print(json.dumps(result, indent=2))
            
        elif command == "populate_all":
            result = demo_store.populate_all_scenarios()
            print(json.dumps(result, indent=2))
            
        elif command == "stats":
            result = demo_store.get_demo_stats()
            print(json.dumps(result, indent=2))
            
        elif command == "reset":
            result = demo_store.reset_demo_data()
            print(json.dumps(result, indent=2))
            
        elif command == "queries":
            queries = demo_store.create_sample_search_queries()
            print(json.dumps(queries, indent=2))
            
        else:
            print("Available commands:")
            print("  init - Initialize demo collections")
            print("  populate [scenario] - Load scenario data")
            print("  populate_all - Load all scenarios")
            print("  stats - Show demo statistics")
            print("  reset - Reset demo data")
            print("  queries - Show sample queries")
    else:
        print("Usage: python demo_vectorstore.py [init|populate|populate_all|stats|reset|queries] [args...]")