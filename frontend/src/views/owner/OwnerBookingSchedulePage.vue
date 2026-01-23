<template>
  <div class="booking-schedule-container">
    <div class="page-header">
      <h1 class="page-title">Quản Lý Lịch Đặt Sân</h1>
      <p class="page-subtitle">Xem và quản lý tất cả lịch đặt sân của các sân bạn sở hữu</p>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid" v-if="bookingSummary">
      <div class="stat-card">
        <div class="stat-icon total">📊</div>
        <div class="stat-content">
          <h3>{{ bookingSummary.total_bookings }}</h3>
          <p>Tổng lượt đặt</p>
          <span class="stat-period">Tuần hiện tại</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon active">🎾</div>
        <div class="stat-content">
          <h3>{{ bookingSummary.active_bookings }}</h3>
          <p>Đang hoạt động</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon completed">✅</div>
        <div class="stat-content">
          <h3>{{ bookingSummary.completed_bookings }}</h3>
          <p>Đã hoàn thành</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon cancelled">❌</div>
        <div class="stat-content">
          <h3>{{ bookingSummary.cancelled_bookings }}</h3>
          <p>Đã hủy</p>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filter-row">
        <div class="filter-group">
          <label>Từ ngày:</label>
          <input type="date" v-model="filters.startDate" @change="loadBookings" />
        </div>
        <div class="filter-group">
          <label>Đến ngày:</label>
          <input type="date" v-model="filters.endDate" @change="loadBookings" />
        </div>
        <div class="filter-group">
          <label>Sân:</label>
          <select v-model="filters.individualCourtId" @change="loadBookings">
            <option :value="null">Tất cả các sân</option>
            <option v-for="court in allIndividualCourts" :key="court.id" :value="court.id">
              {{ court.name }}
            </option>
          </select>
        </div>
        <div class="filter-group">
          <label>Trạng thái:</label>
          <select v-model="filters.status" @change="loadBookings">
            <option :value="null">Tất cả</option>
            <option value="active">Đang hoạt động</option>
            <option value="completed">Đã hoàn thành</option>
            <option value="cancelled">Đã hủy</option>
          </select>
        </div>
        <button class="btn-reset" @click="resetFilters">🔄 Đặt lại</button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Đang tải dữ liệu...</p>
    </div>

    <!-- Bookings List -->
    <div v-else-if="bookings.length > 0" class="bookings-section">
      <h2 class="section-title">Danh sách lịch đặt ({{ bookings.length }} kết quả)</h2>

      <!-- Group by date -->
      <div v-for="(group, date) in groupedBookings" :key="date" class="date-group">
        <h3 class="date-header">{{ formatDateHeader(date) }}</h3>
        <div class="bookings-grid">
          <div
            v-for="booking in group"
            :key="booking.id"
            class="booking-card"
            :class="'status-' + booking.status"
          >
            <div class="booking-header">
              <span class="booking-time">
                ⏰ {{ booking.start_time }} - {{ booking.end_time }}
              </span>
              <span class="booking-status" :class="'badge-' + booking.status">
                {{ getStatusText(booking.status) }}
              </span>
            </div>

            <div class="booking-body">
              <div class="booking-info">
                <p class="court-name">
                  <strong>🏟️ {{ booking.court_name }}</strong>
                </p>
                <p class="individual-court">
                  {{ booking.individual_court.name }}
                </p>
              </div>

              <div class="booking-customer">
                <p class="customer-name">
                  <strong>👤 {{ booking.customer_name || booking.user.full_name }}</strong>
                </p>
                <p class="customer-contact" v-if="!booking.customer_name && booking.user.email">
                  📧 {{ booking.user.email }}
                </p>
                <p class="customer-phone">📱 {{ booking.phone_number }}</p>
              </div>

              <div class="booking-meta">
                <small>Đặt lúc: {{ formatDateTime(booking.created_at) }}</small>
              </div>
            </div>

            <div class="booking-actions">
              <button
                v-if="booking.status === 'active'"
                @click="updateBookingStatus(booking.id, 'cancelled')"
                class="btn-cancel"
              >
                ✗ Hủy
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <div class="empty-icon">📅</div>
      <h3>Không có lịch đặt sân</h3>
      <p>Không tìm thấy lịch đặt sân nào với bộ lọc hiện tại.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from '@/utils/axios'

interface User {
  id: number
  full_name: string
  email: string
  phone_number?: string
}

interface IndividualCourt {
  id: number
  name: string
  court_id: number
  is_active: boolean
}

interface Booking {
  id: number
  booking_date: string
  start_time: string
  end_time: string
  phone_number: string
  customer_name?: string
  status: string
  created_at: string
  court_name: string
  individual_court: IndividualCourt
  user: User
}

interface Court {
  id: number
  name: string
  individual_courts?: IndividualCourt[]
}

const bookings = ref<Booking[]>([])
const courtsWithIndividual = ref<Court[]>([])
const loading = ref(false)

const filters = ref({
  startDate: '',
  endDate: '',
  individualCourtId: null as number | null,
  status: null as string | null,
})

// Calculate summary from actual bookings data
const bookingSummary = computed(() => {
  const total = bookings.value.length
  const active = bookings.value.filter((b) => b.status === 'active').length
  const completed = bookings.value.filter((b) => b.status === 'completed').length
  const cancelled = bookings.value.filter((b) => b.status === 'cancelled').length

  return {
    total_bookings: total,
    active_bookings: active,
    completed_bookings: completed,
    cancelled_bookings: cancelled,
    period_days: 7, // Tuần hiện tại
  }
})

// Initialize default date range (Monday to Sunday of current week)
const initializeDateRange = () => {
  const today = new Date()
  const dayOfWeek = today.getDay() // 0 = Sunday, 1 = Monday, ..., 6 = Saturday

  // Calculate Monday of current week
  const monday = new Date(today)
  const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek // If Sunday, go back 6 days, else go to Monday
  monday.setDate(today.getDate() + diff)

  // Calculate Sunday of current week
  const sunday = new Date(monday)
  sunday.setDate(monday.getDate() + 6)

  filters.value.startDate = monday.toISOString().split('T')[0]
  filters.value.endDate = sunday.toISOString().split('T')[0]
}

// Flatten all individual courts from all venues
const allIndividualCourts = computed(() => {
  const courts: IndividualCourt[] = []
  courtsWithIndividual.value.forEach((venue) => {
    if (venue.individual_courts) {
      courts.push(...venue.individual_courts)
    }
  })
  return courts
})

// Group bookings by date
const groupedBookings = computed(() => {
  const groups: Record<string, Booking[]> = {}

  bookings.value.forEach((booking) => {
    const date = booking.booking_date.split('T')[0]
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(booking)
  })

  // Sort dates descending
  const sortedGroups: Record<string, Booking[]> = {}
  Object.keys(groups)
    .sort((a, b) => b.localeCompare(a))
    .forEach((date) => {
      sortedGroups[date] = groups[date].sort((a, b) => a.start_time.localeCompare(b.start_time))
    })

  return sortedGroups
})

const loadCourts = async () => {
  try {
    const response = await axios.get('/courts/my')
    const venues = response.data

    // Load individual courts for each venue
    const venuesWithIndividual = await Promise.all(
      venues.map(async (venue: Court) => {
        try {
          const individualResponse = await axios.get(`/courts/${venue.id}/individual-courts`)
          return {
            ...venue,
            individual_courts: individualResponse.data,
          }
        } catch (error) {
          console.error(`Error loading individual courts for ${venue.name}:`, error)
          return {
            ...venue,
            individual_courts: [],
          }
        }
      }),
    )

    courtsWithIndividual.value = venuesWithIndividual
  } catch (error) {
    console.error('Error loading courts:', error)
  }
}

const loadBookings = async () => {
  loading.value = true
  try {
    const params: {
      start_date?: string
      end_date?: string
      individual_court_id?: number
      status?: string
    } = {}

    if (filters.value.startDate) params.start_date = filters.value.startDate
    if (filters.value.endDate) params.end_date = filters.value.endDate
    if (filters.value.individualCourtId)
      params.individual_court_id = filters.value.individualCourtId
    if (filters.value.status) params.status = filters.value.status

    const response = await axios.get('/owner/bookings', { params })
    bookings.value = response.data
    console.log('Bookings data:', response.data)
  } catch (error) {
    console.error('Error loading bookings:', error)
    alert('Không thể tải danh sách đặt sân')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  initializeDateRange()
  filters.value.individualCourtId = null
  filters.value.status = null
  loadBookings()
}

const updateBookingStatus = async (bookingId: number, newStatus: string) => {
  const confirmMessage =
    newStatus === 'completed' ? 'Xác nhận hoàn thành lịch đặt này?' : 'Xác nhận hủy lịch đặt này?'

  if (!confirm(confirmMessage)) return

  try {
    await axios.put(`/bookings/${bookingId}`, { status: newStatus })
    alert('Cập nhật trạng thái thành công!')
    loadBookings() // Reload lại sẽ tự động update summary
  } catch (error) {
    console.error('Error updating booking:', error)
    alert('Không thể cập nhật trạng thái')
  }
}

const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    active: 'Đang hoạt động',
    completed: 'Đã hoàn thành',
    cancelled: 'Đã hủy',
  }
  return statusMap[status] || status
}

const formatDateHeader = (dateStr: string): string => {
  const date = new Date(dateStr)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  const dateOnly = date.toISOString().split('T')[0]
  const todayOnly = today.toISOString().split('T')[0]
  const yesterdayOnly = yesterday.toISOString().split('T')[0]

  if (dateOnly === todayOnly) {
    return (
      'Hôm nay - ' +
      date.toLocaleDateString('vi-VN', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    )
  } else if (dateOnly === yesterdayOnly) {
    return (
      'Hôm qua - ' +
      date.toLocaleDateString('vi-VN', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    )
  }

  return date.toLocaleDateString('vi-VN', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const formatDateTime = (dateTimeStr: string): string => {
  const date = new Date(dateTimeStr)
  return date.toLocaleString('vi-VN')
}

onMounted(() => {
  initializeDateRange()
  loadCourts()
  loadBookings()
})
</script>

<style scoped>
.booking-schedule-container {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: bold;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  color: #718096;
  font-size: 1rem;
}

/* Statistics Cards */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 2.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.stat-icon.total {
  background: #e6f7ff;
}

.stat-icon.active {
  background: #d4edda;
}

.stat-icon.completed {
  background: #cfe2ff;
}

.stat-icon.cancelled {
  background: #f8d7da;
}

.stat-content h3 {
  font-size: 2rem;
  font-weight: bold;
  margin: 0;
  color: #1a202c;
}

.stat-content p {
  margin: 0.25rem 0 0 0;
  color: #718096;
  font-size: 0.9rem;
}

.stat-period {
  font-size: 0.75rem;
  color: #a0aec0;
}

/* Filters */
.filters-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 150px;
  flex: 1;
}

.filter-group label {
  font-weight: 500;
  color: #4a5568;
  font-size: 0.9rem;
}

.filter-group input,
.filter-group select {
  padding: 0.625rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: border-color 0.2s;
}

.filter-group input:focus,
.filter-group select:focus {
  outline: none;
  border-color: #3182ce;
}

.btn-reset {
  padding: 0.625rem 1.25rem;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-reset:hover {
  background: #edf2f7;
  border-color: #cbd5e0;
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 4rem 2rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e2e8f0;
  border-top-color: #3182ce;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Bookings Section */
.bookings-section {
  margin-top: 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #1a202c;
  margin-bottom: 1.5rem;
}

.date-group {
  margin-bottom: 2rem;
}

.date-header {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e2e8f0;
}

.bookings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.booking-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #e2e8f0;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.booking-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.booking-card.status-active {
  border-left-color: #48bb78;
}

.booking-card.status-completed {
  border-left-color: #4299e1;
}

.booking-card.status-cancelled {
  border-left-color: #f56565;
}

.booking-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.booking-time {
  font-weight: 600;
  color: #2d3748;
  font-size: 1rem;
}

.booking-status {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-active {
  background: #c6f6d5;
  color: #22543d;
}

.badge-completed {
  background: #bee3f8;
  color: #2c5282;
}

.badge-cancelled {
  background: #fed7d7;
  color: #742a2a;
}

.booking-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.booking-info .court-name,
.booking-customer .customer-name {
  margin: 0 0 0.25rem 0;
  color: #1a202c;
  font-size: 1rem;
}

.booking-info .individual-court,
.booking-customer .customer-contact,
.booking-customer .customer-phone {
  margin: 0.25rem 0;
  color: #718096;
  font-size: 0.9rem;
}

.booking-meta {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #f7fafc;
  color: #a0aec0;
}

.booking-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.booking-actions button {
  flex: 1;
  padding: 0.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.btn-complete {
  background: #48bb78;
  color: white;
}

.btn-complete:hover {
  background: #38a169;
}

.btn-cancel {
  background: #f56565;
  color: white;
}

.btn-cancel:hover {
  background: #e53e3e;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #718096;
}

/* Responsive */
@media (max-width: 768px) {
  .booking-schedule-container {
    padding: 1rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filter-row {
    flex-direction: column;
  }

  .filter-group {
    width: 100%;
  }

  .bookings-grid {
    grid-template-columns: 1fr;
  }
}
</style>
