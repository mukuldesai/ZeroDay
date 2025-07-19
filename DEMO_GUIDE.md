# ZeroDay Demo Guide

## Demo vs Real Data

ZeroDay includes a demo mode to showcase features without requiring backend setup or real data upload.

### Demo Mode Features

**What's Synthetic:**
- User profiles and names
- GitHub repository data (commits, PRs, issues)
- Slack conversations and team interactions
- Learning progress and task completion
- Performance metrics and analytics

**What's Real:**
- UI components and interactions
- Frontend functionality
- Component architecture
- Design system implementation

### Using Demo Mode

1. **Toggle Demo Mode**: Use the demo/real toggle in the upload interface
2. **Demo Indicator**: Look for "Demo Mode" badges in navigation headers
3. **Sample Data**: All data shown is representative of real usage patterns

### Backend Requirements

**Demo Mode**: Frontend-only, no backend required
**Real Mode**: Requires Python backend server running on port 8000

### Quick Start

```bash
# Frontend only (Demo Mode)
cd frontend
npm run dev

# Full system (Real Mode)
# Terminal 1: Backend
python -m uvicorn api.chat:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Demo Scenarios

- **New Developer Onboarding**: Experience the full onboarding flow
- **AI Agent Interactions**: Chat with Knowledge, Mentor, Guide, and Task agents
- **Progress Tracking**: View dashboard with learning paths and task completion
- **Data Upload Simulation**: See how real data would be processed