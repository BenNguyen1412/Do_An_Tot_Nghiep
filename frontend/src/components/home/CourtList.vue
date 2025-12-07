<script setup lang="ts">
import { ref } from 'vue'

interface Court {
  id: number
  name: string
  district: string
  bookings: number
  image: string
  badge: string
  price: number
}

const courts = ref<Court[]>([
  {
    id: 1,
    name: 'COURT AB',
    district: 'District 1, HCMC',
    bookings: 40,
    image: 'https://i.pinimg.com/1200x/0e/c0/4d/0ec04dde4f138cac5ec5e928edef20e9.jpg',
    badge: '40+',
    price: 150000,
  },
  {
    id: 2,
    name: 'COURT E',
    district: 'District 10, HCMC',
    bookings: 80,
    image: 'https://i.pinimg.com/1200x/0e/45/49/0e4549edf637e28dcd0d6c9900a34222.jpg',
    badge: '80+',
    price: 200000,
  },
  {
    id: 3,
    name: 'COURT C',
    district: 'District 3, HCMC',
    bookings: 100,
    image: 'https://i.pinimg.com/736x/4e/28/51/4e2851f36c77df07b96cd59400b39ef4.jpg',
    badge: '100+',
    price: 180000,
  },
])

const getBadgeClass = (bookings: number) => {
  if (bookings >= 100) return 'badge-gold'
  if (bookings >= 80) return 'badge-silver'
  return 'badge-bronze'
}

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
  }).format(price)
}
</script>

<template>
  <section class="court-list-section">
    <div class="container">
      <div class="section-header">
        <div class="header-content">
          <span class="section-badge"><i class="fas fa-trophy"></i> Popular Courts</span>
          <h2 class="section-title">
            Discover nearby pickleball courts for<br />
            <span class="highlight">convenient and accessible gameplay</span>
          </h2>
          <p class="section-description">
            Find the perfect court near you with the best facilities and competitive prices
          </p>
        </div>
        <button class="view-all-btn">View All Courts →</button>
      </div>

      <div class="courts-grid">
        <div v-for="court in courts" :key="court.id" class="court-card">
          <div class="court-image">
            <img :src="court.image" :alt="court.name" />
            <div class="image-overlay">
              <button class="favorite-btn"><i class="fas fa-heart"></i></button>
            </div>
            <div class="court-badge" :class="getBadgeClass(court.bookings)">
              {{ court.badge }} Bookings
            </div>
          </div>

          <div class="court-info">
            <div class="court-header">
              <h3 class="court-name">{{ court.name }}</h3>
            </div>

            <p class="court-district"><i class="fas fa-map-marker-alt"></i> {{ court.district }}</p>

            <div class="court-footer">
              <div class="court-meta">
                <span class="price"> {{ formatPrice(court.price) }}/hour </span>
              </div>

              <button class="book-btn">Book Now</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.court-list-section {
  padding: 100px 40px;
  background: white;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 60px;
  gap: 40px;
}

.header-content {
  flex: 1;
}

.section-badge {
  display: inline-block;
  background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
  color: #856404;
  padding: 10px 20px;
  border-radius: 50px;
  font-size: 0.9rem;
  font-weight: 700;
  margin-bottom: 16px;
}

.section-title {
  font-size: 2.8rem;
  color: #2d5016;
  font-weight: 800;
  line-height: 1.3;
  margin: 0 0 16px 0;
  letter-spacing: -1px;
}

.highlight {
  color: #4a7c2c;
  position: relative;
}

.section-description {
  font-size: 1.1rem;
  color: #666;
  margin: 0;
  max-width: 600px;
}

.view-all-btn {
  padding: 16px 32px;
  background: transparent;
  border: 2px solid #4a7c2c;
  color: #4a7c2c;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.view-all-btn:hover {
  background: #4a7c2c;
  color: white;
  transform: translateX(5px);
}

.courts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 40px;
}

.court-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.08);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid #f0f0f0;
}

.court-card:hover {
  transform: translateY(-12px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
}

.court-image {
  width: 100%;
  height: 260px;
  position: relative;
  overflow: hidden;
}

.court-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.court-card:hover .court-image img {
  transform: scale(1.15);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.3) 0%, transparent 50%);
  opacity: 0;
  transition: opacity 0.3s;
}

.court-card:hover .image-overlay {
  opacity: 1;
}

.favorite-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 44px;
  height: 44px;
  background: white;
  border: none;
  border-radius: 50%;
  font-size: 1.3rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s;
  color: #ff4757;
}

.favorite-btn:hover {
  transform: scale(1.1);
  color: #ff6348;
}

.court-badge {
  position: absolute;
  bottom: 16px;
  left: 16px;
  padding: 10px 20px;
  border-radius: 50px;
  font-size: 0.85rem;
  font-weight: 700;
  backdrop-filter: blur(10px);
}

.badge-gold {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #000;
  box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4);
}

.badge-silver {
  background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
  color: #000;
  box-shadow: 0 4px 15px rgba(192, 192, 192, 0.4);
}

.badge-bronze {
  background: linear-gradient(135deg, #cd7f32 0%, #e89f71 100%);
  color: #fff;
  box-shadow: 0 4px 15px rgba(205, 127, 50, 0.4);
}

.court-info {
  padding: 28px;
}

.court-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.court-name {
  font-size: 1.6rem;
  font-weight: 800;
  color: #2d5016;
  margin: 0;
  letter-spacing: -0.5px;
}

.rating-value {
  font-weight: 700;
  color: #2d5016;
  font-size: 0.95rem;
}

.court-district {
  color: #666;
  margin: 0 0 20px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
}

.court-district i {
  color: #ff4757;
}

.court-footer {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.court-meta {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.distance,
.price {
  font-size: 0.95rem;
  font-weight: 600;
  color: #666;
}

.price {
  color: #4a7c2c;
  font-size: 1.1rem;
  font-weight: 800;
}

.book-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #4a7c2c 0%, #2d5016 100%);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(74, 124, 44, 0.3);
}

.book-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(74, 124, 44, 0.4);
}

@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .section-title {
    font-size: 2rem;
  }

  .courts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
