import React from 'react'
import { TrendingUp, Flame, Clock } from 'lucide-react'

interface WelcomeBannerProps {
  userName?: string
  completionRate: number
  learningStreak: number
  averageResponseTime: string
}

export const WelcomeBanner: React.FC<WelcomeBannerProps> = ({
  userName = "Alex",
  completionRate,
  learningStreak,
  averageResponseTime
}) => {
  return (
    <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-white">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold mb-2">Welcome back, {userName}! 👋</h2>
          <p className="text-indigo-100 mb-4">
            You're making great progress. You've completed {completionRate}% of your onboarding goals this week!
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