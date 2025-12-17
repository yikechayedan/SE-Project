<template>
  <div class="unlogged-home">
    <div ref="threeContainer" class="three-container"></div>

    <header class="main-header">
      <div class="logo" @click="$router.push('/')">
        <el-icon size="30" class="logo-icon"><VideoPlay /></el-icon>
        <span class="logo-text">PolyMetric</span>
      </div>
      <el-button type="primary" class="login-button" @click="$router.push('/login')">
        <el-icon><User /></el-icon>
        <span style="margin-left: 5px;">登录 / 注册</span>
      </el-button>
    </header>

    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="glow">PolyMetric</span>：全维度模型评测与数据集管理平台
        </h1>
        <p class="hero-subtitle">
          汇聚高质量数据集，提供多维度、客观、对抗性评测体系，驱动新一代AI模型发展。
        </p>
        <div class="hero-cta">
          <el-button type="primary" size="large" @click="$router.push('/register')" class="cta-button-primary">
            立即开始
            <el-icon style="margin-left: 5px;"><Right /></el-icon>
          </el-button>
          <el-button type="info" size="large" plain @click="scrollTo('features')" class="cta-button-secondary">
            了解更多
          </el-button>
        </div>
      </div>
    </section>

    <section class="features-section" id="features">
      <h2 class="section-title">核心功能一览</h2>
      <div class="feature-cards">
        <div class="feature-card">
          <el-icon size="40" class="card-icon"><DataBoard /></el-icon>
          <h3>数据集广场</h3>
          <p>浏览、共享和管理海量高质量数据集，支持多种格式和权限控制。</p>
        </div>
        <div class="feature-card">
          <el-icon size="40" class="card-icon"><Monitor /></el-icon>
          <h3>多维评测</h3>
          <p>支持客观、主观、对抗性评测任务，为您提供全方位的模型性能报告。</p>
        </div>
        <div class="feature-card">
          <el-icon size="40" class="card-icon"><MagicStick /></el-icon>
          <h3>自动化流程</h3>
          <p>从数据准备到模型评估，提供一站式、自动化的任务创建和执行能力。</p>
        </div>
      </div>
    </section>

    <footer class="main-footer">
      <p>&copy; 2024 PolyMetric Project. All Rights Reserved.</p>
    </footer>

  </div>
</template>

<script setup>
// 核心库导入
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import * as THREE from 'three'

// Element Plus 图标导入
import { VideoPlay, User, DataBoard, Monitor, MagicStick, Right } from '@element-plus/icons-vue'

const router = useRouter()
const threeContainer = ref(null) // 引用 Three.js 容器

// Three.js 场景变量
let camera = null
let scene = null
let renderer = null
let particles = null
let animationFrameId = null;

// Three.js 动态粒子背景初始化
const initThree = () => {
  if (!threeContainer.value) return;

  const container = threeContainer.value;
  const width = container.clientWidth;
  const height = container.clientHeight;

  // 1. 场景 (Scene)
  scene = new THREE.Scene();

  // 2. 摄像机 (Camera)
  camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
  camera.position.z = 5;

  // 3. 渲染器 (Renderer)
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true }); // alpha: true 允许背景透明
  renderer.setSize(width, height);
  // 清理旧的 canvas 元素，防止重复添加（如果组件热重载）
  while (container.firstChild) {
    container.removeChild(container.firstChild);
  }
  container.appendChild(renderer.domElement);

  // 4. 创建粒子系统 (Particle System)
  const particleCount = 2000;
  const positions = new Float32Array(particleCount * 3);
  const colors = new Float32Array(particleCount * 3);
  const particleGeometry = new THREE.BufferGeometry();

  const color = new THREE.Color();
  const baseColor = new THREE.Color(0x409eff); // 蓝色

  for (let i = 0; i < particleCount; i++) {
    // 随机位置
    positions[i * 3] = (Math.random() - 0.5) * 20;
    positions[i * 3 + 1] = (Math.random() - 0.5) * 20;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 20;

    // 随机颜色
    color.copy(baseColor).multiplyScalar(Math.random() * 0.5 + 0.5);
    colors[i * 3] = color.r;
    colors[i * 3 + 1] = color.g;
    colors[i * 3 + 2] = color.b;
  }

  particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  particleGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

  const particleMaterial = new THREE.PointsMaterial({
    size: 0.05,
    vertexColors: true,
    blending: THREE.AdditiveBlending,
    transparent: true,
    sizeAttenuation: true,
  });

  particles = new THREE.Points(particleGeometry, particleMaterial);
  scene.add(particles);

  // 监听窗口大小变化
  window.addEventListener('resize', onWindowResize, false);
};

// 窗口大小变化处理
const onWindowResize = () => {
  if (!threeContainer.value || !camera || !renderer) return;
  const width = threeContainer.value.clientWidth;
  const height = threeContainer.value.clientHeight;

  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
};

// 动画循环
const animate = () => {
  // 关键：将 requestAnimationFrame 的 ID 存储在 animationFrameId 变量中，方便清理
  animationFrameId = requestAnimationFrame(animate);

  // 粒子旋转
  if (particles) {
    particles.rotation.x += 0.0001;
    particles.rotation.y += 0.0002;
  }

  if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }
};

// 组件卸载时的清理函数
const disposeThree = () => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
  window.removeEventListener('resize', onWindowResize);

  if (renderer && threeContainer.value) {
    threeContainer.value.removeChild(renderer.domElement);
    renderer.dispose();
  }
  // 清理场景中的几何体和材质以释放内存
  if (scene) {
    scene.traverse((object) => {
      if (object.isMesh || object.isPoints) {
        if (object.geometry) object.geometry.dispose();
        if (object.material) {
          if (Array.isArray(object.material)) {
            object.material.forEach(material => material.dispose());
          } else {
            object.material.dispose();
          }
        }
      }
    });
  }
};

onMounted(() => {
  initThree();
  animate();
});

onBeforeUnmount(() => {
  disposeThree();
});

// 滚动到指定ID的逻辑 (业务逻辑保留)
const scrollTo = (id) => {
  document.getElementById(id).scrollIntoView({ behavior: 'smooth' })
}
</script>

<style lang="scss" scoped>
// ------------------------------------
// 基础和布局样式
// ------------------------------------
.unlogged-home {
  min-height: 100vh;
  background-color: #0d1117; // 深色背景
  color: #c9d1d9;
  font-family: 'Inter', sans-serif;
  overflow-x: hidden;
  position: relative;
}

// ------------------------------------
// Three.js 容器样式 (必须全屏且位于最底层)
// ------------------------------------
.three-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0; // 确保在最底层
  opacity: 0.7;
  filter: brightness(1.2);
}

// ------------------------------------
// 头部样式 - z-index 确保在内容之上
// ------------------------------------
.main-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 50px;
  background-color: rgba(13, 17, 23, 0.85);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
  z-index: 100;

  .logo {
    display: flex;
    align-items: center;
    font-size: 24px;
    font-weight: bold;
    cursor: pointer;
    color: #409eff;

    .logo-icon { color: #409eff; margin-right: 8px; }
    .logo-text { font-family: 'Share Tech Mono', monospace; letter-spacing: 1px; }
  }

  .login-button { font-weight: 600; }
}

// ------------------------------------
// 英雄区样式 - z-index 确保在内容之上
// ------------------------------------
.hero-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  text-align: center;
  padding-top: 60px;
  position: relative;
  z-index: 10;

  .hero-content { max-width: 900px; padding: 0 20px; }
  .hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    margin-bottom: 20px;
    line-height: 1.2;

    .glow {
      color: #409eff;
      text-shadow: 0 0 10px #409eff, 0 0 20px rgba(64, 158, 255, 0.5);
    }
  }

  .hero-subtitle {
    font-size: 1.5rem;
    font-weight: 300;
    margin-bottom: 40px;
    color: #9aa8b7;
  }

  .hero-cta {
    display: flex;
    justify-content: center;
    gap: 15px;

    .cta-button-primary {
      background-color: #409eff;
      border-color: #409eff;
      box-shadow: 0 0 15px rgba(64, 158, 255, 0.5);
      transition: all 0.3s ease;
      &:hover {
        background-color: #66b1ff;
        border-color: #66b1ff;
        transform: translateY(-2px);
      }
    }
  }
}


// ------------------------------------
// 特性展示区样式 - z-index 确保在内容之上
// ------------------------------------
.features-section {
  padding: 80px 50px;
  text-align: center;
  background-color: rgba(22, 27, 34, 0.95);
  position: relative;
  z-index: 10;
  box-shadow: 0 -5px 20px rgba(0, 0, 0, 0.5);

  .section-title { font-size: 2.5rem; font-weight: 700; margin-bottom: 50px; color: #ffffff; }

  .feature-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
    max-width: 1200px;
    margin: 0 auto;
  }

  .feature-card {
    background-color: #0d1117;
    padding: 30px;
    border-radius: 12px;
    border: 1px solid #30363d;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    transition: all 0.3s ease;

    &:hover {
      border-color: #409eff;
      box-shadow: 0 0 20px rgba(64, 158, 255, 0.3);
      transform: translateY(-5px);
    }

    .card-icon { color: #409eff; margin-bottom: 15px; }
    h3 { font-size: 1.5rem; margin-bottom: 10px; color: #ffffff; }
    p { color: #8b949e; }
  }
}

// ------------------------------------
// 页脚样式
// ------------------------------------
.main-footer {
  text-align: center;
  padding: 20px;
  border-top: 1px solid #30363d;
  background-color: #0d1117;
  font-size: 0.9rem;
  color: #8b949e;
  position: relative;
  z-index: 10;
}
</style>