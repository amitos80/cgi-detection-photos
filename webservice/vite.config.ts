import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { TanStackRouterVite } from '@tanstack/router-vite-plugin'

// https://vite.dev/config/
export default defineConfig({
  plugins: [TanStackRouterVite({ generatedRouteTree: './src/routeTree.gen.ts' }), react()],
  server: {
    proxy: {
      '/analyze': {
        target: 'http://cgi-detector-service:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/analyze/, '/analyze'),
      },
      '/report': {
        target: 'http://cgi-detector-service:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/report/, '/report'),
      },
    },
  },
});
