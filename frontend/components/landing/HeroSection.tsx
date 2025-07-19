import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Brain, Database, Clock, Sparkles, Play, Github, Linkedin,
  ArrowRight, Code, Users, TrendingUp, Shield
} from 'lucide-react'
import { useLiveDemo } from '../../lib/hooks/useLiveDemo'

interface HeroSectionProps {
  systemStatus: {
    backendConnected: boolean
    documentsIndexed: number
    agentsAvailable: {
      knowledge: boolean
      guide: boolean
      mentor: boolean  
      task: boolean
    }
  }
  aiMetrics: {
    activeAgents: number
    averageResponseTime: string
    confidenceScore: number
  }
}

export const HeroSection: React.FC<HeroSectionProps> = ({ systemStatus, aiMetrics }) => {
  const { isDemoRunning, liveDemoResponse, runLiveDemo } = useLiveDemo()

  const professionalStats = [
    {
      icon: <TrendingUp className="w-5 h-5 text-blue-400" />,
      label: 'AI Agents Active',
      value: `${aiMetrics.activeAgents}/4`,
      color: 'bg-blue-900/30 border-blue-500/30',
      textColor: 'text-blue-300'
    },
    {
      icon: <Database className="w-5 h-5 text-green-400" />,
      label: 'Knowledge Base',
      value: `${systemStatus.documentsIndexed} Documents`,
      color: 'bg-green-900/30 border-green-500/30',
      textColor: 'text-green-300'
    },
    {
      icon: <Clock className="w-5 h-5 text-purple-400" />,
      label: 'Response Time',
      value: aiMetrics.averageResponseTime,
      color: 'bg-purple-900/30 border-purple-500/30',
      textColor: 'text-purple-300'
    },
    {
      icon: <Shield className="w-5 h-5 text-orange-400" />,
      label: 'Uptime',
      value: '99.9%',
      color: 'bg-orange-900/30 border-orange-500/30',
      textColor: 'text-orange-300'
    }
  ]

  return (
    <div className="relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900" />
      <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10" />
      
      <div className="relative max-w-7xl mx-auto px-4 py-20">
        <motion.div 
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center space-x-4 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full px-6 py-3 mb-8">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-green-300 text-sm font-medium">Live Portfolio Demo</span>
            </div>
            <div className="w-px h-4 bg-white/20" />
            <span className="text-white/80 text-sm">Enterprise AI Platform</span>
            <div className="w-px h-4 bg-white/20" />
            <span className="text-white/80 text-sm">Multi-Agent Architecture</span>
          </div>
          
          <div className="flex items-center justify-center space-x-4">
            <motion.a 
              href="https://github.com/mukuldesai/ZeroDay" 
              target="_blank" 
              rel="noopener noreferrer"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center space-x-2 bg-gray-800/80 backdrop-blur-sm text-white px-4 py-2 rounded-lg hover:bg-gray-700/80 transition-all border border-gray-600/50"
            >
              <Github className="w-4 h-4" />
              <span className="text-sm font-medium">View Source</span>
            </motion.a>
            <motion.a 
              href="https://linkedin.com/in/mukuldesai" 
              target="_blank" 
              rel="noopener noreferrer"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center space-x-2 bg-blue-600/90 backdrop-blur-sm text-white px-4 py-2 rounded-lg hover:bg-blue-700/90 transition-all border border-blue-500/50"
            >
              <Linkedin className="w-4 h-4" />
              <span className="text-sm font-medium">Connect</span>
            </motion.a>
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-center mb-16"
        >
          <div className="flex items-center justify-center mb-8">
            <motion.div 
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="relative"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur-xl opacity-30" />
              <div className="relative bg-gradient-to-r from-blue-600 to-purple-600 p-4 rounded-2xl mr-6">
                <Brain className="w-16 h-16 text-white" />
              </div>
            </motion.div>
            <div className="text-left">
              <h1 className="text-7xl font-bold bg-gradient-to-r from-white via-blue-100 to-purple-100 bg-clip-text text-transparent">
                ZeroDay
              </h1>
              <p className="text-xl text-blue-200 mt-2">Enterprise AI Platform</p>
            </div>
          </div>

          <div className="max-w-4xl mx-auto mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6 leading-tight">
              Revolutionize Developer Onboarding with 
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent"> AI Intelligence</span>
            </h2>
            <p className="text-xl text-gray-300 leading-relaxed">
              Transform your development team's productivity with specialized AI agents that understand your codebase, 
              generate personalized learning paths, and provide real-time guidance for faster, smarter onboarding.
            </p>
          </div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-12 max-w-4xl mx-auto"
          >
            {professionalStats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 * index }}
                className={`${stat.color} backdrop-blur-sm rounded-xl p-4 border`}
              >
                <div className="flex items-center space-x-3 mb-2">
                  {stat.icon}
                  <span className={`${stat.textColor} text-sm font-medium`}>{stat.label}</span>
                </div>
                <div className="text-2xl font-bold text-white">{stat.value}</div>
              </motion.div>
            ))}
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-white/5 backdrop-blur-sm rounded-3xl p-8 max-w-3xl mx-auto border border-white/10"
          >
            <div className="flex items-center justify-center mb-6">
              <Sparkles className="w-8 h-8 text-yellow-400 mr-3" />
              <h3 className="text-2xl font-bold text-white">Experience Live AI Intelligence</h3>
            </div>
            
            <p className="text-gray-300 mb-6 text-lg">
              See real AI agents analyze code, generate tasks, and provide mentorship in real-time
            </p>
            
            <motion.button
              onClick={runLiveDemo}
              disabled={isDemoRunning || !systemStatus.backendConnected}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="group relative bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-2xl font-semibold text-lg hover:shadow-2xl transition-all duration-300 flex items-center space-x-3 mx-auto disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur-xl opacity-30 group-hover:opacity-50 transition-opacity" />
              <div className="relative flex items-center space-x-3">
                {isDemoRunning ? (
                  <>
                    <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>AI Processing...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-6 h-6" />
                    <span>Launch Interactive Demo</span>
                    <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </div>
            </motion.button>

            <AnimatePresence>
              {liveDemoResponse && (
                <motion.div
                  initial={{ opacity: 0, y: 20, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -20, scale: 0.95 }}
                  className="mt-8 bg-gradient-to-r from-blue-900/50 to-purple-900/50 backdrop-blur-sm border border-blue-500/30 rounded-2xl p-6"
                >
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="flex items-center space-x-2">
                      <Brain className="w-5 h-5 text-blue-400" />
                      <span className="text-blue-300 font-medium">AI Agent Response</span>
                    </div>
                    <div className="bg-green-500/20 border border-green-500/30 text-green-300 px-3 py-1 rounded-full text-xs font-bold">
                      {aiMetrics.confidenceScore}% confident
                    </div>
                    <div className="bg-purple-500/20 border border-purple-500/30 text-purple-300 px-3 py-1 rounded-full text-xs font-bold">
                      Generated in {aiMetrics.averageResponseTime}
                    </div>
                  </div>
                  <p className="text-white text-lg leading-relaxed">{liveDemoResponse}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="mt-12"
          >
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="bg-white text-gray-900 px-8 py-3 rounded-xl font-semibold hover:bg-gray-100 transition-colors flex items-center space-x-2"
              >
                <Code className="w-5 h-5" />
                <span>Explore Platform</span>
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="border border-white/30 text-white px-8 py-3 rounded-xl font-semibold hover:bg-white/10 transition-colors flex items-center space-x-2"
              >
                <Users className="w-5 h-5" />
                <span>See Architecture</span>
              </motion.button>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}