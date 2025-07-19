import React, { useState, useEffect } from 'react';
import { 
  ArrowRight, MessageSquare, TrendingUp, Target, Database, 
  CheckCircle, Code, Globe, Brain, Shield, Send, Sparkles,
  Play, Zap, Bell, User, Settings, Menu,
  Palette, LogOut, UserCircle, Users, AlertCircle
} from 'lucide-react';

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
  showNotifications?: boolean
}


const NavigationHeader = ({ title, subtitle, showNotifications = true }: NavigationHeaderProps) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showNotificationsDropdown, setShowNotificationsDropdown] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  
  useEffect(() => {
    const handleClickOutside = () => {
      setShowNotificationsDropdown(false);
      setShowSettings(false);
      setShowUserMenu(false);
    };
    
    if (showNotificationsDropdown || showSettings || showUserMenu) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showNotificationsDropdown, showSettings, showUserMenu]);

  const notifications = [
    {
      id: 1,
      title: 'Welcome to ZeroDay',
      message: 'Your AI-powered onboarding platform is ready',
      time: new Date(Date.now() - 2 * 60 * 1000),
      type: 'success'
    },
    {
      id: 2,
      title: 'System Status Update',
      message: 'All AI agents are online and processing requests',
      time: new Date(Date.now() - 8 * 60 * 1000),
      type: 'info'
    },
    {
      id: 3,
      title: 'Demo Available',
      message: 'Interactive demo ready with live scenarios',
      time: new Date(Date.now() - 15 * 60 * 1000),
      type: 'warning'
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
            <a href="/" className="text-blue-400 font-medium text-sm">Home</a>
            <a href="/chat" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">AI Chat</a>
            <a href="/dashboard" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Dashboard</a>
            <a href="/tasks" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Tasks</a>
            <a href="/upload" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Upload</a>
          </div>

          
          <div className="flex items-center space-x-3">
            
            <div className="relative">
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  setShowSettings(!showSettings);
                  setShowNotificationsDropdown(false);
                  setShowUserMenu(false);
                }}
                className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-white/10"
              >
                <Settings className="w-5 h-5" />
              </button>
              
              {showSettings && (
                <div className="absolute right-0 top-full mt-2 w-56 bg-gray-900/80 backdrop-blur-md border border-white/20 rounded-xl p-2 z-50 shadow-lg">
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

            
            {showNotifications && (
              <div className="relative">
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowNotificationsDropdown(!showNotificationsDropdown);
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
            )}

            
            <div className="relative">
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  setShowUserMenu(!showUserMenu);
                  setShowNotificationsDropdown(false);
                  setShowSettings(false);
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
              <a href="/" className="text-blue-400 py-2 px-2 rounded-lg bg-blue-500/10">Home</a>
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

export default function IndexPage() {
  const [chatInput, setChatInput] = useState('');
  const [systemStatus, setSystemStatus] = useState({
    backendConnected: false,
    vectorStoreReady: false,
    documentsIndexed: 0,
    agentsAvailable: 0
  });
  const [aiMetrics, setAiMetrics] = useState({
    activeAgents: 0,
    responseTime: '0.0s'
  });
  const [systemHealth, setSystemHealth] = useState('checking');
  const [lastUpdated, setLastUpdated] = useState<string>("");
  
  useEffect(() => {
    setLastUpdated(new Date().toLocaleString());
  }, []);

  
  useEffect(() => {
    const checkSystemStatus = async () => {
      try {
        
        const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const [healthResponse, agentsResponse, uploadResponse] = await Promise.all([
            fetch(`${API_BASE}/health/`),
            fetch(`${API_BASE}/agents`),
            fetch(`${API_BASE}/api/upload/status`)
        ]);
        
        console.log('Health response:', healthResponse.status);
        console.log('Agents response:', agentsResponse.status);
        console.log('Upload response:', uploadResponse.status);

        let healthData = null;
        let agentsData = null;
        let uploadData = null;

        if (healthResponse.ok) {
          healthData = await healthResponse.json();
          console.log('Health data:', healthData);
        }

        if (agentsResponse.ok) {
          agentsData = await agentsResponse.json();
          console.log('Agents data:', agentsData);
        }

        if (uploadResponse.ok) {
          uploadData = await uploadResponse.json();
          console.log('Upload data:', uploadData);
        }
        
        
        let activeAgentCount = 0;
        if (agentsData) {
          
          activeAgentCount = Object.values(agentsData).filter(
            (agent: any) => agent && agent.available === true
          ).length;
        }

        setSystemStatus({
          backendConnected: healthResponse.ok,
          vectorStoreReady: uploadData?.vector_store_status === 'ready' || uploadData?.documents_indexed > 0,
          documentsIndexed: uploadData?.documents_indexed || 0,
          agentsAvailable: activeAgentCount
        });

        setAiMetrics({
          activeAgents: activeAgentCount,
          responseTime: '1.2s'
        });

        
        if (healthResponse.ok && activeAgentCount >= 4) {
          setSystemHealth('excellent');
        } else if (healthResponse.ok && activeAgentCount >= 2) {
          setSystemHealth('good');
        } else if (healthResponse.ok) {
          setSystemHealth('fair');
        } else {
          setSystemHealth('poor');
        }

      } catch (error) {
        console.error('Failed to check system status:', error);
        setSystemHealth('poor');
        
       
        setSystemStatus({
          backendConnected: false,
          vectorStoreReady: false,
          documentsIndexed: 0,
          agentsAvailable: 0
        });
      }
    };

    checkSystemStatus();
    
   
    const interval = setInterval(checkSystemStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleStartDemo = () => {
    window.location.href = '/demo';
  };

  const handleFormSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (chatInput.trim()) {
      window.location.href = `/chat?q=${encodeURIComponent(chatInput)}`;
    }
  };

  const handleButtonClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (chatInput.trim()) {
      window.location.href = `/chat?q=${encodeURIComponent(chatInput)}`;
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (chatInput.trim()) {
        window.location.href = `/chat?q=${encodeURIComponent(chatInput)}`;
      }
    }
  };

  const handleQuickPrompt = (prompt: string) => {
    setChatInput(prompt);
  };

  const quickPrompts = [
    "Show me the codebase overview",
    "What tasks should I work on?", 
    "Help me with React best practices",
    "Generate a learning plan"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <NavigationHeader
        title="ZeroDay"
        subtitle="Enterprise AI Developer Onboarding Platform"
        showNotifications={true}
      />

      <div className="max-w-7xl mx-auto px-6 py-6">
       
        <div className="mb-8">
          <div className="text-center mb-16">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              AI-Powered
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent"> Developer</span>
              <br />Onboarding
            </h1>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-8">
              Transform how developers join your team with 4 specialized AI agents that provide 
              instant context, personalized guidance, and intelligent task recommendations.
            </p>
            
            <div className="flex flex-col sm:flex-row justify-center gap-4 mb-12">
              <button
                onClick={handleStartDemo}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:shadow-lg transition-all duration-300 flex items-center justify-center space-x-2 hover:from-blue-700 hover:to-indigo-700 shadow-sm"
              >
                <Play className="w-5 h-5" />
                <span>Start Demo</span>
              </button>
              
              <button 
                onClick={() => window.location.href = '/chat'}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 px-8 py-4 rounded-xl text-lg font-semibold hover:shadow-lg transition-all duration-300 flex items-center justify-center space-x-2 shadow-sm"
              >
                <MessageSquare className="w-5 h-5" />
                <span>Try AI Chat</span>
              </button>
            </div>
          </div>
        </div>

        
        <div className="max-w-4xl mx-auto mb-8">
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-2 border border-white/10 shadow-sm overflow-hidden">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-4">
              <div className="flex items-center space-x-3">
                <div className="flex space-x-1">
                  <div className="w-3 h-3 bg-white/30 rounded-full"></div>
                  <div className="w-3 h-3 bg-white/30 rounded-full"></div>
                  <div className="w-3 h-3 bg-white/30 rounded-full"></div>
                </div>
                <h3 className="text-white font-semibold">ZeroDay AI Chat</h3>
                <div className="flex items-center space-x-2 ml-auto">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-white text-sm">{aiMetrics.activeAgents} AI Agents Active</span>
                </div>
              </div>
            </div>
            
            <div className="p-6">
              <div className="space-y-4 mb-6">
                <div className="flex items-start space-x-3">
                  <div className="bg-blue-500/20 p-2 rounded-lg">
                    <Brain className="w-5 h-5 text-blue-400" />
                  </div>
                  <div className="bg-white/5 rounded-lg p-3 flex-1 border border-white/10">
                    <p className="text-gray-300">👋 Hi! I'm your ZeroDay AI assistant. I have 4 specialized agents ready to help:</p>
                    <div className="mt-2 space-y-1 text-sm">
                      <p className="text-gray-400">🔍 <strong className="text-white">Knowledge Agent</strong> - Search code & documentation</p>
                      <p className="text-gray-400">🎯 <strong className="text-white">Task Agent</strong> - Get personalized task suggestions</p>
                      <p className="text-gray-400">👥 <strong className="text-white">Mentor Agent</strong> - Senior developer guidance</p>
                      <p className="text-gray-400">📚 <strong className="text-white">Guide Agent</strong> - Learning path generation</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <form onSubmit={handleFormSubmit}>
                  <div className="relative">
                    <input
                      type="text"
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      placeholder="Ask me anything about your codebase, get task suggestions, or request guidance..."
                      className="w-full px-4 py-3 pr-12 bg-white/10 border border-white/20 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white placeholder-gray-400"
                      onKeyDown={handleKeyPress}
                    />
                    <button
                      type="submit"
                      onClick={handleButtonClick}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                </form>

                <div className="flex flex-wrap gap-2">
                  {quickPrompts.map((prompt, index) => (
                    <button
                      key={index}
                      onClick={() => handleQuickPrompt(prompt)}
                      className="bg-blue-500/20 text-blue-300 px-3 py-1 rounded-full text-sm hover:bg-blue-500/30 transition-colors border border-blue-500/30"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

       
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
            <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
              <Sparkles className="w-8 h-8 mr-3 text-blue-400" />
              Experience the Platform
            </h3>

            <div className="space-y-4">
              <div
                onClick={() => window.location.href = '/chat'}
                className={`group p-4 rounded-xl transition-all duration-300 flex items-center justify-between cursor-pointer ${
                  systemStatus.backendConnected 
                    ? 'bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 hover:from-blue-600/30 hover:to-purple-600/30' 
                    : 'bg-gray-700/20 border border-gray-600/30 cursor-not-allowed opacity-50'
                }`}
              >
                <div className="flex items-center space-x-4">
                  <MessageSquare className="w-6 h-6 text-blue-400" />
                  <div>
                    <div className="text-white font-semibold">AI Chat Interface</div>
                    <div className="text-gray-300 text-sm">Real-time conversations with AI agents</div>
                  </div>
                </div>
                <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-white group-hover:translate-x-1 transition-all" />
              </div>

              <div
                onClick={() => window.location.href = '/dashboard'}
                className="group p-4 rounded-xl bg-gradient-to-r from-indigo-600/20 to-blue-600/20 border border-indigo-500/30 hover:from-indigo-600/30 hover:to-blue-600/30 transition-all duration-300 flex items-center justify-between cursor-pointer"
              >
                <div className="flex items-center space-x-4">
                  <TrendingUp className="w-6 h-6 text-indigo-400" />
                  <div>
                    <div className="text-white font-semibold">Analytics Dashboard</div>
                    <div className="text-gray-300 text-sm">Live performance metrics and insights</div>
                  </div>
                </div>
                <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-white group-hover:translate-x-1 transition-all" />
              </div>

              <div
                onClick={() => window.location.href = '/tasks'}
                className="group p-4 rounded-xl bg-gradient-to-r from-orange-600/20 to-red-600/20 border border-orange-500/30 hover:from-orange-600/30 hover:to-red-600/30 transition-all duration-300 flex items-center justify-between cursor-pointer"
              >
                <div className="flex items-center space-x-4">
                  <Target className="w-6 h-6 text-orange-400" />
                  <div>
                    <div className="text-white font-semibold">Smart Task Generation</div>
                    <div className="text-gray-300 text-sm">AI-powered personalized learning tasks</div>
                  </div>
                </div>
                <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-white group-hover:translate-x-1 transition-all" />
              </div>

              <div
                onClick={() => window.location.href = '/upload'}
                className="group p-4 rounded-xl bg-gradient-to-r from-green-600/20 to-teal-600/20 border border-green-500/30 hover:from-green-600/30 hover:to-teal-600/30 transition-all duration-300 flex items-center justify-between cursor-pointer"
              >
                <div className="flex items-center space-x-4">
                  <Database className="w-6 h-6 text-green-400" />
                  <div>
                    <div className="text-white font-semibold">Data Management</div>
                    <div className="text-gray-300 text-sm">Intelligent document processing</div>
                  </div>
                </div>
                <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-white group-hover:translate-x-1 transition-all" />
              </div>
            </div>
          </div>

          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-white flex items-center">
                <Shield className="w-8 h-8 mr-3 text-green-400" />
                Live System Status
              </h3>
              <div className={`px-3 py-1 rounded-full text-xs font-bold ${
                systemHealth === 'excellent' ? 'bg-green-500/20 text-green-300 border border-green-500/30' :
                systemHealth === 'good' ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30' :
                'bg-red-500/20 text-red-300 border border-red-500/30'
              }`}>
                {systemHealth.toUpperCase()}
              </div>
            </div>

            <div className="space-y-4 mb-8">
              <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                <span className="text-gray-300 font-medium">Backend API</span>
                <div className="flex items-center space-x-2">
                  {systemStatus.backendConnected ? (
                    <CheckCircle className="w-5 h-5 text-green-400" />
                  ) : (
                    <div className="w-5 h-5 border-2 border-red-400 rounded-full" />
                  )}
                  <span className={systemStatus.backendConnected ? 'text-green-400' : 'text-red-400'}>
                    {systemStatus.backendConnected ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                <span className="text-gray-300 font-medium">Knowledge Base</span>
                <div className="flex items-center space-x-2">
                  {systemStatus.vectorStoreReady ? (
                    <CheckCircle className="w-5 h-5 text-green-400" />
                  ) : (
                    <div className="w-5 h-5 border-2 border-yellow-400 rounded-full" />
                  )}
                  <span className={systemStatus.vectorStoreReady ? 'text-green-400' : 'text-yellow-400'}>
                    {systemStatus.documentsIndexed} Documents
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                <span className="text-gray-300 font-medium">AI Agents</span>
                <span className="text-blue-400 font-bold">
                  {aiMetrics.activeAgents}/4 Active
                </span>
              </div>
            </div>

            {systemHealth === 'excellent' && (
              <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  <span className="text-green-300 font-semibold">Platform Ready</span>
                </div>
                <p className="text-green-200 text-sm">
                  All systems operational. Ready for enterprise deployment.
                </p>
              </div>
            )}

            {!systemStatus.backendConnected && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
                <p className="text-red-300 text-sm mb-2">
                  Start the backend to see full functionality:
                </p>
                <code className="text-red-200 text-xs bg-red-900/30 p-2 rounded block font-mono">
                  Reload the agents
                </code>
              </div>
            )}
          </div>
        </div>

       
        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
          <h3 className="text-xl font-semibold text-white mb-6 text-center">
            Enterprise Technology Stack
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center group">
              <div className="bg-blue-500/20 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:bg-blue-500/30 transition-colors">
                <Code className="w-8 h-8 text-blue-400" />
              </div>
              <div className="text-white font-bold text-lg">FastAPI</div>
              <div className="text-gray-400 text-sm">Python Backend</div>
            </div>
            <div className="text-center group">
              <div className="bg-green-500/20 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:bg-green-500/30 transition-colors">
                <Database className="w-8 h-8 text-green-400" />
              </div>
              <div className="text-white font-bold text-lg">ChromaDB</div>
              <div className="text-gray-400 text-sm">Vector Store</div>
            </div>
            <div className="text-center group">
              <div className="bg-purple-500/20 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:bg-purple-500/30 transition-colors">
                <Globe className="w-8 h-8 text-purple-400" />
              </div>
              <div className="text-white font-bold text-lg">Next.js</div>
              <div className="text-gray-400 text-sm">React Frontend</div>
            </div>
            <div className="text-center group">
              <div className="bg-orange-500/20 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:bg-orange-500/30 transition-colors">
                <Brain className="w-8 h-8 text-orange-400" />
              </div>
              <div className="text-white font-bold text-lg">Multi-Agent AI</div>
              <div className="text-gray-400 text-sm">Specialized Agents</div>
            </div>
          </div>
          <div className="mt-6 text-center">
            <p className="text-gray-400">
              TypeScript • Tailwind CSS • Real-time Processing • Enterprise Architecture
            </p>
            {lastUpdated && (
              <p className="text-gray-500 text-sm mt-2">
                Last updated: {lastUpdated}
              </p>
            )} 
          </div>
        </div>
      </div>
    </div>
  );
}