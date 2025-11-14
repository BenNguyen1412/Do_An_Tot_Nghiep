<script setup lang="ts">
import { ref } from 'vue'

const stats = ref([
  {
    image: 'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=600',
    title: 'COURTS',
    value: '100+',
    description: 'Top-quality courts for your Pickleball game.',
  },
  {
    image: 'https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=600',
    title: 'CUSTOMERS',
    value: '4500+',
    description: 'Your game starts here',
  },
])
</script>

<template>
  <section class="stats-section">
    <div class="stats-container">
      <div v-for="(stat, index) in stats" :key="index" class="stat-card">
        <div class="stat-image">
          <img :src="stat.image" :alt="stat.title" />
          <div class="stat-overlay">
            <div class="stat-content">
              <h3 class="stat-title">{{ stat.title }}</h3>
              <div class="stat-value">{{ stat.value }}</div>
              <p class="stat-description">{{ stat.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.stats-section {
  padding: 80px 40px;
  background: #f5f5f5;
}

.stats-container {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 40px;
}

.stat-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  height: 400px;
}

.stat-image {
  width: 100%;
  height: 100%;
  position: relative;
}

.stat-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.stat-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.7));
  display: flex;
  align-items: flex-end;
  padding: 40px;
}

.stat-content {
  color: white;
}

.stat-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  letter-spacing: 2px;
}

.stat-value {
  font-size: 3.5rem;
  font-weight: 700;
  margin: 0 0 12px 0;
}

.stat-description {
  font-size: 1rem;
  margin: 0;
  opacity: 0.9;
}

@media (max-width: 768px) {
  .stats-container {
    grid-template-columns: 1fr;
  }
}
</style>
