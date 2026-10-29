import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    // Sin VITE_API_URL la interfaz usa rutas relativas: en desarrollo se redirigen a la API local.
    // VITE_PROXY permite apuntar la interfaz a otra API local (pruebas E2E con varias bases).
    proxy: { '/api': process.env.VITE_PROXY ?? 'http://127.0.0.1:8000' },
  },
  test: {
    exclude: ['e2e/**', 'node_modules/**'],
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
  },
})
