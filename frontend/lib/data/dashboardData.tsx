import { 
  Code, BookOpen, CheckSquare, Brain, Clock, TrendingUp, Users, Award,
  MessageSquare, Target, Activity, Star, BarChart3
} from 'lucide-react'
import { ProgressData, ActivityItem, LearningPath } from '../types'

export const progressData: ProgressData[] = [
  {
    category: 'Code Understanding',
    completed: 12,
    total: 15,
    color: 'from-blue-500 to-blue-600',
    icon: <Code className="w-5 h-5" />
  },
  {
    category: 'Learning Modules',
    completed: 8,
    total: 12,
    color: 'from-green-500 to-green-600',
    icon: <BookOpen className="w-5 h-5" />
  },
  {
    category: 'Tasks Completed',
    completed: 5,
    total: 8,
    color: 'from-orange-500 to-orange-600',
    icon: <CheckSquare className="w-5 h-5" />
  },
  {
    category: 'Mentoring Sessions',
    completed: 3,
    total: 5,
    color: 'from-purple-500 to-purple-600',
    icon: <Brain className="w-5 h-5" />
  }
]

export const recentActivity: ActivityItem[] = [
  {
    id: '1',
    type: 'chat',
    title: 'Asked about authentication flow',
    description: 'Knowledge Agent explained JWT implementation',
    timestamp: new Date(Date.now() - 30 * 60 * 1000),
    agent: 'Knowledge',
    status: 'completed'
  },
  {
    id: '2',
    type: 'task',
    title: 'Fix login validation bug',
    description: 'Completed with mentor guidance',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    agent: 'Task',
    status: 'completed'
  },
  {
    id: '3',
    type: 'learning',
    title: 'React Hooks Deep Dive',
    description: 'Module 3 of 5 completed',
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
    agent: 'Guide',
    status: 'in-progress'
  },
  {
    id: '4',
    type: 'code',
    title: 'Explored API middleware',
    description: 'Reviewed 15 files in authentication module',
    timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
    agent: 'Knowledge',
    status: 'completed'
  }
]

export const learningPaths: LearningPath[] = [
  {
    id: '1',
    title: 'Frontend Architecture',
    description: 'Master React, TypeScript, and modern frontend patterns',
    progress: 65,
    totalModules: 8,
    completedModules: 5,
    estimatedTime: '2 weeks',
    difficulty: 'medium',
    category: 'Frontend'
  },
  {
    id: '2',
    title: 'Backend APIs',
    description: 'Learn FastAPI, database design, and API security',
    progress: 40,
    totalModules: 10,
    completedModules: 4,
    estimatedTime: '3 weeks',
    difficulty: 'easy',
    category: 'Backend'
  },
  {
    id: '3',
    title: 'DevOps Fundamentals',
    description: 'Docker, CI/CD, and deployment strategies',
    progress: 20,
    totalModules: 6,
    completedModules: 1,
    estimatedTime: '2 weeks',
    difficulty: 'hard',
    category: 'DevOps'
  }
]

export const quickActions = [
  {
    label: 'Ask AI Assistant',
    icon: <MessageSquare className="w-4 h-4" />,
    href: '/chat',
    color: 'bg-indigo-50 text-indigo-600'
  },
  {
    label: 'View Tasks',
    icon: <CheckSquare className="w-4 h-4" />,
    href: '/tasks',
    color: 'bg-green-50 text-green-600'
  },
  {
    label: 'Explore Codebase',
    icon: <Code className="w-4 h-4" />,
    color: 'bg-purple-50 text-purple-600'
  },
  {
    label: 'Continue Learning',
    icon: <BookOpen className="w-4 h-4" />,
    color: 'bg-orange-50 text-orange-600'
  }
]

export const todaysGoals = [
  { task: 'Complete React module', completed: true },
  { task: 'Review 3 PRs', completed: true },
  { task: 'Fix authentication bug', completed: false },
  { task: 'Write unit tests', completed: false }
]

export const stats = {
  totalInteractions: 147,
  averageResponseTime: '2.3s',
  completionRate: 85,
  learningStreak: 7
}

export const chartData = [
  { name: 'Mon', interactions: 12, tasks: 3, learning: 2 },
  { name: 'Tue', interactions: 19, tasks: 5, learning: 3 },
  { name: 'Wed', interactions: 24, tasks: 4, learning: 4 },
  { name: 'Thu', interactions: 15, tasks: 6, learning: 2 },
  { name: 'Fri', interactions: 28, tasks: 8, learning: 5 },
  { name: 'Sat', interactions: 8, tasks: 2, learning: 1 },
  { name: 'Sun', interactions: 6, tasks: 1, learning: 2 }
]