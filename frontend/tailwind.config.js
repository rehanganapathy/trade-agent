/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f5f7ff',
          100: '#ebefff',
          200: '#d6dfff',
          300: '#b3c3ff',
          400: '#8ca0ff',
          500: '#667eea',
          600: '#5465d9',
          700: '#4352c4',
          800: '#3442a0',
          900: '#2a3580',
        },
      },
    },
  },
  plugins: [],
}
