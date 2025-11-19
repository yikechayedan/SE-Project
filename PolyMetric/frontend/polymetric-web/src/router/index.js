import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'UnloggedHome', component: () => import('../views/UnloggedHome.vue') },
  { path: '/home', name: 'LoggedHome', component: () => import('../views/LoggedHome.vue') },
  { path: '/login', name: 'Login', component: () => import('../views/auth/LoginView.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/auth/RegisterView.vue') },
  { path: '/forget', name: 'Forget', component: () => import('../views/auth/ForgetView.vue') },
  { path: '/reset', name: 'Reset', component: () => import('../views/auth/ResetView.vue') },
  { path: '/profile', name: 'Profile', component: () => import('../views/profile/ProfileView.vue') },
  { path: '/profile/edit', name: 'ProfileEdit', component: () => import('../views/profile/ProfileEdit.vue') },
  { path: '/datasets', name: 'DatasetSquare', component: () => import('../views/datasets/DatasetSquare.vue') },
  { path: '/datasets/my-manage', name: 'MyDatasetManage', component: () => import('../views/datasets/MyDatasetManage.vue') },
  { path: '/datasets/my-display', name: 'MyDatasetDisplay', component: () => import('../views/datasets/MyDatasetDisplay.vue') },
  { path: '/evaluation', name: 'EvaluationHall', component: () => import('../views/evaluation/EvaluationHall.vue') },
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

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const publicPaths = ['/', '/login', '/register', '/forget', '/reset']
  if (!publicPaths.includes(to.path) && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router