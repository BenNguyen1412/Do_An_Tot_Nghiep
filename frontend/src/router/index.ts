import { createRouter, createWebHistory } from 'vue-router'
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

// Simple navigation guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')

  console.log('🔍 Router Guard:', {
    to: to.path,
    from: from.path,
    hasToken: !!token,
    hasUser: !!userStr,
  })

  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!token || !userStr) {
      console.log('❌ Not authenticated, redirect to login')
      return next('/login')
    }

    // Check role
    try {
      const user = JSON.parse(userStr)
      if (to.meta.role && to.meta.role !== user.role) {
        console.log('❌ Wrong role, redirect to correct home')
        return next(`/${user.role}/home`)
      }
    } catch (e) {
      console.error('Error parsing user:', e)
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      return next('/login')
    }
  }

  if ((to.path === '/login' || to.path === '/signup') && token && userStr) {
    try {
      const user = JSON.parse(userStr)
      console.log('✅ Already logged in, redirect to home')
      return next(`/${user.role}/home`)
    } catch (e) {
      console.error('Error parsing user:', e)
    }
  }

  next()
})

export default router
