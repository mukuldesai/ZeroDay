import React from 'react'
import { motion } from 'framer-motion'
import { Code, Brain, BookOpen } from 'lucide-react'
import { floatingAnimation } from '../../lib/animations/variants'

interface FloatingElementsProps {
  isDemo?: boolean
}

export const FloatingElements: React.FC<FloatingElementsProps> = ({ isDemo = false }) => {
  const colorClass = isDemo ? 'text-demo-200' : 'text-indigo-200'
  
  return (
    <>
      <motion.div
        variants={floatingAnimation}
        custom={0}
        animate="animate"
        className={`absolute top-20 left-20 ${colorClass} hidden lg:block`}
      >
        <Code className="w-8 h-8" />
      </motion.div>

      <motion.div
        variants={floatingAnimation}
        custom={1}
        animate="animate"
        className={`absolute top-40 right-20 ${isDemo ? 'text-demo-300' : 'text-purple-200'} hidden lg:block`}
      >
        <Brain className="w-10 h-10" />
      </motion.div>

      <motion.div
        variants={floatingAnimation}
        custom={2}
        animate="animate"
        className={`absolute bottom-20 left-1/4 ${isDemo ? 'text-demo-200' : 'text-green-200'} hidden lg:block`}
      >
        <BookOpen className="w-6 h-6" />
      </motion.div>
    </>
  )
}