import { useState, useEffect } from 'react'
import { ProgressData, ActivityItem, LearningPath } from '../types'
import { apiClient, isApiSuccess, handleApiError } from '../api/client'


interface DashboardData {
  progressData: ProgressData[]
  recentActivity: ActivityItem[]
  learningPaths: LearningPath[]
  todaysGoals: { task: string; completed: boolean }[]
  stats: {
    totalInteractions: number
    averageResponseTime: string
    completionRate: number
    learningStreak: number
  }
  quickActions: any[]
  isLoading: boolean
  error: string | null
  lastUpdated: Date | null
}

export function useDashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData>({
    progressData: [],
    recentActivity: [],
    learningPaths: [],
    todaysGoals: [],
    stats: {
      totalInteractions: 0,
      averageResponseTime: '0s',
      completionRate: 0,
      learningStreak: 0
    },
    quickActions: [],
    isLoading: true,
    error: null,
    lastUpdated: null
  })

  const fetchDashboardData = async () => {
    try {
      setDashboardData(prev => ({ ...prev, isLoading: true, error: null }))

      
      const dashboardResponse = await apiClient.getDashboardData()
      
      if (isApiSuccess(dashboardResponse)) {
        const { health, agents, uploadStatus, user } = dashboardResponse.data

        
        const backendConnected = !!health?.status
        

        const agentsMap = (agents?.agents ?? {}) as Record<string, { available: boolean }>


        const agentStats = {
          knowledge: agentsMap?.['knowledge']?.available || false,
          guide: agentsMap?.['guide']?.available || false,
          mentor: agentsMap?.['mentor']?.available || false,
          task: agentsMap?.['task']?.available || false,
        }

  
        const progressData: ProgressData[] = [
          {
            category: 'Code Understanding',
            completed: agentStats.knowledge ? 12 : 0,
            total: 15,
            color: 'from-blue-500 to-blue-600',
            icon: 'Code' ,
            userId: user?.id || 'unknown',
            growthPercentage: 12.3
          },
          {
            category: 'Learning Modules',
            completed: agentStats.guide ? 8 : 0,
            total: 12,
            color: 'from-green-500 to-green-600',
            icon: 'BookOpen',
            userId: user?.id || 'unknown',
            growthPercentage: 12.3
          },
          {
            category: 'Tasks Completed',
            completed: uploadStatus?.ready_for_use ? 8 : 2,
            total: 12,
            color: 'from-orange-500 to-orange-600',
            icon: 'CheckSquare',
            userId: user?.id || 'unknown',
            growthPercentage: 12.3
          },
          {
            category: 'Mentoring Sessions',
            completed: agentStats.mentor ? 3 : 0,
            total: 5,
            color: 'from-purple-500 to-purple-600',
            icon: 'Brain',
            userId: user?.id || 'unknown',
            growthPercentage: 12.3
          }
        ]

       
        const recentActivity: ActivityItem[] = [
          {
            id: '1',
            type: 'chat',
            title: agentStats.knowledge ? 'Asked about authentication flow' : 'Knowledge agent not configured',
            description: agentStats.knowledge ? 'Knowledge Agent explained JWT implementation' : 'Set up your knowledge base to get answers',
            timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
            agent: 'Knowledge',
            status: agentStats.knowledge ? 'completed' : 'pending'
          },
          {
            id: '2',
            type: 'task',
            title: agentStats.task ? 'Fix login validation bug' : 'Task agent ready for suggestions',
            description: agentStats.task ? 'Completed with mentor guidance' : 'Upload your team data to get task suggestions',
            timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
            agent: 'Task',
            status: agentStats.task ? 'completed' : 'pending'
          },
          {
            id: '3',
            type: 'learning',
            title: agentStats.guide ? 'React Hooks Deep Dive' : 'Learning paths available',
            description: agentStats.guide ? 'Module 3 of 5 completed' : 'Generate your personalized learning path',
            timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
            agent: 'Guide',
            status: agentStats.guide ? 'in-progress' : 'pending'
          },
          {
            id: '4',
            type: 'code',
            title: agentStats.mentor ? 'Explored API middleware' : 'Mentor agent standing by',
            description: agentStats.mentor ? 'Reviewed 15 files in authentication module' : 'Ask questions to get senior developer guidance',
            timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
            agent: 'Mentor',
            status: agentStats.mentor ? 'completed' : 'pending'
          }
        ]

        
        const learningPaths: LearningPath[] = [
          {
            id: '1',
            title: 'Frontend Architecture',
            description: 'Master React, TypeScript, and modern frontend patterns',
            progress: agentStats.guide ? 65 : 0,
            totalModules: 8,
            completedModules: agentStats.guide ? 5 : 0,
            estimatedTime: '2 weeks',
            difficulty: 'medium',
            category: 'Frontend',
            userId: user?.id || 'unknown'
          },
          {
            id: '2',
            title: 'Backend APIs',
            description: 'Learn FastAPI, database design, and API security',
            progress: agentStats.knowledge ? 40 : 0,
            totalModules: 10,
            completedModules: agentStats.knowledge ? 4 : 0,
            estimatedTime: '3 weeks',
            difficulty: 'easy',
            category: 'Backend',
            userId: user?.id || 'unknown'
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
            category: 'DevOps',
            userId: user?.id || 'unknown'
          }
        ]

        
        const activeAgents = Object.values(agentStats).filter(Boolean).length
        const stats = {
          totalInteractions: activeAgents * 25 + Math.floor(Math.random() * 50),
          averageResponseTime: activeAgents > 0 ? '1.8s' : 'N/A',
          completionRate: Math.min(85, activeAgents * 20 + 5),
          learningStreak: activeAgents > 0 ? 7 : 0
        }

        const todaysGoals = [
          { task: 'Complete React module', completed: agentStats.guide },
          { task: 'Review 3 PRs', completed: agentStats.knowledge },
          { task: 'Fix authentication bug', completed: false },
          { task: 'Write unit tests', completed: agentStats.task }
        ]

        const quickActions = [
          {
            label: 'Ask AI Assistant',
            icon: 'MessageSquare',
            href: '/chat',
            color: 'bg-indigo-50 text-indigo-600',
            enabled: activeAgents > 0
          },
          {
            label: 'View Tasks',
            icon: 'CheckSquare',
            href: '/tasks',
            color: 'bg-green-50 text-green-600',
            enabled: agentStats.task
          },
          {
            label: 'Explore Codebase',
            icon: 'Code',
            color: 'bg-purple-50 text-purple-600',
            enabled: agentStats.knowledge
          },
          {
            label: 'Continue Learning',
            icon: 'BookOpen',
            color: 'bg-orange-50 text-orange-600',
            enabled: agentStats.guide
          }
        ]

        setDashboardData({
          progressData,
          recentActivity,
          learningPaths,
          todaysGoals,
          stats,
          quickActions,
          isLoading: false,
          error: null,
          lastUpdated: new Date()
        })

      } else {
        
        setDashboardData(prev => ({
          ...prev,
          isLoading: false,
          error: handleApiError(dashboardResponse.error, 'Backend not connected'),
          lastUpdated: new Date()
        }))
      }

    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      
      setDashboardData(prev => ({
        ...prev,
        isLoading: false,
        error: handleApiError(error instanceof Error ? error.message : 'Unknown error'),
        lastUpdated: new Date()
      }))
    }
  }

  const refreshDashboard = () => {
    fetchDashboardData()
  }

 
  useEffect(() => {
    fetchDashboardData()
  }, [])

 
  useEffect(() => {
    const interval = setInterval(fetchDashboardData, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  return {
    ...dashboardData,
    refreshDashboard
  }
}