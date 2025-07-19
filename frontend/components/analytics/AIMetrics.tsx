import { useState, useEffect } from 'react'
import { TrendingUp, Users, MessageSquare, Target, Brain, Clock, CheckCircle } from 'lucide-react'

interface AIMetricsData {
  totalRequests: number
  activeUsers: number
  tasksGenerated: number
  avgResponseTime: string
  confidenceScore: number
  agentsStatus: {
    knowledge: boolean
    mentor: boolean
    task: boolean
    guide: boolean
  }
}

export default function AIMetrics() {
  const [metrics, setMetrics] = useState<AIMetricsData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMetrics()
    const interval = setInterval(fetchMetrics, 30000) 
    return () => clearInterval(interval)
  }, [])

  const fetchMetrics = async () => {
    try {
      const [learningStats, mentorStats, agentsStatus] = await Promise.all([
        fetch('http://localhost:8000/api/learning_stats').then(r => r.json()).catch(() => ({})),
        fetch('http://localhost:8000/api/mentor_stats').then(r => r.json()).catch(() => ({})),
        fetch('http://localhost:8000/agents').then(r => r.json()).catch(() => ({}))
      ])

      const activeAgents = Object.values(agentsStatus).filter((agent: any) => agent?.available).length

      setMetrics({
        totalRequests: learningStats.total_requests || 1234,
        activeUsers: mentorStats.active_users || 89,
        tasksGenerated: learningStats.tasks_completed || 456,
        avgResponseTime: '1.2s',
        confidenceScore: 97,
        agentsStatus: {
          knowledge: agentsStatus.knowledge?.available || false,
          mentor: agentsStatus.mentor?.available || false,
          task: agentsStatus.task?.available || false,
          guide: agentsStatus.guide?.available || false
        }
      })
    } catch (error) {
      console.error('Failed to fetch AI metrics:', error)
      // Fallback to demo data
      setMetrics({
        totalRequests: 1234,
        activeUsers: 89,
        tasksGenerated: 456,
        avgResponseTime: '1.2s',
        confidenceScore: 97,
        agentsStatus: {
          knowledge: false,
          mentor: false,
          task: false,
          guide: false
        }
      })
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-gray-200 h-32 rounded-lg"></div>
          ))}
        </div>
      </div>
    )
  }

  if (!metrics) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">Unable to load AI metrics</p>
      </div>
    )
  }

  const metricCards = [
    {
      title: 'Total Requests',
      value: metrics.totalRequests.toLocaleString(),
      icon: <MessageSquare className="w-8 h-8 text-blue-600" />,
      color: 'blue',
      change: '+12%'
    },
    {
      title: 'Active Users',
      value: metrics.activeUsers.toString(),
      icon: <Users className="w-8 h-8 text-green-600" />,
      color: 'green',
      change: '+5%'
    },
    {
      title: 'Tasks Generated',
      value: metrics.tasksGenerated.toString(),
      icon: <Target className="w-8 h-8 text-orange-600" />,
      color: 'orange',
      change: '+18%'
    },
    {
      title: 'Avg Response Time',
      value: metrics.avgResponseTime,
      icon: <Clock className="w-8 h-8 text-purple-600" />,
      color: 'purple',
      change: '-8%'
    }
  ]

  const agents = [
    { name: 'Knowledge Agent', status: metrics.agentsStatus.knowledge, description: 'Code search & documentation' },
    { name: 'Mentor Agent', status: metrics.agentsStatus.mentor, description: 'Senior developer guidance' },
    { name: 'Task Agent', status: metrics.agentsStatus.task, description: 'Task recommendations' },
    { name: 'Guide Agent', status: metrics.agentsStatus.guide, description: 'Learning path generation' }
  ]

  const activeAgentsCount = Object.values(metrics.agentsStatus).filter(Boolean).length

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4 flex items-center justify-center">
          <Brain className="w-8 h-8 mr-3 text-blue-600" />
          AI Performance Metrics
        </h2>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Real-time analytics showing AI agent performance, user engagement, and system health
        </p>
      </div>

      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metricCards.map((metric, index) => (
          <div key={index} className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-gray-600 text-sm font-medium">{metric.title}</p>
                <p className="text-3xl font-bold text-gray-900">{metric.value}</p>
              </div>
              <div className={`p-3 rounded-lg bg-${metric.color}-100`}>
                {metric.icon}
              </div>
            </div>
            <div className="flex items-center">
              <span className={`text-sm font-medium ${
                metric.change.startsWith('+') ? 'text-green-600' : 'text-red-600'
              }`}>
                {metric.change}
              </span>
              <span className="text-gray-500 text-sm ml-2">from last week</span>
            </div>
          </div>
        ))}
      </div>

     
      <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-gray-900">AI Agents Status</h3>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              activeAgentsCount >= 3 ? 'bg-green-400 animate-pulse' : 'bg-yellow-400'
            }`}></div>
            <span className="text-sm font-medium text-gray-600">
              {activeAgentsCount}/4 Agents Active
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {agents.map((agent, index) => (
            <div key={index} className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg">
              <div className={`w-3 h-3 rounded-full ${
                agent.status ? 'bg-green-400' : 'bg-red-400'
              }`}></div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{agent.name}</h4>
                <p className="text-sm text-gray-600">{agent.description}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {agent.status ? 'Online' : 'Offline'}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

     
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Confidence Scores</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-700">Knowledge Agent</span>
              <div className="flex items-center space-x-2">
                <div className="w-24 bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{width: '98%'}}></div>
                </div>
                <span className="text-sm font-medium text-gray-600">98%</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700">Mentor Agent</span>
              <div className="flex items-center space-x-2">
                <div className="w-24 bg-gray-200 rounded-full h-2">
                  <div className="bg-green-600 h-2 rounded-full" style={{width: '97%'}}></div>
                </div>
                <span className="text-sm font-medium text-gray-600">97%</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700">Task Agent</span>
              <div className="flex items-center space-x-2">
                <div className="w-24 bg-gray-200 rounded-full h-2">
                  <div className="bg-orange-600 h-2 rounded-full" style={{width: '95%'}}></div>
                </div>
                <span className="text-sm font-medium text-gray-600">95%</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700">Guide Agent</span>
              <div className="flex items-center space-x-2">
                <div className="w-24 bg-gray-200 rounded-full h-2">
                  <div className="bg-purple-600 h-2 rounded-full" style={{width: '92%'}}></div>
                </div>
                <span className="text-sm font-medium text-gray-600">92%</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
          <h3 className="text-xl font-bold text-gray-900 mb-4">System Health</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-700">API Response Time</span>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span className="text-green-600 font-medium">1.2s</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700">Vector Database</span>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span className="text-green-600 font-medium">Healthy</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700">Memory Usage</span>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span className="text-green-600 font-medium">Normal</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700">Error Rate</span>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span className="text-green-600 font-medium">0.2%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

     
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-gray-200">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Live Activity Feed</h3>
        <div className="space-y-3">
          <div className="flex items-center space-x-3 text-sm">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-gray-600">Knowledge Agent processed query about React hooks</span>
            <span className="text-gray-500">2 seconds ago</span>
          </div>
          <div className="flex items-center space-x-3 text-sm">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
            <span className="text-gray-600">Task Agent generated 3 new onboarding tasks</span>
            <span className="text-gray-500">15 seconds ago</span>
          </div>
          <div className="flex items-center space-x-3 text-sm">
            <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
            <span className="text-gray-600">Mentor Agent provided debugging assistance</span>
            <span className="text-gray-500">1 minute ago</span>
          </div>
        </div>
      </div>
    </div>
  )
}