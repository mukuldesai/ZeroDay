# ZeroDay — Multi-Agent AI Developer Onboarding

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=langchain&logoColor=white)](https://langchain.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white)](https://openai.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6B35?style=flat&logo=databricks&logoColor=white)](https://trychroma.com)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

A four-agent agentic AI system that accelerates developer onboarding through contextual code search, personalized learning paths, intelligent task recommendations, and real-time mentoring. Agents share context and coordinate responses the way a real team would.

🔗 **[Live Demo](https://zeroday-frontend-alpha.vercel.app/)**
---

## Agent Architecture

```
                    ┌─────────────────────────┐
                    │     Developer Query      │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    Shared Context Bus    │
                    └──┬──────┬───────┬──────┘
                       │      │       │      │
           ┌───────────▼─┐ ┌──▼──┐ ┌─▼───┐ ┌▼────────┐
           │  Knowledge  │ │Guide│ │Mentor│ │  Task   │
           │   Agent     │ │Agent│ │Agent │ │  Agent  │
           │             │ │     │ │      │ │         │
           │ Codebase    │ │Learn│ │Debug │ │Starter  │
           │ search +    │ │paths│ │help +│ │tasks by │
           │ doc lookup  │ │     │ │review│ │skill    │
           └─────────────┘ └─────┘ └──────┘ └─────────┘
```

---

## Features

- **Knowledge Agent** — semantic search across your codebase, documentation, and PRs using ChromaDB vector embeddings
- **Guide Agent** — builds personalized learning roadmaps based on role and experience level, tracks progress
- **Mentor Agent** — provides real-time debugging help, code review, and contextual troubleshooting
- **Task Agent** — recommends appropriate starter tasks matched to the developer's current skill level
- **Shared context** — all agents read from and write to a shared session context so responses stay coherent

---

## Tech Stack

**Backend**
| Tool | Role |
|---|---|
| FastAPI | Async REST API with WebSocket support |
| LangChain | Agent orchestration and LLM chaining |
| ChromaDB | Vector database for semantic codebase search |
| OpenAI GPT | Core language model for all agents |
| SQLite | Local session and progress storage |
| Loguru | Structured logging |

**Frontend**
| Tool | Role |
|---|---|
| Next.js 14 | React framework with TypeScript |
| Tailwind CSS | Utility-first styling |
| Lucide React | Icon system |

---

## Project Structure

```
ZeroDay/
├── api/
│   ├── main.py               # FastAPI app entry point
│   ├── agents/
│   │   ├── knowledge.py      # Codebase search agent
│   │   ├── guide.py          # Learning path agent
│   │   ├── mentor.py         # Real-time help agent
│   │   └── task.py           # Task recommendation agent
│   ├── core/
│   │   ├── context_bus.py    # Shared context management
│   │   └── vectorstore.py    # ChromaDB integration
│   └── routers/
│       ├── chat.py
│       ├── upload.py
│       └── plans.py
├── frontend/
│   ├── app/
│   ├── components/
│   └── package.json
├── data/
│   └── vectorstore/          # Local ChromaDB storage
├── requirements.txt
└── README.md
```

---

## Setup

**Backend**
```bash
git clone https://github.com/mukuldesai/ZeroDay
cd ZeroDay
python -m venv env
source env/bin/activate       # Windows: env\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # Add your API keys
python api/main.py
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`

**Environment variables**
```env
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
VECTOR_STORE_PATH=./data/vectorstore
UPLOAD_DIR=./uploads
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/chat` | Send message to any agent |
| POST | `/api/upload` | Upload codebase for indexing |
| GET | `/api/agents` | List available agents |
| POST | `/api/ask_mentor` | Direct mentor query |
| POST | `/api/generate_plan` | Create a learning plan |
| POST | `/api/suggest_task` | Get task recommendations |

```bash
# Example: query the Knowledge Agent
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How does authentication work?", "agent_type": "knowledge"}'
```

---

## Author

**Mukul Desai** — Data Engineer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-mukuldesai-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/mukuldesai)
[![Portfolio](https://img.shields.io/badge/Portfolio-mukuldesai.vercel.app-000000?style=flat&logo=vercel&logoColor=white)](https://mukuldesai.vercel.app)
