'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  BarChart3, BookOpen, CheckSquare, TrendingUp, Bell, Settings,
  Activity, RefreshCw, Clock, TrendingUp as TrendingUpIcon, Users, Award
} from 'lucide-react'
import Link from 'next/link'

// Data
import { 
  progressData, 
  recentActivity, 
  learningPaths, 
  quickActions, 
  todaysGoals, 
  stats 
} from '../lib/data/dashboardData'

// Components
import { NavigationHeader } from '../components/layout/NavigationHeader'
import { WelcomeBanner } from '../components/ui/WelcomeBanner'
import { ProgressCard } from '../components/ui/ProgressCard'
import { ActivityItem } from '../components/ui/ActivityItem'
import { LearningPathCard } from '../components/ui/LearningPathCard'
import { QuickActionsDashboard } from '../components/ui/QuickActionsDashboard'
import { GoalsTracker } from '../components/ui/GoalsTracker'
import { StatsCard } from '../components/ui/StatsCard'
import { MotionButton } from '../components/ui/MotionButton'

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('overview')
  const [timeRange, setTimeRange] = useState('week')
  const [isLiveMode, setIsLiveMode] = useState(true)

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'learning', label: 'Learning Paths', icon: <BookOpen className="w-4 h-4" /> },
    { id: 'tasks', label: 'Tasks', icon: <CheckSquare className="w-4 h-4" /> },
    { id: 'analytics', label: 'Analytics', icon: <TrendingUp className="w-4 h-4" /> }
  ]

  const navigationActions = (
    <>
      {/* Live Mode Toggle */}
      <MotionButton
        onClick={() => setIsLiveMode(!isLiveMode)}
        className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
          isLiveMode 
            ? 'bg-green-100 text-green-700' 
            : 'bg-gray-100 text-gray-600'
        }`}
        variant="ghost"
      >
        <div className={`w-2 h-2 rounded-full ${isLiveMode ? 'bg-green-500' : 'bg-gray-400'}`} />
        <span className="text-sm font-medium">Live</span>
      </MotionButton>
    </>
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <NavigationHeader
        title="ZeroDay Dashboard"
        subtitle="Your onboarding progress"
        showNotifications
        showSettings
        rightContent={navigationActions}
      />

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center space-x-8 py-6">
          {tabs.map((tab) => (
            <MotionButton
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                activeTab === tab.id
                  ? 'bg-indigo-100 text-indigo-700 border border-indigo-200'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
              variant="ghost"
            >
              {tab.icon}
              <span className="font-medium">{tab.label}</span>
            </MotionButton>
          ))}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 pb-6">
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              {/* Welcome Section */}
              <WelcomeBanner
                completionRate={stats.completionRate}
                learningStreak={stats.learningStreak}
                averageResponseTime={stats.averageResponseTime}
              />

              {/* Progress Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {progressData.map((data, index) => (
                  <ProgressCard key={index} data={data} delay={index * 0.1} />
                ))}
              </div>

              {/* Main Content Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Recent Activity */}
                <div className="lg:col-span-2">
                  <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                        <Activity className="w-5 h-5 mr-2 text-indigo-600" />
                        Recent Activity
                      </h3>
                      <div className="flex items-center space-x-2">
                        <select 
                          value={timeRange}
                          onChange={(e) => setTimeRange(e.target.value)}
                          className="text-sm bg-gray-100 border-0 rounded-lg px-3 py-1 focus:ring-2 focus:ring-indigo-500"
                        >
                          <option value="day">Today</option>
                          <option value="week">This Week</option>
                          <option value="month">This Month</option>
                        </select>
                        <MotionButton variant="ghost" size="sm">
                          <RefreshCw className="w-4 h-4" />
                        </MotionButton>
                      </div>
                    </div>
                    
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                      {recentActivity.map((activity, index) => (
                        <ActivityItem key={activity.id} activity={activity} index={index} />
                      ))}
                    </div>
                  </div>
                </div>

                {/* Quick Actions & Goals */}
                <div className="space-y-6">
                  <QuickActionsDashboard actions={quickActions} />
                  <GoalsTracker goals={todaysGoals} />
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'learning' && (
            <motion.div
              key="learning"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Learning Paths</h2>
                <MotionButton className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700">
                  <BookOpen className="w-4 h-4 mr-2" />
                  Create Custom Path
                </MotionButton>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {learningPaths.map((path, index) => (
                  <LearningPathCard key={path.id} path={path} delay={index * 0.1} />
                ))}
              </div>

              {/* Learning Analytics */}
              <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-6">Learning Analytics</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <StatsCard
                    icon={<TrendingUpIcon className="w-8 h-8" />}
                    title="Time This Week"
                    value="12h 30m"
                    color="bg-green-100 text-green-600"
                  />
                  <StatsCard
                    icon={<Award className="w-8 h-8" />}
                    title="Modules Completed"
                    value={15}
                    color="bg-blue-100 text-blue-600"
                  />
                  <StatsCard
                    icon={<Users className="w-8 h-8" />}
                    title="Average Rating"
                    value="4.8"
                    color="bg-purple-100 text-purple-600"
                  />
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'tasks' && (
            <motion.div
              key="tasks"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Tasks Overview</h2>
                <Link href="/tasks">
                  <MotionButton className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700">
                    <CheckSquare className="w-4 h-4 mr-2" />
                    View All Tasks
                  </MotionButton>
                </Link>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatsCard
                  icon={<CheckSquare className="w-6 h-6" />}
                  title="Total Tasks"
                  value={12}
                  change="+3 this week"
                  color="bg-gradient-to-r from-blue-500 to-blue-600"
                />
                <StatsCard
                  icon={<TrendingUpIcon className="w-6 h-6" />}
                  title="Completed"
                  value={8}
                  change="+2 today"
                  color="bg-gradient-to-r from-green-500 to-green-600"
                />
                <StatsCard
                  icon={<Activity className="w-6 h-6" />}
                  title="In Progress"
                  value={2}
                  color="bg-gradient-to-r from-orange-500 to-orange-600"
                />
                <StatsCard
                  icon={<Clock className="w-6 h-6" />}
                  title="Avg. Completion"
                  value="3.2 hours"
                  change="-20min"
                  color="bg-gradient-to-r from-purple-500 to-purple-600"
                />
              </div>
            </motion.div>
          )}

          {activeTab === 'analytics' && (
            <motion.div
              key="analytics"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Analytics & Insights</h2>
                <MotionButton className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700">
                  Export Data
                </MotionButton>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatsCard
                  icon={<Activity className="w-5 h-5" />}
                  title="Total Interactions"
                  value={stats.totalInteractions}
                  change="+23%"
                  color="bg-gradient-to-r from-blue-500 to-blue-600"
                />
                <StatsCard
                  icon={<Clock className="w-5 h-5" />}
                  title="Avg Response Time"
                  value={stats.averageResponseTime}
                  change="-15%"
                  color="bg-gradient-to-r from-green-500 to-green-600"
                />
                <StatsCard
                  icon={<TrendingUpIcon className="w-5 h-5" />}
                  title="Completion Rate"
                  value={`${stats.completionRate}%`}
                  change="+8%"
                  color="bg-gradient-to-r from-purple-500 to-purple-600"
                />
                <StatsCard
                  icon={<Award className="w-5 h-5" />}
                  title="Learning Streak"
                  value={`${stats.learningStreak} days`}
                  change="+2 days"
                  color="bg-gradient-to-r from-orange-500 to-orange-600"
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}