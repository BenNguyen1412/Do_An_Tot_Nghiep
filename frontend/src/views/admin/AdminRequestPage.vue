<template>
  <AdminDashboardLayout>
    <template #title>Requests Management</template>

    <div class="request-page">
      <!-- Stats Row -->
      <div class="stats-row">
        <div class="stat-item">
          <div class="stat-icon orange">📋</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">Total Requests</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon yellow">⏳</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pending }}</div>
            <div class="stat-label">Pending</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon green">✓</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.approved }}</div>
            <div class="stat-label">Approved</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon red">✕</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.rejected }}</div>
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
            <tr v-if="isLoading">
              <td colspan="6" style="text-align: center; padding: 40px">
                <div style="color: #6b7280">Đang tải...</div>
              </td>
            </tr>
            <tr v-else-if="requests.length === 0">
              <td colspan="6" style="text-align: center; padding: 40px">
                <div style="color: #6b7280">Không có yêu cầu nào</div>
              </td>
            </tr>
            <tr v-else v-for="request in requests" :key="request.id" class="table-row">
              <td>
                <div class="request-name">
                  <div class="request-icon-wrapper Court">
                    <span class="request-icon">🏟️</span>
                  </div>
                  <div class="request-details">
                    <div class="name">{{ request.name }}</div>
                    <div class="request-type-tag">Court Request</div>
                  </div>
                </div>
              </td>
              <td>
                <div class="requester-info">
                  <div class="requester-avatar">
                    {{ getInitials(request.owner?.full_name || 'N/A') }}
                  </div>
                  <span class="requester-name">{{ request.owner?.full_name || 'N/A' }}</span>
                </div>
              </td>
              <td>
                <button
                  class="detail-btn"
                  @click="viewRequestDetails(request)"
                  title="Xem chi tiết"
                >
                  Chi tiết
                </button>
              </td>
              <td>
                <span class="date-text">{{ formatDate(request.created_at) }}</span>
              </td>
              <td>
                <span :class="['status-badge', request.status.toLowerCase()]">
                  {{ request.status }}
                </span>
              </td>
              <td>
                <div class="action-buttons" v-if="request.status === 'pending'">
                  <button
                    class="action-btn approve-btn"
                    title="Approve"
                    @click="approveRequest(request.id)"
                  >
                    ✓
                  </button>
                  <button
                    class="action-btn reject-btn"
                    title="Reject"
                    @click="rejectRequest(request.id)"
                  >
                    ✕
                  </button>
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

    <!-- Request Details Modal -->
    <transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h2>Chi tiết yêu cầu đăng sân</h2>
            <button class="modal-close-btn" @click="closeModal">✕</button>
          </div>

          <div v-if="selectedRequest" class="modal-body">
            <!-- Basic Info -->
            <div class="info-section">
              <h3 class="section-title">Thông tin cơ bản</h3>
              <div class="info-grid">
                <div class="info-item">
                  <label>Tên sân</label>
                  <p>{{ selectedRequest.name }}</p>
                </div>
                <div class="info-item">
                  <label>Số lượng sân</label>
                  <p>{{ selectedRequest.court_quantity }}</p>
                </div>
                <div class="info-item">
                  <label>Địa chỉ</label>
                  <p>{{ selectedRequest.address }}</p>
                </div>
                <div class="info-item">
                  <label>Quận/Huyện</label>
                  <p>{{ selectedRequest.district }}</p>
                </div>
                <div class="info-item">
                  <label>Thành phố</label>
                  <p>{{ selectedRequest.city }}</p>
                </div>
                <div class="info-item">
                  <label>Giờ mở cửa</label>
                  <p>{{ selectedRequest.opening_time }} - {{ selectedRequest.closing_time }}</p>
                </div>
              </div>

              <div class="info-item full-width">
                <label>Mô tả</label>
                <p>{{ selectedRequest.description || 'Không có mô tả' }}</p>
              </div>
            </div>

            <!-- Contact Info -->
            <div class="info-section">
              <h3 class="section-title">Thông tin liên hệ</h3>
              <div class="info-grid">
                <div class="info-item">
                  <label>Số điện thoại</label>
                  <p>{{ selectedRequest.contact_phone }}</p>
                </div>
                <div class="info-item">
                  <label>Email</label>
                  <p>{{ selectedRequest.contact_email || 'Không có' }}</p>
                </div>
                <div class="info-item">
                  <label>Chủ sân</label>
                  <p>{{ selectedRequest.owner?.full_name || 'N/A' }}</p>
                </div>
              </div>
            </div>

            <!-- Facilities -->
            <div class="info-section" v-if="parsedFacilities && parsedFacilities.length > 0">
              <h3 class="section-title">Tiện ích</h3>
              <div class="facilities-list">
                <span v-for="facility in parsedFacilities" :key="facility" class="facility-badge">
                  {{ getFacilityLabel(facility) }}
                </span>
              </div>
            </div>

            <!-- Time Slots -->
            <div class="info-section" v-if="parsedTimeSlots && parsedTimeSlots.length > 0">
              <h3 class="section-title">Khung giờ & Giá</h3>
              <div class="time-slots-list">
                <div v-for="(slot, index) in parsedTimeSlots" :key="index" class="time-slot-item">
                  <span class="time-range">{{ slot.start_time }} - {{ slot.end_time }}</span>
                  <span class="price">{{ formatPrice(slot.price) }}</span>
                </div>
              </div>
            </div>

            <!-- Images -->
            <div class="info-section" v-if="parsedImages && parsedImages.length > 0">
              <h3 class="section-title">Hình ảnh</h3>
              <div class="images-grid">
                <img
                  v-for="(image, index) in parsedImages"
                  :key="index"
                  :src="`http://localhost:8000${image}`"
                  :alt="`Court image ${Number(index) + 1}`"
                  class="court-image"
                />
              </div>
            </div>

            <!-- Status -->
            <div class="info-section">
              <h3 class="section-title">Trạng thái</h3>
              <div class="info-grid">
                <div class="info-item">
                  <label>Trạng thái</label>
                  <span :class="['status-badge', selectedRequest.status.toLowerCase()]">
                    {{ selectedRequest.status }}
                  </span>
                </div>
                <div class="info-item" v-if="selectedRequest.rejection_reason">
                  <label>Lý do từ chối</label>
                  <p>{{ selectedRequest.rejection_reason }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button
              v-if="selectedRequest?.status === 'pending'"
              class="btn-approve"
              @click="approveRequest(selectedRequest.id)"
            >
              ✓ Duyệt
            </button>
            <button
              v-if="selectedRequest?.status === 'pending'"
              class="btn-reject"
              @click="rejectRequest(selectedRequest.id)"
            >
              ✕ Từ chối
            </button>
            <button class="btn-close" @click="closeModal">Đóng</button>
          </div>
        </div>
      </div>
    </transition>
  </AdminDashboardLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import AdminDashboardLayout from '@/layouts/AdminDashboardLayout.vue'
import axiosInstance from '@/utils/axios'
import { useToast } from 'vue-toastification'

const toast = useToast()

interface CourtRequest {
  id: number
  name: string
  address: string
  district: string
  city: string
  description: string | null
  court_quantity: number
  opening_time: string
  closing_time: string
  facilities: string | null
  contact_phone: string
  contact_email: string | null
  images: string | null
  time_slots: string | null
  owner_id: number
  status: string
  rejection_reason: string | null
  reviewed_by: number | null
  reviewed_at: string | null
  created_at: string
  updated_at: string | null
  owner?: {
    id: number
    full_name: string
    email: string
  }
}

const requests = ref<CourtRequest[]>([])
const isLoading = ref(false)
const showModal = ref(false)
const selectedRequest = ref<CourtRequest | null>(null)

const stats = computed(() => {
  const total = requests.value.length
  const pending = requests.value.filter((r) => r.status === 'pending').length
  const approved = requests.value.filter((r) => r.status === 'approved').length
  const rejected = requests.value.filter((r) => r.status === 'rejected').length
  return { total, pending, approved, rejected }
})

const parsedFacilities = computed(() => {
  if (!selectedRequest.value?.facilities) return []
  try {
    return JSON.parse(selectedRequest.value.facilities)
  } catch {
    return []
  }
})

const parsedTimeSlots = computed(() => {
  if (!selectedRequest.value?.time_slots) return []
  try {
    return JSON.parse(selectedRequest.value.time_slots)
  } catch {
    return []
  }
})

const parsedImages = computed(() => {
  if (!selectedRequest.value?.images) return []
  try {
    return JSON.parse(selectedRequest.value.images)
  } catch {
    return []
  }
})

const fetchRequests = async () => {
  isLoading.value = true
  try {
    const response = await axiosInstance.get('/court-requests')
    requests.value = response.data
  } catch (error) {
    console.error('Error fetching requests:', error)
    toast.error('Không thể tải danh sách yêu cầu')
  } finally {
    isLoading.value = false
  }
}

const getInitials = (name: string) => {
  if (!name) return 'N/A'
  const parts = name.trim().split(' ')
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase()
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase()
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

const viewRequestDetails = (request: CourtRequest) => {
  selectedRequest.value = request
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedRequest.value = null
}

const getFacilityLabel = (facilityId: string) => {
  const facilityMap: Record<string, string> = {
    parking: '🚗 Bãi đỗ xe',
    locker: '🔐 Tủ khóa',
    shower: '🚿 Phòng tắm',
    water: '💧 Nước uống',
    toilet: '🚻 Nhà vệ sinh',
  }
  return facilityMap[facilityId] || facilityId
}

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
  }).format(price)
}

const approveRequest = async (requestId: number) => {
  try {
    await axiosInstance.put(`/court-requests/${requestId}`, {
      status: 'approved',
    })
    toast.success('Đã phê duyệt yêu cầu')
    closeModal()
    await fetchRequests()
  } catch (error) {
    console.error('Error approving request:', error)
    toast.error('Không thể phê duyệt yêu cầu')
  }
}

const rejectRequest = async (requestId: number) => {
  const reason = prompt('Nhập lý do từ chối (không bắt buộc):')
  try {
    await axiosInstance.put(`/court-requests/${requestId}`, {
      status: 'rejected',
      rejection_reason: reason || undefined,
    })
    toast.success('Đã từ chối yêu cầu')
    closeModal()
    await fetchRequests()
  } catch (error) {
    console.error('Error rejecting request:', error)
    toast.error('Không thể từ chối yêu cầu')
  }
}

onMounted(() => {
  fetchRequests()
})
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

/* Detail Button */
.detail-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #4169e1 0%, #5a7fee 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(65, 105, 225, 0.2);
}

.detail-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(65, 105, 225, 0.4);
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
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

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 16px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 24px 32px;
  border-bottom: 2px solid #f3f4f6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

.modal-close-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: none;
  background: #f3f4f6;
  cursor: pointer;
  font-size: 20px;
  color: #6b7280;
  transition: all 0.2s ease;
}

.modal-close-btn:hover {
  background: #e5e7eb;
  color: #374151;
}

.modal-body {
  padding: 32px;
  overflow-y: auto;
  flex: 1;
}

.info-section {
  margin-bottom: 32px;
}

.info-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #e5e7eb;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-item label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-item p {
  margin: 0;
  font-size: 0.95rem;
  color: #1f2937;
}

.facilities-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.facility-badge {
  padding: 8px 16px;
  background: #eff6ff;
  color: #1e40af;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
}

.time-slots-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.time-slot-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.time-range {
  font-size: 0.9rem;
  color: #374151;
  font-weight: 600;
}

.price {
  font-size: 0.95rem;
  color: #059669;
  font-weight: 700;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.court-image {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 12px;
  border: 2px solid #e5e7eb;
}

.modal-footer {
  padding: 20px 32px;
  border-top: 2px solid #f3f4f6;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-approve,
.btn-reject,
.btn-close {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn-approve {
  background: #10b981;
  color: white;
}

.btn-approve:hover {
  background: #059669;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-reject {
  background: #ef4444;
  color: white;
}

.btn-reject:hover {
  background: #dc2626;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.btn-close {
  background: #f3f4f6;
  color: #374151;
}

.btn-close:hover {
  background: #e5e7eb;
}

/* Modal Animation */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.3s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.9);
}

@media (max-width: 1024px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  .card-header h2 {
    font-size: 1.35rem;
  }

  .request-table {
    font-size: 14px;
  }

  .modal-container {
    max-width: 90%;
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

  .request-table {
    font-size: 13px;
  }

  .request-table th,
  .request-table td {
    padding: 10px 8px;
  }

  .modal-container {
    max-width: 100%;
    max-height: 95vh;
    margin: 10px;
  }

  .modal-header h3 {
    font-size: 1.25rem;
  }

  .modal-body {
    padding: 20px;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons button {
    width: 100%;
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

  .request-table {
    font-size: 12px;
  }

  .request-table th,
  .request-table td {
    padding: 8px 6px;
  }

  .modal-header h3 {
    font-size: 1.1rem;
  }

  .modal-body {
    padding: 16px;
  }
}
</style>
