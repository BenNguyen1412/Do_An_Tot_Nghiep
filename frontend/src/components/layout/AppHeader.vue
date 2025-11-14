<script setup lang="ts">
import { ref } from 'vue'

const currentTime = ref('')
const currentDate = ref('')

const updateDateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
  currentDate.value = now.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
  })
}

updateDateTime()
setInterval(updateDateTime, 60000)
</script>

<template>
  <header class="app-header">
    <div class="header-container">
      <!-- Logo -->
      <div class="logo-section">
        <div class="logo-icon">🏓</div>
        <div class="logo-text">
          <span class="pickleball">Pickleball</span>
          <span class="brand">NP SPORTCLUB</span>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="main-nav">
        <router-link to="/" class="nav-link active">HOME</router-link>
        <router-link to="/court" class="nav-link">COURT</router-link>
      </nav>

      <!-- Time & Date -->
      <div class="datetime-section">
        <div class="time">
          <span class="icon">🕐</span>
          {{ currentTime }}
        </div>
        <div class="date">
          <span class="icon">📅</span>
          {{ currentDate }}
        </div>
      </div>

      <!-- Sign In Button -->
      <button class="sign-in-btn">
        <span class="icon">👤</span>
        Sign in
      </button>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  padding: 20px 40px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 40px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 2rem;
}

.logo-text {
  display: flex;
  flex-direction: column;
  color: white;
  line-height: 1.2;
}

.pickleball {
  font-size: 0.9rem;
  font-weight: 400;
}

.brand {
  font-size: 1.3rem;
  font-weight: 700;
  letter-spacing: 2px;
}

.main-nav {
  display: flex;
  gap: 40px;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-size: 1.1rem;
  font-weight: 600;
  letter-spacing: 1px;
  padding: 8px 0;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
}

.nav-link:hover,
.nav-link.active {
  border-bottom-color: white;
}

.datetime-section {
  display: flex;
  gap: 20px;
  color: white;
  font-size: 0.95rem;
}

.time,
.date {
  display: flex;
  align-items: center;
  gap: 6px;
}

.icon {
  font-size: 1.1rem;
}

.sign-in-btn {
  background: white;
  color: #2d5016;
  border: none;
  padding: 12px 32px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.sign-in-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

@media (max-width: 1024px) {
  .datetime-section {
    display: none;
  }
}

@media (max-width: 768px) {
  .header-container {
    flex-wrap: wrap;
    gap: 20px;
  }

  .main-nav {
    gap: 20px;
  }
}
</style>
