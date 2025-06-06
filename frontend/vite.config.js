import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000, // You can specify the port for the Vite dev server
    proxy: {
      // Proxying API requests from /api to http://localhost:5001/api
      '/api': {
        target: 'http://localhost:5001', // Your Flask backend URL
        changeOrigin: true, // Needed for virtual hosted sites
        // rewrite: (path) => path.replace(/^\/api/, ''), // Use if Flask doesn't expect /api prefix
                                                           // But our Flask app *does* expect /api
      }
    }
  }
})
