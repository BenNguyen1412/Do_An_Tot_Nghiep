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

interface Booking {
  id: number
  booking_date: string
  start_time: string
  end_time: string
  phone_number: string
  status: string
}

interface IndividualCourt {
  id: number
  court_id: number
  name: string
  is_available: boolean
  bookings?: Booking[]
}

interface CourtItem {
  id: number
  name: string
  isBooked: boolean
  bookedBy?: {
    phone: string
    timeSlot: string
    bookingDate: string
  }
  bookingId?: number
  isEditing: boolean
  tempName: string
}

interface BookingForm {
  booking_date: string
  start_time: string
  end_time: string
  phone_number: string
}

// Real data from API
const courts = ref<CourtItem[]>([])
const isLoading = ref(false)
const venueInfo = ref({
  name: 'Chưa có sân',
  totalCourts: 0,
  opening_time: '06:00',
  closing_time: '22:00',
})
const myVenues = ref<Court[]>([])

// Booking form state
const bookingForms = ref<Record<number, BookingForm>>({})

// Initialize booking form for a court
const initBookingForm = (courtId: number) => {
  bookingForms.value[courtId] = {
    booking_date: '',
    start_time: '',
    end_time: '',
    phone_number: '',
  }
}

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
        opening_time: firstVenue.opening_time,
        closing_time: firstVenue.closing_time,
      }

      // Fetch individual courts with bookings for detailed info
      try {
        const detailResponse = await axiosInstance.get<IndividualCourt[]>(
          `/courts/${firstVenue.id}/individual-courts`,
        )

        console.log('📊 Individual courts data:', detailResponse.data)

        courts.value = detailResponse.data.map((ic) => {
          const activeBooking = ic.bookings?.find((b) => b.status === 'active')
          const hasActiveBooking = !!activeBooking

          console.log(`⚽ Sân ${ic.name}:`, {
            is_available: ic.is_available,
            hasActiveBooking,
            activeBooking,
          })

          return {
            id: ic.id,
            name: ic.name,
            isBooked: hasActiveBooking,
            bookedBy: activeBooking
              ? {
                  phone: activeBooking.phone_number,
                  timeSlot: `${activeBooking.start_time} - ${activeBooking.end_time}`,
                  bookingDate: new Date(activeBooking.booking_date).toLocaleDateString('vi-VN'),
                }
              : undefined,
            bookingId: activeBooking?.id,
            isEditing: false,
            tempName: ic.name,
          }
        })
      } catch (detailError) {
        console.error('Error fetching individual courts details:', detailError)
        // Fallback to basic info
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
  // Initialize booking form if court is available
  if (!court.isBooked) {
    initBookingForm(court.id)
  }
}

const cancelEditCourtName = (court: CourtItem) => {
  court.isEditing = false
  court.tempName = court.name
  // Clear booking form
  delete bookingForms.value[court.id]
}

const saveCourtName = async (court: CourtItem) => {
  if (!court.tempName.trim()) {
    toast.error('Tên sân không được để trống')
    return
  }

  try {
    // Update court name
    await axiosInstance.put(`/individual-courts/${court.id}`, {
      name: court.tempName,
    })

    // If court is available and booking form is filled, create booking
    if (!court.isBooked && bookingForms.value[court.id]) {
      const form = bookingForms.value[court.id]

      // Validate booking form if any field is filled
      const hasBookingData =
        form.booking_date || form.start_time || form.end_time || form.phone_number

      if (hasBookingData) {
        // Validate all fields are filled
        if (!form.booking_date || !form.start_time || !form.end_time || !form.phone_number) {
          toast.error('Vui lòng điền đầy đủ thông tin đặt sân hoặc để trống tất cả')
          return
        }

        // Validate phone number
        if (!/^\d{10}$/.test(form.phone_number)) {
          toast.error('Số điện thoại phải gồm 10 chữ số')
          return
        }

        // Validate time range
        if (form.end_time <= form.start_time) {
          toast.error('Giờ kết thúc phải sau giờ bắt đầu')
          return
        }

        // Validate booking time within opening hours
        if (
          form.start_time < venueInfo.value.opening_time ||
          form.end_time > venueInfo.value.closing_time
        ) {
          toast.error(
            `Thời gian đặt sân phải nằm trong giờ mở cửa (${venueInfo.value.opening_time} - ${venueInfo.value.closing_time})`,
          )
          return
        }

        // Create booking
        const bookingDate = new Date(form.booking_date)
        await axiosInstance.post('/bookings', {
          individual_court_id: court.id,
          booking_date: bookingDate.toISOString(),
          start_time: form.start_time,
          end_time: form.end_time,
          phone_number: form.phone_number,
        })
      }
    }

    court.name = court.tempName
    court.isEditing = false
    delete bookingForms.value[court.id]

    // Refresh courts list
    await fetchMyCourts()

    toast.success('Đã cập nhật thành công')
  } catch (error) {
    console.error('Error updating court:', error)
    const err = error as { response?: { data?: { detail?: string } } }
    toast.error(err.response?.data?.detail || 'Cập nhật thất bại')
  }
}

const getCourtStatusClass = (court: CourtItem) => {
  return court.isBooked ? 'court-booked' : 'court-available'
}

const cancelBooking = async (court: CourtItem) => {
  if (!court.bookingId) {
    toast.error('Không tìm thấy thông tin đặt sân')
    return
  }

  if (!confirm(`Bạn có chắc chắn muốn hủy đơn đặt sân "${court.name}"?`)) {
    return
  }

  try {
    await axiosInstance.delete(`/bookings/${court.bookingId}`)
    toast.success('Đã hủy đơn đặt sân thành công')
    await fetchMyCourts()
  } catch (error) {
    console.error('Error canceling booking:', error)
    const err = error as { response?: { data?: { detail?: string } } }
    toast.error(err.response?.data?.detail || 'Hủy đơn thất bại')
  }
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
              <th>Ngày đặt</th>
              <th>Khung giờ</th>
              <th>SĐT người đặt</th>
              <th>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="(court, index) in courts" :key="court.id">
              <tr :class="[getCourtStatusClass(court), { 'editing-row': court.isEditing }]">
                <td>{{ index + 1 }}</td>
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
                  <span v-if="court.isBooked && court.bookedBy" class="booking-date">
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
                    {{ court.bookedBy.bookingDate }}
                  </span>
                  <span v-else class="text-muted">—</span>
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
                      <!-- Nếu sân đang được đặt: hiển thị nút Hủy đơn -->
                      <button
                        v-if="court.isBooked"
                        class="btn-cancel-booking"
                        @click="cancelBooking(court)"
                        title="Hủy đơn đặt sân"
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
                        Hủy đơn
                      </button>
                      <!-- Nếu sân trống: hiển thị nút Chỉnh sửa -->
                      <button
                        v-else
                        class="btn-edit"
                        @click="startEditCourtName(court)"
                        title="Chỉnh sửa"
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

              <!-- Booking Form Expansion (only for available courts in edit mode) -->
              <tr
                v-if="court.isEditing && !court.isBooked && bookingForms[court.id]"
                class="booking-form-row"
              >
                <td colspan="7">
                  <div class="booking-form-container">
                    <div class="booking-form-header">
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
                      <h4>Đặt lịch cho khách hàng (Tùy chọn)</h4>
                    </div>

                    <div class="booking-form-grid">
                      <div class="form-group">
                        <label>
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
                          Ngày đặt sân
                        </label>
                        <input
                          v-model="bookingForms[court.id].booking_date"
                          type="date"
                          class="form-input"
                        />
                      </div>

                      <div class="form-group">
                        <label>
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
                          Giờ bắt đầu
                        </label>
                        <input
                          v-model="bookingForms[court.id].start_time"
                          type="time"
                          class="form-input"
                        />
                      </div>

                      <div class="form-group">
                        <label>
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
                          Giờ kết thúc
                        </label>
                        <input
                          v-model="bookingForms[court.id].end_time"
                          type="time"
                          class="form-input"
                        />
                      </div>

                      <div class="form-group">
                        <label>
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
                          Số điện thoại
                        </label>
                        <input
                          v-model="bookingForms[court.id].phone_number"
                          type="tel"
                          placeholder="Nhập 10 chữ số"
                          maxlength="10"
                          class="form-input"
                        />
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            </template>
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

.booking-date {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #fef3c7;
  border-radius: 6px;
  font-weight: 600;
  color: #92400e;
}

.booking-date svg {
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

.btn-cancel-booking {
  padding: 8px 14px;
  border: 2px solid #ef4444;
  border-radius: 8px;
  background: white;
  color: #ef4444;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.btn-cancel-booking:hover {
  background: #ef4444;
  color: white;
}

.btn-cancel-booking svg {
  width: 16px;
  height: 16px;
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

/* Editing Row Highlight */
.editing-row {
  background: linear-gradient(90deg, #dbeafe 0%, #ffffff 100%) !important;
  border-left: 4px solid #3b82f6;
}

/* Booking Form Expansion Row */
.booking-form-row {
  background: #f8fafc;
  border-bottom: 2px solid #e5e7eb;
}

.booking-form-container {
  padding: 24px;
  background: white;
  border-radius: 12px;
  margin: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.booking-form-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e5e7eb;
}

.booking-form-header svg {
  width: 24px;
  height: 24px;
  color: #3b82f6;
}

.booking-form-header h4 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #1f2937;
}

.booking-form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 6px;
}

.form-group label svg {
  width: 16px;
  height: 16px;
  color: #6b7280;
}

.form-input {
  padding: 10px 14px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  outline: none;
  transition: all 0.3s ease;
}

.form-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
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

  .booking-form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
