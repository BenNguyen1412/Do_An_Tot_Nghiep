<script setup lang="ts">
import { ref, onMounted } from 'vue'

defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

interface Booking {
  id: number
  court_name: string
  date: string
  time: string
  duration: string
  status: 'confirmed' | 'pending' | 'cancelled' | 'completed'
  total_price: number
  location: string
}

const bookings = ref<Booking[]>([
  // Mock data - sẽ được thay thế bằng API call
  {
    id: 1,
    court_name: 'Sân Pickleball VIP A1',
    date: '2025-11-28',
    time: '18:00',
    duration: '2 giờ',
    status: 'confirmed',
    total_price: 300000,
    location: 'Quận 1, TP.HCM',
  },
  {
    id: 2,
    court_name: 'Sân Pickleball Premium B2',
    date: '2025-11-25',
    time: '15:00',
    duration: '1 giờ',
    status: 'completed',
    total_price: 150000,
    location: 'Quận 3, TP.HCM',
  },
  {
    id: 3,
    court_name: 'Sân Pickleball Standard C3',
    date: '2025-11-20',
    time: '09:00',
    duration: '1.5 giờ',
    status: 'cancelled',
    total_price: 200000,
    location: 'Quận 7, TP.HCM',
  },
])

const activeTab = ref<'all' | 'confirmed' | 'completed' | 'cancelled'>('all')

const filteredBookings = ref<Booking[]>([])

const filterBookings = () => {
  if (activeTab.value === 'all') {
    filteredBookings.value = bookings.value
  } else {
    filteredBookings.value = bookings.value.filter((b) => b.status === activeTab.value)
  }
}

onMounted(() => {
  filterBookings()
})

const setActiveTab = (tab: typeof activeTab.value) => {
  activeTab.value = tab
  filterBookings()
}

const closeModal = () => {
  emit('close')
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('vi-VN', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
  }).format(price)
}

const getStatusInfo = (status: string) => {
  const statusMap = {
    confirmed: { label: 'Đã xác nhận', color: '#3b82f6', bg: '#dbeafe' },
    pending: { label: 'Chờ xác nhận', color: '#f59e0b', bg: '#fef3c7' },
    cancelled: { label: 'Đã hủy', color: '#ef4444', bg: '#fee2e2' },
    completed: { label: 'Hoàn thành', color: '#10b981', bg: '#d1fae5' },
  }
  return statusMap[status as keyof typeof statusMap] || statusMap.pending
}

const viewDetails = (booking: Booking) => {
  console.log('View booking details:', booking)
  // TODO: Show booking details modal
}

const cancelBooking = (booking: Booking) => {
  if (confirm('Bạn có chắc chắn muốn hủy lịch đặt sân này?')) {
    console.log('Cancel booking:', booking)
    // TODO: Call API to cancel booking
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
        <div class="modal-container">
          <!-- Header -->
          <div class="modal-header">
            <div class="header-content">
              <div class="header-icon">
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
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
              </div>
              <h2 class="modal-title">Lịch sử đặt sân</h2>
            </div>
            <button class="close-btn" @click="closeModal">
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
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <!-- Tabs -->
          <div class="tabs-container">
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'all' }"
              @click="setActiveTab('all')"
            >
              <span>Tất cả</span>
              <span class="tab-count">{{ bookings.length }}</span>
            </button>
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'confirmed' }"
              @click="setActiveTab('confirmed')"
            >
              <span>Đã xác nhận</span>
              <span class="tab-count">{{
                bookings.filter((b) => b.status === 'confirmed').length
              }}</span>
            </button>
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'completed' }"
              @click="setActiveTab('completed')"
            >
              <span>Hoàn thành</span>
              <span class="tab-count">{{
                bookings.filter((b) => b.status === 'completed').length
              }}</span>
            </button>
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'cancelled' }"
              @click="setActiveTab('cancelled')"
            >
              <span>Đã hủy</span>
              <span class="tab-count">{{
                bookings.filter((b) => b.status === 'cancelled').length
              }}</span>
            </button>
          </div>

          <!-- Body -->
          <div class="modal-body">
            <div v-if="filteredBookings.length === 0" class="empty-state">
              <div class="empty-icon">📋</div>
              <h3 class="empty-title">Chưa có lịch đặt sân</h3>
              <p class="empty-description">Bạn chưa có lịch đặt sân nào trong danh mục này</p>
            </div>

            <div v-else class="bookings-list">
              <div v-for="booking in filteredBookings" :key="booking.id" class="booking-card">
                <div class="booking-header">
                  <div class="booking-court">
                    <span class="court-icon">🏟️</span>
                    <div class="court-info">
                      <h3 class="court-name">{{ booking.court_name }}</h3>
                      <p class="court-location">📍 {{ booking.location }}</p>
                    </div>
                  </div>
                  <div
                    class="booking-status"
                    :style="{
                      background: getStatusInfo(booking.status).bg,
                      color: getStatusInfo(booking.status).color,
                    }"
                  >
                    {{ getStatusInfo(booking.status).label }}
                  </div>
                </div>

                <div class="booking-details">
                  <div class="detail-item">
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
                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                    <span>{{ formatDate(booking.date) }}</span>
                  </div>
                  <div class="detail-item">
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
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    <span>{{ booking.time }} - {{ booking.duration }}</span>
                  </div>
                  <div class="detail-item price">
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
                        d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    <span>{{ formatPrice(booking.total_price) }}</span>
                  </div>
                </div>

                <div class="booking-actions">
                  <button class="action-btn view" @click="viewDetails(booking)">
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
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                      />
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                      />
                    </svg>
                    Chi tiết
                  </button>
                  <button
                    v-if="booking.status === 'confirmed'"
                    class="action-btn cancel"
                    @click="cancelBooking(booking)"
                  >
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
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                    Hủy đặt
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
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
  z-index: 9999;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Header */
.modal-header {
  padding: 24px 28px;
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-icon svg {
  width: 24px;
  height: 24px;
  color: white;
}

.modal-title {
  color: white;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
}

.close-btn {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: rotate(90deg);
}

.close-btn svg {
  width: 20px;
  height: 20px;
  color: white;
}

/* Tabs */
.tabs-container {
  display: flex;
  gap: 4px;
  padding: 16px 28px 0;
  background: #f9fafb;
  border-bottom: 2px solid #e5e7eb;
}

.tab-btn {
  flex: 1;
  padding: 12px 16px;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 600;
  color: #6b7280;
  font-size: 0.9rem;
}

.tab-btn:hover {
  color: #2d5016;
  background: rgba(45, 80, 22, 0.05);
}

.tab-btn.active {
  color: #2d5016;
  border-bottom-color: #2d5016;
}

.tab-count {
  background: #e5e7eb;
  color: #6b7280;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
}

.tab-btn.active .tab-count {
  background: #2d5016;
  color: white;
}

/* Body */
.modal-body {
  padding: 24px 28px;
  overflow-y: auto;
  flex: 1;
  background: #f9fafb;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #374151;
  margin: 0 0 8px 0;
}

.empty-description {
  color: #6b7280;
  font-size: 0.95rem;
  margin: 0;
}

/* Bookings List */
.bookings-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.booking-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 2px solid #e5e7eb;
  transition: all 0.3s ease;
}

.booking-card:hover {
  border-color: #2d5016;
  box-shadow: 0 8px 24px rgba(45, 80, 22, 0.15);
  transform: translateY(-2px);
}

.booking-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.booking-court {
  display: flex;
  gap: 12px;
  flex: 1;
}

.court-icon {
  font-size: 2rem;
}

.court-info {
  flex: 1;
}

.court-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.court-location {
  font-size: 0.85rem;
  color: #6b7280;
  margin: 0;
}

.booking-status {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
  white-space: nowrap;
}

.booking-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  font-size: 0.9rem;
}

.detail-item svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.detail-item.price {
  color: #2d5016;
  font-weight: 700;
  font-size: 1rem;
}

.booking-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  flex: 1;
  padding: 10px 16px;
  border-radius: 10px;
  border: none;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.action-btn.view {
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  color: white;
}

.action-btn.view:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(45, 80, 22, 0.3);
}

.action-btn.cancel {
  background: #fee2e2;
  color: #dc2626;
  border: 2px solid #fecaca;
}

.action-btn.cancel:hover {
  background: #fecaca;
  border-color: #fca5a5;
}

/* Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.9);
}

/* Responsive */
@media (max-width: 768px) {
  .modal-container {
    max-width: 100%;
    border-radius: 20px 20px 0 0;
    margin-top: auto;
  }

  .tabs-container {
    overflow-x: auto;
    padding: 12px 20px 0;
  }

  .tab-btn {
    flex: none;
    min-width: 120px;
  }

  .modal-header,
  .modal-body {
    padding: 20px;
  }

  .booking-header {
    flex-direction: column;
  }

  .booking-details {
    grid-template-columns: 1fr;
  }

  .booking-actions {
    flex-direction: column;
  }
}
</style>
