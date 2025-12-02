<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/auth'
import axiosInstance from '@/utils/axios'

const toast = useToast()
const authStore = useAuthStore()
const router = useRouter()

// Time slots for pricing
interface TimeSlot {
  id: string
  startTime: string
  endTime: string
  price: string
}

// Form data
const courtForm = ref({
  name: '',
  address: '',
  district: '',
  city: '',
  description: '',
  court_quantity: 1,
  opening_time: '06:00',
  closing_time: '22:00',
  facilities: [] as string[],
  contact_phone: '',
  contact_email: '',
})

const timeSlots = ref<TimeSlot[]>([])
let nextSlotId = 1

// Load user info and check for existing court on mount
onMounted(async () => {
  if (authStore.user) {
    courtForm.value.contact_phone = authStore.user.phone_number || ''
    courtForm.value.contact_email = authStore.user.email || ''

    // Check if we have a current court ID in localStorage for this user
    const storageKey = `currentCourtId_${authStore.user.id}`
    const savedCourtId = localStorage.getItem(storageKey)
    if (savedCourtId) {
      await loadCourtInfo(parseInt(savedCourtId))
    }
  }
})

const images = ref<File[]>([])
const imagePreviews = ref<string[]>([])

// Edit mode
const isEditMode = ref(false)
const currentCourtId = ref<number | null>(null)
const individualCourts = ref<
  Array<{
    id: number
    name: string
    is_available: boolean
  }>
>([])

// Available facilities
const availableFacilities = [
  { id: 'parking', label: 'Bãi đỗ xe', icon: '🚗' },
  { id: 'locker', label: 'Tủ khóa', icon: '🔐' },
  { id: 'shower', label: 'Phòng tắm', icon: '🚿' },
  { id: 'water', label: 'Nước uống', icon: '💧' },
  { id: 'toilet', label: 'Nhà vệ sinh', icon: '🚻' },
  { id: 'lighting', label: 'Đèn chiếu sáng', icon: '💡' },
  { id: 'wifi', label: 'WiFi', icon: '📶' },
  { id: 'shop', label: 'Cửa hàng', icon: '🏪' },
]

const isSaving = ref(false)

const addTimeSlot = () => {
  timeSlots.value.push({
    id: String(nextSlotId++),
    startTime: '',
    endTime: '',
    price: '',
  })
}

const removeTimeSlot = (id: string) => {
  const index = timeSlots.value.findIndex((slot) => slot.id === id)
  if (index > -1) {
    timeSlots.value.splice(index, 1)
  }
}

const toggleFacility = (facilityId: string) => {
  const index = courtForm.value.facilities.indexOf(facilityId)
  if (index > -1) {
    courtForm.value.facilities.splice(index, 1)
  } else {
    courtForm.value.facilities.push(facilityId)
  }
}

const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = Array.from(target.files || [])

  if (images.value.length + files.length > 10) {
    toast.error('Tối đa 10 hình ảnh')
    return
  }

  files.forEach((file) => {
    if (!file.type.startsWith('image/')) {
      toast.error('Chỉ chấp nhận file hình ảnh')
      return
    }

    if (file.size > 5 * 1024 * 1024) {
      toast.error('Kích thước ảnh không được vượt quá 5MB')
      return
    }

    images.value.push(file)

    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreviews.value.push(e.target?.result as string)
    }
    reader.readAsDataURL(file)
  })
}

const removeImage = (index: number) => {
  images.value.splice(index, 1)
  imagePreviews.value.splice(index, 1)
}

const validateForm = () => {
  if (!courtForm.value.name.trim()) {
    toast.error('Vui lòng nhập tên sân')
    return false
  }
  if (!courtForm.value.court_quantity || courtForm.value.court_quantity < 1) {
    toast.error('Số lượng sân phải từ 1 trở lên')
    return false
  }

  if (!courtForm.value.address.trim()) {
    toast.error('Vui lòng nhập địa chỉ')
    return false
  }

  if (!courtForm.value.district.trim()) {
    toast.error('Vui lòng nhập quận/huyện')
    return false
  }

  if (!courtForm.value.city.trim()) {
    toast.error('Vui lòng nhập thành phố')
    return false
  }

  // Validate time slots
  if (timeSlots.value.length === 0) {
    toast.error('Vui lòng thêm ít nhất một khung giờ')
    return false
  }

  for (const slot of timeSlots.value) {
    if (!slot.startTime || !slot.endTime) {
      toast.error('Vui lòng nhập đầy đủ giờ bắt đầu và kết thúc cho tất cả khung giờ')
      return false
    }
    if (slot.startTime >= slot.endTime) {
      toast.error('Giờ kết thúc phải sau giờ bắt đầu')
      return false
    }
    if (!slot.price || parseFloat(slot.price) <= 0) {
      toast.error('Vui lòng nhập giá thuê hợp lệ cho tất cả khung giờ')
      return false
    }
  }

  // Validate time slots coverage
  if (!courtForm.value.opening_time || !courtForm.value.closing_time) {
    toast.error('Vui lòng nhập giờ mở cửa và đóng cửa')
    return false
  }

  if (courtForm.value.opening_time >= courtForm.value.closing_time) {
    toast.error('Giờ đóng cửa phải sau giờ mở cửa')
    return false
  }

  // Check if time slots cover the entire opening hours
  const openingTime = courtForm.value.opening_time
  const closingTime = courtForm.value.closing_time
  const sortedSlots = [...timeSlots.value].sort((a, b) => a.startTime.localeCompare(b.startTime))

  // Check if first slot starts at opening time
  if (sortedSlots[0].startTime !== openingTime) {
    toast.error(
      `Khung giờ đầu tiên phải bắt đầu từ giờ mở cửa (${openingTime}). Hiện tại bắt đầu từ ${sortedSlots[0].startTime}`,
    )
    return false
  }

  // Check if last slot ends at closing time
  if (sortedSlots[sortedSlots.length - 1].endTime !== closingTime) {
    toast.error(
      `Khung giờ cuối cùng phải kết thúc vào giờ đóng cửa (${closingTime}). Hiện tại kết thúc lúc ${sortedSlots[sortedSlots.length - 1].endTime}`,
    )
    return false
  }

  // Check for gaps between time slots
  for (let i = 0; i < sortedSlots.length - 1; i++) {
    if (sortedSlots[i].endTime !== sortedSlots[i + 1].startTime) {
      toast.error(
        `Có khoảng trống giữa các khung giờ (${sortedSlots[i].endTime} - ${sortedSlots[i + 1].startTime}). Vui lòng điền đầy đủ tất cả khung giờ từ ${openingTime} đến ${closingTime}`,
      )
      return false
    }
  }

  if (!courtForm.value.contact_phone.trim()) {
    toast.error('Vui lòng nhập số điện thoại liên hệ')
    return false
  }

  if (!/^[0-9]{10}$/.test(courtForm.value.contact_phone.trim())) {
    toast.error('Số điện thoại phải gồm 10 chữ số')
    return false
  }

  if (images.value.length < 5) {
    toast.error(`Vui lòng tải lên ít nhất 5 hình ảnh (hiện tại: ${images.value.length}/5)`)
    return false
  }

  return true
}

const handleSubmit = async () => {
  if (!validateForm()) return

  isSaving.value = true

  try {
    // Prepare form data
    const formData = new FormData()

    // Prepare court data
    const courtData = {
      name: courtForm.value.name,
      address: courtForm.value.address,
      district: courtForm.value.district,
      city: courtForm.value.city,
      description: courtForm.value.description,
      court_quantity: courtForm.value.court_quantity,
      opening_time: courtForm.value.opening_time,
      closing_time: courtForm.value.closing_time,
      facilities: courtForm.value.facilities,
      contact_phone: courtForm.value.contact_phone,
      contact_email: courtForm.value.contact_email,
      time_slots: timeSlots.value.map((slot) => ({
        start_time: slot.startTime,
        end_time: slot.endTime,
        price: parseFloat(slot.price),
      })),
    }

    // Add court data as JSON string
    formData.append('court_data', JSON.stringify(courtData))

    // Add images
    images.value.forEach((image) => {
      formData.append('images', image)
    })

    // Call API to create court
    const response = await axiosInstance.post('/courts', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    // Save court info for editing
    currentCourtId.value = response.data.id
    isEditMode.value = true

    // Save to localStorage for persistence (user-specific)
    if (authStore.user) {
      const storageKey = `currentCourtId_${authStore.user.id}`
      localStorage.setItem(storageKey, String(response.data.id))
    }

    // Fetch individual courts
    await fetchIndividualCourts(response.data.id)

    // Show success notification
    toast.success(`✅ Đăng tải sân thành công! Đã tạo ${courtForm.value.court_quantity} sân con`, {
      timeout: 5000,
    })

    // Scroll to top to see the success message and edit form
    setTimeout(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }, 100)
  } catch (error) {
    console.error('Error creating court:', error)
    toast.error('Đăng tải sân thất bại. Vui lòng thử lại!')
  } finally {
    isSaving.value = false
  }
}

const loadCourtInfo = async (courtId: number) => {
  try {
    const response = await axiosInstance.get(`/courts/${courtId}`)
    const court = response.data

    // Restore form data
    courtForm.value = {
      name: court.name,
      address: court.address,
      district: court.district,
      city: court.city,
      description: court.description || '',
      court_quantity: court.court_quantity,
      opening_time: court.opening_time,
      closing_time: court.closing_time,
      facilities: court.facilities || [],
      contact_phone: court.contact_phone,
      contact_email: court.contact_email || '',
    }

    // Restore time slots
    if (court.time_slots && court.time_slots.length > 0) {
      timeSlots.value = court.time_slots.map(
        (slot: { start_time: string; end_time: string; price: number }, index: number) => ({
          id: String(index + 1),
          startTime: slot.start_time,
          endTime: slot.end_time,
          price: String(slot.price),
        }),
      )
      nextSlotId = timeSlots.value.length + 1
    }

    // Set edit mode
    currentCourtId.value = courtId
    isEditMode.value = true

    // Fetch individual courts
    await fetchIndividualCourts(courtId)
  } catch (error) {
    console.error('Error loading court info:', error)
    // Remove user-specific court ID from localStorage
    if (authStore.user) {
      const storageKey = `currentCourtId_${authStore.user.id}`
      localStorage.removeItem(storageKey)
    }
  }
}

const fetchIndividualCourts = async (courtId: number) => {
  try {
    const response = await axiosInstance.get(`/courts/${courtId}/individual-courts`)
    individualCourts.value = response.data
  } catch (error) {
    console.error('Error fetching individual courts:', error)
  }
}

const updateCourtInfo = async () => {
  if (!validateForm() || !currentCourtId.value) return

  isSaving.value = true

  try {
    const courtData = {
      name: courtForm.value.name,
      address: courtForm.value.address,
      district: courtForm.value.district,
      city: courtForm.value.city,
      description: courtForm.value.description,
      court_quantity: courtForm.value.court_quantity,
      opening_time: courtForm.value.opening_time,
      closing_time: courtForm.value.closing_time,
      facilities: courtForm.value.facilities,
      contact_phone: courtForm.value.contact_phone,
      contact_email: courtForm.value.contact_email,
      time_slots: timeSlots.value.map((slot) => ({
        start_time: slot.startTime,
        end_time: slot.endTime,
        price: parseFloat(slot.price),
      })),
    }

    await axiosInstance.put(`/courts/${currentCourtId.value}`, courtData)

    toast.success('✅ Cập nhật thông tin sân thành công!')
  } catch (error) {
    console.error('Error updating court:', error)
    toast.error('Cập nhật thông tin sân thất bại. Vui lòng thử lại!')
  } finally {
    isSaving.value = false
  }
}

const formatCurrency = (value: string | number) => {
  const numValue = typeof value === 'string' ? value.replace(/[^0-9]/g, '') : String(value)
  const num = parseFloat(numValue)
  if (isNaN(num)) return ''
  return new Intl.NumberFormat('vi-VN').format(num)
}

const formatTimeWithPeriod = (time: string) => {
  if (!time) return ''
  const [hours] = time.split(':')
  const hour = parseInt(hours)
  if (hour < 12) {
    return `${time} SA`
  } else {
    return `${time} CH`
  }
}
</script>

<template>
  <div class="court-upload-page">
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
            <rect x="4" y="10" width="16" height="8" rx="2" fill="#10b981" />
            <rect x="7" y="6" width="10" height="4" rx="2" fill="#fbbf24" />
            <rect x="9" y="2" width="6" height="4" rx="2" fill="#3b82f6" />
          </svg>
          Đăng tải sân
        </h1>
        <p class="page-subtitle">Điền đầy đủ thông tin để đăng tải sân của bạn</p>
      </div>
      <button class="preview-btn" type="button">
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
        Xem trước
      </button>
    </div>

    <form @submit.prevent="handleSubmit" class="court-form">
      <!-- Basic Information -->
      <div class="form-section">
        <div class="section-header">
          <h2 class="section-title">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              style="
                width: 24px;
                height: 24px;
                display: inline-block;
                vertical-align: middle;
                margin-right: 8px;
              "
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            Thông tin cơ bản
          </h2>
        </div>

        <div class="form-grid">
          <div class="form-group full-width">
            <label class="form-label required">Tên sân</label>
            <input
              v-model="courtForm.name"
              type="text"
              class="form-input"
              placeholder="VD: Sân Pickleball VIP A1"
            />
          </div>

          <div class="form-group full-width">
            <label class="form-label required">Địa chỉ</label>
            <input
              v-model="courtForm.address"
              type="text"
              class="form-input"
              placeholder="VD: 123 Nguyễn Văn A"
            />
          </div>

          <div class="form-group">
            <label class="form-label required">Quận/Huyện</label>
            <input
              v-model="courtForm.district"
              type="text"
              class="form-input"
              placeholder="VD: Quận 1"
            />
          </div>

          <div class="form-group">
            <label class="form-label required">Thành phố</label>
            <input
              v-model="courtForm.city"
              type="text"
              class="form-input"
              placeholder="VD: TP. Hồ Chí Minh"
            />
          </div>

          <div class="form-group">
            <label class="form-label required">Số lượng sân</label>
            <input
              v-model.number="courtForm.court_quantity"
              type="number"
              class="form-input"
              placeholder="VD: 5"
              min="1"
              step="1"
            />
          </div>

          <div class="form-group full-width">
            <label class="form-label">Mô tả</label>
            <textarea
              v-model="courtForm.description"
              class="form-textarea"
              rows="4"
              placeholder="Mô tả chi tiết về sân của bạn..."
            ></textarea>
          </div>
        </div>
      </div>

      <!-- Pricing & Hours -->
      <div class="form-section">
        <div class="section-header">
          <h2 class="section-title">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              style="
                width: 24px;
                height: 24px;
                display: inline-block;
                vertical-align: middle;
                margin-right: 8px;
              "
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Giá thuê theo khung giờ
          </h2>
          <span class="section-subtitle">Thêm các khung giờ và giá thuê tương ứng</span>
        </div>

        <div v-if="timeSlots.length === 0" class="empty-slots">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            class="empty-icon"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          <p class="empty-text">Chưa có khung giờ nào. Nhấn nút bên dưới để thêm.</p>
        </div>

        <div v-else class="time-slots-list">
          <div
            v-for="slot in timeSlots"
            :key="slot.id"
            class="time-slot-item"
            :class="{
              filled: slot.startTime && slot.endTime && slot.price && parseFloat(slot.price) > 0,
            }"
          >
            <div class="slot-inputs">
              <div class="slot-input-group">
                <label class="slot-label">Từ giờ (VD: 06:00 SA, 22:00 CH)</label>
                <input
                  v-model="slot.startTime"
                  type="time"
                  class="slot-time-input"
                  placeholder="Bắt đầu"
                  pattern="[0-9]{2}:[0-9]{2}"
                  step="3600"
                  lang="vi-VN"
                />
              </div>

              <span class="slot-separator">→</span>

              <div class="slot-input-group">
                <label class="slot-label">Đến giờ (VD: 18:00 CH)</label>
                <input
                  v-model="slot.endTime"
                  type="time"
                  class="slot-time-input"
                  placeholder="Kết thúc"
                  pattern="[0-9]{2}:[0-9]{2}"
                  step="3600"
                  lang="vi-VN"
                />
              </div>

              <div class="slot-input-group slot-price-group">
                <label class="slot-label">Giá thuê</label>
                <div class="slot-price-input-wrapper">
                  <input
                    v-model="slot.price"
                    type="number"
                    class="slot-price-input"
                    placeholder="VD: 150000"
                    min="0"
                    step="1000"
                  />
                  <span class="price-unit">VNĐ/giờ</span>
                </div>
              </div>
            </div>

            <button
              type="button"
              class="remove-slot-btn"
              @click="removeTimeSlot(slot.id)"
              title="Xóa khung giờ"
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
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>

            <div
              v-if="slot.startTime && slot.endTime && slot.price && parseFloat(slot.price) > 0"
              class="slot-preview"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                style="
                  width: 18px;
                  height: 18px;
                  display: inline-block;
                  vertical-align: middle;
                  margin-right: 6px;
                "
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              {{ formatTimeWithPeriod(slot.startTime) }} -
              {{ formatTimeWithPeriod(slot.endTime) }} • {{ formatCurrency(slot.price) }} đồng/giờ
            </div>
          </div>
        </div>

        <button type="button" class="add-slot-btn" @click="addTimeSlot">
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
              d="M12 6v6m0 0v6m0-6h6m-6 0H6"
            />
          </svg>
          <span>Thêm khung giờ</span>
        </button>

        <div class="form-grid" style="margin-top: 24px">
          <div class="form-group">
            <label class="form-label">Giờ mở cửa</label>
            <input
              v-model="courtForm.opening_time"
              type="time"
              class="form-input"
              pattern="[0-9]{2}:[0-9]{2}"
              step="3600"
              lang="vi-VN"
              title="VD: 06:00 (6h sáng)"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Giờ đóng cửa</label>
            <input
              v-model="courtForm.closing_time"
              type="time"
              class="form-input"
              pattern="[0-9]{2}:[0-9]{2}"
              step="3600"
              lang="vi-VN"
              title="VD: 22:00 (10h tối)"
            />
          </div>
        </div>

        <div
          v-if="courtForm.opening_time && courtForm.closing_time"
          class="operating-hours-preview"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            style="
              width: 18px;
              height: 18px;
              display: inline-block;
              vertical-align: middle;
              margin-right: 6px;
            "
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          {{ formatTimeWithPeriod(courtForm.opening_time) }} -
          {{ formatTimeWithPeriod(courtForm.closing_time) }}
        </div>
      </div>

      <!-- Facilities -->
      <div class="form-section">
        <div class="section-header">
          <h2 class="section-title">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              style="
                width: 24px;
                height: 24px;
                display: inline-block;
                vertical-align: middle;
                margin-right: 8px;
              "
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
            Tiện ích
          </h2>
          <span class="section-subtitle">Chọn các tiện ích có sẵn tại sân</span>
        </div>

        <div class="facilities-grid">
          <button
            v-for="facility in availableFacilities"
            :key="facility.id"
            type="button"
            class="facility-btn"
            :class="{ active: courtForm.facilities.includes(facility.id) }"
            @click="toggleFacility(facility.id)"
          >
            <span class="facility-icon">{{ facility.icon }}</span>
            <span class="facility-label">{{ facility.label }}</span>
            <svg
              v-if="courtForm.facilities.includes(facility.id)"
              class="facility-check"
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
        </div>
      </div>

      <!-- Images -->
      <div class="form-section">
        <div class="section-header">
          <h2 class="section-title">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              style="
                width: 24px;
                height: 24px;
                display: inline-block;
                vertical-align: middle;
                margin-right: 8px;
              "
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            Hình ảnh
          </h2>
          <span class="section-subtitle">Yêu cầu 5 ảnh chụp của sân muốn đăng tải</span>
        </div>

        <div class="images-section">
          <div class="image-upload-area">
            <input
              type="file"
              id="image-upload"
              multiple
              accept="image/*"
              @change="handleImageUpload"
              style="display: none"
            />
            <label for="image-upload" class="upload-label">
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
                  d="M12 4v16m8-8H4"
                />
              </svg>
              <span>Thêm hình ảnh</span>
            </label>
          </div>

          <div v-if="imagePreviews.length > 0" class="images-preview">
            <div v-for="(preview, index) in imagePreviews" :key="index" class="preview-item">
              <img :src="preview" :alt="'Preview ' + (index + 1)" />
              <button type="button" class="remove-btn" @click="removeImage(index)">
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
              <span v-if="index === 0" class="primary-badge">Ảnh chính</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Contact Information -->
      <div class="form-section">
        <div class="section-header">
          <h2 class="section-title">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              style="
                width: 24px;
                height: 24px;
                display: inline-block;
                vertical-align: middle;
                margin-right: 8px;
              "
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
              />
            </svg>
            Thông tin liên hệ
          </h2>
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label class="form-label required">Số điện thoại</label>
            <input
              v-model="courtForm.contact_phone"
              type="tel"
              class="form-input"
              placeholder="VD: 0901234567"
              maxlength="10"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Email</label>
            <input
              v-model="courtForm.contact_email"
              type="email"
              class="form-input"
              placeholder="VD: contact@example.com"
            />
          </div>
        </div>
      </div>

      <!-- Individual Courts List (if created) -->
      <div v-if="isEditMode && individualCourts.length > 0" class="form-section">
        <div class="section-header">
          <h2 class="section-title">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              style="
                width: 24px;
                height: 24px;
                display: inline-block;
                vertical-align: middle;
                margin-right: 8px;
              "
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
              />
            </svg>
            Danh sách sân đã tạo
          </h2>
        </div>

        <div class="courts-grid">
          <div
            v-for="court in individualCourts"
            :key="court.id"
            class="court-card"
            :class="{ available: court.is_available }"
          >
            <div class="court-header">
              <h3 class="court-name">{{ court.name }}</h3>
              <span class="court-status available">
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
                Đang trống
              </span>
            </div>
          </div>
        </div>

        <div class="action-banner">
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
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p>Bạn có thể chỉnh sửa thông tin sân bên trên và nhấn "Cập nhật" để lưu thay đổi</p>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <button v-if="!isEditMode" type="submit" class="btn-submit" :disabled="isSaving">
          <svg
            v-if="!isSaving"
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
          <svg
            v-else
            class="animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            ></circle>
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          {{ isSaving ? 'Đang đăng tải...' : 'Đăng tải sân' }}
        </button>
        <button
          v-else
          type="button"
          class="btn-submit"
          :disabled="isSaving"
          @click="updateCourtInfo"
        >
          <svg
            v-if="!isSaving"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
            />
          </svg>
          <svg
            v-else
            class="animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            ></circle>
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          {{ isSaving ? 'Đang cập nhật...' : 'Cập nhật thông tin' }}
        </button>
        <button
          v-if="isEditMode"
          type="button"
          class="btn-view-list"
          @click="router.push('/owner/management/court-list')"
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
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
          Xem danh sách sân
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.court-upload-page {
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
}

.page-subtitle {
  color: #6b7280;
  font-size: 0.95rem;
  margin: 0;
}

.preview-btn {
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

.preview-btn:hover {
  border-color: #2d5016;
  color: #2d5016;
  background: #f0fdf4;
}

.preview-btn svg {
  width: 18px;
  height: 18px;
}

/* Form */
.court-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section {
  background: white;
  padding: 28px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.section-header {
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.section-subtitle {
  color: #6b7280;
  font-size: 0.85rem;
  margin: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.time-display {
  font-size: 0.875rem;
  color: #2d5016;
  font-weight: 600;
  margin-top: 4px;
  padding: 6px 12px;
  background: #f0fdf4;
  border-radius: 6px;
  display: inline-block;
  width: fit-content;
}

.form-label {
  font-weight: 600;
  font-size: 0.9rem;
  color: #374151;
}

.form-label.required::after {
  content: ' *';
  color: #ef4444;
}

.form-input,
.form-textarea {
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  font-family: inherit;
}

.form-input::-webkit-calendar-picker-indicator {
  filter: invert(0.5);
  cursor: pointer;
}

.form-input::-webkit-datetime-edit-ampm-field {
  display: none !important;
  visibility: hidden !important;
  width: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

input[type='time'].form-input {
  -webkit-appearance: none;
  appearance: none;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #2d5016;
  box-shadow: 0 0 0 3px rgba(45, 80, 22, 0.1);
}

.form-textarea {
  resize: vertical;
}

.form-hint {
  font-size: 0.85rem;
  color: #2d5016;
  font-weight: 600;
}

/* Time Slots */
.empty-slots {
  padding: 48px 24px;
  background: #f9fafb;
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
}

.empty-icon {
  width: 64px;
  height: 64px;
  color: #6b7280;
}

.empty-text {
  font-size: 0.95rem;
  color: #6b7280;
  margin: 0;
}

.time-slots-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 16px;
}

.operating-hours-preview {
  margin-top: 12px;
  padding: 12px 16px;
  background: #f0fdf4;
  border: 1px solid #86efac;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #2d5016;
  font-weight: 600;
  text-align: center;
}

.time-slot-item {
  padding: 20px;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: all 0.3s ease;
  position: relative;
}

.time-slot-item:hover {
  background: #f0fdf4;
  border-color: #86efac;
}

.time-slot-item.filled {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border-color: #2d5016;
}

.slot-inputs {
  display: grid;
  grid-template-columns: 1fr auto 1fr 1.5fr;
  gap: 16px;
  align-items: end;
}

.slot-input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.slot-label {
  font-weight: 600;
  font-size: 0.85rem;
  color: #374151;
}

.slot-time-input {
  padding: 10px 14px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.slot-time-input::-webkit-calendar-picker-indicator {
  filter: invert(0.5);
  cursor: pointer;
}

.slot-time-input::-webkit-datetime-edit-ampm-field {
  display: none !important;
  visibility: hidden !important;
  width: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

input[type='time']::-webkit-datetime-edit-ampm-field {
  display: none !important;
  visibility: hidden !important;
  width: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

input[type='time'] {
  -webkit-appearance: none;
  -moz-appearance: textfield;
  appearance: none;
}

input[type='time']::-webkit-inner-spin-button,
input[type='time']::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.slot-time-input:focus {
  outline: none;
  border-color: #2d5016;
  box-shadow: 0 0 0 3px rgba(45, 80, 22, 0.1);
}

.slot-separator {
  font-size: 1.2rem;
  color: #6b7280;
  padding-bottom: 10px;
}

.slot-price-group {
  flex: 1.5;
}

.slot-price-input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding-right: 12px;
  transition: all 0.3s ease;
}

.slot-price-input-wrapper:focus-within {
  border-color: #2d5016;
  box-shadow: 0 0 0 3px rgba(45, 80, 22, 0.1);
}

.slot-price-input {
  flex: 1;
  padding: 10px 14px;
  border: none;
  font-size: 0.95rem;
  outline: none;
}

.price-unit {
  font-size: 0.85rem;
  color: #6b7280;
  font-weight: 600;
  white-space: nowrap;
}

.remove-slot-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  padding: 0;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.remove-slot-btn:hover {
  background: #fee2e2;
  border-color: #ef4444;
}

.remove-slot-btn svg {
  width: 18px;
  height: 18px;
  color: #6b7280;
}

.remove-slot-btn:hover svg {
  color: #ef4444;
}

.slot-preview {
  font-size: 0.9rem;
  color: #2d5016;
  font-weight: 600;
  padding: 10px 14px;
  background: #dcfce7;
  border-radius: 8px;
  text-align: center;
}

.add-slot-btn {
  width: 100%;
  padding: 14px 24px;
  background: white;
  border: 2px dashed #d1d5db;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.95rem;
  color: #374151;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.add-slot-btn:hover {
  background: #f0fdf4;
  border-color: #2d5016;
  color: #2d5016;
}

.add-slot-btn svg {
  width: 20px;
  height: 20px;
}

/* Facilities */
.facilities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  justify-items: stretch;
}

.facility-btn {
  padding: 16px;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.facility-btn:hover {
  background: #f0fdf4;
  border-color: #86efac;
}

.facility-btn.active {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border-color: #2d5016;
}

.facility-icon {
  font-size: 2rem;
}

.facility-label {
  font-weight: 600;
  font-size: 0.85rem;
  color: #374151;
  text-align: center;
}

.facility-check {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 20px;
  height: 20px;
  background: #2d5016;
  color: white;
  border-radius: 50%;
  padding: 3px;
}

/* Images */
.images-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.image-upload-area {
  display: flex;
  justify-content: center;
}

.upload-label {
  padding: 32px 48px;
  background: #f9fafb;
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-label:hover {
  background: #f0fdf4;
  border-color: #2d5016;
}

.upload-label svg {
  width: 48px;
  height: 48px;
  color: #6b7280;
}

.upload-label span {
  font-weight: 600;
  font-size: 0.95rem;
  color: #374151;
}

.images-preview {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
}

.preview-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid #e5e7eb;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  background: rgba(0, 0, 0, 0.6);
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.remove-btn:hover {
  background: #ef4444;
}

.remove-btn svg {
  width: 16px;
  height: 16px;
  color: white;
}

.primary-badge {
  position: absolute;
  bottom: 8px;
  left: 8px;
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 700;
}

/* Individual Courts Grid */
.courts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.court-card {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.court-card.available {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border-color: #86efac;
}

.court-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.court-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.court-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.court-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
}

.court-status.available {
  background: #10b981;
  color: white;
}

.court-status svg {
  width: 16px;
  height: 16px;
}

.action-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: #eff6ff;
  border: 1px solid #93c5fd;
  border-radius: 10px;
  margin-top: 16px;
}

.action-banner svg {
  width: 24px;
  height: 24px;
  color: #3b82f6;
  flex-shrink: 0;
}

.action-banner p {
  margin: 0;
  color: #1e40af;
  font-size: 0.9rem;
  font-weight: 500;
}

/* Form Actions */
.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 20px;
  flex-wrap: wrap;
}

.btn-reset,
.btn-submit,
.btn-view-list {
  padding: 14px 32px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  border: none;
  transition: all 0.3s ease;
}

.btn-reset {
  background: #f3f4f6;
  color: #6b7280;
  border: 2px solid #e5e7eb;
}

.btn-reset:hover:not(:disabled) {
  background: #e5e7eb;
  border-color: #d1d5db;
}

.btn-submit {
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  color: white;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(45, 80, 22, 0.3);
}

.btn-view-list {
  background: #3b82f6;
  color: white;
}

.btn-view-list:hover {
  background: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
}

.btn-reset:disabled,
.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-reset svg,
.btn-submit svg,
.btn-view-list svg {
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

/* Responsive */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .slot-inputs {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .slot-separator {
    display: none;
  }

  .remove-slot-btn {
    top: 8px;
    right: 8px;
    width: 28px;
    height: 28px;
  }

  .facilities-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }

  .form-actions {
    flex-direction: column-reverse;
  }

  .btn-reset,
  .btn-submit,
  .btn-view-list {
    width: 100%;
    justify-content: center;
  }

  .courts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
