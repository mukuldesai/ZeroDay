export const API_CONFIG = {
 
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000',
  
  
  ENDPOINTS: {
    
    KNOWLEDGE: '/api/query/code/',      
    KNOWLEDGE_SEARCH: '/api/query/code/search_code',   
    KNOWLEDGE_STATS: '/api/query/code/code_stats',    
    MENTOR: '/api/ask_mentor',
    MENTOR_STATS: '/api/mentor_stats',   
    TASK_SUGGEST: '/api/suggest_task', 
    TASK_CREATE: '/api/create_task',     
    GUIDE: '/api/generate_plan',
    LEARNING_STATS: '/api/learning_stats',
    CHAT: '/api/chat',
    
    
    AGENTS: '/agents',
    HEALTH: '/health',
    
  
    AUTH_ME: '/api/auth/me',            
    AUTH_LOGIN: '/api/auth/login',
    AUTH_LOGOUT: '/api/auth/logout',
    AUTH_VERIFY: '/api/auth/verify',
    
    
    USER_PROFILE: '/api/users/profile',  
    USER_CONTEXT: '/api/users/context',
    
    
    UPLOAD_STATUS: '/api/upload/status', 
    UPLOAD_FILES: '/api/upload/files',   
    UPLOAD_GITHUB: '/api/upload/github', 
    UPLOAD_PROCESS: '/api/upload/process', 
    
    
    QUERY_STATS: '/api/query/stats',     
    
   
    DEMO_ANALYTICS: '/demo/analytics',  
    DEMO_SCENARIOS: '/api/demo/scenarios',
    DEMO_GENERATE: '/api/demo/generate',
    DEMO_STATUS: '/api/demo/status',
    
    
    HEALTH_AGENTS: '/api/health/agents',
    HEALTH_SYSTEM: '/api/health/system',
    HEALTH_DATABASE: '/api/health/database'
  }
};


export const makeApiCall = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${API_CONFIG.BASE_URL}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    console.log(` API Call: ${options.method || 'GET'} ${url}`);
    const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status} for ${url}`);
    }
    
    const data = await response.json();
    console.log(` API Success: ${url}`, data);
    return data;
  } catch (error) {
    console.error(` API Error: ${url}`, error);
    throw error;
  }
};


export const apiClient = {
 
  auth: {
    me: () => makeApiCall(API_CONFIG.ENDPOINTS.AUTH_ME),
    login: (credentials: any) => makeApiCall(API_CONFIG.ENDPOINTS.AUTH_LOGIN, { 
      method: 'POST', 
      body: JSON.stringify(credentials) 
    }),
  },
  
 
  agents: {
    status: () => makeApiCall(API_CONFIG.ENDPOINTS.AGENTS),
    chat: (message: string, agent_type = 'auto') => makeApiCall(API_CONFIG.ENDPOINTS.CHAT, {
      method: 'POST',
      body: JSON.stringify({
        message,
        user_role: 'developer',
        agent_type,
        user_id: 'current_user'
      })
    }),
    knowledge: (question: string) => makeApiCall(API_CONFIG.ENDPOINTS.KNOWLEDGE, {
      method: 'POST', 
      body: JSON.stringify({
        question,
        user_id: 'current_user',
        demo_mode: true
      })
    }),
    mentor: (question: string) => makeApiCall(API_CONFIG.ENDPOINTS.MENTOR, {
      method: 'POST',
      body: JSON.stringify({
        question,
        user_id: 'current_user',
        urgency: 'normal'
      })
    }),
    suggestTask: () => makeApiCall(API_CONFIG.ENDPOINTS.TASK_SUGGEST, {
      method: 'POST',
      body: JSON.stringify({
        user_id: 'current_user',
        user_role: 'developer',
        experience_level: 'intermediate'
      })
    }),
    createTask: (taskData: any) => makeApiCall(API_CONFIG.ENDPOINTS.TASK_CREATE, {
      method: 'POST',
      body: JSON.stringify({
        user_id: 'current_user',
        ...taskData
      })
    })
  },
  
  
  stats: {
    query: () => makeApiCall(API_CONFIG.ENDPOINTS.QUERY_STATS),
    mentor: () => makeApiCall(API_CONFIG.ENDPOINTS.MENTOR_STATS),
    learning: () => makeApiCall(API_CONFIG.ENDPOINTS.LEARNING_STATS),
    codeStats: () => makeApiCall(API_CONFIG.ENDPOINTS.KNOWLEDGE_STATS)
  },
  
  
  upload: {
    status: () => makeApiCall(API_CONFIG.ENDPOINTS.UPLOAD_STATUS),
    files: (formData: FormData) => makeApiCall(API_CONFIG.ENDPOINTS.UPLOAD_FILES, {
      method: 'POST',
      body: formData,
      headers: {} 
    }),
    github: (repoUrl: string, token?: string) => makeApiCall(API_CONFIG.ENDPOINTS.UPLOAD_GITHUB, {
      method: 'POST',
      body: JSON.stringify({ repo_url: repoUrl, token })
    })
  },
  

  demo: {
    analytics: (scenario = 'startup') => makeApiCall(`${API_CONFIG.ENDPOINTS.DEMO_ANALYTICS}/${scenario}`),
    scenarios: () => makeApiCall(API_CONFIG.ENDPOINTS.DEMO_SCENARIOS),
    status: () => makeApiCall(API_CONFIG.ENDPOINTS.DEMO_STATUS)
  },
  

  health: {
    system: () => makeApiCall(API_CONFIG.ENDPOINTS.HEALTH),
    agents: () => makeApiCall(API_CONFIG.ENDPOINTS.HEALTH_AGENTS),
    database: () => makeApiCall(API_CONFIG.ENDPOINTS.HEALTH_DATABASE)
  }
};