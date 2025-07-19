# ZeroDay API Documentation

## Base URL
- Development: `http://localhost:8000`
- Production: `https://your-api-domain.com`

## Authentication

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "12345",
    "email": "user@example.com",
    "org_id": "org_123",
    "role": "member"
  }
}
```

### Logout
```http
POST /api/auth/logout
Authorization: Bearer {token}
```

### User Profile
```http
GET /api/users/profile
Authorization: Bearer {token}
```

**Response:**
```json
{
  "user_id": "12345",
  "email": "user@example.com",
  "org_id": "org_123",
  "role": "member",
  "permissions": ["read", "write"],
  "created_at": "2024-01-15T10:30:00Z",
  "last_active": "2024-01-20T14:22:00Z"
}
```

## AI Agents

### Knowledge Agent
```http
POST /api/agents/knowledge/query
Authorization: Bearer {token}
Content-Type: application/json

{
  "query": "How do I implement authentication?",
  "context": {
    "current_repo": "main-app",
    "tech_stack": ["React", "Node.js"]
  }
}
```

**Response:**
```json
{
  "response": "To implement authentication in your React/Node.js app...",
  "sources": [
    {
      "content": "Authentication implementation guide...",
      "metadata": {
        "file_path": "docs/auth-guide.md",
        "source_type": "documentation"
      },
      "relevance_score": 0.95
    }
  ],
  "query_id": "query_123",
  "timestamp": "2024-01-20T14:22:00Z"
}
```

### Mentor Agent
```http
POST /api/agents/mentor/ask
Authorization: Bearer {token}
Content-Type: application/json

{
  "problem": "Getting 401 error when calling API",
  "context": {
    "error_details": "Unauthorized access",
    "urgency": "high"
  }
}
```

**Response:**
```json
{
  "advice": "The 401 error indicates authentication issues...",
  "suggested_actions": [
    "Check API key validity",
    "Verify token expiration",
    "Review authentication headers"
  ],
  "related_resources": [
    {
      "title": "Authentication Troubleshooting",
      "url": "/docs/auth-troubleshooting"
    }
  ],
  "severity": "medium"
}
```

### Task Agent
```http
POST /api/agents/task/suggest
Authorization: Bearer {token}
Content-Type: application/json

{
  "user_role": "frontend-developer",
  "skill_level": "intermediate",
  "interests": ["React", "TypeScript"]
}
```

**Response:**
```json
{
  "tasks": [
    {
      "id": "task_456",
      "title": "Implement user profile component",
      "description": "Create a reusable user profile component...",
      "difficulty": "intermediate",
      "estimated_hours": 4,
      "technologies": ["React", "TypeScript"],
      "learning_objectives": ["Component design", "TypeScript interfaces"]
    }
  ],
  "total_tasks": 5,
  "recommended_order": ["task_456", "task_789"]
}
```

### Guide Agent
```http
POST /api/agents/guide/generate-plan
Authorization: Bearer {token}
Content-Type: application/json

{
  "user_role": "backend-developer",
  "learning_goal": "Learn microservices architecture",
  "experience_level": "beginner"
}
```

**Response:**
```json
{
  "learning_path": {
    "title": "Microservices Architecture for Backend Developers",
    "duration_weeks": 8,
    "modules": [
      {
        "week": 1,
        "title": "Introduction to Microservices",
        "objectives": ["Understand microservices concepts"],
        "resources": [
          {
            "type": "documentation",
            "title": "Microservices Basics",
            "url": "/docs/microservices-intro"
          }
        ]
      }
    ]
  },
  "prerequisites": ["Basic backend development", "API design"],
  "success_metrics": ["Complete 5 modules", "Build sample project"]
}
```

## File Upload

### Upload Documents
```http
POST /api/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

files: [file1.pdf, file2.md]
source_type: "documentation"
```

**Response:**
```json
{
  "uploaded_files": [
    {
      "filename": "file1.pdf",
      "file_id": "file_123",
      "size": 2048576,
      "processed": true
    }
  ],
  "total_files": 2,
  "processing_status": "completed"
}
```

### Upload Status
```http
GET /api/upload/status/{upload_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "upload_id": "upload_789",
  "status": "processing",
  "total_files": 5,
  "processed_files": 3,
  "failed_files": 0,
  "estimated_completion": "2024-01-20T15:00:00Z"
}
```

## Vector Search

### Search Documents
```http
POST /api/search
Authorization: Bearer {token}
Content-Type: application/json

{
  "query": "authentication implementation",
  "collections": ["documentation", "code"],
  "limit": 10,
  "filters": {
    "source_type": ["documentation", "code"],
    "file_extension": [".md", ".py"]
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "Authentication implementation guide...",
      "metadata": {
        "file_path": "docs/auth.md",
        "source_type": "documentation",
        "created_at": "2024-01-15T10:30:00Z"
      },
      "relevance_score": 0.95,
      "collection": "documentation"
    }
  ],
  "total_results": 25,
  "query_time_ms": 150
}
```

## Demo Data

### Get Demo Scenarios
```http
GET /api/demo/scenarios
Authorization: Bearer {token}
```

**Response:**
```json
{
  "scenarios": [
    {
      "id": "startup",
      "name": "Startup Company",
      "description": "Small tech startup environment",
      "features": ["Agile development", "Small team", "MVP focus"]
    },
    {
      "id": "enterprise",
      "name": "Enterprise Corporation",
      "description": "Large enterprise environment",
      "features": ["Complex architecture", "Multiple teams", "Compliance focus"]
    }
  ]
}
```

### Load Demo Data
```http
POST /api/demo/load/{scenario_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "scenario_id": "startup",
  "loaded": true,
  "documents_created": 150,
  "collections_populated": ["documentation", "code", "slack"],
  "load_time_ms": 5000
}
```

## Health & Monitoring

### System Health
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T14:22:00Z",
  "services": {
    "database": "healthy",
    "vector_store": "healthy",
    "ai_agents": "healthy"
  },
  "version": "1.0.0"
}
```

### User Analytics
```http
GET /api/analytics/user
Authorization: Bearer {token}
```

**Response:**
```json
{
  "user_id": "12345",
  "stats": {
    "queries_today": 25,
    "documents_uploaded": 10,
    "tasks_completed": 3,
    "learning_progress": 65
  },
  "activity_summary": {
    "most_used_agent": "knowledge",
    "favorite_topics": ["authentication", "database"],
    "completion_rate": 0.85
  }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "validation_error",
  "message": "Invalid request format",
  "details": {
    "field": "email",
    "issue": "Invalid email format"
  }
}
```

### 401 Unauthorized
```json
{
  "error": "unauthorized",
  "message": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "error": "forbidden",
  "message": "Insufficient permissions",
  "required_permission": "write"
}
```

### 404 Not Found
```json
{
  "error": "not_found",
  "message": "Resource not found",
  "resource_type": "document",
  "resource_id": "doc_123"
}
```

### 429 Rate Limited
```json
{
  "error": "rate_limited",
  "message": "Too many requests",
  "retry_after": 60,
  "limit": 100,
  "remaining": 0
}
```

### 500 Internal Server Error
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred",
  "request_id": "req_123456"
}
```

## Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/api/auth/login` | 5 requests | 1 minute |
| `/api/agents/*` | 60 requests | 1 minute |
| `/api/search` | 100 requests | 1 minute |
| `/api/upload` | 10 requests | 1 minute |
| Global | 1000 requests | 1 hour |

## Pagination

For endpoints returning lists, use these query parameters:

```http
GET /api/documents?page=2&limit=20&sort=created_at&order=desc
```

**Response includes pagination metadata:**
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": true
  }
}
```

## Webhooks

### Register Webhook
```http
POST /api/webhooks
Authorization: Bearer {token}
Content-Type: application/json

{
  "url": "https://your-app.com/webhook",
  "events": ["document.uploaded", "task.completed"],
  "secret": "webhook_secret_key"
}
```

### Webhook Events

#### Document Uploaded
```json
{
  "event": "document.uploaded",
  "timestamp": "2024-01-20T14:22:00Z",
  "data": {
    "file_id": "file_123",
    "filename": "guide.pdf",
    "user_id": "user_456",
    "org_id": "org_789"
  }
}
```

#### Task Completed
```json
{
  "event": "task.completed",
  "timestamp": "2024-01-20T14:22:00Z",
  "data": {
    "task_id": "task_123",
    "user_id": "user_456",
    "completion_time_minutes": 120,
    "success": true
  }
}
```

## SDK Examples

### Python
```python
import requests

class ZeroDayAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def query_knowledge(self, query, context=None):
        response = requests.post(
            f"{self.base_url}/api/agents/knowledge/query",
            headers=self.headers,
            json={"query": query, "context": context}
        )
        return response.json()

api = ZeroDayAPI("http://localhost:8000", "your_token")
result = api.query_knowledge("How to implement caching?")
```

### JavaScript
```javascript
class ZeroDayAPI {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }

    async queryKnowledge(query, context = null) {
        const response = await fetch(`${this.baseUrl}/api/agents/knowledge/query`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ query, context })
        });
        return response.json();
    }
}

const api = new ZeroDayAPI('http://localhost:8000', 'your_token');
const result = await api.queryKnowledge('How to implement caching?');
```