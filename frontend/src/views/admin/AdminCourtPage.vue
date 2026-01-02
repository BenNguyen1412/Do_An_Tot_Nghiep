<template>
  <AdminDashboardLayout>
    <template #title>Courts Management</template>

    <div class="court-page">
      <!-- Stats Row -->
      <div class="stats-row">
        <div class="stat-item">
          <div class="stat-icon green">🏟️</div>
          <div class="stat-info">
            <div class="stat-value">48</div>
            <div class="stat-label">Total Courts</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon blue">✓</div>
          <div class="stat-info">
            <div class="stat-value">42</div>
            <div class="stat-label">Active</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon orange">⏸️</div>
          <div class="stat-info">
            <div class="stat-value">6</div>
            <div class="stat-label">Inactive</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon purple">📈</div>
          <div class="stat-info">
            <div class="stat-value">+8</div>
            <div class="stat-label">This Month</div>
          </div>
        </div>
      </div>

      <div class="court-table-card">
        <div class="card-header">
          <h2 class="card-title">🏟️ All Courts</h2>
          <div class="card-actions">
            <button class="filter-btn">
              <span>🔍</span>
              <span>Filter</span>
            </button>
          </div>
        </div>

        <table class="court-table">
          <thead>
            <tr>
              <th>Court Name</th>
              <th>Location</th>
              <th>Phone Number</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="court in courts" :key="court.id" class="table-row">
              <td>
                <div class="court-name">
                  <div class="court-icon-wrapper">
                    <span class="court-icon">🏟️</span>
                  </div>
                  <div class="court-details">
                    <div class="name">{{ court.name }}</div>
                    <div class="court-type">{{ court.type }}</div>
                  </div>
                </div>
              </td>
              <td>
                <div class="location-text">
                  <span class="location-icon">📍</span>
                  <span>{{ court.location }}</span>
                </div>
              </td>
              <td>
                <div class="phone-text">
                  <span class="phone-icon">📞</span>
                  <span>{{ court.phoneNumber }}</span>
                </div>
              </td>
              <td>
                <span :class="['status-badge', court.status.toLowerCase()]">{{
                  court.status
                }}</span>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="action-btn view-btn" title="View">👁️</button>
                  <button class="action-btn edit-btn" title="Edit">✏️</button>
                  <button class="action-btn delete-btn" title="Delete">🗑️</button>
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

const courts = ref([
  {
    id: 1,
    name: 'Court A',
    location: '10 Trần Tấn, TP HCM',
    phoneNumber: '0909111333',
    type: 'Indoor',
    status: 'Active',
  },
  {
    id: 2,
    name: 'Court B',
    location: '25 Nguyễn Huệ, TP HCM',
    phoneNumber: '0909222444',
    type: 'Outdoor',
    status: 'Active',
  },
  {
    id: 3,
    name: 'Court C',
    location: '88 Lê Lợi, TP HCM',
    phoneNumber: '0909333555',
    type: 'Indoor',
    status: 'Inactive',
  },
  {
    id: 4,
    name: 'Court D',
    location: '45 Pasteur, Quận 1',
    phoneNumber: '0909444666',
    type: 'Indoor',
    status: 'Active',
  },
  {
    id: 5,
    name: 'Court E',
    location: '120 Hai Bà Trưng, Quận 3',
    phoneNumber: '0909555777',
    type: 'Outdoor',
    status: 'Active',
  },
])
</script>

<style scoped>
.court-page {
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

.stat-icon.blue {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
}

.stat-icon.green {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
}

.stat-icon.orange {
  background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%);
}

.stat-icon.purple {
  background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 100%);
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
.court-table-card {
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

.filter-btn {
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

.filter-btn:hover {
  background: #e5e7eb;
  border-color: #d1d5db;
}

/* Table */
.court-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  margin-bottom: 28px;
}

.court-table thead {
  background: #f9fafb;
}

.court-table th {
  text-align: left;
  padding: 16px 20px;
  font-size: 13px;
  font-weight: 700;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #e5e7eb;
}

.court-table tbody .table-row {
  border-bottom: 1px solid #f3f4f6;
  transition: all 0.2s ease;
}

.court-table tbody .table-row:hover {
  background: #f9fafb;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.court-table tbody .table-row:last-child {
  border-bottom: none;
}

.court-table td {
  padding: 20px;
  font-size: 15px;
  color: #1f2937;
  vertical-align: middle;
}

.court-name {
  display: flex;
  align-items: center;
  gap: 14px;
}

.court-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.25);
}

.court-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.court-details .name {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1;
}

.court-type {
  display: inline-block;
  padding: 3px 10px;
  background: #d1fae5;
  color: #065f46;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  width: fit-content;
}

.location-text,
.phone-text {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  font-size: 14px;
}

.location-icon,
.phone-icon {
  font-size: 16px;
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

.status-badge.active {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.inactive {
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
}

.action-btn:hover {
  transform: translateY(-2px);
}

.view-btn:hover {
  background: #dbeafe;
  border-color: #3b82f6;
}

.edit-btn:hover {
  background: #fef3c7;
  border-color: #f59e0b;
}

.delete-btn:hover {
  background: #fee2e2;
  border-color: #ef4444;
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

@media (max-width: 1024px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  .card-header h2 {
    font-size: 1.35rem;
  }

  .court-table {
    font-size: 14px;
  }
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-value {
    font-size: 1.75rem;
  }

  .stat-label {
    font-size: 0.85rem;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .card-header h2 {
    font-size: 1.25rem;
  }

  .card-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .filter-btn,
  .refresh-btn {
    flex: 1;
    min-width: 120px;
  }

  .court-table {
    font-size: 13px;
  }

  .court-table th,
  .court-table td {
    padding: 10px 8px;
  }
}

@media (max-width: 480px) {
  .page-header h1 {
    font-size: 1.5rem;
  }

  .stat-card {
    padding: 12px;
  }

  .stat-value {
    font-size: 1.5rem;
  }

  .stat-label {
    font-size: 0.8rem;
  }

  .card-header h2 {
    font-size: 1.1rem;
  }

  .filter-btn,
  .refresh-btn {
    font-size: 0.85rem;
    padding: 8px 14px;
  }

  .court-table {
    font-size: 12px;
  }

  .court-table th,
  .court-table td {
    padding: 8px 6px;
  }
}
</style>
