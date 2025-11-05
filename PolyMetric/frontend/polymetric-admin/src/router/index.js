import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/login/LoginView.vue'
import Layout from '../components/Layout.vue'
import DashboardView from '../views/dashboard/DashboardView.vue'
import UserList from '../views/user/UserList.vue'
import DatasetList from '../views/dataset/DatasetList.vue'
import ModelList from '../views/model/ModelList.vue'

const routes = [
  { path: '/login', name: 'Login', component: LoginView },
  {
    path: '/',
    component: Layout,
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', component: DashboardView },
      { path: 'user', component: UserList },
      { path: 'dataset', component: DatasetList },
      { path: 'model', component: ModelList },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'
  if (to.name !== 'Login' && !isLoggedIn) next({ name: 'Login' })
  else next()
})

export default router