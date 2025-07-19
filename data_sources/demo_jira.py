import os
import yaml
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.helpers import get_file_hash, sanitize_text, extract_technical_terms

class DemoJira:
    
    def __init__(self, config_path: str = None, user_id: str = None):
        self.config = self._load_config(config_path)
        self.user_id = user_id or "demo_user"
        
    def _load_config(self, config_path: str = None) -> Dict:
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "demo_settings.yaml"
            )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {'scenarios': ['startup', 'enterprise', 'freelancer']}
    
    def generate_project_data(self, scenario: str = None, project_key: str = None) -> Dict[str, Any]:
        scenario = scenario or 'startup'
        project_key = project_key or self._get_project_key(scenario)
        
        return {
            'project': self._get_project_info(scenario, project_key),
            'users': self._generate_users(scenario),
            'issue_types': self._generate_issue_types(scenario),
            'statuses': self._generate_statuses(scenario),
            'priorities': self._generate_priorities(),
            'components': self._generate_components(scenario),
            'issues': self._generate_issues(scenario, project_key),
            'comments': self._generate_comments(scenario)
        }
    
    def _get_project_key(self, scenario: str) -> str:
        project_keys = {
            'startup': 'DEMO',
            'enterprise': 'CORP',
            'freelancer': 'CLIENT'
        }
        return project_keys.get(scenario, 'DEMO')
    
    def _get_project_info(self, scenario: str, project_key: str) -> Dict[str, Any]:
        project_names = {
            'startup': 'Demo Startup Project',
            'enterprise': 'Enterprise Platform',
            'freelancer': 'Client Website Project'
        }
        
        return {
            'key': project_key,
            'name': project_names.get(scenario, project_names['startup']),
            'description': f'Demo project for {scenario} scenario showcasing typical development workflow',
            'lead': {'displayName': 'Project Lead', 'emailAddress': 'lead@example.com'},
            'projectTypeKey': 'software',
            'url': f'https://demo.atlassian.net/browse/{project_key}',
            'created': (datetime.now() - timedelta(days=180)).isoformat(),
            'updated': datetime.now().isoformat()
        }
    
    def _generate_users(self, scenario: str) -> List[Dict[str, Any]]:
        if scenario == 'enterprise':
            return self._enterprise_users()
        elif scenario == 'freelancer':
            return self._freelancer_users()
        else:
            return self._startup_users()
    
    def _startup_users(self) -> List[Dict[str, Any]]:
        return [
            {
                'accountId': '1001',
                'displayName': 'Sarah Chen',
                'emailAddress': 'sarah@startup.com',
                'active': True,
                'accountType': 'atlassian'
            },
            {
                'accountId': '1002',
                'displayName': 'Mike Rodriguez',
                'emailAddress': 'mike@startup.com',
                'active': True,
                'accountType': 'atlassian'
            },
            {
                'accountId': '1003',
                'displayName': 'Jennifer Kim',
                'emailAddress': 'jen@startup.com',
                'active': True,
                'accountType': 'atlassian'
            },
            {
                'accountId': '1004',
                'displayName': 'Alex Thompson',
                'emailAddress': 'alex@startup.com',
                'active': True,
                'accountType': 'atlassian'
            }
        ]
    
    def _enterprise_users(self) -> List[Dict[str, Any]]:
        return [
            {
                'accountId': '2001',
                'displayName': 'David Wilson',
                'emailAddress': 'david.wilson@enterprise.com',
                'active': True,
                'accountType': 'atlassian'
            },
            {
                'accountId': '2002',
                'displayName': 'Lisa Garcia',
                'emailAddress': 'lisa.garcia@enterprise.com',
                'active': True,
                'accountType': 'atlassian'
            },
            {
                'accountId': '2003',
                'displayName': 'Robert Chen',
                'emailAddress': 'robert.chen@enterprise.com',
                'active': True,
                'accountType': 'atlassian'
            }
        ]
    
    def _freelancer_users(self) -> List[Dict[str, Any]]:
        return [
            {
                'accountId': '3001',
                'displayName': 'Emma Johnson',
                'emailAddress': 'emma@freelancer.com',
                'active': True,
                'accountType': 'atlassian'
            },
            {
                'accountId': '3002',
                'displayName': 'John Smith',
                'emailAddress': 'john@client.com',
                'active': True,
                'accountType': 'customer'
            }
        ]
    
    def _generate_issue_types(self, scenario: str) -> List[Dict[str, Any]]:
        if scenario == 'enterprise':
            return [
                {'id': '1', 'name': 'Epic', 'description': 'Large body of work', 'iconUrl': 'epic.png'},
                {'id': '2', 'name': 'Story', 'description': 'User story', 'iconUrl': 'story.png'},
                {'id': '3', 'name': 'Task', 'description': 'Generic task', 'iconUrl': 'task.png'},
                {'id': '4', 'name': 'Bug', 'description': 'Software defect', 'iconUrl': 'bug.png'},
                {'id': '5', 'name': 'Incident', 'description': 'Production incident', 'iconUrl': 'incident.png'}
            ]
        else:
            return [
                {'id': '1', 'name': 'Story', 'description': 'User story', 'iconUrl': 'story.png'},
                {'id': '2', 'name': 'Task', 'description': 'Generic task', 'iconUrl': 'task.png'},
                {'id': '3', 'name': 'Bug', 'description': 'Software defect', 'iconUrl': 'bug.png'},
                {'id': '4', 'name': 'Feature', 'description': 'New feature', 'iconUrl': 'feature.png'}
            ]
    
    def _generate_statuses(self, scenario: str) -> List[Dict[str, Any]]:
        return [
            {'id': '1', 'name': 'To Do', 'statusCategory': {'key': 'new', 'name': 'To Do'}},
            {'id': '2', 'name': 'In Progress', 'statusCategory': {'key': 'indeterminate', 'name': 'In Progress'}},
            {'id': '3', 'name': 'Code Review', 'statusCategory': {'key': 'indeterminate', 'name': 'In Progress'}},
            {'id': '4', 'name': 'Testing', 'statusCategory': {'key': 'indeterminate', 'name': 'In Progress'}},
            {'id': '5', 'name': 'Done', 'statusCategory': {'key': 'done', 'name': 'Done'}}
        ]
    
    def _generate_priorities(self) -> List[Dict[str, Any]]:
        return [
            {'id': '1', 'name': 'Highest', 'iconUrl': 'highest.png'},
            {'id': '2', 'name': 'High', 'iconUrl': 'high.png'},
            {'id': '3', 'name': 'Medium', 'iconUrl': 'medium.png'},
            {'id': '4', 'name': 'Low', 'iconUrl': 'low.png'},
            {'id': '5', 'name': 'Lowest', 'iconUrl': 'lowest.png'}
        ]
    
    def _generate_components(self, scenario: str) -> List[Dict[str, Any]]:
        if scenario == 'enterprise':
            return [
                {'id': '1', 'name': 'Authentication Service', 'description': 'User authentication and authorization'},
                {'id': '2', 'name': 'API Gateway', 'description': 'External API routing and rate limiting'},
                {'id': '3', 'name': 'User Service', 'description': 'User management microservice'},
                {'id': '4', 'name': 'Infrastructure', 'description': 'Kubernetes and deployment'},
                {'id': '5', 'name': 'Monitoring', 'description': 'Observability and alerting'}
            ]
        elif scenario == 'freelancer':
            return [
                {'id': '1', 'name': 'Frontend', 'description': 'User interface components'},
                {'id': '2', 'name': 'Backend', 'description': 'Server-side functionality'},
                {'id': '3', 'name': 'Design', 'description': 'UI/UX design work'}
            ]
        else:
            return [
                {'id': '1', 'name': 'Frontend', 'description': 'React frontend application'},
                {'id': '2', 'name': 'Backend', 'description': 'FastAPI backend service'},
                {'id': '3', 'name': 'Database', 'description': 'Database schema and queries'},
                {'id': '4', 'name': 'DevOps', 'description': 'Deployment and infrastructure'}
            ]
    
    def _generate_issues(self, scenario: str, project_key: str) -> List[Dict[str, Any]]:
        if scenario == 'enterprise':
            return self._enterprise_issues(project_key)
        elif scenario == 'freelancer':
            return self._freelancer_issues(project_key)
        else:
            return self._startup_issues(project_key)
    
    def _startup_issues(self, project_key: str) -> List[Dict[str, Any]]:
        base_date = datetime.now()
        
        return [
            {
                'key': f'{project_key}-101',
                'fields': {
                    'summary': 'Implement JWT authentication system',
                    'description': {
                        'type': 'doc',
                        'version': 1,
                        'content': [
                            {
                                'type': 'paragraph',
                                'content': [
                                    {'type': 'text', 'text': 'Need to implement a complete JWT-based authentication system for the application.'}
                                ]
                            },
                            {
                                'type': 'paragraph',
                                'content': [
                                    {'type': 'text', 'text': 'Requirements:'}
                                ]
                            },
                            {
                                'type': 'bulletList',
                                'content': [
                                    {'type': 'listItem', 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'User login and registration endpoints'}]}]},
                                    {'type': 'listItem', 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'JWT token generation and validation'}]}]},
                                    {'type': 'listItem', 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Password hashing with bcrypt'}]}]},
                                    {'type': 'listItem', 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Token refresh mechanism'}]}]}
                                ]
                            }
                        ]
                    },
                    'status': {'name': 'In Progress'},
                    'priority': {'name': 'High'},
                    'issuetype': {'name': 'Story'},
                    'assignee': {'displayName': 'Sarah Chen', 'emailAddress': 'sarah@startup.com'},
                    'reporter': {'displayName': 'Mike Rodriguez', 'emailAddress': 'mike@startup.com'},
                    'created': (base_date - timedelta(days=5)).isoformat(),
                    'updated': (base_date - timedelta(hours=2)).isoformat(),
                    'labels': ['authentication', 'security', 'backend'],
                    'components': [{'name': 'Backend'}],
                    'comment': {
                        'comments': [
                            {
                                'id': '1001',
                                'body': {
                                    'type': 'doc',
                                    'version': 1,
                                    'content': [
                                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Started implementing the JWT middleware. Using the jose library for token handling.'}]}
                                    ]
                                },
                                'author': {'displayName': 'Sarah Chen'},
                                'created': (base_date - timedelta(days=3)).isoformat(),
                                'updated': (base_date - timedelta(days=3)).isoformat()
                            }
                        ]
                    }
                }
            },
            {
                'key': f'{project_key}-102',
                'fields': {
                    'summary': 'Fix responsive design issues on mobile devices',
                    'description': {
                        'type': 'doc',
                        'version': 1,
                        'content': [
                            {
                                'type': 'paragraph',
                                'content': [
                                    {'type': 'text', 'text': 'The dashboard components are not displaying correctly on mobile devices with screen widths below 768px.'}
                                ]
                            },
                            {
                                'type': 'paragraph',
                                'content': [
                                    {'type': 'text', 'text': 'Issues identified:'}
                                ]
                            },
                            {
                                'type': 'bulletList',
                                'content': [
                                    {'type': 'listItem', 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Navigation menu overlaps main content'}]}]},
                                    {'type': 'listItem', 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Forms are cut off on small screens'}]}]},
                                    {'type': 'listItem', 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Charts do not resize properly'}]}]}
                                ]
                            }
                        ]
                    },
                    'status': {'name': 'To Do'},
                    'priority': {'name': 'Medium'},
                    'issuetype': {'name': 'Bug'},
                    'assignee': {'displayName': 'Alex Thompson', 'emailAddress': 'alex@startup.com'},
                    'reporter': {'displayName': 'Jennifer Kim', 'emailAddress': 'jen@startup.com'},
                    'created': (base_date - timedelta(days=2)).isoformat(),
                    'updated': (base_date - timedelta(hours=6)).isoformat(),
                    'labels': ['frontend', 'mobile', 'responsive'],
                    'components': [{'name': 'Frontend'}],
                    'comment': {'comments': []}
                }
            }
        ]
    
    def _enterprise_issues(self, project_key: str) -> List[Dict[str, Any]]:
        base_date = datetime.now()
        
        return [
            {
                'key': f'{project_key}-501',
                'fields': {
                    'summary': 'Migrate authentication service to microservices architecture',
                    'description': {
                        'type': 'doc',
                        'version': 1,
                        'content': [
                            {
                                'type': 'paragraph',
                                'content': [
                                    {'type': 'text', 'text': 'Phase 1 of microservices migration - extract authentication logic from monolith into dedicated service.'}
                                ]
                            },
                            {
                                'type': 'paragraph',
                                'content': [
                                    {'type': 'text', 'text': 'Key requirements:'}
                                ]
                            },
                            {
                                'type': 'bulletList',
                                'content': [
                                    {'type': 'listItem', 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Maintain backward compatibility during transition'}]}]},
                                    {'type': 'listItem', 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Implement circuit breaker pattern for resilience'}]}]},
                                    {'type': 'listItem', 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Set up monitoring and alerting'}]}]},
                                    {'type': 'listItem', 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Database migration strategy'}]}]}
                                ]
                            }
                        ]
                    },
                    'status': {'name': 'In Progress'},
                    'priority': {'name': 'Highest'},
                    'issuetype': {'name': 'Epic'},
                    'assignee': {'displayName': 'Robert Chen', 'emailAddress': 'robert.chen@enterprise.com'},
                    'reporter': {'displayName': 'David Wilson', 'emailAddress': 'david.wilson@enterprise.com'},
                    'created': (base_date - timedelta(days=14)).isoformat(),
                    'updated': (base_date - timedelta(hours=4)).isoformat(),
                    'labels': ['microservices', 'architecture', 'migration'],
                    'components': [{'name': 'Authentication Service'}, {'name': 'Infrastructure'}],
                    'comment': {
                        'comments': [
                            {
                                'id': '2001',
                                'body': {
                                    'type': 'doc',
                                    'version': 1,
                                    'content': [
                                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Completed database schema analysis. Planning to use event sourcing for data synchronization.'}]}
                                    ]
                                },
                                'author': {'displayName': 'Robert Chen'},
                                'created': (base_date - timedelta(days=7)).isoformat(),
                                'updated': (base_date - timedelta(days=7)).isoformat()
                            }
                        ]
                    }
                }
            }
        ]
    
    def _freelancer_issues(self, project_key: str) -> List[Dict[str, Any]]:
        base_date = datetime.now()
        
        return [
            {
                'key': f'{project_key}-201',
                'fields': {
                    'summary': 'Add dark mode theme with toggle',
                    'description': {
                        'type': 'doc',
                        'version': 1,
                        'content': [
                            {
                                'type': 'paragraph',
                                'content': [
                                    {'type': 'text', 'text': 'Client has requested a dark mode option for better user experience during evening hours.'}
                                ]
                            },
                            {
                                'type': 'paragraph',
                                'content': [
                                    {'type': 'text', 'text': 'Requirements:'}
                                ]
                            },
                            {
                                'type': 'bulletList',
                                'content': [
                                    {'type': 'listItem', 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Dark theme color palette'}]}]},
                                    {'type': 'listItem', 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Theme toggle button in header'}]}]},
                                    {'type': 'listItem', 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Persistence in localStorage'}]}]},
                                    {'type': 'listItem', 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Smooth transitions between themes'}]}]}
                                ]
                            }
                        ]
                    },
                    'status': {'name': 'Done'},
                    'priority': {'name': 'Medium'},
                    'issuetype': {'name': 'Feature'},
                    'assignee': {'displayName': 'Emma Johnson', 'emailAddress': 'emma@freelancer.com'},
                    'reporter': {'displayName': 'John Smith', 'emailAddress': 'john@client.com'},
                    'created': (base_date - timedelta(days=8)).isoformat(),
                    'updated': (base_date - timedelta(days=1)).isoformat(),
                    'labels': ['frontend', 'theme', 'ui'],
                    'components': [{'name': 'Frontend'}, {'name': 'Design'}],
                    'comment': {
                        'comments': [
                            {
                                'id': '3001',
                                'body': {
                                    'type': 'doc',
                                    'version': 1,
                                    'content': [
                                        {'type': 'paragraph', 'content': [{'type': 'text', 'text': 'Dark mode implementation completed! The color palette looks great and all accessibility requirements are met.'}]}
                                    ]
                                },
                                'author': {'displayName': 'Emma Johnson'},
                                'created': (base_date - timedelta(days=1)).isoformat(),
                                'updated': (base_date - timedelta(days=1)).isoformat()
                            }
                        ]
                    }
                }
            }
        ]
    
    def _generate_comments(self, scenario: str) -> List[Dict[str, Any]]:
        base_date = datetime.now()
        
        return [
            {
                'id': '1001',
                'body': 'Implementation looks good! Please make sure to add unit tests for the authentication middleware.',
                'author': {'displayName': 'Tech Lead', 'emailAddress': 'lead@example.com'},
                'created': (base_date - timedelta(hours=6)).isoformat(),
                'updated': (base_date - timedelta(hours=6)).isoformat(),
                'issue_key': 'DEMO-101'
            },
            {
                'id': '1002',
                'body': 'The mobile responsive fixes work great on my iPhone. Tested the form layouts and they look much better now.',
                'author': {'displayName': 'QA Tester', 'emailAddress': 'qa@example.com'},
                'created': (base_date - timedelta(hours=2)).isoformat(),
                'updated': (base_date - timedelta(hours=2)).isoformat(),
                'issue_key': 'DEMO-102'
            }
        ]
    
    def format_as_documents(self, jira_data: Dict[str, Any], scenario: str = None) -> List[Dict[str, Any]]:
        documents = []
        
        for issue in jira_data.get('issues', []):
            description = self._extract_adf_text(issue['fields']['description'])
            title = issue['fields']['summary']
            full_content = f"{title}. {description}"
            
            doc = {
                'content': sanitize_text(full_content),
                'metadata': {
                    'source_type': 'ticket',
                    'ticket_id': issue['key'],
                    'title': title,
                    'status': issue['fields']['status']['name'],
                    'priority': issue['fields']['priority']['name'],
                    'issue_type': issue['fields']['issuetype']['name'],
                    'assignee': issue['fields']['assignee']['displayName'] if issue['fields'].get('assignee') else None,
                    'reporter': issue['fields']['reporter']['displayName'] if issue['fields'].get('reporter') else None,
                    'created_at': issue['fields']['created'],
                    'updated_at': issue['fields']['updated'],
                    'labels': issue['fields'].get('labels', []),
                    'components': [c['name'] for c in issue['fields'].get('components', [])],
                    'content_hash': get_file_hash(full_content),
                    'file_path': f"tickets/jira/{issue['key']}",
                    'tags': ['ticket', 'jira'] + issue['fields'].get('labels', []),
                    'technical_terms': extract_technical_terms(full_content),
                    'complexity': self._estimate_complexity(issue['fields']),
                    'difficulty': self._determine_difficulty(issue['fields']),
                    'is_demo': True,
                    'demo_scenario': scenario or 'default',
                    'user_id': self.user_id,
                    'demo_note': 'This is synthetic demo data for showcase purposes'
                }
            }
            documents.append(doc)
            
            for comment in issue['fields'].get('comment', {}).get('comments', []):
                comment_text = self._extract_adf_text(comment['body'])
                if comment_text.strip():
                    comment_doc = {
                        'content': sanitize_text(comment_text),
                        'metadata': {
                            'source_type': 'ticket_comment',
                            'ticket_id': issue['key'],
                            'title': title,
                            'commenter': comment['author']['displayName'],
                            'created_at': comment['created'],
                            'updated_at': comment['updated'],
                            'content_hash': get_file_hash(comment_text),
                            'file_path': f"tickets/jira/{issue['key']}/comment-{comment['id']}",
                            'tags': ['ticket_comment', 'jira'],
                            'technical_terms': extract_technical_terms(comment_text),
                            'comment_type': self._classify_comment_type(comment_text),
                            'is_demo': True,
                            'demo_scenario': scenario or 'default',
                            'user_id': self.user_id,
                            'demo_note': 'This is synthetic demo data for showcase purposes'
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
    
    def _estimate_complexity(self, fields: Dict) -> str:
        issue_type = fields.get('issuetype', {}).get('name', '').lower()
        priority = fields.get('priority', {}).get('name', '').lower()
        
        if 'epic' in issue_type or priority in ['highest', 'critical']:
            return 'high'
        elif 'story' in issue_type or priority == 'high':
            return 'medium'
        else:
            return 'low'
    
    def _determine_difficulty(self, fields: Dict) -> str:
        components = [c.get('name', '').lower() for c in fields.get('components', [])]
        labels = [label.lower() for label in fields.get('labels', [])]
        
        if any(comp in ['infrastructure', 'architecture', 'microservices'] for comp in components):
            return 'advanced'
        elif any(label in ['security', 'migration', 'backend'] for label in labels):
            return 'intermediate'
        else:
            return 'beginner'
    
    def _classify_comment_type(self, comment_text: str) -> str:
        text_lower = comment_text.lower()
        
        if any(word in text_lower for word in ['completed', 'done', 'finished']):
            return 'update'
        elif any(word in text_lower for word in ['looks good', 'approved', 'lgtm']):
            return 'approval'
        elif '?' in text_lower or 'question' in text_lower:
            return 'question'
        elif any(word in text_lower for word in ['suggest', 'recommend', 'consider']):
            return 'suggestion'
        else:
            return 'discussion'
    
    def get_project_stats(self, scenario: str = None) -> Dict[str, Any]:
        scenario = scenario or 'startup'
        jira_data = self.generate_project_data(scenario)
        
        return {
            'project_info': jira_data['project'],
            'users_count': len(jira_data['users']),
            'issue_types_count': len(jira_data['issue_types']),
            'components_count': len(jira_data['components']),
            'issues_count': len(jira_data['issues']),
            'comments_count': len(jira_data['comments']),
            'total_documents': len(jira_data['issues']) + len(jira_data['comments'])
        }


def generate_jira_demo_quick(scenario: str = 'startup', user_id: str = None) -> Dict[str, Any]:
    demo_jira = DemoJira(user_id=user_id)
    return demo_jira.generate_project_data(scenario)

if __name__ == "__main__":
    import sys
    import json
    
    def main():
        if len(sys.argv) > 1:
            command = sys.argv[1]
            demo_jira = DemoJira()
            
            if command == "generate":
                scenario = sys.argv[2] if len(sys.argv) > 2 else 'startup'
                data = demo_jira.generate_project_data(scenario)
                
                print(f"Generated Jira demo data for {scenario} scenario:")
                print(f"  Users: {len(data['users'])}")
                print(f"  Issue Types: {len(data['issue_types'])}")
                print(f"  Components: {len(data['components'])}")
                print(f"  Issues: {len(data['issues'])}")
                print(f"  Comments: {len(data['comments'])}")
                
            elif command == "stats":
                scenario = sys.argv[2] if len(sys.argv) > 2 else 'startup'
                stats = demo_jira.get_project_stats(scenario)
                print("Jira Demo Statistics:")
                print(json.dumps(stats, indent=2))
                
            elif command == "documents":
                scenario = sys.argv[2] if len(sys.argv) > 2 else 'startup'
                jira_data = demo_jira.generate_project_data(scenario)
                documents = demo_jira.format_as_documents(jira_data, scenario)
                
                print(f"Generated {len(documents)} document objects:")
                for i, doc in enumerate(documents[:3]):
                    print(f"\nSample {i+1}:")
                    print(f"  Type: {doc['metadata']['source_type']}")
                    print(f"  ID: {doc['metadata']['ticket_id']}")
                    print(f"  Title: {doc['metadata']['title']}")
                    print(f"  Status: {doc['metadata']['status']}")
                    print(f"  Content: {doc['content'][:100]}...")
                    
            else:
                print("Available commands:")
                print("  generate [scenario] - Generate Jira demo data")
                print("  stats [scenario] - Show project statistics")
                print("  documents [scenario] - Generate formatted documents")
        else:
            print("Usage: python demo_jira.py [generate|stats|documents] [scenario]")
            print("Scenarios: startup, enterprise, freelancer")
    
    main()