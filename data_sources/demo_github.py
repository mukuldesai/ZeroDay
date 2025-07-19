import os
import yaml
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.helpers import get_file_hash, sanitize_text, extract_technical_terms

class DemoGitHub:
    
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
    
    def generate_repository_data(self, scenario: str = None, repo_name: str = None) -> Dict[str, Any]:
        scenario = scenario or 'startup'
        repo_name = repo_name or f"demo-{scenario}-app"
        
        return {
            'repository': self._get_repository_info(scenario, repo_name),
            'pull_requests': self._generate_pull_requests(scenario),
            'issues': self._generate_issues(scenario),
            'commits': self._generate_commits(scenario),
            'branches': self._generate_branches(scenario),
            'releases': self._generate_releases(scenario)
        }
    
    def _get_repository_info(self, scenario: str, repo_name: str) -> Dict[str, Any]:
        repo_descriptions = {
            'startup': f"Modern web application built with FastAPI and React. Features user authentication, real-time updates, and responsive design.",
            'enterprise': f"Enterprise-grade microservices platform with Kubernetes deployment, monitoring, and CI/CD pipeline.",
            'freelancer': f"Custom website solution with optimized performance, SEO-friendly design, and modern UI/UX."
        }
        
        return {
            'name': repo_name,
            'full_name': f"demo-org/{repo_name}",
            'description': repo_descriptions.get(scenario, repo_descriptions['startup']),
            'private': False,
            'html_url': f"https://github.com/demo-org/{repo_name}",
            'clone_url': f"https://github.com/demo-org/{repo_name}.git",
            'created_at': (datetime.now() - timedelta(days=180)).isoformat(),
            'updated_at': datetime.now().isoformat(),
            'language': 'TypeScript',
            'size': 15420,
            'stargazers_count': 247 if scenario == 'enterprise' else 89,
            'watchers_count': 34 if scenario == 'enterprise' else 12,
            'forks_count': 18 if scenario == 'enterprise' else 7,
            'open_issues_count': 8,
            'topics': self._get_repository_topics(scenario),
            'license': {'key': 'mit', 'name': 'MIT License'},
            'default_branch': 'main'
        }
    
    def _get_repository_topics(self, scenario: str) -> List[str]:
        topic_mapping = {
            'startup': ['webapp', 'react', 'fastapi', 'authentication', 'realtime'],
            'enterprise': ['microservices', 'kubernetes', 'monitoring', 'cicd', 'scalable'],
            'freelancer': ['website', 'seo', 'performance', 'responsive', 'modern']
        }
        return topic_mapping.get(scenario, topic_mapping['startup'])
    
    def _generate_pull_requests(self, scenario: str) -> List[Dict[str, Any]]:
        if scenario == 'enterprise':
            return self._enterprise_pull_requests()
        elif scenario == 'freelancer':
            return self._freelancer_pull_requests()
        else:
            return self._startup_pull_requests()
    
    def _startup_pull_requests(self) -> List[Dict[str, Any]]:
        base_date = datetime.now()
        
        return [
            {
                'number': 42,
                'title': 'Implement JWT authentication system',
                'body': '''## Overview
This PR implements a complete JWT-based authentication system for the application.

## Changes Made
- 🔐 Added JWT token generation and validation
- 🛡️ Implemented password hashing with bcrypt
- 📝 Created login and registration endpoints
- 🔄 Added token refresh mechanism
- ✅ Comprehensive test coverage

## Testing
- Unit tests for auth functions
- Integration tests for API endpoints
- Manual testing with Postman

## Security Considerations
- Secure password hashing
- Token expiration handling
- Input validation and sanitization

Closes #23
''',
                'state': 'merged',
                'user': {'login': 'sarah-dev', 'avatar_url': 'https://github.com/sarah-dev.png'},
                'assignee': {'login': 'tech-lead'},
                'labels': [
                    {'name': 'feature', 'color': '0075ca'},
                    {'name': 'security', 'color': 'd73a4a'},
                    {'name': 'backend', 'color': '0e8a16'}
                ],
                'created_at': (base_date - timedelta(days=5)).isoformat(),
                'updated_at': (base_date - timedelta(days=2)).isoformat(),
                'merged_at': (base_date - timedelta(days=2)).isoformat(),
                'head': {'ref': 'feature/jwt-auth'},
                'base': {'ref': 'main'},
                'additions': 387,
                'deletions': 42,
                'changed_files': 12,
                'commits': 8
            },
            {
                'number': 41,
                'title': 'Fix responsive design issues on mobile',
                'body': '''## Problem
Dashboard components were breaking on mobile devices below 768px width.

## Solution
- 📱 Fixed navigation menu overlap
- 🎨 Improved form layouts for small screens
- 📊 Made charts responsive
- 🔧 Added proper media queries

## Screenshots
Before/after screenshots attached showing the improvements.

## Testing
- Tested on iPhone 12, Samsung Galaxy S21
- Chrome DevTools mobile simulation
- Responsive design validation
''',
                'state': 'open',
                'user': {'login': 'mike-frontend', 'avatar_url': 'https://github.com/mike-frontend.png'},
                'assignee': {'login': 'mike-frontend'},
                'labels': [
                    {'name': 'bug', 'color': 'd73a4a'},
                    {'name': 'frontend', 'color': '1d76db'},
                    {'name': 'mobile', 'color': 'fbca04'}
                ],
                'created_at': (base_date - timedelta(days=3)).isoformat(),
                'updated_at': (base_date - timedelta(hours=6)).isoformat(),
                'merged_at': None,
                'head': {'ref': 'fix/mobile-responsive'},
                'base': {'ref': 'main'},
                'additions': 156,
                'deletions': 89,
                'changed_files': 7,
                'commits': 4
            }
        ]
    
    def _enterprise_pull_requests(self) -> List[Dict[str, Any]]:
        base_date = datetime.now()
        
        return [
            {
                'number': 128,
                'title': 'Implement circuit breaker pattern for external services',
                'body': '''## Architecture Enhancement
This PR introduces the circuit breaker pattern to improve system resilience when dealing with external service failures.

## Implementation Details
- 🔄 Circuit breaker with configurable thresholds
- 📊 Metrics collection for monitoring
- ⚡ Fallback mechanisms for critical operations
- 🎛️ Admin dashboard for circuit breaker status
- 📈 Integration with Prometheus monitoring

## Configuration
- Failure threshold: 5 consecutive failures
- Recovery timeout: 30 seconds
- Half-open state testing: 3 requests

## Testing Strategy
- Unit tests with mocked service failures
- Integration tests with actual service disruption
- Load testing to verify performance impact
- Chaos engineering validation

## Monitoring
- Circuit breaker state changes logged
- Metrics exported to Prometheus
- Alerts configured for prolonged open states

This is part of our Q2 reliability improvement initiative.
''',
                'state': 'merged',
                'user': {'login': 'principal-engineer', 'avatar_url': 'https://github.com/principal-engineer.png'},
                'assignee': {'login': 'reliability-team'},
                'labels': [
                    {'name': 'enhancement', 'color': '0075ca'},
                    {'name': 'reliability', 'color': '0e8a16'},
                    {'name': 'architecture', 'color': '5319e7'}
                ],
                'created_at': (base_date - timedelta(days=8)).isoformat(),
                'updated_at': (base_date - timedelta(days=1)).isoformat(),
                'merged_at': (base_date - timedelta(days=1)).isoformat(),
                'head': {'ref': 'feature/circuit-breaker'},
                'base': {'ref': 'main'},
                'additions': 892,
                'deletions': 134,
                'changed_files': 23,
                'commits': 15
            }
        ]
    
    def _freelancer_pull_requests(self) -> List[Dict[str, Any]]:
        base_date = datetime.now()
        
        return [
            {
                'number': 15,
                'title': 'Add dark mode theme with smooth transitions',
                'body': '''## Client Feature Request
Client requested dark mode option for better user experience during evening hours.

## Implementation
- 🌙 Dark theme with carefully chosen color palette
- 🎨 Smooth CSS transitions between themes
- 💾 Theme preference saved in localStorage
- ♿ Accessibility compliance with proper contrast ratios
- 📱 Mobile-optimized dark theme

## Design Choices
- Used CSS custom properties for theme variables
- Ensured WCAG AA compliance for contrast
- Added subtle animations for theme switching
- Consistent styling across all components

## Client Feedback
"The dark mode looks absolutely gorgeous! Our users are going to love this."

## Browser Support
- Chrome, Firefox, Safari, Edge
- Mobile browsers on iOS and Android
''',
                'state': 'merged',
                'user': {'login': 'freelance-dev', 'avatar_url': 'https://github.com/freelance-dev.png'},
                'assignee': {'login': 'freelance-dev'},
                'labels': [
                    {'name': 'feature', 'color': '0075ca'},
                    {'name': 'ui', 'color': '1d76db'},
                    {'name': 'client-request', 'color': 'fbca04'}
                ],
                'created_at': (base_date - timedelta(days=4)).isoformat(),
                'updated_at': (base_date - timedelta(days=1)).isoformat(),
                'merged_at': (base_date - timedelta(days=1)).isoformat(),
                'head': {'ref': 'feature/dark-mode'},
                'base': {'ref': 'main'},
                'additions': 234,
                'deletions': 67,
                'changed_files': 9,
                'commits': 6
            }
        ]
    
    def _generate_issues(self, scenario: str) -> List[Dict[str, Any]]:
        base_date = datetime.now()
        
        common_issues = [
            {
                'number': 87,
                'title': 'Add comprehensive API documentation',
                'body': '''We need to create detailed API documentation for all endpoints to help new developers understand the system.

**Requirements:**
- OpenAPI/Swagger specification
- Interactive documentation with examples
- Authentication flow documentation
- Error code reference
- Rate limiting information

**Acceptance Criteria:**
- [ ] All endpoints documented
- [ ] Examples for each endpoint
- [ ] Error responses documented
- [ ] Authentication explained
- [ ] Hosted documentation site

This will significantly improve developer experience and reduce onboarding time.
''',
                'state': 'open',
                'user': {'login': 'tech-writer', 'avatar_url': 'https://github.com/tech-writer.png'},
                'assignee': None,
                'labels': [
                    {'name': 'documentation', 'color': '0075ca'},
                    {'name': 'good first issue', 'color': '7057ff'},
                    {'name': 'help wanted', 'color': '008672'}
                ],
                'created_at': (base_date - timedelta(days=12)).isoformat(),
                'updated_at': (base_date - timedelta(days=3)).isoformat(),
                'comments': 5
            },
            {
                'number': 86,
                'title': 'Memory leak in data processing module',
                'body': '''**Bug Report**

**Environment:**
- Version: 2.1.3
- OS: Ubuntu 20.04
- Node.js: 18.15.0

**Description:**
Memory usage continuously increases during large data processing operations and never gets released.

**Steps to Reproduce:**
1. Start the application
2. Process a dataset with 10k+ records
3. Monitor memory usage
4. Observe memory not being freed after processing

**Expected Behavior:**
Memory should be released after processing completes.

**Actual Behavior:**
Memory usage grows and stays high, eventually causing OOM errors.

**Additional Context:**
This issue started appearing after the recent optimization update in v2.1.0.
''',
                'state': 'open',
                'user': {'login': 'performance-tester', 'avatar_url': 'https://github.com/performance-tester.png'},
                'assignee': {'login': 'backend-team'},
                'labels': [
                    {'name': 'bug', 'color': 'd73a4a'},
                    {'name': 'performance', 'color': 'fbca04'},
                    {'name': 'high priority', 'color': 'd93f0b'}
                ],
                'created_at': (base_date - timedelta(days=8)).isoformat(),
                'updated_at': (base_date - timedelta(hours=12)).isoformat(),
                'comments': 8
            }
        ]
        
        return common_issues
    
    def _generate_commits(self, scenario: str) -> List[Dict[str, Any]]:
        base_date = datetime.now()
        
        commits = [
            {
                'sha': 'a1b2c3d4e5f6789012345678901234567890abcd',
                'commit': {
                    'message': 'feat: add JWT authentication middleware\n\n- Implement token validation\n- Add user context to requests\n- Handle token expiration gracefully',
                    'author': {
                        'name': 'Sarah Developer',
                        'email': 'sarah@example.com',
                        'date': (base_date - timedelta(days=2)).isoformat()
                    }
                },
                'author': {'login': 'sarah-dev', 'avatar_url': 'https://github.com/sarah-dev.png'},
                'html_url': 'https://github.com/demo-org/demo-app/commit/a1b2c3d4e5f6789012345678901234567890abcd'
            },
            {
                'sha': 'b2c3d4e5f6789012345678901234567890abcdef1',
                'commit': {
                    'message': 'fix: resolve mobile responsive issues\n\n- Fix navigation menu overlap\n- Improve form layouts\n- Add proper media queries',
                    'author': {
                        'name': 'Mike Frontend',
                        'email': 'mike@example.com',
                        'date': (base_date - timedelta(days=1)).isoformat()
                    }
                },
                'author': {'login': 'mike-frontend', 'avatar_url': 'https://github.com/mike-frontend.png'},
                'html_url': 'https://github.com/demo-org/demo-app/commit/b2c3d4e5f6789012345678901234567890abcdef1'
            }
        ]
        
        return commits
    
    def _generate_branches(self, scenario: str) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'main',
                'commit': {'sha': 'a1b2c3d4e5f6789012345678901234567890abcd'},
                'protected': True
            },
            {
                'name': 'develop',
                'commit': {'sha': 'b2c3d4e5f6789012345678901234567890abcdef1'},
                'protected': True
            },
            {
                'name': 'feature/user-dashboard',
                'commit': {'sha': 'c3d4e5f6789012345678901234567890abcdef12'},
                'protected': False
            },
            {
                'name': 'fix/mobile-responsive',
                'commit': {'sha': 'd4e5f6789012345678901234567890abcdef123'},
                'protected': False
            }
        ]
    
    def _generate_releases(self, scenario: str) -> List[Dict[str, Any]]:
        base_date = datetime.now()
        
        return [
            {
                'tag_name': 'v2.1.0',
                'name': 'Version 2.1.0 - Authentication & Security',
                'body': '''## 🚀 New Features
- JWT-based authentication system
- User registration and login
- Password reset functionality
- Rate limiting for API endpoints

## 🐛 Bug Fixes
- Fixed memory leak in data processing
- Resolved mobile responsive issues
- Fixed CORS configuration

## 🔧 Improvements
- Enhanced error handling
- Better logging and monitoring
- Performance optimizations

## 📦 Dependencies
- Updated React to 18.2.0
- Updated FastAPI to 0.95.0
- Added bcrypt for password hashing

## 🔄 Migration Notes
No breaking changes in this release.
''',
                'draft': False,
                'prerelease': False,
                'created_at': (base_date - timedelta(days=14)).isoformat(),
                'published_at': (base_date - timedelta(days=14)).isoformat(),
                'author': {'login': 'tech-lead'},
                'assets': []
            },
            {
                'tag_name': 'v2.0.1',
                'name': 'Version 2.0.1 - Hotfix',
                'body': '''## 🐛 Hotfix
- Critical security patch for authentication
- Fixed API rate limiting bypass
- Resolved database connection pool issues

## 📦 Dependencies
- Updated jwt library to latest secure version
''',
                'draft': False,
                'prerelease': False,
                'created_at': (base_date - timedelta(days=21)).isoformat(),
                'published_at': (base_date - timedelta(days=21)).isoformat(),
                'author': {'login': 'security-team'},
                'assets': []
            }
        ]
    
    def format_as_documents(self, github_data: Dict[str, Any], scenario: str = None) -> List[Dict[str, Any]]:
        documents = []
        base_date = datetime.now()
        
        for pr in github_data.get('pull_requests', []):
            doc = {
                'content': sanitize_text(pr['body']),
                'metadata': {
                    'source_type': 'pull_request',
                    'pr_number': pr['number'],
                    'pr_title': pr['title'],
                    'pr_state': pr['state'],
                    'pr_url': f"https://github.com/demo-org/demo-app/pull/{pr['number']}",
                    'repository': 'demo-org/demo-app',
                    'author': pr['user']['login'],
                    'created_at': pr['created_at'],
                    'updated_at': pr['updated_at'],
                    'merged_at': pr.get('merged_at'),
                    'content_hash': get_file_hash(pr['body']),
                    'tags': ['pull_request', pr['state']] + [label['name'] for label in pr.get('labels', [])],
                    'file_path': f"prs/demo-org-demo-app/pr-{pr['number']}",
                    'changes': {
                        'additions': pr.get('additions', 0),
                        'deletions': pr.get('deletions', 0),
                        'changed_files': pr.get('changed_files', 0),
                        'commits': pr.get('commits', 0),
                        'merged': pr['state'] == 'merged'
                    },
                    'technical_terms': extract_technical_terms(pr['body']),
                    'complexity': 'medium',
                    'pr_type': 'feature',
                    'is_demo': True,
                    'demo_scenario': scenario or 'default',
                    'user_id': self.user_id,
                    'demo_note': 'This is synthetic demo data for showcase purposes'
                }
            }
            documents.append(doc)
        
        for issue in github_data.get('issues', []):
            doc = {
                'content': sanitize_text(issue['body']),
                'metadata': {
                    'source_type': 'github_issue',
                    'issue_number': issue['number'],
                    'title': issue['title'],
                    'state': issue['state'],
                    'repository': 'demo-org/demo-app',
                    'author': issue['user']['login'],
                    'assignee': issue.get('assignee', {}).get('login') if issue.get('assignee') else None,
                    'created_at': issue['created_at'],
                    'updated_at': issue['updated_at'],
                    'labels': [label['name'] for label in issue.get('labels', [])],
                    'comments_count': issue.get('comments', 0),
                    'content_hash': get_file_hash(issue['body']),
                    'file_path': f"issues/demo-org-demo-app/issue-{issue['number']}",
                    'tags': ['github_issue', issue['state']] + [label['name'] for label in issue.get('labels', [])],
                    'technical_terms': extract_technical_terms(issue['body']),
                    'is_demo': True,
                    'demo_scenario': scenario or 'default',
                    'user_id': self.user_id,
                    'demo_note': 'This is synthetic demo data for showcase purposes'
                }
            }
            documents.append(doc)
        
        return documents
    
    def get_repository_stats(self, scenario: str = None) -> Dict[str, Any]:
        scenario = scenario or 'startup'
        repo_data = self.generate_repository_data(scenario)
        
        return {
            'repository_info': repo_data['repository'],
            'pull_requests_count': len(repo_data['pull_requests']),
            'issues_count': len(repo_data['issues']),
            'commits_count': len(repo_data['commits']),
            'branches_count': len(repo_data['branches']),
            'releases_count': len(repo_data['releases']),
            'total_documents': len(repo_data['pull_requests']) + len(repo_data['issues'])
        }


def generate_github_demo_quick(scenario: str = 'startup', user_id: str = None) -> Dict[str, Any]:
    demo_github = DemoGitHub(user_id=user_id)
    return demo_github.generate_repository_data(scenario)

if __name__ == "__main__":
    import sys
    import json
    
    def main():
        if len(sys.argv) > 1:
            command = sys.argv[1]
            demo_github = DemoGitHub()
            
            if command == "generate":
                scenario = sys.argv[2] if len(sys.argv) > 2 else 'startup'
                data = demo_github.generate_repository_data(scenario)
                
                print(f"Generated GitHub demo data for {scenario} scenario:")
                print(f"  Pull Requests: {len(data['pull_requests'])}")
                print(f"  Issues: {len(data['issues'])}")
                print(f"  Commits: {len(data['commits'])}")
                print(f"  Branches: {len(data['branches'])}")
                print(f"  Releases: {len(data['releases'])}")
                
            elif command == "stats":
                scenario = sys.argv[2] if len(sys.argv) > 2 else 'startup'
                stats = demo_github.get_repository_stats(scenario)
                print("GitHub Demo Statistics:")
                print(json.dumps(stats, indent=2))
                
            elif command == "documents":
                scenario = sys.argv[2] if len(sys.argv) > 2 else 'startup'
                github_data = demo_github.generate_repository_data(scenario)
                documents = demo_github.format_as_documents(github_data, scenario)
                
                print(f"Generated {len(documents)} document objects:")
                for i, doc in enumerate(documents[:3]):
                    print(f"\nSample {i+1}:")
                    print(f"  Type: {doc['metadata']['source_type']}")
                    print(f"  Title: {doc['metadata'].get('pr_title') or doc['metadata'].get('title')}")
                    print(f"  Content: {doc['content'][:100]}...")
                    
            else:
                print("Available commands:")
                print("  generate [scenario] - Generate GitHub demo data")
                print("  stats [scenario] - Show repository statistics")
                print("  documents [scenario] - Generate formatted documents")
        else:
            print("Usage: python demo_github.py [generate|stats|documents] [scenario]")
            print("Scenarios: startup, enterprise, freelancer")
    
    main()