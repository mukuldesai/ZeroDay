import React from 'react'
import { motion } from 'framer-motion'
import { 
  Upload, CheckCircle, AlertCircle, Clock, RefreshCw, 
  Github, FileText, MessageSquare, Database 
} from 'lucide-react'

interface UploadStatusCardProps {
  uploadStatus: any
  error: any
  refreshStatus: () => void
}

export const UploadStatusCard: React.FC<UploadStatusCardProps> = ({
  uploadStatus,
  error,
  refreshStatus
}) => {
  const statusItems = [
    {
      key: 'github',
      label: 'GitHub Repository',
      icon: <Github className="w-4 h-4" />,
      description: 'Code structure and PRs',
      count: uploadStatus?.temp_data?.github || 0
    },
    {
      key: 'docs',
      label: 'Documentation',
      icon: <FileText className="w-4 h-4" />,
      description: 'README and guides',
      count: uploadStatus?.temp_data?.docs || 0
    },
    {
      key: 'slack',
      label: 'Team Conversations',
      icon: <MessageSquare className="w-4 h-4" />,
      description: 'Chat history and discussions',
      count: uploadStatus?.temp_data?.slack || 0
    },
    {
      key: 'processed',
      label: 'Vector Processing',
      icon: <Database className="w-4 h-4" />,
      description: 'AI embeddings created',
      status: uploadStatus?.ready_for_use || false
    }
  ]

  const getStatusIcon = (item: any) => {
    if (item.key === 'processed') {
      return item.status ? (
        <CheckCircle className="w-5 h-5 text-green-400" />
      ) : (
        <Clock className="w-5 h-5 text-yellow-400" />
      )
    }
    
    return item.count > 0 ? (
      <CheckCircle className="w-5 h-5 text-green-400" />
    ) : (
      <AlertCircle className="w-5 h-5 text-gray-400" />
    )
  }

  const getStatusText = (item: any) => {
    if (item.key === 'processed') {
      return item.status ? 'Completed' : 'Pending'
    }
    return item.count > 0 ? `${item.count} items` : 'Not uploaded'
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-white flex items-center">
          <Upload className="w-6 h-6 mr-2 text-blue-400" />
          Upload Status
        </h3>
        <button
          onClick={refreshStatus}
          className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span className="text-sm">Refresh</span>
        </button>
      </div>

      {error && (
        <div className="mb-6 bg-red-900/30 border border-red-500/30 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <AlertCircle className="w-4 h-4 text-red-400" />
            <span className="text-red-300 font-medium">Connection Error</span>
          </div>
          <p className="text-red-200 text-sm">
            Unable to fetch upload status. Make sure the backend is running.
          </p>
        </div>
      )}

      <div className="space-y-4">
        {statusItems.map((item, index) => (
          <motion.div
            key={item.key}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center space-x-4 p-4 bg-gray-700/30 rounded-lg"
          >
            <div className="p-2 bg-gray-600/50 rounded-lg text-gray-300">
              {item.icon}
            </div>
            <div className="flex-1">
              <div className="font-medium text-white">{item.label}</div>
              <div className="text-sm text-gray-400">{item.description}</div>
            </div>
            <div className="flex items-center space-x-2">
              {getStatusIcon(item)}
              <span className="text-sm text-gray-300">
                {getStatusText(item)}
              </span>
            </div>
          </motion.div>
        ))}
      </div>

      {uploadStatus?.ready_for_use && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mt-6 bg-green-900/30 border border-green-500/30 rounded-lg p-4"
        >
          <div className="flex items-center space-x-2 mb-2">
            <CheckCircle className="w-4 h-4 text-green-400" />
            <span className="text-green-300 font-medium">Processing Complete</span>
          </div>
          <p className="text-green-200 text-sm">
            {uploadStatus.documents_indexed} documents have been processed and are ready for AI queries.
          </p>
        </motion.div>
      )}

      {!uploadStatus?.ready_for_use && (uploadStatus?.temp_data?.github > 0 || uploadStatus?.temp_data?.docs > 0 || uploadStatus?.temp_data?.slack > 0) && (
        <div className="mt-6 bg-yellow-900/30 border border-yellow-500/30 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Clock className="w-4 h-4 text-yellow-400" />
            <span className="text-yellow-300 font-medium">Ready to Process</span>
          </div>
          <p className="text-yellow-200 text-sm">
            Data uploaded successfully. Build the knowledge base to enable AI features.
          </p>
        </div>
      )}
    </motion.div>
  )
}