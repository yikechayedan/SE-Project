import { createRouter, createWebHistory } from 'vue-router'
import axios from 'axios'

const routes = [
  { path: '/', name: 'UnloggedHome', component: () => import('../views/UnloggedHome.vue') },
  { path: '/home', name: 'LoggedHome', component: () => import('../views/LoggedHome.vue') },
  { path: '/login', name: 'Login', component: () => import('../views/auth/LoginView.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/auth/RegisterView.vue') },
  { path: '/forget', name: 'Forget', component: () => import('../views/auth/ForgetView.vue') },
  { path: '/reset', name: 'Reset', component: () => import('../views/auth/ResetView.vue') },
  { path: '/profile', name: 'Profile', component: () => import('../views/profile/ProfileView.vue') },
  { path: '/profile/edit', name: 'ProfileEdit', component: () => import('../views/profile/ProfileEdit.vue') },
  
  // ✅ 修正：使用实际存在的文件名
  { path: '/datasets', name: 'Datasets', component: () => import('../views/datasets/DatasetSquare.vue') },
  { path: '/datasets/my', name: 'MyDatasets', component: () => import('../views/datasets/MyDatasetManage.vue') },
  { path: '/datasets/display', name: 'DatasetDisplay', component: () => import('../views/datasets/MyDatasetDisplay.vue') },
  
  // ✅ 修正：使用实际存在的文件名
  { path: '/models', name: 'Models', component: () => import('../views/models/ModelsView.vue') },
  
  // ✅ 修正：使用实际存在的文件名
  { path: '/evaluation', name: 'Evaluation', component: () => import('../views/evaluation/EvaluationHall.vue') },
  { path: '/evaluation/objective', name: 'ObjectiveEval', component: () => import('../views/evaluation/ObjectiveEval.vue') },
  { path: '/evaluation/subjective', name: 'SubjectiveEval', component: () => import('../views/evaluation/SubjectiveEval.vue') },
  { path: '/evaluation/adversarial', name: 'AdversarialEval', component: () => import('../views/evaluation/AdversarialEval.vue') },
  { path: '/tasks/my-manage', name: 'MyTaskManage', component: () => import('../views/evaluation/MyTaskManage.vue') },
  
  { path: '/user/:id', name: 'UserProfile', component: () => import('../views/profile/UserProfile.vue') },
  { path: '/user/:id/datasets', name: 'UserDatasets', component: () => import('../views/profile/UserDatasets.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 公开页面（不需要登录）
const publicPaths = ['/', '/login', '/register', '/forget', '/reset']

// 尝试用 refresh token 刷新 access token
async function tryRefreshToken() {
  const refresh = localStorage.getItem('refresh')
  if (!refresh) return false
  
  try {
    const res = await axios.post('http://127.0.0.1:8000/api/users/token/refresh/', {
      refresh: refresh
    })
    localStorage.setItem('token', res.data.access)
    return true  // 刷新成功
  } catch (e) {
    // refresh token 也过期了，清除所有登录信息
    localStorage.removeItem('token')
    localStorage.removeItem('refresh')
    localStorage.removeItem('username')
    return false  // 刷新失败
  }
}

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  const publicPaths = ['/', '/login', '/register', '/forget', '/reset']
  
  // ✅ 新增：已登录用户访问首页，自动跳转到 /home
  if (to.path === '/' && token) {
    next('/home')
    return
  }
  
  // 公开页面直接放行
  if (publicPaths.includes(to.path)) {
    next()
    return
  }
  
  // 有 token，直接放行
  if (token) {
    next()
    return
  }
  
  // 没有 token，尝试用 refresh 刷新
  const refreshed = await tryRefreshToken()
  
  if (refreshed) {
    next()
  } else {
    next('/login')
  }
})

export default router