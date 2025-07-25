import React, { useState, useEffect } from 'react';
import { 
  Database, Brain, Server, Layers, Bell, User, Menu, Settings, Globe, Code, MessageSquare, Target,
  Palette, Shield, LogOut, UserCircle, CheckCircle, AlertCircle, Users
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
      title: 'System Architecture Updated',
      message: 'New AI agent endpoints have been deployed',
      time: new Date(Date.now() - 10 * 60 * 1000),
      type: 'success'
    },
    {
      id: 2,
      title: 'Database Optimization',
      message: 'Vector database performance improved by 40%',
      time: new Date(Date.now() - 25 * 60 * 1000),
      type: 'info'
    },
    {
      id: 3,
      title: 'Agent Performance Alert',
      message: 'Knowledge agent response time increased',
      time: new Date(Date.now() - 45 * 60 * 1000),
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
                      View system status
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

const ArchitecturePage = () => {
  const architectureComponents = [
    {
      title: 'Frontend',
      description: 'Next.js with React',
      icon: <Layers className="w-8 h-8" />,
      color: 'bg-gradient-to-r from-blue-600 to-indigo-600',
      details: 'TypeScript • Tailwind CSS • Framer Motion • SWR'
    },
    {
      title: 'Backend',
      description: 'FastAPI Python',
      icon: <Server className="w-8 h-8" />,
      color: 'bg-gradient-to-r from-green-600 to-emerald-600',
      details: 'RESTful APIs • Async Operations • CORS Enabled'
    },
    {
      title: 'AI Agents',
      description: '4 Specialized Agents',
      icon: <Brain className="w-8 h-8" />,
      color: 'bg-gradient-to-r from-purple-600 to-pink-600',
      details: 'Knowledge • Task • Mentor • Guide Agents'
    },
    {
      title: 'Database',
      description: 'ChromaDB Vector Store',
      icon: <Database className="w-8 h-8" />,
      color: 'bg-gradient-to-r from-orange-600 to-red-600',
      details: 'Vector Embeddings • Document Search • Real-time'
    }
  ];

  const agentDetails = [
    {
      name: 'Knowledge Agent',
      description: 'Code search & documentation',
      icon: <Code className="w-6 h-6 text-blue-400" />,
      endpoints: ['/api/query/code/search_code', '/api/query/code/explain_code'],
      capabilities: ['Code Search', 'Documentation Lookup', 'Function Analysis']
    },
    {
      name: 'Task Agent',
      description: 'Personalized task recommendations',
      icon: <Target className="w-6 h-6 text-orange-400" />,
      endpoints: ['/api/suggest_task', '/api/quick_task'],
      capabilities: ['Task Generation', 'Skill Assessment', 'Progress Tracking']
    },
    {
      name: 'Mentor Agent',
      description: 'Senior developer guidance',
      icon: <MessageSquare className="w-6 h-6 text-purple-400" />,
      endpoints: ['/api/ask_mentor', '/api/mentor_stats'],
      capabilities: ['Code Review', 'Best Practices', 'Troubleshooting']
    },
    {
      name: 'Guide Agent',
      description: 'Learning path generation',
      icon: <Globe className="w-6 h-6 text-green-400" />,
      endpoints: ['/api/generate_plan', '/api/customized_plan'],
      capabilities: ['Learning Plans', 'Curriculum Design', 'Progress Monitoring']
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <NavigationHeader
        title="System Architecture"
        subtitle="Technical overview of the ZeroDay AI platform"
        isDemo={true}
      />

      <div className="max-w-7xl mx-auto px-6 py-6">
      
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">System Architecture</h1>
          <p className="text-sm text-gray-400">Technical overview of the ZeroDay AI platform</p>
        </div>

        
        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm mb-8">
          <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
            <Layers className="w-6 h-6 mr-3 text-blue-400" />
            Platform Architecture
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {architectureComponents.map((component, index) => (
              <div
                key={component.title}
                className={`${component.color} rounded-xl p-6 text-white relative overflow-hidden shadow-sm`}
              >
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
                <div className="relative">
                  <div className="flex items-center justify-between mb-4">
                    {component.icon}
                  </div>
                  <h3 className="font-bold text-white text-lg mb-2">{component.title}</h3>
                  <p className="text-white/80 text-sm mb-3">{component.description}</p>
                  <p className="text-white/60 text-xs">{component.details}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

       
        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm mb-8">
          <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
            <Brain className="w-6 h-6 mr-3 text-purple-400" />
            AI Agents Architecture
          </h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {agentDetails.map((agent, index) => (
              <div
                key={agent.name}
                className="bg-white/5 rounded-xl p-6 border border-white/10 shadow-sm"
              >
                <div className="flex items-center space-x-3 mb-4">
                  <div className="p-2 bg-white/10 rounded-lg">
                    {agent.icon}
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-lg">{agent.name}</h3>
                    <p className="text-sm text-gray-400">{agent.description}</p>
                  </div>
                </div>
                
                <div className="mb-4">
                  <h4 className="text-white font-semibold text-sm mb-2">API Endpoints:</h4>
                  <div className="space-y-1">
                    {agent.endpoints.map((endpoint, idx) => (
                      <code key={idx} className="block text-xs bg-black/20 text-blue-300 px-2 py-1 rounded">
                        {endpoint}
                      </code>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h4 className="text-white font-semibold text-sm mb-2">Capabilities:</h4>
                  <div className="flex flex-wrap gap-2">
                    {agent.capabilities.map((capability, idx) => (
                      <span 
                        key={idx}
                        className="text-xs bg-white/10 text-gray-300 px-2 py-1 rounded-full border border-white/20"
                      >
                        {capability}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        
        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
          <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
            <Server className="w-6 h-6 mr-3 text-green-400" />
            Technical Specifications
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-white/5 rounded-xl p-6 border border-white/10 shadow-sm">
              <h3 className="font-bold text-white text-lg mb-4">Frontend Stack</h3>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• Next.js 13+ (App Router)</li>
                <li>• React 18 with Hooks</li>
                <li>• TypeScript for type safety</li>
                <li>• Tailwind CSS for styling</li>
                <li>• Framer Motion for animations</li>
                <li>• SWR for data fetching</li>
              </ul>
            </div>
            
            <div className="bg-white/5 rounded-xl p-6 border border-white/10 shadow-sm">
              <h3 className="font-bold text-white text-lg mb-4">Backend Stack</h3>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• FastAPI (Python 3.9+)</li>
                <li>• Async/Await operations</li>
                <li>• Pydantic for validation</li>
                <li>• CORS middleware enabled</li>
                <li>• RESTful API design</li>
                <li>• Auto-generated docs</li>
              </ul>
            </div>
            
            <div className="bg-white/5 rounded-xl p-6 border border-white/10 shadow-sm">
              <h3 className="font-bold text-white text-lg mb-4">Data & AI</h3>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• ChromaDB vector database</li>
                <li>• OpenAI embeddings</li>
                <li>• Real-time processing</li>
                <li>• Document indexing</li>
                <li>• Semantic search</li>
                <li>• Multi-agent orchestration</li>
              </ul>
            </div>
          </div>
          
          <div className="mt-8 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-xl p-6 border border-blue-500/20">
            <h3 className="font-bold text-white text-lg mb-4">Deployment & Infrastructure</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-blue-400 font-semibold mb-2">Development</h4>
                <ul className="space-y-1 text-gray-300 text-sm">
                  <li>• Local development with hot reload</li>
                  <li>• Frontend: localhost:3000</li>
                  <li>• Backend: localhost:8000</li>
                  <li>• Auto API documentation</li>
                </ul>
              </div>
              <div>
                <h4 className="text-purple-400 font-semibold mb-2">Production Ready</h4>
                <ul className="space-y-1 text-gray-300 text-sm">
                  <li>• Docker containerization</li>
                  <li>• Environment configurations</li>
                  <li>• Health check endpoints</li>
                  <li>• Scalable architecture</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArchitecturePage;