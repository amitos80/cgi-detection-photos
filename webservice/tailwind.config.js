/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./src/**/*.css", // Explicitly include CSS files for Tailwind to scan
  ],
  theme: {
      colors: {
        primary: {
          light: 'rgb(var(--color-primary-light) / <alpha-value>)',
          DEFAULT: 'rgb(var(--color-primary-DEFAULT) / <alpha-value>)',
          dark: 'rgb(var(--color-primary-dark) / <alpha-value>)',
        },
        secondary: {
          light: 'rgb(var(--color-secondary-light) / <alpha-value>)',
          DEFAULT: 'rgb(var(--color-secondary-DEFAULT) / <alpha-value>)',
          dark: 'rgb(var(--color-secondary-dark) / <alpha-value>)',
        },
        accent: {
          success: 'rgb(var(--color-accent-success) / <alpha-value>)',
          warning: 'rgb(var(--color-accent-warning) / <alpha-value>)',
          danger: 'rgb(var(--color-accent-danger) / <alpha-value>)',
          info: 'rgb(var(--color-accent-info) / <alpha-value>)',
        },
        dark: 'rgb(var(--color-dark) / <alpha-value>)',
        light: 'rgb(var(--color-light) / <alpha-value>)',
      },
      spacing: {
        '1': '4px',
        '2': '8px',
        '3': '12px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '8': '32px',
        '10': '40px',
        '12': '48px',
        '16': '64px',
        '20': '80px',
        '24': '96px',
        '32': '128px',
        '40': '160px',
        '48': '192px',
        '56': '224px',
        '64': '256px',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.02)', // subtle shadow
        'medium': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)', // slightly more pronounced
        'elevate': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)', // for elevated elements
      },
      transitionProperty: {
        'width': 'width',
        'height': 'height',
        'spacing': 'margin, padding',
      },
      transitionDuration: {
        'DEFAULT': '200ms',
        '400': '400ms',
      },
      transitionTimingFunction: {
        'in-out': 'ease-in-out',
      },
    },