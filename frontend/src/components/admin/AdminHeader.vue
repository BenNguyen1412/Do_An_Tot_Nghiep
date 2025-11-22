<template>
  <div class="admin-header">
    <div class="header-content">
      <div class="header-left">
        <div class="page-title-section">
          <h1 class="page-title">
            <slot name="title">Dashboard</slot>
          </h1>
          <div class="breadcrumb">
            <span class="breadcrumb-item">🏠 Home</span>
            <span class="breadcrumb-separator">/</span>
            <span class="breadcrumb-item active">
              <slot name="title">Dashboard</slot>
            </span>
          </div>
        </div>
      </div>

      <div class="header-actions">
        <!-- Notifications -->
        <div class="notification-btn" @click="toggleNotifications">
          <span class="notification-icon">🔔</span>
          <span class="notification-badge">3</span>
        </div>

        <!-- User Info -->
        <div class="user-info">
          <div class="user-avatar">
            <span class="avatar-text">{{ userInitials }}</span>
          </div>
          <div class="user-details">
            <span class="user-name">{{ authStore.user?.full_name || 'Admin' }}</span>
            <span class="user-role">{{ getRoleDisplay(authStore.user?.role) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const userInitials = computed(() => {
  const fullName = authStore.user?.full_name || 'Admin'
  const names = fullName.split(' ')
  if (names.length >= 2) {
    return (names[0][0] + names[names.length - 1][0]).toUpperCase()
  }
  return fullName.substring(0, 2).toUpperCase()
})

const getRoleDisplay = (role?: string) => {
  const roleMap: Record<string, string> = {
    admin: 'Super Admin',
    user: 'User',
    owner: 'Owner',
    enterprise: 'Enterprise',
  }
  return roleMap[role || 'admin'] || 'Admin'
}

const toggleNotifications = () => {
  console.log('Toggle notifications')
}
</script>

<style scoped>
.admin-header {
  height: 85px;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  z-index: 999;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header-content {
  height: 100%;
  padding: 0 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 100%;
}

.header-left {
  flex: 1;
}

.page-title-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  font-size: 26px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  letter-spacing: -0.5px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #6b7280;
}

.breadcrumb-item {
  transition: color 0.2s ease;
}

.breadcrumb-item:not(.active) {
  cursor: pointer;
}

.breadcrumb-item:not(.active):hover {
  color: #4169e1;
}

.breadcrumb-item.active {
  color: #4169e1;
  font-weight: 600;
}

.breadcrumb-separator {
  color: #d1d5db;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* Notification Button */
.notification-btn {
  position: relative;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9fafb;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1.5px solid transparent;
}

.notification-btn:hover {
  background: #f3f4f6;
  border-color: #e5e7eb;
}

.notification-icon {
  font-size: 20px;
}

.notification-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 18px;
  height: 18px;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #fff;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

/* User Info */
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px 8px 8px;
  background: #f9fafb;
  border: 1.5px solid #e5e7eb;
  border-radius: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #4169e1 0%, #5a7fee 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #fff;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(65, 105, 225, 0.3);
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1;
}

.user-role {
  font-size: 12px;
  color: #6b7280;
  line-height: 1;
}
</style>
