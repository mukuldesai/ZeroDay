'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Zap, 
  Brain, 
  Code, 
  BookOpen, 
  CheckSquare, 
  TrendingUp, 
  Users, 
  Clock, 
  Target,
  Award,
  Calendar,
  FileText,
  GitBranch,
  MessageSquare,
  BarChart3,
  PieChart,
  Activity,
  Star,
  Flame,
  Coffee,
  Lightbulb,
  ArrowRight,
  ArrowUp,
  ArrowDown,
  ChevronRight,
  Filter,
  Download,
  Settings,
  Bell,
  Search,
  MoreHorizontal,
  Play,
  Pause,
  RefreshCw,
  Eye,
  ThumbsUp,
  MessageCircle,
  Bookmark,
  Share2
} from 'lucide-react'
import Link from 'next/link'

// Types
interface ProgressData {
  category: string
  completed: number
  total: number
  color: string
  icon: React.ReactNode
}

interface ActivityItem {
  id: string
  type: 'chat' | 'task' | 'learning' | 'code'
  title: string
  description: string
  timestamp: Date
  agent?: string
  status?: 'completed' | 'in-progress' | 'pending'
}

interface LearningPath {
  id: string
  title: string
  description: string
  progress: number
  totalModules: number
  completedModules: number
  estimatedTime: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  category: string
}

interface TaskRecommendation {
  id: string
  title: string
  description: string
  difficulty: 'easy' | 'medium' | 'hard'
  estimatedTime: string
  skillsRequired: string[]
  priority: 'high' | 'medium' | 'low'
  category: string
}

// Mock Data
const progressData: ProgressData[] = [
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

const recentActivity: ActivityItem[] = [
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

const learningPaths: LearningPath[] = [
  {
    id: '1',
    title: 'Frontend Architecture',
    description: 'Master React, TypeScript, and modern frontend patterns',
    progress: 65,
    totalModules: 8,
    completedModules: 5,
    estimatedTime: '2 weeks',
    difficulty: 'intermediate',
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
    difficulty: 'beginner',
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
    difficulty: 'advanced',
    category: 'DevOps'
  }
]

const taskRecommendations: TaskRecommendation[] = [
  {
    id: '1',
    title: 'Add loading states to dashboard',
    description: 'Improve UX by adding skeleton loaders and loading indicators',
    difficulty: 'easy',
    estimatedTime: '2 hours',
    skillsRequired: ['React', 'CSS'],
    priority: 'high',
    category: 'Frontend'
  },
  {
    id: '2',
    title: 'Implement user preferences API',
    description: 'Create endpoints for storing and retrieving user settings',
    difficulty: 'medium',
    estimatedTime: '4 hours',
    skillsRequired: ['FastAPI', 'Database'],
    priority: 'medium',
    category: 'Backend'
  },
  {
    id: '3',
    title: 'Set up automated testing',
    description: 'Configure Jest and React Testing Library for components',
    difficulty: 'hard',
    estimatedTime: '6 hours',
    skillsRequired: ['Testing', 'JavaScript'],
    priority: 'low',
    category: 'Quality'
  }
]

// Components
const ProgressCard = ({ data }: { data: ProgressData }) => {
  const percentage = (data.completed / data.total) * 100

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300"
    >
      <div className="flex items-center justify-between mb-4">
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${data.color} flex items-center justify-center text-white`}>
          {data.icon}
        </div>
        <span className="text-sm text-gray-500">
          {data.completed}/{data.total}
        </span>
      </div>
      
      <h3 className="font-semibold text-gray-900 mb-2">{data.category}</h3>
      
      <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className={`h-2 rounded-full bg-gradient-to-r ${data.color}`}
        />
      </div>
      
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-600">{Math.round(percentage)}% complete</span>
        <motion.span 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-green-600 flex items-center"
        >
          <ArrowUp className="w-3 h-3 mr-1" />
          +12%
        </motion.span>
      </div>
    </motion.div>
  )
}

const ActivityItem = ({ activity }: { activity: ActivityItem }) => {
  const getActivityIcon = () => {
    switch (activity.type) {
      case 'chat': return <MessageSquare className="w-4 h-4" />
      case 'task': return <CheckSquare className="w-4 h-4" />
      case 'learning': return <BookOpen className="w-4 h-4" />
      case 'code': return <Code className="w-4 h-4" />
      default: return <Activity className="w-4 h-4" />
    }
  }

  const getStatusColor = () => {
    switch (activity.status) {
      case 'completed': return 'bg-green-100 text-green-700'
      case 'in-progress': return 'bg-yellow-100 text-yellow-700'
      case 'pending': return 'bg-gray-100 text-gray-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  const timeAgo = (timestamp: Date) => {
    const now = new Date()
    const diff = now.getTime() - timestamp.getTime()
    const minutes = Math.floor(diff / (1000 * 60))
    const hours = Math.floor(diff / (1000 * 60 * 60))
    
    if (minutes < 60) return `${minutes}m ago`
    return `${hours}h ago`
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      whileHover={{ x: 5 }}
      className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors cursor-pointer"
    >
      <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600 flex-shrink-0">
        {getActivityIcon()}
      </div>
      <div className="flex-1 min-w-0">
        <h4 className="font-medium text-gray-900 truncate">{activity.title}</h4>
        <p className="text-sm text-gray-600 truncate">{activity.description}</p>
        <div className="flex items-center space-x-2 mt-1">
          <span className="text-xs text-gray-500">{timeAgo(activity.timestamp)}</span>
          {activity.agent && (
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
              {activity.agent}
            </span>
          )}
          {activity.status && (
            <span className={`text-xs px-2 py-0.5 rounded ${getStatusColor()}`}>
              {activity.status}
            </span>
          )}
        </div>
      </div>
    </motion.div>
  )
}

const LearningPathCard = ({ path }: { path: LearningPath }) => {
  const getDifficultyColor = () => {
    switch (path.difficulty) {
      case 'beginner': return 'bg-green-100 text-green-700'
      case 'intermediate': return 'bg-yellow-100 text-yellow-700'
      case 'advanced': return 'bg-red-100 text-red-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300"
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-semibold text-gray-900 mb-1">{path.title}</h3>
          <p className="text-sm text-gray-600">{path.description}</p>
        </div>
        <span className={`text-xs px-2 py-1 rounded ${getDifficultyColor()}`}>
          {path.difficulty}
        </span>
      </div>

      <div className="mb-4">
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="text-gray-600">Progress</span>
          <span className="font-medium">{path.progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${path.progress}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
            className="h-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500"
          />
        </div>
      </div>

      <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
        <span>{path.completedModules}/{path.totalModules} modules</span>
        <span>{path.estimatedTime} remaining</span>
      </div>

      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="w-full bg-indigo-50 text-indigo-600 py-2 rounded-lg font-medium hover:bg-indigo-100 transition-colors flex items-center justify-center space-x-2"
      >
        <span>Continue Learning</span>
        <ArrowRight className="w-4 h-4" />
      </motion.button>
    </motion.div>
  )
}

const TaskCard = ({ task }: { task: TaskRecommendation }) => {
  const getDifficultyColor = () => {
    switch (task.difficulty) {
      case 'easy': return 'bg-green-100 text-green-700'
      case 'medium': return 'bg-yellow-100 text-yellow-700'
      case 'hard': return 'bg-red-100 text-red-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  const getPriorityColor = () => {
    switch (task.priority) {
      case 'high': return 'bg-red-100 text-red-700'
      case 'medium': return 'bg-yellow-100 text-yellow-700'
      case 'low': return 'bg-green-100 text-green-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  return (
    <motion.div
      whileHover={{ scale: 1.01, y: -1 }}
      className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-300"
    >
      <div className="flex items-start justify-between mb-3">
        <h4 className="font-medium text-gray-900 text-sm">{task.title}</h4>
        <span className={`text-xs px-2 py-1 rounded ${getPriorityColor()}`}>
          {task.priority}
        </span>
      </div>

      <p className="text-sm text-gray-600 mb-3">{task.description}</p>

      <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
        <span className={`px-2 py-1 rounded ${getDifficultyColor()}`}>
          {task.difficulty}
        </span>
        <span>{task.estimatedTime}</span>
      </div>

      <div className="flex flex-wrap gap-1 mb-3">
        {task.skillsRequired.map((skill, index) => (
          <span key={index} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
            {skill}
          </span>
        ))}
      </div>

      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="w-full bg-orange-50 text-orange-600 py-2 rounded-lg text-sm font-medium hover:bg-orange-100 transition-colors"
      >
        Start Task
      </motion.button>
    </motion.div>
  )
}

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('overview')
  const [timeRange, setTimeRange] = useState('week')
  const [isLiveMode, setIsLiveMode] = useState(true)

  // Mock stats
  const stats = {
    totalInteractions: 147,
    averageResponseTime: '2.3s',
    completionRate: 85,
    learningStreak: 7
  }

  const chartData = [
    { name: 'Mon', interactions: 12, tasks: 3, learning: 2 },
    { name: 'Tue', interactions: 19, tasks: 5, learning: 3 },
    { name: 'Wed', interactions: 24, tasks: 4, learning: 4 },
    { name: 'Thu', interactions: 15, tasks: 6, learning: 2 },
    { name: 'Fri', interactions: 28, tasks: 8, learning: 5 },
    { name: 'Sat', interactions: 8, tasks: 2, learning: 1 },
    { name: 'Sun', interactions: 6, tasks: 1, learning: 2 }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="flex items-center space-x-3">
                <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-2 rounded-xl">
                  <Zap className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">ZeroDay Dashboard</h1>
                  <p className="text-sm text-gray-600">Your onboarding progress</p>
                </div>
              </Link>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Live Mode Toggle */}
              <motion.button
                onClick={() => setIsLiveMode(!isLiveMode)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                  isLiveMode 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-gray-100 text-gray-600'
                }`}
              >
                <div className={`w-2 h-2 rounded-full ${isLiveMode ? 'bg-green-500' : 'bg-gray-400'}`} />
                <span className="text-sm font-medium">Live</span>
              </motion.button>

              {/* Notifications */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Bell className="w-5 h-5" />
                <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
              </motion.button>

              {/* Settings */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Settings className="w-5 h-5" />
              </motion.button>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center space-x-8 mt-6">
            {[
              { id: 'overview', label: 'Overview', icon: <BarChart3 className="w-4 h-4" /> },
              { id: 'learning', label: 'Learning Paths', icon: <BookOpen className="w-4 h-4" /> },
              { id: 'tasks', label: 'Tasks', icon: <CheckSquare className="w-4 h-4" /> },
              { id: 'analytics', label: 'Analytics', icon: <TrendingUp className="w-4 h-4" /> }
            ].map((tab) => (
              <motion.button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  activeTab === tab.id
                    ? 'bg-indigo-100 text-indigo-700 border border-indigo-200'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                {tab.icon}
                <span className="font-medium">{tab.label}</span>
              </motion.button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              {/* Welcome Section */}
              <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold mb-2">Welcome back, Alex! 👋</h2>
                    <p className="text-indigo-100 mb-4">
                      You're making great progress. You've completed 85% of your onboarding goals this week!
                    </p>
                    <div className="flex items-center space-x-6">
                      <div className="flex items-center space-x-2">
                        <Flame className="w-5 h-5" />
                        <span>{stats.learningStreak} day streak</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Clock className="w-5 h-5" />
                        <span>{stats.averageResponseTime} avg response</span>
                      </div>
                    </div>
                  </div>
                  <div className="hidden md:block">
                    <div className="w-32 h-32 bg-white/10 rounded-full flex items-center justify-center">
                      <TrendingUp className="w-16 h-16" />
                    </div>
                  </div>
                </div>
              </div>

              {/* Progress Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {progressData.map((data, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1, duration: 0.6 }}
                  >
                    <ProgressCard data={data} />
                  </motion.div>
                ))}
              </div>

              {/* Main Content Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Recent Activity */}
                <div className="lg:col-span-2">
                  <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                        <Activity className="w-5 h-5 mr-2 text-indigo-600" />
                        Recent Activity
                      </h3>
                      <div className="flex items-center space-x-2">
                        <select 
                          value={timeRange}
                          onChange={(e) => setTimeRange(e.target.value)}
                          className="text-sm bg-gray-100 border-0 rounded-lg px-3 py-1 focus:ring-2 focus:ring-indigo-500"
                        >
                          <option value="day">Today</option>
                          <option value="week">This Week</option>
                          <option value="month">This Month</option>
                        </select>
                        <motion.button
                          whileHover={{ rotate: 180 }}
                          className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
                        >
                          <RefreshCw className="w-4 h-4" />
                        </motion.button>
                      </div>
                    </div>
                    
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                      {recentActivity.map((activity, index) => (
                        <motion.div
                          key={activity.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                        >
                          <ActivityItem activity={activity} />
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Quick Actions & Stats */}
                <div className="space-y-6">
                  {/* Quick Actions */}
                  <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <Lightbulb className="w-5 h-5 mr-2 text-yellow-500" />
                      Quick Actions
                    </h3>
                    <div className="space-y-3">
                      <Link href="/chat">
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          className="w-full bg-indigo-50 text-indigo-600 p-3 rounded-lg hover:bg-indigo-100 transition-colors flex items-center space-x-2"
                        >
                          <MessageSquare className="w-4 h-4" />
                          <span>Ask AI Assistant</span>
                        </motion.button>
                      </Link>
                      <Link href="/tasks">
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          className="w-full bg-green-50 text-green-600 p-3 rounded-lg hover:bg-green-100 transition-colors flex items-center space-x-2"
                        >
                          <CheckSquare className="w-4 h-4" />
                          <span>View Tasks</span>
                        </motion.button>
                      </Link>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className="w-full bg-purple-50 text-purple-600 p-3 rounded-lg hover:bg-purple-100 transition-colors flex items-center space-x-2"
                      >
                        <Code className="w-4 h-4" />
                        <span>Explore Codebase</span>
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className="w-full bg-orange-50 text-orange-600 p-3 rounded-lg hover:bg-orange-100 transition-colors flex items-center space-x-2"
                      >
                        <BookOpen className="w-4 h-4" />
                        <span>Continue Learning</span>
                      </motion.button>
                    </div>
                  </div>

                  {/* Today's Goals */}
                  <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <Target className="w-5 h-5 mr-2 text-red-500" />
                      Today's Goals
                    </h3>
                    <div className="space-y-3">
                      {[
                        { task: 'Complete React module', completed: true },
                        { task: 'Review 3 PRs', completed: true },
                        { task: 'Fix authentication bug', completed: false },
                        { task: 'Write unit tests', completed: false }
                      ].map((goal, index) => (
                        <div key={index} className="flex items-center space-x-3">
                          <div className={`w-4 h-4 rounded-full flex items-center justify-center ${
                            goal.completed ? 'bg-green-500' : 'bg-gray-300'
                          }`}>
                            {goal.completed && <CheckSquare className="w-2.5 h-2.5 text-white" />}
                          </div>
                          <span className={`text-sm ${
                            goal.completed ? 'text-gray-500 line-through' : 'text-gray-900'
                          }`}>
                            {goal.task}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'learning' && (
            <motion.div
              key="learning"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Learning Paths</h2>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors flex items-center space-x-2"
                >
                  <BookOpen className="w-4 h-4" />
                  <span>Create Custom Path</span>
                </motion.button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {learningPaths.map((path, index) => (
                  <motion.div
                    key={path.id}
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1, duration: 0.6 }}
                  >
                    <LearningPathCard path={path} />
                  </motion.div>
                ))}
              </div>

              {/* Learning Analytics */}
              <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-6">Learning Analytics</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                      <TrendingUp className="w-8 h-8 text-green-600" />
                    </div>
                    <div className="text-2xl font-bold text-gray-900">12h 30m</div>
                    <div className="text-sm text-gray-600">Time This Week</div>
                  </div>
                  <div className="text-center">
                    <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                      <Award className="w-8 h-8 text-blue-600" />
                    </div>
                    <div className="text-2xl font-bold text-gray-900">15</div>
                    <div className="text-sm text-gray-600">Modules Completed</div>
                  </div>
                  <div className="text-center">
                    <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                      <Star className="w-8 h-8 text-purple-600" />
                    </div>
                    <div className="text-2xl font-bold text-gray-900">4.8</div>
                    <div className="text-sm text-gray-600">Average Rating</div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'tasks' && (
            <motion.div
              key="tasks"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Recommended Tasks</h2>
                <div className="flex items-center space-x-4">
                  <select className="bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500">
                    <option>All Categories</option>
                    <option>Frontend</option>
                    <option>Backend</option>
                    <option>DevOps</option>
                  </select>
                  <select className="bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500">
                    <option>All Difficulties</option>
                    <option>Easy</option>
                    <option>Medium</option>
                    <option>Hard</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {taskRecommendations.map((task, index) => (
                  <motion.div
                    key={task.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1, duration: 0.6 }}
                  >
                    <TaskCard task={task} />
                  </motion.div>
                ))}
              </div>

              {/* Task Analytics */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Task Completion Rate</h3>
                  <div className="space-y-4">
                    {[
                      { category: 'Frontend', completed: 8, total: 10, color: 'from-blue-500 to-blue-600' },
                      { category: 'Backend', completed: 5, total: 8, color: 'from-green-500 to-green-600' },
                      { category: 'DevOps', completed: 2, total: 5, color: 'from-purple-500 to-purple-600' }
                    ].map((item, index) => (
                      <div key={index}>
                        <div className="flex items-center justify-between text-sm mb-2">
                          <span className="text-gray-600">{item.category}</span>
                          <span className="font-medium">{item.completed}/{item.total}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full bg-gradient-to-r ${item.color}`}
                            style={{ width: `${(item.completed / item.total) * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Weekly Task Activity</h3>
                  <div className="space-y-3">
                    {chartData.map((day, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 w-8">{day.name}</span>
                        <div className="flex-1 mx-4">
                          <div className="flex space-x-1">
                            <div 
                              className="bg-blue-200 h-4 rounded"
                              style={{ width: `${(day.tasks / 8) * 100}%` }}
                            />
                          </div>
                        </div>
                        <span className="text-sm font-medium text-gray-900 w-6">{day.tasks}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'analytics' && (
            <motion.div
              key="analytics"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Analytics & Insights</h2>
                <div className="flex items-center space-x-4">
                  <select 
                    value={timeRange}
                    onChange={(e) => setTimeRange(e.target.value)}
                    className="bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="week">This Week</option>
                    <option value="month">This Month</option>
                    <option value="quarter">This Quarter</option>
                  </select>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors flex items-center space-x-2"
                  >
                    <Download className="w-4 h-4" />
                    <span>Export</span>
                  </motion.button>
                </div>
              </div>

              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {[
                  { 
                    label: 'Total Interactions', 
                    value: stats.totalInteractions, 
                    change: '+23%', 
                    positive: true,
                    icon: <MessageSquare className="w-5 h-5" />
                  },
                  { 
                    label: 'Avg Response Time', 
                    value: stats.averageResponseTime, 
                    change: '-15%', 
                    positive: true,
                    icon: <Clock className="w-5 h-5" />
                  },
                  { 
                    label: 'Completion Rate', 
                    value: `${stats.completionRate}%`, 
                    change: '+8%', 
                    positive: true,
                    icon: <Target className="w-5 h-5" />
                  },
                  { 
                    label: 'Learning Streak', 
                    value: `${stats.learningStreak} days`, 
                    change: '+2 days', 
                    positive: true,
                    icon: <Flame className="w-5 h-5" />
                  }
                ].map((metric, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1, duration: 0.6 }}
                    className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-gray-600">{metric.icon}</div>
                      <span className={`text-sm font-medium flex items-center ${
                        metric.positive ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {metric.positive ? <ArrowUp className="w-3 h-3 mr-1" /> : <ArrowDown className="w-3 h-3 mr-1" />}
                        {metric.change}
                      </span>
                    </div>
                    <div className="text-2xl font-bold text-gray-900 mb-1">{metric.value}</div>
                    <div className="text-sm text-gray-600">{metric.label}</div>
                  </motion.div>
                ))}
              </div>

              {/* Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Weekly Activity</h3>
                  <div className="h-64 flex items-end justify-between space-x-2">
                    {chartData.map((day, index) => (
                      <div key={index} className="flex-1 flex flex-col items-center">
                        <div className="w-full bg-gray-100 rounded-t relative" style={{ height: '200px' }}>
                          <motion.div
                            initial={{ height: 0 }}
                            animate={{ height: `${(day.interactions / 30) * 100}%` }}
                            transition={{ delay: index * 0.1, duration: 0.6 }}
                            className="absolute bottom-0 w-full bg-gradient-to-t from-indigo-500 to-indigo-400 rounded-t"
                          />
                        </div>
                        <span className="text-xs text-gray-600 mt-2">{day.name}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Usage</h3>
                  <div className="space-y-4">
                    {[
                      { name: 'Knowledge Agent', usage: 45, color: 'from-blue-500 to-blue-600' },
                      { name: 'Task Agent', usage: 25, color: 'from-orange-500 to-orange-600' },
                      { name: 'Guide Agent', usage: 20, color: 'from-green-500 to-green-600' },
                      { name: 'Mentor Agent', usage: 10, color: 'from-purple-500 to-purple-600' }
                    ].map((agent, index) => (
                      <div key={index} className="flex items-center space-x-4">
                        <div className="w-20 text-sm text-gray-600">{agent.name}</div>
                        <div className="flex-1 bg-gray-200 rounded-full h-3">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${agent.usage}%` }}
                            transition={{ delay: index * 0.1, duration: 0.6 }}
                            className={`h-3 rounded-full bg-gradient-to-r ${agent.color}`}
                          />
                        </div>
                        <div className="w-12 text-sm font-medium text-gray-900">{agent.usage}%</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Insights */}
              <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Insights</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-4 rounded-xl border border-green-200">
                    <div className="flex items-start space-x-3">
                      <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                        <TrendingUp className="w-4 h-4 text-white" />
                      </div>
                      <div>
                        <h4 className="font-medium text-green-900 mb-1">Great Progress!</h4>
                        <p className="text-sm text-green-700">
                          Your learning velocity has increased 23% this week. Keep up the momentum!
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-xl border border-blue-200">
                    <div className="flex items-start space-x-3">
                      <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                        <Lightbulb className="w-4 h-4 text-white" />
                      </div>
                      <div>
                        <h4 className="font-medium text-blue-900 mb-1">Suggestion</h4>
                        <p className="text-sm text-blue-700">
                          Consider focusing on backend tasks to balance your skill development.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}