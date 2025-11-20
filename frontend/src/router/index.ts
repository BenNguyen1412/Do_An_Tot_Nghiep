import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomePage from '@/views/HomePage.vue'
import LoginPage from '@/views/auth/LoginPage.vue'
import SignUpPage from '@/views/auth/SignUpPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignUpPage,
    },
    {
      path: '/user/home',
      name: 'user-home',
      component: () => import('@/views/user/UserHomePage.vue'),
      meta: { requiresAuth: true, role: 'user' },
    },
    {
      path: '/owner/home',
      name: 'owner-home',
      component: () => import('@/views/owner/OwnerHomePage.vue'),
      meta: { requiresAuth: true, role: 'owner' },
    },
    {
      path: '/enterprise/home',
      name: 'enterprise-home',
      component: () => import('@/views/enterprise/EnterpriseHomePage.vue'),
      meta: { requiresAuth: true, role: 'enterprise' },
    },
  ],
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // Kiểm tra authentication từ localStorage
  const token = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')
  const isAuthenticated = !!(token && userStr)

  let userRole = null
  if (userStr) {
    try {
      const user = JSON.parse(userStr)
      userRole = user.role
    } catch (e) {
      console.error('Error parsing user:', e)
    }
  }

  console.log('🔍 Router Guard:', {
    to: to.path,
    isAuthenticated,
    userRole,
  })

  // Chỉ kiểm tra routes yêu cầu authentication
  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      console.log('❌ Not authenticated, redirecting to login')
      return next('/login')
    }

    if (to.meta.role && to.meta.role !== userRole) {
      console.log('❌ Wrong role, redirecting to correct home')
      return next(`/${userRole}/home`)
    }
  }

  // Nếu đã login mà vào login/signup → redirect về home
  if ((to.path === '/login' || to.path === '/signup') && isAuthenticated) {
    console.log('✅ Already authenticated, redirecting to home')
    return next(`/${userRole}/home`)
  }

  next()
})

export default router
