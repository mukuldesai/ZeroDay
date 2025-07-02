'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence, Variants, easeInOut } from 'framer-motion'
import { 
  Zap, 
  Brain, 
  Code, 
  BookOpen, 
  CheckSquare, 
  ArrowRight, 
  Users, 
  Clock, 
  TrendingUp, 
  Sparkles,
  Bot,
  GitBranch,
  FileText,
  MessageSquare,
  Shield,
  Rocket,
  Star,
  Play,
  ChevronDown,
  Github,
  Slack,
  Calendar,
  Target,
  Award,
  BarChart3
} from 'lucide-react'
import Link from 'next/link'


// Animation variants
const fadeInUp = {
  initial: { opacity: 0, y: 60 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6, ease: "easeOut" }
}

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
}

const floatingAnimation: Variants = {
  animate: (delay = 0) => ({
    y: [0, -10, 0],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: easeInOut,
      delay,
    },
  }),
};

// Components
const StatCard = ({ icon, value, label, color }: {
  icon: React.ReactNode
  value: string
  label: string
  color: string
}) => (
  <motion.div
    whileHover={{ scale: 1.05, y: -5 }}
    className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300"
  >
    <div className={`w-12 h-12 rounded-xl ${color} flex items-center justify-center mb-4`}>
      {icon}
    </div>
    <div className="text-3xl font-bold text-gray-900 mb-1">{value}</div>
    <div className="text-gray-600 text-sm">{label}</div>
  </motion.div>
)

const FeatureCard = ({ icon, title, description, color, bgColor }: {
  icon: React.ReactNode
  title: string
  description: string
  color: string
  bgColor: string
}) => (
  <motion.div
    whileHover={{ scale: 1.02, y: -5 }}
    className="group bg-white rounded-2xl p-8 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300"
  >
    <div className={`w-16 h-16 rounded-2xl ${bgColor} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
      <div className={color}>
        {icon}
      </div>
    </div>
    <h3 className="text-xl font-bold text-gray-900 mb-3">{title}</h3>
    <p className="text-gray-600 leading-relaxed">{description}</p>
  </motion.div>
)

const AgentCard = ({ agent, delay }: {
  agent: {
    name: string
    description: string
    icon: React.ReactNode
    color: string
    bgColor: string
    features: string[]
  }
  delay: number
}) => (
  <motion.div
    initial={{ opacity: 0, y: 30 }}
    whileInView={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.6 }}
    viewport={{ once: true }}
    whileHover={{ scale: 1.02 }}
    className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300"
  >
    <div className={`w-14 h-14 rounded-xl ${agent.bgColor} flex items-center justify-center mb-4`}>
      <div className={agent.color}>
        {agent.icon}
      </div>
    </div>
    <h3 className="text-xl font-bold text-gray-900 mb-2">{agent.name}</h3>
    <p className="text-gray-600 mb-4">{agent.description}</p>
    <ul className="space-y-2">
      {agent.features.map((feature, index) => (
        <li key={index} className="flex items-center text-sm text-gray-600">
          <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full mr-3"></div>
          {feature}
        </li>
      ))}
    </ul>
  </motion.div>
)

export default function IndexPage() {
  const [activeDemo, setActiveDemo] = useState(0)
  const [isVideoPlaying, setIsVideoPlaying] = useState(false)

  const stats = [
    { icon: <Clock className="w-6 h-6 text-white" />, value: "2 Days", label: "Average Onboarding Time", color: "bg-gradient-to-r from-blue-500 to-blue-600" },
    { icon: <TrendingUp className="w-6 h-6 text-white" />, value: "85%", label: "Faster Time to First PR", color: "bg-gradient-to-r from-green-500 to-green-600" },
    { icon: <Users className="w-6 h-6 text-white" />, value: "90%", label: "Developer Satisfaction", color: "bg-gradient-to-r from-purple-500 to-purple-600" },
    { icon: <Award className="w-6 h-6 text-white" />, value: "50%", label: "Reduced Mentor Overhead", color: "bg-gradient-to-r from-orange-500 to-orange-600" }
  ]

  const features = [
    {
      icon: <Brain className="w-8 h-8" />,
      title: "Multi-Agent AI System",
      description: "Four specialized AI agents working together to provide comprehensive onboarding support tailored to your needs.",
      color: "text-purple-600",
      bgColor: "bg-purple-50"
    },
    {
      icon: <Code className="w-8 h-8" />,
      title: "Intelligent Code Search",
      description: "Advanced code understanding that explains complex architectures, patterns, and helps you navigate large codebases instantly.",
      color: "text-blue-600",
      bgColor: "bg-blue-50"
    },
    {
      icon: <BookOpen className="w-8 h-8" />,
      title: "Personalized Learning Paths",
      description: "Dynamic learning plans that adapt to your experience level, role, and team requirements for optimal skill development.",
      color: "text-green-600",
      bgColor: "bg-green-50"
    },
    {
      icon: <Target className="w-8 h-8" />,
      title: "Smart Task Recommendations",
      description: "AI-powered task suggestions that match your skill level and help you make meaningful contributions from day one.",
      color: "text-orange-600",
      bgColor: "bg-orange-50"
    }
  ]

  const agents = [
    {
      name: "Knowledge Agent",
      description: "Your code exploration companion",
      icon: <Code className="w-6 h-6" />,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
      features: [
        "Explains complex code patterns",
        "Searches across entire codebase",
        "Provides context-aware documentation",
        "Identifies dependencies and relationships"
      ]
    },
    {
      name: "Mentor Agent",
      description: "Senior developer guidance on demand",
      icon: <Brain className="w-6 h-6" />,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
      features: [
        "Debugging assistance and troubleshooting",
        "Best practices and code review tips",
        "Architecture guidance and decisions",
        "Career development advice"
      ]
    },
    {
      name: "Guide Agent",
      description: "Personalized learning path creator",
      icon: <BookOpen className="w-6 h-6" />,
      color: "text-green-600",
      bgColor: "bg-green-50",
      features: [
        "Creates custom learning roadmaps",
        "Tracks progress and milestones",
        "Adapts to your learning pace",
        "Suggests relevant resources"
      ]
    },
    {
      name: "Task Agent",
      description: "Smart task recommendation engine",
      icon: <CheckSquare className="w-6 h-6" />,
      color: "text-orange-600",
      bgColor: "bg-orange-50",
      features: [
        "Matches tasks to skill level",
        "Prioritizes high-impact contributions",
        "Provides implementation guidance",
        "Tracks completion and feedback"
      ]
    }
  ]

  const demoSteps = [
    "Ask about authentication flow",
    "Get personalized learning plan", 
    "Receive task recommendations",
    "Debug with AI assistance"
  ]

  // Auto-rotate demo
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveDemo((prev) => (prev + 1) % demoSteps.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Navigation */}
      <motion.nav 
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.6 }}
        className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-2 rounded-xl">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">ZeroDay</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-600 hover:text-gray-900 transition-colors">Features</a>
              <a href="#agents" className="text-gray-600 hover:text-gray-900 transition-colors">AI Agents</a>
              <a href="#demo" className="text-gray-600 hover:text-gray-900 transition-colors">Demo</a>
              <Link href="/chat">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-indigo-600 text-white px-6 py-2 rounded-xl hover:bg-indigo-700 transition-colors"
                >
                  Try Now
                </motion.button>
              </Link>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <motion.div
            variants={staggerContainer}
            initial="initial"
            animate="animate"
            className="text-center"
          >
            {/* Badge */}
            <motion.div
              variants={fadeInUp}
              className="inline-flex items-center space-x-2 bg-indigo-50 border border-indigo-200 rounded-full px-4 py-2 mb-8"
            >
              <Sparkles className="w-4 h-4 text-indigo-600" />
              <span className="text-indigo-700 text-sm font-medium">AI-Powered Developer Onboarding</span>
            </motion.div>

            {/* Main Headline */}
            <motion.h1
              variants={fadeInUp}
              className="text-4xl sm:text-6xl lg:text-7xl font-bold text-gray-900 mb-6"
            >
              From{' '}
              <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                2 Weeks
              </span>
              {' '}to{' '}
              <span className="bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
                2 Days
              </span>
            </motion.h1>

            <motion.p
              variants={fadeInUp}
              className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed"
            >
              Revolutionary AI agents that understand your codebase, create personalized learning paths, 
              and accelerate developer onboarding like never before.
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              variants={fadeInUp}
              className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6 mb-16"
            >
              <Link href="/chat">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-8 py-4 rounded-2xl text-lg font-semibold hover:shadow-lg transition-all duration-300 flex items-center space-x-2"
                >
                  <Rocket className="w-5 h-5" />
                  <span>Start Onboarding</span>
                  <ArrowRight className="w-5 h-5" />
                </motion.button>
              </Link>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsVideoPlaying(true)}
                className="bg-white text-gray-900 px-8 py-4 rounded-2xl text-lg font-semibold border border-gray-200 hover:shadow-lg transition-all duration-300 flex items-center space-x-2"
              >
                <Play className="w-5 h-5" />
                <span>Watch Demo</span>
              </motion.button>
            </motion.div>

            {/* Stats */}
            <motion.div
              variants={staggerContainer}
              initial="initial"
              animate="animate"
              className="grid grid-cols-2 lg:grid-cols-4 gap-6 max-w-4xl mx-auto"
            >
              {stats.map((stat, index) => (
                <motion.div key={index} variants={fadeInUp}>
                  <StatCard {...stat} />
                </motion.div>
              ))}
            </motion.div>
          </motion.div>
        </div>

        {/* Floating Elements */}
        <motion.div
        variants={floatingAnimation}
        custom={0}
        animate="animate"
        className="absolute top-20 left-20 text-indigo-200 hidden lg:block"
        >
        <Code className="w-8 h-8" />
        </motion.div>

        <motion.div
        variants={floatingAnimation}
        custom={1}
        animate="animate"
        className="absolute top-40 right-20 text-purple-200 hidden lg:block"
        >
        <Brain className="w-10 h-10" />
        </motion.div>

        <motion.div
        variants={floatingAnimation}
        custom={2}
        animate="animate"
        className="absolute bottom-20 left-1/4 text-green-200 hidden lg:block"
        >
        <BookOpen className="w-6 h-6" />
        </motion.div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Intelligent Onboarding Features
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our AI agents work together to create the most comprehensive and efficient 
              developer onboarding experience ever built.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1, duration: 0.6 }}
                viewport={{ once: true }}
              >
                <FeatureCard {...feature} />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* AI Agents Section */}
      <section id="agents" className="py-20 bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Meet Your AI Onboarding Team
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Four specialized AI agents, each designed to excel in different aspects 
              of developer onboarding and support.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {agents.map((agent, index) => (
              <AgentCard key={index} agent={agent} delay={index * 0.1} />
            ))}
          </div>
        </div>
      </section>

      {/* Interactive Demo Section */}
      <section id="demo" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              See ZeroDay in Action
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Experience how our AI agents transform the onboarding process with 
              intelligent, contextual assistance.
            </p>
          </motion.div>

          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-3xl p-8 lg:p-12">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              {/* Demo Controls */}
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-6">Try These Examples:</h3>
                <div className="space-y-4">
                  {demoSteps.map((step, index) => (
                    <motion.button
                      key={index}
                      onClick={() => setActiveDemo(index)}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className={`w-full text-left p-4 rounded-xl transition-all duration-300 ${
                        activeDemo === index
                          ? 'bg-indigo-600 text-white shadow-lg'
                          : 'bg-white text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                          activeDemo === index
                            ? 'bg-white text-indigo-600'
                            : 'bg-indigo-100 text-indigo-600'
                        }`}>
                          {index + 1}
                        </div>
                        <span className="font-medium">{step}</span>
                      </div>
                    </motion.button>
                  ))}
                </div>
              </div>

              {/* Demo Visual */}
              <div className="bg-white rounded-2xl shadow-xl p-6">
                <div className="bg-gray-900 rounded-lg p-4 text-green-400 font-mono text-sm">
                  <div className="flex items-center space-x-2 mb-3">
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="text-gray-400 ml-4">ZeroDay Terminal</span>
                  </div>
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={activeDemo}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.5 }}
                    >
                      <div className="mb-2">$ {demoSteps[activeDemo]}</div>
                      <div className="text-blue-400">🤖 Analyzing codebase...</div>
                      <div className="text-yellow-400">✨ Generating response...</div>
                      <div className="text-green-400">✅ Response ready!</div>
                    </motion.div>
                  </AnimatePresence>
                </div>
                
                <div className="mt-6 text-center">
                  <Link href="/chat">
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition-all duration-300"
                    >
                      Try Live Demo
                    </motion.button>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-indigo-600 to-purple-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
              Ready to Transform Your Onboarding?
            </h2>
            <p className="text-xl text-indigo-100 mb-10 max-w-2xl mx-auto">
              Join the future of developer onboarding. Get new team members productive 
              in days, not weeks.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
              <Link href="/chat">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-white text-indigo-600 px-8 py-4 rounded-2xl text-lg font-semibold hover:shadow-lg transition-all duration-300 flex items-center space-x-2"
                >
                  <Rocket className="w-5 h-5" />
                  <span>Get Started Now</span>
                  <ArrowRight className="w-5 h-5" />
                </motion.button>
              </Link>
              <Link href="/dashboard">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="border-2 border-white text-white px-8 py-4 rounded-2xl text-lg font-semibold hover:bg-white hover:text-indigo-600 transition-all duration-300 flex items-center space-x-2"
                >
                  <BarChart3 className="w-5 h-5" />
                  <span>View Dashboard</span>
                </motion.button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center space-x-3 mb-4 md:mb-0">
              <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-2 rounded-xl">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold">ZeroDay</span>
            </div>
            <div className="text-gray-400 text-sm">
              © 2025 ZeroDay. Transforming developer onboarding with AI.
            </div>
          </div>
        </div>
      </footer>

      {/* Video Modal */}
      <AnimatePresence>
        {isVideoPlaying && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
            onClick={() => setIsVideoPlaying(false)}
          >
            <motion.div
              initial={{ scale: 0.5 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.5 }}
              className="bg-white rounded-2xl p-8 max-w-4xl w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="text-center">
                <h3 className="text-2xl font-bold text-gray-900 mb-4">ZeroDay Demo Video</h3>
                <div className="bg-gray-100 rounded-xl h-64 flex items-center justify-center mb-6">
                  <div className="text-gray-500">
                    <Play className="w-16 h-16 mx-auto mb-4" />
                    <p>Demo video will be embedded here</p>
                  </div>
                </div>
                <button
                  onClick={() => setIsVideoPlaying(false)}
                  className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}