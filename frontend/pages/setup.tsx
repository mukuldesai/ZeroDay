import React, { useState, useEffect } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '${API_BASE}'
import { 
  Bell, User, Menu, Settings, Brain, ChevronRight, CheckCircle, Star, Target, Code, Users,
  Palette, Shield, LogOut, UserCircle, AlertCircle, MessageSquare
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
  isDemo?: boolean
}

interface AuthUser {
  name: string;
  email: string;
  role: string;
}

interface SetupData {
  role: string;
  experience: string;
  team: string;
  goals: string[];
  preferences: {
    learningStyle: string;
    timeCommitment: string;
    focusAreas: string[];
  };
}

interface DemoUser {
  id: string;
  name: string;
  role: string;
  experience: string;
  scenario: string;
}

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
      title: 'Setup Assistant Ready',
      message: 'Your personalized onboarding experience is being prepared',
      time: new Date(Date.now() - 1 * 60 * 1000),
      type: 'success'
    },
    {
      id: 2,
      title: 'Demo Scenarios Available',
      message: 'Multiple demo user profiles ready for testing',
      time: new Date(Date.now() - 5 * 60 * 1000),
      type: 'info'
    },
    {
      id: 3,
      title: 'Profile Customization',
      message: 'AI agents will be tailored to your role and experience',
      time: new Date(Date.now() - 10 * 60 * 1000),
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
            <a href="/demo" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Demo</a>
            <a href="/login" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Login</a>
            <a href="/setup" className="text-blue-400 font-medium text-sm">Setup</a>
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
                      className="flex items-center space-x-3 px-3 py-2 text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 rounded-lg transition-colors"
                    >
                      <Palette className="w-4 h-4" />
                      <span>Setup</span>
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
                    <h3 className="text-white font-semibold">Setup Notifications</h3>
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
                      View setup progress
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
                    <p className="text-sm font-medium text-white">Setting Up</p>
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
                      href="/demo"
                      className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                    >
                      <Users className="w-4 h-4" />
                      <span>Try Demo</span>
                    </a>
                    <button
                      onClick={() => window.location.href = '/login'}
                      className="flex items-center space-x-3 w-full px-3 py-2 text-red-300 hover:text-red-200 hover:bg-red-500/10 rounded-lg transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Exit Setup</span>
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
              <a href="/demo" className="text-gray-300 hover:text-white transition-colors py-2 px-2 rounded-lg hover:bg-white/10">Demo</a>
              <a href="/login" className="text-gray-300 hover:text-white transition-colors py-2 px-2 rounded-lg hover:bg-white/10">Login</a>
              <a href="/setup" className="text-blue-400 py-2 px-2 rounded-lg bg-blue-500/10">Setup</a>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};


const useAuth = () => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
      setIsAuthenticated(true);
    }
  }, []);

  return { user, isAuthenticated };
};

export default function SetupPage() {
  const [currentStep, setCurrentStep] = useState(0);
  const [setupData, setSetupData] = useState<SetupData>({
    role: '',
    experience: '',
    team: '',
    goals: [],
    preferences: {
      learningStyle: '',
      timeCommitment: '',
      focusAreas: []
    }
  });
  const [demoUsers, setDemoUsers] = useState<DemoUser[]>([]);
  const [selectedDemoUser, setSelectedDemoUser] = useState<string>('');
  const [isDemoMode, setIsDemoMode] = useState(false);
  const { user } = useAuth();
  
  const selectedUser = demoUsers.find((u) => u.id === selectedDemoUser);
  
  const steps = [
    { title: 'Mode Selection', key: 'mode' },
    { title: 'Role & Experience', key: 'role' },
    { title: 'Team & Goals', key: 'team' },
    { title: 'Learning Preferences', key: 'preferences' },
    { title: 'Complete Setup', key: 'complete' }
  ];

  const roles = [
    'Frontend Developer',
    'Backend Developer', 
    'Full Stack Developer',
    'DevOps Engineer',
    'Data Scientist',
    'Product Manager',
    'Designer',
    'QA Engineer'
  ];

  const experienceLevels = [
    { value: 'junior', label: 'Junior (0-2 years)' },
    { value: 'mid', label: 'Mid-level (2-5 years)' },
    { value: 'senior', label: 'Senior (5+ years)' },
    { value: 'lead', label: 'Lead/Principal (8+ years)' }
  ];

  const learningStyles = [
    { value: 'visual', label: 'Visual Learning', icon: '👁️' },
    { value: 'hands-on', label: 'Hands-on Practice', icon: '🛠️' },
    { value: 'reading', label: 'Reading Documentation', icon: '📚' },
    { value: 'collaborative', label: 'Collaborative Learning', icon: '👥' }
  ];

  const focusAreas = [
    'Frontend Development',
    'Backend APIs',
    'Database Design',
    'DevOps & Deployment',
    'Testing & QA',
    'Security Best Practices',
    'Performance Optimization',
    'Team Collaboration'
  ];

  useEffect(() => {
    const fetchDemoUsers = async () => {
      try {
        
        const response = await fetch('${API_BASE}/demo/scenarios');
        
        if (response.ok) {
          const scenarios = await response.json();
          console.log('Demo scenarios loaded:', scenarios);
          
          
          const apiUsers = Array.isArray(scenarios) ? scenarios.map((scenario: any) => ({
            id: scenario.id,
            name: `${scenario.user_profile?.name || 'Demo User'} (${scenario.name})`,
            role: scenario.user_profile?.role || 'Developer',
            experience: scenario.user_profile?.experience || 'intermediate',
            scenario: scenario.id
          })) : [];
          
          if (apiUsers.length > 0) {
            setDemoUsers(apiUsers);
            return;
          }
        }
      } catch (error) {
        console.error('Failed to fetch demo scenarios:', error);
      }
      
     
      const predefinedUsers = [
        { 
          id: 'startup', 
          name: 'Sarah Chen (TechStartup Inc)', 
          role: 'Senior Full Stack Developer', 
          experience: '3 years', 
          scenario: 'startup' 
        },
        { 
          id: 'enterprise', 
          name: 'Marcus Rodriguez (Enterprise Corp)', 
          role: 'Senior Software Engineer', 
          experience: '7 years', 
          scenario: 'enterprise' 
        },
        { 
          id: 'freelancer', 
          name: 'Alex Thompson (Independent)', 
          role: 'Full Stack Developer', 
          experience: '5 years', 
          scenario: 'freelancer' 
        }
      ];
      setDemoUsers(predefinedUsers);
    };

    fetchDemoUsers();
  }, []);

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = async () => {
    try {
      if (isDemoMode && selectedDemoUser) {
        
        const demoUser = demoUsers.find(u => u.id === selectedDemoUser);
        const scenarioParam = demoUser?.scenario || selectedDemoUser;
        const nameParam = encodeURIComponent(demoUser?.name || 'Demo User');
        
        window.location.href = `/dashboard?demo=${scenarioParam}&user=${nameParam}`;
        return;
      }

      
      try {
        const setupPayload = {
          name: user?.name || 'User',
          email: user?.email || 'user@example.com',
          role: setupData.role,
          experience_level: setupData.experience,
          team: setupData.team || 'Development Team',
          preferences: {
            ...setupData.preferences,
            goals: setupData.goals
          },
          demo_mode: false
        };

        console.log('Saving setup data:', setupPayload);

        const response = await fetch('${API_BASE}/api/users/setup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(setupPayload)
        });

        if (response.ok) {
          const result = await response.json();
          console.log('Setup saved successfully:', result);
          
          
          localStorage.setItem('setup_completed', 'true');
          localStorage.setItem('user_profile', JSON.stringify(setupPayload));
          
          window.location.href = '/dashboard';
        } else {
          const errorData = await response.json().catch(() => ({}));
          console.error('Setup API error:', errorData);
          throw new Error(errorData.detail || 'Setup failed');
        }
      } catch (apiError) {
        console.error('API setup failed, continuing with local setup:', apiError);
        
        
        const localSetup = {
          role: setupData.role,
          experience: setupData.experience,
          team: setupData.team,
          goals: setupData.goals,
          preferences: setupData.preferences,
          completed_at: new Date().toISOString()
        };
        
        localStorage.setItem('setup_completed', 'true');
        localStorage.setItem('user_profile', JSON.stringify(localSetup));
        
        window.location.href = '/dashboard';
      }
    } catch (error) {
      console.error('Setup completion failed:', error);
      
      
      localStorage.setItem('setup_completed', 'true');
      window.location.href = '/dashboard';
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="space-y-6">
            <div className="text-center mb-6">
              <h2 className="text-xl font-semibold text-white mb-2">Choose Your Experience</h2>
              <p className="text-sm text-gray-400">Select how you'd like to explore ZeroDay</p>
            </div>

            <div className="space-y-4">
              <button
                onClick={() => setIsDemoMode(false)}
                className={`w-full p-6 text-left border rounded-xl transition-all ${
                  !isDemoMode
                    ? 'border-blue-500/50 bg-blue-600/20'
                    : 'border-white/20 bg-white/5 hover:border-blue-400/50'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className="p-3 bg-blue-500/20 rounded-xl">
                    <Settings className="w-6 h-6 text-blue-400" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">Personal Setup</h3>
                    <p className="text-sm text-gray-400">Customize ZeroDay for your specific role and goals</p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => setIsDemoMode(true)}
                className={`w-full p-6 text-left border rounded-xl transition-all ${
                  isDemoMode
                    ? 'border-green-500/50 bg-green-600/20'
                    : 'border-white/20 bg-white/5 hover:border-green-400/50'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className="p-3 bg-green-500/20 rounded-xl">
                    <Users className="w-6 h-6 text-green-400" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">Demo Mode</h3>
                    <p className="text-sm text-gray-400">Experience ZeroDay with realistic demo scenarios</p>
                  </div>
                </div>
              </button>
            </div>

            {isDemoMode && (
              <div className="mt-6 p-4 bg-green-500/10 border border-green-500/20 rounded-xl">
                <h4 className="font-medium text-green-300 mb-3 flex items-center">
                  <Users className="w-5 h-5 mr-2" />
                  Select Demo User Profile
                </h4>
                <div className="space-y-2">
                  {demoUsers.map((user: DemoUser) => (
                    <button
                      key={user.id}
                      onClick={() => setSelectedDemoUser(user.id)}
                      className={`w-full p-3 text-left border rounded-xl transition-all ${
                        selectedDemoUser === user.id 
                          ? 'border-green-500/50 bg-green-600/20' 
                          : 'border-white/20 hover:border-green-400/50 bg-white/5'
                      }`}
                    >
                      <div className="font-medium text-white">{user.name}</div>
                      <div className="text-sm text-gray-300">
                        {user.role} • {user.experience} experience
                      </div>
                      {selectedDemoUser === user.id && (
                        <div className="mt-2 text-xs text-green-300">
                          ✓ Selected - You'll experience ZeroDay as this user
                        </div>
                      )}
                    </button>
                  ))}
                </div>
                
                {selectedDemoUser && (
                  <div className="mt-3 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                    <p className="text-blue-300 text-sm">
                      🎯 Demo will include realistic project data, tasks, and AI interactions 
                      for {demoUsers.find(u => u.id === selectedDemoUser)?.scenario} environment
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        );

      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center mb-6">
              <h2 className="text-xl font-semibold text-white mb-2">Role & Experience</h2>
              <p className="text-sm text-gray-400">Tell us about your professional background</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">What's your primary role?</label>
              <div className="grid grid-cols-2 gap-3">
                {roles.map((role) => (
                  <button
                    key={role}
                    onClick={() => setSetupData(prev => ({ ...prev, role }))}
                    className={`p-3 text-left border rounded-xl transition-all ${
                      setupData.role === role
                        ? 'border-blue-500/50 bg-blue-600/20'
                        : 'border-white/20 bg-white/5 hover:border-blue-400/50'
                    }`}
                  >
                    <span className="text-white text-sm">{role}</span>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">Experience level?</label>
              <div className="space-y-2">
                {experienceLevels.map((level) => (
                  <button
                    key={level.value}
                    onClick={() => setSetupData(prev => ({ ...prev, experience: level.value }))}
                    className={`w-full p-3 text-left border rounded-xl transition-all ${
                      setupData.experience === level.value
                        ? 'border-blue-500/50 bg-blue-600/20'
                        : 'border-white/20 bg-white/5 hover:border-blue-400/50'
                    }`}
                  >
                    <span className="text-white">{level.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center mb-6">
              <h2 className="text-xl font-semibold text-white mb-2">Team & Goals</h2>
              <p className="text-sm text-gray-400">Help us understand your team context</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">Team size</label>
              <input
                type="text"
                value={setupData.team}
                onChange={(e) => setSetupData(prev => ({ ...prev, team: e.target.value }))}
                placeholder="e.g., 10 developers, 2 designers"
                className="w-full p-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">Learning goals (select all that apply)</label>
              <div className="grid grid-cols-2 gap-3">
                {focusAreas.map((area) => (
                  <button
                    key={area}
                    onClick={() => {
                      const newGoals = setupData.goals.includes(area)
                        ? setupData.goals.filter(g => g !== area)
                        : [...setupData.goals, area];
                      setSetupData(prev => ({ ...prev, goals: newGoals }));
                    }}
                    className={`p-3 text-left border rounded-xl transition-all ${
                      setupData.goals.includes(area)
                        ? 'border-green-500/50 bg-green-600/20'
                        : 'border-white/20 bg-white/5 hover:border-green-400/50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-white text-sm">{area}</span>
                      {setupData.goals.includes(area) && (
                        <CheckCircle className="w-4 h-4 text-green-400" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center mb-6">
              <h2 className="text-xl font-semibold text-white mb-2">Learning Preferences</h2>
              <p className="text-sm text-gray-400">How do you prefer to learn new things?</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">Learning style</label>
              <div className="space-y-2">
                {learningStyles.map((style) => (
                  <button
                    key={style.value}
                    onClick={() => setSetupData(prev => ({ 
                      ...prev, 
                      preferences: { ...prev.preferences, learningStyle: style.value }
                    }))}
                    className={`w-full p-3 text-left border rounded-xl transition-all ${
                      setupData.preferences.learningStyle === style.value
                        ? 'border-purple-500/50 bg-purple-600/20'
                        : 'border-white/20 bg-white/5 hover:border-purple-400/50'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{style.icon}</span>
                      <span className="text-white">{style.label}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">Time commitment per week</label>
              <div className="grid grid-cols-2 gap-3">
                {['1-2 hours', '3-5 hours', '6-10 hours', '10+ hours'].map((time) => (
                  <button
                    key={time}
                    onClick={() => setSetupData(prev => ({ 
                      ...prev, 
                      preferences: { ...prev.preferences, timeCommitment: time }
                    }))}
                    className={`p-3 text-center border rounded-xl transition-all ${
                      setupData.preferences.timeCommitment === time
                        ? 'border-orange-500/50 bg-orange-600/20'
                        : 'border-white/20 bg-white/5 hover:border-orange-400/50'
                    }`}
                  >
                    <span className="text-white text-sm">{time}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="text-center space-y-6">
            <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-6">
              <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-green-300 mb-2">Setup Complete!</h3>
              <p className="text-green-200">
                {isDemoMode 
                  ? selectedUser
                    ? `Demo mode is ready with ${selectedUser.name}'s profile.`
                    : 'Demo mode is ready.'
                  : `ZeroDay is now personalized for your experience as a ${setupData.role}.`
                }
              </p>
            </div>

            {!isDemoMode && (
              <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4">
                <h4 className="text-white font-medium mb-2">Your Profile Summary</h4>
                <div className="text-sm text-gray-300 space-y-1">
                  <p>Role: {setupData.role}</p>
                  <p>Experience: {experienceLevels.find(e => e.value === setupData.experience)?.label}</p>
                  <p>Goals: {setupData.goals.length} selected focus areas</p>
                </div>
              </div>
            )}
          </div>
        );

      default:
        return (
          <div className="text-center space-y-6">
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-blue-300 mb-2">Step {currentStep}</h3>
              <p className="text-blue-200">Continue setting up your profile</p>
            </div>
          </div>
        );
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 0:
        return isDemoMode ? !!selectedDemoUser : true;
      case 1:
        return setupData.role && setupData.experience;
      case 2:
        return setupData.team && setupData.goals.length > 0;
      case 3:
        return setupData.preferences.learningStyle && setupData.preferences.timeCommitment;
      default:
        return true;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <NavigationHeader
        title="ZeroDay Setup"
        subtitle="Personalize your AI assistant for better onboarding"
        isDemo={false}
      />

      <div className="max-w-7xl mx-auto px-6 py-6">
        
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2 text-center">
            Welcome to ZeroDay{user?.name ? `, ${user.name}` : ''}!
          </h1>
          <p className="text-sm text-gray-400 text-center">
            {isDemoMode ? 'Experience ZeroDay with realistic demo scenarios' : 'Let\'s personalize your AI assistant for better onboarding'}
          </p>
        </div>

        <div className="max-w-2xl mx-auto">
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
            
            <div className="mb-8">
              <div className="flex items-center justify-between">
                {steps.map((step, index) => (
                  <div key={step.key} className="flex items-center">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-all ${
                      index <= currentStep ? 'bg-blue-600 text-white' : 'bg-white/20 text-gray-400'
                    }`}>
                      {index < currentStep ? (
                        <CheckCircle className="w-5 h-5" />
                      ) : (
                        index + 1
                      )}
                    </div>
                    <span className={`ml-2 text-sm hidden md:block ${
                      index <= currentStep ? 'text-blue-300' : 'text-gray-500'
                    }`}>
                      {step.title}
                    </span>
                    {index < steps.length - 1 && (
                      <div className={`w-8 h-0.5 mx-4 transition-all ${
                        index < currentStep ? 'bg-blue-600' : 'bg-white/20'
                      }`} />
                    )}
                  </div>
                ))}
              </div>
            </div>

            
            <div className="mb-8 min-h-[400px]">
              {renderStepContent()}
            </div>

            
            <div className="flex justify-between">
              <button
                onClick={handleBack}
                disabled={currentStep === 0}
                className="px-6 py-3 text-gray-300 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Back
              </button>

              {currentStep < steps.length - 1 ? (
                <button
                  onClick={handleNext}
                  disabled={!canProceed()}
                  className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center space-x-2 shadow-sm"
                >
                  <span>Next</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              ) : (
                <button
                  onClick={handleComplete}
                  className="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl font-semibold hover:from-green-700 hover:to-emerald-700 transition-all flex items-center space-x-2 shadow-sm"
                >
                  <span>{isDemoMode ? 'Start Demo' : 'Complete Setup'}</span>
                  <Target className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
