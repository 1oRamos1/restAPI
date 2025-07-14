/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./src/**/*.{js,jsx,ts,tsx}", // <-- this is important for React
    "./public/index.html"
  ],
  theme: {
    fontFamily: {
      sans: ['Inter','Fredoka', 'sans-serif'],
      kumbh: ['"Kumbh Sans"', 'sans-serif'],
    },
    extend: {
      colors: {
        red: {
          600: '#e60012',
          700: '#cc0011',
        },
        blue40: '#3582c4',
        blue50: '#2271b1',
        blue70: '#0a4b78',
        blue80: '#043959',
        blue90: '#01263a',
        blue100: '#00131c',
        blue5: '#c5d9ed',
        blue0: '#f0f6fc',
      },
    },
  },
  plugins: [],
};