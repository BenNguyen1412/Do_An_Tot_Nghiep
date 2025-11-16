<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const currentTime = ref('')
const currentDate = ref('')
const isScrolled = ref(false)

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

const handleScroll = () => {
  isScrolled.value = window.scrollY > 50
}

onMounted(() => {
  updateDateTime()
  setInterval(updateDateTime, 60000)
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <header class="app-header" :class="{ scrolled: isScrolled }">
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
        <router-link to="/about" class="nav-link">ABOUT US</router-link>
      </nav>

      <!-- Time & Date -->
      <div class="datetime-section">
        <div class="time">
          <span class="icon">🕐</span>
          <span>{{ currentTime }}</span>
        </div>
        <div class="date">
          <span class="icon">📅</span>
          <span>{{ currentDate }}</span>
        </div>
      </div>

      <!-- Sign In Button -->
      <router-link to="/login" class="sign-in-btn">
        <span class="icon">👤</span>
        <span>Sign in</span>
      </router-link>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  padding: 24px 40px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  transition: all 0.3s ease;
}

.app-header.scrolled {
  padding: 16px 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
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
  cursor: pointer;
  transition: transform 0.3s;
}

.logo-section:hover {
  transform: scale(1.05);
}

.logo-icon {
  font-size: 2.2rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
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
  opacity: 0.9;
}

.brand {
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: 2px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.main-nav {
  display: flex;
  gap: 48px;
  flex: 1;
  justify-content: center;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-size: 1.05rem;
  font-weight: 600;
  letter-spacing: 1px;
  padding: 8px 4px;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
  position: relative;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: -3px;
  left: 0;
  width: 0;
  height: 3px;
  background: white;
  transition: width 0.3s ease;
}

.nav-link:hover::after,
.nav-link.active::after {
  width: 100%;
}

.nav-link.active {
  font-weight: 700;
}

.datetime-section {
  display: flex;
  gap: 24px;
  color: white;
  font-size: 0.95rem;
}

.time,
.date {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 16px;
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.icon {
  font-size: 1.2rem;
}

.sign-in-btn {
  background: white;
  color: #2d5016;
  border: none;
  padding: 14px 36px;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.sign-in-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
  background: #f0f0f0;
}

.sign-in-btn:active {
  transform: translateY(-1px);
}

@media (max-width: 1200px) {
  .datetime-section {
    display: none;
  }
}

@media (max-width: 768px) {
  .app-header {
    padding: 16px 20px;
  }

  .header-container {
    flex-wrap: wrap;
    gap: 16px;
  }

  .main-nav {
    gap: 24px;
    width: 100%;
    justify-content: center;
  }

  .logo-section {
    flex: 1;
  }
}
</style>
