import { ReactNode } from 'react'

export interface User {
  id: number
  name: string
  email: string
  isDemo: boolean
}

export interface DemoScenario {
  id: string
  name: string
  company_type: string
  team_size: number
  industry: string
  tech_stack: string[];
  user_profile: {
    name: string
    role: string
    experience: string
  }
}

export interface AuthToken {
  token: string
  expiresAt: string
}

export interface AuthUser {
  id: string
  email: string
  name: string
  isDemo: boolean
  permissions: string[]
  createdAt: string
  lastLoginAt?: string
}

export interface UserSession {
  user: AuthUser
  token: string
  expiresAt: string
  isAuthenticated: boolean
}

export interface UserContext {
  userId: string
  displayName: string
  email: string
  isDemo: boolean
  permissions: string[]
  createdAt: string
  lastActivity: string
}

export interface Organization {
  id: number
  name: string
  userId: number
  createdAt: string
}

export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'  
  timestamp: string
  agent?: AgentType
  type?: 'text' | 'code' | 'plan' | 'task'
  metadata?: MessageMetadata
  sources?: string[]
  suggestions?: string[]
  userId?: string
}

export interface MessageMetadata {
  confidence?: number
  sources?: string[]
  codeLanguage?: string
  userId?: string
}

export type AgentType = 'knowledge' | 'mentor' | 'guide' | 'task'

export interface Agent {
  id: AgentType
  name: string
  description: string
  icon: React.ReactNode
  color: string
  bgColor: string
  features?: string[]
}

export interface Task {
  id: string
  title: string
  description: string
  status: TaskStatus
  priority: TaskPriority
  difficulty: DifficultyType
  category: string
  estimatedTime: string
  actualTime?: string
  assignedAgent: AgentType
  skillsRequired: string[]
  prerequisites: string[]
  tags: string[]
  dueDate?: Date
  createdAt: Date
  updatedAt: Date
  completedAt?: Date  
  feedback?: TaskFeedback
  progress?: number
  subtasks?: SubTask[]
  assignee?: string
  source?: string
  userId?: string
  relatedFiles?: string[]
  aiGenerated?: boolean
  confidence?: number
  skills?: string[]
}

export type TaskStatus = 'todo' | 'in-progress' | 'review' | 'completed' | 'suggested'

export type TaskPriority = 'low' | 'medium' | 'high'

export type DifficultyType = 'easy' | 'medium' | 'hard'

export interface SubTask {
  id: string
  title: string
  completed: boolean
  estimatedTime: string
  userId?: string
}

export interface TaskFeedback {
  rating: number
  comment: string
  userId?: string
}

export interface LearningPath {
  id: string
  title: string
  description: string
  progress: number
  totalModules: number
  completedModules: number
  estimatedTime: string
  difficulty: DifficultyType
  userId: string
  category: string
}

export interface ActivityItem {
  id: string
  type: 'chat' | 'task' | 'learning' | 'code' | 'upload' | 'system'
  title: string
  description: string
  timestamp: string
  agent?: string
  status?: 'completed' | 'in-progress' | 'pending'
  userId?: string
}

export interface ProgressData {
  category: string
  completed: number
  total: number
  color: string
  icon: React.ReactNode
  userId: string
  growthPercentage: number
}

export interface TaskStats {
  total: number
  completed: number
  inProgress: number
  pending: number
  avgCompletionTime: string
  userId?: string
}

export interface TaskFilter {
  status: string[]  
  priority: string[]  
  difficulty: string[]  
  category: string[]
  agent: string[]
  userId?: string
}

export interface TaskFilters {
  status: TaskStatus[]
  priority: string[]
  difficulty: string[]
  category: string[]
  assignee: string[]
  search: string
  userId?: string
}

export interface QuickAction {
  text: string
  icon: ReactNode
  agent: 'knowledge' | 'guide' | 'mentor' | 'task'
  userId?: string
}

export interface TaskCardProps {
  task: Task
  onStatusChange: (id: string, status: TaskStatus) => void
  onEdit: (task: Task) => void
  onDelete?: (id: string) => void
  userId?: string
}

export interface TaskFiltersProps {
  filters: Partial<TaskFilter>
  onFilterChange: (filters: Partial<TaskFilter>) => void
  onReset: () => void
  taskCounts: Record<string, number>
  userId?: string
}

export interface TaskListViewProps {
  tasks: Task[]
  onStatusChange: (id: string, status: TaskStatus) => void
  onEdit: (task: Task) => void
  onDelete?: (id: string) => void
  userId?: string
}

export interface KanbanColumn {
  id: string
  title: string
  tasks: Task[]
  color: string
}

export interface KanbanBoardProps {
  kanbanColumns: KanbanColumn[]  
  onStatusChange?: (id: string, status: TaskStatus) => void
  onEdit?: (task: Task) => void
  onDelete?: (id: string) => void
  onDragEnd?: (result: any) => void
  userId?: string
}

export interface ApiResponse<T = any> {
  data?: T
  error?: string
  status: number
  userId?: string
}

export interface SystemHealth {
  status: string
  version: string
  agents_status: Record<AgentType, boolean>
}

export interface Stats {
  totalInteractions: number
  averageResponseTime: string
  completionRate: number
  learningStreak: number
  tasksCompleted: number
  documentsRead: number
  questionsAsked: number
  milestonesMet: number
  userId?: string
}

export interface DemoModeConfig {
  enabled: boolean
  scenario: DemoScenario | null
  syntheticData: boolean
  mockIntegrations: boolean
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto'
  notifications: boolean
  autoSave: boolean
  language: string
  timezone: string
  userId: string
}

export interface Permission {
  id: string
  name: string
  description: string
  category: string
}

export interface Role {
  id: string
  name: string
  description: string
  permissions: Permission[]
}