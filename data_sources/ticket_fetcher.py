import os
import yaml
import httpx
import base64
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger
from datetime import datetime, timedelta
import asyncio
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.helpers import get_file_hash, sanitize_text, extract_technical_terms
from dotenv import load_dotenv
load_dotenv()

class TicketFetcher:
    
    def __init__(self, config_path: str = None, demo_mode: bool = False, user_id: str = None):
        self.config = self._load_config(config_path)
        self.demo_mode = demo_mode
        self.user_id = user_id or "demo_user"
        self.jira_token = os.getenv("JIRA_API_TOKEN")
        self.jira_email = os.getenv("JIRA_EMAIL")
        self.jira_url = os.getenv("JIRA_URL")
        self.github_token = os.getenv("GITHUB_TOKEN")
        
        if self.demo_mode:
            self.demo_config = self._load_demo_config()
            logger.info(f"TicketFetcher initialized in DEMO mode for user: {self.user_id}")
        else:
            logger.info(f"TicketFetcher initialized in REAL mode for user: {self.user_id}")
        
    def _load_config(self, config_path: str = None) -> Dict:
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "settings.yaml"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_demo_config(self) -> Dict:
        demo_config_path = os.path.join(
            os.path.dirname(__file__), "..", "configs", "demo_settings.yaml"
        )
        
        try:
            with open(demo_config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning("Demo config not found, using defaults")
            return {
                'scenarios': ['startup', 'enterprise', 'freelancer']
            }
    
    async def fetch_tickets(
        self, 
        source: str = "mock",
        limit: int = 50,
        days_back: int = 90,
        project_key: str = None,
        scenario: str = None
    ) -> List[Dict[str, Any]]:
        
        if self.demo_mode:
            return await self._fetch_demo_tickets(scenario, limit)
        else:
            return await self._fetch_real_tickets(source, limit, days_back, project_key)
    
    async def _fetch_demo_tickets(self, scenario: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        logger.info(f"Generating DEMO tickets for scenario: {scenario or 'default'}")
        
        demo_tickets = self._generate_synthetic_tickets(scenario, limit)
        
        documents = []
        for ticket_data in demo_tickets:
            ticket_documents = self._process_demo_ticket(ticket_data, scenario)
            documents.extend(ticket_documents)
        
        for doc in documents:
            doc['metadata'].update({
                'is_demo': True,
                'demo_scenario': scenario or 'default',
                'user_id': self.user_id,
                'demo_note': 'This is synthetic demo data for showcase purposes'
            })
        
        logger.info(f"Generated {len(documents)} DEMO ticket documents")
        return documents
    
    async def _fetch_real_tickets(self, source: str = "mock", limit: int = 50, days_back: int = 90, project_key: str = None) -> List[Dict[str, Any]]:
        logger.info(f"Fetching tickets from {source} (limit: {limit}, days_back: {days_back})")
        
        if source == "jira":
            documents = await self._fetch_jira_tickets(limit, days_back, project_key)
        elif source == "github":
            documents = await self._fetch_github_issues(limit, days_back)
        else:
            documents = self._generate_mock_tickets(limit)
        
        for doc in documents:
            doc['metadata'].update({
                'is_demo': False,
                'user_id': self.user_id
            })
        
        return documents
    
    def _generate_synthetic_tickets(self, scenario: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        startup_tickets = [
            {
                "title": "Implement user authentication system",
                "description": "Set up JWT-based authentication with login, logout, and registration endpoints. Include password hashing, token validation, and session management. Need to support social login (Google, GitHub) as well.",
                "status": "In Progress",
                "priority": "High",
                "type": "Feature",
                "assignee": "sarah-fullstack",
                "reporter": "tech-lead",
                "labels": ["authentication", "security", "mvp"],
                "components": ["backend", "frontend"],
                "comments": [
                    {"author": "sarah-fullstack", "text": "Working on JWT implementation. Social auth integration will be in phase 2."},
                    {"author": "tech-lead", "text": "Make sure to include proper error handling for expired tokens."}
                ]
            },
            {
                "title": "Fix responsive design on mobile",
                "description": "The dashboard breaks on screens smaller than 768px. Navigation menu overlaps content and forms are cut off. Need to implement proper mobile-first responsive design.",
                "status": "To Do",
                "priority": "Medium",
                "type": "Bug",
                "assignee": "mike-frontend",
                "reporter": "product-manager",
                "labels": ["ui", "mobile", "responsive"],
                "components": ["frontend"],
                "comments": [
                    {"author": "mike-frontend", "text": "I'll start with the navigation menu issue first. Should be straightforward."}
                ]
            }
        ]
        
        enterprise_tickets = [
            {
                "title": "Migrate legacy authentication service to microservices",
                "description": "Phase 1 of microservices migration. Extract authentication logic from monolith into dedicated service. Includes database migration, API versioning, and gradual rollout strategy. Must maintain backward compatibility.",
                "status": "In Progress",
                "priority": "Critical",
                "type": "Epic",
                "assignee": "principal-engineer",
                "reporter": "architecture-team",
                "labels": ["microservices", "migration", "architecture"],
                "components": ["auth-service", "infrastructure"],
                "comments": [
                    {"author": "principal-engineer", "text": "Database schema migration completed. Working on service boundaries now."},
                    {"author": "devops-lead", "text": "Infrastructure is ready. Load balancers configured for gradual traffic switching."}
                ]
            },
            {
                "title": "Implement distributed tracing across services",
                "description": "Set up OpenTelemetry for distributed tracing across all microservices. Include correlation IDs, span propagation, and integration with monitoring dashboard. Critical for debugging production issues.",
                "status": "Code Review",
                "priority": "High",
                "type": "Feature",
                "assignee": "observability-team",
                "reporter": "sre-lead",
                "labels": ["observability", "tracing", "monitoring"],
                "components": ["infrastructure", "monitoring"],
                "comments": [
                    {"author": "observability-team", "text": "Implementation complete. All services now emit proper trace data."},
                    {"author": "sre-lead", "text": "Great work! The debugging improvements are already noticeable."}
                ]
            }
        ]
        
        freelancer_tickets = [
            {
                "title": "Add dark mode theme toggle",
                "description": "Client requested dark mode option for better user experience during evening hours. Implement theme toggle in header with localStorage persistence. Ensure proper contrast ratios for accessibility.",
                "status": "Done",
                "priority": "Medium",
                "type": "Feature",
                "assignee": "freelance-dev",
                "reporter": "client-contact",
                "labels": ["ui", "theme", "accessibility"],
                "components": ["frontend"],
                "comments": [
                    {"author": "freelance-dev", "text": "Dark mode implemented with smooth transitions. Client loves the color palette!"},
                    {"author": "client-contact", "text": "Perfect! Users are already commenting positively about the dark mode."}
                ]
            },
            {
                "title": "Optimize images for faster loading",
                "description": "Website images are loading slowly on mobile devices. Implement lazy loading, WebP format conversion, and responsive image sizes. Target 50% reduction in page load time.",
                "status": "In Progress",
                "priority": "Medium",
                "type": "Performance",
                "assignee": "freelance-dev",
                "reporter": "client-contact",
                "labels": ["performance", "images", "mobile"],
                "components": ["frontend"],
                "comments": [
                    {"author": "freelance-dev", "text": "Converted all images to WebP. Working on implementing lazy loading now."}
                ]
            }
        ]
        
        if scenario == 'enterprise':
            base_tickets = enterprise_tickets
        elif scenario == 'freelancer':
            base_tickets = freelancer_tickets
        else:
            base_tickets = startup_tickets
        
        result_tickets = []
        for i in range(min(limit, len(base_tickets) * 5)):
            base_ticket = base_tickets[i % len(base_tickets)]
            ticket_copy = base_ticket.copy()
            ticket_copy['ticket_id'] = f"DEMO-{i+1:03d}"
            result_tickets.append(ticket_copy)
        
        return result_tickets
    
    def _process_demo_ticket(self, ticket_data: Dict, scenario: str = None) -> List[Dict[str, Any]]:
        documents = []
        
        full_content = f"{ticket_data['title']}. {ticket_data['description']}"
        
        created_date = datetime.now() - timedelta(days=len(ticket_data.get('comments', [])) * 2)
        updated_date = datetime.now() - timedelta(hours=6)
        
        ticket_doc = {
            'content': sanitize_text(full_content),
            'metadata': {
                'source_type': 'ticket',
                'ticket_id': ticket_data['ticket_id'],
                'title': ticket_data['title'],
                'status': ticket_data['status'],
                'priority': ticket_data['priority'],
                'issue_type': ticket_data['type'],
                'assignee': ticket_data['assignee'],
                'reporter': ticket_data['reporter'],
                'created_at': created_date.isoformat(),
                'updated_at': updated_date.isoformat(),
                'labels': ticket_data['labels'],
                'components': ticket_data['components'],
                'content_hash': get_file_hash(full_content),
                'file_path': f"tickets/demo/{ticket_data['ticket_id']}",
                'tags': ['ticket', 'demo'] + ticket_data['labels'],
                'technical_terms': extract_technical_terms(ticket_data['description']),
                'complexity': self._estimate_ticket_complexity(ticket_data),
                'difficulty': self._determine_difficulty(ticket_data)
            }
        }
        documents.append(ticket_doc)
        
        for j, comment in enumerate(ticket_data.get('comments', [])):
            comment_doc = {
                'content': sanitize_text(comment['text']),
                'metadata': {
                    'source_type': 'ticket_comment',
                    'ticket_id': ticket_data['ticket_id'],
                    'title': ticket_data['title'],
                    'commenter': comment['author'],
                    'created_at': (created_date + timedelta(hours=j*12)).isoformat(),
                    'content_hash': get_file_hash(comment['text']),
                    'file_path': f"tickets/demo/{ticket_data['ticket_id']}/comment-{j+1}",
                    'tags': ['ticket_comment', 'demo', 'discussion'],
                    'technical_terms': extract_technical_terms(comment['text']),
                    'comment_type': self._classify_comment_type(comment['text'])
                }
            }
            documents.append(comment_doc)
        
        return documents
    
 

    
    async def _fetch_jira_tickets(self, limit: int, days_back: int, project_key: str = None) -> List[Dict[str, Any]]:
        if not all([self.jira_token, self.jira_email, self.jira_url]):
            logger.warning("Jira credentials not configured, generating mock data")
            return self._generate_mock_tickets(limit)
        
        documents = []
        
        try:
            auth_string = f"{self.jira_email}:{self.jira_token}"
            auth_bytes = base64.b64encode(auth_string.encode()).decode()
            headers = {
                "Authorization": f"Basic {auth_bytes}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            since_date = datetime.now() - timedelta(days=days_back)
            jql_parts = [f"updated >= '{since_date.strftime('%Y-%m-%d')}'"]
            
            if project_key:
                jql_parts.append(f"project = {project_key}")
            
            jql = " AND ".join(jql_parts)
            
            async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
                search_url = f"{self.jira_url}/rest/api/3/search"
                params = {
                    "jql": jql,
                    "maxResults": limit,
                    "fields": "summary,description,status,priority,assignee,reporter,created,updated,issuetype,components,labels,comments"
                }
                
                response = await client.get(search_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                issues = data.get("issues", [])
                
                for issue in issues:
                    try:
                        issue_docs = self._process_jira_issue(issue)
                        documents.extend(issue_docs)
                        
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        logger.error(f"Error processing Jira issue {issue.get('key', 'unknown')}: {str(e)}")
                        continue
        
        except Exception as e:
            logger.error(f"Error fetching Jira tickets: {str(e)}")
            return self._generate_mock_tickets(limit)
        
        logger.info(f"Fetched {len(documents)} Jira ticket documents")
        return documents
    
    async def _fetch_github_issues(self, limit: int, days_back: int) -> List[Dict[str, Any]]:
        if not self.github_token:
            logger.warning("GitHub token not configured, generating mock data")
            return self._generate_mock_tickets(limit)
        
        repo_url = self.config.get('data_sources', {}).get('github', {}).get('repo_url')
        if not repo_url:
            logger.warning("GitHub repo URL not configured, generating mock data")
            return self._generate_mock_tickets(limit)
        
        documents = []
        
        try:
            if "github.com/" in repo_url:
                repo_path = repo_url.split("github.com/")[-1].strip("/")
                owner, repo = repo_path.split("/")[:2]
            else:
                logger.error("Invalid GitHub repo URL format")
                return self._generate_mock_tickets(limit)
            
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            since_date = datetime.now() - timedelta(days=days_back)
            since_str = since_date.isoformat()
            
            async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
                url = f"https://api.github.com/repos/{owner}/{repo}/issues"
                params = {
                    "state": "all",
                    "since": since_str,
                    "per_page": min(100, limit),
                    "sort": "updated"
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                issues = response.json()
                
                for issue in issues[:limit]:
                    try:
                        if issue.get("pull_request"):
                            continue
                        
                        comments = []
                        if issue.get("comments", 0) > 0:
                            comments_url = issue["comments_url"]
                            comments_response = await client.get(comments_url)
                            if comments_response.status_code == 200:
                                comments = comments_response.json()
                        
                        issue_docs = self._process_github_issue(issue, comments, owner, repo)
                        documents.extend(issue_docs)
                        
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        logger.error(f"Error processing GitHub issue #{issue.get('number', 'unknown')}: {str(e)}")
                        continue
        
        except Exception as e:
            logger.error(f"Error fetching GitHub issues: {str(e)}")
            return self._generate_mock_tickets(limit)
        
        logger.info(f"Fetched {len(documents)} GitHub issue documents")
        return documents
    
    def _generate_mock_tickets(self, limit: int) -> List[Dict[str, Any]]:
        logger.info(f"Generating {limit} mock tickets")
        
        mock_tickets = [
            {
                "title": "Fix authentication timeout issue",
                "description": "Users are experiencing timeout errors when logging in during peak hours. The authentication service seems to be overwhelmed with requests. We need to investigate connection pooling and potentially implement rate limiting.",
                "status": "In Progress",
                "priority": "High",
                "type": "Bug",
                "assignee": "john.doe",
                "reporter": "jane.smith",
                "labels": ["authentication", "performance", "bug"],
                "components": ["auth-service", "api-gateway"],
                "comments": [
                    {"author": "john.doe", "text": "Investigating connection pool settings. Current pool size might be too small for peak load."},
                    {"author": "jane.smith", "text": "Adding monitoring to track connection pool utilization."}
                ]
            },
            {
                "title": "Implement user profile dashboard",
                "description": "Create a new dashboard where users can view and edit their profile information. Should include profile picture upload, contact details, and notification preferences. Design mockups are available in Figma.",
                "status": "To Do",
                "priority": "Medium",
                "type": "Feature",
                "assignee": "alice.dev",
                "reporter": "product.manager",
                "labels": ["frontend", "dashboard", "user-experience"],
                "components": ["web-app", "user-service"],
                "comments": [
                    {"author": "alice.dev", "text": "Reviewed the design mockups. Will start with basic profile editing functionality."},
                    {"author": "ux.designer", "text": "Make sure to include accessibility features as discussed."}
                ]
            },
            {
                "title": "Database migration for user preferences",
                "description": "Migrate user preference data from the old schema to the new normalized structure. This includes updating all existing records and ensuring data integrity. Migration should be reversible and include proper rollback procedures.",
                "status": "Done",
                "priority": "High",
                "type": "Task",
                "assignee": "db.admin",
                "reporter": "tech.lead",
                "labels": ["database", "migration", "backend"],
                "components": ["database", "user-service"],
                "comments": [
                    {"author": "db.admin", "text": "Migration completed successfully. All data integrity checks passed."},
                    {"author": "tech.lead", "text": "Great work! Performance improvements are already visible."}
                ]
            },
            {
                "title": "API rate limiting implementation",
                "description": "Implement rate limiting for public API endpoints to prevent abuse and ensure fair usage. Should support different rate limits for different user tiers (free, premium, enterprise). Include proper error responses and retry-after headers.",
                "status": "In Review",
                "priority": "Medium",
                "type": "Feature",
                "assignee": "api.dev",
                "reporter": "security.team",
                "labels": ["api", "security", "rate-limiting"],
                "components": ["api-gateway", "middleware"],
                "comments": [
                    {"author": "api.dev", "text": "Implementation complete. Added Redis-based rate limiting with sliding window algorithm."},
                    {"author": "security.team", "text": "Code review in progress. Looks good so far."}
                ]
            },
            {
                "title": "Update documentation for new API endpoints",
                "description": "Update API documentation to include the new user management endpoints added in v2.1. Include examples, error codes, and authentication requirements. Also update the OpenAPI spec file.",
                "status": "To Do",
                "priority": "Low",
                "type": "Documentation",
                "assignee": "tech.writer",
                "reporter": "api.dev",
                "labels": ["documentation", "api"],
                "components": ["documentation"],
                "comments": [
                    {"author": "tech.writer", "text": "Will start working on this after the current release documentation is complete."}
                ]
            }
        ]
        
        documents = []
        base_date = datetime.now()
        
        for i in range(min(limit, len(mock_tickets) * 10)):
            ticket_template = mock_tickets[i % len(mock_tickets)]
            ticket_id = f"MOCK-{i+1:03d}"
            
            created_date = base_date - timedelta(days=i*2, hours=i)
            updated_date = created_date + timedelta(hours=i*3)
            
            ticket_doc = {
                'content': sanitize_text(f"{ticket_template['title']}. {ticket_template['description']}"),
                'metadata': {
                    'source_type': 'ticket',
                    'ticket_id': ticket_id,
                    'title': ticket_template['title'],
                    'status': ticket_template['status'],
                    'priority': ticket_template['priority'],
                    'issue_type': ticket_template['type'],
                    'assignee': ticket_template['assignee'],
                    'reporter': ticket_template['reporter'],
                    'created_at': created_date.isoformat(),
                    'updated_at': updated_date.isoformat(),
                    'labels': ticket_template['labels'],
                    'components': ticket_template['components'],
                    'content_hash': get_file_hash(ticket_template['description']),
                    'file_path': f"tickets/mock/{ticket_id}",
                    'tags': ['ticket', 'mock'] + ticket_template['labels'],
                    'technical_terms': extract_technical_terms(ticket_template['description']),
                    'complexity': self._estimate_ticket_complexity(ticket_template),
                    'difficulty': self._determine_difficulty(ticket_template)
                }
            }
            documents.append(ticket_doc)
            
            for j, comment in enumerate(ticket_template['comments']):
                comment_doc = {
                    'content': sanitize_text(comment['text']),
                    'metadata': {
                        'source_type': 'ticket_comment',
                        'ticket_id': ticket_id,
                        'title': ticket_template['title'],
                        'commenter': comment['author'],
                        'created_at': (created_date + timedelta(hours=j*6)).isoformat(),
                        'content_hash': get_file_hash(comment['text']),
                        'file_path': f"tickets/mock/{ticket_id}/comment-{j+1}",
                        'tags': ['ticket_comment', 'mock', 'discussion'],
                        'technical_terms': extract_technical_terms(comment['text']),
                        'comment_type': self._classify_comment_type(comment['text'])
                    }
                }
                documents.append(comment_doc)
        
        return documents
    
    def _extract_adf_text(self, adf_content: Dict) -> str:
        if not isinstance(adf_content, dict):
            return str(adf_content)
        
        text_parts = []
        
        def extract_text_recursive(node):
            if isinstance(node, dict):
                if node.get('type') == 'text':
                    text_parts.append(node.get('text', ''))
                elif 'content' in node:
                    for child in node['content']:
                        extract_text_recursive(child)
            elif isinstance(node, list):
                for item in node:
                    extract_text_recursive(item)
        
        extract_text_recursive(adf_content)
        return ' '.join(text_parts)
    
    def _get_jira_user_name(self, user_obj: Optional[Dict]) -> Optional[str]:
        if not user_obj:
            return None
        return user_obj.get('displayName') or user_obj.get('name') or user_obj.get('emailAddress')
    
    def _extract_github_priority(self, issue: Dict) -> str:
        labels = [label.get('name', '').lower() for label in issue.get('labels', [])]
        
        if any('critical' in label or 'urgent' in label for label in labels):
            return 'Critical'
        elif any('high' in label for label in labels):
            return 'High'
        elif any('low' in label for label in labels):
            return 'Low'
        else:
            return 'Medium'
    
    def _estimate_ticket_complexity(self, ticket: Dict) -> str:
        description = ticket.get('description', '').lower()
        
        if any(word in description for word in ['migration', 'refactor', 'architecture']):
            return 'high'
        elif any(word in description for word in ['implement', 'feature', 'dashboard']):
            return 'medium'
        else:
            return 'low'
    
    def _estimate_jira_complexity(self, fields: Dict) -> str:
        issue_type = fields.get('issuetype', {}).get('name', '').lower()
        priority = fields.get('priority', {}).get('name', '').lower()
        
        if 'epic' in issue_type or priority == 'critical':
            return 'high'
        elif 'story' in issue_type or priority == 'high':
            return 'medium'
        else:
            return 'low'
    
    def _estimate_github_complexity(self, issue: Dict) -> str:
        labels = [label.get('name', '').lower() for label in issue.get('labels', [])]
        body_length = len(issue.get('body') or "")
        
        if any(label in ['epic', 'major', 'breaking-change'] for label in labels):
            return 'high'
        elif body_length > 500 or any(label in ['enhancement', 'feature'] for label in labels):
            return 'medium'
        else:
            return 'low'
    
    def _determine_difficulty(self, ticket: Dict) -> str:
        labels = ticket.get('labels', [])
        
        if any(label in ['backend', 'database', 'security'] for label in labels):
            return 'intermediate'
        elif any(label in ['frontend', 'documentation'] for label in labels):
            return 'beginner'
        else:
            return 'intermediate'
    
    def _determine_jira_difficulty(self, fields: Dict) -> str:
        components = [c.get('name', '').lower() for c in fields.get('components', [])]
        
        if any(comp in ['backend', 'database', 'security', 'infrastructure'] for comp in components):
            return 'advanced'
        elif any(comp in ['frontend', 'ui', 'documentation'] for comp in components):
            return 'beginner'
        else:
            return 'intermediate'
    
    def _determine_github_difficulty(self, issue: Dict) -> str:
        labels = [label.get('name', '').lower() for label in issue.get('labels', [])]
        
        if any(label in ['good first issue', 'beginner', 'documentation'] for label in labels):
            return 'beginner'
        elif any(label in ['advanced', 'expert', 'architecture'] for label in labels):
            return 'advanced'
        else:
            return 'intermediate'
    
    def _classify_comment_type(self, comment_text: str) -> str:
        text_lower = comment_text.lower()
        
        if any(word in text_lower for word in ['solution', 'fix', 'resolved', 'workaround']):
            return 'solution'
        elif text_lower.endswith('?') or 'question' in text_lower:
            return 'question'
        elif any(word in text_lower for word in ['agree', 'lgtm', 'approved', 'looks good']):
            return 'approval'
        elif any(word in text_lower for word in ['suggestion', 'consider', 'recommend']):
            return 'suggestion'
        elif any(word in text_lower for word in ['update', 'progress', 'status']):
            return 'update'
        else:
            return 'discussion'
    
    def set_demo_mode(self, demo_mode: bool, scenario: str = None) -> None:
        self.demo_mode = demo_mode
        if demo_mode:
            logger.info(f"Switched to DEMO mode with scenario: {scenario or 'default'}")
        else:
            logger.info("Switched to REAL mode")
    
    def get_demo_scenarios(self) -> List[str]:
        if hasattr(self, 'demo_config'):
            return self.demo_config.get('scenarios', ['startup', 'enterprise', 'freelancer'])
        return ['startup', 'enterprise', 'freelancer']
    
    def get_fetcher_stats(self) -> Dict[str, Any]:
        return {
            "supported_sources": ["jira", "github", "mock"],
            "demo_mode": self.demo_mode,
            "user_id": self.user_id,
            "demo_scenarios": self.get_demo_scenarios() if self.demo_mode else None,
            "jira_configured": all([self.jira_token, self.jira_email, self.jira_url]),
            "github_configured": bool(self.github_token),
            "mock_data_available": True,
            "data_types_processed": [
                "ticket_descriptions",
                "ticket_comments",
                "metadata",
                "labels_and_components",
                "status_tracking"
            ],
            "processing_features": [
                "content_sanitization",
                "technical_term_extraction",
                "complexity_estimation",
                "difficulty_classification",
                "comment_type_analysis"
            ]
        }
    
    def _process_jira_issue(self, issue: Dict) -> List[Dict[str, Any]]:
        documents = []
        fields = issue.get('fields', {})
        
        description = fields.get('description', {})
        if isinstance(description, dict):
            description_text = self._extract_adf_text(description)
        else:
            description_text = str(description) if description else ""
        
        title = fields.get('summary', '')
        full_content = f"{title}. {description_text}"
        
        issue_doc = {
            'content': sanitize_text(full_content),
            'metadata': {
                'source_type': 'ticket',
                'ticket_id': issue.get('key'),
                'title': title,
                'status': fields.get('status', {}).get('name', 'Unknown'),
                'priority': fields.get('priority', {}).get('name', 'Unknown'),
                'issue_type': fields.get('issuetype', {}).get('name', 'Unknown'),
                'assignee': self._get_jira_user_name(fields.get('assignee')),
                'reporter': self._get_jira_user_name(fields.get('reporter')),
                'created_at': fields.get('created'),
                'updated_at': fields.get('updated'),
                'labels': fields.get('labels', []),
                'components': [c.get('name') for c in fields.get('components', [])],
                'content_hash': get_file_hash(full_content),
                'file_path': f"tickets/jira/{issue.get('key')}",
                'tags': ['ticket', 'jira'] + fields.get('labels', []),
                'technical_terms': extract_technical_terms(full_content),
                'complexity': self._estimate_jira_complexity(fields),
                'difficulty': self._determine_jira_difficulty(fields)
            }
        }
        documents.append(issue_doc)
        
        comments = fields.get('comment', {}).get('comments', [])
        for comment in comments:
            comment_body  = comment.get('body', {})
            if isinstance(comment_body, dict):
                comment_text = self._extract_adf_text(comment_body)
            else:
                comment_text = str(comment_body) if comment_body else ""
            
            if comment_text.strip():
                comment_doc = {
                    'content': sanitize_text(comment_text),
                    'metadata': {
                        'source_type': 'ticket_comment',
                        'ticket_id': issue.get('key'),
                        'title': title,
                        'commenter': self._get_jira_user_name(comment.get('author')),
                        'created_at': comment.get('created'),
                        'updated_at': comment.get('updated'),
                        'content_hash': get_file_hash(comment_text),
                        'file_path': f"tickets/jira/{issue.get('key')}/comment-{comment.get('id')}",
                        'tags': ['ticket_comment', 'jira'],
                        'technical_terms': extract_technical_terms(comment_text),
                        'comment_type': self._classify_comment_type(comment_text)
                    }
                }
                documents.append(comment_doc)
        
        return documents
    
    def _process_github_issue(self, issue: Dict, comments: List[Dict], owner: str, repo: str) -> List[Dict[str, Any]]:
        documents = []

        title = issue.get('title', '')
        body = issue.get('body') or ''
        full_content = f"{title}. {body}"

        issue_doc = {
            'content': sanitize_text(full_content),
            'metadata': {
                'source_type': 'ticket',
                'ticket_id': f"#{issue.get('number')}",
                'title': title,
                'status': issue.get('state', 'open'),
                'priority': self._extract_github_priority(issue),
                'issue_type': 'issue',
                'assignee': issue.get('assignee', {}).get('login') if issue.get('assignee') else None,
                'reporter': issue.get('user', {}).get('login'),
                'created_at': issue.get('created_at'),
                'updated_at': issue.get('updated_at'),
                'labels': [label.get('name') for label in issue.get('labels', [])],
                'repository': f"{owner}/{repo}",
                'content_hash': get_file_hash(full_content),
                'file_path': f"tickets/github/{owner}-{repo}/issue-{issue.get('number')}",
                'tags': ['ticket', 'github'] + [label.get('name') for label in issue.get('labels', [])],
                'technical_terms': extract_technical_terms(full_content),
                'complexity': self._estimate_github_complexity(issue),
                'difficulty': self._determine_github_difficulty(issue)
            }
        }
        documents.append(issue_doc)

        for comment in comments:
            comment_body = comment.get('body', '')
            if comment_body.strip():
                comment_doc = {
                    'content': sanitize_text(comment_body),
                    'metadata': {
                        'source_type': 'ticket_comment',
                        'ticket_id': f"#{issue.get('number')}",
                        'title': title,
                        'commenter': comment.get('user', {}).get('login'),
                        'created_at': comment.get('created_at'),
                        'updated_at': comment.get('updated_at'),
                        'repository': f"{owner}/{repo}",
                        'content_hash': get_file_hash(comment_body),
                        'file_path': f"tickets/github/{owner}-{repo}/issue-{issue.get('number')}/comment-{comment.get('id')}",
                        'tags': ['ticket_comment', 'github'],
                        'technical_terms': extract_technical_terms(comment_body),
                        'comment_type': self._classify_comment_type(comment_body)
                    }
                }
                documents.append(comment_doc)

        return documents


def fetch_tickets_quick(source: str = "mock", limit: int = 20, demo_mode: bool = False, user_id: str = None, scenario: str = None) -> List[Dict[str, Any]]:
    fetcher = TicketFetcher(demo_mode=demo_mode, user_id=user_id)
    import asyncio
    return asyncio.run(fetcher.fetch_tickets(source, limit, scenario=scenario))

if __name__ == "__main__":
    
    
    async def main():
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            demo_mode = '--demo' in sys.argv
            user_id = None
            scenario = None
            
            for i, arg in enumerate(sys.argv):
                if arg == '--user' and i + 1 < len(sys.argv):
                    user_id = sys.argv[i + 1]
                elif arg == '--scenario' and i + 1 < len(sys.argv):
                    scenario = sys.argv[i + 1]
            
            fetcher = TicketFetcher(demo_mode=demo_mode, user_id=user_id)
            
            if command == "fetch":
                source = "mock"
                limit = 10
                
                for i, arg in enumerate(sys.argv[2:], 2):
                    if not arg.startswith('--') and arg not in [user_id, scenario]:
                        if source == "mock":
                            source = arg
                        else:
                            try:
                                limit = int(arg)
                            except ValueError:
                                pass
                        break
                
                results = await fetcher.fetch_tickets(source, limit, scenario=scenario)
                print(f"Fetched {len(results)} ticket documents from {source}")
                
                if demo_mode:
                    print(f"Demo mode: {demo_mode}, Scenario: {scenario or 'default'}")
                
                for i, result in enumerate(results[:3]):
                    print(f"\nSample {i+1}:")
                    print(f"Type: {result['metadata']['source_type']}")
                    print(f"ID: {result['metadata']['ticket_id']}")
                    print(f"Title: {result['metadata']['title']}")
                    print(f"Status: {result['metadata']['status']}")
                    print(f"Demo: {result['metadata'].get('is_demo', False)}")
                    print(f"Content: {result['content'][:100]}...")
                    
            elif command == "demo":
                print("Available demo scenarios:")
                for scenario in fetcher.get_demo_scenarios():
                    print(f"  - {scenario}")
                    
            elif command == "stats":
                stats = fetcher.get_fetcher_stats()
                print("Ticket Fetcher Statistics:")
                print(json.dumps(stats, indent=2))
                
            else:
                print("Available commands:")
                print("  fetch [source] [limit] [--demo] [--user USER_ID] [--scenario SCENARIO] - Fetch tickets")
                print("  demo - Show available demo scenarios")
                print("  stats - Show fetcher capabilities")
        else:
            print("Usage: python ticket_fetcher.py [fetch|demo|stats] [options...]")
            print("Options:")
            print("  --demo              Enable demo mode")
            print("  --user USER_ID      Set user ID")
            print("  --scenario NAME     Set demo scenario (startup/enterprise/freelancer)")
    
    asyncio.run(main())
    
    