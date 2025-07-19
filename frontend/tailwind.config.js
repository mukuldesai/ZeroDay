/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./lib/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        demo: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          badge: '#f0f9ff',
          text: '#0369a1',
          border: '#bae6fd',
          indicator: '#0ea5e9'
        },
        auth: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          primary: '#475569',
          secondary: '#64748b',
          accent: '#0ea5e9'
        },
        user: {
          50: '#fefce8',
          100: '#fef9c3', 
          200: '#fef08a',
          300: '#fde047',
          400: '#facc15',
          500: '#eab308',
          600: '#ca8a04',
          700: '#a16207',
          800: '#854d0e',
          900: '#713f12'
        }
      },
      animation: {
        'demo-pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'auth-slide': 'slideInFromRight 0.3s ease-out',
        'demo-bounce': 'bounce 1s infinite',
        'demo-glow': 'glow 2s ease-in-out infinite alternate'
      },
      keyframes: {
        slideInFromRight: {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' }
        },
        glow: {
          '0%': { boxShadow: '0 0 5px #0ea5e9' },
          '100%': { boxShadow: '0 0 20px #0ea5e9, 0 0 30px #0ea5e9' }
        }
      },
      backdropBlur: {
        xs: '2px',
      },
      backgroundImage: {
        'demo-gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'auth-gradient': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'user-gradient': 'linear-gradient(135deg, #fde047 0%, #facc15 100%)'
      },
      boxShadow: {
        'demo': '0 4px 14px 0 rgba(14, 165, 233, 0.2)',
        'auth': '0 4px 14px 0 rgba(71, 85, 105, 0.2)',
        'user': '0 4px 14px 0 rgba(250, 204, 21, 0.2)'
      }
    },
  },
  plugins: [],
}