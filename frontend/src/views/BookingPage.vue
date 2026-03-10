<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import axiosInstance from '@/utils/axios'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const toast = useToast()

interface TimeSlot {
  start_time: string
  end_time: string
  price: number
}

interface IndividualCourt {
  id: number
  name: string
  is_available: boolean
}

interface CourtOwner {
  id: number
  full_name: string
  email: string
  phone_number?: string | null
}

interface Court {
  id: number
  name: string
  address: string
  district: string
  city: string
  opening_time: string
  closing_time: string
  images: string[]
  time_slots?: TimeSlot[]
  individual_courts?: IndividualCourt[]
  contact_phone: string
  contact_email?: string
  owner_id: number
  owner?: CourtOwner
}

const court = ref<Court | null>(null)
const isLoading = ref(false)
const currentStep = ref(1)

// Date selection
const selectedDate = ref<Date>(new Date())
const availableDates = ref<Date[]>([])

// Time selection
const selectedTimeSlots = ref<string[]>([])

// Step 2: User Information
const userInfo = ref({
  name: '',
  email: '',
  phone: '',
})

// Generate available dates (next 7 days)
const generateAvailableDates = () => {
  const dates: Date[] = []
  const today = new Date()
  for (let i = 0; i < 7; i++) {
    const date = new Date(today)
    date.setDate(today.getDate() + i)
    dates.push(date)
  }
  availableDates.value = dates
}

// Date navigation
const currentDateIndex = computed(() => {
  return availableDates.value.findIndex(
    (date) => date.toDateString() === selectedDate.value.toDateString(),
  )
})

const visibleDates = computed(() => {
  const index = currentDateIndex.value
  // Show 6 dates at a time
  const startIndex = Math.max(0, Math.min(index, availableDates.value.length - 6))
  return availableDates.value.slice(startIndex, startIndex + 6)
})

const canGoPrev = computed(() => currentDateIndex.value > 0)
const canGoNext = computed(() => currentDateIndex.value < availableDates.value.length - 1)

const previousDate = () => {
  if (canGoPrev.value) {
    selectedDate.value = availableDates.value[currentDateIndex.value - 1]
  }
}

const nextDate = () => {
  if (canGoNext.value) {
    selectedDate.value = availableDates.value[currentDateIndex.value + 1]
  }
}

const selectDate = (date: Date) => {
  selectedDate.value = date
  selectedTimeSlots.value = []
}

// Format date
const formatDateShort = (date: Date) => {
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const months = [
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec',
  ]
  return {
    day: days[date.getDay()],
    date: date.getDate(),
    month: months[date.getMonth()],
  }
}

const formatDateFull = (date: Date) => {
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const months = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
  ]
  return `${days[date.getDay()]}, ${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`
}

const formatDateForBooking = (date: Date) => {
  const months = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
  ]
  return `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`
}

// Generate time slots (30-minute intervals)
const generateTimeSlots = () => {
  if (!court.value) return []

  const slots: string[] = []
  const [startHour] = court.value.opening_time.split(':').map(Number)
  const [endHour] = court.value.closing_time.split(':').map(Number)

  // Generate 30-minute intervals
  for (let hour = startHour; hour < endHour; hour++) {
    slots.push(`${String(hour).padStart(2, '0')}:00`)
    slots.push(`${String(hour).padStart(2, '0')}:30`)
  }
  // Add final hour slot
  slots.push(`${String(endHour).padStart(2, '0')}:00`)

  return slots
}

const timeSlots = computed(() => generateTimeSlots())

// Check if a time slot is in the past
const isSlotInPast = (slot: string): boolean => {
  const today = new Date()
  const isToday = selectedDate.value.toDateString() === today.toDateString()

  if (!isToday) {
    // If selected date is in the future, no slots are in the past
    return selectedDate.value < today
  }

  // For today, check if the slot time has passed
  const [slotHour, slotMinute] = slot.split(':').map(Number)
  const currentHour = today.getHours()
  const currentMinute = today.getMinutes()

  // Compare slot time with current time
  if (slotHour < currentHour) {
    return true
  } else if (slotHour === currentHour && slotMinute <= currentMinute) {
    return true
  }

  return false
}

// Toggle time slot selection (range selection with start and end)
const toggleTimeSlot = (slot: string) => {
  // Check if slot is in the past
  if (isSlotInPast(slot)) {
    toast.error('Không thể đặt sân cho khung giờ đã qua')
    return
  }

  const index = selectedTimeSlots.value.indexOf(slot)

  if (index > -1) {
    // If clicking on an already selected slot, clear selection
    selectedTimeSlots.value = []
    return
  }

  if (selectedTimeSlots.value.length === 0) {
    // First selection: set as start time
    selectedTimeSlots.value = [slot]
  } else if (selectedTimeSlots.value.length === 1) {
    // Second selection: set as end time and fill range
    const startSlot = selectedTimeSlots.value[0]
    const allSlots = timeSlots.value
    const startIndex = allSlots.indexOf(startSlot)
    const endIndex = allSlots.indexOf(slot)

    if (endIndex <= startIndex) {
      // If end is before or same as start, set new start
      selectedTimeSlots.value = [slot]
    } else {
      // Check if any slot in the range is in the past
      const rangeSlots = allSlots.slice(startIndex, endIndex + 1)
      const hasPastSlot = rangeSlots.some((s) => isSlotInPast(s))

      if (hasPastSlot) {
        toast.error('Không thể đặt sân cho khung giờ bao gồm thời gian đã qua')
        selectedTimeSlots.value = []
        return
      }

      // Fill all slots between start and end (inclusive)
      selectedTimeSlots.value = rangeSlots
    }
  } else {
    // Reset and start new selection
    selectedTimeSlots.value = [slot]
  }
}

const isSlotSelected = (slot: string) => {
  return selectedTimeSlots.value.includes(slot)
}

// Get price for a specific time slot
const getPriceForSlot = (slot: string): number => {
  if (!court.value?.time_slots || court.value.time_slots.length === 0) {
    return 100000 // Default price
  }

  // Find the price tier that this slot falls into
  const timeSlot = court.value.time_slots.find((ts) => {
    return slot >= ts.start_time && slot < ts.end_time
  })

  return timeSlot?.price || court.value.time_slots[0].price
}

// Calculate booking details with multi-tier pricing
const bookingDetails = computed(() => {
  if (selectedTimeSlots.value.length === 0) {
    return {
      startTime: '',
      endTime: '',
      totalHours: 0,
      totalPrice: 0,
      priceBreakdown: [],
    }
  }

  const sortedSlots = [...selectedTimeSlots.value].sort()
  const startTime = sortedSlots[0]
  const endTime = sortedSlots[sortedSlots.length - 1]

  // Calculate total hours (each slot is 30 minutes, end is inclusive)
  // Total hours = (number of slots - 1) * 0.5
  const totalHours = (sortedSlots.length - 1) * 0.5

  // Calculate price with multi-tier support and track breakdown
  const priceMap = new Map<number, number>() // price -> hours
  let totalPrice = 0

  for (let i = 0; i < sortedSlots.length - 1; i++) {
    const slotPrice = getPriceForSlot(sortedSlots[i])
    totalPrice += slotPrice * 0.5 // 30 minutes = 0.5 hour

    // Track hours per price tier
    const currentHours = priceMap.get(slotPrice) || 0
    priceMap.set(slotPrice, currentHours + 0.5)
  }

  // Convert to array for display
  const priceBreakdown = Array.from(priceMap.entries()).map(([price, hours]) => ({
    price,
    hours,
    subtotal: price * hours,
  }))

  return {
    startTime,
    endTime,
    totalHours,
    totalPrice,
    priceBreakdown,
  }
})

// Format price
const formatPrice = (price: number) => {
  const formatted = new Intl.NumberFormat('vi-VN').format(price / 1000)
  return `${formatted}k`
}

// Fetch court details
const fetchCourtDetails = async () => {
  isLoading.value = true
  try {
    const courtId = route.params.id
    const response = await axiosInstance.get(`/courts/${courtId}`)
    court.value = response.data
  } catch (error) {
    console.error('Error fetching court details:', error)
  } finally {
    isLoading.value = false
  }
}

// Get court banner image
const courtBanner = computed(() => {
  if (!court.value || !court.value.images || court.value.images.length === 0) {
    return 'https://i.pinimg.com/1200x/0e/c0/4d/0ec04dde4f138cac5ec5e928edef20e9.jpg'
  }
  const img = court.value.images[0]
  if (img.startsWith('/')) {
    return `http://localhost:8000${img}`
  }
  return img
})

// Navigation
const goBack = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  } else {
    router.back()
  }
}

const goNext = () => {
  if (currentStep.value === 1) {
    if (selectedTimeSlots.value.length === 0) {
      toast.error('Vui lòng chọn khung giờ bắt đầu và kết thúc')
      return
    }
    // Check minimum 1 hour (2 slots of 30 minutes: start and end)
    if (selectedTimeSlots.value.length < 3) {
      toast.error('Thời gian đặt sân tối thiểu là 1 giờ')
      return
    }
    // Pre-fill user info from auth store if available
    if (authStore.user) {
      userInfo.value.name = authStore.user.full_name || ''
      userInfo.value.email = authStore.user.email || ''
      userInfo.value.phone = authStore.user.phone_number || ''
    }
    currentStep.value = 2
  } else if (currentStep.value === 2) {
    // Validate user information
    if (!userInfo.value.name.trim()) {
      toast.error('Vui lòng nhập họ tên')
      return
    }
    if (!userInfo.value.email.trim()) {
      toast.error('Vui lòng nhập email')
      return
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(userInfo.value.email)) {
      toast.error('Email không hợp lệ')
      return
    }
    if (!userInfo.value.phone.trim()) {
      toast.error('Vui lòng nhập số điện thoại')
      return
    }
    if (!/^[0-9]{10,11}$/.test(userInfo.value.phone.replace(/\s/g, ''))) {
      toast.error('Số điện thoại không hợp lệ (10-11 chữ số)')
      return
    }
    currentStep.value = 3
  } else if (currentStep.value === 3) {
    // TODO: Implement payment step
  }
}

const showManagement = computed(() => authStore.user?.role === 'owner')
const showAdvertisement = computed(() => authStore.user?.role === 'enterprise')

onMounted(() => {
  if (!authStore.user || !authStore.token) {
    router.push('/login')
    return
  }
  fetchCourtDetails()
  generateAvailableDates()
})
</script>

<template>
  <div class="booking-page">
    <AppHeader :showManagement="showManagement" :showAdvertisement="showAdvertisement" />

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading...</p>
    </div>

    <!-- Booking Content -->
    <div v-else-if="court" class="booking-content">
      <!-- Banner -->
      <div class="banner-section">
        <img :src="courtBanner" :alt="court.name" class="banner-image" />
      </div>

      <!-- Progress Indicator -->
      <div class="progress-section">
        <div class="progress-container">
          <div
            class="progress-step"
            :class="{ active: currentStep >= 1, completed: currentStep > 1 }"
          >
            <div class="step-number">1</div>
            <span class="step-label">Time & Date</span>
          </div>
          <div class="progress-line" :class="{ active: currentStep >= 2 }"></div>
          <div
            class="progress-step"
            :class="{ active: currentStep >= 2, completed: currentStep > 2 }"
          >
            <div class="step-number">2</div>
            <span class="step-label">Order confirmation</span>
          </div>
          <div class="progress-line" :class="{ active: currentStep >= 3 }"></div>
          <div class="progress-step" :class="{ active: currentStep >= 3 }">
            <div class="step-number">3</div>
            <span class="step-label">Payment</span>
          </div>
        </div>
      </div>

      <!-- Main Booking Section -->
      <div class="main-section" v-if="currentStep === 1">
        <div class="booking-container">
          <!-- Left: Date & Time Selection -->
          <div class="selection-panel">
            <!-- Instructions -->
            <div class="instructions-box">
              <h2 class="section-title">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                >
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke-width="2" />
                  <line x1="16" y1="2" x2="16" y2="6" stroke-width="2" />
                  <line x1="8" y1="2" x2="8" y2="6" stroke-width="2" />
                  <line x1="3" y1="10" x2="21" y2="10" stroke-width="2" />
                </svg>
                Select Date & Time
              </h2>
            </div>

            <!-- Date Picker -->
            <div class="picker-section">
              <h3 class="picker-label">
                <span class="label-icon">📅</span>
                Choose Date
              </h3>
              <div class="date-picker">
                <button class="date-nav-btn" @click="previousDate" :disabled="!canGoPrev">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M15 19l-7-7 7-7"
                    />
                  </svg>
                </button>

                <div class="dates-container">
                  <div
                    v-for="date in visibleDates"
                    :key="date.toISOString()"
                    class="date-card"
                    :class="{ selected: date.toDateString() === selectedDate.toDateString() }"
                    @click="selectDate(date)"
                  >
                    <div class="date-day">{{ formatDateShort(date).day }}</div>
                    <div class="date-number">
                      {{ formatDateShort(date).date }}
                    </div>
                    <div class="date-month">{{ formatDateShort(date).month }}</div>
                  </div>
                </div>

                <button class="date-nav-btn" @click="nextDate" :disabled="!canGoNext">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Time Slots -->
            <div class="picker-section">
              <div class="picker-header">
                <h3 class="picker-label">
                  <span class="label-icon">⏰</span>
                  Choose Time Slots
                </h3>
                <button
                  v-if="selectedTimeSlots.length > 0"
                  class="clear-btn"
                  @click="selectedTimeSlots = []"
                >
                  Clear All
                </button>
              </div>

              <div class="time-slots-grid">
                <button
                  v-for="slot in timeSlots"
                  :key="slot"
                  class="time-slot-btn"
                  :class="{
                    selected: isSlotSelected(slot),
                    disabled: isSlotInPast(slot),
                  }"
                  :disabled="isSlotInPast(slot)"
                  @click="toggleTimeSlot(slot)"
                >
                  <span class="slot-time">{{ slot }}</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Right: Booking Details -->
          <div class="details-panel">
            <div class="details-card">
              <h3 class="details-title">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
                BOOKING SUMMARY
              </h3>

              <div class="details-content">
                <!-- Date -->
                <div class="detail-group">
                  <div class="detail-label">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                    >
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke-width="2" />
                      <line x1="16" y1="2" x2="16" y2="6" stroke-width="2" />
                      <line x1="8" y1="2" x2="8" y2="6" stroke-width="2" />
                      <line x1="3" y1="10" x2="21" y2="10" stroke-width="2" />
                    </svg>
                    <span>Date</span>
                  </div>
                  <div class="detail-value">{{ formatDateFull(selectedDate) }}</div>
                </div>

                <!-- Time Range -->
                <div class="detail-group" v-if="bookingDetails.startTime">
                  <div class="detail-label">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                    >
                      <circle cx="12" cy="12" r="10" stroke-width="2" />
                      <polyline points="12 6 12 12 16 14" stroke-width="2" />
                    </svg>
                    <span>Time</span>
                  </div>
                  <div class="detail-value time-range">
                    <span class="time-start">{{ bookingDetails.startTime }}</span>
                    <span class="time-separator">→</span>
                    <span class="time-end">{{ bookingDetails.endTime }}</span>
                  </div>
                </div>

                <!-- Duration -->
                <div class="detail-group" v-if="bookingDetails.totalHours > 0">
                  <div class="detail-label">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                    >
                      <circle cx="12" cy="12" r="10" stroke-width="2" />
                      <polyline points="12 6 12 12 16 14" stroke-width="2" />
                    </svg>
                    <span>Duration</span>
                  </div>
                  <div class="detail-value">{{ bookingDetails.totalHours }} hour(s)</div>
                </div>

                <!-- Price Breakdown -->
                <div v-if="bookingDetails.totalPrice > 0" class="price-breakdown">
                  <!-- Show detailed breakdown if multiple price tiers -->
                  <template
                    v-if="bookingDetails.priceBreakdown && bookingDetails.priceBreakdown.length > 1"
                  >
                    <div class="breakdown-header">Price per hour (detailed)</div>
                    <div
                      v-for="(tier, index) in bookingDetails.priceBreakdown"
                      :key="index"
                      class="breakdown-item tier-item"
                    >
                      <span>{{ formatPrice(tier.price) }}/h × {{ tier.hours }}h</span>
                      <span>{{ formatPrice(tier.subtotal) }}</span>
                    </div>
                  </template>

                  <!-- Show simple breakdown if single price tier -->
                  <template v-else>
                    <div class="breakdown-item">
                      <span>Price per hour</span>
                      <span>{{
                        formatPrice(bookingDetails.priceBreakdown?.[0]?.price || 100000)
                      }}</span>
                    </div>
                    <div class="breakdown-item">
                      <span>Duration</span>
                      <span>{{ bookingDetails.totalHours }}h</span>
                    </div>
                  </template>

                  <div class="breakdown-divider"></div>
                  <div class="breakdown-total">
                    <span>Total Amount</span>
                    <span class="total-amount">{{ formatPrice(bookingDetails.totalPrice) }}</span>
                  </div>
                </div>

                <!-- Empty State -->
                <div v-else class="empty-state">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <p>Select time slots to see booking details</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 2: Order Confirmation -->
      <div class="main-section" v-if="currentStep === 2">
        <div class="confirmation-container">
          <div class="confirmation-card">
            <!-- Booking Details -->
            <div class="info-section">
              <h3 class="section-heading">BOOKING DETAILS</h3>
              <div class="info-grid">
                <div class="info-item">
                  <label>Date</label>
                  <div class="info-value">{{ formatDateForBooking(selectedDate) }}</div>
                </div>
                <div class="info-item">
                  <label>Start time</label>
                  <div class="info-value">{{ bookingDetails.startTime }}</div>
                </div>
                <div class="info-item">
                  <label>End time</label>
                  <div class="info-value">{{ bookingDetails.endTime }}</div>
                </div>
              </div>
            </div>

            <!-- Your Information -->
            <div class="info-section">
              <h3 class="section-heading">YOUR INFORMATION</h3>
              <div class="info-grid">
                <div class="info-item">
                  <label>Name</label>
                  <input
                    v-model="userInfo.name"
                    type="text"
                    class="info-input"
                    placeholder="Enter your name"
                  />
                </div>
                <div class="info-item">
                  <label>Email</label>
                  <input
                    v-model="userInfo.email"
                    type="email"
                    class="info-input"
                    placeholder="Enter your email"
                  />
                </div>
                <div class="info-item">
                  <label>Phone</label>
                  <input
                    v-model="userInfo.phone"
                    type="tel"
                    class="info-input"
                    placeholder="Enter your phone number"
                  />
                </div>
              </div>
            </div>

            <!-- Contact Information -->
            <div class="info-section">
              <h3 class="section-heading">CONTACT INFORMATION</h3>
              <div class="info-grid">
                <div class="info-item">
                  <label>Name</label>
                  <div class="info-value">{{ court?.owner?.full_name || 'N/A' }}</div>
                </div>
                <div class="info-item">
                  <label>Email</label>
                  <div class="info-value">{{ court?.contact_email || 'N/A' }}</div>
                </div>
                <div class="info-item">
                  <label>Phone</label>
                  <div class="info-value">{{ court?.contact_phone || 'N/A' }}</div>
                </div>
              </div>
            </div>

            <!-- Payment Information -->
            <div class="info-section payment-section">
              <h3 class="section-heading">PAYMENT INFORMATION</h3>
              <div class="payment-summary">
                <div class="payment-row">
                  <span class="payment-label">Subtotal</span>
                  <span class="payment-value"
                    >{{
                      new Intl.NumberFormat('vi-VN').format(bookingDetails.totalPrice)
                    }}
                    VNĐ</span
                  >
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Buttons -->
      <div class="navigation-section">
        <div class="navigation-container">
          <button class="nav-btn btn-back" @click="goBack">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            Back
          </button>
          <button class="nav-btn btn-next" @click="goNext">
            Next
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M14 5l7 7m0 0l-7 7m7-7H3"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <AppFooter />
  </div>
</template>

<style scoped>
.booking-page {
  min-height: 100vh;
  background: #f8f9fa;
}

/* Loading */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e5e7eb;
  border-top-color: #2d5016;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Banner */
.banner-section {
  width: 100%;
  height: 180px;
  overflow: hidden;
  background: #1f2937;
}

.banner-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.7;
}

/* Progress Indicator */
.progress-section {
  background: white;
  padding: 30px 40px;
  border-bottom: 1px solid #e5e7eb;
}

.progress-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.step-number {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #d1d5db;
  color: #9ca3af;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: 700;
  transition: all 0.3s;
}

.progress-step.active .step-number,
.progress-step.completed .step-number {
  background: #2d5016;
  color: white;
}

.step-label {
  font-size: 0.9rem;
  color: #6b7280;
  font-weight: 500;
}

.progress-step.active .step-label {
  color: #2d5016;
  font-weight: 700;
}

.progress-line {
  width: 100px;
  height: 3px;
  background: #d1d5db;
  transition: all 0.3s;
}

.progress-line.active {
  background: #2d5016;
}

/* Main Section */
.main-section {
  padding: 40px;
  background: #f8f9fa;
}

.booking-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 40px;
}

/* Selection Panel */
.selection-panel {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* Instructions Box */
.instructions-box {
  background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
  border-left: 4px solid #2d5016;
  padding: 20px 24px;
  border-radius: 12px;
  margin-bottom: 32px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.3rem;
  font-weight: 800;
  color: #2d5016;
  margin: 0;
}

.section-title svg {
  width: 24px;
  height: 24px;
  stroke-width: 2.5;
}

/* Picker Section */
.picker-section {
  margin-bottom: 32px;
  padding-bottom: 32px;
  border-bottom: 2px solid #f3f4f6;
}

.picker-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
  margin-bottom: 0;
}

.picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.picker-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.1rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 20px 0;
}

.label-icon {
  font-size: 1.3rem;
}

.clear-btn {
  padding: 8px 16px;
  background: #fee2e2;
  color: #991b1b;
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.clear-btn:hover {
  background: #fecaca;
  transform: translateY(-1px);
}

/* Date Picker */
.date-picker {
  display: flex;
  align-items: center;
  gap: 16px;
}

.date-nav-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 2px solid #e5e7eb;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  flex-shrink: 0;
}

.date-nav-btn:not(:disabled):hover {
  border-color: #2d5016;
  background: #f0fdf4;
}

.date-nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.date-nav-btn svg {
  width: 20px;
  height: 20px;
  color: #2d5016;
}

.dates-container {
  display: flex;
  gap: 12px;
  flex: 1;
  overflow-x: auto;
  scroll-behavior: smooth;
}

.date-card {
  flex: 1;
  min-width: 80px;
  padding: 16px 12px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.date-card:hover {
  border-color: #2d5016;
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(45, 80, 22, 0.15);
}

.date-card.selected {
  background: linear-gradient(135deg, #2d5016 0%, #3d6620 100%);
  border-color: #2d5016;
  color: white;
  box-shadow: 0 6px 16px rgba(45, 80, 22, 0.3);
}

.date-day {
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 8px;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.date-number {
  font-size: 1.8rem;
  font-weight: 800;
  line-height: 1;
  margin-bottom: 4px;
}

.date-month {
  font-size: 0.85rem;
  font-weight: 600;
  opacity: 0.9;
}

/* Time Slots Grid */
.time-slots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 12px;
}

.time-slot-btn {
  padding: 18px 12px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 56px;
}

.time-slot-btn:hover:not(:disabled) {
  border-color: #2d5016;
  background: #f0fdf4;
  transform: translateY(-2px);
  box-shadow: 0 3px 10px rgba(45, 80, 22, 0.15);
}

.time-slot-btn.selected {
  background: linear-gradient(135deg, #2d5016 0%, #3d6620 100%);
  border-color: #2d5016;
  box-shadow: 0 3px 10px rgba(45, 80, 22, 0.3);
}

.time-slot-btn.disabled,
.time-slot-btn:disabled {
  background: #f3f4f6;
  border-color: #e5e7eb;
  cursor: not-allowed;
  opacity: 0.5;
}

.time-slot-btn.disabled .slot-time,
.time-slot-btn:disabled .slot-time {
  color: #9ca3af;
  text-decoration: line-through;
}

.slot-time {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1f2937;
}

.time-slot-btn.selected .slot-time {
  color: white;
  font-weight: 800;
}

/* Details Panel */
.details-panel {
  position: sticky;
  top: 100px;
  height: fit-content;
}

.details-card {
  background: white;
  border-radius: 16px;
  padding: 0;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.details-title {
  font-size: 1rem;
  font-weight: 700;
  color: white;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  padding: 1.5rem 2rem;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  letter-spacing: 0.5px;
}

.details-title svg {
  width: 24px;
  height: 24px;
  stroke-width: 2;
}

.details-content {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-label svg {
  width: 16px;
  height: 16px;
  stroke-width: 2;
}

.detail-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1a1a1a;
  padding-left: 1.5rem;
}

.time-range {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.time-start,
.time-end {
  padding: 0.5rem 1rem;
  background: #f0f9ff;
  border-radius: 8px;
  color: #2563eb;
  font-weight: 600;
}

.time-separator {
  color: #2563eb;
  font-weight: 700;
  font-size: 1.2rem;
}

.price-breakdown {
  margin-top: 1rem;
  padding: 1.5rem;
  background: #f8fafc;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.breakdown-header {
  font-size: 0.85rem;
  font-weight: 700;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.95rem;
  color: #4b5563;
}

.breakdown-item.tier-item {
  padding-left: 0.75rem;
  border-left: 3px solid #e5e7eb;
  margin-bottom: 0.5rem;
}

.breakdown-item span:last-child {
  font-weight: 600;
  color: #1a1a1a;
}

.breakdown-divider {
  height: 1px;
  background: linear-gradient(to right, transparent, #e5e7eb, transparent);
  margin: 0.5rem 0;
}

.breakdown-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.75rem;
  border-top: 2px solid #2563eb;
}

.breakdown-total span:first-child {
  font-size: 1rem;
  font-weight: 700;
  color: #1a1a1a;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.total-amount {
  font-size: 1.75rem;
  font-weight: 800;
  color: #2563eb;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #9ca3af;
}

.empty-state svg {
  width: 64px;
  height: 64px;
  margin: 0 auto 1rem;
  opacity: 0.3;
  stroke-width: 1.5;
}

.empty-state p {
  font-size: 0.95rem;
  line-height: 1.5;
}

/* Navigation */
.navigation-section {
  padding: 30px 40px;
  background: white;
  border-top: 1px solid #e5e7eb;
}

.navigation-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  gap: 20px;
}

.nav-btn {
  padding: 14px 32px;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  border: none;
}

.nav-btn svg {
  width: 20px;
  height: 20px;
}

.btn-back {
  background: #e5e7eb;
  color: #1f2937;
}

.btn-back:hover {
  background: #d1d5db;
  transform: translateX(-4px);
}

.btn-next {
  background: #0a2463;
  color: white;
}

.btn-next:hover {
  background: #0d3380;
  transform: translateX(4px);
}

/* Order Confirmation (Step 2) */
.confirmation-container {
  max-width: 800px;
  margin: 0 auto;
}

.confirmation-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.info-section {
  margin-bottom: 32px;
  padding-bottom: 32px;
  border-bottom: 2px solid #f3f4f6;
}

.info-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
  margin-bottom: 0;
}

.section-heading {
  font-size: 1rem;
  font-weight: 700;
  color: #0a2463;
  margin: 0 0 24px 0;
  letter-spacing: 0.5px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #6b7280;
}

.info-value {
  font-size: 1rem;
  font-weight: 500;
  color: #1f2937;
  padding: 12px 0;
}

.info-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  color: #1f2937;
  transition: all 0.3s;
  background: white;
}

.info-input:focus {
  outline: none;
  border-color: #0a2463;
  box-shadow: 0 0 0 3px rgba(10, 36, 99, 0.1);
}

.info-input::placeholder {
  color: #9ca3af;
}

.payment-section {
  background: #f8fafc;
  padding: 24px;
  border-radius: 12px;
  margin-top: 32px;
}

.payment-section .section-heading {
  margin-bottom: 16px;
}

.payment-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.payment-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.payment-label {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
}

.payment-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0a2463;
}

/* Responsive */
@media (max-width: 1024px) {
  .booking-container {
    grid-template-columns: 1fr;
  }

  .details-panel {
    position: static;
  }
}

@media (max-width: 768px) {
  .main-section,
  .navigation-section {
    padding: 20px;
  }

  .selection-panel {
    padding: 20px;
  }

  .time-slots-grid {
    grid-template-columns: repeat(auto-fill, minmax(85px, 1fr));
    gap: 8px;
  }

  .progress-container {
    gap: 12px;
  }

  .progress-line {
    width: 60px;
  }

  .step-label {
    font-size: 0.8rem;
  }

  .section-title {
    font-size: 1.1rem;
  }

  .instructions-box {
    padding: 16px 20px;
  }

  .date-card {
    min-width: 80px;
    padding: 12px 8px;
  }

  .date-number {
    font-size: 1.5rem;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .confirmation-card {
    padding: 24px;
  }
}

@media (max-width: 480px) {
  .time-slots-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
  }

  .dates-container {
    gap: 8px;
  }

  .date-card {
    min-width: 70px;
    padding: 10px 6px;
  }

  .date-number {
    font-size: 1.3rem;
  }

  .section-title {
    font-size: 1rem;
  }

  .picker-label {
    font-size: 1rem;
  }

  .confirmation-card {
    padding: 20px;
  }

  .section-heading {
    font-size: 0.9rem;
  }
}
</style>
