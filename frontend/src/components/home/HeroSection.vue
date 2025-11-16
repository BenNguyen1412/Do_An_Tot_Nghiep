<script setup lang="ts">
import { ref } from 'vue'

const searchQuery = ref('')
const selectedLocation = ref('')

const handleSearch = () => {
  console.log('Search:', searchQuery.value, selectedLocation.value)
}
</script>

<template>
  <section class="hero-section">
    <div class="hero-background">
      <div class="hero-overlay"></div>
    </div>

    <div class="hero-container">
      <!-- Left Content -->
      <div class="hero-content">
        <div class="hero-badge">🏆 #1 Pickleball Platform in Vietnam</div>

        <h1 class="hero-title">Our pick court has...</h1>

        <h2 class="hero-subtitle">
          WE SERVICE OUR SPORT<br />
          <span class="highlight">FOR EVERYBODY</span>
        </h2>

        <p class="hero-description">
          WATASHI HA PHUOC DESU, NIHONG<br />
          GA SUKI DESU, NIHONG GA<br />
          IKITAIDESU.
        </p>

        <!-- Search Box -->
        <div class="search-box">
          <div class="search-field">
            <label>🔍 Search for</label>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Enter court name..."
              class="search-input"
            />
          </div>

          <div class="search-field">
            <label>📍 Where</label>
            <select v-model="selectedLocation" class="location-select">
              <option value="">Choose location</option>
              <option value="district1">District 1, HCMC</option>
              <option value="district3">District 3, HCMC</option>
              <option value="district10">District 10, HCMC</option>
            </select>
          </div>

          <button class="search-btn" @click="handleSearch">
            <span class="btn-icon">🔍</span>
            <span class="btn-text">Search</span>
          </button>
        </div>

        <!-- Features -->
        <div class="hero-features">
          <div class="feature-item">
            <span class="feature-icon">✓</span>
            <span>100+ Courts Available</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">✓</span>
            <span>Instant Booking</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">✓</span>
            <span>Best Price Guarantee</span>
          </div>
        </div>
      </div>

      <!-- Right Image -->
      <div class="hero-image-section">
        <div class="image-card">
          <img
            src="https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=800"
            alt="Pickleball Paddle"
          />
          <div class="image-badge">
            <div class="badge-content">
              <span class="badge-number">4.9</span>
              <span class="badge-stars">⭐⭐⭐⭐⭐</span>
              <span class="badge-text">4,500+ Reviews</span>
            </div>
          </div>
        </div>

        <!-- Floating Cards -->
        <div class="floating-card card-1">
          <div class="card-icon">🎾</div>
          <div class="card-info">
            <span class="card-title">Equipment Ready</span>
            <span class="card-desc">Paddles & Balls</span>
          </div>
        </div>

        <div class="floating-card card-2">
          <div class="card-icon">⚡</div>
          <div class="card-info">
            <span class="card-title">Quick Booking</span>
            <span class="card-desc">2 minutes setup</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero-section {
  position: relative;
  padding: 100px 40px 120px;
  overflow: hidden;
}

.hero-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  z-index: -1;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(circle at 20% 50%, rgba(76, 175, 80, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(139, 195, 74, 0.1) 0%, transparent 50%);
}

.hero-container {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
  align-items: center;
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  animation: fadeInLeft 1s ease;
}

@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #4a7c2c 0%, #2d5016 100%);
  color: white;
  padding: 12px 24px;
  border-radius: 50px;
  font-size: 0.9rem;
  font-weight: 600;
  width: fit-content;
  box-shadow: 0 4px 15px rgba(74, 124, 44, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.hero-title {
  font-size: 2.2rem;
  color: #555;
  font-weight: 500;
  margin: 0;
  letter-spacing: -0.5px;
}

.hero-subtitle {
  font-size: 3.2rem;
  color: #2d5016;
  font-weight: 800;
  line-height: 1.1;
  margin: 0;
  letter-spacing: -1px;
}

.highlight {
  color: #4a7c2c;
  position: relative;
  display: inline-block;
}

.highlight::after {
  content: '';
  position: absolute;
  bottom: 8px;
  left: 0;
  right: 0;
  height: 12px;
  background: rgba(139, 195, 74, 0.3);
  z-index: -1;
}

.hero-description {
  font-size: 1.15rem;
  color: #666;
  line-height: 1.8;
  margin: 0;
  font-weight: 500;
}

.search-box {
  background: white;
  padding: 32px;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 16px;
  align-items: flex-end;
  margin-top: 16px;
  transition: all 0.3s;
}

.search-box:hover {
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.search-field {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.search-field label {
  font-size: 0.95rem;
  color: #666;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.search-input,
.location-select {
  padding: 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s;
  font-family: inherit;
}

.search-input:focus,
.location-select:focus {
  border-color: #4a7c2c;
  box-shadow: 0 0 0 4px rgba(74, 124, 44, 0.1);
}

.location-select {
  background: white;
  cursor: pointer;
}

.search-btn {
  padding: 16px 36px;
  background: linear-gradient(135deg, #4a7c2c 0%, #2d5016 100%);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 4px 15px rgba(74, 124, 44, 0.3);
}

.search-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(74, 124, 44, 0.4);
}

.btn-icon {
  font-size: 1.2rem;
}

.hero-features {
  display: flex;
  gap: 32px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #2d5016;
  font-weight: 600;
  font-size: 0.95rem;
}

.feature-icon {
  width: 24px;
  height: 24px;
  background: #4a7c2c;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
}

.hero-image-section {
  position: relative;
  animation: fadeInRight 1s ease;
}

@keyframes fadeInRight {
  from {
    opacity: 0;
    transform: translateX(50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.image-card {
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.image-card img {
  width: 100%;
  height: 600px;
  object-fit: cover;
  display: block;
}

.image-badge {
  position: absolute;
  bottom: 30px;
  right: 30px;
  background: white;
  padding: 20px 28px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.badge-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.badge-number {
  font-size: 2rem;
  font-weight: 800;
  color: #2d5016;
}

.badge-stars {
  font-size: 1rem;
  letter-spacing: 2px;
}

.badge-text {
  font-size: 0.85rem;
  color: #666;
  font-weight: 600;
}

.floating-card {
  position: absolute;
  background: white;
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 16px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-15px);
  }
}

.card-1 {
  top: 60px;
  left: -40px;
  animation-delay: 0s;
}

.card-2 {
  bottom: 100px;
  left: -60px;
  animation-delay: 1.5s;
}

.card-icon {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #4a7c2c 0%, #2d5016 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.card-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-title {
  font-weight: 700;
  color: #2d5016;
  font-size: 1rem;
}

.card-desc {
  font-size: 0.85rem;
  color: #666;
}

@media (max-width: 1024px) {
  .hero-container {
    grid-template-columns: 1fr;
    gap: 60px;
  }

  .hero-image-section {
    order: -1;
  }

  .floating-card {
    display: none;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 60px 20px 80px;
  }

  .search-box {
    flex-direction: column;
    padding: 24px;
  }

  .hero-subtitle {
    font-size: 2.2rem;
  }

  .hero-title {
    font-size: 1.6rem;
  }

  .image-card img {
    height: 400px;
  }
}
</style>
