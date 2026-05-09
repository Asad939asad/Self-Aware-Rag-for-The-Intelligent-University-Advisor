import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          bg:        "#0A0E1A",   // Deep navy — main background
          surface:   "#111827",   // Slightly lighter — card/panel background
          border:    "#1E2D45",   // Subtle border color
          accent:    "#2563EB",   // Electric blue — primary action color
          accentHov: "#1D4ED8",   // Darker blue on hover
          gold:      "#F59E0B",   // Amber gold — university branding accent
          goldLight: "#FDE68A",   // Light gold — for subtle highlights
          text:      "#F1F5F9",   // Near white — primary text
          muted:     "#94A3B8",   // Slate gray — secondary text, timestamps
          user:      "#1E3A5F",   // Dark blue — user message bubble background
          bot:       "#0F1F35",   // Darker navy — advisor message bubble background
          success:   "#10B981",   // Emerald — checkpoint pass indicators
          warning:   "#F59E0B",   // Amber — hallucination detected indicators
          danger:    "#EF4444",   // Red — error states
          checkpoint:"#7C3AED",   // Purple — checkpoint badge backgrounds
        }
      },
      fontFamily: {
        display: ["Syne", "sans-serif"],
        body: ["Bricolage Grotesque", "sans-serif"],
        mono: ["Azeret Mono", "monospace"],
      },
    },
  },
  plugins: [],
}

export default config
