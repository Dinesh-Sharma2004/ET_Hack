export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#091521",
        mist: "#edf4f7",
        accent: "#0f766e",
        coral: "#f97316",
        gold: "#d4a017"
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Manrope'", "sans-serif"]
      },
      boxShadow: {
        glow: "0 18px 40px rgba(15, 118, 110, 0.18)"
      }
    }
  },
  plugins: []
};
