import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { quasar } from '@quasar/vite-plugin'

export default defineConfig({
  plugins: [
    vue(),
    quasar()
  ],
  server: {
    port: 5173,
    host: '0.0.0.0'
  }
})