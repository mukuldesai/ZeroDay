import os
import yaml
import markdown
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger
from datetime import datetime
import re
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.helpers import get_file_hash, extract_file_metadata, sanitize_text
from dotenv import load_dotenv
load_dotenv()

class DocIngestor:
    
    def __init__(self, config_path: str = None, demo_mode: bool = False, user_id: str = None):
        self.config = self._load_config(config_path)
        self.demo_mode = demo_mode
        self.user_id = user_id or "demo_user"
        self.supported_extensions = {'.md', '.rst', '.txt', '.markdown', '.mkd'}
        self.markdown_parser = markdown.Markdown(extensions=[
            'toc', 'tables', 'fenced_code', 'codehilite'
        ])
        
        if self.demo_mode:
            self.demo_config = self._load_demo_config()
            logger.info(f"DocIngestor initialized in DEMO mode for user: {self.user_id}")
        else:
            logger.info(f"DocIngestor initialized in REAL mode for user: {self.user_id}")
        
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
                'demo_data_path': os.path.join(os.path.dirname(__file__), "..", "demo", "sample_data", "documents"),
                'scenarios': ['startup', 'enterprise', 'freelancer']
            }
    
    async def ingest_docs(self, base_path: str = None, scenario: str = None) -> List[Dict[str, Any]]:
        if self.demo_mode:
            return await self._ingest_demo_docs(scenario)
        else:
            return await self._ingest_real_docs(base_path)
    
    async def _ingest_demo_docs(self, scenario: str = None) -> List[Dict[str, Any]]:
        logger.info(f"Ingesting DEMO documentation for scenario: {scenario or 'default'}")
        
        demo_path = self.demo_config.get('demo_data_path')
        if not demo_path or not os.path.exists(demo_path):
            logger.warning("Demo documents not found, generating synthetic data")
            return self._generate_synthetic_docs(scenario)
        
        documents = await self._ingest_real_docs(demo_path)
        
        for doc in documents:
            doc['metadata'].update({
                'is_demo': True,
                'demo_scenario': scenario or 'default',
                'user_id': self.user_id,
                'demo_note': 'This is synthetic demo data for showcase purposes'
            })
        
        logger.info(f"Generated {len(documents)} DEMO documentation chunks")
        return documents
    
    async def _ingest_real_docs(self, base_path: str = None) -> List[Dict[str, Any]]:
        if not base_path:
            base_path = self.config['data_sources']['documentation']['path']
        
        base_path = Path(base_path).resolve()
        
        if not base_path.exists():
            logger.warning(f"Documentation path does not exist: {base_path}")
            return []
        
        logger.info(f"Starting documentation ingestion from: {base_path}")
        
        documents = []
        
        for file_path in self._walk_directory(base_path):
            try:
                if file_path.suffix.lower() in self.supported_extensions:
                    file_documents = await self._ingest_file(file_path, base_path)
                    documents.extend(file_documents)
                    
            except Exception as e:
                logger.error(f"Error ingesting file {file_path}: {str(e)}")
                continue
        
        for doc in documents:
            doc['metadata'].update({
                'is_demo': False,
                'user_id': self.user_id
            })
        
        logger.info(f"Ingested {len(documents)} documentation chunks from {base_path}")
        return documents
    
    def _generate_synthetic_docs(self, scenario: str = None) -> List[Dict[str, Any]]:
        synthetic_docs = [
            {
                'title': 'Getting Started Guide',
                'content': '''# Getting Started with ZeroDay Platform

Welcome to ZeroDay, the AI-powered developer onboarding platform. This guide will help you get up and running quickly.

## Prerequisites

Before you begin, ensure you have:
- Node.js 18+ installed
- Python 3.9+ installed
- Git configured on your system
- Access to your organization's repositories

## Quick Setup

1. Clone the repository
2. Install dependencies
3. Configure environment variables
4. Run the development server

### Installation Steps

```bash
git clone https://github.com/mukuldesai/ZeroDay
cd zeroday
npm install
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_key
DATABASE_URL=sqlite:///app.db
GITHUB_TOKEN=your_github_token
```

## First Steps

Once setup is complete, you can:
- Upload your codebase for analysis
- Chat with AI mentors
- Generate learning plans
- Track your progress

The platform will analyze your code and provide personalized guidance based on your experience level and project requirements.
''',
                'tags': ['getting-started', 'setup', 'installation'],
                'difficulty': 'beginner'
            },
            {
                'title': 'API Documentation',
                'content': '''# ZeroDay API Reference

The ZeroDay platform provides a comprehensive REST API for integrating with external tools and services.

## Authentication

All API requests require authentication using API keys:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.zeroday.dev/v1/
```

## Core Endpoints

### User Management

#### GET /api/users/profile
Get current user profile information.

**Response:**
```json
{
  "id": "user_123",
  "username": "developer",
  "organization": "acme-corp",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST /api/users/preferences
Update user preferences and settings.

### Code Analysis

#### POST /api/analyze/upload
Upload and analyze codebase files.

**Parameters:**
- `files`: Array of file objects
- `language`: Programming language (optional)
- `framework`: Framework type (optional)

**Response:**
```json
{
  "analysis_id": "analysis_456",
  "status": "processing",
  "estimated_time": 120
}
```

#### GET /api/analyze/{analysis_id}/results
Retrieve analysis results.

### AI Mentoring

#### POST /api/chat/mentor
Start a conversation with an AI mentor.

**Request Body:**
```json
{
  "message": "How do I implement authentication?",
  "context": "react-typescript",
  "mentor_type": "senior_dev"
}
```

## Rate Limits

- 100 requests per minute for analysis endpoints
- 1000 requests per minute for chat endpoints
- 10 file uploads per hour

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 429: Rate Limited
- 500: Server Error
''',
                'tags': ['api', 'documentation', 'reference'],
                'difficulty': 'intermediate'
            },
            {
                'title': 'Architecture Overview',
                'content': '''# ZeroDay Platform Architecture

This document outlines the high-level architecture of the ZeroDay developer onboarding platform.

## System Components

### Frontend Layer
- **Next.js Application**: React-based user interface
- **Component Library**: Reusable UI components
- **State Management**: Context API and custom hooks
- **Authentication**: Session-based auth with JWT tokens

### Backend Services
- **FastAPI Server**: Main application server
- **AI Agent System**: Intelligent mentoring and guidance
- **Vector Database**: ChromaDB for semantic search
- **Task Queue**: Background job processing

### Data Layer
- **PostgreSQL**: Primary database for user data
- **Redis**: Caching and session storage
- **File Storage**: S3-compatible object storage
- **Vector Store**: Embeddings and semantic search

## AI Agent Architecture

The platform uses a multi-agent system:

### Guide Agent
Provides contextual help and navigation assistance.

### Knowledge Agent
Answers technical questions using codebase context.

### Mentor Agent
Offers career guidance and best practices.

### Task Agent
Generates learning tasks and challenges.

## Security Considerations

### Data Protection
- All data encrypted at rest and in transit
- Regular security audits and penetration testing
- GDPR and SOC2 compliance

### Access Control
- Role-based permissions
- API rate limiting
- Audit logging for all actions

## Scalability

### Horizontal Scaling
- Containerized microservices
- Kubernetes orchestration
- Auto-scaling based on demand

### Performance Optimization
- CDN for static assets
- Database connection pooling
- Intelligent caching strategies

## Monitoring and Observability

- Application metrics with Prometheus
- Distributed tracing with Jaeger
- Log aggregation with ELK stack
- Real-time alerting and notifications

The architecture is designed to be cloud-native, scalable, and maintainable while providing a seamless developer experience.
''',
                'tags': ['architecture', 'system-design', 'scalability'],
                'difficulty': 'advanced'
            }
        ]
        
        documents = []
        for i, doc_data in enumerate(synthetic_docs):
            sections = self._split_by_headers(doc_data['content'])
            
            for section in sections:
                if not section['content'].strip():
                    continue
                
                clean_content = sanitize_text(section['content'])
                
                doc = {
                    'content': clean_content,
                    'metadata': {
                        'source_type': 'documentation',
                        'file_path': f"{doc_data['title'].lower().replace(' ', '_')}.md",
                        'section_title': section['title'],
                        'section_level': section['level'],
                        'file_size': len(clean_content),
                        'created_at': datetime.now().isoformat(),
                        'modified_at': datetime.now().isoformat(),
                        'content_hash': get_file_hash(clean_content),
                        'tags': doc_data['tags'],
                        'difficulty': doc_data['difficulty'],
                        'doc_type': 'markdown',
                        'keywords': self._extract_keywords(clean_content),
                        'is_demo': True,
                        'demo_scenario': scenario or 'default',
                        'user_id': self.user_id,
                        'demo_note': 'This is synthetic demo data for showcase purposes'
                    }
                }
                documents.append(doc)
        
        logger.info(f"Generated {len(documents)} synthetic documentation chunks")
        return documents
    
    def _walk_directory(self, base_path: Path) -> List[Path]:
        files = []
        
        for root, dirs, filenames in os.walk(base_path):
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', '.venv', 'venv'}]
            
            for filename in filenames:
                file_path = Path(root) / filename
                
                if file_path.suffix.lower() in self.supported_extensions:
                    files.append(file_path)
        
        return files
    
    async def _ingest_file(self, file_path: Path, base_path: Path) -> List[Dict[str, Any]]:
        try:
            with open(file_path, 'r', encoding='utf-8', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return []
            
            relative_path = file_path.relative_to(base_path)
            file_metadata = extract_file_metadata(file_path)
            
            if file_path.suffix.lower() in {'.md', '.markdown', '.mkd'}:
                documents = self._parse_markdown(content, str(relative_path), file_metadata)
            elif file_path.suffix.lower() == '.rst':
                documents = self._parse_rst(content, str(relative_path), file_metadata)
            else:
                documents = self._parse_text(content, str(relative_path), file_metadata)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error ingesting file {file_path}: {str(e)}")
            return []
    
    def _parse_markdown(self, content: str, file_path: str, file_metadata: Dict) -> List[Dict[str, Any]]:
        documents = []
        
        frontmatter = self._extract_frontmatter(content)
        if frontmatter:
            content = content[frontmatter['end_pos']:]
        
        sections = self._split_by_headers(content)
        
        for section in sections:
            if not section['content'].strip():
                continue
            
            clean_content = sanitize_text(section['content'])
            code_blocks = self._extract_code_blocks(section['content'])
            links = self._extract_links(section['content'])
            
            doc = {
                'content': clean_content,
                'metadata': {
                    'source_type': 'documentation',
                    'file_path': file_path,
                    'section_title': section['title'],
                    'section_level': section['level'],
                    'file_size': file_metadata['size'],
                    'created_at': file_metadata['created_at'],
                    'modified_at': file_metadata['modified_at'],
                    'content_hash': get_file_hash(clean_content),
                    'tags': self._extract_tags(section['content'], frontmatter),
                    'difficulty': self._estimate_difficulty(clean_content),
                    'doc_type': 'markdown',
                    'code_blocks': len(code_blocks),
                    'external_links': len(links),
                    'frontmatter': frontmatter.get('data', {}) if frontmatter else {},
                    'keywords': self._extract_keywords(clean_content)
                }
            }
            documents.append(doc)
        
        return documents
    
    def _parse_rst(self, content: str, file_path: str, file_metadata: Dict) -> List[Dict[str, Any]]:
        sections = self._split_rst_by_headers(content)
        documents = []
        
        for section in sections:
            if not section['content'].strip():
                continue
            
            clean_content = sanitize_text(section['content'])
            
            doc = {
                'content': clean_content,
                'metadata': {
                    'source_type': 'documentation',
                    'file_path': file_path,
                    'section_title': section['title'],
                    'section_level': section['level'],
                    'file_size': file_metadata['size'],
                    'created_at': file_metadata['created_at'],
                    'modified_at': file_metadata['modified_at'],
                    'content_hash': get_file_hash(clean_content),
                    'tags': self._extract_tags(section['content']),
                    'difficulty': self._estimate_difficulty(clean_content),
                    'doc_type': 'rst',
                    'keywords': self._extract_keywords(clean_content)
                }
            }
            documents.append(doc)
        
        return documents
    
    def _parse_text(self, content: str, file_path: str, file_metadata: Dict) -> List[Dict[str, Any]]:
        chunks = self._chunk_text(content)
        documents = []
        
        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            
            clean_content = sanitize_text(chunk)
            
            doc = {
                'content': clean_content,
                'metadata': {
                    'source_type': 'documentation',
                    'file_path': file_path,
                    'section_title': f"Section {i+1}",
                    'section_level': 1,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'file_size': file_metadata['size'],
                    'created_at': file_metadata['created_at'],
                    'modified_at': file_metadata['modified_at'],
                    'content_hash': get_file_hash(clean_content),
                    'tags': self._extract_tags(chunk),
                    'difficulty': self._estimate_difficulty(clean_content),
                    'doc_type': 'text',
                    'keywords': self._extract_keywords(clean_content)
                }
            }
            documents.append(doc)
        
        return documents
    
    def _extract_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        if not content.startswith('---'):
            return None
        
        try:
            end_marker = content.find('\n---\n', 4)
            if end_marker == -1:
                return None
            
            frontmatter_text = content[4:end_marker]
            frontmatter_data = yaml.safe_load(frontmatter_text)
            
            return {
                'data': frontmatter_data,
                'end_pos': end_marker + 5
            }
        except Exception as e:
            logger.warning(f"Error parsing frontmatter: {str(e)}")
            return None
    
    def _split_by_headers(self, content: str) -> List[Dict[str, Any]]:
        lines = content.split('\n')
        sections = []
        current_section = {
            'title': 'Introduction',
            'level': 1,
            'content': '',
            'start_line': 0
        }

        found_header = False

        for i, line in enumerate(lines):
            match = re.match(r'^(#{1,6})\s+(.*)', line.strip())
            if match:
                found_header = True
                if current_section['content'].strip():
                    sections.append(current_section)
                level = len(match.group(1))
                title = match.group(2).strip()
                current_section = {
                    'title': title,
                    'level': level,
                    'content': '',
                    'start_line': i
                }
            else:
                current_section['content'] += line + '\n'

        if current_section['content'].strip():
            sections.append(current_section)

        # fallback: treat whole content as one chunk if no headers were found
        if not found_header and content.strip():
            return [{
                'title': 'Full Document',
                'level': 1,
                'content': content,
                'start_line': 0
            }]

        return sections

    
    def _split_rst_by_headers(self, content: str) -> List[Dict[str, Any]]:
        sections = []
        lines = content.split('\n')
        
        current_section = {
            'title': 'Introduction',
            'level': 0,
            'content': '',
            'start_line': 0
        }
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                
                if re.match(r'^[=\-`:\'"~^_*+#<>]{3,}', next_line) and len(next_line) >= len(line.strip()):
                
                    if current_section['content'].strip():
                        sections.append(current_section)
                    
                    char = next_line[0]
                    level_map = {'=': 1, '-': 2, '`': 3, ':': 4, "'": 5, '"': 6, '~': 7, '^': 8, '_': 9, '*': 10, '+': 11, '#': 12}
                    level = level_map.get(char, 1)
                    
                    current_section = {
                        'title': line.strip(),
                        'level': level,
                        'content': '',
                        'start_line': i
                    }
                    
                    i += 2
                    continue
            
            current_section['content'] += line + '\n'
            i += 1

        if current_section['content'].strip():
            sections.append(current_section)
        
        return sections
    
    def _chunk_text(self, content: str, max_chunk_size: int = 1000) -> List[str]:
        if len(content) <= max_chunk_size:
            return [content]
        
        chunks = []
        paragraphs = content.split('\n\n')
        
        current_chunk = ''
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= max_chunk_size:
                current_chunk += paragraph + '\n\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + '\n\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        code_blocks = []
        
        fenced_pattern = r'```(\w+)?\n(.*?)```'
        for match in re.finditer(fenced_pattern, content, re.DOTALL):
            language = match.group(1) or 'unknown'
            code = match.group(2).strip()
            code_blocks.append({
                'language': language,
                'code': code
            })

        indented_pattern = r'\n((?:    .*\n?)+)'
        for match in re.finditer(indented_pattern, content):
            code = match.group(1).strip()
            code = '\n'.join(line[4:] if line.startswith('    ') else line for line in code.split('\n'))
            code_blocks.append({
                'language': 'unknown',
                'code': code
            })
        
        return code_blocks
    
    def _extract_links(self, content: str) -> List[Dict[str, str]]:
        links = []
        
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(link_pattern, content):
            text = match.group(1)
            url = match.group(2)
            links.append({
                'text': text,
                'url': url,
                'type': 'markdown'
            })

        ref_pattern = r'\[([^\]]+)\]\[([^\]]+)\]'
        for match in re.finditer(ref_pattern, content):
            text = match.group(1)
            ref = match.group(2)
            links.append({
                'text': text,
                'reference': ref,
                'type': 'reference'
            })
        
        return links
    
    def _extract_tags(self, content: str, frontmatter: Dict = None) -> List[str]:
        tags = []
        
        if frontmatter and 'data' in frontmatter:
            fm_data = frontmatter['data']
            if 'tags' in fm_data:
                tags.extend(fm_data['tags'] if isinstance(fm_data['tags'], list) else [fm_data['tags']])
            if 'keywords' in fm_data:
                tags.extend(fm_data['keywords'] if isinstance(fm_data['keywords'], list) else [fm_data['keywords']])
            if 'category' in fm_data:
                tags.append(fm_data['category'])
        
        tech_terms = [
            'api', 'rest', 'graphql', 'database', 'sql', 'nosql', 'docker', 'kubernetes',
            'react', 'vue', 'angular', 'node', 'python', 'javascript', 'typescript',
            'git', 'github', 'deployment', 'testing', 'authentication', 'authorization',
            'microservices', 'serverless', 'cloud', 'aws', 'azure', 'gcp'
        ]
        
        content_lower = content.lower()
        for term in tech_terms:
            if term in content_lower:
                tags.append(term)
        
        code_terms = re.findall(r'`([^`]+)`', content)
        tags.extend([term for term in code_terms if len(term) > 2 and len(term) < 20])
        
        return list(set(tags))
    
    def _extract_keywords(self, content: str) -> List[str]:
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        
        stop_words = {
            'this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 'were',
            'said', 'each', 'which', 'their', 'time', 'would', 'there', 'could',
            'other', 'more', 'very', 'what', 'know', 'just', 'first', 'into', 'over',
            'think', 'also', 'your', 'work', 'life', 'only', 'can', 'still', 'should',
            'after', 'being', 'now', 'made', 'before', 'through', 'when', 'where',
            'much', 'good', 'well', 'such', 'most', 'some', 'many', 'even', 'back',
            'come', 'these', 'than', 'them', 'want', 'here', 'does', 'about'
        }
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in keywords[:10]]
    
    def _estimate_difficulty(self, content: str) -> str:
        difficulty_score = 0
        
        tech_terms = ['api', 'algorithm', 'architecture', 'framework', 'implementation', 'configuration']
        difficulty_score += sum(1 for term in tech_terms if term in content.lower())
        
        complex_patterns = ['async', 'promise', 'callback', 'closure', 'inheritance', 'polymorphism']
        difficulty_score += sum(1 for pattern in complex_patterns if pattern in content.lower())
        
        word_count = len(content.split())
        if word_count > 500:
            difficulty_score += 2
        elif word_count > 200:
            difficulty_score += 1
        
        code_blocks = len(re.findall(r'```.*?```', content, re.DOTALL))
        difficulty_score += code_blocks
        
        if difficulty_score < 3:
            return 'beginner'
        elif difficulty_score < 8:
            return 'intermediate'
        else:
            return 'advanced'
    
    async def ingest_single_file(self, file_path: str) -> List[Dict[str, Any]]:
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File does not exist: {file_path}")
            return []
        
        if file_path.suffix.lower() not in self.supported_extensions:
            logger.warning(f"Unsupported file type: {file_path.suffix}")
            return []
        
        return await self._ingest_file(file_path, file_path.parent)
    
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
    
    def get_supported_formats(self) -> List[str]:
        return list(self.supported_extensions)
    
    def get_ingestion_stats(self) -> Dict[str, Any]:
        return {
            "supported_extensions": list(self.supported_extensions),
            "markdown_extensions": ['toc', 'tables', 'fenced_code', 'codehilite'],
            "demo_mode": self.demo_mode,
            "user_id": self.user_id,
            "demo_scenarios": self.get_demo_scenarios() if self.demo_mode else None,
            "features": [
                "frontmatter_extraction",
                "header_based_sectioning", 
                "code_block_detection",
                "link_extraction",
                "keyword_extraction",
                "difficulty_estimation"
            ]
        }


def ingest_docs_quick(base_path: str = None, demo_mode: bool = False, user_id: str = None, scenario: str = None) -> List[Dict[str, Any]]:
    ingestor = DocIngestor(demo_mode=demo_mode, user_id=user_id)
    import asyncio
    return asyncio.run(ingestor.ingest_docs(base_path, scenario))

def ingest_single_doc(file_path: str, demo_mode: bool = False, user_id: str = None) -> List[Dict[str, Any]]:
    ingestor = DocIngestor(demo_mode=demo_mode, user_id=user_id)
    import asyncio
    return asyncio.run(ingestor.ingest_single_file(file_path))

if __name__ == "__main__":
    import sys
    import asyncio
    import json
    
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
            
            ingestor = DocIngestor(demo_mode=demo_mode, user_id=user_id)
            
            if command == "ingest":
                base_path = None
                for arg in sys.argv[2:]:
                    if not arg.startswith('--') and arg not in [user_id, scenario]:
                        base_path = arg
                        break
                
                results = await ingestor.ingest_docs(base_path, scenario)
                print(f"Ingested {len(results)} documentation chunks")
                
                if demo_mode:
                    print(f"Demo mode: {demo_mode}, Scenario: {scenario or 'default'}")
                
                for i, result in enumerate(results[:3]):
                    print(f"\nSample {i+1}:")
                    print(f"Type: {result['metadata']['doc_type']}")
                    print(f"Title: {result['metadata']['section_title']}")
                    print(f"File: {result['metadata']['file_path']}")
                    print(f"Difficulty: {result['metadata']['difficulty']}")
                    print(f"Demo: {result['metadata'].get('is_demo', False)}")
                    print(f"Content: {result['content'][:100]}...")
                    
            elif command == "file":
                if len(sys.argv) < 3:
                    print("Usage: python doc_ingestor.py file <file_path>")
                    return
                    
                file_path = None
                for arg in sys.argv[2:]:
                    if not arg.startswith('--') and arg not in [user_id, scenario]:
                        file_path = arg
                        break
                
                if not file_path:
                    print("Error: No file path provided")
                    return
                    
                results = await ingestor.ingest_single_file(file_path)
                print(f"Ingested {len(results)} chunks from {file_path}")
                
                for result in results:
                    print(f"Section: {result['metadata']['section_title']}")
                    print(f"Tags: {result['metadata']['tags']}")
                    print(f"Keywords: {result['metadata']['keywords']}")
                    print(f"Demo: {result['metadata'].get('is_demo', False)}")
                    
            elif command == "demo":
                print("Available demo scenarios:")
                for scenario in ingestor.get_demo_scenarios():
                    print(f"  - {scenario}")
                    
            elif command == "stats":
                stats = ingestor.get_ingestion_stats()
                print("Documentation Ingestor Statistics:")
                print(json.dumps(stats, indent=2))
                
            else:
                print("Available commands:")
                print("  ingest [path] [--demo] [--user USER_ID] [--scenario SCENARIO] - Ingest documentation")
                print("  file <file_path> [--demo] [--user USER_ID] - Ingest single documentation file")
                print("  demo - Show available demo scenarios")
                print("  stats - Show ingestor capabilities")
        else:
            print("Usage: python doc_ingestor.py [ingest|file|demo|stats] [options...]")
            print("Options:")
            print("  --demo              Enable demo mode")
            print("  --user USER_ID      Set user ID")
            print("  --scenario NAME     Set demo scenario (startup/enterprise/freelancer)")
    
    asyncio.run(main())