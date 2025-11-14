<script setup lang="ts">
import { ref } from 'vue'

interface FAQ {
  question: string
  answer: string
  isOpen: boolean
}

const faqs = ref<FAQ[]>([
  {
    question: 'How can I book a court ?',
    answer:
      'You can book a court through our website or mobile app. Simply select your preferred date, time, and location.',
    isOpen: false,
  },
  {
    question: 'What about locker room ?',
    answer:
      'All our facilities include clean and secure locker rooms with showers and changing areas.',
    isOpen: false,
  },
  {
    question: 'Can I rent an equipment ?',
    answer:
      'Yes, we offer equipment rental including paddles, balls, and other accessories at affordable rates.',
    isOpen: false,
  },
])

const toggleFAQ = (index: number) => {
  faqs.value[index].isOpen = !faqs.value[index].isOpen
}
</script>

<template>
  <section class="faq-section">
    <div class="faq-container">
      <div v-for="(faq, index) in faqs" :key="index" class="faq-item" @click="toggleFAQ(index)">
        <div class="faq-question">
          <span class="faq-icon">{{ faq.isOpen ? '−' : '+' }}</span>
          <h3>{{ faq.question }}</h3>
        </div>
        <div v-if="faq.isOpen" class="faq-answer">
          <p>{{ faq.answer }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.faq-section {
  padding: 80px 40px;
  background: white;
}

.faq-container {
  max-width: 1000px;
  margin: 0 auto;
}

.faq-item {
  border-bottom: 2px solid #e0e0e0;
  padding: 24px 0;
  cursor: pointer;
  transition: all 0.3s;
}

.faq-item:hover {
  background: #f9f9f9;
}

.faq-question {
  display: flex;
  align-items: center;
  gap: 16px;
}

.faq-icon {
  width: 32px;
  height: 32px;
  border: 2px solid #2d5016;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: #2d5016;
  font-weight: 300;
}

.faq-question h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
  font-weight: 600;
}

.faq-answer {
  margin-top: 16px;
  padding-left: 48px;
  animation: slideDown 0.3s ease;
}

.faq-answer p {
  margin: 0;
  color: #666;
  line-height: 1.6;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
