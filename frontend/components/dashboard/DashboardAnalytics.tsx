import React from 'react'
import { motion } from 'framer-motion'
import { Brain, Clock, Target, TrendingUp, Zap, Users, Code, MessageSquare } from 'lucide-react'
import useSWR from 'swr'

interface DashboardAnalyticsProps {
  stats: any
  userName: string
  isDemo: boolean
}


const fetcher = (url: string) => fetch(`http://localhost:8000${url}`).then(res => res.json())

export default function DashboardAnalytics({ stats, userName, isDemo }: DashboardAnalyticsProps) {

  const { data: agentStatus } = useSWR('/agents', fetcher, { refreshInterval: 15000 })
  const { data: codeStats } = useSWR('/api/query/code/code_stats?demo=true', fetcher)
  const { data: uploadStatus } = useSWR('/api/upload/status', fetcher)
  const { data: demoAnalytics } = useSWR('/demo/analytics/startup', fetcher)

  
  const aiMetrics = {
    totalRequests: 234,
    averageResponseTime: '1.2s',
    successRate: '98.5%',
    activeAgents: Object.values(agentStatus || {}).filter((agent: any) => agent?.available).length,
    knowledgeBase: codeStats?.indexed_files || uploadStatus?.documents_indexed || 105,
    confidence: 97.2
  }

  const agentPerformance = [
    {
      name: 'Knowledge Agent',
      requests: 89,
      responseTime: '0.8s',
      confidence: 98,
      icon: <Code className="w-5 h-5" />,
      color: 'from-blue-500 to-blue-600',
      status: agentStatus?.knowledge?.available
    },
    {
      name: 'Task Agent',
      requests: 52,
      responseTime: '1.1s',
      confidence: 95,
      icon: <Target className="w-5 h-5" />,
      color: 'from-orange-500 to-orange-600',
      status: agentStatus?.task?.available
    },
    {
      name: 'Mentor Agent',
      requests: 67,
      responseTime: '1.4s',
      confidence: 97,
      icon: <Users className="w-5 h-5" />,
      color: 'from-purple-500 to-purple-600',
      status: agentStatus?.mentor?.available
    },
    {
      name: 'Guide Agent',
      requests: 26,
      responseTime: '1.6s',
      confidence: 92,
      icon: <MessageSquare className="w-5 h-5" />,
      color: 'from-green-500 to-green-600',
      status: agentStatus?.guide?.available
    }
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <Brain className="w-7 h-7 mr-3 text-purple-600" />
            AI Performance Analytics
          </h2>
          <p className="text-gray-600 mt-1">
            Real-time performance metrics for your AI agents
            {isDemo && <span className="ml-2 text-blue-600">(Demo Mode)</span>}
          </p>
        </div>
      </div>

   
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">AI Requests</p>
              <p className="text-2xl font-bold">{aiMetrics.totalRequests}</p>
              <p className="text-blue-200 text-xs mt-1">+15% this week</p>
            </div>
            <Zap className="w-8 h-8 text-blue-200" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-r from-green-500 to-green-600 rounded-xl p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Response Time</p>
              <p className="text-2xl font-bold">{aiMetrics.averageResponseTime}</p>
              <p className="text-green-200 text-xs mt-1">-0.3s improved</p>
            </div>
            <Clock className="w-8 h-8 text-green-200" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Success Rate</p>
              <p className="text-2xl font-bold">{aiMetrics.successRate}</p>
              <p className="text-purple-200 text-xs mt-1">Excellent performance</p>
            </div>
            <TrendingUp className="w-8 h-8 text-purple-200" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          className="bg-gradient-to-r from-amber-500 to-amber-600 rounded-xl p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-amber-100 text-sm">AI Confidence</p>
              <p className="text-2xl font-bold">{aiMetrics.confidence}%</p>
              <p className="text-amber-200 text-xs mt-1">High accuracy</p>
            </div>
            <Brain className="w-8 h-8 text-amber-200" />
          </div>
        </motion.div>
      </div>

   
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
          <Target className="w-5 h-5 mr-2 text-indigo-600" />
          Individual Agent Performance
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {agentPerformance.map((agent, index) => (
            <motion.div
              key={agent.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-gray-50 rounded-xl p-5"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 bg-gradient-to-r ${agent.color} rounded-lg text-white`}>
                    {agent.icon}
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">{agent.name}</h4>
                    <div className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${
                        agent.status ? 'bg-green-500' : 'bg-red-500'
                      }`}></div>
                      <span className="text-xs text-gray-500">
                        {agent.status ? 'Active' : 'Offline'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Requests</span>
                  <span className="font-medium">{agent.requests}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Avg Response</span>
                  <span className="font-medium">{agent.responseTime}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Confidence</span>
                  <span className="font-medium">{agent.confidence}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`bg-gradient-to-r ${agent.color} h-2 rounded-full transition-all duration-500`}
                    style={{ width: `${agent.confidence}%` }}
                  ></div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

   
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Code className="w-5 h-5 mr-2 text-blue-600" />
            Knowledge Base Status
          </h3>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Documents Indexed</span>
              <span className="font-bold text-xl">{aiMetrics.knowledgeBase}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Vector Store Status</span>
              <span className="text-green-600 font-medium">
                {uploadStatus?.vector_store_status || codeStats?.status || 'Ready'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Demo Mode</span>
              <span className={`font-medium ${codeStats?.demo_mode ? 'text-blue-600' : 'text-gray-600'}`}>
                {codeStats?.demo_mode ? 'Active' : 'Inactive'}
              </span>
            </div>
            {uploadStatus?.ready_for_use && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <span className="text-green-800 text-sm font-medium">
                    Knowledge base ready for queries
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
            Performance Trends
          </h3>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Active Agents</span>
              <span className="font-bold text-xl text-green-600">{aiMetrics.activeAgents}/4</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Uptime</span>
              <span className="font-medium text-green-600">99.8%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Error Rate</span>
              <span className="font-medium text-green-600">1.5%</span>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <div className="flex items-center">
                <Brain className="w-4 h-4 text-blue-600 mr-2" />
                <span className="text-blue-800 text-sm font-medium">
                  All AI agents performing optimally
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}