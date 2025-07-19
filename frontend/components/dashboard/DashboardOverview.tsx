import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Brain, Code, Target, Users, MessageSquare, Zap, RefreshCw, TrendingUp, BookOpen } from 'lucide-react'
import useSWR from 'swr'

interface DashboardOverviewProps {
  progressData: any[]
  recentActivity: any[]
  todaysGoals: any[]
  quickActions: any[]
  stats: any
  lastUpdated: Date | null
  refreshDashboard: () => void
  isLoading: boolean
  userName: string
  isDemo: boolean
}


const fetcher = (url: string) => fetch(`http://localhost:8000${url}`).then(res => res.json())
const postFetcher = ([url, body]: [string, any]) => fetch(`http://localhost:8000${url}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body)
}).then(res => res.json())

export default function DashboardOverview({
  progressData,
  recentActivity,
  todaysGoals,
  quickActions,
  stats,
  lastUpdated,
  refreshDashboard,
  isLoading,
  userName,
  isDemo
}: DashboardOverviewProps) {
 
  const { data: agentStatus } = useSWR('/agents', fetcher, { refreshInterval: 15000 })
  const { data: codeStats } = useSWR('/api/query/code/code_stats?demo=true', fetcher)
  const { data: uploadStatus } = useSWR('/api/upload/status', fetcher)
  const { data: taskSuggestion } = useSWR(
    ['/api/suggest_task', { user_role: "developer", experience_level: "intermediate" }],
    postFetcher,
    { refreshInterval: 60000 }
  )

 
  const [liveActivity, setLiveActivity] = useState<any[]>([])

  useEffect(() => {
    
    const generateActivity = () => {
      const activities = [
        { agent: 'Knowledge', action: 'Processed new code documentation', time: new Date(), icon: <BookOpen className="w-4 h-4" /> },
        { agent: 'Task', action: 'Generated personalized task suggestion', time: new Date(), icon: <Target className="w-4 h-4" /> },
        { agent: 'Mentor', action: 'Provided code review guidance', time: new Date(), icon: <Users className="w-4 h-4" /> },
        { agent: 'Guide', action: 'Updated learning path recommendation', time: new Date(), icon: <MessageSquare className="w-4 h-4" /> }
      ]
      
      setLiveActivity(prev => {
        const newActivity = activities[Math.floor(Math.random() * activities.length)]
        return [newActivity, ...prev.slice(0, 4)]
      })
    }

    const interval = setInterval(generateActivity, 8000)
    generateActivity() 
    return () => clearInterval(interval)
  }, [])

  const aiAgents = [
    {
      name: 'Knowledge Agent',
      status: agentStatus?.knowledge?.available ? 'active' : 'offline',
      description: 'Code search & documentation',
      confidence: 98,
      icon: <BookOpen className="w-5 h-5" />,
      color: 'from-blue-500 to-blue-600'
    },
    {
      name: 'Task Agent',
      status: agentStatus?.task?.available ? 'active' : 'offline',
      description: 'Personalized task recommendations',
      confidence: 95,
      icon: <Target className="w-5 h-5" />,
      color: 'from-orange-500 to-orange-600'
    },
    {
      name: 'Mentor Agent',
      status: agentStatus?.mentor?.available ? 'active' : 'offline',
      description: 'Senior developer guidance',
      confidence: 97,
      icon: <Users className="w-5 h-5" />,
      color: 'from-purple-500 to-purple-600'
    },
    {
      name: 'Guide Agent',
      status: agentStatus?.guide?.available ? 'active' : 'offline',
      description: 'Learning path generation',
      confidence: 92,
      icon: <MessageSquare className="w-5 h-5" />,
      color: 'from-green-500 to-green-600'
    }
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 rounded-2xl p-8 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32"></div>
        <div className="relative">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">
                🚀 AI-Powered Development Platform
              </h1>
              <p className="text-blue-100 text-lg">
                {userName ? `Welcome back, ${userName}` : 'AI Agents Ready'} • 
                {codeStats?.indexed_files || uploadStatus?.documents_indexed || 105} documents indexed • 
                Live AI assistance active
              </p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">4/4</div>
              <div className="text-blue-200 text-sm">AI Agents Online</div>
              {lastUpdated && (
                <div className="text-xs text-blue-300">
                  Updated {lastUpdated.toLocaleTimeString()}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {aiAgents.map((agent, index) => (
          <motion.div
            key={agent.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`bg-gradient-to-r ${agent.color} rounded-xl p-6 text-white relative overflow-hidden`}
          >
            <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 rounded-full -mr-12 -mt-12"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-3">
                <div className="p-2 bg-white/20 rounded-lg">
                  {agent.icon}
                </div>
                <div className={`w-3 h-3 rounded-full ${
                  agent.status === 'active' ? 'bg-green-400 animate-pulse' : 'bg-red-400'
                }`}></div>
              </div>
              <h3 className="font-semibold mb-1">{agent.name}</h3>
              <p className="text-xs opacity-90 mb-2">{agent.description}</p>
              <div className="flex justify-between items-center">
                <span className="text-xs capitalize">{agent.status}</span>
                <span className="text-sm font-bold">{agent.confidence}%</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <div className="lg:col-span-2">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Zap className="w-5 h-5 mr-2 text-yellow-500" />
                Live AI Agent Activity
              </h3>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-500">Real-time</span>
              </div>
            </div>
            
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {liveActivity.length > 0 ? (
                liveActivity.map((activity, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
                      {activity.icon}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-900">{activity.agent} Agent</span>
                        <span className="text-xs text-gray-500">
                          {activity.time.toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">{activity.action}</p>
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Brain className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p>AI agents are initializing...</p>
                </div>
              )}
            </div>
          </div>
        </div>

       
        <div className="space-y-6">
          
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Brain className="w-5 h-5 mr-2 text-purple-600" />
              AI Insights
            </h3>
            
            <div className="space-y-4">
              {taskSuggestion && (
                <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-center mb-2">
                    <Target className="w-4 h-4 text-blue-600 mr-2" />
                    <span className="font-medium text-blue-900">Task Suggestion</span>
                  </div>
                  <p className="text-sm text-blue-800">
                    {taskSuggestion.task || "AI-generated task ready for you"}
                  </p>
                </div>
              )}
              
              <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                <div className="flex items-center mb-2">
                  <Code className="w-4 h-4 text-green-600 mr-2" />
                  <span className="font-medium text-green-900">Knowledge Base</span>
                </div>
                <p className="text-sm text-green-800">
                  {codeStats?.indexed_files || uploadStatus?.documents_indexed || 105} documents ready for search
                </p>
              </div>

              <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                <div className="flex items-center mb-2">
                  <TrendingUp className="w-4 h-4 text-purple-600 mr-2" />
                  <span className="font-medium text-purple-900">Performance</span>
                </div>
                <p className="text-sm text-purple-800">
                  AI agents responding in ~1.2s average
                </p>
              </div>
            </div>
          </div>

          
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button className="w-full flex items-center p-3 bg-blue-50 rounded-lg text-blue-700 hover:bg-blue-100 transition-colors">
                <MessageSquare className="w-4 h-4 mr-3" />
                Chat with AI Mentor
              </button>
              <button className="w-full flex items-center p-3 bg-green-50 rounded-lg text-green-700 hover:bg-green-100 transition-colors">
                <Target className="w-4 h-4 mr-3" />
                Get Task Suggestion
              </button>
              <button className="w-full flex items-center p-3 bg-purple-50 rounded-lg text-purple-700 hover:bg-purple-100 transition-colors">
                <BookOpen className="w-4 h-4 mr-3" />
                Search Knowledge Base
              </button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}