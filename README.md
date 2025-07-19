# ZeroDay - AI-Powered Developer Onboarding Platform

A sophisticated agentic AI system that accelerates developer onboarding through intelligent mentoring, personalized learning paths, and contextual task recommendations.

## 🚀 Features

- **4 Specialized AI Agents**: Knowledge, Guide, Mentor, and Task agents working in harmony
- **Intelligent Code Analysis**: Vector-powered search across your entire codebase
- **Personalized Learning Paths**: Adaptive guidance based on role and experience
- **Real-time Mentoring**: Contextual help and troubleshooting assistance
- **Smart Task Recommendations**: Curated starter tasks matched to skill level
- **Modern Tech Stack**: FastAPI backend with Next.js frontend

## 🎯 Demo Mode

Experience ZeroDay's capabilities with synthetic data and mock integrations:
- Interactive chat with all 4 AI agents
- Sample learning paths and task suggestions
- Simulated code search and analysis
- Demo Slack integration workflows

## 🛠 Tech Stack

**Backend:**
- FastAPI with async/await architecture
- ChromaDB vector database for semantic search
- OpenAI/Anthropic LLM integration
- Loguru for structured logging

**Frontend:**
- Next.js 14 with TypeScript
- Tailwind CSS for modern styling
- Lucide React icons
- Responsive design system

**Infrastructure:**
- SQLite for local development
- Docker-optional deployment
- Vercel-ready frontend
- Environment-based configuration

## 🏃‍♂️ Quick Start

### Prerequisites
```bash
Python 3.9+
Node.js 18+
```

### Backend Setup
```bash
git clone https://github.com/mukuldesai/ZeroDay
cd zeroday
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
pip install -r requirements.txt
python api/main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to see ZeroDay in action.

## 🎮 Usage

### Chat with AI Agents
```bash
# Ask the Knowledge Agent
POST /api/chat
{
  "message": "How does the authentication system work?",
  "agent_type": "knowledge"
}

# Get learning guidance
POST /api/chat
{
  "message": "I want to learn React",
  "agent_type": "guide"
}
```

### Upload Team Data
```bash
# Upload codebase for analysis
POST /api/upload
{
  "file": "codebase.zip",
  "data_type": "github_repo"
}
```

## 🏗 Architecture

ZeroDay uses a modular agent architecture where each AI agent specializes in different aspects of developer onboarding:

- **Knowledge Agent**: Searches and analyzes your codebase, documentation, and PRs
- **Guide Agent**: Creates personalized learning roadmaps and tracks progress
- **Mentor Agent**: Provides real-time help, debugging assistance, and guidance
- **Task Agent**: Recommends appropriate starter tasks based on skill level

## 🔧 Configuration

Key environment variables:
```bash
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
VECTOR_STORE_PATH=./data/vectorstore
UPLOAD_DIR=./uploads
```

## 📊 API Endpoints

- `POST /api/chat` - Main chat interface
- `POST /api/upload` - Data upload and processing
- `GET /api/agents` - List available agents
- `POST /api/ask_mentor` - Direct mentor queries
- `POST /api/generate_plan` - Create learning plans
- `POST /api/suggest_task` - Get task recommendations

## 🚢 Deployment

### Local Development
```bash
python api/main.py &
cd frontend && npm run dev
```

### Production (Vercel + Railway)
1. Deploy frontend to Vercel
2. Deploy backend to Railway/Render
3. Configure environment variables
4. Update CORS settings

## 🤝 Contributing

This is a portfolio project showcasing modern AI agent architecture and full-stack development skills. The codebase demonstrates:

- Clean FastAPI async patterns
- Modular agent design
- Vector database integration
- Modern React/TypeScript practices
- Professional deployment strategies

## 📝 License

MIT License - feel free to use this code for learning and portfolio purposes.

## 🔗 Links

- [Live Demo](https://zeroday-demo.vercel.app)
- [Portfolio](https://v0-portfolio-page-creation-seven.vercel.app/)
- [LinkedIn](https://linkedin.com/in/mukuldesai)