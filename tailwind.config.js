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
    },
  },
  plugins: [],
}
