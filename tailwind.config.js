/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        james: {
          bg: '#F7F8FA',
          surface: '#FFFFFF',
          border: '#E8EAED',
          primary: '#1A56DB',
          primaryHover: '#1245B8',
          text: '#111827',
          muted: '#6B7280',
          light: '#F3F4F6',
          disclaimer: '#FFFBEB',
          disclaimerBorder: '#FDE68A',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      keyframes: {
        'cell-ripple': {
          '0%':   { backgroundColor: 'rgba(255,255,255,0.05)', transform: 'scale(1)' },
          '50%':  { backgroundColor: 'rgba(255,255,255,0.35)', transform: 'scale(1.05)' },
          '100%': { backgroundColor: 'rgba(255,255,255,0.05)', transform: 'scale(1)' },
        },
      },
      animation: {
        'cell-ripple': 'cell-ripple var(--duration, 400ms) var(--delay, 0ms) ease-in-out both',
      },
    },
  },
  plugins: [],
}
