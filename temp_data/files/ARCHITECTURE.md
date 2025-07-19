# ZeroDay Architecture

## System Overview

ZeroDay is an AI-powered developer onboarding platform built with a modern full-stack architecture designed for scalability and maintainability.

## Technology Stack

### Frontend
- **Next.js 13+** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Animations and transitions
- **Lucide React** - Icon library

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation and serialization
- **ChromaDB** - Vector database for embeddings
- **SQLite** - Local development database
- **uvicorn** - ASGI server

### AI/ML Integration
- **OpenAI API** - Language model integration
- **Anthropic Claude** - Alternative LLM support
- **Vector Embeddings** - Semantic search and retrieval
- **Multi-Agent System** - Specialized AI agents

## Architecture Patterns

### Multi-Agent Design
Four specialized AI agents handle different aspects of onboarding:
- **Knowledge Agent** - Code search and explanations
- **Mentor Agent** - Senior developer guidance
- **Guide Agent** - Learning path generation
- **Task Agent** - Task recommendations

### Component Architecture
- **Atomic Design** - Reusable UI components
- **Custom Hooks** - Shared business logic
- **Context API** - Global state management
- **API Client** - Centralized API communication

### Data Flow
1. User uploads team data (GitHub, Slack, docs)
2. Backend processes and creates vector embeddings
3. AI agents query vector store for context
4. Frontend displays personalized recommendations

## Deployment Strategy

### Development
- Local SQLite database
- ChromaDB local storage
- Hot-reload development servers

### Production
- Vercel frontend deployment
- Railway/Render backend hosting
- PostgreSQL database
- Pinecone vector store

## Security Considerations
- API key management via environment variables
- User session handling
- Data privacy and access controls
- CORS configuration

## Performance Optimizations
- Vector search indexing
- Component lazy loading
- API response caching
- Optimistic UI updates