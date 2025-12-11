import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'  // ✅ 新增

export default defineConfig({
  plugins: [vue()],
  resolve: {              // ✅ 新增
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  }
})