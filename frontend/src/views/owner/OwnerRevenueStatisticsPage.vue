<script setup lang="ts">
import { ref, computed } from 'vue'

// Filter states
const timeFilter = ref<'day' | 'month' | 'year'>('month')
const selectedDate = ref(new Date().toISOString().split('T')[0])
const selectedMonth = ref(new Date().toISOString().slice(0, 7))
const selectedYear = ref(new Date().getFullYear().toString())

// Mock data - sẽ được thay thế bằng API call
const revenueData = ref({
  total: 45800000,
  bookings: 156,
  averagePerBooking: 293589,
  growth: 12.5,
})

const chartData = ref([
  { label: '00:00', value: 0 },
  { label: '06:00', value: 1200000 },
  { label: '09:00', value: 2500000 },
  { label: '12:00', value: 3800000 },
  { label: '15:00', value: 5200000 },
  { label: '18:00', value: 8900000 },
  { label: '21:00', value: 6500000 },
  { label: '23:59', value: 4200000 },
])

const topCourts = ref([
  { name: 'Sân VIP A1', revenue: 12500000, bookings: 42, growth: 15.2 },
  { name: 'Sân Premium B2', revenue: 9800000, bookings: 38, growth: 8.7 },
  { name: 'Sân Standard C3', revenue: 7600000, bookings: 35, growth: -2.3 },
  { name: 'Sân VIP A2', revenue: 6900000, bookings: 28, growth: 22.1 },
])

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
  }).format(value)
}

const formatPercent = (value: number) => {
  return value > 0 ? `+${value.toFixed(1)}%` : `${value.toFixed(1)}%`
}

const maxChartValue = computed(() => {
  return Math.max(...chartData.value.map((d) => d.value))
})
</script>

<template>
  <div class="revenue-statistics-page">
    <!-- Filters -->
    <div class="filters-section">
      <div class="filter-group">
        <label class="filter-label">Xem theo:</label>
        <div class="filter-buttons">
          <button
            class="filter-btn"
            :class="{ active: timeFilter === 'day' }"
            @click="timeFilter = 'day'"
          >
            📅 Ngày
          </button>
          <button
            class="filter-btn"
            :class="{ active: timeFilter === 'month' }"
            @click="timeFilter = 'month'"
          >
            📆 Tháng
          </button>
          <button
            class="filter-btn"
            :class="{ active: timeFilter === 'year' }"
            @click="timeFilter = 'year'"
          >
            📊 Năm
          </button>
        </div>
      </div>

      <div class="date-selector">
        <input v-if="timeFilter === 'day'" v-model="selectedDate" type="date" class="date-input" />
        <input
          v-else-if="timeFilter === 'month'"
          v-model="selectedMonth"
          type="month"
          class="date-input"
        />
        <input
          v-else
          v-model="selectedYear"
          type="number"
          class="date-input"
          min="2020"
          :max="new Date().getFullYear()"
        />
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card primary">
        <div class="stat-icon">💰</div>
        <div class="stat-content">
          <span class="stat-label">Tổng doanh thu</span>
          <span class="stat-value">{{ formatCurrency(revenueData.total) }}</span>
          <span class="stat-change positive">{{ formatPercent(revenueData.growth) }}</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">🎯</div>
        <div class="stat-content">
          <span class="stat-label">Số lượt đặt</span>
          <span class="stat-value">{{ revenueData.bookings }}</span>
          <span class="stat-change positive">+18 lượt</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">📈</div>
        <div class="stat-content">
          <span class="stat-label">Trung bình/đặt</span>
          <span class="stat-value">{{ formatCurrency(revenueData.averagePerBooking) }}</span>
          <span class="stat-change">~</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">⭐</div>
        <div class="stat-content">
          <span class="stat-label">Đánh giá TB</span>
          <span class="stat-value">4.8 / 5.0</span>
          <span class="stat-change positive">+0.2 điểm</span>
        </div>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="chart-section">
      <div class="section-header">
        <h2 class="section-title">📊 Biểu đồ doanh thu theo giờ</h2>
        <button class="export-btn">
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
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
            />
          </svg>
          Xuất báo cáo
        </button>
      </div>

      <div class="chart-container">
        <div class="chart-wrapper">
          <div
            v-for="(item, index) in chartData"
            :key="index"
            class="chart-bar"
            :style="{ height: (item.value / maxChartValue) * 100 + '%' }"
          >
            <div class="bar-tooltip">{{ formatCurrency(item.value) }}</div>
          </div>
        </div>
        <div class="chart-labels">
          <span v-for="(item, index) in chartData" :key="index" class="chart-label">{{
            item.label
          }}</span>
        </div>
      </div>
    </div>

    <!-- Top Courts Section -->
    <div class="top-courts-section">
      <div class="section-header">
        <h2 class="section-title">🏆 Top sân có doanh thu cao nhất</h2>
      </div>

      <div class="courts-table">
        <div class="table-header">
          <div class="table-cell">Thứ hạng</div>
          <div class="table-cell">Tên sân</div>
          <div class="table-cell">Doanh thu</div>
          <div class="table-cell">Lượt đặt</div>
          <div class="table-cell">Tăng trưởng</div>
        </div>
        <div v-for="(court, index) in topCourts" :key="index" class="table-row">
          <div class="table-cell rank">
            <span class="rank-badge" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
          </div>
          <div class="table-cell court-name">
            <span class="court-icon">🏟️</span>
            {{ court.name }}
          </div>
          <div class="table-cell revenue">{{ formatCurrency(court.revenue) }}</div>
          <div class="table-cell bookings">{{ court.bookings }} lượt</div>
          <div class="table-cell growth">
            <span class="growth-badge" :class="court.growth > 0 ? 'positive' : 'negative'">
              {{ formatPercent(court.growth) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.revenue-statistics-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Filters */
.filters-section {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-label {
  font-weight: 600;
  color: #374151;
  font-size: 0.95rem;
}

.filter-buttons {
  display: flex;
  gap: 8px;
}

.filter-btn {
  padding: 10px 20px;
  background: #f3f4f6;
  border: 2px solid transparent;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.9rem;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-btn:hover {
  background: #e5e7eb;
  color: #374151;
}

.filter-btn.active {
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  color: white;
  border-color: #2d5016;
}

.date-selector {
  margin-left: auto;
}

.date-input {
  padding: 10px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.9rem;
  color: #374151;
  transition: all 0.3s ease;
}

.date-input:focus {
  outline: none;
  border-color: #2d5016;
  box-shadow: 0 0 0 3px rgba(45, 80, 22, 0.1);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-card.primary {
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  color: white;
}

.stat-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 0.85rem;
  opacity: 0.8;
  font-weight: 500;
}

.stat-card.primary .stat-label {
  color: rgba(255, 255, 255, 0.9);
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 800;
  line-height: 1;
}

.stat-change {
  font-size: 0.8rem;
  font-weight: 600;
}

.stat-change.positive {
  color: #10b981;
}

.stat-card.primary .stat-change.positive {
  color: #fbbf24;
}

.stat-change.negative {
  color: #ef4444;
}

/* Chart Section */
.chart-section,
.top-courts-section {
  background: white;
  padding: 28px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.export-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.export-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(45, 80, 22, 0.3);
}

.export-btn svg {
  width: 18px;
  height: 18px;
}

.chart-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chart-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  height: 300px;
  padding: 20px 0;
}

.chart-bar {
  flex: 1;
  background: linear-gradient(180deg, #4a7c2c 0%, #2d5016 100%);
  border-radius: 8px 8px 0 0;
  position: relative;
  min-height: 20px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.chart-bar:hover {
  background: linear-gradient(180deg, #fbbf24 0%, #f59e0b 100%);
}

.chart-bar:hover .bar-tooltip {
  opacity: 1;
  transform: translateY(-8px);
}

.bar-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #1f2937;
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
  opacity: 0;
  transition: all 0.3s ease;
  pointer-events: none;
}

.chart-labels {
  display: flex;
  gap: 12px;
}

.chart-label {
  flex: 1;
  text-align: center;
  font-size: 0.8rem;
  color: #6b7280;
  font-weight: 600;
}

/* Top Courts Table */
.courts-table {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.table-header,
.table-row {
  display: grid;
  grid-template-columns: 80px 1fr 200px 150px 150px;
  gap: 16px;
  padding: 16px 20px;
}

.table-header {
  background: #f9fafb;
  border-bottom: 2px solid #e5e7eb;
  font-weight: 700;
  font-size: 0.85rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.table-row {
  border-bottom: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.table-row:hover {
  background: #f9fafb;
}

.table-row:last-child {
  border-bottom: none;
}

.table-cell {
  display: flex;
  align-items: center;
}

.rank-badge {
  width: 32px;
  height: 32px;
  background: #e5e7eb;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.9rem;
  color: #6b7280;
}

.rank-badge.rank-1 {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: white;
}

.rank-badge.rank-2 {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
  color: white;
}

.rank-badge.rank-3 {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  color: white;
}

.court-name {
  font-weight: 600;
  color: #1f2937;
  gap: 8px;
}

.court-icon {
  font-size: 1.2rem;
}

.revenue {
  font-weight: 700;
  color: #2d5016;
}

.bookings {
  color: #6b7280;
  font-weight: 600;
}

.growth-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 0.85rem;
}

.growth-badge.positive {
  background: #d1fae5;
  color: #10b981;
}

.growth-badge.negative {
  background: #fee2e2;
  color: #ef4444;
}

/* Responsive */
@media (max-width: 1024px) {
  .page-header h1 {
    font-size: 1.75rem;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  .table-header,
  .table-row {
    grid-template-columns: 60px 1fr 150px 120px 120px;
    gap: 12px;
    padding: 12px 16px;
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 20px 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .export-btn {
    width: 100%;
    justify-content: center;
  }

  .filters-section {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .date-selector {
    margin-left: 0;
    width: 100%;
    justify-content: space-between;
  }

  .date-input {
    width: 100%;
    max-width: none;
  }

  .stats-grid {
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

  .chart-section,
  .revenue-table-section {
    padding: 20px;
  }

  .section-title {
    font-size: 1.25rem;
  }

  .chart-wrapper {
    height: 200px;
  }

  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .table-header {
    display: none;
  }

  .table-cell {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #f3f4f6;
  }

  .table-cell::before {
    content: attr(data-label);
    font-weight: 600;
    color: #6b7280;
  }

  .table-row {
    padding: 12px;
    border-bottom: 1px solid #e5e7eb;
  }
}

@media (max-width: 480px) {
  .page-container {
    padding: 16px 12px;
  }

  .page-header h1 {
    font-size: 1.35rem;
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

  .chart-section,
  .revenue-table-section {
    padding: 16px;
  }

  .section-title {
    font-size: 1.1rem;
  }

  .export-btn {
    padding: 10px 16px;
    font-size: 0.9rem;
  }

  .date-input {
    padding: 8px 12px;
    font-size: 0.9rem;
  }
}
</style>
