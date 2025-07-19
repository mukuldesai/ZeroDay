import React from 'react'
import { motion } from 'framer-motion'
import { 
  BookOpen, Target, Users, MessageSquare, 
  Zap, TrendingUp, Clock, CheckCircle 
} from 'lucide-react'

interface AIAgentShowcaseProps {
  agentsAvailable: {
    knowledge: boolean
    guide: boolean
    mentor: boolean
    task: boolean
  }
}

export const AIAgentShowcase: React.FC<AIAgentShowcaseProps> = ({ agentsAvailable }) => {
  const aiAgents = [
    {
      id: 'knowledge',
      name: 'Knowledge Agent',
      title: 'Code Intelligence',
      description: 'Advanced code search, documentation analysis, and semantic understanding',
      longDescription: 'Instantly search through codebases, understand complex architectures, and provide contextual documentation. Powered by vector embeddings and semantic analysis.',
      icon: <BookOpen className="w-8 h-8" />,
      color: 'from-blue-500 to-blue-600',
      glowColor: 'shadow-blue-500/25',
      available: agentsAvailable.knowledge,
      stats: {
        requests: 2847,
        confidence: 98,
        responseTime: '0.8s',
        accuracy: '97%'
      },
      capabilities: [
        'Semantic code search',
        'Architecture analysis', 
        'Documentation generation',
        'Code explanation'
      ]
    },
    {
      id: 'task',
      name: 'Task Agent',
      title: 'Smart Planning',
      description: 'Personalized task generation and intelligent workflow optimization',
      longDescription: 'Creates tailored learning tasks, tracks progress, and adapts recommendations based on skill level and team needs.',
      icon: <Target className="w-8 h-8" />,
      color: 'from-orange-500 to-orange-600',
      glowColor: 'shadow-orange-500/25',
      available: agentsAvailable.task,
      stats: {
        requests: 1653,
        confidence: 95,
        responseTime: '1.1s',
        accuracy: '94%'
      },
      capabilities: [
        'Personalized tasks',
        'Progress tracking',
        'Skill assessment',
        'Workflow optimization'
      ]
    },
    {
      id: 'mentor',
      name: 'Mentor Agent',
      title: 'Expert Guidance',
      description: 'Senior developer insights and real-time troubleshooting assistance',
      longDescription: 'Provides expert-level guidance, debugging help, and best practices. Like having a senior developer available 24/7.',
      icon: <Users className="w-8 h-8" />,
      color: 'from-purple-500 to-purple-600',
      glowColor: 'shadow-purple-500/25',
      available: agentsAvailable.mentor,
      stats: {
        requests: 3241,
        confidence: 97,
        responseTime: '1.3s',
        accuracy: '96%'
      },
      capabilities: [
        'Expert troubleshooting',
        'Code reviews',
        'Best practices',
        'Architecture guidance'
      ]
    },
    {
      id: 'guide',
      name: 'Guide Agent',
      title: 'Learning Paths',
      description: 'Adaptive learning path creation and educational content curation',
      longDescription: 'Designs comprehensive learning journeys, curates educational content, and adapts paths based on progress and goals.',
      icon: <MessageSquare className="w-8 h-8" />,
      color: 'from-green-500 to-green-600',
      glowColor: 'shadow-green-500/25',
      available: agentsAvailable.guide,
      stats: {
        requests: 892,
        confidence: 92,
        responseTime: '1.5s',
        accuracy: '93%'
      },
      capabilities: [
        'Learning path design',
        'Content curation',
        'Progress adaptation',
        'Skill gap analysis'
      ]
    }
  ]

  return (
    <div className="py-20 bg-gradient-to-b from-transparent to-gray-900/50">
      <div className="max-w-7xl mx-auto px-4">
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Meet Your 
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent"> AI Team</span>
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Four specialized AI agents working together to accelerate your development workflow 
            and provide intelligent, context-aware assistance.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
          {aiAgents.map((agent, index) => (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 * index }}
              whileHover={{ y: -8, scale: 1.02 }}
              className={`relative group bg-white/5 backdrop-blur-sm rounded-3xl p-8 border border-white/10 hover:border-white/20 transition-all duration-500 ${agent.glowColor} hover:shadow-2xl`}
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${agent.color} opacity-0 group-hover:opacity-10 rounded-3xl transition-opacity duration-500`} />
              
              <div className="absolute top-6 right-6">
                <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${
                  agent.available 
                    ? 'bg-green-500/20 border border-green-500/30' 
                    : 'bg-red-500/20 border border-red-500/30'
                }`}>
                  <div className={`w-2 h-2 rounded-full ${
                    agent.available ? 'bg-green-400 animate-pulse' : 'bg-red-400'
                  }`} />
                  <span className={`text-xs font-medium ${
                    agent.available ? 'text-green-300' : 'text-red-300'
                  }`}>
                    {agent.available ? 'ACTIVE' : 'OFFLINE'}
                  </span>
                </div>
              </div>

              <div className="relative z-10">
                <div className={`inline-flex p-4 rounded-2xl bg-gradient-to-br ${agent.color} mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  {agent.icon}
                </div>
                
                <h3 className="text-2xl font-bold text-white mb-2">{agent.name}</h3>
                <p className="text-lg text-blue-300 font-medium mb-4">{agent.title}</p>
                <p className="text-gray-300 mb-6 leading-relaxed">{agent.longDescription}</p>

                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-white/5 rounded-xl p-3 border border-white/10">
                    <div className="flex items-center space-x-2 mb-1">
                      <TrendingUp className="w-4 h-4 text-green-400" />
                      <span className="text-xs text-gray-400 font-medium">REQUESTS</span>
                    </div>
                    <div className="text-xl font-bold text-white">{agent.stats.requests.toLocaleString()}</div>
                  </div>
                  <div className="bg-white/5 rounded-xl p-3 border border-white/10">
                    <div className="flex items-center space-x-2 mb-1">
                      <CheckCircle className="w-4 h-4 text-blue-400" />
                      <span className="text-xs text-gray-400 font-medium">CONFIDENCE</span>
                    </div>
                    <div className="text-xl font-bold text-white">{agent.stats.confidence}%</div>
                  </div>
                  <div className="bg-white/5 rounded-xl p-3 border border-white/10">
                    <div className="flex items-center space-x-2 mb-1">
                      <Clock className="w-4 h-4 text-purple-400" />
                      <span className="text-xs text-gray-400 font-medium">RESPONSE</span>
                    </div>
                    <div className="text-xl font-bold text-white">{agent.stats.responseTime}</div>
                  </div>
                  <div className="bg-white/5 rounded-xl p-3 border border-white/10">
                    <div className="flex items-center space-x-2 mb-1">
                      <Zap className="w-4 h-4 text-orange-400" />
                      <span className="text-xs text-gray-400 font-medium">ACCURACY</span>
                    </div>
                    <div className="text-xl font-bold text-white">{agent.stats.accuracy}</div>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">Key Capabilities</h4>
                  <div className="space-y-2">
                    {agent.capabilities.map((capability, idx) => (
                      <div key={idx} className="flex items-center space-x-2">
                        <div className="w-1.5 h-1.5 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full" />
                        <span className="text-sm text-gray-300">{capability}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10"
        >
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold text-white mb-2">
                {Object.values(agentsAvailable).filter(Boolean).length}/4
              </div>
              <div className="text-gray-400 text-sm font-medium">Agents Active</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white mb-2">8,633</div>
              <div className="text-gray-400 text-sm font-medium">Total Requests</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white mb-2">96%</div>
              <div className="text-gray-400 text-sm font-medium">Avg Confidence</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white mb-2">1.1s</div>
              <div className="text-gray-400 text-sm font-medium">Avg Response</div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}