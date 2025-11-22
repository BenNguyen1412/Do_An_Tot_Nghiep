<template>
  <div class="admin-dashboard-layout">
    <AdminSidebar />
    <div class="main-content">
      <AdminHeader>
        <template #title>
          <slot name="title">Dashboard</slot>
        </template>
      </AdminHeader>
      <div class="content-area">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AdminSidebar from '@/components/admin/AdminSidebar.vue'
import AdminHeader from '@/components/admin/AdminHeader.vue'
</script>

<style scoped>
.admin-dashboard-layout {
  display: flex;
  min-height: 100vh;
  background: #f5f5f5;
}

.main-content {
  flex: 1;
  margin-left: 280px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.content-area {
  flex: 1;
  padding: 32px 40px;
  overflow-y: auto;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}
</style>
