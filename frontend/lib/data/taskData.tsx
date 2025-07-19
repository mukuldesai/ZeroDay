import { Task } from '../types'

export const mockTasks: Task[] = [
  {
    id: '1',
    title: 'Implement user authentication flow',
    description: 'Create a complete authentication system with JWT tokens, password hashing, and secure session management.',
    status: 'in-progress',
    priority: 'high',
    difficulty: 'medium',
    category: 'Backend',
    estimatedTime: '4 hours',
    actualTime: '2.5 hours',
    assignedAgent: 'mentor',
    skillsRequired: ['FastAPI', 'JWT', 'Security'],
    prerequisites: ['Database setup', 'User model'],
    tags: ['security', 'api', 'backend'],
    dueDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
    createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000),
    updatedAt: new Date(),
    progress: 65,
    subtasks: [
      { id: 's1', title: 'Set up JWT configuration', completed: true, estimatedTime: '30m' },
      { id: 's2', title: 'Create login endpoint', completed: true, estimatedTime: '1h' },
      { id: 's3', title: 'Implement password hashing', completed: false, estimatedTime: '45m' },
      { id: 's4', title: 'Add logout functionality', completed: false, estimatedTime: '30m' }
    ]
  },
  {
    id: '2',
    title: 'Design responsive dashboard layout',
    description: 'Create a modern, responsive dashboard using React and Tailwind CSS with mobile-first approach.',
    status: 'completed',
    priority: 'medium',
    difficulty: 'easy',
    category: 'Frontend',
    estimatedTime: '3 hours',
    actualTime: '2.8 hours',
    assignedAgent: 'knowledge',
    skillsRequired: ['React', 'Tailwind CSS', 'Responsive Design'],
    prerequisites: ['Project setup'],
    tags: ['ui', 'responsive', 'design'],
    dueDate: new Date(Date.now() - 24 * 60 * 60 * 1000),
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 12 * 60 * 60 * 1000),
    completedAt: new Date(Date.now() - 12 * 60 * 60 * 1000),
    progress: 100,
    feedback: { rating: 5, comment: 'Excellent work on the responsive design!' },
    subtasks: [
      { id: 's5', title: 'Create layout components', completed: true, estimatedTime: '1h' },
      { id: 's6', title: 'Implement mobile responsiveness', completed: true, estimatedTime: '1.5h' },
      { id: 's7', title: 'Add dark mode support', completed: true, estimatedTime: '30m' }
    ]
  },
  {
    id: '3',
    title: 'Set up CI/CD pipeline',
    description: 'Configure automated testing, building, and deployment pipeline using GitHub Actions.',
    status: 'todo',
    priority: 'low',
    difficulty: 'hard',
    category: 'DevOps',
    estimatedTime: '6 hours',
    assignedAgent: 'guide',
    skillsRequired: ['GitHub Actions', 'Docker', 'Deployment'],
    prerequisites: ['Repository setup'],
    tags: ['devops', 'automation', 'deployment'],
    dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    createdAt: new Date(),
    updatedAt: new Date(),
    progress: 0,
    subtasks: [
      { id: 's8', title: 'Configure GitHub Actions', completed: false, estimatedTime: '2h' },
      { id: 's9', title: 'Set up test automation', completed: false, estimatedTime: '2h' },
      { id: 's10', title: 'Configure deployment', completed: false, estimatedTime: '2h' }
    ]
  },
  {
    id: '4',
    title: 'Write comprehensive unit tests',
    description: 'Create unit tests for all core components and API endpoints with high coverage.',
    status: 'review',
    priority: 'medium',
    difficulty: 'medium',
    category: 'Testing',
    estimatedTime: '5 hours',
    actualTime: '4.2 hours',
    assignedAgent: 'task',
    skillsRequired: ['Jest', 'React Testing Library', 'Python Testing'],
    prerequisites: ['Component implementation'],
    tags: ['testing', 'quality', 'coverage'],
    dueDate: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000),
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 1 * 60 * 60 * 1000),
    progress: 90,
    subtasks: [
      { id: 's11', title: 'Write component tests', completed: true, estimatedTime: '2h' },
      { id: 's12', title: 'Write API tests', completed: true, estimatedTime: '2h' },
      { id: 's13', title: 'Achieve 90% coverage', completed: false, estimatedTime: '1h' }
    ]
  }
]

export const taskStats = {
  totalTasks: 4,
  completedTasks: 1,
  inProgressTasks: 1,
  todoTasks: 1,
  reviewTasks: 1,
  averageCompletionTime: '3.2 hours',
  successRate: 85
}

export const taskFilters = [
  { label: 'All', value: 'all' },
  { label: 'Todo', value: 'todo' },
  { label: 'In Progress', value: 'in-progress' },
  { label: 'Review', value: 'review' },
  { label: 'Completed', value: 'completed' }
]

export const priorityColors = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-red-100 text-red-800'
}

export const difficultyColors = {
  easy: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  hard: 'bg-red-100 text-red-800'
}