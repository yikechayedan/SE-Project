<template>
  <canvas ref="canvasRef" class="wave-canvas"></canvas>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const canvasRef = ref(null)
let ctx = null
let animationId = null
let width = 0
let height = 0
let increment = 0
let mouseX = 0

// 配置参数
const config = {
  waveLength: 0.01, // 波浪密度
  amplitude: 100,   // 波浪高度
  frequency: 0.01,  // 波动速度
  color: 'rgba(64, 158, 255, 0.15)', // 蓝色半透明
  lineCount: 3      // 波浪线条数
}

const resize = () => {
  if (!canvasRef.value) return
  width = window.innerWidth
  height = window.innerHeight
  canvasRef.value.width = width
  canvasRef.value.height = height
}

const animate = () => {
  if (!ctx) return
  animationId = requestAnimationFrame(animate)
  
  // 每一帧稍微清除画布，形成拖尾效果会比较梦幻，这里选择完全清除保持清爽
  ctx.clearRect(0, 0, width, height)
  
  increment += config.frequency

  for (let i = 0; i < config.lineCount; i++) {
    ctx.beginPath()
    ctx.moveTo(0, height / 2)
    
    for (let x = 0; x < width; x++) {
      // 核心波浪算法：正弦波 + 鼠标干扰 + 偏移量
      const y = height / 2 + 
                Math.sin(x * config.waveLength + increment + i * 2) * config.amplitude * Math.sin(increment) +
                Math.sin(x * 0.003 + increment) * 50
      
      ctx.lineTo(x, y)
    }

    // 填充渐变色
    const gradient = ctx.createLinearGradient(0, 0, width, 0)
    gradient.addColorStop(0, 'rgba(64, 158, 255, 0.05)')
    gradient.addColorStop(0.5, 'rgba(64, 158, 255, 0.2)')
    gradient.addColorStop(1, 'rgba(64, 158, 255, 0.05)')
    
    ctx.strokeStyle = gradient
    ctx.lineWidth = 2
    ctx.stroke()
  }
}

onMounted(() => {
  const canvas = canvasRef.value
  ctx = canvas.getContext('2d')
  resize()
  animate()
  window.addEventListener('resize', resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  cancelAnimationFrame(animationId)
})
</script>

<style scoped>
.wave-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0; /* 最底层 */
  pointer-events: none;
  background-color: #0d1117; /* 确保背景色统一 */
}
</style>