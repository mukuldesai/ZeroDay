import React from 'react'
import { Lightbulb } from 'lucide-react'
import { MotionButton } from './MotionButton'
import Link from 'next/link'

interface QuickAction {
  label: string
  icon: React.ReactNode
  href?: string
  onClick?: () => void
  color: string
}

interface QuickActionsDashboardProps {
  actions: QuickAction[]
}

export const QuickActionsDashboard: React.FC<QuickActionsDashboardProps> = ({ actions }) => {
  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <Lightbulb className="w-5 h-5 mr-2 text-yellow-500" />
        Quick Actions
      </h3>
      <div className="space-y-3">
        {actions.map((action, index) => {
          const ButtonContent = (
            <MotionButton
              onClick={action.onClick}
              className={`w-full ${action.color} p-3 rounded-lg hover:opacity-90 transition-colors flex items-center space-x-2`}
              variant="ghost"
            >
              {action.icon}
              <span>{action.label}</span>
            </MotionButton>
          )

          return action.href ? (
            <Link key={index} href={action.href}>
              {ButtonContent}
            </Link>
          ) : (
            <div key={index}>{ButtonContent}</div>
          )
        })}
      </div>
    </div>
  )
}