<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import axiosInstance from '@/utils/axios'

const toast = useToast()

interface Court {
  id: number
  name: string
  address: string
  district: string
  city: string
  court_quantity: number
  opening_time: string
  closing_time: string
  individual_courts?: IndividualCourt[]
}

interface IndividualCourt {
  id: number
  court_id: number
  name: string
  is_available: boolean
}

interface CourtItem {
  id: number
  name: string
  isBooked: boolean
  bookedBy?: {
    phone: string
    timeSlot: string
  }
  isEditing: boolean
  tempName: string
}

// Real data from API
const courts = ref<CourtItem[]>([])
const isLoading = ref(false)
const venueInfo = ref({
  name: 'Chưa có sân',
  totalCourts: 0,
})
const myVenues = ref<Court[]>([])

// Generate courts based on quantity
const generateCourts = (quantity: number) => {
  const newCourts: CourtItem[] = []
  for (let i = 1; i <= quantity; i++) {
    newCourts.push({
      id: i,
      name: `Sân ${i}`,
      isBooked: false,
      isEditing: false,
      tempName: `Sân ${i}`,
    })
  }
  return newCourts
}

// Fetch courts from API
const fetchMyCourts = async () => {
  isLoading.value = true
  try {
    const response = await axiosInstance.get<Court[]>('/courts/my')
    myVenues.value = response.data

    // If user has venues, show the first one
    if (myVenues.value.length > 0) {
      const firstVenue = myVenues.value[0]
      venueInfo.value = {
        name: firstVenue.name,
        totalCourts: firstVenue.court_quantity,
      }

      // Convert individual courts to CourtItem format
      if (firstVenue.individual_courts) {
        courts.value = firstVenue.individual_courts.map((ic) => ({
          id: ic.id,
          name: ic.name,
          isBooked: !ic.is_available,
          isEditing: false,
          tempName: ic.name,
        }))
      } else {
        courts.value = generateCourts(firstVenue.court_quantity)
      }
    } else {
      courts.value = []
      toast.info('Bạn chưa có sân nào. Hãy đăng tải sân mới!')
    }
  } catch (error) {
    console.error('Error fetching courts:', error)
    const err = error as { response?: { data?: { detail?: string } } }
    toast.error(err.response?.data?.detail || 'Không thể tải danh sách sân')
  } finally {
    isLoading.value = false
  }
}

// Initialize courts on mount
onMounted(() => {
  fetchMyCourts()
})

const availableCourts = computed(() => courts.value.filter((c) => !c.isBooked).length)
const bookedCourts = computed(() => courts.value.filter((c) => c.isBooked).length)

const startEditCourtName = (court: CourtItem) => {
  court.isEditing = true
  court.tempName = court.name
}

const cancelEditCourtName = (court: CourtItem) => {
  court.isEditing = false
  court.tempName = court.name
}

const saveCourtName = async (court: CourtItem) => {
  if (!court.tempName.trim()) {
    toast.error('Tên sân không được để trống')
    return
  }

  try {
    // TODO: Call API to update court name
    court.name = court.tempName
    court.isEditing = false
    toast.success('Đã cập nhật tên sân')
  } catch (error) {
    console.error('Error updating court name:', error)
    toast.error('Cập nhật tên sân thất bại')
  }
}

const getCourtStatusClass = (court: CourtItem) => {
  return court.isBooked ? 'court-booked' : 'court-available'
}

const refreshCourts = async () => {
  await fetchMyCourts()
  toast.success('Đã làm mới danh sách')
}
</script>

<template>
  <div class="court-list-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            style="
              width: 40px;
              height: 40px;
              display: inline-block;
              vertical-align: middle;
              margin-right: 8px;
            "
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
          Danh sách sân
        </h1>
        <p class="page-subtitle">Quản lý và theo dõi tình trạng các sân của bạn</p>
      </div>
      <button class="refresh-btn" @click="refreshCourts" :disabled="isLoading">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          :class="{ 'animate-spin': isLoading }"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
        Làm mới
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon stat-icon-total">
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
              d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
            />
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-label">Tổng số sân</span>
          <span class="stat-value">{{ courts.length }}</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon stat-icon-available">
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
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-label">Sân trống</span>
          <span class="stat-value">{{ availableCourts }}</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon stat-icon-booked">
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
        </div>
        <div class="stat-content">
          <span class="stat-label">Đang được đặt</span>
          <span class="stat-value">{{ bookedCourts }}</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon stat-icon-rate">
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
              d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
            />
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-label">Tỷ lệ đặt sân</span>
          <span class="stat-value"
            >{{ courts.length > 0 ? Math.round((bookedCourts / courts.length) * 100) : 0 }}%</span
          >
        </div>
      </div>
    </div>

    <!-- Courts Table -->
    <div class="courts-table-container">
      <div class="table-header">
        <h2 class="table-title">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <rect x="4" y="10" width="16" height="8" rx="2" fill="#10b981" />
            <rect x="7" y="6" width="10" height="4" rx="2" fill="#fbbf24" />
            <rect x="9" y="2" width="6" height="4" rx="2" fill="#3b82f6" />
          </svg>
          Chi tiết các sân
        </h2>
      </div>

      <div class="table-wrapper">
        <table class="courts-table">
          <thead>
            <tr>
              <th>STT</th>
              <th>Tên sân</th>
              <th>Trạng thái</th>
              <th>Khung giờ</th>
              <th>SĐT người đặt</th>
              <th>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="court in courts" :key="court.id" :class="getCourtStatusClass(court)">
              <td>{{ court.id }}</td>
              <td class="court-name-cell">
                <template v-if="!court.isEditing">
                  <span class="court-name">{{ court.name }}</span>
                </template>
                <template v-else>
                  <input
                    v-model="court.tempName"
                    type="text"
                    class="court-name-input"
                    @keyup.enter="saveCourtName(court)"
                    @keyup.esc="cancelEditCourtName(court)"
                  />
                </template>
              </td>
              <td>
                <span
                  class="status-badge"
                  :class="court.isBooked ? 'status-booked' : 'status-available'"
                >
                  <svg
                    v-if="court.isBooked"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                    />
                  </svg>
                  <svg
                    v-else
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  {{ court.isBooked ? 'Đang được đặt' : 'Còn trống' }}
                </span>
              </td>
              <td>
                <span v-if="court.isBooked && court.bookedBy" class="time-slot">
                  {{ court.bookedBy.timeSlot }}
                </span>
                <span v-else class="text-muted">—</span>
              </td>
              <td>
                <a
                  v-if="court.isBooked && court.bookedBy"
                  :href="`tel:${court.bookedBy.phone}`"
                  class="phone-link"
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
                      d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                    />
                  </svg>
                  {{ court.bookedBy.phone }}
                </a>
                <span v-else class="text-muted">—</span>
              </td>
              <td>
                <div class="action-buttons">
                  <template v-if="!court.isEditing">
                    <button class="btn-edit" @click="startEditCourtName(court)" title="Đổi tên sân">
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
                          d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                        />
                      </svg>
                    </button>
                  </template>
                  <template v-else>
                    <button class="btn-save" @click="saveCourtName(court)" title="Lưu">
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
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                    </button>
                    <button class="btn-cancel" @click="cancelEditCourtName(court)" title="Hủy">
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
                  </template>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="courts.length === 0" class="empty-state">
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
            d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
          />
        </svg>
        <p class="empty-text">Chưa có sân nào</p>
        <p class="empty-hint">Hãy đăng tải sân và nhập số lượng sân để tự động tạo danh sách</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.court-list-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Page Header */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #1f2937;
  margin: 0 0 4px 0;
  display: flex;
  align-items: center;
}

.page-subtitle {
  color: #6b7280;
  font-size: 0.95rem;
  margin: 0;
}

.refresh-btn {
  padding: 12px 24px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.refresh-btn:hover:not(:disabled) {
  border-color: #2d5016;
  color: #2d5016;
  background: #f0fdf4;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-btn svg {
  width: 18px;
  height: 18px;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
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
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon svg {
  width: 28px;
  height: 28px;
  color: white;
}

.stat-icon-total {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.stat-icon-available {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.stat-icon-booked {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.stat-icon-rate {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 0.85rem;
  color: #6b7280;
  font-weight: 500;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 800;
  color: #1f2937;
}

/* Courts Table */
.courts-table-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.table-header {
  padding: 24px 28px;
  border-bottom: 2px solid #f3f4f6;
  background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
}

.table-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.table-title svg {
  width: 28px;
  height: 28px;
}

.table-wrapper {
  overflow-x: auto;
}

.courts-table {
  width: 100%;
  border-collapse: collapse;
}

.courts-table thead {
  background: #f9fafb;
}

.courts-table th {
  padding: 16px 20px;
  text-align: left;
  font-size: 0.85rem;
  font-weight: 700;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #e5e7eb;
}

.courts-table tbody tr {
  transition: all 0.3s ease;
  border-bottom: 1px solid #f3f4f6;
}

.courts-table tbody tr:hover {
  background: #f9fafb;
}

.courts-table tbody tr.court-available {
  background: linear-gradient(90deg, #f0fdf4 0%, #ffffff 100%);
}

.courts-table tbody tr.court-booked {
  background: linear-gradient(90deg, #fef3c7 0%, #ffffff 100%);
}

.courts-table td {
  padding: 18px 20px;
  font-size: 0.95rem;
  color: #374151;
}

.court-name-cell {
  font-weight: 600;
}

.court-name {
  color: #1f2937;
}

.court-name-input {
  width: 100%;
  padding: 8px 12px;
  border: 2px solid #2d5016;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  outline: none;
  transition: all 0.3s ease;
}

.court-name-input:focus {
  box-shadow: 0 0 0 3px rgba(45, 80, 22, 0.1);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
}

.status-badge svg {
  width: 16px;
  height: 16px;
}

.status-available {
  background: #dcfce7;
  color: #166534;
}

.status-booked {
  background: #fef3c7;
  color: #92400e;
}

.time-slot {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #f3f4f6;
  border-radius: 6px;
  font-weight: 600;
  color: #374151;
}

.phone-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #dbeafe;
  border-radius: 6px;
  font-weight: 600;
  color: #1e40af;
  text-decoration: none;
  transition: all 0.3s ease;
}

.phone-link:hover {
  background: #3b82f6;
  color: white;
}

.phone-link svg {
  width: 14px;
  height: 14px;
}

.text-muted {
  color: #9ca3af;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-edit,
.btn-save,
.btn-cancel {
  width: 36px;
  height: 36px;
  padding: 0;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.btn-edit:hover {
  background: #dbeafe;
  border-color: #3b82f6;
}

.btn-edit svg {
  width: 18px;
  height: 18px;
  color: #3b82f6;
}

.btn-save:hover {
  background: #dcfce7;
  border-color: #10b981;
}

.btn-save svg {
  width: 18px;
  height: 18px;
  color: #10b981;
}

.btn-cancel:hover {
  background: #fee2e2;
  border-color: #ef4444;
}

.btn-cancel svg {
  width: 18px;
  height: 18px;
  color: #ef4444;
}

/* Empty State */
.empty-state {
  padding: 64px 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  text-align: center;
}

.empty-state svg {
  width: 80px;
  height: 80px;
  color: #d1d5db;
}

.empty-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: #6b7280;
  margin: 0;
}

.empty-hint {
  font-size: 0.95rem;
  color: #9ca3af;
  margin: 0;
  max-width: 400px;
}

/* Responsive */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .table-wrapper {
    overflow-x: scroll;
  }

  .courts-table {
    min-width: 800px;
  }
}
</style>
