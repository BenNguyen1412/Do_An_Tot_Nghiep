<template>
  <AdminDashboardLayout>
    <template #title>Requests Management</template>

    <div class="request-page">
      <!-- Stats Row -->
      <div class="stats-row">
        <div class="stat-item">
          <div class="stat-icon orange">📋</div>
          <div class="stat-info">
            <div class="stat-value">156</div>
            <div class="stat-label">Total Requests</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon yellow">⏳</div>
          <div class="stat-info">
            <div class="stat-value">23</div>
            <div class="stat-label">Pending</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon green">✓</div>
          <div class="stat-info">
            <div class="stat-value">118</div>
            <div class="stat-label">Approved</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon red">✕</div>
          <div class="stat-info">
            <div class="stat-value">15</div>
            <div class="stat-label">Rejected</div>
          </div>
        </div>
      </div>

      <div class="request-table-card">
        <div class="card-header">
          <h2 class="card-title">📋 All Requests</h2>
          <div class="card-actions">
            <button class="filter-btn">
              <span>🔍</span>
              <span>Filter</span>
            </button>
            <button class="export-btn">
              <span>📥</span>
              <span>Export</span>
            </button>
          </div>
        </div>

        <table class="request-table">
          <thead>
            <tr>
              <th>Request Type</th>
              <th>Requester</th>
              <th>Detail</th>
              <th>Date</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="request in requests" :key="request.id" class="table-row">
              <td>
                <div class="request-name">
                  <div class="request-icon-wrapper" :class="request.type">
                    <span class="request-icon">{{ request.icon }}</span>
                  </div>
                  <div class="request-details">
                    <div class="name">{{ request.name }}</div>
                    <div class="request-type-tag">{{ request.type }}</div>
                  </div>
                </div>
              </td>
              <td>
                <div class="requester-info">
                  <div class="requester-avatar">{{ request.requesterInitials }}</div>
                  <span class="requester-name">{{ request.requester }}</span>
                </div>
              </td>
              <td>
                <a :href="request.detail" class="detail-link" target="_blank">{{
                  request.detail
                }}</a>
              </td>
              <td>
                <span class="date-text">{{ request.time }}</span>
              </td>
              <td>
                <span :class="['status-badge', request.status.toLowerCase()]">{{
                  request.status
                }}</span>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="action-btn approve-btn" title="Approve">✓</button>
                  <button class="action-btn reject-btn" title="Reject">✕</button>
                  <button class="action-btn view-btn" title="View">👁️</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="pagination">
          <button class="page-btn prev-btn">‹</button>
          <button class="page-btn active">1</button>
          <button class="page-btn">2</button>
          <button class="page-btn">3</button>
          <button class="page-btn">4</button>
          <button class="page-btn">5</button>
          <span class="page-dots">...</span>
          <button class="page-btn next-btn">›</button>
        </div>
      </div>
    </div>
  </AdminDashboardLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AdminDashboardLayout from '@/layouts/AdminDashboardLayout.vue'

const requests = ref([
  {
    id: 1,
    name: 'Upload court A',
    detail: 'View Document',
    time: '05/11/2025',
    icon: '🏟️',
    type: 'Court',
    status: 'Pending',
    requester: 'Nguyễn Văn A',
    requesterInitials: 'NA',
  },
  {
    id: 2,
    name: 'Upload court B',
    detail: 'View Document',
    time: '04/11/2025',
    icon: '🏟️',
    type: 'Court',
    status: 'Approved',
    requester: 'Trần Thị B',
    requesterInitials: 'TB',
  },
  {
    id: 3,
    name: 'Upload ad',
    detail: 'View Document',
    time: '03/11/2025',
    icon: '📢',
    type: 'Advertisement',
    status: 'Pending',
    requester: 'Lê Văn C',
    requesterInitials: 'LC',
  },
  {
    id: 4,
    name: 'Partnership Request',
    detail: 'View Document',
    time: '02/11/2025',
    icon: '🤝',
    type: 'Partnership',
    status: 'Approved',
    requester: 'Phạm Thị D',
    requesterInitials: 'PD',
  },
  {
    id: 5,
    name: 'Upload court C',
    detail: 'View Document',
    time: '01/11/2025',
    icon: '🏟️',
    type: 'Court',
    status: 'Rejected',
    requester: 'Hoàng Văn E',
    requesterInitials: 'HE',
  },
])
</script>

<style scoped>
.request-page {
  max-width: 1400px;
  margin: 0 auto;
}

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 28px;
}

.stat-item {
  background: #fff;
  border-radius: 14px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.stat-icon.orange {
  background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%);
}

.stat-icon.yellow {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
}

.stat-icon.green {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
}

.stat-icon.red {
  background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  color: #1f2937;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
  font-weight: 500;
}

/* Table Card */
.request-table-card {
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f3f4f6;
}

.card-title {
  font-size: 22px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.card-actions {
  display: flex;
  gap: 12px;
}

.filter-btn,
.export-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  background: #f3f4f6;
  color: #374151;
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-btn:hover,
.export-btn:hover {
  background: #e5e7eb;
  border-color: #d1d5db;
}

/* Table */
.request-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  margin-bottom: 28px;
}

.request-table thead {
  background: #f9fafb;
}

.request-table th {
  text-align: left;
  padding: 16px 20px;
  font-size: 13px;
  font-weight: 700;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #e5e7eb;
}

.request-table tbody .table-row {
  border-bottom: 1px solid #f3f4f6;
  transition: all 0.2s ease;
}

.request-table tbody .table-row:hover {
  background: #f9fafb;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.request-table tbody .table-row:last-child {
  border-bottom: none;
}

.request-table td {
  padding: 20px;
  font-size: 15px;
  color: #1f2937;
  vertical-align: middle;
}

.request-name {
  display: flex;
  align-items: center;
  gap: 14px;
}

.request-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.request-icon-wrapper.Court {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.25);
}

.request-icon-wrapper.Advertisement {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.25);
}

.request-icon-wrapper.Partnership {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.25);
}

.request-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.request-details .name {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1;
}

.request-type-tag {
  display: inline-block;
  padding: 3px 10px;
  background: #e0e7ff;
  color: #4338ca;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  width: fit-content;
}

.requester-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.requester-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  box-shadow: 0 2px 6px rgba(99, 102, 241, 0.25);
}

.requester-name {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.detail-link {
  color: #4169e1;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.3s ease;
}

.detail-link:hover {
  color: #3155c4;
  text-decoration: underline;
}

.date-text {
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
}

.status-badge {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.status-badge.pending {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.approved {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.rejected {
  background: #fee2e2;
  color: #991b1b;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1.5px solid #e5e7eb;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
  font-weight: bold;
}

.action-btn:hover {
  transform: translateY(-2px);
}

.approve-btn:hover {
  background: #d1fae5;
  border-color: #10b981;
  color: #065f46;
}

.reject-btn:hover {
  background: #fee2e2;
  border-color: #ef4444;
  color: #991b1b;
}

.view-btn:hover {
  background: #dbeafe;
  border-color: #3b82f6;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding-top: 8px;
}

.page-btn {
  min-width: 40px;
  height: 40px;
  border: 1.5px solid #e5e7eb;
  background: #fff;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-btn:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
  color: #374151;
}

.page-btn.active {
  background: linear-gradient(135deg, #4169e1 0%, #5a7fee 100%);
  border-color: #4169e1;
  color: #fff;
  box-shadow: 0 4px 12px rgba(65, 105, 225, 0.3);
}

.page-dots {
  padding: 0 8px;
  color: #9ca3af;
  font-weight: bold;
}

.prev-btn,
.next-btn {
  font-size: 18px;
  font-weight: bold;
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: 1fr;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .card-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .request-table {
    font-size: 13px;
  }
}
</style>
