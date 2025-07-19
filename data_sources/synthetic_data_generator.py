import os
import yaml
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.helpers import get_file_hash, sanitize_text, extract_technical_terms
from dotenv import load_dotenv
load_dotenv()

class SyntheticDataGenerator:
    
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
            return {
                'scenarios': ['startup', 'enterprise', 'freelancer'],
                'data_volume': {
                    'code_files': 20,
                    'documents': 15,
                    'prs': 10,
                    'conversations': 8,
                    'tickets': 12
                }
            }
    
    async def generate_all_synthetic_data(self, scenario: str = None) -> Dict[str, List[Dict[str, Any]]]:
        scenario = scenario or 'startup'
        logger.info(f"Generating complete synthetic dataset for scenario: {scenario}")
        
        data = {
            'code': self._generate_code_data(scenario),
            'documents': self._generate_document_data(scenario),
            'pull_requests': self._generate_pr_data(scenario),
            'conversations': self._generate_conversation_data(scenario),
            'tickets': self._generate_ticket_data(scenario)
        }
        
        total_items = sum(len(items) for items in data.values())
        logger.info(f"Generated {total_items} synthetic data items for {scenario} scenario")
        
        return data
    
    def _generate_code_data(self, scenario: str) -> List[Dict[str, Any]]:
        if scenario == 'enterprise':
            return self._enterprise_code_data()
        elif scenario == 'freelancer':
            return self._freelancer_code_data()
        else:
            return self._startup_code_data()
    
    def _startup_code_data(self) -> List[Dict[str, Any]]:
        files = [
            {
                'file_path': 'src/auth/login.py',
                'content': '''from fastapi import HTTPException, Depends
from passlib.context import CryptContext
from jose import jwt
import bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.secret_key = "your-secret-key"
        self.algorithm = "HS256"
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
''',
                'language': 'python',
                'complexity': 'medium',
                'tags': ['authentication', 'security', 'fastapi']
            },
            {
                'file_path': 'frontend/components/Dashboard.tsx',
                'content': '''import React, { useState, useEffect } from 'react';
import { Card, Grid, Typography } from '@mui/material';

interface DashboardProps {
    userId: string;
}

export const Dashboard: React.FC<DashboardProps> = ({ userId }) => {
    const [metrics, setMetrics] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(`/api/users/${userId}/metrics`);
                const data = await response.json();
                setMetrics(data);
            } catch (error) {
                console.error('Failed to fetch metrics:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [userId]);

    if (loading) return <div>Loading...</div>;

    return (
        <Grid container spacing={3}>
            {metrics.map((metric, index) => (
                <Grid item xs={12} md={6} key={index}>
                    <Card>
                        <Typography variant="h6">{metric.title}</Typography>
                        <Typography variant="h4">{metric.value}</Typography>
                    </Card>
                </Grid>
            ))}
        </Grid>
    );
};
''',
                'language': 'typescript',
                'complexity': 'medium',
                'tags': ['react', 'dashboard', 'frontend']
            }
        ]
        
        return self._format_code_files(files)
    
    def _enterprise_code_data(self) -> List[Dict[str, Any]]:
        files = [
            {
                'file_path': 'services/auth-service/src/main.py',
                'content': '''from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import get_db
from .auth import AuthManager
from .monitoring import setup_metrics

app = FastAPI(title="Authentication Service", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth_manager = AuthManager()
setup_metrics(app)

@app.post("/auth/login")
async def login(credentials: UserCredentials, db: Session = Depends(get_db)):
    try:
        user = auth_manager.authenticate_user(db, credentials.email, credentials.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = auth_manager.create_access_token(user.id)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication service error")
''',
                'language': 'python',
                'complexity': 'high',
                'tags': ['microservices', 'authentication', 'fastapi']
            },
            {
                'file_path': 'infrastructure/k8s/auth-service.yaml',
                'content': '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: auth-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: auth-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
''',
                'language': 'yaml',
                'complexity': 'high',
                'tags': ['kubernetes', 'infrastructure', 'deployment']
            }
        ]
        
        return self._format_code_files(files)
    
    def _freelancer_code_data(self) -> List[Dict[str, Any]]:
        files = [
            {
                'file_path': 'src/components/ThemeToggle.tsx',
                'content': '''import React from 'react';
import { IconButton, useTheme } from '@mui/material';
import { Brightness4, Brightness7 } from '@mui/icons-material';
import { useThemeContext } from '../contexts/ThemeContext';

export const ThemeToggle: React.FC = () => {
    const theme = useTheme();
    const { toggleTheme } = useThemeContext();

    return (
        <IconButton 
            onClick={toggleTheme} 
            color="inherit"
            aria-label="toggle theme"
        >
            {theme.palette.mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
        </IconButton>
    );
};
''',
                'language': 'typescript',
                'complexity': 'low',
                'tags': ['react', 'theme', 'ui']
            },
            {
                'file_path': 'src/utils/imageOptimizer.js',
                'content': '''const sharp = require('sharp');
const fs = require('fs').promises;
const path = require('path');

class ImageOptimizer {
    constructor(options = {}) {
        this.quality = options.quality || 80;
        this.formats = options.formats || ['webp', 'jpeg'];
        this.sizes = options.sizes || [480, 768, 1024, 1200];
    }

    async optimizeImage(inputPath, outputDir) {
        const filename = path.parse(inputPath).name;
        const results = [];

        for (const format of this.formats) {
            for (const size of this.sizes) {
                const outputPath = path.join(outputDir, `${filename}-${size}w.${format}`);
                
                await sharp(inputPath)
                    .resize(size, null, { withoutEnlargement: true })
                    .toFormat(format, { quality: this.quality })
                    .toFile(outputPath);
                
                results.push({
                    size,
                    format,
                    path: outputPath
                });
            }
        }

        return results;
    }

    async generateSrcSet(images) {
        return images.map(img => `${img.path} ${img.size}w`).join(', ');
    }
}

module.exports = ImageOptimizer;
''',
                'language': 'javascript',
                'complexity': 'medium',
                'tags': ['optimization', 'images', 'performance']
            }
        ]
        
        return self._format_code_files(files)
    
    def _format_code_files(self, files: List[Dict]) -> List[Dict[str, Any]]:
        formatted_files = []
        base_date = datetime.now()
        
        for i, file_data in enumerate(files):
            doc = {
                'content': file_data['content'],
                'metadata': {
                    'source_type': 'code',
                    'file_path': file_data['file_path'],
                    'language': file_data['language'],
                    'structure_type': 'file',
                    'name': os.path.splitext(os.path.basename(file_data['file_path']))[0],
                    'line_start': 1,
                    'line_end': len(file_data['content'].split('\n')),
                    'file_size': len(file_data['content']),
                    'created_at': (base_date - timedelta(days=i*2)).isoformat(),
                    'modified_at': (base_date - timedelta(hours=i*6)).isoformat(),
                    'content_hash': get_file_hash(file_data['content']),
                    'tags': file_data['tags'],
                    'complexity': file_data['complexity'],
                    'dependencies': [],
                    'is_demo': True,
                    'user_id': self.user_id,
                    'demo_note': 'This is synthetic demo data for showcase purposes'
                }
            }
            formatted_files.append(doc)
        
        return formatted_files
    
    def _generate_document_data(self, scenario: str) -> List[Dict[str, Any]]:
        docs = [
            {
                'title': 'API Documentation',
                'content': '''# API Reference Guide

## Authentication Endpoints

### POST /auth/login
Authenticate user and receive access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### POST /auth/register
Create new user account.

## User Management

### GET /users/profile
Get current user profile information.

### PUT /users/profile
Update user profile data.

Rate limiting: 100 requests per minute per user.
''',
                'difficulty': 'intermediate',
                'tags': ['api', 'documentation', 'authentication']
            },
            {
                'title': 'Setup Guide',
                'content': '''# Project Setup Guide

## Prerequisites
- Node.js 18+
- Python 3.9+
- Docker (optional)

## Installation Steps

1. Clone the repository
```bash
git clone https://github.com/company/project.git
cd project
```

2. Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

3. Install frontend dependencies
```bash
cd frontend
npm install
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application
```bash
# Backend
python main.py

# Frontend (new terminal)
npm run dev
```

## Configuration

Environment variables:
- `DATABASE_URL`: Database connection string
- `JWT_SECRET`: Secret key for token generation
- `REDIS_URL`: Redis connection for caching
''',
                'difficulty': 'beginner',
                'tags': ['setup', 'installation', 'guide']
            }
        ]
        
        formatted_docs = []
        base_date = datetime.now()
        
        for i, doc_data in enumerate(docs):
            doc = {
                'content': sanitize_text(doc_data['content']),
                'metadata': {
                    'source_type': 'documentation',
                    'file_path': f"{doc_data['title'].lower().replace(' ', '_')}.md",
                    'section_title': doc_data['title'],
                    'section_level': 1,
                    'file_size': len(doc_data['content']),
                    'created_at': (base_date - timedelta(days=i*3)).isoformat(),
                    'modified_at': (base_date - timedelta(hours=i*8)).isoformat(),
                    'content_hash': get_file_hash(doc_data['content']),
                    'tags': doc_data['tags'],
                    'difficulty': doc_data['difficulty'],
                    'doc_type': 'markdown',
                    'keywords': extract_technical_terms(doc_data['content'])[:10],
                    'is_demo': True,
                    'user_id': self.user_id,
                    'demo_note': 'This is synthetic demo data for showcase purposes'
                }
            }
            formatted_docs.append(doc)
        
        return formatted_docs
    
    def _generate_pr_data(self, scenario: str) -> List[Dict[str, Any]]:
        if scenario == 'enterprise':
            prs = [
                {
                    'number': 1,
                    'title': 'Implement circuit breaker pattern for external services',
                    'body': '''## Overview
Add circuit breaker pattern to prevent cascade failures when external services are down.

## Changes
- Added CircuitBreaker class with configurable thresholds
- Integrated with API client for external service calls
- Added metrics and monitoring for circuit breaker states
- Fallback mechanisms for critical operations

## Testing
- Unit tests for circuit breaker logic
- Integration tests with service failures
- Load testing to verify performance impact
''',
                    'state': 'merged',
                    'author': 'reliability-engineer',
                    'additions': 342,
                    'deletions': 28,
                    'changed_files': 12
                }
            ]
        else:
            prs = [
                {
                    'number': 1,
                    'title': 'Add user registration form validation',
                    'body': '''## Summary
Implement client-side and server-side validation for user registration form.

## Changes
- Added email format validation
- Password strength requirements
- Confirm password matching
- Real-time validation feedback
- Server-side validation with proper error messages

## Testing
- Form validation unit tests
- E2E tests for registration flow
''',
                    'state': 'open',
                    'author': 'frontend-dev',
                    'additions': 156,
                    'deletions': 12,
                    'changed_files': 5
                }
            ]
        
        formatted_prs = []
        base_date = datetime.now()
        
        for i, pr_data in enumerate(prs):
            doc = {
                'content': sanitize_text(pr_data['body']),
                'metadata': {
                    'source_type': 'pull_request',
                    'pr_number': pr_data['number'],
                    'pr_title': pr_data['title'],
                    'pr_state': pr_data['state'],
                    'pr_url': f"https://github.com/demo/repo/pull/{pr_data['number']}",
                    'repository': 'demo/repo',
                    'author': pr_data['author'],
                    'created_at': (base_date - timedelta(days=i*2)).isoformat(),
                    'updated_at': (base_date - timedelta(hours=i*6)).isoformat(),
                    'merged_at': (base_date - timedelta(hours=i*3)).isoformat() if pr_data['state'] == 'merged' else None,
                    'content_hash': get_file_hash(pr_data['body']),
                    'tags': ['pull_request', pr_data['state']],
                    'file_path': f"prs/demo-repo/pr-{pr_data['number']}",
                    'changes': {
                        'additions': pr_data['additions'],
                        'deletions': pr_data['deletions'],
                        'changed_files': pr_data['changed_files'],
                        'merged': pr_data['state'] == 'merged'
                    },
                    'technical_terms': extract_technical_terms(pr_data['body']),
                    'complexity': 'medium',
                    'pr_type': 'feature',
                    'is_demo': True,
                    'user_id': self.user_id,
                    'demo_note': 'This is synthetic demo data for showcase purposes'
                }
            }
            formatted_prs.append(doc)
        
        return formatted_prs
    
    def _generate_conversation_data(self, scenario: str) -> List[Dict[str, Any]]:
        conversations = [
            {
                'channel': 'general',
                'messages': [
                    {'user': 'tech-lead', 'text': 'New deployment went smoothly! All services are responding normally.'},
                    {'user': 'frontend-dev', 'text': 'Great! I can confirm the UI changes are working as expected.'},
                    {'user': 'backend-dev', 'text': 'Database migration completed without issues. Performance looks good.'}
                ]
            }
        ]
        
        formatted_conversations = []
        base_date = datetime.now()
        
        for i, conv_data in enumerate(conversations):
            conversation_text = '\n'.join([f"{msg['user']}: {msg['text']}" for msg in conv_data['messages']])
            
            doc = {
                'content': sanitize_text(conversation_text),
                'metadata': {
                    'source_type': 'slack_conversation',
                    'channel': conv_data['channel'],
                    'channel_purpose': f"Demo {conv_data['channel']} channel",
                    'is_private': False,
                    'message_count': len(conv_data['messages']),
                    'participants': list(set(msg['user'] for msg in conv_data['messages'])),
                    'start_time': str(int((base_date - timedelta(hours=i*2)).timestamp())),
                    'end_time': str(int((base_date - timedelta(hours=i*2-1)).timestamp())),
                    'date': (base_date - timedelta(days=i)).strftime('%Y-%m-%d'),
                    'content_hash': get_file_hash(conversation_text),
                    'file_path': f"slack/{conv_data['channel']}/conv-{i}",
                    'tags': ['slack', 'conversation', conv_data['channel']],
                    'technical_terms': extract_technical_terms(conversation_text),
                    'conversation_type': 'general_discussion',
                    'urgency': 'low',
                    'summary': f"Team discussion in #{conv_data['channel']}",
                    'is_demo': True,
                    'user_id': self.user_id,
                    'demo_note': 'This is synthetic demo data for showcase purposes'
                }
            }
            formatted_conversations.append(doc)
        
        return formatted_conversations
    
    def _generate_ticket_data(self, scenario: str) -> List[Dict[str, Any]]:
        tickets = [
            {
                'title': 'Implement user authentication',
                'description': 'Set up JWT-based authentication system with login and registration endpoints.',
                'status': 'In Progress',
                'priority': 'High',
                'type': 'Feature',
                'assignee': 'backend-dev',
                'reporter': 'product-manager',
                'labels': ['authentication', 'security'],
                'components': ['backend', 'api']
            }
        ]
        
        formatted_tickets = []
        base_date = datetime.now()
        
        for i, ticket_data in enumerate(tickets):
            full_content = f"{ticket_data['title']}. {ticket_data['description']}"
            
            doc = {
                'content': sanitize_text(full_content),
                'metadata': {
                    'source_type': 'ticket',
                    'ticket_id': f"DEMO-{i+1:03d}",
                    'title': ticket_data['title'],
                    'status': ticket_data['status'],
                    'priority': ticket_data['priority'],
                    'issue_type': ticket_data['type'],
                    'assignee': ticket_data['assignee'],
                    'reporter': ticket_data['reporter'],
                    'created_at': (base_date - timedelta(days=i*3)).isoformat(),
                    'updated_at': (base_date - timedelta(hours=i*8)).isoformat(),
                    'labels': ticket_data['labels'],
                    'components': ticket_data['components'],
                    'content_hash': get_file_hash(full_content),
                    'file_path': f"tickets/demo/DEMO-{i+1:03d}",
                    'tags': ['ticket', 'demo'] + ticket_data['labels'],
                    'technical_terms': extract_technical_terms(ticket_data['description']),
                    'complexity': 'medium',
                    'difficulty': 'intermediate',
                    'is_demo': True,
                    'user_id': self.user_id,
                    'demo_note': 'This is synthetic demo data for showcase purposes'
                }
            }
            formatted_tickets.append(doc)
        
        return formatted_tickets
    
    def get_scenarios(self) -> List[str]:
        return self.config.get('scenarios', ['startup', 'enterprise', 'freelancer'])
    
    def get_data_volume_config(self) -> Dict[str, int]:
        return self.config.get('data_volume', {
            'code_files': 20,
            'documents': 15,
            'prs': 10,
            'conversations': 8,
            'tickets': 12
        })


def generate_synthetic_data_quick(scenario: str = 'startup', user_id: str = None) -> Dict[str, List[Dict[str, Any]]]:
    generator = SyntheticDataGenerator(user_id=user_id)
    import asyncio
    return asyncio.run(generator.generate_all_synthetic_data(scenario))

if __name__ == "__main__":
    
    async def main():
        if len(sys.argv) > 1:
            command = sys.argv[1]
            generator = SyntheticDataGenerator()
            
            if command == "generate":
                scenario = sys.argv[2] if len(sys.argv) > 2 else 'startup'
                data = await generator.generate_all_synthetic_data(scenario)
                
                total_items = sum(len(items) for items in data.values())
                print(f"Generated {total_items} synthetic data items for {scenario} scenario")
                
                for data_type, items in data.items():
                    print(f"  {data_type}: {len(items)} items")
                    
            elif command == "scenarios":
                scenarios = generator.get_scenarios()
                print("Available scenarios:")
                for scenario in scenarios:
                    print(f"  - {scenario}")
                    
            elif command == "config":
                config = generator.get_data_volume_config()
                print("Data volume configuration:")
                print(json.dumps(config, indent=2))
                
            else:
                print("Available commands:")
                print("  generate [scenario] - Generate synthetic data")
                print("  scenarios - List available scenarios")
                print("  config - Show data volume configuration")
        else:
            print("Usage: python synthetic_data_generator.py [generate|scenarios|config] [args...]")
    
    asyncio.run(main())