import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    // Docker on Windows doesn't pass file-change events through, so poll there.
    watch: { usePolling: process.env.VITE_USE_POLLING === 'true' },
    // Calls to /api/... go to FastAPI, so the frontend never hard-codes the backend URL.
    proxy: {
      '/api': process.env.VITE_API_PROXY_TARGET || 'http://localhost:8000',
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './tests/setup.js',
  },
})
