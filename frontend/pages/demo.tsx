import React, { useState, useEffect } from 'react';
import { 
  Play, CheckCircle, Bell, User, Menu, Settings, Brain,
  Palette, Shield, LogOut, UserCircle, Users, AlertCircle, MessageSquare
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
  title: string;
  subtitle?: string;
  isDemo?: boolean;
};

type DemoScenario = {
  id: string;
  name: string;
  company_type: string;
  team_size: number;
  industry: string;
  user_profile: {
    name: string;
    role: string;
    experience: string;
  };
  tech_stack: string[];
};

const NavigationHeader = ({ title, subtitle, isDemo = false }: NavigationHeaderProps) => {
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
      title: 'Demo Environment Ready',
      message: 'All scenarios loaded and AI agents are active',
      time: new Date(Date.now() - 1 * 60 * 1000),
      type: 'success'
    },
    {
      id: 2,
      title: 'Live Data Available',
      message: 'Real-time demo data synchronized successfully',
      time: new Date(Date.now() - 5 * 60 * 1000),
      type: 'info'
    },
    {
      id: 3,
      title: 'Demo Session Started',
      message: 'Interactive demo mode activated for new users',
      time: new Date(Date.now() - 12 * 60 * 1000),
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

export default function DemoPage() {
  const [scenarios, setScenarios] = useState<DemoScenario[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<string>('startup');
  const [currentScenario, setCurrentScenario] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [backendConnected, setBackendConnected] = useState(false);
  const [demoData, setDemoData] = useState<any>(null);

  const predefinedScenarios: DemoScenario[] = [
    {
      id: 'startup',
      name: 'TechStartup Inc',
      company_type: 'early_stage_startup',
      team_size: 12,
      industry: 'fintech',
      user_profile: {
        name: 'Sarah Chen',
        role: 'Senior Full Stack Developer',
        experience: '3 years'
      },
      tech_stack: ['React', 'Node.js', 'Python', 'PostgreSQL']
    },
    {
      id: 'enterprise',
      name: 'Enterprise Solutions Corp',
      company_type: 'large_enterprise',
      team_size: 250,
      industry: 'healthcare',
      user_profile: {
        name: 'Marcus Rodriguez',
        role: 'Senior Software Engineer',
        experience: '7 years'
      },
      tech_stack: ['Java', 'Spring Boot', 'Oracle', 'Kubernetes']
    },
    {
      id: 'freelancer',
      name: 'Independent Developer',
      company_type: 'freelancer',
      team_size: 1,
      industry: 'web_development',
      user_profile: {
        name: 'Alex Thompson',
        role: 'Full Stack Developer',
        experience: '5 years'
      },
      tech_stack: ['Vue.js', 'Laravel', 'MySQL', 'AWS']
    }
  ];

  
  useEffect(() => {
    const loadDemoScenarios = async () => {
      try {
        console.log('🔄 Loading demo scenarios from API...');
        const response = await fetch('http://127.0.0.1:8000/demo/scenarios');
        
        if (response.ok) {
          const data = await response.json();
          console.log(' Demo scenarios loaded:', data);
          setBackendConnected(true);
          
          
          const transformedScenarios = Array.isArray(data) ? data.map((scenario: any) => ({
            id: scenario.id,
            name: scenario.name,
            company_type: scenario.company_type,
            team_size: scenario.team_size,
            industry: scenario.industry,
            user_profile: {
              name: scenario.user_profile?.name || 'Demo User',
              role: scenario.user_profile?.role || 'Developer',
              experience: scenario.user_profile?.experience || 'intermediate'
            },
            tech_stack: Array.isArray(scenario.tech_stack) ? scenario.tech_stack : 
                        typeof scenario.tech_stack === 'string' ? scenario.tech_stack.split(', ') :
                        ['React', 'Node.js', 'PostgreSQL']
          })) : predefinedScenarios;
          
          setScenarios(transformedScenarios);
          setCurrentScenario(transformedScenarios[0]);
          setSelectedScenario(transformedScenarios[0].id);
        } else {
          console.log(' Demo API not available, using predefined scenarios');
          setBackendConnected(false);
          setScenarios(predefinedScenarios);
          setCurrentScenario(predefinedScenarios[0]);
        }
      } catch (error) {
        console.error(' Failed to load demo scenarios:', error);
        setBackendConnected(false);
        setScenarios(predefinedScenarios);
        setCurrentScenario(predefinedScenarios[0]);
      }
    };

    loadDemoScenarios();
  }, []);

  
  useEffect(() => {
    const loadDemoData = async () => {
      if (!selectedScenario || !backendConnected) return;
      
      try {
        console.log(` Loading demo data for scenario: ${selectedScenario}`);
        
        // Load demo analytics, tasks, and chat messages
        const [analyticsRes, tasksRes, chatRes] = await Promise.all([
          fetch(`http://127.0.0.1:8000/demo/analytics/${selectedScenario}`),
          fetch(`http://127.0.0.1:8000/demo/tasks/${selectedScenario}`),
          fetch(`http://127.0.0.1:8000/demo/chat/messages/${selectedScenario}`)
        ]);

        const demoInfo: any = {};

        if (analyticsRes.ok) {
          demoInfo.analytics = await analyticsRes.json();
        }
        if (tasksRes.ok) {
          demoInfo.tasks = await tasksRes.json();
        }
        if (chatRes.ok) {
          demoInfo.chatMessages = await chatRes.json();
        }

        setDemoData(demoInfo);
        console.log(' Demo data loaded:', demoInfo);
      } catch (error) {
        console.error(' Failed to load demo data:', error);
      }
    };

    loadDemoData();
  }, [selectedScenario, backendConnected]);

  
  useEffect(() => {
    const scenario = scenarios.find(s => s.id === selectedScenario);
    setCurrentScenario(scenario);
  }, [selectedScenario, scenarios]);

  const handleScenarioSelect = (scenarioId: string) => {
    setSelectedScenario(scenarioId);
  };

  const handleStartDemo = async () => {
    setLoading(true);
    
    try {
      
      const healthCheck = await fetch('http://127.0.0.1:8000/health');
      
      if (healthCheck.ok) {
        console.log('✅ Backend is ready, starting demo with scenario:', selectedScenario);
      } else {
        console.log('⚠️ Backend not available, starting demo in offline mode');
      }
    } catch (error) {
      console.log('⚠️ Starting demo in offline mode');
    }
    
   
    setTimeout(() => {
      const scenarioName = encodeURIComponent(currentScenario?.name || 'Demo');
      window.location.href = `/dashboard?demo=${selectedScenario}&scenario=${scenarioName}`;
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <NavigationHeader
        title="ZeroDay Demo"
        subtitle={backendConnected ? 
          "Live demo with real AI agents and dynamic data" : 
          "Interactive demo with sample scenarios"
        }
        isDemo={true}
      />

      <div className="max-w-7xl mx-auto px-6 py-6">
        
        <div className="mb-8">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <h1 className="text-3xl font-bold text-white">Interactive Demo</h1>
            <div className={`px-3 py-1 rounded-full text-xs font-bold border animate-pulse ${
              backendConnected 
                ? 'bg-green-400/20 text-green-300 border-green-400/30' 
                : 'bg-yellow-400/20 text-yellow-300 border-yellow-400/30'
            }`}>
              {backendConnected ? '🚀 LIVE' : '📱 DEMO'}
            </div>
          </div>
          <p className="text-xl text-gray-300 text-center">
            {backendConnected ? 
              'Experience ZeroDay with live AI agents and real demo data' :
              'Choose a scenario and explore ZeroDay\'s AI-powered onboarding platform'
            }
          </p>
          {backendConnected && demoData && (
            <div className="mt-4 flex justify-center space-x-6 text-sm">
              {demoData.analytics && (
                <div className="text-blue-400">
                  📊 {demoData.analytics.projects_in_progress || 0} Projects
                </div>
              )}
              {demoData.tasks && (
                <div className="text-green-400">
                  ✅ {Array.isArray(demoData.tasks) ? demoData.tasks.length : 0} Tasks
                </div>
              )}
              {demoData.chatMessages && (
                <div className="text-purple-400">
                  💬 {Array.isArray(demoData.chatMessages) ? demoData.chatMessages.length : 0} Messages
                </div>
              )}
            </div>
          )}
        </div>

        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">Choose Your Scenario</h2>
              {backendConnected && (
                <div className="bg-green-500/20 text-green-300 px-2 py-1 rounded text-xs border border-green-500/30">
                  Live Data
                </div>
              )}
            </div>
            <div className="space-y-4">
              {scenarios.map((scenario, index) => (
                <button
                  key={scenario.id}
                  onClick={() => handleScenarioSelect(scenario.id)}
                  className={`w-full text-left p-4 rounded-xl border-2 transition-all ${
                    selectedScenario === scenario.id
                      ? 'border-blue-500/50 bg-blue-600/20'
                      : 'border-white/20 hover:border-blue-400/50 bg-white/5'
                  }`}
                >
                  <h3 className="font-semibold text-white">{scenario.name}</h3>
                  <p className="text-sm text-gray-300">{scenario.industry} • {scenario.team_size} people</p>
                  <p className="text-sm text-blue-400 mt-1">{scenario.user_profile.role}</p>
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-6">
            {currentScenario && (
              <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
                <h3 className="text-xl font-semibold text-white mb-4">Scenario Details</h3>
                <div className="space-y-3">
                  <div>
                    <span className="text-sm font-medium text-gray-400">Company:</span>
                    <p className="text-white">{currentScenario.name}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-400">Your Role:</span>
                    <p className="text-white">{currentScenario.user_profile.role}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-400">Experience Level:</span>
                    <p className="text-white">{currentScenario.user_profile.experience}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-400">Team Size:</span>
                    <p className="text-white">{currentScenario.team_size} people</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-400">Industry:</span>
                    <p className="text-white">{currentScenario.industry}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-400">Tech Stack:</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {currentScenario.tech_stack?.map((tech: string, index: number) => (
                        <span
                          key={index}
                          className="bg-blue-500/20 text-blue-300 text-xs px-2 py-1 rounded-full border border-blue-500/30"
                        >
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                
                {backendConnected && demoData && (
                  <div className="mt-4 pt-4 border-t border-white/10">
                    <h4 className="text-sm font-semibold text-blue-300 mb-2">Live Demo Data Preview:</h4>
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      {demoData.analytics && (
                        <div className="bg-blue-500/10 p-2 rounded border border-blue-500/20">
                          <div className="text-blue-300">Projects Active</div>
                          <div className="text-white font-bold">{demoData.analytics.projects_in_progress || 0}</div>
                        </div>
                      )}
                      {demoData.tasks && Array.isArray(demoData.tasks) && (
                        <div className="bg-green-500/10 p-2 rounded border border-green-500/20">
                          <div className="text-green-300">Available Tasks</div>
                          <div className="text-white font-bold">{demoData.tasks.length}</div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
              <h3 className="text-xl font-semibold text-white mb-4">What You'll Experience</h3>
              <ul className="space-y-3 text-gray-300">
                <li className="flex items-start space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                  <span>AI chat with {backendConnected ? 'live' : 'contextual'} project knowledge</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                  <span>Interactive dashboard with {backendConnected ? 'real-time' : 'realistic'} metrics</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                  <span>Task management with {backendConnected ? 'live AI' : 'AI'} suggestions</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                  <span>Code analysis and documentation tools</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                  <span>Learning paths tailored to your role</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div className="text-center mb-8">
          <button
            onClick={handleStartDemo}
            disabled={loading}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:shadow-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 disabled:opacity-50 flex items-center justify-center space-x-2 mx-auto shadow-sm"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                <span>Starting Demo...</span>
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                <span>Start {backendConnected ? 'Live' : 'Demo'} Experience</span>
              </>
            )}
          </button>
          <p className="text-sm text-gray-400 mt-4">
            Takes 5-10 minutes • No registration required • {backendConnected ? 'Live AI platform' : 'Full demo'} access
          </p>
        </div>

        
        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
          <h3 className="text-xl font-semibold text-white mb-6 text-center">Demo Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-blue-500/20 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4 border border-blue-500/30">
                <Brain className="w-8 h-8 text-blue-400" />
              </div>
              <h4 className="font-semibold text-white mb-2">AI Agents</h4>
              <p className="text-gray-300 text-sm">
                Experience all 4 specialized AI agents {backendConnected ? 'with live responses' : 'in action'}
              </p>
            </div>
            <div className="text-center">
              <div className="bg-green-500/20 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4 border border-green-500/30">
                <CheckCircle className="w-8 h-8 text-green-400" />
              </div>
              <h4 className="font-semibold text-white mb-2">{backendConnected ? 'Live' : 'Real'} Data</h4>
              <p className="text-gray-300 text-sm">
                Interact with {backendConnected ? 'dynamic' : 'realistic'} project data and scenarios
              </p>
            </div>
            <div className="text-center">
              <div className="bg-purple-500/20 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4 border border-purple-500/30">
                <Play className="w-8 h-8 text-purple-400" />
              </div>
              <h4 className="font-semibold text-white mb-2">Full Access</h4>
              <p className="text-gray-300 text-sm">Complete platform experience with no limitations</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}