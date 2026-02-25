import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './lib/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          navy: '#0B1D3A',
          dark: '#071226',
          gold: '#C89D3D',
          light: '#EAF0FF'
        }
      }
    }
  },
  plugins: []
};

export default config;
