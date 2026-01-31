import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/views/Layout.vue'),
    redirect: '/monitor',
    children: [
      {
        path: '/monitor',
        name: 'Monitor',
        component: () => import('@/views/Monitor.vue')
      },
      {
        path: '/devices',
        name: 'Devices',
        component: () => import('@/views/Devices.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { requiresAuth: true, role: 'admin' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 如果是登录页面，直接放行
  if (to.path === '/login') {
    next()
    return
  }
  
  // 需要认证的页面
  if (to.meta.requiresAuth) {
    // 如果已经认证通过，直接放行
    if (authStore.isAuthenticated) {
      next()
      return
    }
    
    // 如果有token但未验证，检查token有效性
    if (authStore.token && !authStore.hasCheckedAuth) {
      const isValid = await authStore.checkAuth()
      if (isValid) {
        next()
        return
      }
    }
    
    // 未认证或token无效，跳转到登录页
    next('/login')
    return
  }
  
  // 不需要认证的直接放行
  next()
})

export default router