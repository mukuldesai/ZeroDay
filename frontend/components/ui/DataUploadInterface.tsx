import React, { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { 
  Upload, GitBranch, FileText, MessageSquare, Database, 
  CheckCircle, AlertCircle, ToggleLeft, ToggleRight, 
  Brain, Zap, Sparkles, Clock
} from 'lucide-react'

interface UploadStatus {
  type: 'idle' | 'uploading' | 'success' | 'error'
  message?: string
}

export default function DataUploadInterface() {
  const [isDemo, setIsDemo] = useState(true)
  const [uploadStatus, setUploadStatus] = useState<Record<string, UploadStatus>>({
    github: { type: 'idle' },
    docs: { type: 'idle' },
    slack: { type: 'idle' },
    processing: { type: 'idle' }
  })

  const [repoUrl, setRepoUrl] = useState('')
  const [processing, setProcessing] = useState(false)
  
  const docsFileRef = useRef<HTMLInputElement>(null)
  const slackFileRef = useRef<HTMLInputElement>(null)

  const handleDemoToggle = () => {
    setIsDemo(!isDemo)
    if (!isDemo) {
      
      setUploadStatus({
        github: { type: 'success', message: 'Demo GitHub data loaded: 45 files, 12 PRs' },
        docs: { type: 'success', message: 'Demo documentation loaded: README.md, API_DOCS.md' },
        slack: { type: 'success', message: 'Demo Slack data loaded: 250+ conversations' },
        processing: { type: 'idle' }
      })
    } else {
      
      setUploadStatus({
        github: { type: 'idle' },
        docs: { type: 'idle' },
        slack: { type: 'idle' },
        processing: { type: 'idle' }
      })
    }
  }

  const handleGitHubUpload = async () => {
    if (!repoUrl.trim() && !isDemo) return

    setUploadStatus(prev => ({ ...prev, github: { type: 'uploading' } }))

    try {
      if (isDemo) {
        
        setTimeout(() => {
          setUploadStatus(prev => ({ 
            ...prev, 
            github: { type: 'success', message: 'Demo GitHub data processed: React codebase, 45 files analyzed' }
          }))
        }, 2000)
        return
      }

      const response = await fetch('http://localhost:8000/api/upload/github', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          repo_url: repoUrl,
          demo_mode: false,
          user_id: 'current_user'
        })
      })

      if (response.ok) {
        const data = await response.json()
        setUploadStatus(prev => ({ 
          ...prev, 
          github: { type: 'success', message: `GitHub data processed: ${data.files_processed || 'Repository'} analyzed` }
        }))
      } else {
        throw new Error('GitHub upload failed')
      }
    } catch (error) {
      setUploadStatus(prev => ({ 
        ...prev, 
        github: { type: 'error', message: 'Failed to process GitHub data. Check repository URL.' }
      }))
    }
  }

  const handleFileUpload = async (type: string, files: FileList | null) => {
    
    if (isDemo && !files) {
      setUploadStatus(prev => ({ ...prev, [type]: { type: 'uploading' } }))
      
      setTimeout(() => {
        const messages = {
          docs: 'Demo documentation processed: README.md, ARCHITECTURE.md, API_GUIDE.md',
          slack: 'Demo Slack data processed: 250+ conversations, 15 channels, 6 months history'
        }
        setUploadStatus(prev => ({ 
          ...prev, 
          [type]: { type: 'success', message: messages[type as keyof typeof messages] }
        }))
      }, 1500)
      return
    }

    if (!files || files.length === 0) return

    setUploadStatus(prev => ({ ...prev, [type]: { type: 'uploading' } }))

    try {
      const formData = new FormData()
      Array.from(files).forEach(file => formData.append('files', file))
      formData.append('type', type)
      formData.append('demo_mode', isDemo.toString())
      formData.append('user_id', 'current_user')

      const response = await fetch('http://localhost:8000/api/upload/files', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        setUploadStatus(prev => ({ 
          ...prev, 
          [type]: { type: 'success', message: `${files.length} files uploaded and processed successfully` }
        }))
      } else {
        throw new Error('File upload failed')
      }
    } catch (error) {
      setUploadStatus(prev => ({ 
        ...prev, 
        [type]: { type: 'error', message: 'Failed to process files. Check file format and backend connection.' }
      }))
    }
  }

  const handleProcessData = async () => {
    setProcessing(true)
    setUploadStatus(prev => ({ ...prev, processing: { type: 'uploading', message: 'Building AI knowledge base...' } }))
    
    try {
      const response = await fetch('http://localhost:8000/api/upload/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          action: 'build_index',
          demo_mode: isDemo,
          user_id: 'current_user'
        })
      })

      if (response.ok) {
        const result = await response.json()
        setUploadStatus(prev => ({ 
          ...prev, 
          processing: { 
            type: 'success', 
            message: isDemo 
              ? ' Demo knowledge base ready! 105 documents processed, 4 AI agents activated.'
              : ' Knowledge base built successfully! AI agents are now ready to assist.'
          }
        }))
      } else {
        throw new Error('Processing failed')
      }
    } catch (error) {
      setUploadStatus(prev => ({ 
        ...prev, 
        processing: { type: 'error', message: 'Processing failed. Check backend connection and try again.' }
      }))
    } finally {
      setProcessing(false)
    }
  }

  const getStatusIcon = (status: UploadStatus) => {
    switch (status.type) {
      case 'uploading':
        return <div className="animate-spin w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full" />
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />
      default:
        return null
    }
  }

  const canProcess = () => {
    return uploadStatus.github.type === 'success' || 
           uploadStatus.docs.type === 'success' || 
           uploadStatus.slack.type === 'success'
  }

  const dataTypes = [
    {
      id: 'github',
      title: 'GitHub Repository',
      description: 'Import code structure, PRs, and development history',
      icon: <GitBranch className="w-6 h-6" />,
      color: 'from-blue-500 to-blue-600'
    },
    {
      id: 'docs',
      title: 'Documentation',
      description: 'Upload README, guides, and technical documentation',
      icon: <FileText className="w-6 h-6" />,
      color: 'from-green-500 to-green-600'
    },
    {
      id: 'slack',
      title: 'Team Conversations',
      description: 'Import Slack exports for team context understanding',
      icon: <MessageSquare className="w-6 h-6" />,
      color: 'from-purple-500 to-purple-600'
    }
  ]

  return (
    <div className="space-y-8">
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center justify-center">
            <Brain className="w-7 h-7 mr-3 text-blue-400" />
            AI Data Processing Center
          </h2>
          <p className="text-gray-300 mb-6">
            Upload your team's data to create a personalized AI-powered onboarding experience
          </p>
          
          <div className="flex items-center justify-center space-x-3">
            <span className={`text-sm ${!isDemo ? 'text-white font-medium' : 'text-gray-400'}`}>Real Data</span>
            <button onClick={handleDemoToggle} className="focus:outline-none">
              {isDemo ? (
                <ToggleRight className="w-8 h-8 text-blue-500" />
              ) : (
                <ToggleLeft className="w-8 h-8 text-gray-400" />
              )}
            </button>
            <span className={`text-sm ${isDemo ? 'text-blue-400 font-medium' : 'text-gray-400'}`}>Demo Mode</span>
          </div>
          
          {isDemo && (
            <div className="bg-blue-900/30 border border-blue-500/30 rounded-lg p-4 mt-4">
              <div className="flex items-center justify-center space-x-2 mb-2">
                <Sparkles className="w-4 h-4 text-blue-400" />
                <span className="text-blue-300 font-medium">Demo Mode Active</span>
              </div>
              <p className="text-blue-200 text-sm">
                Experience ZeroDay with synthetic data showcasing enterprise-grade AI onboarding capabilities.
              </p>
            </div>
          )}
        </div>
      </motion.div>

      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {dataTypes.map((dataType, index) => (
          <motion.div
            key={dataType.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className={`p-3 bg-gradient-to-r ${dataType.color} rounded-lg text-white`}>
                  {dataType.icon}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">{dataType.title}</h3>
                  <p className="text-sm text-gray-400">{dataType.description}</p>
                </div>
              </div>
              {getStatusIcon(uploadStatus[dataType.id])}
            </div>
            
            {dataType.id === 'github' && (
              <div className="space-y-4">
                <input
                  type="text"
                  value={isDemo ? "github.com/zeroday/demo-project" : repoUrl}
                  onChange={(e) => !isDemo && setRepoUrl(e.target.value)}
                  placeholder={isDemo ? "Demo repository loaded" : "https://github.com/yourusername/repository"}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isDemo}
                />
                <button
                  onClick={handleGitHubUpload}
                  disabled={uploadStatus.github.type === 'uploading'}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  {uploadStatus.github.type === 'uploading' ? 'Processing...' : 'Import Repository'}
                </button>
              </div>
            )}

            {dataType.id === 'docs' && (
              <div className="space-y-3">
                {isDemo ? (
                  <div className="bg-blue-900/30 border border-blue-500/30 rounded-lg p-4">
                    <p className="text-blue-300 text-sm">
                      Demo files: README.md, API_DOCS.md, ARCHITECTURE.md, GETTING_STARTED.md
                    </p>
                  </div>
                ) : (
                  <input
                    ref={docsFileRef}
                    type="file"
                    multiple
                    accept=".md,.txt,.pdf,.doc,.docx"
                    onChange={(e) => handleFileUpload('docs', e.target.files)}
                    className="hidden"
                  />
                )}
                <button
                  onClick={() => isDemo ? handleFileUpload('docs', null) : docsFileRef.current?.click()}
                  disabled={uploadStatus.docs.type === 'uploading'}
                  className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
                >
                  {uploadStatus.docs.type === 'uploading' 
                    ? 'Processing...' 
                    : isDemo 
                      ? 'Load Demo Documentation' 
                      : 'Upload Documentation'
                  }
                </button>
              </div>
            )}

            {dataType.id === 'slack' && (
              <div className="space-y-3">
                {isDemo ? (
                  <div className="bg-purple-900/30 border border-purple-500/30 rounded-lg p-4">
                    <p className="text-purple-300 text-sm">
                      Demo data: 250+ conversations, 15 channels, 25 team members, 6 months of history
                    </p>
                  </div>
                ) : (
                  <input
                    ref={slackFileRef}
                    type="file"
                    accept=".zip,.json"
                    onChange={(e) => handleFileUpload('slack', e.target.files)}
                    className="hidden"
                  />
                )}
                <button
                  onClick={() => isDemo ? handleFileUpload('slack', null) : slackFileRef.current?.click()}
                  disabled={uploadStatus.slack.type === 'uploading'}
                  className="w-full bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
                >
                  {uploadStatus.slack.type === 'uploading' 
                    ? 'Processing...' 
                    : isDemo 
                      ? 'Load Demo Slack Data' 
                      : 'Upload Slack Export'
                  }
                </button>
              </div>
            )}

            {uploadStatus[dataType.id].message && (
              <div className={`mt-4 p-3 rounded-lg text-sm ${
                uploadStatus[dataType.id].type === 'error' 
                  ? 'bg-red-900/30 border border-red-500/30 text-red-200' 
                  : uploadStatus[dataType.id].type === 'success'
                    ? 'bg-green-900/30 border border-green-500/30 text-green-200'
                    : 'bg-blue-900/30 border border-blue-500/30 text-blue-200'
              }`}>
                {uploadStatus[dataType.id].message}
              </div>
            )}
          </motion.div>
        ))}
      </div>

      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-8 border border-gray-700/50"
      >
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-3 bg-gradient-to-r from-orange-500 to-red-500 rounded-lg text-white">
            <Database className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-white">Build AI Knowledge Base</h3>
            <p className="text-gray-400">Process uploaded data and create AI embeddings for intelligent queries</p>
          </div>
        </div>

        <div className="bg-gray-700/30 rounded-lg p-6 mb-6">
          <h4 className="font-medium text-white mb-4 flex items-center">
            <Zap className="w-4 h-4 mr-2 text-yellow-400" />
            Processing Pipeline
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
            {[
              { label: 'GitHub Data', status: uploadStatus.github.type === 'success' },
              { label: 'Documentation', status: uploadStatus.docs.type === 'success' },
              { label: 'Team Conversations', status: uploadStatus.slack.type === 'success' },
              { label: 'AI Processing', status: uploadStatus.processing.type === 'success' }
            ].map((step, index) => (
              <div key={index} className="flex items-center space-x-2">
                <div className={`w-4 h-4 rounded-full flex items-center justify-center ${
                  step.status ? 'bg-green-500' : 'bg-gray-600'
                }`}>
                  {step.status && <CheckCircle className="w-3 h-3 text-white" />}
                </div>
                <span className={step.status ? 'text-green-300' : 'text-gray-400'}>
                  {step.label}
                </span>
              </div>
            ))}
          </div>
        </div>
        
        <button
          onClick={handleProcessData}
          disabled={processing || !canProcess()}
          className="w-full bg-gradient-to-r from-orange-600 to-red-600 text-white py-4 px-6 rounded-lg hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-3 transition-all duration-300"
        >
          {processing ? (
            <>
              <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
              <span>Building AI Knowledge Base...</span>
              <Clock className="w-5 h-5" />
            </>
          ) : (
            <>
              <Database className="w-5 h-5" />
              <span>{canProcess() ? 'Build AI Knowledge Base' : 'Upload Data First'}</span>
              <Zap className="w-5 h-5" />
            </>
          )}
        </button>
        
        {uploadStatus.processing.message && (
          <div className={`mt-4 p-4 rounded-lg ${
            uploadStatus.processing.type === 'error' 
              ? 'bg-red-900/30 border border-red-500/30 text-red-200' 
              : uploadStatus.processing.type === 'success'
                ? 'bg-green-900/30 border border-green-500/30 text-green-200'
                : 'bg-blue-900/30 border border-blue-500/30 text-blue-200'
          }`}>
            {uploadStatus.processing.message}
          </div>
        )}
        
        {!canProcess() && (
          <p className="text-sm text-gray-400 text-center mt-4">
            Upload at least one data source above to enable AI knowledge base building
          </p>
        )}
      </motion.div>
    </div>
  )
}