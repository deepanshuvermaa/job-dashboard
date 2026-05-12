/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // ElevenLabs Palette
        eggshell: '#fdfcfc',
        powder: '#f5f3f1',
        chalk: '#e5e5e5',
        fog: '#b1b0b0',
        gravel: '#777169',
        slate: '#a59f97',
        cinder: '#575349',
        obsidian: '#000000',
        // Accents (used sparingly)
        'signal-blue': '#0447ff',
        ember: '#ff4704',
        // Grade system
        'grade-a': '#16a34a',
        'grade-b': '#2563eb',
        'grade-c': '#ca8a04',
        'grade-d': '#dc2626',
        'grade-f': '#71717a',
      },
      fontFamily: {
        display: ['var(--font-display-serif)', 'Instrument Serif', 'Cormorant Garamond', 'Georgia', 'serif'],
        body: ['var(--font-inter)', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      fontSize: {
        'display': ['48px', { lineHeight: '1.08', letterSpacing: '-0.96px', fontWeight: '400' }],
        'heading-lg': ['36px', { lineHeight: '1.13', letterSpacing: '-0.72px', fontWeight: '400' }],
        'heading': ['32px', { lineHeight: '1.17', letterSpacing: '-0.64px', fontWeight: '400' }],
        'heading-sm': ['20px', { lineHeight: '1.4', letterSpacing: '0', fontWeight: '500' }],
        'subheading': ['18px', { lineHeight: '1.44', letterSpacing: '0', fontWeight: '400' }],
        'body-lg': ['16px', { lineHeight: '1.5', letterSpacing: '0.1px', fontWeight: '400' }],
        'body': ['14px', { lineHeight: '1.43', letterSpacing: '0.1px', fontWeight: '400' }],
        'body-medium': ['14px', { lineHeight: '1.43', letterSpacing: '0.1px', fontWeight: '500' }],
        'caption': ['12px', { lineHeight: '1.33', letterSpacing: '0.1px', fontWeight: '400' }],
        'label': ['11px', { lineHeight: '1.0', letterSpacing: '1.2px', fontWeight: '500' }],
        'micro': ['10px', { lineHeight: '1.2', letterSpacing: '0', fontWeight: '400' }],
      },
      borderRadius: {
        'card': '16px',
        'badge': '12px',
        'input': '4px',
        'modal': '24px',
        'panel': '20px',
        'pill': '9999px',
      },
      boxShadow: {
        'subtle': 'rgba(0, 0, 0, 0.075) 0px 0px 0px 0.5px inset',
        'card': 'rgba(0, 0, 0, 0.4) 0px 0px 1px 0px, rgba(0, 0, 0, 0.04) 0px 2px 4px 0px',
        'card-hover': 'rgba(0, 0, 0, 0.4) 0px 0px 1px 0px, rgba(0, 0, 0, 0.06) 0px 4px 8px 0px',
        'button': 'rgba(0, 0, 0, 0.06) 0px 0px 0px 1px, rgba(0, 0, 0, 0.04) 0px 1px 2px, rgba(0, 0, 0, 0.04) 0px 2px 4px',
      },
      maxWidth: {
        'page': '1200px',
      },
    },
  },
  plugins: [],
}
