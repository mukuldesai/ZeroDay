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

class PRFetcher:
    """
    Pull Request Fetcher: Retrieves and processes GitHub PR data
    Extracts PR descriptions, discussions, code changes, and review comments
    """
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = self._setup_headers()
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from settings.yaml"""
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "settings.yaml"
            )
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _setup_headers(self) -> Dict[str, str]:
        """Setup GitHub API headers"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ZeroDay-Onboarding-Agent"
        }
        
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        
        return headers
    
    async def fetch_pull_requests(
        self, 
        repo_url: str = None, 
        limit: int = None,
        state: str = "all",
        days_back: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Fetch pull requests from GitHub repository
        
        Args:
            repo_url: GitHub repository URL
            limit: Maximum number of PRs to fetch
            state: PR state (open, closed, all)
            days_back: How many days back to fetch PRs
            
        Returns:
            List of processed PR documents
        """
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
        
        logger.info(f"Processed {len(documents)} PR documents from {owner}/{repo}")
        return documents
    
    def _parse_repo_url(self, repo_url: str) -> tuple:
        """Parse GitHub repository URL to extract owner and repo name"""
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
        """Fetch list of pull requests"""
        
        
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
        """Fetch detailed PR information"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching PR #{pr_number} details: {str(e)}")
            return {}
    
    async def _fetch_pr_reviews(self, client: httpx.AsyncClient, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """Fetch PR review comments"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching PR #{pr_number} reviews: {str(e)}")
            return []
    
    async def _fetch_pr_comments(self, client: httpx.AsyncClient, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """Fetch PR discussion comments"""
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
        """Process PR data into structured documents"""
        
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
        """Extract tags from PR data"""
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
        """Extract tags from review data"""
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
        """Extract tags from comment data"""
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
        """Summarize PR changes"""
        return {
            'additions': pr.get('additions', 0),
            'deletions': pr.get('deletions', 0),
            'changed_files': pr.get('changed_files', 0),
            'commits': pr.get('commits', 0),
            'mergeable': pr.get('mergeable'),
            'merged': pr.get('merged', False)
        }
    
    def _estimate_pr_complexity(self, pr: Dict) -> str:
        """Estimate PR complexity based on changes"""
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
        """Classify PR type based on title and description"""
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
        """Fetch a single PR by number"""
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
                
               
                return self._process_pr_data(pr_details, reviews, comments, owner, repo)
                
        except Exception as e:
            logger.error(f"Error fetching PR #{pr_number}: {str(e)}")
            return []
    
    def get_fetch_stats(self) -> Dict[str, Any]:
        """Get fetcher statistics and capabilities"""
        return {
            "github_token_configured": bool(self.github_token),
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


def fetch_prs_quick(repo_url: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Quick PR fetching function"""
    fetcher = PRFetcher()
    import asyncio
    return asyncio.run(fetcher.fetch_pull_requests(repo_url, limit))

if __name__ == "__main__":
    
    import sys
    import asyncio
    import json
    
    async def main():
        if len(sys.argv) > 1:
            command = sys.argv[1]
            fetcher = PRFetcher()
            
            if command == "fetch":
                repo_url = sys.argv[2] if len(sys.argv) > 2 else None
                limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
                
                if not repo_url:
                    print("Usage: python pr_fetcher.py fetch <repo_url> [limit]")
                    return
                
                results = await fetcher.fetch_pull_requests(repo_url, limit)
                print(f"Fetched {len(results)} PR documents")
                
                
                for i, result in enumerate(results[:3]):
                    print(f"\nSample {i+1}:")
                    print(f"Type: {result['metadata']['source_type']}")
                    print(f"PR: #{result['metadata']['pr_number']} - {result['metadata']['pr_title']}")
                    print(f"Author: {result['metadata'].get('author', 'N/A')}")
                    print(f"Content: {result['content'][:100]}...")
                    
            elif command == "single":
                if len(sys.argv) < 4:
                    print("Usage: python pr_fetcher.py single <repo_url> <pr_number>")
                    return
                
                repo_url = sys.argv[2]
                pr_number = int(sys.argv[3])
                
                results = await fetcher.fetch_single_pr(repo_url, pr_number)
                print(f"Fetched {len(results)} documents for PR #{pr_number}")
                
                for result in results:
                    print(f"- {result['metadata']['source_type']}: {result['content'][:50]}...")
                    
            elif command == "stats":
                stats = fetcher.get_fetch_stats()
                print("PR Fetcher Statistics:")
                print(json.dumps(stats, indent=2))
                
            else:
                print("Available commands:")
                print("  fetch <repo_url> [limit] - Fetch PRs from repository")
                print("  single <repo_url> <pr_number> - Fetch single PR")
                print("  stats - Show fetcher capabilities")
        else:
            print("Usage: python pr_fetcher.py [fetch|single|stats] [args...]")
    
    asyncio.run(main())