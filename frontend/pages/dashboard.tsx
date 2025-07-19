import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  BarChart3, BookOpen, CheckSquare, TrendingUp, Wifi, WifiOff, Zap, Brain, Target, Users, Code, MessageSquare, Clock, ArrowUp, Bell, User, Menu, Settings,
  Palette, Shield, LogOut, UserCircle, CheckCircle, AlertCircle
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
  showNotifications?: boolean
  showSettings?: boolean
}

type ButtonProps = {
  onClick: () => void
  className?: string
  children: React.ReactNode
}

type AgentAvailability = {
  available: boolean
  name: string
}

type AgentStatus = {
  knowledge?: AgentAvailability
  task?: AgentAvailability
  mentor?: AgentAvailability
  guide?: AgentAvailability
}

type UploadStatus = {
  documents_indexed?: number
  vector_store_status?: string
}

type CodeStats = {
  indexed_files?: number
  status?: string
  demo_mode?: boolean
}

type TaskSuggestion = {
  task?: string
}


const DEMO_MODE = true; 
const API_TIMEOUT = 3000; 
const FETCH_RETRY_COUNT = 1;

const MotionButton = React.memo(({ onClick, className, children }: ButtonProps) => {
  return (
    <button
      onClick={onClick}
      className={className}
    >
      {children}
    </button>
  );
});

const NavigationHeader = React.memo(({ title, subtitle, rightContent, showNotifications = false, showSettings = false }: NavigationHeaderProps) => { 
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showNotificationsDropdown, setShowNotificationsDropdown] = useState(false);
  const [showSettingsDropdown, setShowSettingsDropdown] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

 
  const notifications = useMemo(() => [
    {
      id: 1,
      title: 'AI Agents Online',
      message: 'All 4 AI agents are active and processing requests',
      time: new Date(Date.now() - 3 * 60 * 1000),
      type: 'success'
    },
    {
      id: 2,
      title: 'Knowledge Base Updated',
      message: 'Vector database refreshed with 105 documents',
      time: new Date(Date.now() - 10 * 60 * 1000),
      type: 'info'
    },
    {
      id: 3,
      title: 'Performance Alert',
      message: 'Response time optimization completed',
      time: new Date(Date.now() - 20 * 60 * 1000),
      type: 'warning'
    }
  ], []);

  const getNotificationIcon = useCallback((type: string) => {
    switch (type) {
      case 'success': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'warning': return <AlertCircle className="w-4 h-4 text-yellow-400" />;
      case 'info': return <MessageSquare className="w-4 h-4 text-blue-400" />;
      default: return <Bell className="w-4 h-4 text-gray-400" />;
    }
  }, []);

  useEffect(() => {
    const handleClickOutside = () => {
      setShowNotificationsDropdown(false);
      setShowSettingsDropdown(false);
      setShowUserMenu(false);
    };
    
    if (showNotificationsDropdown || showSettingsDropdown || showUserMenu) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showNotificationsDropdown, showSettingsDropdown, showUserMenu]);

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
              <span className="hidden sm:block text-gray-400 text-sm">Enterprise AI Developer Platform</span>
            </div>
          </div>

          <div className="hidden md:flex items-center space-x-6">
            <a href="/" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Home</a>
            <a href="/chat" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">AI Chat</a>
            <a href="/dashboard" className="text-blue-400 font-medium text-sm">Dashboard</a>
            <a href="/tasks" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Tasks</a>
            <a href="/upload" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Upload</a>
          </div>

          <div className="flex items-center space-x-3">
            {rightContent}
            
            {showSettings && (
              <div className="relative">
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowSettingsDropdown(!showSettingsDropdown);
                    setShowNotificationsDropdown(false);
                    setShowUserMenu(false);
                  }}
                  className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-white/10"
                >
                  <Settings className="w-5 h-5" />
                </button>
                
                {showSettingsDropdown && (
                  <div className="absolute right-0 top-full mt-2 w-56 bg-gray-900/80 backdrop-blur-md border border-white/20 rounded-xl p-2 z-50 shadow-lg">
                    <div className="py-1">
                      <a href="/setup" className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors">
                        <Palette className="w-4 h-4" />
                        <span>Preferences</span>
                      </a>
                      <a href="/security" className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors">
                        <Shield className="w-4 h-4" />
                        <span>Security</span>
                      </a>
                    </div>
                  </div>
                )}
              </div>
            )}

            {showNotifications && (
              <div className="relative">
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowNotificationsDropdown(!showNotificationsDropdown);
                    setShowSettingsDropdown(false);
                    setShowUserMenu(false);
                  }}
                  className="p-2 text-gray-400 hover:text-white transition-colors relative rounded-lg hover:bg-white/10"
                >
                  <Bell className="w-5 h-5" />
                  {notifications.length > 0 && (
                    <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
                  )}
                </button>
                
                {showNotificationsDropdown && (
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
                  </div>
                )}
              </div>
            )}

            <div className="relative">
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  setShowUserMenu(!showUserMenu);
                  setShowNotificationsDropdown(false);
                  setShowSettingsDropdown(false);
                }}
                className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-white/10 flex items-center justify-center"
              >
                <div className="w-6 h-6 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full flex items-center justify-center text-white text-xs font-bold">
                  D
                </div>
              </button>
              
              {showUserMenu && (
                <div className="absolute right-0 top-full mt-2 w-56 bg-gray-900/80 backdrop-blur-md border border-white/20 rounded-xl p-2 z-50 shadow-lg">
                  <div className="px-3 py-2 border-b border-white/10">
                    <p className="text-sm font-medium text-white">Developer</p>
                    <p className="text-xs text-gray-400">demo@zeroday.ai</p>
                  </div>
                  <div className="py-1">
                    <a href="/dashboard" className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors">
                      <UserCircle className="w-4 h-4" />
                      <span>Profile</span>
                    </a>
                    <button onClick={() => window.location.href = '/login'} className="flex items-center space-x-3 w-full px-3 py-2 text-red-300 hover:text-red-200 hover:bg-red-500/10 rounded-lg transition-colors">
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
              <a href="/dashboard" className="text-blue-400 py-2 px-2 rounded-lg bg-blue-500/10">Dashboard</a>
              <a href="/tasks" className="text-gray-300 hover:text-white transition-colors py-2 px-2 rounded-lg hover:bg-white/10">Tasks</a>
              <a href="/upload" className="text-gray-300 hover:text-white transition-colors py-2 px-2 rounded-lg hover:bg-white/10">Upload</a>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
});

export default function OptimizedDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(false);
  const [hasErrors, setHasErrors] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

 
  const [dashboardData, setDashboardData] = useState({
    realTimeMetrics: {
      activeAgents: 4,
      responseTime: '1.2s',
      documentsIndexed: 105,
      lastAgentActivity: new Date()
    },
    agentStatus: {
      knowledge: { available: true, name: 'Knowledge Agent' },
      task: { available: true, name: 'Task Agent' },
      mentor: { available: true, name: 'Mentor Agent' },
      guide: { available: true, name: 'Guide Agent' }
    },
    uploadStatus: {
      documents_indexed: 105,
      vector_store_status: 'ready'
    },
    codeStats: {
      indexed_files: 105,
      status: 'ready',
      demo_mode: true
    },
    taskSuggestion: {
      task: 'Consider implementing error boundaries for better error handling in your React components'
    }
  });

 
  const fetchData = useCallback(async (url: string, options: any = {}) => {
    if (DEMO_MODE) {
      
      return null;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: { 'Content-Type': 'application/json', ...options.headers }
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      console.warn(`⚠️ API call failed: ${url}`, error);
      return null;
    }
  }, []);

  
  useEffect(() => {
    setLastUpdated(new Date().toLocaleString());
    
    if (DEMO_MODE) {
     
      console.log('🚀 Demo mode - loading instantly');
      return;
    }

    // Only make essential API calls
    const loadEssentialData = async () => {
      setIsLoading(true);
      
      try {
       
        const agentResult = await fetchData('/agents');
        if (agentResult) {
          setDashboardData(prev => ({
            ...prev,
            agentStatus: {
              knowledge: { 
                ...prev.agentStatus.knowledge,
                available: agentResult.knowledge?.available || false
              },
              mentor: { 
                ...prev.agentStatus.mentor,
                available: agentResult.mentor?.available || false
              },
              guide: { 
                ...prev.agentStatus.guide,
                available: agentResult.guide?.available || false
              },
              task: { 
                ...prev.agentStatus.task,
                available: agentResult.task?.available || false
              }
            }
          }));
        }
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
        setHasErrors(true);
      } finally {
        setIsLoading(false);
      }
    };

    loadEssentialData();
  }, [fetchData]);

  
  useEffect(() => {
    if (DEMO_MODE) return;

    const interval = setInterval(() => {
      setDashboardData(prev => ({
        ...prev,
        realTimeMetrics: {
          ...prev.realTimeMetrics,
          responseTime: `${(Math.random() * 2 + 0.5).toFixed(1)}s`,
          lastAgentActivity: new Date()
        }
      }));
    }, 30000); 
    return () => clearInterval(interval);
  }, []);

  
  const tabs = useMemo(() => [
    { id: 'overview', label: 'AI Dashboard', icon: <Brain className="w-4 h-4" /> },
    { id: 'agents', label: 'Live Agents', icon: <Zap className="w-4 h-4" /> },
    { id: 'analytics', label: 'Performance', icon: <TrendingUp className="w-4 h-4" /> },
    { id: 'knowledge', label: 'Knowledge Base', icon: <BookOpen className="w-4 h-4" /> }
  ], []);

  
  const aiAgentStatus = useMemo(() => [
    {
      name: 'Knowledge Agent',
      status: dashboardData.agentStatus?.knowledge?.available ? 'active' : 'inactive',
      lastResponse: '2s ago',
      confidence: 98,
      requests: 47,
      icon: <BookOpen className="w-5 h-5" />,
      realName: dashboardData.agentStatus?.knowledge?.name || 'Knowledge Agent'
    },
    {
      name: 'Task Agent', 
      status: dashboardData.agentStatus?.task?.available ? 'active' : 'inactive',
      lastResponse: '5s ago', 
      confidence: 95,
      requests: 23,
      icon: <Target className="w-5 h-5" />,
      realName: dashboardData.agentStatus?.task?.name || 'Task Agent'
    },
    {
      name: 'Mentor Agent',
      status: dashboardData.agentStatus?.mentor?.available ? 'active' : 'inactive', 
      lastResponse: '1s ago',
      confidence: 97,
      requests: 31,
      icon: <Users className="w-5 h-5" />,
      realName: dashboardData.agentStatus?.mentor?.name || 'Mentor Agent'
    },
    {
      name: 'Guide Agent',
      status: dashboardData.agentStatus?.guide?.available ? 'active' : 'inactive',
      lastResponse: '8s ago',
      confidence: 92, 
      requests: 15,
      icon: <MessageSquare className="w-5 h-5" />,
      realName: dashboardData.agentStatus?.guide?.name || 'Guide Agent'
    }
  ], [dashboardData.agentStatus]);

  const rightContent = useMemo(() => (
    <div className="flex items-center space-x-3">
      <div className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-green-500/20 border border-green-500/30">
        <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
        <span className="text-sm font-medium text-green-300">
          {DEMO_MODE ? 'Demo Mode' : 'Live'}
        </span>
      </div>
      <div className="px-3 py-2 rounded-lg bg-blue-500/20 border border-blue-500/30">
        <span className="text-sm font-medium text-blue-300">
          Response: {dashboardData.realTimeMetrics.responseTime}
        </span>
      </div>
    </div>
  ), [dashboardData.realTimeMetrics.responseTime]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <NavigationHeader
        title="ZeroDay AI Platform"
        subtitle={
          hasErrors 
            ? "⚠️ Some services offline - Demo mode active" 
            : `🚀 AI Dashboard • ${dashboardData.realTimeMetrics.activeAgents} Agents Active`
        }
        showNotifications={true}
        showSettings={true}
        rightContent={rightContent}
      />

      {(hasErrors || DEMO_MODE) && (
        <div className="max-w-7xl mx-auto px-6 py-2">
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-5 h-5 text-blue-400">⚡</div>
              <div>
                <p className="text-sm font-medium text-blue-300">
                  {DEMO_MODE ? 'Demo Mode - Optimized Loading' : 'Demo Mode Active'}
                </p>
                <p className="text-xs text-blue-400">
                  {DEMO_MODE 
                    ? 'Fast loading with demo data - no API delays'
                    : 'Some backend services offline - showcasing with demo data'
                  }
                </p>
                {lastUpdated && (
                  <p className="text-xs text-blue-500 mt-1">Last updated: {lastUpdated}</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">AI Dashboard</h1>
          <p className="text-sm text-gray-400">
            Monitor AI agent performance and system metrics • 
            {DEMO_MODE ? ' Demo Mode - Optimized Performance' : ' Real-time data'}
          </p>
        </div>

        <div className="flex items-center space-x-8 mb-8">
          {tabs.map((tab) => (
            <MotionButton
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white border border-blue-500/50 shadow-sm'
                  : 'text-gray-300 hover:text-white hover:bg-white/10 border border-white/20'
              }`}
            >
              {tab.icon}
              <span className="font-medium">{tab.label}</span>
            </MotionButton>
          ))}
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400" />
            <span className="ml-3 text-gray-300">Loading AI dashboard...</span>
          </div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <div className="space-y-8">
                
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="bg-gradient-to-br from-blue-600/20 to-indigo-600/20 border border-blue-500/30 rounded-xl p-6 text-white relative overflow-hidden backdrop-blur-sm shadow-sm">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
                    <div className="relative">
                      <div className="flex items-center justify-between mb-2">
                        <Brain className="w-8 h-8 text-blue-400" />
                        <span className="text-2xl font-bold">{dashboardData.realTimeMetrics.activeAgents}</span>
                      </div>
                      <p className="text-blue-200">AI Agents Active</p>
                      <p className="text-xs text-blue-300 mt-1">Knowledge • Task • Mentor • Guide</p>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-green-600/20 to-emerald-600/20 border border-green-500/30 rounded-xl p-6 text-white relative overflow-hidden backdrop-blur-sm shadow-sm">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
                    <div className="relative">
                      <div className="flex items-center justify-between mb-2">
                        <Code className="w-8 h-8 text-green-400" />
                        <span className="text-2xl font-bold">
                          {dashboardData.codeStats?.indexed_files || dashboardData.uploadStatus?.documents_indexed || 105}
                        </span>
                      </div>
                      <p className="text-green-200">Documents Indexed</p>
                      <p className="text-xs text-green-300 mt-1">
                        {dashboardData.codeStats?.status || dashboardData.uploadStatus?.vector_store_status || "Ready"}
                      </p>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-purple-600/20 to-pink-600/20 border border-purple-500/30 rounded-xl p-6 text-white relative overflow-hidden backdrop-blur-sm shadow-sm">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
                    <div className="relative">
                      <div className="flex items-center justify-between mb-2">
                        <Clock className="w-8 h-8 text-purple-400" />
                        <span className="text-2xl font-bold">{dashboardData.realTimeMetrics.responseTime}</span>
                      </div>
                      <p className="text-purple-200">Avg Response Time</p>
                      <p className="text-xs text-purple-300 mt-1">Optimized performance</p>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-amber-600/20 to-orange-600/20 border border-amber-500/30 rounded-xl p-6 text-white relative overflow-hidden backdrop-blur-sm shadow-sm">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
                    <div className="relative">
                      <div className="flex items-center justify-between mb-2">
                        <TrendingUp className="w-8 h-8 text-amber-400" />
                        <span className="text-2xl font-bold">97%</span>
                      </div>
                      <p className="text-amber-200">AI Confidence</p>
                      <p className="text-xs text-amber-300 mt-1">Average across all agents</p>
                    </div>
                  </div>
                </div>

                
                <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-semibold text-white flex items-center">
                      <Zap className="w-6 h-6 mr-2 text-blue-400" />
                      Live AI Agent Activity
                    </h3>
                    <div className="text-sm text-gray-400">
                      Last update: {getRelativeTime(dashboardData.realTimeMetrics.lastAgentActivity)}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {aiAgentStatus.map((agent, idx) => (
                      <div key={idx} className="bg-white/5 rounded-xl p-4 border border-white/10 shadow-sm">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-2">
                            <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
                              {agent.icon}
                            </div>
                            <div className={`w-2 h-2 rounded-full ${agent.status === 'active' ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
                          </div>
                          <span className="text-xs text-gray-400">{agent.lastResponse}</span>
                        </div>
                        <h4 className="font-medium text-white mb-2">{agent.realName}</h4>
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-400">Status</span>
                            <span className={agent.status === 'active' ? 'text-green-400' : 'text-red-400'}>
                              {agent.status}
                            </span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-400">Confidence</span>
                            <span className="text-green-400">{agent.confidence}%</span>
                          </div>
                          <div className="w-full bg-gray-700 rounded-full h-1.5">
                            <div 
                              className="bg-green-400 h-1.5 rounded-full transition-all duration-500" 
                              style={{ width: `${agent.confidence}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                
                <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
                  <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
                    <MessageSquare className="w-6 h-6 mr-2 text-green-400" />
                    Latest AI Insights
                  </h3>
                  
                  <div className="space-y-4">
                    {dashboardData.taskSuggestion && (
                      <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4">
                        <div className="flex items-start space-x-3">
                          <div className="p-2 bg-blue-500/20 rounded-lg">
                            <Target className="w-4 h-4 text-blue-400" />
                          </div>
                          <div className="flex-1">
                            <h4 className="font-medium text-blue-300 mb-1">Task Agent Suggestion</h4>
                            <p className="text-sm text-blue-200">
                              {dashboardData.taskSuggestion.task || "Ready to provide personalized recommendations"}
                            </p>
                            <span className="text-xs text-blue-400 mt-2 block">Generated just now</span>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-4">
                      <div className="flex items-start space-x-3">
                        <div className="p-2 bg-green-500/20 rounded-lg">
                          <BookOpen className="w-4 h-4 text-green-400" />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-medium text-green-300 mb-1">Knowledge Agent Analysis</h4>
                          <p className="text-sm text-green-200">
                            Processed {dashboardData.codeStats?.indexed_files || 105} documents - Knowledge base optimized
                          </p>
                          <span className="text-xs text-green-400 mt-2 block">
                            {dashboardData.codeStats?.status || "Ready"}
                            {DEMO_MODE && " • Demo Mode"}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'agents' && (
              <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
                <h3 className="text-xl font-semibold text-white mb-6">Live AI Agent Status</h3>
                <div className="text-gray-300">
                  Real-time agent monitoring dashboard...
                  <br />Your {dashboardData.realTimeMetrics.activeAgents} AI agents are active and optimized!
                </div>
              </div>
            )}

            {activeTab === 'analytics' && (
              <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
                <h3 className="text-xl font-semibold text-white mb-6">Performance Analytics</h3>
                <div className="text-gray-300">
                  Performance metrics dashboard showing optimized response times and AI accuracy.
                  <br />Average response time: {dashboardData.realTimeMetrics.responseTime}
                </div>
              </div>
            )}

            {activeTab === 'knowledge' && (
              <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
                <h3 className="text-xl font-semibold text-white mb-6">Knowledge Base Status</h3>
                <div className="text-gray-300">
                  Knowledge base with {dashboardData.codeStats?.indexed_files || 105} documents indexed and optimized.
                  <br />Vector embeddings ready for intelligent search and analysis.
                  <br />Status: {dashboardData.codeStats?.status || "ready"}
                  {DEMO_MODE && <span className="text-blue-400"> • Demo Mode - Optimized</span>}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}