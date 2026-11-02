import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// El build va a ../web, que FastAPI sirve en / y /static (ensayo/api.py).
export default defineConfig({
  base: "./",
  plugins: [react(), tailwindcss()],
  resolve: { alias: { "@": decodeURIComponent(new URL("./src", import.meta.url).pathname) } },
  build: { outDir: "../web", emptyOutDir: true, assetsDir: "static" },
  server: { proxy: { "/api": "http://localhost:8040" } },
});
