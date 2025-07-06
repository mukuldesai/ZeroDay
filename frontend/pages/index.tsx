import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Zap } from 'lucide-react'
import Link from 'next/link'

// Data
import { stats, features, agents, demoSteps } from '../lib/data/landingData'

// Components
import { HeroSection } from '../components/ui/HeroSection'
import { StatCardHero } from '../components/ui/StatCardHero'
import { FeatureCard } from '../components/ui/FeatureCard'
import { AgentCardLanding } from '../components/ui/AgentCardLanding'
import { InteractiveDemo } from '../components/ui/InteractiveDemo'
import { VideoModal } from '../components/ui/VideoModal'
import { FloatingElements } from '../components/ui/FloatingElements'
import { SectionHeader } from '../components/ui/SectionHeader'
import { CTASection } from '../components/ui/CTASection'
import { MotionButton } from '../components/ui/MotionButton'
import { staggerContainer } from '../lib/animations/variants'

export default function IndexPage() {
  const [isVideoPlaying, setIsVideoPlaying] = useState(false)

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
                <MotionButton className="bg-indigo-600 text-white px-6 py-2 rounded-xl hover:bg-indigo-700 transition-colors">
                  Try Now
                </MotionButton>
              </Link>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Hero Section */}
      <HeroSection onPlayVideo={() => setIsVideoPlaying(true)} />

      {/* Stats Section */}
      <motion.div
        variants={staggerContainer}
        initial="initial"
        animate="animate"
        className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pb-16"
      >
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <StatCardHero key={index} {...stat} delay={index * 0.1} />
          ))}
        </div>
      </motion.div>

      {/* Floating Elements */}
      <FloatingElements />

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <SectionHeader
            title="Intelligent Onboarding Features"
            subtitle="Our AI agents work together to create the most comprehensive and efficient developer onboarding experience ever built."
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <FeatureCard key={index} {...feature} delay={index * 0.1} />
            ))}
          </div>
        </div>
      </section>

      {/* AI Agents Section */}
      <section id="agents" className="py-20 bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <SectionHeader
            title="Meet Your AI Onboarding Team"
            subtitle="Four specialized AI agents, each designed to excel in different aspects of developer onboarding and support."
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {agents.map((agent, index) => (
              <AgentCardLanding key={index} agent={agent} delay={index * 0.1} />
            ))}
          </div>
        </div>
      </section>

      {/* Interactive Demo Section */}
      <InteractiveDemo demoSteps={demoSteps} />

      {/* CTA Section */}
      <CTASection />

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
      <VideoModal 
        isOpen={isVideoPlaying} 
        onClose={() => setIsVideoPlaying(false)} 
      />
    </div>
  )
}