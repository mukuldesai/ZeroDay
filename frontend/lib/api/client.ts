const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ApiResponse<T = any> {
  data?: T
  error?: string
  status: number
}

export interface ChatRequest {
  message: string
  user_role?: string
  context?: Record<string, any>
  agent_type?: string
}

export interface ChatResponse {
  response: string
  agent_used: string
  confidence: number
  sources: Array<{ type: string; path: string; section: string }>
  suggestions: string[]
  timestamp: string
}

export interface SystemHealth {
  status: string
  version: string
  services?: Record<string, string>
  timestamp?: string
  message?: string
}

export interface UploadStatus {
  vector_store_status: string
  documents_indexed: number
  temp_data: Record<string, number>
  ready_for_use: boolean
  user_id?: string
}

export interface TaskSuggestion {
  id: string
  title: string
  description: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  estimated_time: string
  category: string
  priority: 'low' | 'medium' | 'high'
  skills_required: string[]
}

export interface User {
  id: string
  name: string
  role: string
  experience_level: string
  team: string
  joined_date: string
  avatar?: string
  is_demo?: boolean
}

export interface DemoScenario {
  id: string
  name: string
  company_type: string
  team_size: number
  industry: string
  user_profile: {
    name: string
    role: string
    experience: string
  }
}

export interface AgentStatus {
  id: string
  name: string
  description: string
  available: boolean
  icon: string
  color: string
  bgColor: string
}

class ApiClient {
  private baseUrl: string = API_BASE

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      })

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}`
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorData.message || errorMessage
        } catch {
          errorMessage = response.statusText || errorMessage
        }
        
        return {
          status: response.status,
          error: errorMessage
        }
      }

      const data = await response.json()
      return {
        data,
        status: response.status
      }
    } catch (error) {
      return {
        status: 0,
        error: error instanceof Error ? error.message : 'Network error'
      }
    }
  }

  
  async getHealth(): Promise<ApiResponse<SystemHealth>> {
    return this.request<SystemHealth>('/')
  }

  async getHealthCheck(): Promise<ApiResponse<SystemHealth>> {
    return this.request<SystemHealth>('/health')
  }

 
  async getAgents(): Promise<ApiResponse<Record<string, AgentStatus>>> {
    return this.request<Record<string, AgentStatus>>('/agents')
  }


  async getUploadStatus(): Promise<ApiResponse<UploadStatus>> {
    return this.request<UploadStatus>('/api/upload/status')
  }

  async uploadFiles(files: File[], type: string, demoMode: boolean = false): Promise<ApiResponse<any>> {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    formData.append('type', type)
    formData.append('demo_mode', demoMode.toString())
    formData.append('user_id', 'current_user')

    try {
      const response = await fetch(`${this.baseUrl}/api/upload/files`, {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        return {
          status: response.status,
          error: errorData.detail || errorData.message || `HTTP ${response.status}`
        }
      }

      const data = await response.json()
      return {
        data,
        status: response.status
      }
    } catch (error) {
      return {
        status: 0,
        error: error instanceof Error ? error.message : 'Upload failed'
      }
    }
  }

  async uploadGitHubRepo(repoUrl: string, demoMode: boolean = false): Promise<ApiResponse<any>> {
    return this.request('/api/upload/github', {
      method: 'POST',
      body: JSON.stringify({
        repo_url: repoUrl,
        demo_mode: demoMode,
        user_id: 'current_user'
      })
    })
  }

  
  async sendChatMessage(request: ChatRequest): Promise<ApiResponse<ChatResponse>> {
    return this.request<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify(request)
    })
  }

  
  async getTasks(userRole: string = 'developer'): Promise<ApiResponse<TaskSuggestion[]>> {
    return this.request<TaskSuggestion[]>(`/api/suggest_task?user_role=${encodeURIComponent(userRole)}`)
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    return this.request<User>('/api/auth/me')
  }


  async getDemoScenarios(): Promise<ApiResponse<DemoScenario[]>> {
    return this.request<DemoScenario[]>('/demo/scenarios')
  }

  async getDemoScenario(scenarioId: string): Promise<ApiResponse<any>> {
    return this.request(`/demo/scenarios/${scenarioId}`)
  }

  async getDemoTasks(scenarioId: string): Promise<ApiResponse<any>> {
    return this.request(`/demo/tasks/${scenarioId}`)
  }

  async getDemoChatMessages(scenarioId: string): Promise<ApiResponse<any>> {
    return this.request(`/demo/chat/messages/${scenarioId}`)
  }

 
  async processData(demoMode: boolean = false): Promise<ApiResponse<any>> {
    return this.request('/api/upload/process', {
      method: 'POST',
      body: JSON.stringify({
        action: 'build_index',
        demo_mode: demoMode,
        user_id: 'current_user'
      })
    })
  }

  
  async getDashboardData(): Promise<ApiResponse<{
    health: SystemHealth | null
    agents: Record<string, AgentStatus> | null
    uploadStatus: UploadStatus | null
    user: User | null
  }>> {
    try {
      const [healthRes, agentsRes, uploadRes, userRes] = await Promise.allSettled([
        this.getHealth(),
        this.getAgents(),
        this.getUploadStatus(),
        this.getCurrentUser()
      ])

      return {
        status: 200,
        data: {
          health: healthRes.status === 'fulfilled' && healthRes.value.data ? healthRes.value.data : null,
          agents: agentsRes.status === 'fulfilled' && agentsRes.value.data ? agentsRes.value.data : null,
          uploadStatus: uploadRes.status === 'fulfilled' && uploadRes.value.data ? uploadRes.value.data : null,
          user: userRes.status === 'fulfilled' && userRes.value.data ? userRes.value.data : null
        }
      }
    } catch (error) {
      return {
        status: 0,
        error: error instanceof Error ? error.message : 'Failed to fetch dashboard data'
      }
    }
  }
}

export const apiClient = new ApiClient()

export const handleApiError = (error: string | undefined, fallback: string = 'An error occurred'): string => {
  if (!error) return fallback
  if (error.includes('Network error') || error.includes('fetch')) {
    return 'Cannot connect to ZeroDay backend. Make sure the server is running.'
  }
  return error
}

export const isApiSuccess = <T>(response: ApiResponse<T>): response is ApiResponse<T> & { data: T } => {
  return !response.error && !!response.data
}

export default apiClient