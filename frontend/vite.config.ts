import { resolve } from 'node:path'
import { defineConfig } from 'vitest/config'
import viteReact from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'

import tanstackRouter from '@tanstack/router-plugin/vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    tanstackRouter({ autoCodeSplitting: true }),
    viteReact(),
    visualizer({
      filename: 'dist/stats.html',
      open: true,
      gzipSize: true,
      brotliSize: true,
    }),
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://77.37.122.76:4444',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
  build: {
    // rollupOptions: {
    //   output: {
    //     manualChunks: (id) => {
    //       // Split node_modules into separate chunks
    //       if (id.includes('node_modules')) {
    //         // Mantine packages (your biggest dependency)
    //         if (id.includes('@mantine/core')) {
    //           return 'mantine-core'
    //         }
    //         if (id.includes('@mantine/hooks')) {
    //           return 'mantine-hooks'
    //         }
    //         if (id.includes('@mantine/dropzone')) {
    //           return 'mantine-dropzone'
    //         }

    //         // React ecosystem
    //         if (id.includes('react') || id.includes('react-dom')) {
    //           return 'react-vendor'
    //         }

    //         // TanStack Router
    //         if (id.includes('@tanstack')) {
    //           return 'tanstack'
    //         }

    //         // All other node_modules
    //         return 'vendor'
    //       }
    //     },
    //   },
    // },
    chunkSizeWarningLimit: 800,
  },
})
