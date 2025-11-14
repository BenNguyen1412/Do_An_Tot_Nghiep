<script setup lang="ts">
import { ref } from 'vue'

const searchQuery = ref('')
const selectedLocation = ref('')
</script>

<template>
  <section class="hero-section">
    <div class="hero-container">
      <!-- Left Content -->
      <div class="hero-content">
        <h1 class="hero-title">Our pick court ha ...</h1>
        <h2 class="hero-subtitle">
          WE SERVICE OUR SPORT<br />
          FOR EVERYBODY
        </h2>
        <p class="hero-description">
          WATASHI HA PHUOC DESU, NIHONG<br />
          GA SUKI DESU, NIHONG GA<br />
          IKITAIDESU.
        </p>

        <!-- Search Box -->
        <div class="search-box">
          <div class="search-field">
            <label>Search for</label>
            <input v-model="searchQuery" type="text" placeholder="Court" class="search-input" />
          </div>

          <div class="search-field">
            <label>Where</label>
            <select v-model="selectedLocation" class="location-select">
              <option value="">Chose location</option>
              <option value="district1">District 1, HCMC</option>
              <option value="district3">District 3, HCMC</option>
              <option value="district10">District 10, HCMC</option>
            </select>
          </div>

          <button class="search-btn">🔍</button>
        </div>
      </div>

      <!-- Right Image -->
      <div class="hero-image">
        <img
          src="https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=600"
          alt="Pickleball Paddle"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero-section {
  background: #f5f5f5;
  padding: 80px 40px;
}

.hero-container {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-title {
  font-size: 2rem;
  color: #333;
  font-weight: 400;
  margin: 0;
}

.hero-subtitle {
  font-size: 2.5rem;
  color: #2d5016;
  font-weight: 700;
  line-height: 1.2;
  margin: 0;
}

.hero-description {
  font-size: 1.1rem;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

.search-box {
  background: white;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 16px;
  align-items: flex-end;
}

.search-field {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.search-field label {
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
}

.search-input,
.location-select {
  padding: 14px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s;
}

.search-input:focus,
.location-select:focus {
  border-color: #4a7c2c;
}

.location-select {
  background: white;
  cursor: pointer;
}

.search-btn {
  padding: 14px 24px;
  background: #4a7c2c;
  border: none;
  border-radius: 8px;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.3s;
}

.search-btn:hover {
  background: #2d5016;
  transform: translateY(-2px);
}

.hero-image {
  position: relative;
}

.hero-image img {
  width: 100%;
  height: 500px;
  object-fit: cover;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

@media (max-width: 1024px) {
  .hero-container {
    grid-template-columns: 1fr;
  }

  .hero-image {
    order: -1;
  }
}

@media (max-width: 768px) {
  .search-box {
    flex-direction: column;
  }

  .hero-subtitle {
    font-size: 2rem;
  }
}
</style>
