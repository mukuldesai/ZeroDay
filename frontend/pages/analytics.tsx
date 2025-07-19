import React, { useState, useEffect } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '${API_BASE}'
import { 
  TrendingUp, Users, MessageSquare, Target, Download, RefreshCw, Bell, User, Menu, Brain, Settings,
  Palette, Shield, LogOut, UserCircle, ChevronDown, CheckCircle, Clock, AlertCircle
} from 'lucide-react';

const formatTime = (date: Date): string => {
  return date.toLocaleString(); 
};

const getRelativeTime = (timestamp: Date) => {
  const now = new Date();
  const seconds = Math.floor((now.getTime() - timestamp.getTime()) / 1000);
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
};

type NavigationHeaderProps = {
  title: string
  subtitle?: string
  rightContent?: React.ReactNode
  isDemo?: boolean
}

const NavigationHeader = ({ title, subtitle, rightContent, isDemo }: NavigationHeaderProps) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  
  useEffect(() => {
    const handleClickOutside = () => {
      setShowNotifications(false);
      setShowSettings(false);
      setShowUserMenu(false);
    };
    
    if (showNotifications || showSettings || showUserMenu) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showNotifications, showSettings, showUserMenu]);

  const notifications = [
    {
      id: 1,
      title: 'System Update Complete',
      message: 'Analytics dashboard has been updated with new metrics',
      time: new Date(Date.now() - 5 * 60 * 1000),
      type: 'success'
    },
    {
      id: 2,
      title: 'High Usage Alert',
      message: 'AI requests increased by 150% in the last hour',
      time: new Date(Date.now() - 15 * 60 * 1000),
      type: 'warning'
    },
    {
      id: 3,
      title: 'New User Onboarded',
      message: 'Frontend Developer Sarah joined the platform',
      time: new Date(Date.now() - 30 * 60 * 1000),
      type: 'info'
    }
  ];

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'warning': return <AlertCircle className="w-4 h-4 text-yellow-400" />;
      case 'info': return <MessageSquare className="w-4 h-4 text-blue-400" />;
      default: return <Bell className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <nav className="bg-black/20 backdrop-blur-sm border-b border-white/10 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-400 to-purple-400 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div className="flex items-center space-x-2">
              <h1 className="text-white font-bold text-lg">ZeroDay</h1>
              <span className="hidden sm:block text-gray-400 text-sm">Enterprise AI Developer Onboarding Platform</span>
            </div>
          </div>

          
          <div className="hidden md:flex items-center space-x-6">
            <a href="/" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Home</a>
            <a href="/chat" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">AI Chat</a>
            <a href="/dashboard" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Dashboard</a>
            <a href="/tasks" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Tasks</a>
            <a href="/upload" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Upload</a>
          </div>

       
          <div className="flex items-center space-x-3">
            {rightContent}
            
            {isDemo && (
              <div className="bg-yellow-400/20 text-yellow-300 px-3 py-1 rounded-full text-xs font-bold border border-yellow-400/30">
                🚀 DEMO
              </div>
            )}
            
        
            <div className="relative">
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  setShowSettings(!showSettings);
                  setShowNotifications(false);
                  setShowUserMenu(false);
                }}
                className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-white/10"
              >
                <Settings className="w-5 h-5" />
              </button>
              
              {showSettings && (
                <div className="absolute right-0 top-full mt-2 w-80 bg-gray-900/80 backdrop-blur-md border border-white/20 rounded-xl p-4 z-50 shadow-lg">
                  <div className="py-1">
                    <a
                      href="/setup"
                      className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                    >
                      <Palette className="w-4 h-4" />
                      <span>Preferences</span>
                    </a>
                    <a
                      href="/security"
                      className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                    >
                      <Shield className="w-4 h-4" />
                      <span>Security</span>
                    </a>
                    <button
                      onClick={() => console.log('Theme toggle')}
                      className="flex items-center space-x-3 w-full px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                    >
                      <Brain className="w-4 h-4" />
                      <span>Theme</span>
                    </button>
                  </div>
                </div>
              )}
            </div>

            
            <div className="relative">
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  setShowNotifications(!showNotifications);
                  setShowSettings(false);
                  setShowUserMenu(false);
                }}
                className="p-2 text-gray-400 hover:text-white transition-colors relative rounded-lg hover:bg-white/10"
              >
                <Bell className="w-5 h-5" />
                {notifications.length > 0 && (
                  <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
                )}
              </button>
              
              {showNotifications && (
                <div className="absolute right-0 top-full mt-2 w-80 bg-gray-900/80 backdrop-blur-md border border-white/20 rounded-xl p-4 z-50 shadow-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-white font-semibold">Notifications</h3>
                    <span className="text-xs text-gray-400">{notifications.length} new</span>
                  </div>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {notifications.map((notification) => (
                      <div key={notification.id} className="p-3 bg-white/5 rounded-lg border border-white/10">
                        <div className="flex items-start space-x-3">
                          {getNotificationIcon(notification.type)}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-white truncate">
                              {notification.title}
                            </p>
                            <p className="text-xs text-gray-400 mt-1">
                              {notification.message}
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                              {getRelativeTime(notification.time)}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-3 pt-3 border-t border-white/10">
                    <a
                      href="/analytics"
                      className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
                    >
                      View all notifications
                    </a>
                  </div>
                </div>
              )}
            </div>

            
            <div className="relative">
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  setShowUserMenu(!showUserMenu);
                  setShowNotifications(false);
                  setShowSettings(false);
                }}
                className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-white/10 flex items-center justify-center"
              >
                <div className="w-6 h-6 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full flex items-center justify-center text-white text-xs font-bold">
                  D
                </div>
              </button>
              
              {showUserMenu && (
                <div className="absolute right-0 top-full mt-2 w-80 bg-gray-900/80 backdrop-blur-md border border-white/20 rounded-xl p-4 z-50 shadow-lg">
                  <div className="px-3 py-2 border-b border-white/10">
                    <p className="text-sm font-medium text-white">Developer</p>
                    <p className="text-xs text-gray-400">demo@zeroday.ai</p>
                  </div>
                  <div className="py-1">
                    <a
                      href="/dashboard"
                      className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                    >
                      <UserCircle className="w-4 h-4" />
                      <span>Profile</span>
                    </a>
                    <a
                      href="/setup"
                      className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                    >
                      <Users className="w-4 h-4" />
                      <span>Team Info</span>
                    </a>
                    <button
                      onClick={() => window.location.href = '/login'}
                      className="flex items-center space-x-3 w-full px-3 py-2 text-red-300 hover:text-red-200 hover:bg-red-500/10 rounded-lg transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Logout</span>
                    </button>
                  </div>
                </div>
              )}
            </div>

           
            <button 
              className="md:hidden p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-white/10"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              <Menu className="w-5 h-5" />
            </button>
          </div>
        </div>

        
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-white/10">
            <div className="flex flex-col space-y-2">
              <a href="/" className="text-gray-300 hover:text-white transition-colors py-2 px-2 rounded-lg hover:bg-white/10">Home</a>
              <a href="/chat" className="text-gray-300 hover:text-white transition-colors py-2 px-2 rounded-lg hover:bg-white/10">AI Chat</a>
              <a href="/dashboard" className="text-gray-300 hover:text-white transition-colors py-2 px-2 rounded-lg hover:bg-white/10">Dashboard</a>
              <a href="/tasks" className="text-gray-300 hover:text-white transition-colors py-2 px-2 rounded-lg hover:bg-white/10">Tasks</a>
              <a href="/upload" className="text-gray-300 hover:text-white transition-colors py-2 px-2 rounded-lg hover:bg-white/10">Upload</a>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

type AIMetricsProps = {
  timeRange: string  
}

const AIMetrics = ({ timeRange }: AIMetricsProps) => {
  const [metrics, setMetrics] = useState({
    totalRequests: 1234,
    activeUsers: 89,
    tasksGenerated: 456,
    avgResponseTime: '1.2s',
    aiAccuracy: 94.5,
    systemUptime: 99.9
  });

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const [healthResponse, agentsResponse, uploadResponse] = await Promise.all([
          fetch('${API_BASE}/health'),
          fetch('${API_BASE}/agents'),
          fetch('${API_BASE}/api/upload/status')
        ]);

        if (healthResponse.ok) {
          const healthData = await healthResponse.json();
          console.log('Health data:', healthData);
          setMetrics(prev => ({
            ...prev,
            systemUptime: 99.9,
            avgResponseTime: '1.2s'
          }));
        }

        if (agentsResponse.ok) {
          const agentsData = await agentsResponse.json();
          console.log('Agents data:', agentsData);
          const activeAgents = Array.isArray(agentsData) 
            ? agentsData.filter((agent: any) => agent.available).length
            : Object.values(agentsData).filter((agent: any) => agent?.available).length;
          setMetrics(prev => ({
            ...prev,
            totalRequests: 1234,
            activeUsers: activeAgents
          }));
        }

        if (uploadResponse.ok) {
          const uploadData = await uploadResponse.json();
          console.log('Upload data:', uploadData);
          setMetrics(prev => ({
            ...prev,
            tasksGenerated: uploadData.documents_indexed || prev.tasksGenerated
          }));
        }
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      }
    };

    fetchMetrics();
  }, [timeRange]);

  const metricCards = [
    {
      title: 'Total AI Requests',
      value: metrics.totalRequests.toLocaleString(),
      change: '+12.5%',
      icon: <MessageSquare className="w-6 h-6" />,
      color: 'bg-gradient-to-r from-blue-600 to-indigo-600'
    },
    {
      title: 'Active Users',
      value: metrics.activeUsers.toString(),
      change: '+8.3%',
      icon: <Users className="w-6 h-6" />,
      color: 'bg-gradient-to-r from-green-600 to-emerald-600'
    },
    {
      title: 'Tasks Generated',
      value: metrics.tasksGenerated.toLocaleString(),
      change: '+15.7%',
      icon: <Target className="w-6 h-6" />,
      color: 'bg-gradient-to-r from-orange-600 to-red-600'
    },
    {
      title: 'Avg Response Time',
      value: metrics.avgResponseTime,
      change: '-5.2%',
      icon: <TrendingUp className="w-6 h-6" />,
      color: 'bg-gradient-to-r from-purple-600 to-pink-600'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {metricCards.map((metric, index) => (
        <div
          key={metric.title}
          className={`${metric.color} rounded-xl p-6 text-white relative overflow-hidden shadow-sm`}
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
          <div className="relative">
            <div className="flex items-center justify-between mb-2">
              {metric.icon}
              <span className="text-xs bg-white/20 px-2 py-1 rounded-full">{metric.change}</span>
            </div>
            <div className="text-2xl font-bold mb-1">{metric.value}</div>
            <div className="text-sm opacity-90">{metric.title}</div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('7d');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [systemMetrics, setSystemMetrics] = useState({
    uptime: 99.9,
    avgResponse: '1.2s',
    agentsOnline: 4,
    documentsIndexed: 105
  });

  const timeRanges = [
    { value: '1d', label: 'Last 24 Hours' },
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' },
    { value: '90d', label: 'Last 90 Days' }
  ];

  useEffect(() => {
    const fetchSystemMetrics = async () => {
      try {
        const [healthResponse, uploadResponse, agentsResponse] = await Promise.all([
          fetch('${API_BASE}/health'),
          fetch('${API_BASE}/api/upload/status'),
          fetch('${API_BASE}/agents')
        ]);

        if (healthResponse.ok) {
          const healthData = await healthResponse.json();
          setSystemMetrics(prev => ({
            ...prev,
            uptime: 99.9,
            avgResponse: '1.2s'
          }));
        }

        if (uploadResponse.ok) {
          const uploadData = await uploadResponse.json();
          setSystemMetrics(prev => ({
            ...prev,
            documentsIndexed: uploadData.documents_indexed || prev.documentsIndexed
          }));
        }

        if (agentsResponse.ok) {
          const agentsData = await agentsResponse.json();
          const activeAgents = Array.isArray(agentsData) 
            ? agentsData.filter((agent: any) => agent.available).length
            : Object.values(agentsData).filter((agent: any) => agent?.available).length;
          setSystemMetrics(prev => ({
            ...prev,
            agentsOnline: activeAgents
          }));
        }
      } catch (error) {
        console.error('Failed to fetch system metrics:', error);
      }
    };

    fetchSystemMetrics();
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await Promise.all([
        fetch('${API_BASE}/health'),
        fetch('${API_BASE}/agents'),
        fetch('${API_BASE}/api/upload/status')
      ]);
    } catch (error) {
      console.error('Failed to refresh data:', error);
    }
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsRefreshing(false);
  };

  const handleExport = () => {
    const csvData = `Metric,Value,Period
Total Requests,1234,${timeRange}
Active Users,89,${timeRange}
Tasks Generated,456,${timeRange}
Avg Response Time,1.2s,${timeRange}
System Uptime,${systemMetrics.uptime}%,${timeRange}
Documents Indexed,${systemMetrics.documentsIndexed},${timeRange}`;
    
    const blob = new Blob([csvData], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `zeroday-analytics-${timeRange}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const rightContent = (
    <div className="flex items-center space-x-3">
      <select
        value={timeRange}
        onChange={(e) => setTimeRange(e.target.value)}
        className="bg-white/10 border border-white/20 text-white rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        {timeRanges.map(range => (
          <option key={range.value} value={range.value} className="bg-gray-800 text-white">
            {range.label}
          </option>
        ))}
      </select>

      <button
        onClick={handleRefresh}
        disabled={isRefreshing}
        className="bg-white/10 border border-white/20 text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-white/20 disabled:opacity-50 flex items-center space-x-2 transition-colors"
      >
        <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
        <span className="hidden sm:inline">{isRefreshing ? 'Refreshing...' : 'Refresh'}</span>
      </button>

      <button
        onClick={handleExport}
        className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg px-4 py-2 text-sm font-medium hover:from-blue-700 hover:to-indigo-700 flex items-center space-x-2 transition-all shadow-sm"
      >
        <Download className="w-4 h-4" />
        <span className="hidden sm:inline">Export</span>
      </button>
    </div>
  );
  

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
  <NavigationHeader
    title="Analytics Dashboard"
    subtitle="Monitor AI agent performance and system metrics in real-time"
    rightContent={rightContent}
    isDemo={true}
  />

  <div className="max-w-7xl mx-auto px-6 py-6">
    
    <div className="mb-8">
      <h1 className="text-3xl font-bold text-white mb-2">Analytics Dashboard</h1>
      <p className="text-sm text-gray-400">Monitor AI agent performance and system metrics in real-time</p>
    </div>

    <AIMetrics timeRange={timeRange} />

    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
        <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
          <TrendingUp className="w-6 h-6 mr-3 text-blue-400" />
          Usage Trends
        </h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
            <div>
              <h4 className="font-medium text-white">Peak Usage Hours</h4>
              <p className="text-sm text-gray-400">9 AM - 5 PM EST</p>
            </div>
            <div className="text-2xl font-bold text-blue-400">8h</div>
          </div>
          <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
            <div>
              <h4 className="font-medium text-white">Most Active Agent</h4>
              <p className="text-sm text-gray-400">Knowledge Agent</p>
            </div>
            <div className="text-2xl font-bold text-green-400">67%</div>
          </div>
          <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
            <div>
              <h4 className="font-medium text-white">User Satisfaction</h4>
              <p className="text-sm text-gray-400">Average rating</p>
            </div>
            <div className="text-2xl font-bold text-yellow-400">4.8/5</div>
          </div>
        </div>
      </div>

      <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
        <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
          <MessageSquare className="w-6 h-6 mr-3 text-purple-400" />
          Recent Activity
        </h3>
        <div className="space-y-4">
          <div className="flex items-start space-x-3 p-3 bg-blue-500/10 rounded-xl border border-blue-500/20">
            <MessageSquare className="w-5 h-5 text-blue-400 mt-1" />
            <div>
              <p className="text-sm font-medium text-white">New user onboarded</p>
              <p className="text-xs text-gray-400">Frontend Developer joined the platform</p>
              <p className="text-xs text-gray-500 mt-1">
                {getRelativeTime(new Date(Date.now() - 5 * 60 * 1000))}
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-3 p-3 bg-green-500/10 rounded-xl border border-green-500/20">
            <Target className="w-5 h-5 text-green-400 mt-1" />
            <div>
              <p className="text-sm font-medium text-white">Task completion spike</p>
              <p className="text-xs text-gray-400">15 tasks completed in the last hour</p>
              <p className="text-xs text-gray-500 mt-1">
                {getRelativeTime(new Date(Date.now() - 60 * 60 * 1000))}
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-3 p-3 bg-purple-500/10 rounded-xl border border-purple-500/20">
            <Users className="w-5 h-5 text-purple-400 mt-1" />
            <div>
              <p className="text-sm font-medium text-white">Learning path created</p>
              <p className="text-xs text-gray-400">React fundamentals path for junior developers</p>
              <p className="text-xs text-gray-500 mt-1">
                {getRelativeTime(new Date(Date.now() - 2 * 60 * 60 * 1000))}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
      <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
        <Brain className="w-6 h-6 mr-3 text-indigo-400" />
        System Overview
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="text-center p-4 bg-white/5 rounded-xl border border-white/10">
          <div className="text-3xl font-bold text-green-400 mb-2">{systemMetrics.uptime}%</div>
          <div className="text-sm text-gray-400">Uptime</div>
        </div>

        <div className="text-center p-4 bg-white/5 rounded-xl border border-white/10">
          <div className="text-3xl font-bold text-blue-400 mb-2">{systemMetrics.avgResponse}</div>
          <div className="text-sm text-gray-400">Avg Response</div>
        </div>

        <div className="text-center p-4 bg-white/5 rounded-xl border border-white/10">
          <div className="text-3xl font-bold text-orange-400 mb-2">{systemMetrics.agentsOnline}/4</div>
          <div className="text-sm text-gray-400">Agents Online</div>
        </div>

        <div className="text-center p-4 bg-white/5 rounded-xl border border-white/10">
          <div className="text-3xl font-bold text-purple-400 mb-2">{systemMetrics.documentsIndexed}</div>
          <div className="text-sm text-gray-400">Docs Indexed</div>
        </div>
      </div>
    </div>
  </div>
</div>
);
}
