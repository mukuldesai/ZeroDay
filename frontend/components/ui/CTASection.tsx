import React from 'react'
import { motion } from 'framer-motion'
import { Rocket, ArrowRight, BarChart3 } from 'lucide-react'
import Link from 'next/link'
import { MotionButton } from './MotionButton'

interface CTASectionProps {
  isDemo?: boolean
}

export const CTASection: React.FC<CTASectionProps> = ({ isDemo = false }) => {
  return (
    <section className={`py-20 ${
      isDemo 
        ? 'bg-gradient-to-r from-demo-600 to-demo-800' 
        : 'bg-gradient-to-r from-indigo-600 to-purple-600'
    }`}>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
        >
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            {isDemo ? 'Experience ZeroDay in Action' : 'Ready to Transform Your Onboarding?'}
          </h2>
          <p className="text-xl text-indigo-100 mb-10 max-w-2xl mx-auto">
            {isDemo 
              ? 'See how ZeroDay works with realistic synthetic data - no setup required.'
              : 'Join the future of developer onboarding. Get new team members productive in days, not weeks.'
            }
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
            <Link href={isDemo ? "/demo" : "/chat"}>
              <MotionButton className="bg-white text-indigo-600 px-8 py-4 rounded-2xl text-lg font-semibold hover:shadow-lg transition-all duration-300 flex items-center space-x-2">
                <Rocket className="w-5 h-5" />
                <span>{isDemo ? 'Try Demo' : 'Get Started Now'}</span>
                <ArrowRight className="w-5 h-5" />
              </MotionButton>
            </Link>
            <Link href="/dashboard">
              <MotionButton
                variant="ghost"
                className="border-2 border-white text-white px-8 py-4 rounded-2xl text-lg font-semibold hover:bg-white hover:text-indigo-600 transition-all duration-300 flex items-center space-x-2"
              >
                <BarChart3 className="w-5 h-5" />
                <span>View Dashboard</span>
              </MotionButton>
            </Link>
          </div>
          {isDemo && (
            <div className="mt-6 text-demo-100 text-sm">
              Currently viewing demo mode with synthetic data
            </div>
          )}
        </motion.div>
      </div>
    </section>
  )
}