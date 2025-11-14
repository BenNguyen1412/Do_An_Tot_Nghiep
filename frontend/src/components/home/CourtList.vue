<script setup lang="ts">
import { ref } from 'vue'

interface Court {
  id: number
  name: string
  district: string
  bookings: number
  distance: string
  image: string
  badge: string
}

const courts = ref<Court[]>([
  {
    id: 1,
    name: 'SÂN AB',
    district: 'Distric 1, HCMC',
    bookings: 40,
    distance: '1.1 km away',
    image: 'https://images.unsplash.com/photo-1622163642998-1ea32b0bbc67?w=400',
    badge: '40+',
  },
  {
    id: 2,
    name: 'SÂN E',
    district: 'Distric 10, HCMC',
    bookings: 80,
    distance: '3 km away',
    image: 'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=400',
    badge: '80+',
  },
  {
    id: 3,
    name: 'SÂN C',
    district: 'Distric 3, HCMC',
    bookings: 100,
    distance: '1.2 km away',
    image: 'https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=400',
    badge: '100+',
  },
])
</script>

<template>
  <section class="court-list-section">
    <div class="container">
      <h2 class="section-title">
        Discover nearby pickleball courts for convenient<br />
        and accessible gameplay.
      </h2>

      <div class="courts-grid">
        <div v-for="court in courts" :key="court.id" class="court-card">
          <div class="court-image">
            <img :src="court.image" :alt="court.name" />
          </div>

          <div class="court-info">
            <h3 class="court-name">{{ court.name }}</h3>
            <p class="court-district">📍 {{ court.district }}</p>

            <div class="court-meta">
              <span class="bookings-badge" :class="getBadgeClass(court.bookings)">
                {{ court.badge }} Bookings
              </span>
              <span class="distance-badge"> 🚗 {{ court.distance }} </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script lang="ts">
export default {
  methods: {
    getBadgeClass(bookings: number) {
      if (bookings >= 100) return 'badge-gold'
      if (bookings >= 80) return 'badge-silver'
      return 'badge-bronze'
    },
  },
}
</script>

<style scoped>
.court-list-section {
  padding: 80px 40px;
  background: white;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
}

.section-title {
  text-align: center;
  font-size: 2rem;
  color: #333;
  margin-bottom: 60px;
  line-height: 1.4;
}

.courts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 32px;
}

.court-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition:
    transform 0.3s,
    box-shadow 0.3s;
}

.court-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.court-image {
  width: 100%;
  height: 240px;
  overflow: hidden;
}

.court-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.court-card:hover .court-image img {
  transform: scale(1.1);
}

.court-info {
  padding: 24px;
}

.court-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d5016;
  margin: 0 0 12px 0;
}

.court-district {
  color: #666;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.court-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.bookings-badge,
.distance-badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
}

.bookings-badge {
  background: #fff3cd;
  color: #856404;
}

.badge-gold {
  background: #ffd700;
  color: #000;
}

.badge-silver {
  background: #c0c0c0;
  color: #000;
}

.badge-bronze {
  background: #cd7f32;
  color: #fff;
}

.distance-badge {
  background: #d4edda;
  color: #155724;
}

@media (max-width: 768px) {
  .section-title {
    font-size: 1.5rem;
  }
}
</style>
