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
          <span class="stat-period">{{ currentMonthYear }}</span>
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

    <!-- Calendar Navigation -->
    <div class="calendar-navigation">
      <button @click="previousMonth" class="nav-btn">← Tháng trước</button>
      <h2 class="current-month">{{ currentMonthYear }}</h2>
      <button @click="nextMonth" class="nav-btn">Tháng sau →</button>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filter-row">
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

    <!-- Calendar View -->
    <div v-else class="calendar-section">
      <!-- Calendar Grid -->
      <div class="calendar-container">
        <div class="calendar-header">
          <div v-for="day in weekDays" :key="day" class="calendar-weekday">
            {{ day }}
          </div>
        </div>
        <div class="calendar-grid">
          <div
            v-for="day in calendarDays"
            :key="day.date"
            class="calendar-day"
            :class="{
              'other-month': !day.isCurrentMonth,
              today: day.isToday,
              'has-bookings': day.bookingCount > 0,
            }"
            @click="selectDate(day.date)"
          >
            <div class="day-number">{{ day.dayNumber }}</div>
            <div v-if="day.bookingCount > 0" class="booking-indicator">
              <span class="booking-dot">●</span>
              {{ day.bookingCount }}
            </div>
          </div>
        </div>
      </div>

      <div class="select-date-prompt">
        <div class="prompt-icon">📅</div>
        <p>Nhấn vào một ngày trên lịch để xem chi tiết lịch đặt sân</p>
      </div>
    </div>

    <!-- Booking Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">📅 Lịch đặt sân - {{ formatDateHeader(selectedDate!) }}</h3>
          <button class="modal-close" @click="closeModal">✕</button>
        </div>

        <div class="modal-body">
          <div v-if="selectedDateBookings.length > 0" class="modal-bookings-grid">
            <div
              v-for="booking in selectedDateBookings"
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
                <button
                  v-if="booking.status === 'cancelled'"
                  @click="deleteBooking(booking.id)"
                  class="btn-delete"
                  title="Xóa lịch đặt"
                >
                  🗑️ Xóa
                </button>
              </div>
            </div>
          </div>

          <div v-else class="no-bookings-modal">
            <div class="empty-icon">📭</div>
            <p>Không có lịch đặt sân nào trong ngày này</p>
          </div>
        </div>
      </div>
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

// Calendar state
const currentMonth = ref(new Date().getMonth())
const currentYear = ref(new Date().getFullYear())
const selectedDate = ref<string | null>(null)
const showModal = ref(false)

const weekDays = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']

// Helper function to format date string without timezone issues
const formatDateString = (year: number, month: number, day: number): string => {
  const yyyy = year
  const mm = String(month + 1).padStart(2, '0')
  const dd = String(day).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

// Get today's date without timezone issues
const getTodayString = (): string => {
  const now = new Date()
  return formatDateString(now.getFullYear(), now.getMonth(), now.getDate())
}

// Calculate summary from actual bookings data for selected calendar month
const bookingSummary = computed(() => {
  // Filter bookings for the currently viewed month on calendar
  const viewedMonthBookings = bookings.value.filter((b) => {
    // Parse booking date string to avoid timezone issues
    const bookingDateStr = b.booking_date.split('T')[0]
    const [year, month] = bookingDateStr.split('-').map(Number)

    return month - 1 === currentMonth.value && year === currentYear.value
  })

  const total = viewedMonthBookings.length
  const completed = viewedMonthBookings.filter((b) => b.status === 'completed').length
  const cancelled = viewedMonthBookings.filter((b) => b.status === 'cancelled').length

  return {
    total_bookings: total,
    completed_bookings: completed,
    cancelled_bookings: cancelled,
  }
})

// Initialize default date range (first to last day of current month)
const initializeDateRange = () => {
  const today = new Date()
  const year = today.getFullYear()
  const month = today.getMonth()

  // Last day of current month
  const lastDayOfMonth = new Date(year, month + 1, 0).getDate()

  filters.value.startDate = formatDateString(year, month, 1)
  filters.value.endDate = formatDateString(year, month, lastDayOfMonth)
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

// Current month year display
const currentMonthYear = computed(() => {
  const date = new Date(currentYear.value, currentMonth.value)
  return date.toLocaleDateString('vi-VN', { month: 'long', year: 'numeric' })
})

// Generate calendar days
const calendarDays = computed(() => {
  const firstDay = new Date(currentYear.value, currentMonth.value, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0)
  const prevMonthLastDay = new Date(currentYear.value, currentMonth.value, 0)

  const days: Array<{
    date: string
    dayNumber: number
    isCurrentMonth: boolean
    isToday: boolean
    bookingCount: number
  }> = []

  // Get first day of week (0 = Sunday, 1 = Monday, etc.)
  const firstDayOfWeek = firstDay.getDay()

  // Add previous month days to fill the week
  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    const dayNum = prevMonthLastDay.getDate() - i
    const year = currentYear.value
    const month = currentMonth.value === 0 ? 11 : currentMonth.value - 1
    const dateStr = formatDateString(year, month, dayNum)
    days.push({
      date: dateStr,
      dayNumber: dayNum,
      isCurrentMonth: false,
      isToday: false,
      bookingCount: getBookingCountForDate(dateStr),
    })
  }

  // Add current month days
  const today = getTodayString()
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const dateStr = formatDateString(currentYear.value, currentMonth.value, i)
    days.push({
      date: dateStr,
      dayNumber: i,
      isCurrentMonth: true,
      isToday: dateStr === today,
      bookingCount: getBookingCountForDate(dateStr),
    })
  }

  // Add next month days to complete the grid
  const remainingDays = 42 - days.length // 6 weeks * 7 days
  for (let i = 1; i <= remainingDays; i++) {
    const year = currentMonth.value === 11 ? currentYear.value + 1 : currentYear.value
    const month = currentMonth.value === 11 ? 0 : currentMonth.value + 1
    const dateStr = formatDateString(year, month, i)
    days.push({
      date: dateStr,
      dayNumber: i,
      isCurrentMonth: false,
      isToday: false,
      bookingCount: getBookingCountForDate(dateStr),
    })
  }

  return days
})

// Get bookings for selected date
const selectedDateBookings = computed(() => {
  if (!selectedDate.value) return []

  const now = new Date()
  const today = getTodayString()
  const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`

  return bookings.value
    .filter((booking) => {
      const date = booking.booking_date.split('T')[0]

      if (date !== selectedDate.value) return false

      // Skip currently active bookings on today
      if (booking.status === 'active' && date === today) {
        const isCurrentlyActive =
          booking.start_time <= currentTime && currentTime < booking.end_time
        if (isCurrentlyActive) return false
      }

      return true
    })
    .sort((a, b) => a.start_time.localeCompare(b.start_time))
})

// Helper function to count bookings for a date
const getBookingCountForDate = (dateStr: string): number => {
  const now = new Date()
  const today = getTodayString()
  const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`

  return bookings.value.filter((booking) => {
    const bookingDate = booking.booking_date.split('T')[0]

    if (bookingDate !== dateStr) return false

    // Exclude currently active bookings
    if (booking.status === 'active' && bookingDate === today) {
      const isCurrentlyActive = booking.start_time <= currentTime && currentTime < booking.end_time
      if (isCurrentlyActive) return false
    }

    return true
  }).length
}

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

const deleteBooking = async (bookingId: number) => {
  if (!confirm('Bạn có chắc chắn muốn xóa lịch đặt này vĩnh viễn?')) return

  try {
    await axios.delete(`/bookings/${bookingId}`)
    alert('Đã xóa lịch đặt thành công!')
    loadBookings() // Reload to update list and summary
  } catch (error) {
    console.error('Error deleting booking:', error)
    alert('Không thể xóa lịch đặt')
  }
}

// Calendar navigation functions
const previousMonth = async () => {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
  await updateDateRangeForCalendar()
  selectedDate.value = null
}

const nextMonth = async () => {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
  await updateDateRangeForCalendar()
  selectedDate.value = null
}

const selectDate = async (date: string) => {
  // Parse date string manually to avoid timezone issues
  const [year, month] = date.split('-').map(Number)
  const clickedMonth = month - 1 // JavaScript months are 0-indexed
  const clickedYear = year

  // If clicked date is from different month, switch to that month first
  if (clickedMonth !== currentMonth.value || clickedYear !== currentYear.value) {
    currentMonth.value = clickedMonth
    currentYear.value = clickedYear
    await updateDateRangeForCalendar()
  }

  // Set selected date and show modal
  selectedDate.value = date
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedDate.value = null
}

const updateDateRangeForCalendar = async () => {
  const lastDayOfMonth = new Date(currentYear.value, currentMonth.value + 1, 0).getDate()

  filters.value.startDate = formatDateString(currentYear.value, currentMonth.value, 1)
  filters.value.endDate = formatDateString(currentYear.value, currentMonth.value, lastDayOfMonth)

  await loadBookings()
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
  const [year, month, day] = dateStr.split('-').map(Number)
  const date = new Date(year, month - 1, day)

  const now = new Date()
  const today = getTodayString()

  // Calculate yesterday properly
  const yesterdayDate = new Date(now)
  yesterdayDate.setDate(yesterdayDate.getDate() - 1)
  const yesterday = formatDateString(
    yesterdayDate.getFullYear(),
    yesterdayDate.getMonth(),
    yesterdayDate.getDate(),
  )

  if (dateStr === today) {
    return (
      'Hôm nay - ' +
      date.toLocaleDateString('vi-VN', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    )
  } else if (dateStr === yesterday) {
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

/* Calendar Navigation */
.calendar-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
  margin-bottom: 2rem;
}

.current-month {
  font-size: 1.75rem;
  font-weight: 800;
  color: white;
  margin: 0;
  text-transform: capitalize;
  letter-spacing: 0.5px;
}

.nav-btn {
  padding: 0.875rem 2rem;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

/* Calendar Section */
.calendar-section {
  background: white;
  border-radius: 16px;
  padding: 2.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.calendar-container {
  margin-bottom: 2rem;
}

.calendar-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.calendar-weekday {
  text-align: center;
  font-weight: 800;
  color: #667eea;
  padding: 1rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px;
  font-size: 0.95rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.75rem;
}

.calendar-day {
  aspect-ratio: 1;
  padding: 1rem;
  border: 2px solid #e9ecef;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: white;
  position: relative;
  min-height: 80px;
}

.calendar-day:hover {
  border-color: #667eea;
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.25);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.calendar-day:hover .day-number {
  color: white;
}

.calendar-day:hover .booking-indicator {
  background: white;
  color: #667eea;
}

.calendar-day.other-month {
  opacity: 0.25;
  background: #f8f9fa;
  cursor: default;
}

.calendar-day.other-month:hover {
  transform: none;
  border-color: #e9ecef;
  box-shadow: none;
  background: #f8f9fa;
}

.calendar-day.today {
  background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
  border-color: #fdcb6e;
  font-weight: 700;
  box-shadow: 0 4px 15px rgba(253, 203, 110, 0.4);
}

.calendar-day.today .day-number {
  color: #2d3436;
}

.calendar-day.has-bookings {
  border-color: #00b894;
  background: linear-gradient(135deg, #d1f2eb 0%, #a8e6cf 100%);
}

.calendar-day.has-bookings .day-number {
  color: #00684a;
  font-weight: 700;
}

.day-number {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.booking-indicator {
  font-size: 0.7rem;
  background: #00b894;
  color: white;
  padding: 0.25rem 0.6rem;
  border-radius: 20px;
  font-weight: 700;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.booking-dot {
  font-size: 0.5rem;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-container {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 1200px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.4s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px 20px 0 0;
  border-bottom: 3px solid rgba(255, 255, 255, 0.2);
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin: 0;
}

.modal-close {
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-size: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.modal-body {
  padding: 2rem;
  overflow-y: auto;
  max-height: calc(85vh - 100px);
}

.modal-bookings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.no-bookings-modal {
  text-align: center;
  padding: 4rem 2rem;
}

.no-bookings-modal .empty-icon {
  font-size: 5rem;
  margin-bottom: 1rem;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.no-bookings-modal p {
  font-size: 1.2rem;
  color: #718096;
  margin: 0;
}

.select-date-prompt {
  text-align: center;
  padding: 3rem;
  color: #718096;
}

.prompt-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.select-date-prompt p {
  font-size: 1.1rem;
  color: #a0aec0;
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
  grid-template-columns: repeat(3, 1fr);
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

.btn-delete {
  background: #ef4444;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}

.btn-delete:hover {
  background: #dc2626;
  transform: scale(1.02);
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
@media (max-width: 1200px) {
  .bookings-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

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

  .calendar-navigation {
    padding: 1.5rem 1rem;
  }

  .current-month {
    font-size: 1.2rem;
  }

  .nav-btn {
    padding: 0.65rem 1.25rem;
    font-size: 0.85rem;
  }

  .calendar-section {
    padding: 1.5rem 1rem;
  }

  .calendar-header {
    gap: 0.5rem;
  }

  .calendar-weekday {
    font-size: 0.7rem;
    padding: 0.6rem 0.3rem;
  }

  .calendar-grid {
    gap: 0.5rem;
  }

  .calendar-day {
    padding: 0.5rem;
    min-height: 60px;
  }

  .day-number {
    font-size: 1rem;
  }

  .booking-indicator {
    font-size: 0.6rem;
    padding: 0.15rem 0.4rem;
  }

  .modal-container {
    width: 95%;
    max-height: 90vh;
  }

  .modal-header {
    padding: 1.5rem;
  }

  .modal-title {
    font-size: 1.2rem;
  }

  .modal-body {
    padding: 1.5rem;
  }

  .modal-bookings-grid {
    grid-template-columns: 1fr;
  }
}
</style>
