<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axiosInstance from '@/utils/axios'
import { useToast } from 'vue-toastification'

defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'update'): void
}>()

const authStore = useAuthStore()
const toast = useToast()

const isEditing = ref(false)
const isSaving = ref(false)
const editForm = ref({
  full_name: '',
  phone_number: '',
})

const startEdit = () => {
  editForm.value = {
    full_name: authStore.user?.full_name || '',
    phone_number: authStore.user?.phone_number || '',
  }
  isEditing.value = true
}

const cancelEdit = () => {
  isEditing.value = false
}

const saveChanges = async () => {
  // Validation
  if (!editForm.value.full_name.trim()) {
    toast.error('Họ và tên không được để trống')
    return
  }

  if (editForm.value.phone_number && !/^[0-9]{10}$/.test(editForm.value.phone_number.trim())) {
    toast.error('Số điện thoại phải gồm 10 chữ số')
    return
  }

  isSaving.value = true

  try {
    // Call API to update user profile
    const response = await axiosInstance.put(`/users/${authStore.user?.id}`, {
      full_name: editForm.value.full_name.trim(),
      phone_number: editForm.value.phone_number.trim() || null,
    })

    // Update auth store with new data
    if (authStore.user) {
      authStore.user.full_name = response.data.full_name
      authStore.user.phone_number = response.data.phone_number
      // Update localStorage
      localStorage.setItem('user', JSON.stringify(authStore.user))
    }

    toast.success('✅ Cập nhật thông tin thành công!')
    isEditing.value = false
    emit('update')
  } catch (error: unknown) {
    console.error('Error updating profile:', error)
    const errorMessage =
      (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
      'Cập nhật thông tin thất bại'
    toast.error(errorMessage)
  } finally {
    isSaving.value = false
  }
}

const closeModal = () => {
  isEditing.value = false
  emit('close')
}

const getRoleName = (role: string | undefined) => {
  const roleMap: Record<string, string> = {
    user: 'Người dùng',
    enterprise: 'Doanh nghiệp',
    owner: 'Chủ sân',
    admin: 'Quản trị viên',
  }
  return roleMap[role || 'user'] || role
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
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
              </div>
              <h2 class="modal-title">Thông tin cá nhân</h2>
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

          <!-- Body -->
          <div class="modal-body">
            <!-- Avatar Section -->
            <div class="avatar-section">
              <div class="avatar-large">
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
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
              </div>
              <div class="role-badge">{{ getRoleName(authStore.user?.role) }}</div>
            </div>

            <!-- Info Form -->
            <div class="info-section">
              <div class="info-grid">
                <!-- Full Name -->
                <div class="info-item">
                  <label class="info-label">
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
                        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                      />
                    </svg>
                    Họ và tên
                  </label>
                  <input
                    v-if="isEditing"
                    v-model="editForm.full_name"
                    type="text"
                    class="info-input"
                  />
                  <div v-else class="info-value">{{ authStore.user?.full_name || 'N/A' }}</div>
                </div>

                <!-- Email -->
                <div class="info-item">
                  <label class="info-label">
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
                        d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                      />
                    </svg>
                    Email
                  </label>
                  <div class="info-value">{{ authStore.user?.email || 'N/A' }}</div>
                  <span class="info-note">Email không thể thay đổi</span>
                </div>

                <!-- Phone -->
                <div class="info-item">
                  <label class="info-label">
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
                    v-if="isEditing"
                    v-model="editForm.phone_number"
                    type="tel"
                    class="info-input"
                    placeholder="Nhập số điện thoại"
                  />
                  <div v-else class="info-value">
                    {{ authStore.user?.phone_number || 'Chưa cập nhật' }}
                  </div>
                </div>

                <!-- Account Status -->
                <div class="info-item">
                  <label class="info-label">
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
                    Trạng thái tài khoản
                  </label>
                  <div class="info-value">
                    {{ authStore.user?.is_active ? 'Đang hoạt động' : 'Không hoạt động' }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Stats Section -->
            <div class="stats-section">
              <div class="stat-card">
                <div class="stat-icon">🏟️</div>
                <div class="stat-content">
                  <div class="stat-number">0</div>
                  <div class="stat-label">Lượt đặt sân</div>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon">⭐</div>
                <div class="stat-content">
                  <div class="stat-number">0</div>
                  <div class="stat-label">Điểm tích lũy</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="modal-footer">
            <button v-if="!isEditing" class="btn-edit" @click="startEdit">
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
              Chỉnh sửa
            </button>
            <template v-else>
              <button class="btn-cancel" @click="cancelEdit" :disabled="isSaving">Hủy</button>
              <button class="btn-save" @click="saveChanges" :disabled="isSaving">
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
                {{ isSaving ? 'Đang lưu...' : 'Lưu thay đổi' }}
              </button>
            </template>
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
  max-width: 600px;
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

/* Body */
.modal-body {
  padding: 28px;
  overflow-y: auto;
  flex: 1;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-bottom: 28px;
}

.avatar-large {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(45, 80, 22, 0.3);
}

.avatar-large svg {
  width: 50px;
  height: 50px;
  color: white;
}

.role-badge {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: white;
  padding: 6px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.85rem;
  box-shadow: 0 4px 12px rgba(251, 191, 36, 0.3);
}

/* Info Section */
.info-section {
  margin-bottom: 24px;
}

.info-grid {
  display: grid;
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-label svg {
  width: 18px;
  height: 18px;
}

.info-value {
  color: #1f2937;
  font-size: 1.05rem;
  font-weight: 600;
  padding: 12px 16px;
  background: #f9fafb;
  border-radius: 10px;
  border: 2px solid #e5e7eb;
}

.info-input {
  padding: 12px 16px;
  border: 2px solid #2d5016;
  border-radius: 10px;
  font-size: 1.05rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.info-input:focus {
  outline: none;
  border-color: #4a7c2c;
  box-shadow: 0 0 0 3px rgba(45, 80, 22, 0.1);
}

.info-note {
  color: #9ca3af;
  font-size: 0.8rem;
  font-style: italic;
}

/* Stats Section */
.stats-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-card {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border: 2px solid #86efac;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-icon {
  font-size: 2rem;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 1.75rem;
  font-weight: 800;
  color: #2d5016;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.85rem;
  color: #4a7c2c;
  font-weight: 600;
}

/* Footer */
.modal-footer {
  padding: 20px 28px;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-edit,
.btn-save,
.btn-cancel {
  padding: 12px 24px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  border: none;
}

.btn-edit {
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  color: white;
  flex: 1;
}

.btn-edit:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(45, 80, 22, 0.3);
}

.btn-edit svg {
  width: 18px;
  height: 18px;
}

.btn-cancel {
  background: #f3f4f6;
  color: #6b7280;
  border: 2px solid #e5e7eb;
}

.btn-cancel:hover {
  background: #e5e7eb;
  border-color: #d1d5db;
}

.btn-save {
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  color: white;
}

.btn-save:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(45, 80, 22, 0.3);
}

.btn-save svg {
  width: 18px;
  height: 18px;
}

.btn-save:disabled,
.btn-cancel:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-save:disabled:hover,
.btn-cancel:disabled:hover {
  transform: none;
  box-shadow: none;
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
}

.btn-cancel:disabled:hover {
  background: #f3f4f6;
}

/* Spinner Animation */
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
@media (max-width: 640px) {
  .modal-container {
    max-width: 100%;
    border-radius: 20px 20px 0 0;
    margin-top: auto;
  }

  .modal-header {
    padding: 20px;
  }

  .modal-title {
    font-size: 1.25rem;
  }

  .modal-body {
    padding: 20px;
  }

  .stats-section {
    grid-template-columns: 1fr;
  }

  .btn-edit {
    flex: unset;
  }
}
</style>
