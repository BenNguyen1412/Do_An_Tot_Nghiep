<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isSidebarOpen = ref(true)

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}

const goToHome = () => {
  router.push('/owner/home')
}

const menuItems = [
  {
    id: 'revenue',
    label: 'Thống kê doanh thu',
    icon: '📊',
    path: '/owner/management/revenue',
  },
  {
    id: 'courts',
    label: 'Đăng tải sân',
    icon: '🏟️',
    path: '/owner/management/courts',
  },
]

const isActive = (path: string) => {
  return route.path === path
}
</script>

<template>
  <div class="owner-management-layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: !isSidebarOpen }">
      <div class="sidebar-header">
        <div class="logo-section">
          <div class="logo-icon">
            <img src="/Logo.png" alt="Logo" />
          </div>
          <transition name="fade">
            <div v-if="isSidebarOpen" class="logo-text">
              <span class="logo-title">Owner Panel</span>
              <span class="logo-subtitle">Management</span>
            </div>
          </transition>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.id"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <transition name="fade">
            <span v-if="isSidebarOpen" class="nav-label">{{ item.label }}</span>
          </transition>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <button class="footer-btn" @click="goToHome" :title="isSidebarOpen ? '' : 'Về trang chủ'">
          <span class="btn-icon">🏠</span>
          <transition name="fade">
            <span v-if="isSidebarOpen" class="btn-label">Về trang chủ</span>
          </transition>
        </button>
        <button
          class="footer-btn logout"
          @click="handleLogout"
          :title="isSidebarOpen ? '' : 'Đăng xuất'"
        >
          <span class="btn-icon">🚪</span>
          <transition name="fade">
            <span v-if="isSidebarOpen" class="btn-label">Đăng xuất</span>
          </transition>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="main-wrapper">
      <!-- Top Bar -->
      <header class="top-bar">
        <button class="toggle-btn" @click="toggleSidebar">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>

        <div class="top-bar-title">
          <h1>{{ menuItems.find((item) => isActive(item.path))?.label || 'Management' }}</h1>
        </div>

        <div class="user-info">
          <div class="user-avatar">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
          </div>
          <div class="user-details">
            <span class="user-name">{{ authStore.user?.full_name }}</span>
            <span class="user-role">Owner</span>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.owner-management-layout {
  display: flex;
  min-height: 100vh;
  background: #f8fafc;
}

/* Sidebar */
.sidebar {
  width: 280px;
  background: linear-gradient(180deg, #2d5016 0%, #1a3009 100%);
  color: white;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.1);
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 1000;
}

.sidebar.collapsed {
  width: 80px;
}

.sidebar-header {
  padding: 24px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 70px;
  height: 70px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  filter: drop-shadow(0 2px 6px rgba(255, 255, 255, 0.2));
  transition: transform 0.3s ease;
}

.logo-icon:hover {
  transform: scale(1.1);
}

.logo-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-title {
  font-size: 1.2rem;
  font-weight: 700;
  line-height: 1.2;
}

.logo-subtitle {
  font-size: 0.8rem;
  opacity: 0.8;
}

/* Navigation */
.sidebar-nav {
  flex: 1;
  padding: 20px 0;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
}

.nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: #fbbf24;
  transform: scaleY(0);
  transition: transform 0.3s ease;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.active {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
}

.nav-item.active::before {
  transform: scaleY(1);
}

.nav-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.nav-label {
  font-weight: 600;
  font-size: 0.95rem;
}

/* Sidebar Footer */
.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 600;
}

.footer-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(4px);
}

.footer-btn.logout {
  background: rgba(239, 68, 68, 0.2);
}

.footer-btn.logout:hover {
  background: rgba(239, 68, 68, 0.3);
}

.btn-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.btn-label {
  flex: 1;
}

/* Main Wrapper */
.main-wrapper {
  flex: 1;
  margin-left: 280px;
  transition: margin-left 0.3s ease;
  display: flex;
  flex-direction: column;
}

.sidebar.collapsed + .main-wrapper {
  margin-left: 80px;
}

/* Top Bar */
.top-bar {
  background: white;
  padding: 20px 32px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.toggle-btn {
  width: 40px;
  height: 40px;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-btn:hover {
  background: #e5e7eb;
}

.toggle-btn svg {
  width: 20px;
  height: 20px;
  color: #374151;
}

.top-bar-title {
  flex: 1;
}

.top-bar-title h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: #f9fafb;
  border-radius: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar svg {
  width: 24px;
  height: 24px;
  color: white;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: #1f2937;
}

.user-role {
  font-size: 0.75rem;
  color: #6b7280;
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 32px;
}

/* Fade Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 1024px) {
  .sidebar {
    width: 80px;
  }

  .sidebar.collapsed {
    width: 0;
    overflow: hidden;
  }

  .main-wrapper {
    margin-left: 80px;
  }

  .sidebar.collapsed + .main-wrapper {
    margin-left: 0;
  }

  .user-details {
    display: none;
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 0;
    overflow: hidden;
  }

  .sidebar.collapsed {
    width: 0;
  }

  .main-wrapper {
    margin-left: 0;
  }

  .top-bar {
    padding: 16px 20px;
  }

  .top-bar-title h1 {
    font-size: 1.2rem;
  }

  .main-content {
    padding: 20px;
  }
}
</style>
