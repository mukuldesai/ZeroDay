import React, { useState, useEffect } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '${API_BASE}'
import { 
  Bell, User, Menu, Settings, Brain, Eye, EyeOff, Lock, Mail,
  Palette, Shield, LogOut, UserCircle, Users, CheckCircle, AlertCircle, MessageSquare
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

type User = {
  email: string
  name: string
  role: string
}

type LoginFormProps = {
  onLogin: (email: string, password: string) => void
  loading: boolean
  error?: string
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
      title: 'Login System Ready',
      message: 'Authentication service is active and ready for users',
      time: new Date(Date.now() - 1 * 60 * 1000),
      type: 'success'
    },
    {
      id: 2,
      title: 'Demo Mode Available',
      message: 'Try the platform without creating an account',
      time: new Date(Date.now() - 5 * 60 * 1000),
      type: 'info'
    },
    {
      id: 3,
      title: 'Security Update',
      message: 'Enhanced authentication protocols activated',
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
            <a href="/" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Home</a>
            <a href="/demo" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Demo</a>
            <a href="/architecture" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Architecture</a>
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
                    <p className="text-sm font-medium text-white">Guest User</p>
                    <p className="text-xs text-gray-400">Please sign in</p>
                  </div>
                  <div className="py-1">
                    <a
                      href="/register"
                      className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                    >
                      <UserCircle className="w-4 h-4" />
                      <span>Create Account</span>
                    </a>
                    <a
                      href="/demo"
                      className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                    >
                      <Users className="w-4 h-4" />
                      <span>Try Demo</span>
                    </a>
                    <a
                      href="/"
                      className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Back to Home</span>
                    </a>
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
              <a href="/architecture" className="text-gray-300 hover:text-white transition-colors py-2 px-2 rounded-lg hover:bg-white/10">Architecture</a>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};


const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string): Promise<void> => {
    try {
     
      if (email === 'demo@zeroday.dev' && password === 'demo') {
        const demoUser = { email, name: 'Demo User', role: 'Developer' };
        setIsAuthenticated(true);
        setUser(demoUser);
        localStorage.setItem('auth_token', 'demo_token');
        localStorage.setItem('user', JSON.stringify(demoUser));
        return Promise.resolve();
      }
        
      
      const response = await fetch('${API_BASE}/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          email: email,      
          password: password 
        })
      });

      if (response.status === 405) {
        
        throw new Error('Login service temporarily unavailable. Try demo mode.');
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Invalid credentials');
      }

      const data = await response.json();
      
      const userData = {
        email: email,
        name: data.user?.name || data.name || 'User',
        role: data.user?.role || data.role || 'Developer'
      };

      setIsAuthenticated(true);
      setUser(userData);
      
      
      if (data.token || data.access_token) {
        localStorage.setItem('auth_token', data.token || data.access_token);
      }
      localStorage.setItem('user', JSON.stringify(userData));

      return Promise.resolve();
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const logout = () => {
    setIsAuthenticated(false);
    setUser(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  };

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const savedUser = localStorage.getItem('user');
    
    if (token && savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setIsAuthenticated(true);
        setUser(userData);
      } catch (error) {
        
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
      }
    }
  }, []);

  return { isAuthenticated, user, login, logout };
};


const LoginForm = ({ onLogin, loading, error }: LoginFormProps) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (email && password) {
      onLogin(email, password);
    }
  };

  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-300 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="text-sm text-gray-300 block mb-1">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full bg-transparent border border-white/10 rounded-lg px-3 py-2 text-white placeholder-gray-400"
            placeholder="you@company.com"
            required
          />
        </div>

        <div>
          <label className="text-sm text-gray-300 block mb-1">Password</label>
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-transparent border border-white/10 rounded-lg px-3 py-2 text-white placeholder-gray-400"
              placeholder="Enter your password"
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-2.5 text-gray-400 hover:text-white"
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>

        <div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors disabled:opacity-50"
          >
            {loading ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Signing In...</span>
              </div>
            ) : (
              'Sign In'
            )}
          </button>
        </div>
      </form>

      <div className="flex items-center justify-between">
        <label className="flex items-center">
          <input
            type="checkbox"
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-300">Remember me</span>
        </label>
        <button className="text-sm text-blue-400 hover:text-blue-300">
          Forgot password?
        </button>
      </div>
    </div>
  );
};


export default function LoginPage() {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, isAuthenticated } = useAuth();
  const [lastUpdated, setLastUpdated] = useState<string>('');

  useEffect(() => {
    if (isAuthenticated) {
      window.location.href = '/dashboard';
    }
  }, [isAuthenticated]);

  useEffect(() => {
    setLastUpdated(new Date().toLocaleString());
  }, []);

  const handleLogin = async (email: string, password: string) => {
    setLoading(true);
    setError('');

    try {
      await login(email, password);
      
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 500);
    } catch (err) {
      let errorMessage = 'Login failed';
      
      if (err instanceof Error) {
        errorMessage = err.message;
      }
      
      
      if (errorMessage.includes('405') || errorMessage.includes('Method')) {
        errorMessage = 'Login service is being configured. Please try demo mode for now.';
      } else if (errorMessage.includes('404')) {
        errorMessage = 'Authentication service not found. Please try demo mode.';
      } else if (errorMessage.includes('500')) {
        errorMessage = 'Server error. Please try demo mode or contact support.';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterClick = () => {
    window.location.href = '/register';
  };

  const handleDemoLogin = () => {
    handleLogin('demo@zeroday.dev', 'demo');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <NavigationHeader
        title="ZeroDay Login"
        subtitle="Access your AI-powered developer workspace"
        isDemo={false}
      />

      <div className="max-w-7xl mx-auto px-6 py-6">
        
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2 text-center">Welcome Back</h1>
          <p className="text-sm text-gray-400 text-center">Sign in to continue to ZeroDay</p>
        </div>

        <div className="max-w-md mx-auto">
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-400 to-purple-400 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Brain className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-xl font-semibold text-white mb-2">Sign In</h2>
              <p className="text-sm text-gray-400">Access your developer workspace</p>
            </div>

            <LoginForm 
              onLogin={handleLogin}
              loading={loading}
              error={error}
            />

            <div className="text-center mt-6">
              <p className="text-sm text-gray-300">
                Don't have an account?{' '}
                <button 
                  onClick={handleRegisterClick}
                  className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
                >
                  Sign up
                </button>
              </p>
            </div>

            <div className="mt-6 bg-blue-500/10 rounded-xl p-4 border border-blue-500/20">
              <h3 className="text-lg font-medium text-blue-300 mb-3 flex items-center">
                <Brain className="w-5 h-5 mr-2" />
                Demo Access
              </h3>
              <p className="text-sm text-blue-200 mb-4">
                Try ZeroDay with realistic demo data. No registration required.
              </p>
              <button
                onClick={handleDemoLogin}
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 px-4 rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 transition-all duration-200 shadow-sm"
              >
                {loading ? 'Loading...' : 'Enter Demo Mode'}
              </button>
            </div>

            
            <div className="mt-6 text-center">
              <p className="text-xs text-gray-400">
                By signing in, you agree to our{' '}
                <a href="/terms" className="text-blue-400 hover:text-blue-300">Terms of Service</a>
                {' '}and{' '}
                <a href="/privacy" className="text-blue-400 hover:text-blue-300">Privacy Policy</a>
              </p>
            </div>
          </div>

          
          <div className="mt-8 bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
            <h3 className="text-xl font-semibold text-white mb-4 text-center">What You Get</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <span className="text-gray-300 text-sm">4 AI agents for instant onboarding help</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-gray-300 text-sm">Personalized task recommendations</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                <span className="text-gray-300 text-sm">Real-time code analysis and guidance</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-orange-400 rounded-full"></div>
                <span className="text-gray-300 text-sm">Learning paths tailored to your role</span>
              </div>
            </div>
          </div>

          {lastUpdated && (
            <div className="mt-4 text-center">
              <p className="text-gray-500 text-xs">Last updated: {lastUpdated}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
