import { Code, BookOpen, Brain, CheckSquare } from 'lucide-react'
import { Agent, QuickAction } from '../types'

export const agents: Agent[] = [
  {
    id: 'knowledge',
    name: 'Knowledge',
    description: 'Code search & explanations',
    icon: <Code className="w-4 h-4" />,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 border-blue-200'
  },
  {
    id: 'mentor',
    name: 'Mentor',
    description: 'Senior developer guidance',
    icon: <Brain className="w-4 h-4" />,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 border-purple-200'
  },
  {
    id: 'guide',
    name: 'Guide',
    description: 'Learning path generation',
    icon: <BookOpen className="w-4 h-4" />,
    color: 'text-green-600',
    bgColor: 'bg-green-50 border-green-200'
  },
  {
    id: 'task',
    name: 'Task',
    description: 'Task recommendations',
    icon: <CheckSquare className="w-4 h-4" />,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50 border-orange-200'
  }
]

export const quickActions: QuickAction[] = [
  { text: "Explain authentication flow", icon: <Code className="w-3 h-3" />, agent: 'knowledge' },
  { text: "Create learning plan", icon: <BookOpen className="w-3 h-3" />, agent: 'guide' },
  { text: "Help with debugging", icon: <Brain className="w-3 h-3" />, agent: 'mentor' },
  { text: "Suggest first task", icon: <CheckSquare className="w-3 h-3" />, agent: 'task' }
]