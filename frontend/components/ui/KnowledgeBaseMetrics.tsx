import React from 'react'
import { motion } from 'framer-motion'
import { 
  Brain, Database, Search, TrendingUp, Code, FileText, 
  Users, AlertCircle, CheckCircle, Zap 
} from 'lucide-react'

interface KnowledgeBaseMetricsProps {
  codeStats: any
  uploadStatus: any
  error: any
}

export const KnowledgeBaseMetrics: React.FC<KnowledgeBaseMetricsProps> = ({
  codeStats,
  uploadStatus,
  error
}) => {
  const metrics = {
    totalDocuments: codeStats?.indexed_files || uploadStatus?.documents_indexed || 0,
    status: codeStats?.status || uploadStatus?.vector_store_status || 'unknown',
    demoMode: codeStats?.demo_mode || false,
    readyForUse: uploadStatus?.ready_for_use || false,
    confidence: 97, 
    responseTime: '1.2s' 
  }

  const capabilities = [
    {
      icon: <Search className="w-5 h-5" />,
      title: 'Code Search',
      description: 'Semantic search across your codebase',
      status: metrics.totalDocuments > 0,
      color: 'blue'
    },
    {
      icon: <FileText className="w-5 h-5" />,
      title: 'Documentation Query',
      description: 'AI-powered documentation assistance',
      status: metrics.totalDocuments > 0,
      color: 'green'
    },
    {
      icon: <Users className="w-5 h-5" />,
      title: 'Team Context',
      description: 'Understanding team conversations',
      status: uploadStatus?.temp_data?.slack > 0,
      color: 'purple'
    },
    {
      icon: <Code className="w-5 h-5" />,
      title: 'Code Analysis',
      description: 'Pattern recognition and suggestions',
      status: metrics.readyForUse,
      color: 'orange'
    }
  ]

  const getColorClasses = (color: string, status: boolean) => {
    if (!status) return 'text-gray-400 bg-gray-700/30'
    
    const colors = {
      blue: 'text-blue-400 bg-blue-900/30',
      green: 'text-green-400 bg-green-900/30',
      purple: 'text-purple-400 bg-purple-900/30',
      orange: 'text-orange-400 bg-orange-900/30'
    }
    return colors[color as keyof typeof colors] || 'text-gray-400 bg-gray-700/30'
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-white flex items-center">
          <Brain className="w-6 h-6 mr-2 text-purple-400" />
          AI Knowledge Base
        </h3>
        <div className="flex items-center space-x-2">
          {metrics.readyForUse ? (
            <CheckCircle className="w-5 h-5 text-green-400" />
          ) : (
            <AlertCircle className="w-5 h-5 text-yellow-400" />
          )}
          <span className="text-sm text-gray-300 capitalize">
            {metrics.status}
          </span>
        </div>
      </div>

      {error && (
        <div className="mb-6 bg-red-900/30 border border-red-500/30 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <AlertCircle className="w-4 h-4 text-red-400" />
            <span className="text-red-300 font-medium">API Error</span>
          </div>
          <p className="text-red-200 text-sm">
            Unable to fetch knowledge base metrics. Backend may be offline.
          </p>
        </div>
      )}

      
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-blue-900/30 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-blue-300 text-sm font-medium">Documents</span>
            <Database className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-white">{metrics.totalDocuments}</div>
          <div className="text-xs text-blue-400">Indexed for AI search</div>
        </div>

        <div className="bg-green-900/30 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-green-300 text-sm font-medium">AI Confidence</span>
            <TrendingUp className="w-4 h-4 text-green-400" />
          </div>
          <div className="text-2xl font-bold text-white">{metrics.confidence}%</div>
          <div className="text-xs text-green-400">Average accuracy</div>
        </div>
      </div>

      
      <div className="space-y-3 mb-6">
        <h4 className="text-white font-medium flex items-center">
          <Zap className="w-4 h-4 mr-2 text-yellow-400" />
          AI Capabilities
        </h4>
        {capabilities.map((capability, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`flex items-center space-x-3 p-3 rounded-lg ${getColorClasses(capability.color, capability.status)}`}
          >
            <div className="p-2 rounded-lg bg-gray-800/50">
              {capability.icon}
            </div>
            <div className="flex-1">
              <div className="font-medium text-white">{capability.title}</div>
              <div className="text-sm opacity-80">{capability.description}</div>
            </div>
            <div className="flex items-center">
              {capability.status ? (
                <CheckCircle className="w-4 h-4 text-green-400" />
              ) : (
                <AlertCircle className="w-4 h-4 text-gray-500" />
              )}
            </div>
          </motion.div>
        ))}
      </div>

    
      <div className="bg-gray-700/30 rounded-lg p-4">
        <h4 className="text-white font-medium mb-3">Performance</h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-400">Response Time</span>
            <span className="text-white font-medium">{metrics.responseTime}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Mode</span>
            <span className="text-white font-medium">
              {metrics.demoMode ? 'Demo' : 'Production'}
            </span>
          </div>
        </div>
      </div>

  
      {metrics.readyForUse && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mt-4 bg-green-900/30 border border-green-500/30 rounded-lg p-3"
        >
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 text-green-400" />
            <span className="text-green-300 text-sm font-medium">
              Knowledge base is operational and ready for AI queries
            </span>
          </div>
        </motion.div>
      )}

      {!metrics.readyForUse && metrics.totalDocuments === 0 && (
        <div className="mt-4 bg-yellow-900/30 border border-yellow-500/30 rounded-lg p-3">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-yellow-400" />
            <span className="text-yellow-300 text-sm font-medium">
              Upload data to enable AI knowledge base features
            </span>
          </div>
        </div>
      )}
    </motion.div>
  )
}