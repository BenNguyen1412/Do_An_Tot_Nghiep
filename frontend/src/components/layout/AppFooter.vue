<script setup lang="ts">
import { ref } from 'vue'

const currentYear = new Date().getFullYear()

const email = ref('')

const subscribeNewsletter = () => {
  if (email.value) {
    alert(`Thanks for subscribing with: ${email.value}`)
    email.value = ''
  }
}

const socialLinks = [
  { icon: '📘', name: 'Facebook', url: '#' },
  { icon: '📷', name: 'Instagram', url: '#' },
  { icon: '🐦', name: 'Twitter', url: '#' },
  { icon: '💼', name: 'LinkedIn', url: '#' },
]

const quickLinks = [
  { name: 'Home', url: '/' },
  { name: 'Court', url: '/court' },
  { name: 'About us', url: '/about' },
]

const supportLinks = [
  { name: 'Help Center', url: '/help' },
  { name: 'Contact Us', url: '/contact' },
]
</script>

<template>
  <footer class="app-footer">
    <!-- Main Footer Content -->
    <div class="footer-main">
      <div class="footer-container">
        <!-- Company Info -->
        <div class="footer-section brand-section">
          <div class="footer-logo">
            <div class="logo-icon">🏓</div>
            <div class="logo-text">
              <span class="pickleball">Pickleball</span>
              <span class="brand">NP SPORTCLUB</span>
            </div>
          </div>
          <p class="brand-description">
            Your premier destination for Pickleball courts and facilities. Experience the best
            gameplay with top-quality courts and excellent service.
          </p>

          <!-- Social Links -->
          <div class="social-links">
            <a
              v-for="social in socialLinks"
              :key="social.name"
              :href="social.url"
              class="social-link"
              :title="social.name"
            >
              {{ social.icon }}
            </a>
          </div>
        </div>

        <!-- Quick Links -->
        <div class="footer-section">
          <h3 class="footer-title">Quick Links</h3>
          <ul class="footer-links">
            <li v-for="link in quickLinks" :key="link.name">
              <router-link :to="link.url" class="footer-link">
                {{ link.name }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Support -->
        <div class="footer-section">
          <h3 class="footer-title">Support</h3>
          <ul class="footer-links">
            <li v-for="link in supportLinks" :key="link.name">
              <a :href="link.url" class="footer-link">
                {{ link.name }}
              </a>
            </li>
          </ul>
        </div>

        <!-- Contact & Newsletter -->
        <div class="footer-section">
          <h3 class="footer-title">Contact Us</h3>
          <div class="contact-info">
            <div class="contact-item">
              <span class="contact-icon">📍</span>
              <span>266 Ly Thuong Kiet, Dien Hong<br />District, HCMC</span>
            </div>
            <div class="contact-item">
              <span class="contact-icon">✉️</span>
              <a href="mailto:huuphuoc1218@gmail.com">huuphuoc1218@gmail.com</a>
            </div>
            <div class="contact-item">
              <span class="contact-icon">📞</span>
              <a href="tel:+84123948172">+84 123 948 172</a>
            </div>
          </div>

          <!-- Newsletter -->
          <div class="newsletter">
            <h4 class="newsletter-title">Subscribe to Newsletter</h4>
            <form @submit.prevent="subscribeNewsletter" class="newsletter-form">
              <input
                v-model="email"
                type="email"
                placeholder="Your email address"
                class="newsletter-input"
                required
              />
              <button type="submit" class="newsletter-btn">➤</button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer Bottom -->
    <div class="footer-bottom">
      <div class="footer-container">
        <div class="footer-bottom-content">
          <p class="copyright">© {{ currentYear }} NP Sportclub. All rights reserved.</p>
          <div class="footer-badges">
            <span class="badge">🔒 Secure Payment</span>
            <span class="badge">✓ Verified Business</span>
            <span class="badge">⭐ 4.9 Rating</span>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  background: linear-gradient(135deg, #a8d5a8 0%, #8bc34a 100%);
  color: #1b5e20;
}

.footer-main {
  padding: 80px 40px 40px;
}

.footer-container {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.5fr;
  gap: 60px;
}

.footer-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.brand-section {
  gap: 24px;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 2.5rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.pickleball {
  font-size: 1rem;
  font-weight: 500;
  opacity: 0.9;
}

.brand {
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: 2px;
}

.brand-description {
  font-size: 1rem;
  line-height: 1.7;
  opacity: 0.9;
  margin: 0;
}

.social-links {
  display: flex;
  gap: 12px;
}

.social-link {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  transition: all 0.3s;
  backdrop-filter: blur(10px);
}

.social-link:hover {
  background: white;
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.footer-title {
  font-size: 1.3rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: 0.5px;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.footer-link {
  color: #1b5e20;
  text-decoration: none;
  font-size: 1rem;
  transition: all 0.3s;
  display: inline-block;
  font-weight: 500;
}

.footer-link:hover {
  color: #2d5016;
  transform: translateX(5px);
  font-weight: 600;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.contact-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  font-size: 1rem;
  line-height: 1.6;
}

.contact-icon {
  font-size: 1.3rem;
  flex-shrink: 0;
}

.contact-item a {
  color: #1b5e20;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.contact-item a:hover {
  color: #2d5016;
  text-decoration: underline;
}

.newsletter {
  margin-top: 8px;
}

.newsletter-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0 0 12px 0;
}

.newsletter-form {
  display: flex;
  gap: 8px;
}

.newsletter-input {
  flex: 1;
  padding: 14px 18px;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-radius: 10px;
  font-size: 0.95rem;
  outline: none;
  background: rgba(255, 255, 255, 0.3);
  color: #1b5e20;
  backdrop-filter: blur(10px);
  transition: all 0.3s;
}

.newsletter-input::placeholder {
  color: rgba(27, 94, 32, 0.6);
}

.newsletter-input:focus {
  background: rgba(255, 255, 255, 0.5);
  border-color: white;
}

.newsletter-btn {
  padding: 14px 20px;
  background: #2d5016;
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s;
}

.newsletter-btn:hover {
  background: #1b5e20;
  transform: translateX(4px);
}

.footer-bottom {
  background: rgba(0, 0, 0, 0.1);
  padding: 28px 40px;
  backdrop-filter: blur(10px);
}

.footer-bottom-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.copyright {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 500;
}

.footer-badges {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.badge {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
}

@media (max-width: 1024px) {
  .footer-container {
    grid-template-columns: 1fr 1fr;
    gap: 40px;
  }
}

@media (max-width: 768px) {
  .footer-main {
    padding: 60px 20px 40px;
  }

  .footer-container {
    grid-template-columns: 1fr;
    gap: 40px;
  }

  .footer-bottom {
    padding: 20px;
  }

  .footer-bottom-content {
    flex-direction: column;
    text-align: center;
  }

  .footer-badges {
    justify-content: center;
  }
}
</style>
