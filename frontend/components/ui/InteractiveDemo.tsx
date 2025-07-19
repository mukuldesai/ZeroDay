import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { MotionButton } from './MotionButton'

interface InteractiveDemoProps {
  demoSteps: string[]
  isDemoMode?: boolean
}

export const InteractiveDemo: React.FC<InteractiveDemoProps> = ({ 
  demoSteps, 
  isDemoMode = false 
}) => {
  const [activeDemo, setActiveDemo] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveDemo((prev) => (prev + 1) % demoSteps.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [demoSteps.length])

  const getDemoResponse = (step: string) => {
    if (isDemoMode) {
      return {
        analyzing: '🤖 Using synthetic codebase...',
        generating: '✨ Generating response from demo data...',
        ready: '✅ Demo response ready!'
      }
    }
    return {
      analyzing: '🤖 Analyzing your codebase...',
      generating: '✨ Generating personalized response...',
      ready: '✅ Response ready!'
    }
  }

  return (
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
            {isDemoMode ? 'Demo Mode Active' : 'See ZeroDay in Action'}
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {isDemoMode 
              ? 'Experience the full system with synthetic data - no setup required.'
              : 'Experience how our AI agents transform the onboarding process with intelligent assistance.'
            }
          </p>
        </motion.div>

        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-3xl p-8 lg:p-12">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-6">
                {isDemoMode ? 'Demo Examples:' : 'Try These Examples:'}
              </h3>
              <div className="space-y-4">
                {demoSteps.map((step, index) => (
                  <MotionButton
                    key={index}
                    onClick={() => setActiveDemo(index)}
                    className={`w-full text-left p-4 rounded-xl transition-all duration-300 ${
                      activeDemo === index
                        ? 'bg-indigo-600 text-white shadow-lg'
                        : 'bg-white text-gray-700 hover:bg-gray-50'
                    }`}
                    variant="ghost"
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
                  </MotionButton>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-xl p-6">
              <div className="bg-gray-900 rounded-lg p-4 text-green-400 font-mono text-sm">
                <div className="flex items-center space-x-2 mb-3">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-gray-400 ml-4">
                    ZeroDay {isDemoMode ? 'Demo' : 'Terminal'}
                  </span>
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
                    <div className="text-blue-400">{getDemoResponse(demoSteps[activeDemo]).analyzing}</div>
                    <div className="text-yellow-400">{getDemoResponse(demoSteps[activeDemo]).generating}</div>
                    <div className="text-green-400">{getDemoResponse(demoSteps[activeDemo]).ready}</div>
                  </motion.div>
                </AnimatePresence>
              </div>
              
              <div className="mt-6 text-center space-y-3">
                <Link href={isDemoMode ? "/chat" : "/demo"}>
                  <MotionButton className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition-all duration-300">
                    {isDemoMode ? 'Try Live Chat' : 'Try Full Demo'}
                  </MotionButton>
                </Link>
                {!isDemoMode && (
                  <div className="text-sm text-gray-500">
                    No setup required - uses synthetic data
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}