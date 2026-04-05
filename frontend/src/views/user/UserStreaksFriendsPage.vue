<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { isAxiosError } from 'axios'
import axiosInstance from '@/utils/axios'
import { useToast } from 'vue-toastification'

interface FriendUser {
  id: number
  full_name: string
  email: string
}

interface FriendItem {
  user: FriendUser
  since: string
}

const toast = useToast()
const isLoading = ref(false)
const isSending = ref(false)
const showAddModal = ref(false)
const friendEmail = ref('')
const friends = ref<FriendItem[]>([])

const loadFriends = async () => {
  isLoading.value = true
  try {
    const response = await axiosInstance.get('/friends/me')
    friends.value = response.data.friends || []
  } catch {
    toast.error('Unable to load friends list')
  } finally {
    isLoading.value = false
  }
}

const openAddModal = () => {
  friendEmail.value = ''
  showAddModal.value = true
}

const closeAddModal = () => {
  showAddModal.value = false
}

const submitAddFriend = async () => {
  if (!friendEmail.value.trim()) {
    toast.error('Please enter an email')
    return
  }

  isSending.value = true
  try {
    await axiosInstance.post('/friends/requests', {
      email: friendEmail.value.trim(),
    })
    toast.success('Friend request sent successfully')
    closeAddModal()
  } catch (error: unknown) {
    const message = isAxiosError(error)
      ? error.response?.data?.detail || 'User email not found'
      : 'User email not found'
    toast.error(message)
  } finally {
    isSending.value = false
  }
}

const formatDate = (value: string) => {
  return new Date(value).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  })
}

const getInitials = (fullName: string) => {
  const parts = fullName.trim().split(' ')
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
}

const handleFriendsUpdated = () => {
  loadFriends()
}

onMounted(() => {
  loadFriends()
  window.addEventListener('friends-updated', handleFriendsUpdated)
})

onUnmounted(() => {
  window.removeEventListener('friends-updated', handleFriendsUpdated)
})
</script>

<template>
  <section class="panel">
    <div class="panel-head">
      <div>
        <h2>Friends</h2>
        <p>Manage your friend list and send friend requests by email.</p>
      </div>
      <button class="add-friend-btn" type="button" @click="openAddModal">Add Friend</button>
    </div>

    <div v-if="isLoading" class="state">Loading friends list...</div>
    <div v-else-if="friends.length === 0" class="state">No friends yet.</div>

    <div v-else class="table-shell">
      <table class="friends-table">
        <thead>
          <tr>
            <th>Friend</th>
            <th>Email</th>
            <th>Friends Since</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="friend in friends" :key="friend.user.id">
            <td>
              <div class="friend-cell">
                <div class="avatar">{{ getInitials(friend.user.full_name) }}</div>
                <span class="friend-name">{{ friend.user.full_name }}</span>
              </div>
            </td>
            <td class="email-cell">{{ friend.user.email }}</td>
            <td>{{ formatDate(friend.since) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showAddModal" class="modal-overlay" @click.self="closeAddModal">
          <div class="modal-card">
            <h3>Add Friend</h3>
            <p>Enter the email of a user who already has an account.</p>
            <input v-model="friendEmail" type="email" placeholder="example@email.com" />
            <div class="modal-actions">
              <button type="button" class="btn cancel" @click="closeAddModal">Cancel</button>
              <button
                type="button"
                class="btn submit"
                :disabled="isSending"
                @click="submitAddFriend"
              >
                {{ isSending ? 'Sending...' : 'Send Request' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </section>
</template>

<style scoped>
.panel {
  background: white;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.panel-head h2 {
  margin: 0;
  font-size: 1.4rem;
  color: #111827;
}

.panel-head p {
  margin: 8px 0 0;
  color: #64748b;
  font-size: 0.95rem;
}

.add-friend-btn {
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: white;
  font-weight: 700;
  padding: 10px 16px;
  cursor: pointer;
}

.state {
  margin-top: 20px;
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
  padding: 16px;
  color: #64748b;
}

.table-shell {
  margin-top: 20px;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  overflow: auto;
}

.friends-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 680px;
  background: white;
}

.friends-table thead th {
  position: sticky;
  top: 0;
  z-index: 1;
  text-align: left;
  font-size: 0.8rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  font-weight: 700;
  color: #334155;
  background: #f1f5f9;
  border-bottom: 1px solid #cbd5e1;
  padding: 12px 14px;
}

.friends-table tbody td {
  padding: 14px;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
  font-size: 0.92rem;
}

.friends-table tbody tr:hover {
  background: #f8fafc;
}

.avatar {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: white;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.friend-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.friend-name {
  font-weight: 700;
  color: #0f172a;
}

.email-cell {
  color: #475569;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 20px;
}

.modal-card {
  width: 100%;
  max-width: 440px;
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
}

.modal-card h3 {
  margin: 0;
  color: #111827;
}

.modal-card p {
  margin: 8px 0 14px;
  color: #64748b;
}

.modal-card input {
  width: 100%;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  padding: 12px;
  font-size: 14px;
  outline: none;
}

.modal-card input:focus {
  border-color: #22c55e;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.15);
}

.modal-actions {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.btn {
  border: none;
  border-radius: 10px;
  padding: 10px 14px;
  font-weight: 700;
  cursor: pointer;
}

.btn.cancel {
  background: #e5e7eb;
  color: #334155;
}

.btn.submit {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: white;
}

.modal-enter-active,
.modal-leave-active {
  transition: all 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

@media (max-width: 1024px) {
  .panel-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
