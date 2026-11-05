import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://localhost:8000", ws: true, changeOrigin: true },
    },
  },
  build: {
    outDir: "dist",
    chunkSizeWarningLimit: 2000,
    rollupOptions: {
      output: {
        // libraries change rarely: separate files stay cached in the browser across app updates
        manualChunks(id) {
          if (!id.includes("node_modules")) return undefined;
          // AI SDKs are imported on demand only - keep them in their own lazy chunks
          if (/@anthropic-ai|@google\/genai/.test(id)) return undefined;
          if (/@mantine|@floating-ui|react-number-format|react-textarea-autosize|dayjs/.test(id)) return "vendor-ui";
          if (/react-arborist|react-dnd|dnd-core|redux|react-window/.test(id)) return "vendor-tree";
          if (/[\\/]node_modules[\\/](react|react-dom|scheduler|react-router|react-router-dom|@remix-run|i18next|react-i18next|zustand|@tabler)[\\/]/.test(id)) return "vendor";
          return undefined; // everything else: let the bundler place it (lazy deps stay lazy)
        },
      },
    },
  },
  worker: { format: "es" },
});
