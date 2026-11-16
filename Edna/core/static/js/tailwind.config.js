/** @type {import('tailwindcss').Config} */
export default {
  content: ["./templates/**/*.html", "./static/**/*.js"],
  theme: {
    extend: {
      colors: {
        primary: "#0b6e8c",
        "primary-dark": "#0a5c77",
        "primary-light": "#e5f0f5",
        accent: "#1e3b5c",
        gray50: "#f9fafb",
        gray100: "#f3f4f6",
        gray200: "#e5e7eb",
        gray300: "#d1d5db",
        gray600: "#4b5563",
        gray700: "#374151",
        gray800: "#1f2937",
        gray900: "#111827",
      },
      boxShadow: {
        sm: "0 1px 3px rgba(0,0,0,0.05)",
        md: "0 4px 6px -1px rgba(0,0,0,0.1)",
        lg: "0 10px 15px -3px rgba(0,0,0,0.1)",
      },
      borderRadius: {
        DEFAULT: "12px",
        sm: "6px",
      },
      fontFamily: {
        sans: ["Inter", "Outfit", "system-ui"],
      },
    },
  },
  plugins: [],
};
