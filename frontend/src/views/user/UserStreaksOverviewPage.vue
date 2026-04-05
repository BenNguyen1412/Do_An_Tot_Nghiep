<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import axiosInstance from '@/utils/axios'
import { useToast } from 'vue-toastification'

interface FriendUser {
  id: number
  full_name: string
  email: string
}

interface FriendStreakItem {
  user: FriendUser
  since: string
  current_streak: number
  best_streak: number
}

const toast = useToast()
const isLoading = ref(false)
const friends = ref<FriendStreakItem[]>([])

const loadFriendStreaks = async () => {
  isLoading.value = true
  try {
    const response = await axiosInstance.get('/friends/me')
    friends.value = response.data.friends || []
  } catch {
    toast.error('Unable to load streak list')
  } finally {
    isLoading.value = false
  }
}

const formatDate = (value: string) => {
  return new Date(value).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  })
}

const handleFriendsUpdated = () => {
  loadFriendStreaks()
}

onMounted(() => {
  loadFriendStreaks()
  window.addEventListener('friends-updated', handleFriendsUpdated)
})

onUnmounted(() => {
  window.removeEventListener('friends-updated', handleFriendsUpdated)
})
</script>

<template>
  <section class="overview-page">
    <div class="panel-head">
      <h2>Friends Streaks</h2>
      <p>All your friends and their current streak progress.</p>
    </div>

    <div v-if="isLoading" class="state">Loading streak list...</div>
    <div v-else-if="friends.length === 0" class="state">No friends yet.</div>

    <div v-else class="table-shell">
      <table class="friends-streak-table">
        <thead>
          <tr>
            <th>Friend</th>
            <th>Email</th>
            <th>Friends Since</th>
            <th>Current Streak</th>
            <th>Best Streak</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="friend in friends" :key="friend.user.id">
            <td class="name-cell">{{ friend.user.full_name }}</td>
            <td class="email-cell">{{ friend.user.email }}</td>
            <td>{{ formatDate(friend.since) }}</td>
            <td>
              <span class="streak-chip current">
                {{ friend.current_streak }} day{{ friend.current_streak === 1 ? '' : 's' }}
              </span>
            </td>
            <td>
              <span class="streak-chip best">
                {{ friend.best_streak }} day{{ friend.best_streak === 1 ? '' : 's' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.overview-page {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
  display: grid;
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
}

.state {
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
  padding: 20px;
  color: #64748b;
  background: #f8fafc;
}

.table-shell {
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  overflow: auto;
}

.friends-streak-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 760px;
  background: white;
}

.friends-streak-table thead th {
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

.friends-streak-table tbody td {
  padding: 14px;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
  font-size: 0.92rem;
}

.friends-streak-table tbody tr:hover {
  background: #f8fafc;
}

.name-cell {
  font-weight: 700;
  color: #0f172a;
}

.email-cell {
  color: #475569;
}

.streak-chip {
  display: inline-block;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 0.8rem;
  font-weight: 700;
}

.streak-chip.current {
  background: #dcfce7;
  color: #166534;
}

.streak-chip.best {
  background: #ecfccb;
  color: #3f6212;
}

@media (max-width: 1024px) {
  .overview-page {
    padding: 16px;
  }
}
</style>
