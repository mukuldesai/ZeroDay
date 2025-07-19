import React from 'react'
import { TrendingUp, Flame, Clock } from 'lucide-react'

interface WelcomeBannerProps {
  userName?: string
  completionRate: number
  learningStreak: number
  averageResponseTime: string
  isDemo?: boolean
}

export const WelcomeBanner: React.FC<WelcomeBannerProps> = ({
  userName = "Developer", 
  completionRate,
  learningStreak,
  averageResponseTime,
  isDemo = false
}) => {
  return (
    <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-white relative">
      
      {isDemo && (
        <div className="absolute top-4 right-4 bg-yellow-400 text-black px-3 py-1 rounded-full text-sm font-medium">
          Demo Mode
        </div>
      )}
      
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold mb-2">Welcome back, {userName}! 👋</h2>
          <p className="text-indigo-100 mb-4">
            {isDemo 
              ? `This is a demo showing how ZeroDay tracks progress. In a real scenario, you'd see ${completionRate}% completion of your onboarding goals.`
              : `You're making great progress. You've completed ${completionRate}% of your onboarding goals this week!`
            }
          </p>
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <Flame className="w-5 h-5" />
              <span>{learningStreak} day streak</span>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="w-5 h-5" />
              <span>{averageResponseTime} avg response</span>
            </div>
          </div>
        </div>
        <div className="hidden md:block">
          <div className="w-32 h-32 bg-white/10 rounded-full flex items-center justify-center">
            <TrendingUp className="w-16 h-16" />
          </div>
        </div>
      </div>
    </div>
  )
}