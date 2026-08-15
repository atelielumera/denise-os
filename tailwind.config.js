export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0a0a0f', surface: '#16161f', 's2': '#1c1c28', 's3': '#22222f',
        line: 'rgba(255,255,255,0.07)', accent: '#8b5cf6', 'accent2': '#a78bfa',
        ok: '#34d399', water: '#38bdf8', warn: '#fbbf24', danger: '#f87171', pink: '#f472b6',
      },
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] },
    },
  },
  plugins: [],
}
