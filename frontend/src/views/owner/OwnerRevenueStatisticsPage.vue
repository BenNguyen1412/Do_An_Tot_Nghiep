<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import axios from '@/utils/axios'
import { useToast } from 'vue-toastification'

// Filter states
const timeFilter = ref<'day' | 'month' | 'year'>('month')
const selectedDate = ref(new Date().toISOString().split('T')[0])
const selectedMonth = ref(new Date().toISOString().slice(0, 7))
const selectedYear = ref(new Date().getFullYear().toString())
const isLoading = ref(false)
const loadError = ref('')
const toast = useToast()

interface BookingItem {
  id: number
  booking_date: string
  start_time: string
  end_time: string
  total_price?: number | null
  court_name?: string | null
  status?: string | null
  booking_status?: string | null
  payment_status?: string | null
  payment_method?: string | null
}

interface RevenueStats {
  total: number
  bookings: number
  averagePerBooking: number
  growth: number
  bookingsGrowth: number
  completedBookings: number
  cancelledBookings: number
}

interface ChartPoint {
  label: string
  value: number
}

interface OwnerCourt {
  id: number
  opening_time?: string | null
  closing_time?: string | null
}

interface TimeRange {
  open: number
  close: number
}

interface DateRange {
  startDate: string
  endDate: string
}

const revenueData = ref<RevenueStats>({
  total: 0,
  bookings: 0,
  averagePerBooking: 0,
  growth: 0,
  bookingsGrowth: 0,
  completedBookings: 0,
  cancelledBookings: 0,
})

const chartData = ref<ChartPoint[]>([])
const ownerOpenRanges = ref<TimeRange[]>([])
const hasLoadedOwnerHours = ref(false)

const toLocalDateString = (date: Date): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const getSelectedDateRange = (): DateRange => {
  if (timeFilter.value === 'day') {
    const selected = selectedDate.value || toLocalDateString(new Date())
    return { startDate: selected, endDate: selected }
  }

  if (timeFilter.value === 'month') {
    const [yearStr, monthStr] = (selectedMonth.value || new Date().toISOString().slice(0, 7)).split(
      '-',
    )
    const year = Number(yearStr)
    const month = Number(monthStr)

    if (!Number.isFinite(year) || !Number.isFinite(month)) {
      const now = new Date()
      const start = new Date(now.getFullYear(), now.getMonth(), 1)
      const end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
      return { startDate: toLocalDateString(start), endDate: toLocalDateString(end) }
    }

    const start = new Date(year, month - 1, 1)
    const end = new Date(year, month, 0)
    return { startDate: toLocalDateString(start), endDate: toLocalDateString(end) }
  }

  const year = Number(selectedYear.value) || new Date().getFullYear()
  const start = new Date(year, 0, 1)
  const end = new Date(year, 11, 31)
  return { startDate: toLocalDateString(start), endDate: toLocalDateString(end) }
}

const getPreviousDateRange = ({ startDate, endDate }: DateRange): DateRange => {
  const start = new Date(startDate)
  const end = new Date(endDate)
  const dayCount = Math.max(1, Math.round((end.getTime() - start.getTime()) / 86400000) + 1)

  const prevEnd = new Date(start)
  prevEnd.setDate(prevEnd.getDate() - 1)

  const prevStart = new Date(prevEnd)
  prevStart.setDate(prevStart.getDate() - dayCount + 1)

  return {
    startDate: toLocalDateString(prevStart),
    endDate: toLocalDateString(prevEnd),
  }
}

const normalizeStatus = (value: string | null | undefined): string => {
  if (!value) return ''
  const normalized = value.toLowerCase().trim()
  return normalized.includes('.') ? normalized.split('.').pop() || '' : normalized
}

const toMinutes = (timeText: string): number => {
  const [hours, minutes] = timeText.split(':').map(Number)
  if (!Number.isFinite(hours) || !Number.isFinite(minutes)) return 0
  return hours * 60 + minutes
}

const loadOwnerOpenRanges = async () => {
  if (hasLoadedOwnerHours.value) return

  try {
    const response = await axios.get('/courts/my')
    const courts: OwnerCourt[] = response.data || []

    ownerOpenRanges.value = courts
      .map((court) => {
        const open = toMinutes(court.opening_time || '')
        const close = toMinutes(court.closing_time || '')
        return { open, close }
      })
      .filter((range) => range.close > range.open)
  } catch (error) {
    console.error('Error loading owner courts for opening hours:', error)
    ownerOpenRanges.value = []
  } finally {
    hasLoadedOwnerHours.value = true
  }
}

const isWithinOwnerOpeningHours = (startTime: string, endTime: string): boolean => {
  // Fallback: if opening-hours info cannot be loaded, do not block chart rendering.
  if (!ownerOpenRanges.value.length) return true

  const startMinutes = toMinutes(startTime)
  const endMinutes = toMinutes(endTime)

  return ownerOpenRanges.value.some(
    (range) => startMinutes >= range.open && endMinutes <= range.close,
  )
}

const isRevenueBooking = (booking: BookingItem): boolean => {
  const total = Number(booking.total_price || 0)
  if (total <= 0) return false

  const status = normalizeStatus(booking.booking_status || booking.status)
  const paymentStatus = normalizeStatus(booking.payment_status)
  const paymentMethod = normalizeStatus(booking.payment_method)

  if (status === 'cancelled' || paymentStatus === 'failed' || paymentStatus === 'refunded') {
    return false
  }

  if (paymentStatus === 'paid' || paymentMethod === 'cash') {
    return true
  }

  return ['confirmed', 'active', 'completed'].includes(status)
}

const computeGrowth = (current: number, previous: number): number => {
  if (previous <= 0) return current > 0 ? 100 : 0
  return ((current - previous) / previous) * 100
}

const buildChartData = (bookings: BookingItem[]) => {
  const grouped = new Map<string, number>()

  bookings.forEach((booking) => {
    if (!isRevenueBooking(booking)) return
    if (!isWithinOwnerOpeningHours(booking.start_time, booking.end_time)) return

    const total = Number(booking.total_price || 0)
    const slotLabel = `${booking.start_time}-${booking.end_time}`
    grouped.set(slotLabel, (grouped.get(slotLabel) || 0) + total)
  })

  chartData.value = Array.from(grouped.entries())
    .sort((a, b) => toMinutes(a[0].split('-')[0]) - toMinutes(b[0].split('-')[0]))
    .map(([label, value]) => ({ label, value }))
}

const getBookingsByRange = async ({ startDate, endDate }: DateRange): Promise<BookingItem[]> => {
  const response = await axios.get('/owner/bookings', {
    params: {
      start_date: startDate,
      end_date: endDate,
    },
  })

  return response.data || []
}

const fetchRevenueData = async () => {
  isLoading.value = true
  loadError.value = ''

  try {
    await loadOwnerOpenRanges()

    const currentRange = getSelectedDateRange()
    const previousRange = getPreviousDateRange(currentRange)

    const [currentBookings, previousBookings] = await Promise.all([
      getBookingsByRange(currentRange),
      getBookingsByRange(previousRange),
    ])

    const currentRevenueBookings = currentBookings.filter(isRevenueBooking)
    const previousRevenueBookings = previousBookings.filter(isRevenueBooking)

    const totalRevenue = currentRevenueBookings.reduce(
      (sum, b) => sum + Number(b.total_price || 0),
      0,
    )
    const previousTotalRevenue = previousRevenueBookings.reduce(
      (sum, b) => sum + Number(b.total_price || 0),
      0,
    )

    const completedBookings = currentBookings.filter((b) => {
      const status = normalizeStatus(b.booking_status || b.status)
      return status === 'completed'
    }).length

    const cancelledBookings = currentBookings.filter((b) => {
      const status = normalizeStatus(b.booking_status || b.status)
      return status === 'cancelled'
    }).length

    revenueData.value = {
      total: totalRevenue,
      bookings: currentRevenueBookings.length,
      averagePerBooking: currentRevenueBookings.length
        ? totalRevenue / currentRevenueBookings.length
        : 0,
      growth: computeGrowth(totalRevenue, previousTotalRevenue),
      bookingsGrowth: computeGrowth(currentRevenueBookings.length, previousRevenueBookings.length),
      completedBookings,
      cancelledBookings,
    }

    buildChartData(currentBookings)
  } catch (error) {
    console.error('Error loading owner revenue data:', error)
    loadError.value = 'Unable to load revenue statistics. Please try again.'
    toast.error(loadError.value)
    revenueData.value = {
      total: 0,
      bookings: 0,
      averagePerBooking: 0,
      growth: 0,
      bookingsGrowth: 0,
      completedBookings: 0,
      cancelledBookings: 0,
    }
    chartData.value = []
  } finally {
    isLoading.value = false
  }
}

const exportReport = () => {
  const currentRange = getSelectedDateRange()
  const lines = [
    `Period,${currentRange.startDate} to ${currentRange.endDate}`,
    `Total Revenue,${revenueData.value.total}`,
    `Revenue Bookings,${revenueData.value.bookings}`,
    `Average Per Booking,${revenueData.value.averagePerBooking}`,
    `Completed Bookings,${revenueData.value.completedBookings}`,
    `Cancelled Bookings,${revenueData.value.cancelledBookings}`,
  ]

  const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `owner-revenue-${timeFilter.value}-${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
  }).format(value)
}

const maxChartValue = computed(() => {
  const max = Math.max(...chartData.value.map((d) => d.value))
  return max > 0 ? max : 1
})

watch([timeFilter, selectedDate, selectedMonth, selectedYear], fetchRevenueData)
onMounted(fetchRevenueData)
</script>

<template>
  <div class="revenue-statistics-page">
    <!-- Filters -->
    <div class="filters-section">
      <div class="filter-group">
        <label class="filter-label">View by:</label>
        <div class="filter-buttons">
          <button
            class="filter-btn"
            :class="{ active: timeFilter === 'day' }"
            @click="timeFilter = 'day'"
          >
            <img
              src="/alarm-clock-icon-illustration-design-free-vector.jpg"
              alt="Day"
              class="btn-icon"
            />
            Day
          </button>
          <button
            class="filter-btn"
            :class="{ active: timeFilter === 'month' }"
            @click="timeFilter = 'month'"
          >
            <img src="/month.png" alt="Month" class="btn-icon" />
            Month
          </button>
          <button
            class="filter-btn"
            :class="{ active: timeFilter === 'year' }"
            @click="timeFilter = 'year'"
          >
            <img src="/year.png" alt="Year" class="btn-icon" />
            Year
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

    <div class="data-state" v-if="isLoading">Loading revenue data...</div>
    <div class="data-state error" v-else-if="loadError">{{ loadError }}</div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card primary">
        <div class="stat-icon">
          <img src="/total%20revenue.png" alt="Total Revenue" class="stat-icon-img" />
        </div>
        <div class="stat-content">
          <span class="stat-label">Total Revenue</span>
          <span class="stat-value">{{ formatCurrency(revenueData.total) }}</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <img src="/booking.png" alt="Bookings" class="stat-icon-img" />
        </div>
        <div class="stat-content">
          <span class="stat-label">Revenue Bookings</span>
          <span class="stat-value">{{ revenueData.bookings }}</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <img src="/revenue.png" alt="Average revenue" class="stat-icon-img" />
        </div>
        <div class="stat-content">
          <span class="stat-label">Average/Booking</span>
          <span class="stat-value">{{ formatCurrency(revenueData.averagePerBooking) }}</span>
          <span class="stat-change">~</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <img src="/logo-pickball.webp" alt="Completed" class="stat-icon-img" />
        </div>
        <div class="stat-content">
          <span class="stat-label">Completed Bookings</span>
          <span class="stat-value">{{ revenueData.completedBookings }}</span>
          <span class="stat-change">Cancelled: {{ revenueData.cancelledBookings }}</span>
        </div>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="chart-section">
      <div class="section-header">
        <h2 class="section-title">
          <img
            src="/revenue%20by%20time%20slot.png"
            alt="Revenue by Time Slot"
            class="section-title-icon"
          />
          Revenue by Time Slot
        </h2>
        <button class="export-btn" @click="exportReport">
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
          Export Report
        </button>
      </div>

      <div class="chart-container" v-if="chartData.length">
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
      <div v-else class="chart-empty">
        No bookings found in the selected period within court opening hours.
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

.data-state {
  padding: 12px 16px;
  border-radius: 12px;
  background: #f0f9ff;
  color: #1d4ed8;
  font-weight: 600;
  border: 1px solid #bfdbfe;
}

.data-state.error {
  background: #fef2f2;
  border-color: #fecaca;
  color: #b91c1c;
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
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
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
  flex-shrink: 0;
}

.stat-icon-img {
  width: 44px;
  height: 44px;
  object-fit: contain;
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
.chart-section {
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
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.section-title-icon {
  width: 22px;
  height: 22px;
  object-fit: contain;
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

.chart-empty {
  padding: 24px;
  border: 1px dashed #d1d5db;
  border-radius: 12px;
  text-align: center;
  color: #6b7280;
  font-weight: 600;
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
