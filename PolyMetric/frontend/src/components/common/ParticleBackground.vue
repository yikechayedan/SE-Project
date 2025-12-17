<template>
  <canvas ref="canvasRef" class="particle-canvas"></canvas>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const canvasRef = ref(null)
let ctx = null
let animationFrameId = null
let particles = []
let mouse = { x: -1000, y: -1000, isMoving: false, lastMoveTime: 0 }

// 配置参数
const config = {
  particleCount: 80, // 粒子数量（稀疏）
  connectionRadius: 150, // 鼠标交互半径
  gravity: 0.5, // 下落速度
  scatterForce: 0.8, // 散开力度
  gatherForce: 0.02, // 聚集力度
  colors: ['rgba(64, 158, 255, 0.6)', 'rgba(255, 255, 255, 0.4)'] // 蓝色和白色
}

class Particle {
  constructor(w, h) {
    this.x = Math.random() * w
    this.y = Math.random() * h
    this.vx = (Math.random() - 0.5) * 0.5 // 轻微的横向漂浮
    this.vy = Math.random() * 0.5 + config.gravity // 下落速度
    this.size = Math.random() * 2 + 1
    this.color = config.colors[Math.floor(Math.random() * config.colors.length)]
    this.originalVy = this.vy
  }

  update(w, h) {
    // 1. 基础下落运动
    this.x += this.vx
    this.y += this.vy

    // 边界检查：掉出底部则回到顶部
    if (this.y > h) {
      this.y = -10
      this.x = Math.random() * w
    }
    if (this.x > w || this.x < 0) {
      this.vx *= -1
    }

    // 2. 鼠标交互逻辑
    const dx = mouse.x - this.x
    const dy = mouse.y - this.y
    const distance = Math.sqrt(dx * dx + dy * dy)

    if (distance < config.connectionRadius) {
      const forceDirectionX = dx / distance
      const forceDirectionY = dy / distance
      const force = (config.connectionRadius - distance) / config.connectionRadius

      if (mouse.isMoving) {
        // A. 鼠标移动：散开 (Repel)
        // 粒子受到反向推力
        this.vx -= forceDirectionX * force * config.scatterForce
        this.vy -= forceDirectionY * force * config.scatterForce
      } else {
        // B. 鼠标静止：聚集 (Gather)
        // 粒子受到正向引力
        this.vx += forceDirectionX * force * config.gatherForce
        this.vy += forceDirectionY * force * config.gatherForce
      }
    }

    // 3. 摩擦力 (让受力后的粒子逐渐恢复正常速度)
    this.vx *= 0.96 
    this.vy = this.vy * 0.96 + (this.originalVy * 0.04) // 逐渐恢复到下落速度
  }

  draw() {
    if (!ctx) return
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fillStyle = this.color
    ctx.fill()
  }
}

const initCanvas = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  ctx = canvas.getContext('2d')

  particles = []
  for (let i = 0; i < config.particleCount; i++) {
    particles.push(new Particle(canvas.width, canvas.height))
  }
}

const animate = () => {
  if (!canvasRef.value || !ctx) return
  
  ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
  
  // 检查鼠标是否停止移动 (超过100ms未移动视为静止)
  if (Date.now() - mouse.lastMoveTime > 100) {
    mouse.isMoving = false
  }

  particles.forEach(p => {
    p.update(canvasRef.value.width, canvasRef.value.height)
    p.draw()
  })

  animationFrameId = requestAnimationFrame(animate)
}

const handleMouseMove = (e) => {
  mouse.x = e.clientX
  mouse.y = e.clientY
  mouse.isMoving = true
  mouse.lastMoveTime = Date.now()
}

const handleResize = () => {
  initCanvas()
}

onMounted(() => {
  initCanvas()
  animate()
  window.addEventListener('resize', handleResize)
  window.addEventListener('mousemove', handleMouseMove)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('mousemove', handleMouseMove)
  cancelAnimationFrame(animationFrameId)
})
</script>

<style scoped>
.particle-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none; /* 让鼠标事件穿透 canvas，不影响下方交互 */
  z-index: 1; /* 背景层级 */
}
</style>