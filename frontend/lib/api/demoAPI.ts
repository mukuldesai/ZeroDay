const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface DemoScenario {
  id: string;
  name: string;
  company_type: string;
  team_size: number;
  industry: string;
  user_profile: {
    name: string;
    role: string;
    experience: string;
  };
}

interface DemoMessage {
  id: number;
  content: string;
  sender: string;
  timestamp: string;
}

interface DemoTask {
  id: number;
  title: string;
  description: string;
  status: string;
  priority: string;
  deadline: string;
  assignee: string;
  tags: string[];
}

interface DemoAnalytics {
  projects_completed: number;
  projects_in_progress: number;
  team_size: number;
  learning_goals_count: number;
  recent_activities: string[];
  tech_stack: string[];
  company_type: string;
}

export const demoAPI = {
  getScenarios: async (): Promise<DemoScenario[]> => {
    const response = await fetch(`${API_BASE}/demo/scenarios`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch demo scenarios');
    }
    
    return response.json();
  },

  getScenario: async (scenarioId: string) => {
    const response = await fetch(`${API_BASE}/demo/scenarios/${scenarioId}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch scenario: ${scenarioId}`);
    }
    
    return response.json();
  },

  getChatMessages: async (scenarioId: string): Promise<DemoMessage[]> => {
    const response = await fetch(`${API_BASE}/demo/chat/messages/${scenarioId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch demo chat messages');
    }
    
    return response.json();
  },

  getTasks: async (scenarioId: string): Promise<DemoTask[]> => {
    const response = await fetch(`${API_BASE}/demo/tasks/${scenarioId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch demo tasks');
    }
    
    return response.json();
  },

  getAnalytics: async (scenarioId: string): Promise<DemoAnalytics> => {
    const response = await fetch(`${API_BASE}/demo/analytics/${scenarioId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch demo analytics');
    }
    
    return response.json();
  }
};