/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./src/**/*.css", // Explicitly include CSS files for Tailwind to scan
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#60a5fa', // Equivalent to blue-400 for a lighter shade
          DEFAULT: '#3b82f6', // Equivalent to blue-500
          dark: '#2563eb', // Equivalent to blue-600 for a darker shade
        },
        secondary: {
          light: '#a78bfa', // Equivalent to violet-400
          DEFAULT: '#8b5cf6', // Equivalent to violet-500
          dark: '#7c3aed', // Equivalent to violet-600
        },
        accent: {
          success: '#22c55e', // Equivalent to green-500
          warning: '#fcd34d', // Equivalent to amber-300
          danger: '#ef4444', // Equivalent to red-500
          info: '#3b82f6', // Reusing primary default for info
        },
        dark: '#1f2937', // Equivalent to gray-800
        light: '#f9fafb', // Equivalent to gray-50
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}