import os
import ast
import yaml
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
from loguru import logger
from datetime import datetime
import hashlib
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.helpers import get_file_hash, extract_file_metadata, sanitize_text

class CodeParser:
    """
    Enhanced Code Parser: Extracts and processes code files for indexing
    Handles multiple programming languages with syntax-aware parsing
    Supports demo mode with synthetic data
    Now includes context-aware extraction, validation, and enrichment
    """
    
    def __init__(self, config_path: str = None, demo_mode: bool = False, user_id: str = None):
        self.config = self._load_config(config_path)
        self.demo_mode = demo_mode
        self.user_id = user_id or "demo_user"
        self.supported_extensions = self._get_supported_extensions()
        self.language_parsers = self._setup_language_parsers()
        
        
        self._setup_context_patterns()
        
       
        if self.demo_mode:
            self.demo_config = self._load_demo_config()
            logger.info(f"CodeParser initialized in DEMO mode for user: {self.user_id}")
        else:
            logger.info(f"CodeParser initialized in REAL mode for user: {self.user_id}")
        
    def _setup_context_patterns(self):
        """Setup patterns for context-aware extraction and enrichment"""
        
        self.test_patterns = re.compile(r'test_|_test|TestCase|unittest|pytest|@pytest|assert\s+|should_|spec_', re.IGNORECASE)
        
       
        self.api_patterns = re.compile(r'@app\.|@router\.|@get|@post|@put|@delete|@patch|fastapi|flask|endpoint|route|handler', re.IGNORECASE)
        
        
        self.utility_patterns = re.compile(r'util|helper|tool|common|shared|config|constant|settings', re.IGNORECASE)
        
        
        self.model_patterns = re.compile(r'model|schema|entity|dto|pydantic|sqlalchemy|BaseModel|dataclass', re.IGNORECASE)
        
        
        self.database_patterns = re.compile(r'db|database|query|crud|repository|session|migration|orm', re.IGNORECASE)
        
        
        self.auth_patterns = re.compile(r'auth|login|logout|password|token|jwt|session|security|permission', re.IGNORECASE)
        
       
        self.validation_patterns = re.compile(r'valid|check|verify|ensure|confirm|sanitize|clean', re.IGNORECASE)
        
        
        self.processing_patterns = re.compile(r'process|parse|transform|convert|format|serialize|deserialize', re.IGNORECASE)
        
        
        self.complexity_keywords = {
            'simple': ['get', 'set', 'is_', 'has_', 'to_', 'from_', 'init'],
            'moderate': ['process', 'handle', 'manage', 'create', 'update', 'delete', 'validate', 'parse'],
            'complex': ['algorithm', 'optimize', 'calculate', 'transform', 'aggregate', 'analyze', 'orchestrate']
        }
        
        
        self.decorator_patterns = re.compile(r'@(\w+)(?:\.[a-zA-Z_]\w*)*(?:\([^)]*\))?', re.MULTILINE)
    
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from settings.yaml"""
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "settings.yaml"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_demo_config(self) -> Dict:
        """Load demo-specific configuration"""
        demo_config_path = os.path.join(
            os.path.dirname(__file__), "..", "configs", "demo_settings.yaml"
        )
        
        try:
            with open(demo_config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning("Demo config not found, using defaults")
            return {
                'demo_data_path': os.path.join(os.path.dirname(__file__), "..", "demo", "sample_data", "code_samples"),
                'scenarios': ['startup', 'enterprise', 'freelancer']
            }
    
    def _get_supported_extensions(self) -> Set[str]:
        """Get supported file extensions from config"""
        return set(self.config['data_sources']['codebase']['extensions'])
    
    def _setup_language_parsers(self) -> Dict[str, Any]:
        """Setup language-specific parsers"""
        return {
            '.py': self._parse_python,
            '.js': self._parse_javascript,
            '.ts': self._parse_typescript,
            '.jsx': self._parse_jsx,
            '.tsx': self._parse_tsx,
            '.java': self._parse_java,
            '.go': self._parse_go,
            '.rs': self._parse_rust,
            '.cpp': self._parse_cpp,
            '.c': self._parse_c,
            '.h': self._parse_header
        }
    
    def _validate_code_structure(self, structure: Dict[str, Any]) -> bool:
        """Validate extracted code structure for quality and completeness"""
       
        if not structure.get('name') or not structure.get('content'):
            return False
        
       
        content = structure.get('content', '').strip()
        if len(content) < 10:
            return False
        
        
        name = structure.get('name', '')
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name) and structure.get('type') != 'file':
            return False
        
       
        if any(pattern in name.lower() for pattern in ['__pycache__', '.pyc', 'temp', 'tmp']):
            return False
        
        return True
    
    def _enrich_code_structure(self, structure: Dict[str, Any], file_content: str, file_path: str) -> Dict[str, Any]:
        """Add context-aware enrichment to code structures"""
        name = structure.get('name', '').lower()
        content = structure.get('content', '').lower()
        structure_type = structure.get('type', '')
        
        
        if 'enrichment' not in structure:
            structure['enrichment'] = {}
        
        
        purpose = self._infer_purpose(name, content, file_path)
        if purpose:
            structure['enrichment']['purpose'] = purpose
        
       
        category = self._detect_code_category(name, content, file_path)
        if category:
            structure['enrichment']['category'] = category
        
        complexity = self._assess_complexity(structure, content)
        structure['enrichment']['complexity'] = complexity
        
       
        semantic_info = self._extract_semantic_info(structure, content)
        structure['enrichment'].update(semantic_info)
        
        
        structure['enrichment']['llm_summary'] = self._create_llm_summary(structure)
        
        return structure
    
    def _infer_purpose(self, name: str, content: str, file_path: str) -> Optional[str]:
        """Infer the purpose of a code structure from name and content"""
       
        if self.test_patterns.search(name) or self.test_patterns.search(content):
            return 'testing'
        elif self.api_patterns.search(content) or 'endpoint' in name:
            return 'api_endpoint'
        elif self.auth_patterns.search(name) or self.auth_patterns.search(content):
            return 'authentication'
        elif self.validation_patterns.search(name) or self.validation_patterns.search(content):
            return 'validation'
        elif self.database_patterns.search(name) or self.database_patterns.search(content):
            return 'database_operation'
        elif self.processing_patterns.search(name) or self.processing_patterns.search(content):
            return 'data_processing'
        elif self.utility_patterns.search(name) or self.utility_patterns.search(file_path):
            return 'utility'
        elif self.model_patterns.search(name) or self.model_patterns.search(content):
            return 'data_model'
        elif 'config' in name or 'setting' in name:
            return 'configuration'
        elif 'main' in name or '__main__' in content:
            return 'entry_point'
        
        return None
    
    def _detect_code_category(self, name: str, content: str, file_path: str) -> Optional[str]:
        """Detect high-level category of code"""
        file_path_lower = file_path.lower()
        
        
        if any(pattern in file_path_lower for pattern in ['test', 'spec']):
            return 'test'
        elif any(pattern in file_path_lower for pattern in ['api', 'route', 'endpoint']):
            return 'api'
        elif any(pattern in file_path_lower for pattern in ['model', 'schema']):
            return 'model'
        elif any(pattern in file_path_lower for pattern in ['util', 'helper', 'common']):
            return 'utility'
        elif any(pattern in file_path_lower for pattern in ['config', 'setting']):
            return 'configuration'
        elif any(pattern in file_path_lower for pattern in ['db', 'database', 'migration']):
            return 'database'
        elif any(pattern in file_path_lower for pattern in ['auth', 'security']):
            return 'security'
        
        
        if self.test_patterns.search(content):
            return 'test'
        elif self.api_patterns.search(content):
            return 'api'
        elif self.model_patterns.search(content):
            return 'model'
        elif self.utility_patterns.search(content):
            return 'utility'
        
        return 'business_logic' 
    
    def _assess_complexity(self, structure: Dict[str, Any], content: str) -> str:
        """Assess complexity using enhanced heuristics"""
        name = structure.get('name', '').lower()
        lines = len(content.split('\n'))
        
        
        for complexity_level, keywords in self.complexity_keywords.items():
            if any(keyword in name for keyword in keywords):
                
                if complexity_level == 'simple' and lines > 50:
                    return 'moderate'
                elif complexity_level == 'moderate' and lines > 100:
                    return 'complex'
                return complexity_level
        
        
        control_structures = len(re.findall(r'\b(if|for|while|try|catch|switch|case|elif|else)\b', content, re.IGNORECASE))
        nested_depth = content.count('    ')  
        
        complexity_score = lines + (control_structures * 5) + (nested_depth * 2)
        
        if complexity_score < 30:
            return 'simple'
        elif complexity_score < 100:
            return 'moderate'
        else:
            return 'complex'
    
    def _extract_semantic_info(self, structure: Dict[str, Any], content: str) -> Dict[str, Any]:
        """Extract semantic information for better LLM understanding"""
        semantic_info = {}
        
        
        concepts = self._extract_key_concepts(content)
        if concepts:
            semantic_info['key_concepts'] = concepts
        
        
        frameworks = self._detect_frameworks(content)
        if frameworks:
            semantic_info['frameworks'] = frameworks
        
        
        patterns = self._detect_design_patterns(content)
        if patterns:
            semantic_info['design_patterns'] = patterns
        
        
        maintainability = self._assess_maintainability(structure, content)
        semantic_info['maintainability'] = maintainability
        
        return semantic_info
    
    def _extract_key_concepts(self, content: str) -> List[str]:
        """Extract key concepts and domain entities from code"""
        concepts = []
        
        
        class_matches = re.findall(r'class\s+([A-Z][a-zA-Z0-9_]*)', content)
        concepts.extend(class_matches)
        
        
        func_matches = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
        domain_functions = [f for f in func_matches if not f.startswith('_') and len(f) > 3]
        concepts.extend(domain_functions[:5])  
        
        
        string_matches = re.findall(r'["\']([A-Z][a-zA-Z\s]+)["\']', content)
        domain_strings = [s for s in string_matches if len(s.split()) <= 3 and s.isalpha()]
        concepts.extend(domain_strings[:3])
        
        return list(set(concepts))
    
    def _detect_frameworks(self, content: str) -> List[str]:
        """Detect frameworks and libraries being used"""
        frameworks = []
        
        framework_patterns = {
            'fastapi': r'from\s+fastapi|import\s+fastapi|FastAPI',
            'flask': r'from\s+flask|import\s+flask|Flask',
            'django': r'from\s+django|import\s+django|Django',
            'react': r'import.*react|from.*react',
            'vue': r'import.*vue|from.*vue',
            'express': r'express\(',
            'spring': r'@SpringBootApplication|@RestController',
            'sqlalchemy': r'from\s+sqlalchemy|import\s+sqlalchemy',
            'pandas': r'import\s+pandas|from\s+pandas',
            'numpy': r'import\s+numpy|from\s+numpy',
            'pytest': r'import\s+pytest|from\s+pytest',
            'unittest': r'import\s+unittest|from\s+unittest'
        }
        
        for framework, pattern in framework_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                frameworks.append(framework)
        
        return frameworks
    
    def _detect_design_patterns(self, content: str) -> List[str]:
        """Detect common design patterns in code"""
        patterns = []
        
        
        if re.search(r'class.*:.*_instance.*=.*None', content, re.DOTALL):
            patterns.append('singleton')
        
        
        if re.search(r'def\s+create|def\s+build|Factory', content):
            patterns.append('factory')
        
        
        if re.search(r'subscribe|notify|observer|listener', content, re.IGNORECASE):
            patterns.append('observer')
        
        
        if re.search(r'strategy|algorithm.*=|policy', content, re.IGNORECASE):
            patterns.append('strategy')
        
       
        if re.search(r'@\w+|decorator', content, re.IGNORECASE):
            patterns.append('decorator')
        
        return patterns
    
    def _assess_maintainability(self, structure: Dict[str, Any], content: str) -> Dict[str, Any]:
        """Assess code maintainability indicators"""
        lines = len(content.split('\n'))
        
       
        has_docstring = bool(structure.get('docstring'))
        has_type_hints = ':' in content and '->' in content
        has_comments = '#' in content
        function_length = lines if structure.get('type') == 'function' else None
        
        maintainability_score = 0
        issues = []
        
        
        if has_docstring:
            maintainability_score += 2
        else:
            issues.append('missing_docstring')
        
        if has_type_hints:
            maintainability_score += 2
        
        if has_comments:
            maintainability_score += 1
        
       
        if function_length and function_length > 50:
            issues.append('long_function')
            maintainability_score -= 1
        
        
        complexity = structure.get('enrichment', {}).get('complexity', 'moderate')
        if complexity == 'complex':
            issues.append('high_complexity')
            maintainability_score -= 1
        
        return {
            'score': max(0, maintainability_score),
            'has_docstring': has_docstring,
            'has_type_hints': has_type_hints,
            'has_comments': has_comments,
            'issues': issues
        }
    
    def _create_llm_summary(self, structure: Dict[str, Any]) -> str:
        """Create LLM-friendly summary of the code structure"""
        name = structure.get('name', 'unknown')
        struct_type = structure.get('type', 'code')
        purpose = structure.get('enrichment', {}).get('purpose')
        category = structure.get('enrichment', {}).get('category')
        complexity = structure.get('enrichment', {}).get('complexity', 'moderate')
        
        
        summary_parts = [f"This is a {complexity} {struct_type} named '{name}'"]
        
        if purpose:
            summary_parts.append(f"with purpose: {purpose.replace('_', ' ')}")
        
        if category:
            summary_parts.append(f"in category: {category.replace('_', ' ')}")
        
        
        docstring = structure.get('docstring')
        if docstring:
            summary_parts.append(f"Description: {docstring[:100]}...")
        
        
        concepts = structure.get('enrichment', {}).get('key_concepts', [])
        if concepts:
            summary_parts.append(f"Key concepts: {', '.join(concepts[:3])}")
        
        return '. '.join(summary_parts) + '.'

    async def parse_codebase(self, base_path: str = None, scenario: str = None) -> List[Dict[str, Any]]:
        """
        Parse entire codebase and extract structured information
        Enhanced with validation and enrichment
        
        Args:
            base_path: Root path to parse (defaults to config path or demo path)
            scenario: Demo scenario to use (startup/enterprise/freelancer)
            
        Returns:
            List of document dictionaries ready for indexing
        """
        if self.demo_mode:
            return await self._parse_demo_codebase(scenario)
        else:
            return await self._parse_real_codebase(base_path)
    
    async def _parse_demo_codebase(self, scenario: str = None) -> List[Dict[str, Any]]:
        """Parse demo codebase with synthetic data"""
        logger.info(f"Parsing DEMO codebase for scenario: {scenario or 'default'}")
        
       
        demo_path = self.demo_config.get('demo_data_path')
        if not demo_path or not os.path.exists(demo_path):
            logger.warning("Demo code samples not found, generating synthetic data")
            return self._generate_synthetic_code_data(scenario)
        
       
        documents = await self._parse_real_codebase(demo_path)
        
        
        for doc in documents:
            doc['metadata'].update({
                'is_demo': True,
                'demo_scenario': scenario or 'default',
                'user_id': self.user_id,
                'demo_note': 'This is synthetic demo data for showcase purposes'
            })
        
        logger.info(f"Generated {len(documents)} DEMO code documents")
        return documents
    
    async def _parse_real_codebase(self, base_path: str = None) -> List[Dict[str, Any]]:
        """Parse real codebase with enhanced validation and enrichment"""
        if not base_path:
            base_path = self.config['data_sources']['codebase']['path']
        
        base_path = Path(base_path).resolve()
        
        if not base_path.exists():
            logger.warning(f"Codebase path does not exist: {base_path}")
            return []
        
        logger.info(f"Starting enhanced codebase parsing from: {base_path}")
        
        documents = []
        ignore_patterns = self.config['data_sources']['codebase']['ignore_patterns']
        
        for file_path in self._walk_directory(base_path, ignore_patterns):
            try:
                if file_path.suffix in self.supported_extensions:
                    file_documents = await self._parse_file(file_path, base_path)
                   
                    for doc in file_documents:
                        if self._validate_parsed_document(doc):
                            documents.append(doc)
                    
            except Exception as e:
                logger.error(f"Error parsing file {file_path}: {str(e)}")
                continue
        
      
        for doc in documents:
            doc['metadata'].update({
                'is_demo': False,
                'user_id': self.user_id
            })
        
        logger.info(f"Parsed {len(documents)} validated code documents from {base_path}")
        return documents
    
    def _validate_parsed_document(self, doc: Dict[str, Any]) -> bool:
        """Validate complete parsed document"""
        metadata = doc.get('metadata', {})
        content = doc.get('content', '')
        
        
        if not content or len(content.strip()) < 10:
            return False
        
        
        if metadata.get('structure_type') == 'function' and 'def ' not in content:
            return False
        
        if metadata.get('structure_type') == 'class' and 'class ' not in content:
            return False
        
        return True
    
    def _generate_synthetic_code_data(self, scenario: str = None) -> List[Dict[str, Any]]:
        """Generate enhanced synthetic code data when demo files don't exist"""
        synthetic_files = [
            {
                'name': 'app.py',
                'language': 'python',
                'content': '''# Main application entry point
import fastapi
from fastapi import FastAPI, HTTPException
from typing import Dict, List
import uvicorn

app = FastAPI(title="Demo API", version="1.0.0")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hello World", "status": "active"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

class UserService:
    """Service for user management"""
    
    def __init__(self):
        self.users = {}
    
    async def create_user(self, user_data: Dict) -> Dict:
        """Create a new user"""
        user_id = len(self.users) + 1
        user = {"id": user_id, **user_data}
        self.users[user_id] = user
        return user
    
    async def get_user(self, user_id: int) -> Dict:
        """Get user by ID"""
        if user_id not in self.users:
            raise HTTPException(status_code=404, detail="User not found")
        return self.users[user_id]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
                'complexity': 'medium',
                'tags': ['api', 'fastapi', 'python', 'web']
            },
            {
                'name': 'components/Dashboard.tsx',
                'language': 'typescript',
                'content': '''import React, { useState, useEffect } from 'react';
import { Card, Button, Alert } from '@/components/ui';

interface DashboardProps {
    userId: string;
    isDemo?: boolean;
}

interface MetricData {
    label: string;
    value: number;
    change: number;
}

export const Dashboard: React.FC<DashboardProps> = ({ userId, isDemo = false }) => {
    const [metrics, setMetrics] = useState<MetricData[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchMetrics = async () => {
            try {
                setLoading(true);
                const response = await fetch(`/api/metrics/${userId}`);
                if (!response.ok) throw new Error('Failed to fetch metrics');
                const data = await response.json();
                setMetrics(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Unknown error');
            } finally {
                setLoading(false);
            }
        };

        fetchMetrics();
    }, [userId]);

    const handleRefresh = () => {
        setError(null);
        fetchMetrics();
    };

    if (loading) return <div className="loading-spinner">Loading...</div>;
    if (error) return <Alert variant="error">{error}</Alert>;

    return (
        <div className="dashboard-container">
            {isDemo && (
                <Alert variant="info">
                    This is demo data for showcase purposes
                </Alert>
            )}
            
            <div className="metrics-grid">
                {metrics.map((metric, index) => (
                    <Card key={index} className="metric-card">
                        <h3>{metric.label}</h3>
                        <div className="metric-value">{metric.value}</div>
                        <div className={`metric-change ${metric.change >= 0 ? 'positive' : 'negative'}`}>
                            {metric.change >= 0 ? '+' : ''}{metric.change}%
                        </div>
                    </Card>
                ))}
            </div>
            
            <Button onClick={handleRefresh} className="refresh-button">
                Refresh Data
            </Button>
        </div>
    );
};

export default Dashboard;
''',
                'complexity': 'medium',
                'tags': ['react', 'typescript', 'dashboard', 'ui']
            },
            {
                'name': 'utils/database.py',
                'language': 'python',
                'content': '''"""Database utilities and connection management"""
import sqlite3
import asyncio
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Async database manager for SQLite operations"""
    
    def __init__(self, db_path: str = "app.db"):
        self.db_path = db_path
        self._connection = None
    
    async def connect(self) -> None:
        """Establish database connection"""
        try:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
            await self._create_tables()
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    async def _create_tables(self) -> None:
        """Create necessary database tables"""
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
        """
        
        create_sessions_table = """
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
        
        cursor = self._connection.cursor()
        cursor.execute(create_users_table)
        cursor.execute(create_sessions_table)
        self._connection.commit()
    
    async def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        cursor = self._connection.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    async def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query"""
        cursor = self._connection.cursor()
        cursor.execute(query, params)
        self._connection.commit()
        return cursor.rowcount
    
    async def close(self) -> None:
        """Close database connection"""
        if self._connection:
            self._connection.close()
            logger.info("Database connection closed")

@asynccontextmanager
async def get_db():
    """Database context manager"""
    db = DatabaseManager()
    try:
        await db.connect()
        yield db
    finally:
        await db.close()
''',
                'complexity': 'high',
                'tags': ['database', 'sqlite', 'async', 'python']
            }
        ]
        
        documents = []
        for i, file_data in enumerate(synthetic_files):
            
            doc = {
                'content': file_data['content'],
                'metadata': {
                    'source_type': 'code',
                    'file_path': file_data['name'],
                    'language': file_data['language'],
                    'structure_type': 'file',
                    'name': Path(file_data['name']).stem,
                    'line_start': 1,
                    'line_end': len(file_data['content'].split('\n')),
                    'file_size': len(file_data['content']),
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'modified_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'content_hash': get_file_hash(file_data['content']),
                    'tags': file_data['tags'],
                    'complexity': file_data['complexity'],
                    'dependencies': [],
                    'is_demo': True,
                    'demo_scenario': scenario or 'default',
                    'user_id': self.user_id,
                    'demo_note': 'This is synthetic demo data for showcase purposes',
                    
                    'enrichment': {
                        'purpose': self._infer_purpose(file_data['name'], file_data['content'], file_data['name']),
                        'category': self._detect_code_category(file_data['name'], file_data['content'], file_data['name']),
                        'complexity': file_data['complexity'],
                        'frameworks': self._detect_frameworks(file_data['content']),
                        'llm_summary': f"This is a {file_data['complexity']} complexity {file_data['language']} file named {file_data['name']} containing {', '.join(file_data['tags'])} code."
                    }
                }
            }
            documents.append(doc)
        
        logger.info(f"Generated {len(documents)} enhanced synthetic code documents")
        return documents
    
    def _walk_directory(self, base_path: Path, ignore_patterns: List[str]) -> List[Path]:
        """Walk directory and yield relevant files"""
        files = []
        
        for root, dirs, filenames in os.walk(base_path):
            
            dirs[:] = [d for d in dirs if not self._should_ignore(d, ignore_patterns)]
            
            for filename in filenames:
                file_path = Path(root) / filename
                
                
                if self._should_ignore(str(file_path), ignore_patterns):
                    continue
                
                
                if file_path.suffix in self.supported_extensions:
                    files.append(file_path)
        
        return files
    
    def _should_ignore(self, path: str, ignore_patterns: List[str]) -> bool:
        """Check if path should be ignored based on patterns"""
        path_str = str(path).lower()
        
        for pattern in ignore_patterns:
            if pattern.lower() in path_str:
                return True
        
        return False
    
    async def _parse_file(self, file_path: Path, base_path: Path) -> List[Dict[str, Any]]:
        """Parse a single file and extract code structures with enhanced processing"""
        try:
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return []
            
           
            relative_path = file_path.relative_to(base_path)
            
            
            file_metadata = extract_file_metadata(file_path)
            
            
            extension = file_path.suffix
            parser_func = self.language_parsers.get(extension, self._parse_generic)
            
            parsed_structures = parser_func(content, str(relative_path))
            
            
            validated_structures = []
            for structure in parsed_structures:
                if self._validate_code_structure(structure):
                    enriched_structure = self._enrich_code_structure(structure, content, str(relative_path))
                    validated_structures.append(enriched_structure)
            
            
            documents = []
            for structure in validated_structures:
                doc = {
                    'content': structure['content'],
                    'metadata': {
                        'source_type': 'code',
                        'file_path': str(relative_path),
                        'language': self._get_language_from_extension(extension),
                        'structure_type': structure['type'],
                        'name': structure.get('name', ''),
                        'line_start': structure.get('line_start', 1),
                        'line_end': structure.get('line_end', 1),
                        'file_size': file_metadata['size'],
                        'created_at': file_metadata['created_at'],
                        'modified_at': file_metadata['modified_at'],
                        'content_hash': get_file_hash(content),
                        'tags': structure.get('tags', []),
                        'complexity': structure.get('complexity', 'medium'),
                        'dependencies': structure.get('dependencies', []),
                        
                        'enrichment': structure.get('enrichment', {}),
                        
                        'docstring': structure.get('docstring', ''),
                        'arguments': structure.get('arguments', []),
                        'methods': structure.get('methods', []),
                        'base_classes': structure.get('base_classes', []),
                        'is_async': structure.get('is_async', False)
                    }
                }
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {str(e)}")
            return []
    
    def _get_language_from_extension(self, extension: str) -> str:
        """Map file extension to language name"""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c'
        }
        return language_map.get(extension, 'unknown')
    
    
    def _parse_python(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Enhanced Python parsing with better edge case handling"""
        structures = []
        
        try:
            tree = ast.parse(content)
            lines = content.split('\n')
            
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_info = self._extract_python_function_enhanced(node, lines, file_path, content)
                    if func_info:  
                        structures.append(func_info)
                    
                elif isinstance(node, ast.ClassDef):
                    class_info = self._extract_python_class_enhanced(node, lines, file_path, content)
                    if class_info:  
                        structures.append(class_info)
            
            
            module_info = {
                'type': 'module',
                'name': Path(file_path).stem,
                'content': content,
                'line_start': 1,
                'line_end': len(lines),
                'tags': self._extract_python_imports(tree),
                'complexity': self._estimate_complexity(content),
                'dependencies': self._extract_python_imports(tree)
            }
            structures.append(module_info)
            
        except SyntaxError as e:
            logger.warning(f"Syntax error in Python file {file_path}: {str(e)}")
            
            structures = self._parse_python_fallback(content, file_path)
        
        return structures
    
    def _extract_python_function_enhanced(self, node: ast.FunctionDef, lines: List[str], file_path: str, full_content: str) -> Optional[Dict[str, Any]]:
        """Enhanced Python function extraction with better handling of edge cases"""
        try:
            start_line = node.lineno
            end_line = getattr(node, 'end_lineno', None) or start_line
            
            
            if end_line == start_line:
                end_line = self._find_function_end_line(lines, start_line, node.name)
            
            
            func_lines = lines[start_line-1:end_line]
            func_content = '\n'.join(func_lines)
            
            
            if len(func_content.strip()) < 10 or 'def ' not in func_content:
                return None
            
            
            docstring = ast.get_docstring(node) or ""
            
            
            args = []
            for arg in node.args.args:
                arg_info = {'name': arg.arg}
                if arg.annotation:
                    arg_info['type'] = ast.unparse(arg.annotation) if hasattr(ast, 'unparse') else str(arg.annotation)
                args.append(arg_info)
            
            
            decorators = []
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name):
                    decorators.append(decorator.id)
                elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                    decorators.append(decorator.func.id)
                elif hasattr(ast, 'unparse'):
                    decorators.append(ast.unparse(decorator))
            
            
            return_type = None
            if node.returns:
                return_type = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
            
            return {
                'type': 'function',
                'name': node.name,
                'content': func_content,
                'line_start': start_line,
                'line_end': end_line,
                'tags': ['function', node.name] + [arg['name'] for arg in args],
                'complexity': self._estimate_function_complexity_enhanced(node, func_content),
                'docstring': docstring,
                'arguments': args,
                'decorators': decorators,
                'return_type': return_type,
                'is_async': isinstance(node, ast.AsyncFunctionDef),
                'is_private': node.name.startswith('_'),
                'is_property': 'property' in decorators
            }
        except Exception as e:
            logger.warning(f"Error extracting function {getattr(node, 'name', 'unknown')}: {e}")
            return None
    
    def _extract_python_class_enhanced(self, node: ast.ClassDef, lines: List[str], file_path: str, full_content: str) -> Optional[Dict[str, Any]]:
        """Enhanced Python class extraction with better method detection"""
        try:
            start_line = node.lineno
            end_line = getattr(node, 'end_lineno', None) or start_line
            
            
            if end_line == start_line:
                end_line = self._find_class_end_line(lines, start_line, node.name)
            
            
            class_lines = lines[start_line-1:end_line]
            class_content = '\n'.join(class_lines)
            
            
            if len(class_content.strip()) < 10 or 'class ' not in class_content:
                return None
            
            
            docstring = ast.get_docstring(node) or ""
            
           
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_info = {
                        'name': item.name,
                        'is_async': isinstance(item, ast.AsyncFunctionDef),
                        'is_private': item.name.startswith('_'),
                        'is_static': any(isinstance(d, ast.Name) and d.id == 'staticmethod' for d in item.decorator_list),
                        'is_classmethod': any(isinstance(d, ast.Name) and d.id == 'classmethod' for d in item.decorator_list),
                        'is_property': any(isinstance(d, ast.Name) and d.id == 'property' for d in item.decorator_list)
                    }
                    methods.append(method_info)
            
          
            base_classes = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    base_classes.append(base.id)
                elif hasattr(ast, 'unparse'):
                    base_classes.append(ast.unparse(base))
            
           
            decorators = []
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name):
                    decorators.append(decorator.id)
                elif hasattr(ast, 'unparse'):
                    decorators.append(ast.unparse(decorator))
            
            return {
                'type': 'class',
                'name': node.name,
                'content': class_content,
                'line_start': start_line,
                'line_end': end_line,
                'tags': ['class', node.name] + [m['name'] for m in methods],
                'complexity': self._estimate_class_complexity_enhanced(node, class_content),
                'docstring': docstring,
                'methods': methods,
                'base_classes': base_classes,
                'decorators': decorators,
                'is_abstract': any('ABC' in bc or 'abstract' in bc.lower() for bc in base_classes)
            }
        except Exception as e:
            logger.warning(f"Error extracting class {getattr(node, 'name', 'unknown')}: {e}")
            return None
    
    def _find_function_end_line(self, lines: List[str], start_line: int, func_name: str) -> int:
        """Find the end line of a function by analyzing indentation"""
        if start_line >= len(lines):
            return start_line
        
        
        func_line = lines[start_line - 1]
        func_indent = len(func_line) - len(func_line.lstrip())
        
        
        for i in range(start_line, len(lines)):
            line = lines[i]
            if line.strip():  
                line_indent = len(line) - len(line.lstrip())
                if line_indent <= func_indent:
                    return i
        
        return len(lines)
    
    def _find_class_end_line(self, lines: List[str], start_line: int, class_name: str) -> int:
        """Find the end line of a class by analyzing indentation"""
        if start_line >= len(lines):
            return start_line
        
       
        class_line = lines[start_line - 1]
        class_indent = len(class_line) - len(class_line.lstrip())
        
       
        for i in range(start_line, len(lines)):
            line = lines[i]
            if line.strip():  
                line_indent = len(line) - len(line.lstrip())
                if line_indent <= class_indent:
                    return i
        
        return len(lines)
    
    def _parse_python_fallback(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Fallback Python parsing using regex when AST fails"""
        structures = []
        lines = content.split('\n')
        
        
        func_pattern = r'^(\s*)def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        for i, line in enumerate(lines):
            match = re.match(func_pattern, line)
            if match:
                indent, func_name = match.groups()
                end_line = self._find_block_end_regex(lines, i, len(indent))
                func_content = '\n'.join(lines[i:end_line])
                
                structures.append({
                    'type': 'function',
                    'name': func_name,
                    'content': func_content,
                    'line_start': i + 1,
                    'line_end': end_line,
                    'tags': ['function', func_name],
                    'complexity': 'medium',
                    'docstring': '',
                    'arguments': [],
                    'is_async': 'async def' in line
                })
        
        
        class_pattern = r'^(\s*)class\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        for i, line in enumerate(lines):
            match = re.match(class_pattern, line)
            if match:
                indent, class_name = match.groups()
                end_line = self._find_block_end_regex(lines, i, len(indent))
                class_content = '\n'.join(lines[i:end_line])
                
                structures.append({
                    'type': 'class',
                    'name': class_name,
                    'content': class_content,
                    'line_start': i + 1,
                    'line_end': end_line,
                    'tags': ['class', class_name],
                    'complexity': 'medium',
                    'docstring': '',
                    'methods': [],
                    'base_classes': []
                })
        
        return structures
    
    def _find_block_end_regex(self, lines: List[str], start: int, base_indent: int) -> int:
        """Find end of code block using indentation analysis"""
        for i in range(start + 1, len(lines)):
            line = lines[i]
            if line.strip():
                line_indent = len(line) - len(line.lstrip())
                if line_indent <= base_indent:
                    return i
        return len(lines)
    
    def _extract_python_imports(self, tree: ast.AST) -> List[str]:
        """Extract import information from Python AST"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        return imports
    
    def _estimate_function_complexity_enhanced(self, node: ast.FunctionDef, content: str) -> str:
        """Enhanced function complexity estimation"""
        
        nested_count = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                nested_count += 1
        
       
        param_count = len(node.args.args)
        
        
        line_count = len(content.split('\n'))
        
       
        complexity_score = nested_count * 2 + param_count + (line_count // 10)
        
        if complexity_score < 5:
            return 'simple'
        elif complexity_score < 15:
            return 'moderate'
        else:
            return 'complex'
    
    def _estimate_class_complexity_enhanced(self, node: ast.ClassDef, content: str) -> str:
        """Enhanced class complexity estimation"""
        method_count = len([n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))])
        line_count = len(content.split('\n'))
        base_class_count = len(node.bases)
        
        complexity_score = method_count + (line_count // 20) + base_class_count * 2
        
        if complexity_score < 8:
            return 'simple'
        elif complexity_score < 20:
            return 'moderate'
        else:
            return 'complex'
    
   
    def _parse_javascript(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse JavaScript files with enhanced validation"""
        structures = self._parse_generic_with_patterns(
            content, file_path, 'javascript',
            function_patterns=[r'function\s+(\w+)', r'(\w+)\s*:\s*function', r'const\s+(\w+)\s*=.*=>'],
            class_patterns=[r'class\s+(\w+)']
        )
        return [s for s in structures if self._validate_code_structure(s)]
    
    def _parse_typescript(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse TypeScript files with enhanced validation"""
        structures = self._parse_generic_with_patterns(
            content, file_path, 'typescript',
            function_patterns=[r'function\s+(\w+)', r'(\w+)\s*:\s*function', r'const\s+(\w+)\s*=.*=>', r'(\w+)\s*\([^)]*\)\s*:\s*\w+'],
            class_patterns=[r'class\s+(\w+)', r'interface\s+(\w+)', r'type\s+(\w+)']
        )
        return [s for s in structures if self._validate_code_structure(s)]
    
    def _parse_jsx(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse JSX files with enhanced validation"""
        structures = self._parse_javascript(content, file_path)
        
       
        for structure in structures:
            structure['tags'].extend(['react', 'jsx'])
            
        return structures
    
    def _parse_tsx(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse TSX files with enhanced validation"""
        structures = self._parse_typescript(content, file_path)
        
        
        for structure in structures:
            structure['tags'].extend(['react', 'tsx'])
            
        return structures
    
    def _parse_java(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse Java files with enhanced validation"""
        structures = self._parse_generic_with_patterns(
            content, file_path, 'java',
            function_patterns=[r'(public|private|protected)?\s*\w+\s+(\w+)\s*\('],
            class_patterns=[r'(public|private)?\s*class\s+(\w+)', r'interface\s+(\w+)']
        )
        return [s for s in structures if self._validate_code_structure(s)]
    
    def _parse_go(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse Go files with enhanced validation"""
        structures = self._parse_generic_with_patterns(
            content, file_path, 'go',
            function_patterns=[r'func\s+(\w+)', r'func\s+\(\w+\s+\*?\w+\)\s+(\w+)'],
            class_patterns=[r'type\s+(\w+)\s+struct']
        )
        return [s for s in structures if self._validate_code_structure(s)]
    
    def _parse_rust(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse Rust files with enhanced validation"""
        structures = self._parse_generic_with_patterns(
            content, file_path, 'rust',
            function_patterns=[r'fn\s+(\w+)', r'pub\s+fn\s+(\w+)'],
            class_patterns=[r'struct\s+(\w+)', r'enum\s+(\w+)', r'trait\s+(\w+)']
        )
        return [s for s in structures if self._validate_code_structure(s)]
    
    def _parse_cpp(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse C++ files with enhanced validation"""
        structures = self._parse_generic_with_patterns(
            content, file_path, 'cpp',
            function_patterns=[r'\w+\s+(\w+)\s*\(', r'(\w+)::\w+\s*\('],
            class_patterns=[r'class\s+(\w+)', r'struct\s+(\w+)']
        )
        return [s for s in structures if self._validate_code_structure(s)]
    
    def _parse_c(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse C files with enhanced validation"""
        structures = self._parse_generic_with_patterns(
            content, file_path, 'c',
            function_patterns=[r'\w+\s+(\w+)\s*\('],
            class_patterns=[r'struct\s+(\w+)', r'typedef\s+struct.*?(\w+)']
        )
        return [s for s in structures if self._validate_code_structure(s)]
    
    def _parse_header(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse header files (.h) with enhanced validation"""
        structures = self._parse_generic_with_patterns(
            content, file_path, 'c',
            function_patterns=[r'\w+\s+(\w+)\s*\('],
            class_patterns=[r'struct\s+(\w+)', r'typedef\s+struct.*?(\w+)']
        )
        return [s for s in structures if self._validate_code_structure(s)]
    
    def _parse_generic_with_patterns(
        self, 
        content: str, 
        file_path: str, 
        language: str,
        function_patterns: List[str] = None,
        class_patterns: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Generic parsing using regex patterns with enhanced extraction"""
        import re
        
        structures = []
        lines = content.split('\n')
        
       
        if function_patterns:
            for pattern in function_patterns:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    func_name = match.group(1) if match.groups() else 'unknown'
                    if len(func_name) > 1 and func_name.replace('_', '').isalnum():  
                        line_num = content[:match.start()].count('\n') + 1
                        
                        structures.append({
                            'type': 'function',
                            'name': func_name,
                            'content': self._extract_block_content(lines, line_num),
                            'line_start': line_num,
                            'line_end': line_num + 10,
                            'tags': ['function', func_name],
                            'complexity': 'medium',
                            'docstring': '',
                            'arguments': []
                        })
        
     
        if class_patterns:
            for pattern in class_patterns:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    class_name = match.group(1) if match.groups() else match.group(2) if len(match.groups()) > 1 else 'unknown'
                    if len(class_name) > 1 and class_name.replace('_', '').isalnum():  # Validate name
                        line_num = content[:match.start()].count('\n') + 1
                        
                        structures.append({
                            'type': 'class',
                            'name': class_name,
                            'content': self._extract_block_content(lines, line_num, 30),
                            'line_start': line_num,
                            'line_end': line_num + 20,
                            'tags': ['class', class_name],
                            'complexity': 'medium',
                            'docstring': '',
                            'methods': []
                        })
        
       
        structures.append({
            'type': 'file',
            'name': Path(file_path).stem,
            'content': content,
            'line_start': 1,
            'line_end': len(lines),
            'tags': [language, 'file'],
            'complexity': self._estimate_complexity(content)
        })
        
        return structures
    
    def _parse_generic(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Generic parsing for unsupported file types with validation"""
        lines = content.split('\n')
        
        structure = {
            'type': 'file',
            'name': Path(file_path).stem,
            'content': content,
            'line_start': 1,
            'line_end': len(lines),
            'tags': ['file', 'generic'],
            'complexity': self._estimate_complexity(content)
        }
        
        return [structure] if self._validate_code_structure(structure) else []
    
    def _extract_block_content(self, lines: List[str], start_line: int, max_lines: int = 20) -> str:
        """Extract a block of content around a specific line"""
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), start_idx + max_lines)
        return '\n'.join(lines[start_idx:end_idx])
    
    def _estimate_complexity(self, content: str) -> str:
        """Estimate code complexity based on enhanced metrics"""
        lines = len(content.split('\n'))
        
 
        complexity_indicators = {
            'if': 1, 'for': 2, 'while': 2, 'try': 3, 'catch': 2, 
            'switch': 2, 'case': 1, 'async': 2, 'await': 1,
            'recursive': 5, 'nested': 3
        }
        
        indicator_score = 0
        content_lower = content.lower()
        for indicator, weight in complexity_indicators.items():
            indicator_score += content_lower.count(indicator) * weight
        
     
        total_score = (lines // 10) + indicator_score
        
        if total_score < 15:
            return 'simple'
        elif total_score < 50:
            return 'moderate'
        else:
            return 'complex'

   
    def set_demo_mode(self, demo_mode: bool, scenario: str = None) -> None:
        """Toggle demo mode on/off"""
        self.demo_mode = demo_mode
        if demo_mode:
            logger.info(f"Switched to DEMO mode with scenario: {scenario or 'default'}")
        else:
            logger.info("Switched to REAL mode")
    
    def get_demo_scenarios(self) -> List[str]:
        """Get available demo scenarios"""
        if hasattr(self, 'demo_config'):
            return self.demo_config.get('scenarios', [])
        return []