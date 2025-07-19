import os
import yaml
import httpx
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

class PRFetcher:
    
    def __init__(self, config_path: str = None, demo_mode: bool = False, user_id: str = None):
        self.config = self._load_config(config_path)
        self.demo_mode = demo_mode
        self.user_id = user_id or "demo_user"
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = self._setup_headers()
        
        if self.demo_mode:
            self.demo_config = self._load_demo_config()
            logger.info(f"PRFetcher initialized in DEMO mode for user: {self.user_id}")
        else:
            logger.info(f"PRFetcher initialized in REAL mode for user: {self.user_id}")
        
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
    
    def _setup_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ZeroDay-Onboarding-Agent"
        }
        
        if self.github_token and not self.demo_mode:
            headers["Authorization"] = f"token {self.github_token}"
        
        return headers
    
    async def fetch_pull_requests(
        self, 
        repo_url: str = None, 
        limit: int = None,
        state: str = "all",
        days_back: int = 90,
        scenario: str = None
    ) -> List[Dict[str, Any]]:
        
        if self.demo_mode:
            return await self._fetch_demo_prs(scenario, limit)
        else:
            return await self._fetch_real_prs(repo_url, limit, state, days_back)
    
    async def _fetch_demo_prs(self, scenario: str = None, limit: int = None) -> List[Dict[str, Any]]:
        logger.info(f"Generating DEMO PRs for scenario: {scenario or 'default'}")
        
        if not limit:
            limit = 10
        
        demo_prs = self._generate_synthetic_prs(scenario, limit)
        
        documents = []
        for pr_data in demo_prs:
            pr_documents = self._process_demo_pr_data(pr_data, scenario)
            documents.extend(pr_documents)
        
        for doc in documents:
            doc['metadata'].update({
                'is_demo': True,
                'demo_scenario': scenario or 'default',
                'user_id': self.user_id,
                'demo_note': 'This is synthetic demo data for showcase purposes'
            })
        
        logger.info(f"Generated {len(documents)} DEMO PR documents")
        return documents
    
    async def _fetch_real_prs(self, repo_url: str = None, limit: int = None, state: str = "all", days_back: int = 90) -> List[Dict[str, Any]]:
        if not repo_url:
            repo_url = self.config['data_sources']['github']['repo_url']
        
        if not limit:
            limit = self.config['data_sources']['github']['pr_limit']
        
        owner, repo = self._parse_repo_url(repo_url)
        if not owner or not repo:
            logger.error(f"Invalid repository URL: {repo_url}")
            return []
        
        logger.info(f"Fetching PRs from {owner}/{repo} (limit: {limit}, state: {state})")
        
        documents = []
        
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
                prs = await self._fetch_prs_list(client, owner, repo, state, limit, days_back)
                
                for pr in prs:
                    try:
                        pr_details = await self._fetch_pr_details(client, owner, repo, pr['number'])
                        reviews = await self._fetch_pr_reviews(client, owner, repo, pr['number'])
                        comments = await self._fetch_pr_comments(client, owner, repo, pr['number'])
                        
                        pr_documents = self._process_pr_data(pr_details, reviews, comments, owner, repo)
                        documents.extend(pr_documents)
                        
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        logger.error(f"Error processing PR #{pr['number']}: {str(e)}")
                        continue
        
        except Exception as e:
            logger.error(f"Error fetching PRs: {str(e)}")
            return []
        
        for doc in documents:
            doc['metadata'].update({
                'is_demo': False,
                'user_id': self.user_id
            })
        
        logger.info(f"Processed {len(documents)} PR documents from {owner}/{repo}")
        return documents
    
    def _generate_synthetic_prs(self, scenario: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        startup_prs = [
            {
                'number': 1,
                'title': 'Add user authentication system',
                'body': '''## Summary
Implements JWT-based authentication system with login/logout functionality.

## Changes
- Added auth middleware
- Created login/register endpoints
- Added password hashing with bcrypt
- Implemented JWT token validation

## Testing
- Added unit tests for auth functions
- Tested login/logout flow manually
- Verified token expiration handling

Closes #12''',
                'state': 'merged',
                'author': 'sarah-dev',
                'created_at': '2024-01-15T10:30:00Z',
                'merged_at': '2024-01-16T14:20:00Z',
                'additions': 245,
                'deletions': 12,
                'changed_files': 8,
                'commits': 6,
                'labels': ['feature', 'authentication'],
                'reviews': [
                    {
                        'body': 'Great implementation! The JWT handling looks solid. One minor suggestion: consider adding rate limiting to prevent brute force attacks.',
                        'state': 'approved',
                        'reviewer': 'tech-lead'
                    }
                ],
                'comments': [
                    {
                        'body': 'Should we add password strength validation as well?',
                        'author': 'junior-dev'
                    }
                ]
            },
            {
                'number': 2,
                'title': 'Fix memory leak in data processing',
                'body': '''## Bug Description
Memory usage was continuously growing during large data processing operations.

## Root Cause
Data chunks were not being properly garbage collected due to circular references.

## Solution
- Fixed circular references in DataProcessor class
- Added explicit cleanup in finally blocks
- Implemented proper resource disposal

## Impact
Memory usage now remains stable during long-running operations.''',
                'state': 'merged',
                'author': 'performance-expert',
                'created_at': '2024-01-20T09:15:00Z',
                'merged_at': '2024-01-20T16:45:00Z',
                'additions': 67,
                'deletions': 34,
                'changed_files': 3,
                'commits': 2,
                'labels': ['bugfix', 'performance'],
                'reviews': [
                    {
                        'body': 'Excellent fix! The memory profiling results look much better now.',
                        'state': 'approved',
                        'reviewer': 'senior-engineer'
                    }
                ],
                'comments': []
            }
        ]
        
        enterprise_prs = [
            {
                'number': 15,
                'title': 'Implement microservices architecture migration',
                'body': '''## Overview
Phase 1 of microservices migration - separating user service from monolith.

## Architecture Changes
- Created dedicated user-service container
- Implemented service discovery with Consul
- Added API gateway routing
- Set up inter-service communication via gRPC

## Infrastructure
- Added Kubernetes manifests
- Configured load balancing
- Implemented health checks
- Added monitoring with Prometheus

## Database Changes
- Migrated user tables to separate database
- Implemented data synchronization
- Added database connection pooling

## Security
- Service-to-service authentication
- mTLS for internal communication
- Updated security policies

This is part of the Q2 architecture modernization initiative.''',
                'state': 'open',
                'author': 'principal-architect',
                'created_at': '2024-01-25T11:00:00Z',
                'merged_at': None,
                'additions': 1247,
                'deletions': 89,
                'changed_files': 42,
                'commits': 18,
                'labels': ['architecture', 'microservices', 'infrastructure'],
                'reviews': [
                    {
                        'body': 'Comprehensive implementation. The service boundaries look well-defined. Please ensure backward compatibility during the transition period.',
                        'state': 'changes_requested',
                        'reviewer': 'enterprise-architect'
                    }
                ],
                'comments': [
                    {
                        'body': 'What is the rollback strategy if we encounter issues in production?',
                        'author': 'devops-lead'
                    }
                ]
            }
        ]
        
        freelancer_prs = [
            {
                'number': 3,
                'title': 'Add dark mode theme support',
                'body': '''## Feature Request
Client requested dark mode option for better user experience.

## Implementation
- Added theme context provider
- Created dark/light theme configurations
- Updated all components to use theme variables
- Added theme toggle button in header

## CSS Changes
- Converted hardcoded colors to CSS variables
- Added dark mode color palette
- Ensured proper contrast ratios
- Tested with accessibility tools

The client is very happy with the visual improvements!''',
                'state': 'merged',
                'author': 'fullstack-freelancer',
                'created_at': '2024-01-18T14:30:00Z',
                'merged_at': '2024-01-19T10:15:00Z',
                'additions': 156,
                'deletions': 78,
                'changed_files': 12,
                'commits': 5,
                'labels': ['feature', 'ui', 'client-request'],
                'reviews': [
                    {
                        'body': 'Looks great! The color choices work well and accessibility is maintained.',
                        'state': 'approved',
                        'reviewer': 'client-reviewer'
                    }
                ],
                'comments': []
            }
        ]
        
        if scenario == 'enterprise':
            base_prs = enterprise_prs
        elif scenario == 'freelancer':
            base_prs = freelancer_prs
        else:
            base_prs = startup_prs
        
        result_prs = []
        for i in range(min(limit, len(base_prs) * 3)):
            base_pr = base_prs[i % len(base_prs)]
            pr_copy = base_pr.copy()
            pr_copy['number'] = i + 1
            result_prs.append(pr_copy)
        
        return result_prs
    
    def _process_demo_pr_data(self, pr_data: Dict, scenario: str = None) -> List[Dict[str, Any]]:
        documents = []
        
        pr_doc = {
            'content': sanitize_text(pr_data['body']),
            'metadata': {
                'source_type': 'pull_request',
                'pr_number': pr_data['number'],
                'pr_title': pr_data['title'],
                'pr_state': pr_data['state'],
                'pr_url': f"https://github.com/demo/repo/pull/{pr_data['number']}",
                'repository': 'demo/repo',
                'author': pr_data['author'],
                'created_at': pr_data['created_at'],
                'updated_at': pr_data['created_at'],
                'merged_at': pr_data.get('merged_at'),
                'content_hash': get_file_hash(pr_data['body']),
                'tags': self._extract_demo_pr_tags(pr_data),
                'file_path': f"prs/demo-repo/pr-{pr_data['number']}",
                'changes': {
                    'additions': pr_data.get('additions', 0),
                    'deletions': pr_data.get('deletions', 0),
                    'changed_files': pr_data.get('changed_files', 0),
                    'commits': pr_data.get('commits', 0),
                    'merged': pr_data['state'] == 'merged'
                },
                'technical_terms': extract_technical_terms(pr_data['body']),
                'complexity': self._estimate_demo_pr_complexity(pr_data),
                'pr_type': self._classify_pr_type(pr_data['title'], pr_data['body'])
            }
        }
        documents.append(pr_doc)
        
        for review in pr_data.get('reviews', []):
            review_doc = {
                'content': sanitize_text(review['body']),
                'metadata': {
                    'source_type': 'pr_review',
                    'pr_number': pr_data['number'],
                    'pr_title': pr_data['title'],
                    'repository': 'demo/repo',
                    'reviewer': review['reviewer'],
                    'review_state': review['state'],
                    'created_at': pr_data['created_at'],
                    'content_hash': get_file_hash(review['body']),
                    'file_path': f"prs/demo-repo/pr-{pr_data['number']}/review-{hash(review['body'])}",
                    'tags': ['review', 'feedback', review['state']],
                    'technical_terms': extract_technical_terms(review['body'])
                }
            }
            documents.append(review_doc)
        
        for comment in pr_data.get('comments', []):
            comment_doc = {
                'content': sanitize_text(comment['body']),
                'metadata': {
                    'source_type': 'pr_comment',
                    'pr_number': pr_data['number'],
                    'pr_title': pr_data['title'],
                    'repository': 'demo/repo',
                    'commenter': comment['author'],
                    'created_at': pr_data['created_at'],
                    'updated_at': pr_data['created_at'],
                    'content_hash': get_file_hash(comment['body']),
                    'file_path': f"prs/demo-repo/pr-{pr_data['number']}/comment-{hash(comment['body'])}",
                    'tags': ['comment', 'discussion'],
                    'technical_terms': extract_technical_terms(comment['body'])
                }
            }
            documents.append(comment_doc)
        
        return documents
    
    def _extract_demo_pr_tags(self, pr_data: Dict) -> List[str]:
        tags = ['pull_request', pr_data['state']]
        tags.extend(pr_data.get('labels', []))
        
        title_lower = pr_data['title'].lower()
        if 'feat' in title_lower or 'add' in title_lower:
            tags.append('feature')
        elif 'fix' in title_lower or 'bug' in title_lower:
            tags.append('bugfix')
        elif 'refactor' in title_lower:
            tags.append('refactor')
        
        return list(set(tags))
    
    def _estimate_demo_pr_complexity(self, pr_data: Dict) -> str:
        additions = pr_data.get('additions', 0)
        deletions = pr_data.get('deletions', 0)
        files_changed = pr_data.get('changed_files', 0)
        
        total_changes = additions + deletions
        
        if total_changes < 50 and files_changed <= 3:
            return 'low'
        elif total_changes < 200 and files_changed <= 10:
            return 'medium'
        else:
            return 'high'
    
    def _parse_repo_url(self, repo_url: str) -> tuple:
        try:
            if repo_url.startswith("https://github.com/"):
                parts = repo_url.replace("https://github.com/", "").strip("/").split("/")
            elif repo_url.startswith("git@github.com:"):
                parts = repo_url.replace("git@github.com:", "").replace(".git", "").split("/")
            else:
                parts = repo_url.strip("/").split("/")
            
            if len(parts) >= 2:
                return parts[0], parts[1]
            
        except Exception as e:
            logger.error(f"Error parsing repo URL {repo_url}: {str(e)}")
        
        return None, None
    
    async def _fetch_prs_list(
        self, 
        client: httpx.AsyncClient, 
        owner: str, 
        repo: str, 
        state: str, 
        limit: int,
        days_back: int
    ) -> List[Dict]:
        
        since_date = datetime.now() - timedelta(days=days_back)
        since_str = since_date.isoformat()
        
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        params = {
            "state": state,
            "per_page": min(100, limit),
            "sort": "updated",
            "direction": "desc"
        }
        
        all_prs = []
        page = 1
        
        while len(all_prs) < limit:
            params["page"] = page
            
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                prs = response.json()
                if not prs:
                    break
                
                for pr in prs:
                    if len(all_prs) >= limit:
                        break
                    
                    updated_at = datetime.fromisoformat(pr['updated_at'].replace('Z', '+00:00'))
                    if updated_at >= since_date.replace(tzinfo=updated_at.tzinfo):
                        all_prs.append(pr)
                
                page += 1
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error fetching PRs: {e.response.status_code}")
                break
            except Exception as e:
                logger.error(f"Error fetching PRs page {page}: {str(e)}")
                break
        
        return all_prs[:limit]
    
    async def _fetch_pr_details(self, client: httpx.AsyncClient, owner: str, repo: str, pr_number: int) -> Dict:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching PR #{pr_number} details: {str(e)}")
            return {}
    
    async def _fetch_pr_reviews(self, client: httpx.AsyncClient, owner: str, repo: str, pr_number: int) -> List[Dict]:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching PR #{pr_number} reviews: {str(e)}")
            return []
    
    async def _fetch_pr_comments(self, client: httpx.AsyncClient, owner: str, repo: str, pr_number: int) -> List[Dict]:
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching PR #{pr_number} comments: {str(e)}")
            return []
    
    def _process_pr_data(
        self, 
        pr: Dict, 
        reviews: List[Dict], 
        comments: List[Dict],
        owner: str,
        repo: str
    ) -> List[Dict[str, Any]]:
        
        if not pr:
            return []
        
        documents = []
        pr_number = pr['number']
        
        if pr.get('body'):
            pr_doc = {
                'content': sanitize_text(pr['body']),
                'metadata': {
                    'source_type': 'pull_request',
                    'pr_number': pr_number,
                    'pr_title': pr['title'],
                    'pr_state': pr['state'],
                    'pr_url': pr['html_url'],
                    'repository': f"{owner}/{repo}",
                    'author': pr['user']['login'],
                    'created_at': pr['created_at'],
                    'updated_at': pr['updated_at'],
                    'merged_at': pr.get('merged_at'),
                    'content_hash': get_file_hash(pr['body']),
                    'tags': self._extract_pr_tags(pr),
                    'file_path': f"prs/{owner}-{repo}/pr-{pr_number}",
                    'changes': self._summarize_changes(pr),
                    'technical_terms': extract_technical_terms(pr['body']),
                    'complexity': self._estimate_pr_complexity(pr),
                    'pr_type': self._classify_pr_type(pr['title'], pr.get('body', ''))
                }
            }
            documents.append(pr_doc)
        
        for review in reviews:
            if review.get('body'):
                review_doc = {
                    'content': sanitize_text(review['body']),
                    'metadata': {
                        'source_type': 'pr_review',
                        'pr_number': pr_number,
                        'pr_title': pr['title'],
                        'repository': f"{owner}/{repo}",
                        'reviewer': review['user']['login'],
                        'review_state': review['state'],
                        'created_at': review['submitted_at'],
                        'content_hash': get_file_hash(review['body']),
                        'file_path': f"prs/{owner}-{repo}/pr-{pr_number}/review-{review['id']}",
                        'tags': ['review', 'feedback'] + self._extract_review_tags(review),
                        'technical_terms': extract_technical_terms(review['body'])
                    }
                }
                documents.append(review_doc)
        
        for comment in comments:
            if comment.get('body'):
                comment_doc = {
                    'content': sanitize_text(comment['body']),
                    'metadata': {
                        'source_type': 'pr_comment',
                        'pr_number': pr_number,
                        'pr_title': pr['title'],
                        'repository': f"{owner}/{repo}",
                        'commenter': comment['user']['login'],
                        'created_at': comment['created_at'],
                        'updated_at': comment['updated_at'],
                        'content_hash': get_file_hash(comment['body']),
                        'file_path': f"prs/{owner}-{repo}/pr-{pr_number}/comment-{comment['id']}",
                        'tags': ['comment', 'discussion'] + self._extract_comment_tags(comment),
                        'technical_terms': extract_technical_terms(comment['body'])
                    }
                }
                documents.append(comment_doc)
        
        return documents
    
    def _extract_pr_tags(self, pr: Dict) -> List[str]:
        tags = ['pull_request']
        
        tags.append(pr['state'])
        
        for label in pr.get('labels', []):
            tags.append(label['name'])
        
        if pr.get('head', {}).get('ref'):
            branch_name = pr['head']['ref']
            if 'feature' in branch_name.lower():
                tags.append('feature')
            elif 'fix' in branch_name.lower() or 'bug' in branch_name.lower():
                tags.append('bugfix')
            elif 'hotfix' in branch_name.lower():
                tags.append('hotfix')
        
        title_lower = pr['title'].lower()
        if 'feat' in title_lower or 'add' in title_lower:
            tags.append('feature')
        elif 'fix' in title_lower or 'bug' in title_lower:
            tags.append('bugfix')
        elif 'refactor' in title_lower:
            tags.append('refactor')
        elif 'test' in title_lower:
            tags.append('testing')
        elif 'doc' in title_lower:
            tags.append('documentation')
        
        return list(set(tags))
    
    def _extract_review_tags(self, review: Dict) -> List[str]:
        tags = []
        
        state = review.get('state', '').lower()
        if state == 'approved':
            tags.append('approved')
        elif state == 'changes_requested':
            tags.append('changes_requested')
        elif state == 'commented':
            tags.append('commented')
        
        return tags
    
    def _extract_comment_tags(self, comment: Dict) -> List[str]:
        tags = []
        
        body_lower = comment.get('body', '').lower()
        
        if 'lgtm' in body_lower or 'looks good' in body_lower:
            tags.append('approval')
        elif 'question' in body_lower or '?' in comment.get('body', ''):
            tags.append('question')
        elif 'suggestion' in body_lower or 'consider' in body_lower:
            tags.append('suggestion')
        elif 'issue' in body_lower or 'problem' in body_lower:
            tags.append('issue')
        
        return tags
    
    def _summarize_changes(self, pr: Dict) -> Dict[str, Any]:
        return {
            'additions': pr.get('additions', 0),
            'deletions': pr.get('deletions', 0),
            'changed_files': pr.get('changed_files', 0),
            'commits': pr.get('commits', 0),
            'mergeable': pr.get('mergeable'),
            'merged': pr.get('merged', False)
        }
    
    def _estimate_pr_complexity(self, pr: Dict) -> str:
        additions = pr.get('additions', 0)
        deletions = pr.get('deletions', 0)
        files_changed = pr.get('changed_files', 0)
        
        total_changes = additions + deletions
        
        if total_changes < 50 and files_changed <= 3:
            return 'low'
        elif total_changes < 200 and files_changed <= 10:
            return 'medium'
        else:
            return 'high'
    
    def _classify_pr_type(self, title: str, body: str) -> str:
        combined_text = (title + ' ' + body).lower()
        
        if any(word in combined_text for word in ['feat', 'feature', 'add', 'implement']):
            return 'feature'
        elif any(word in combined_text for word in ['fix', 'bug', 'resolve', 'issue']):
            return 'bugfix'
        elif any(word in combined_text for word in ['refactor', 'cleanup', 'improve']):
            return 'refactor'
        elif any(word in combined_text for word in ['test', 'spec', 'coverage']):
            return 'test'
        elif any(word in combined_text for word in ['doc', 'readme', 'comment']):
            return 'documentation'
        elif any(word in combined_text for word in ['chore', 'update', 'bump']):
            return 'maintenance'
        else:
            return 'other'
    
    async def fetch_single_pr(self, repo_url: str, pr_number: int) -> List[Dict[str, Any]]:
        if self.demo_mode:
            demo_prs = self._generate_synthetic_prs(None, 10)
            target_pr = next((pr for pr in demo_prs if pr['number'] == pr_number), None)
            if target_pr:
                return self._process_demo_pr_data(target_pr)
            return []
        
        owner, repo = self._parse_repo_url(repo_url)
        if not owner or not repo:
            logger.error(f"Invalid repository URL: {repo_url}")
            return []
        
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
                pr_details = await self._fetch_pr_details(client, owner, repo, pr_number)
                if not pr_details:
                    return []
                
                reviews = await self._fetch_pr_reviews(client, owner, repo, pr_number)
                comments = await self._fetch_pr_comments(client, owner, repo, pr_number)
                
                documents = self._process_pr_data(pr_details, reviews, comments, owner, repo)
                
                for doc in documents:
                    doc['metadata'].update({
                        'is_demo': False,
                        'user_id': self.user_id
                    })
                
                return documents
                
        except Exception as e:
            logger.error(f"Error fetching PR #{pr_number}: {str(e)}")
            return []
    
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
    
    def get_fetch_stats(self) -> Dict[str, Any]:
        return {
            "github_token_configured": bool(self.github_token),
            "demo_mode": self.demo_mode,
            "user_id": self.user_id,
            "demo_scenarios": self.get_demo_scenarios() if self.demo_mode else None,
            "rate_limit_handling": True,
            "supported_data_types": [
                "pr_descriptions",
                "review_comments", 
                "discussion_comments",
                "pr_metadata",
                "change_statistics"
            ],
            "processing_features": [
                "content_sanitization",
                "technical_term_extraction",
                "pr_type_classification",
                "complexity_estimation",
                "tag_extraction"
            ]
        }


def fetch_prs_quick(repo_url: str = None, limit: int = 20, demo_mode: bool = False, user_id: str = None, scenario: str = None) -> List[Dict[str, Any]]:
    fetcher = PRFetcher(demo_mode=demo_mode, user_id=user_id)
    import asyncio
    return asyncio.run(fetcher.fetch_pull_requests(repo_url, limit, scenario=scenario))

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
            
            fetcher = PRFetcher(demo_mode=demo_mode, user_id=user_id)
            
            if command == "fetch":
                repo_url = None
                limit = 10
                
                for i, arg in enumerate(sys.argv[2:], 2):
                    if not arg.startswith('--') and arg not in [user_id, scenario]:
                        if repo_url is None:
                            repo_url = arg
                        else:
                            try:
                                limit = int(arg)
                            except ValueError:
                                pass
                        break
                
                if demo_mode and not repo_url:
                    repo_url = "demo/repo"
                
                results = await fetcher.fetch_pull_requests(repo_url, limit, scenario=scenario)
                print(f"Fetched {len(results)} PR documents")
                
                if demo_mode:
                    print(f"Demo mode: {demo_mode}, Scenario: {scenario or 'default'}")
                
                for i, result in enumerate(results[:3]):
                    print(f"\nSample {i+1}:")
                    print(f"Type: {result['metadata']['source_type']}")
                    print(f"PR: #{result['metadata']['pr_number']} - {result['metadata']['pr_title']}")
                    print(f"Author: {result['metadata'].get('author', 'N/A')}")
                    print(f"Demo: {result['metadata'].get('is_demo', False)}")
                    print(f"Content: {result['content'][:100]}...")
                    
            elif command == "single":
                repo_url = None
                pr_number = None
                
                for i, arg in enumerate(sys.argv[2:], 2):
                    if not arg.startswith('--') and arg not in [user_id, scenario]:
                        if repo_url is None:
                            repo_url = arg
                        else:
                            try:
                                pr_number = int(arg)
                            except ValueError:
                                pass
                        break
                
                if not repo_url or pr_number is None:
                    print("Usage: python pr_fetcher.py single <repo_url> <pr_number>")
                    return
                
                results = await fetcher.fetch_single_pr(repo_url, pr_number)
                print(f"Fetched {len(results)} documents for PR #{pr_number}")
                
                for result in results:
                    print(f"- {result['metadata']['source_type']}: {result['content'][:50]}...")
                    print(f"  Demo: {result['metadata'].get('is_demo', False)}")
                    
            elif command == "demo":
                print("Available demo scenarios:")
                for scenario in fetcher.get_demo_scenarios():
                    print(f"  - {scenario}")
                    
            elif command == "stats":
                stats = fetcher.get_fetch_stats()
                print("PR Fetcher Statistics:")
                print(json.dumps(stats, indent=2))
                
            else:
                print("Available commands:")
                print("  fetch [repo_url] [limit] [--demo] [--user USER_ID] [--scenario SCENARIO] - Fetch PRs")
                print("  single <repo_url> <pr_number> [--demo] [--user USER_ID] - Fetch single PR")
                print("  demo - Show available demo scenarios")
                print("  stats - Show fetcher capabilities")
        else:
            print("Usage: python pr_fetcher.py [fetch|single|demo|stats] [options...]")
            print("Options:")
            print("  --demo              Enable demo mode")
            print("  --user USER_ID      Set user ID")
            print("  --scenario NAME     Set demo scenario (startup/enterprise/freelancer)")
    
    asyncio.run(main())