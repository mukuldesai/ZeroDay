import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Zap, Settings, Bell, Menu, X, Home, MessageSquare, Target, 
  Upload, BarChart3, Shield, Server, User, Play, Brain
} from 'lucide-react';

interface NavigationHeaderProps {
  title?: string;
  subtitle?: string;
  showNotifications?: boolean;
  showSettings?: boolean;
  rightContent?: React.ReactNode;
  gradient?: string;
  isDemo?: boolean;
}

export const NavigationHeader: React.FC<NavigationHeaderProps> = ({
  title = "ZeroDay",
  subtitle,
  showNotifications = false,
  showSettings = true,
  rightContent,
  gradient = 'from-blue-600 to-indigo-600',
  isDemo = false
}) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [showNotificationPanel, setShowNotificationPanel] = useState(false);
  const [showSettingsPanel, setShowSettingsPanel] = useState(false);
  const [isClient, setIsClient] = useState(false);
  const [currentPath, setCurrentPath] = useState('/');

  
  useEffect(() => {
    setIsClient(true);
    setCurrentPath(window.location.pathname);
  }, []);

  const navigationItems = [
    { href: '/', label: 'Home', icon: 'home' },
    { href: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
    { href: '/chat', label: 'AI Chat', icon: 'chat' },
    { href: '/tasks', label: 'Tasks', icon: 'tasks' },
    { href: '/upload', label: 'Upload', icon: 'upload' },
    { href: '/analytics', label: 'Analytics', icon: 'analytics' },
    { href: '/architecture', label: 'Architecture', icon: 'server' },
    { href: '/security', label: 'Security', icon: 'shield' },
    { href: '/demo', label: 'Demo', icon: 'play' },
    { href: '/login', label: 'Login', icon: 'user' }
  ];

  // Icon mapping to prevent hydration issues
  const getIcon = (iconName: string) => {
    const iconProps = { className: "w-4 h-4" };
    switch (iconName) {
      case 'home': return <Home {...iconProps} />;
      case 'dashboard': return <BarChart3 {...iconProps} />;
      case 'chat': return <MessageSquare {...iconProps} />;
      case 'tasks': return <Target {...iconProps} />;
      case 'upload': return <Upload {...iconProps} />;
      case 'analytics': return <BarChart3 {...iconProps} />;
      case 'server': return <Server {...iconProps} />;
      case 'shield': return <Shield {...iconProps} />;
      case 'play': return <Play {...iconProps} />;
      case 'user': return <User {...iconProps} />;
      default: return <Home {...iconProps} />;
    }
  };

  const isActivePage = (href: string) => {
    if (!isClient) return false;
    if (href === '/') return currentPath === '/';
    return currentPath.startsWith(href);
  };

  const handleNotificationClick = () => {
    setShowNotificationPanel(!showNotificationPanel);
    setShowSettingsPanel(false);
  };

  const handleSettingsClick = () => {
    setShowSettingsPanel(!showSettingsPanel);
    setShowNotificationPanel(false);
  };

  const handleNavigation = (href: string) => {
    window.location.href = href;
  };


  if (!isClient) {
    return (
      <div className="bg-black/20 backdrop-blur-sm border-b border-white/10 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3 flex-shrink-0">
              <div className={`bg-gradient-to-r ${gradient} p-2 rounded-xl`}>
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div className="min-w-0">
                <h1 className="text-xl font-bold text-white truncate">{title}</h1>
                {subtitle && <p className="text-xs text-gray-400 truncate">{subtitle}</p>}
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {isDemo && (
                <div className="bg-yellow-400/20 text-yellow-300 px-2 py-1 rounded-full text-xs font-bold border border-yellow-400/30">
                  🚀 DEMO
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-black/20 backdrop-blur-sm border-b border-white/10 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          
          <button 
            onClick={() => handleNavigation('/')}
            className="flex items-center space-x-3 flex-shrink-0"
          >
            <div className={`bg-gradient-to-r ${gradient} p-2 rounded-xl`}>
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div className="min-w-0">
              <h1 className="text-xl font-bold text-white truncate">{title}</h1>
              {subtitle && <p className="text-xs text-gray-400 truncate">{subtitle}</p>}
            </div>
          </button>

        
          <nav className="hidden lg:flex items-center space-x-1 flex-1 justify-center">
            {navigationItems.slice(0, 8).map((item) => (
              <motion.button
                key={item.href}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => handleNavigation(item.href)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActivePage(item.href)
                    ? 'bg-blue-600/20 text-blue-300 border border-blue-500/30'
                    : 'text-gray-300 hover:text-white hover:bg-white/10'
                }`}
              >
                {getIcon(item.icon)}
                <span className="hidden xl:block">{item.label}</span>
              </motion.button>
            ))}
          </nav>

        
          <div className="flex items-center space-x-2 flex-shrink-0">
           
            {isDemo && (
              <div className="bg-yellow-400/20 text-yellow-300 px-2 py-1 rounded-full text-xs font-bold border border-yellow-400/30 animate-pulse">
                🚀 DEMO
              </div>
            )}

         
            <div className="hidden md:flex items-center space-x-2 bg-green-500/20 border border-green-500/30 rounded-lg px-2 py-1">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-xs font-medium text-green-300">AI Active</span>
            </div>

            
            <div className="hidden md:flex items-center space-x-2">
              {rightContent}
            </div>

            
            {showNotifications && (
              <div className="relative">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleNotificationClick}
                  className="relative p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg"
                >
                  <Bell className="w-5 h-5" />
                  <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
                </motion.button>

                
                {showNotificationPanel && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute right-0 mt-2 w-80 bg-white/10 backdrop-blur-sm rounded-lg shadow-lg border border-white/20 z-50"
                  >
                    <div className="p-4">
                      <h3 className="text-lg font-semibold text-white mb-4">Notifications</h3>
                      <div className="space-y-3">
                        <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                          <p className="text-sm font-medium text-blue-300">New AI suggestion available</p>
                          <p className="text-xs text-blue-200">Your task agent has new recommendations</p>
                        </div>
                        <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
                          <p className="text-sm font-medium text-green-300">Knowledge base updated</p>
                          <p className="text-xs text-green-200">105 new documents indexed</p>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>
            )}

         
            {showSettings && (
              <div className="relative">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleSettingsClick}
                  className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg"
                >
                  <Settings className="w-5 h-5" />
                </motion.button>

            
                {showSettingsPanel && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute right-0 mt-2 w-64 bg-white/10 backdrop-blur-sm rounded-lg shadow-lg border border-white/20 z-50"
                  >
                    <div className="p-4">
                      <h3 className="text-lg font-semibold text-white mb-4">Settings</h3>
                      <div className="space-y-2">
                        <button
                          onClick={() => handleNavigation('/profile')}
                          className="block w-full text-left px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/10 rounded-lg"
                        >
                          Profile Settings
                        </button>
                        <button
                          onClick={() => handleNavigation('/preferences')}
                          className="block w-full text-left px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/10 rounded-lg"
                        >
                          AI Preferences
                        </button>
                        <button
                          onClick={() => handleNavigation('/login')}
                          className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/10 rounded-lg"
                        >
                          Sign Out
                        </button>
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>
            )}

           
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="lg:hidden p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg"
            >
              {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="lg:hidden py-4 border-t border-white/10"
          >
            <div className="grid grid-cols-2 gap-2">
              {navigationItems.map((item) => (
                <motion.button
                  key={item.href}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => {
                    setIsMobileMenuOpen(false);
                    handleNavigation(item.href);
                  }}
                  className={`flex items-center space-x-2 px-3 py-3 rounded-lg text-sm font-medium transition-colors ${
                    isActivePage(item.href)
                      ? 'bg-blue-600/20 text-blue-300 border border-blue-500/30'
                      : 'text-gray-300 hover:text-white hover:bg-white/10'
                  }`}
                >
                  {getIcon(item.icon)}
                  <span>{item.label}</span>
                </motion.button>
              ))}
            </div>
            
            
            {rightContent && (
              <div className="mt-4 pt-4 border-t border-white/10">
                {rightContent}
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
};