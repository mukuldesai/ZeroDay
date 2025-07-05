// Common types used across the application
import { ReactNode } from 'react'

export interface Message {
  id: string
  content: string
  sender: 'user' | 'bot'
  timestamp: Date
  agent?: AgentType
  type?: 'text' | 'code' | 'plan' | 'task'
  metadata?: MessageMetadata
}

export interface MessageMetadata {
  confidence?: number
  sources?: string[]
  codeLanguage?: string
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
  priority: PriorityType
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
  progress: number
  subtasks: SubTask[]
}

export type TaskStatus = 'todo' | 'in-progress' | 'review' | 'completed'
export type PriorityType = 'low' | 'medium' | 'high' | 'urgent'
export type DifficultyType = 'easy' | 'medium' | 'hard'

export interface SubTask {
  id: string
  title: string
  completed: boolean
  estimatedTime: string
}

export interface TaskFeedback {
  rating: number
  comment: string
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
  category: string
}

export interface ActivityItem {
  id: string
  type: 'chat' | 'task' | 'learning' | 'code'
  title: string
  description: string
  timestamp: Date
  agent?: string
  status?: 'completed' | 'in-progress' | 'pending'
}

export interface ProgressData {
  category: string
  completed: number
  total: number
  color: string
  icon: React.ReactNode
}

export interface TaskStats {
  total: number
  completed: number
  inProgress: number
  pending: number
  avgCompletionTime: string
}

export interface TaskFilter {
  status: TaskStatus[]
  priority: PriorityType[]
  difficulty: DifficultyType[]
  category: string[]
  agent: AgentType[]
}

export interface QuickAction {
  text: string
  icon: ReactNode // or JSX.Element if you want stricter typing
  agent: 'knowledge' | 'guide' | 'mentor' | 'task'
}