<script setup lang="ts">
import { useRouter } from 'vue-router'
import AppHeader from '@/components/layout/AppHeader.vue'
import HeroSection from '@/components/home/HeroSection.vue'
import CourtList from '@/components/home/CourtList.vue'
import StatsSection from '@/components/home/StatsSection.vue'
import FAQSection from '@/components/home/FAQSection.vue'
import AppFooter from '@/components/layout/AppFooter.vue'

const router = useRouter()

const goToAdvertisements = () => {
  router.push('/owner/advertisements/list')
}
</script>

<template>
  <div class="owner-home-page">
    <!-- Header cho Owner: Home, Court, Management + Time + Owner Name -->
    <AppHeader :show-management="true" />

    <HeroSection />

    <!-- Advertisement Button Section -->
    <div class="ad-section">
      <button @click="goToAdvertisements" class="btn-ads">
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
            d="M13 10V3L4 14h7v7l9-11h-7z"
          />
        </svg>
        Quản lý Quảng cáo
      </button>
    </div>

    <CourtList />
    <StatsSection />
    <FAQSection />
    <AppFooter />
  </div>
</template>

<style scoped>
.owner-home-page {
  min-height: 100vh;
}

.ad-section {
  display: flex;
  justify-content: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, #f0fdf4 0%, #fef3c7 100%);
}

.btn-ads {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 28px;
  background: #22c55e;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.btn-ads:hover {
  background: #16a34a;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(34, 197, 94, 0.4);
}

.btn-ads:active {
  transform: translateY(0);
}

.btn-ads svg {
  width: 20px;
  height: 20px;
}

@media (max-width: 768px) {
  .ad-section {
    padding: 30px 15px;
  }

  .btn-ads {
    padding: 12px 24px;
    font-size: 14px;
  }
}
</style>
