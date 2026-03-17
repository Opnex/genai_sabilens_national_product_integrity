/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Nigerian dark green as primary
        primary: '#008753',
        'primary-dark': '#006B3F',
        'primary-light': '#E8F3E8',
        accent: '#0A0E1A',
        'accent-2': '#1B2332',
        surface: '#FFFFFF',
        background: '#F7FAF9',
        muted: '#6B7280',
        border: '#E5EAE8',
        success: '#008753',
        warning: '#F59E0B',
        danger: '#FF4757',
        'nigeria-green': '#008753',
        'nigeria-white': '#FFFFFF',
      },
      fontFamily: {
        sans: ['Poppins', 'sans-serif'], // Poppins for UI text
        heading: ['Plus Jakarta Sans', 'sans-serif'], // Plus Jakarta Sans for headings
        mono: ['Poppins', 'monospace'],
      },
      boxShadow: {
        'soft': '0 2px 12px rgba(0,135,83,0.06)',
        'card': '0 8px 32px rgba(0,135,83,0.08)',
        'glow': '0 0 32px rgba(0,135,83,0.25)',
      },
      borderRadius: {
        'xl': '16px',
        '2xl': '20px',
        '3xl': '28px',
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #008753 0%, #00A86B 100%)',
        'gradient-success': 'linear-gradient(135deg, #008753 0%, #00C896 100%)',
      },
    },
  },
  plugins: [],
}