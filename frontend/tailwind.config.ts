import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Dark surface palette — forensic / legal aesthetic
        surface: {
          0: "#08090c",
          1: "#0f1117",
          2: "#161a23",
          3: "#1e2330",
          4: "#252b3a",
        },
        border: "#2a3145",
        // Severity colors
        severity: {
          low: "#22c55e",      // green-500
          medium: "#f59e0b",   // amber-500
          high: "#ef4444",     // red-500
        },
        // Accent
        accent: {
          DEFAULT: "#6366f1",  // indigo-500
          hover: "#818cf8",    // indigo-400
        },
        muted: "#64748b",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      animation: {
        "pulse-slow": "pulse 3s ease-in-out infinite",
        "fade-in": "fadeIn 0.4s ease-out forwards",
        "slide-up": "slideUp 0.35s ease-out forwards",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};
export default config;
