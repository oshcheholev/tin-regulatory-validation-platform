/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Bank Austria Corporate Colors
        // To change back to original blue theme, replace the hex values below
        // or swap with the commented alternative values
        primary: {
          50: '#fef2f2',    // alt: '#eff6ff' (blue)
          100: '#fee2e2',   // alt: '#dbeafe' (blue)
          200: '#fecaca',   // alt: '#bfdbfe' (blue)
          300: '#fca5a5',   // alt: '#93c5fd' (blue)
          400: '#f87171',   // alt: '#60a5fa' (blue)
          500: '#ef4444',   // alt: '#3b82f6' (blue)
          600: '#D9001C',   // Bank Austria Red - alt: '#2563eb' (blue)
          700: '#b90018',   // alt: '#1d4ed8' (blue)
          800: '#9a0014',   // alt: '#1e40af' (blue)
          900: '#7b0010',   // alt: '#1e3a8a' (blue)
        },
      },
    },
  },
  plugins: [],
}
