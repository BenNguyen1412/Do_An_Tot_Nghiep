<template>
  <footer class="app-footer">
    <div class="footer-container">
      <!-- Logo Section -->
      <div class="footer-section">
        <div class="footer-logo">
          <div class="logo-icon">🏓</div>
          <div class="logo-text">
            <span class="pickleball">Pickleball</span>
            <span class="brand">NP SPORTCLUB</span>
          </div>
        </div>
      </div>

      <!-- Links Section -->
      <div class="footer-section">
        <h3>Home</h3>
        <h3>Court</h3>
        <h3>About us</h3>
      </div>

      <!-- Contact Section -->
      <div class="footer-section">
        <h3>Contact us</h3>
        <p>266 Ly Thuong Kiet, Dien Hong<br />district, HCMC</p>
        <p>huuphuoc1218@gmail.com</p>
        <p>+84 123948172</p>
      </div>
    </div>

    <div class="footer-bottom">
      <p>© 2025 NP Sportclub - All rights reserved.</p>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  background: #a8d5a8;
  color: #2d5016;
  padding: 60px 40px 20px;
}

.footer-container {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 40px;
  margin-bottom: 40px;
}

.footer-section h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 16px 0;
}

.footer-section p {
  margin: 8px 0;
  line-height: 1.6;
  color: #2d5016;
}

.footer-logo {
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

.footer-bottom {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid rgba(45, 80, 22, 0.3);
}

.footer-bottom p {
  margin: 0;
  font-size: 0.9rem;
}
</style>
