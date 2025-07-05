import React from 'react'
import { motion } from 'framer-motion'
import { Zap, Settings, Bell } from 'lucide-react'
import Link from 'next/link'
import { MotionButton } from '../ui/MotionButton'

interface NavigationHeaderProps {
  title: string
  subtitle?: string
  showNotifications?: boolean
  showSettings?: boolean
  rightContent?: React.ReactNode
  gradient?: string
}

export const NavigationHeader: React.FC<NavigationHeaderProps> = ({
  title,
  subtitle,
  showNotifications = false,
  showSettings = false,
  rightContent,
  gradient = 'from-indigo-600 to-purple-600'
}) => {
  return (
    <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-3">
            <div className={`bg-gradient-to-r ${gradient} p-2 rounded-xl`}>
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
              {subtitle && <p className="text-sm text-gray-600">{subtitle}</p>}
            </div>
          </Link>
          
          <div className="flex items-center space-x-4">
            {rightContent}
            
            {showNotifications && (
              <MotionButton variant="ghost" size="sm">
                <div className="relative">
                  <Bell className="w-5 h-5" />
                  <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
                </div>
              </MotionButton>
            )}
            
            {showSettings && (
              <MotionButton variant="ghost" size="sm">
                <Settings className="w-5 h-5" />
              </MotionButton>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}