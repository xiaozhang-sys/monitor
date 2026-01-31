import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import fs from 'fs'

// 使用新的配置加载器
function loadUnifiedConfig() {
  try {
    const configPath = resolve(__dirname, '../config/apps/frontend.json')
    const backendConfigPath = resolve(__dirname, '../config/apps/backend.json')
    
    const frontendConfig = JSON.parse(fs.readFileSync(configPath, 'utf-8'))
    const backendConfig = JSON.parse(fs.readFileSync(backendConfigPath, 'utf-8'))
    
    return {
      frontendPort: frontendConfig.server.port,
      backendPort: backendConfig.server.port,
      webrtcPort: 8090, // WebRTC服务端口
      frontendConfig,
      backendConfig
    }
  } catch (error) {
    console.warn('无法加载统一配置，使用默认端口', error)
    return {
      frontendPort: 5173,
      backendPort: 8004,
      webrtcPort: 8090,
      frontendConfig: {},
      backendConfig: {}
    }
  }
}

const config = loadUnifiedConfig()

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: config.frontendPort,
    host: '127.0.0.1',
    strictPort: true,
    proxy: {
      '/api/stream': {
        target: `http://127.0.0.1:${config.webrtcPort}`,
        changeOrigin: true,
        secure: false
      },
      '/api': {
        target: `http://localhost:${config.backendPort}`,
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ''),
        onProxyReq: (proxyReq, req, res) => {
          console.log('Proxying request:', req.method, req.url);
        },
        onProxyRes: (proxyRes, req, res) => {
          console.log('Received response:', proxyRes.statusCode, req.url);
        },
        onError: (err, req, res) => {
          console.error('Proxy error:', err);
          res.writeHead(500, {
            'Content-Type': 'application/json'
          });
          res.end(JSON.stringify({
            error: 'Proxy Error',
            message: 'Unable to connect to backend service'
          }));
        }
      },
      '/webrtc': {
        target: `http://127.0.0.1:${config.webrtcPort}`,
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/webrtc/, '')
      }
    },
    historyApiFallback: true
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vue: ['vue', 'vue-router', 'pinia'],
          vendor: ['axios']
        }
      }
    }
  },
  define: {
    __VUE_OPTIONS_API__: true,
    __VUE_PROD_DEVTOOLS__: false
  }
})