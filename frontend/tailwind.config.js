/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // Google Fonts - 精选字体组合
      fontFamily: {
        sans: ['Inter', 'Noto Sans SC', 'system-ui', 'sans-serif'],
        display: ['Outfit', 'Noto Sans SC', 'system-ui', 'sans-serif'],
      },

      // 颜色系统
      colors: {
        // 主色调 - 柔和的蓝紫色
        primary: {
          50: '#f0f4ff',
          100: '#e0e8ff',
          200: '#c7d4fe',
          300: '#a3b6fc',
          400: '#7d8ff7',
          500: '#6366f1', // 主要品牌色
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
        },
        // 强调色 - 柔和的珊瑚色
        accent: {
          50: '#fff1f0',
          100: '#ffe4e1',
          200: '#ffc9c3',
          300: '#ffa39e',
          400: '#ff7875',
          500: '#ff6b6b',
          600: '#fa5252',
          700: '#f03e3e',
          800: '#e03131',
          900: '#c92a2a',
        },
        // 背景色
        background: {
          DEFAULT: '#f8fafc',
          light: '#f1f5f9',
          dark: '#0f172a',
        },
        // 文字色
        text: {
          primary: '#1e293b',
          secondary: '#64748b',
          muted: '#94a3b8',
          inverse: '#f8fafc',
        },
        // 边框色
        border: {
          light: '#e2e8f0',
          DEFAULT: '#cbd5e1',
          dark: '#94a3b8',
        },
        // Glassmorphism 背景色
        glass: {
          light: 'rgba(255, 255, 255, 0.25)',
          DEFAULT: 'rgba(255, 255, 255, 0.35)',
          dark: 'rgba(255, 255, 255, 0.5)',
        },
        // Claymorphism 背景色
        clay: {
          light: '#f8fafc',
          DEFAULT: '#ffffff',
          dark: '#f1f5f9',
        },
      },

      // 边框圆角
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
        '3xl': '2rem',
        '4xl': '3rem',
      },

      // 阴影系统
      boxShadow: {
        // Glassmorphism 阴影
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
        'glass-lg': '0 12px 48px 0 rgba(31, 38, 135, 0.2)',
        // Claymorphism 阴影
        'clay': 'inset 0 -6px 16px rgba(0, 0, 0, 0.05), 0 4px 16px rgba(0, 0, 0, 0.08)',
        'clay-lg': 'inset 0 -8px 24px rgba(0, 0, 0, 0.06), 0 8px 32px rgba(0, 0, 0, 0.12)',
        // 极简阴影
        'minimal': '0 1px 3px rgba(0, 0, 0, 0.08)',
        'minimal-md': '0 4px 12px rgba(0, 0, 0, 0.1)',
        'minimal-lg': '0 8px 24px rgba(0, 0, 0, 0.12)',
      },

      // 间距规范
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },

      // 字间距
      letterSpacing: {
        'tighter': '-0.04em',
        'tight': '-0.02em',
        'normal': '0',
        'wide': '0.02em',
        'wider': '0.04em',
      },

      // 行高
      lineHeight: {
        'tight': '1.2',
        'snug': '1.375',
        'normal': '1.5',
        'relaxed': '1.625',
        'loose': '2',
      },

      // 动效
      transitionDuration: {
        '250': '250ms',
        '350': '350ms',
        '450': '450ms',
      },

      // 动画
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'float-delayed': 'float 6s ease-in-out 3s infinite',
        'pulse-soft': 'pulse 3s ease-in-out infinite',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'fade-in': 'fadeIn 0.5s ease-out',
      },

      // 关键帧
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },

      // 断点
      screens: {
        'xs': '475px',
        '3xl': '1920px',
      },
    },
  },
  plugins: [],
}
