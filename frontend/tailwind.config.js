/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#0E1512",
          900: "#141F1A",
          800: "#1C2B24",
          700: "#26382F",
        },
        paper: {
          50: "#FAF8F3",
          100: "#F2EEE3",
        },
        growth: {
          500: "#3E8E5A",
          600: "#2F7248",
          700: "#255A39",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        serif: ["Source Serif 4", "Georgia", "serif"],
      },
    },
  },
  plugins: [],
};
