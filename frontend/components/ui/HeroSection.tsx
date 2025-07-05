import React from 'react'
import { motion } from 'framer-motion'
import { Sparkles, Rocket, Play, ArrowRight } from 'lucide-react'
import Link from 'next/link'
import { MotionButton } from './MotionButton'
import { fadeInUp, staggerContainer } from '../../lib/animations/variants'

interface HeroSectionProps {
  onPlayVideo: () => void
}

export const HeroSection: React.FC<HeroSectionProps> = ({ onPlayVideo }) => {
  return (
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
              <MotionButton
                className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-8 py-4 rounded-2xl text-lg font-semibold hover:shadow-lg transition-all duration-300 flex items-center space-x-2"
              >
                <Rocket className="w-5 h-5" />
                <span>Start Onboarding</span>
                <ArrowRight className="w-5 h-5" />
              </MotionButton>
            </Link>
            <MotionButton
              onClick={onPlayVideo}
              variant="secondary"
              className="bg-white text-gray-900 px-8 py-4 rounded-2xl text-lg font-semibold border border-gray-200 hover:shadow-lg transition-all duration-300 flex items-center space-x-2"
            >
              <Play className="w-5 h-5" />
              <span>Watch Demo</span>
            </MotionButton>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}