<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import ChatWidget from '../components/ChatWidget.vue'

const router = useRouter()
const authStore = useAuthStore()
const showChat = ref(false)

onMounted(() => {
  // If user is already logged in, redirect to their dashboard
  if (authStore.isAuthenticated) {
    const roleRoutes = {
      customer: '/customer/home',
      admin: '/admin/dashboard',
      owner: '/owner/dashboard'
    }
    router.push(roleRoutes[authStore.role] || '/login')
  }
})

function openChat() {
  showChat.value = true
}

function closeChat() {
  showChat.value = false
}
</script>

<template>
  <div class="home-page">
    <!-- Logo badges top left -->
    <div class="logo-badges">
      <img src="../assets/images/logo_gundar_aptikom.png" alt="Logo Gundar & Aptikom">
    </div>
    
    <!-- Decorative boxes -->
    <div class="deco-box-top-right">
      <img src="../assets/images/decor_pojok_kanan_atas.png" alt="Dekorasi">
    </div>
    <div class="deco-box-bottom-left">
      <img src="../assets/images/decor_pojok_kiri_bawah.png" alt="Dekorasi">
    </div>
    
    <!-- Main Content Container -->
    <div class="main-content">
      <!-- Main logo -->
      <div class="logo-main">
        <img src="../assets/images/logo_apik.png" alt="Apik Laundry">
      </div>
      
      <!-- Tagline -->
      <p class="tagline">
        Cek Status, Riwayat, dan Info Laundry<br>Tanpa Ribet
      </p>
      
      <!-- Buttons -->
      <div class="button-group">
        <router-link to="/login" class="btn btn-login">Login</router-link>
        <router-link to="/register" class="btn btn-register">Register</router-link>
      </div>
    </div>
    
    <!-- Tanya Apik chat button -->
    <div @click="openChat" class="chat-button">
      <img src="../assets/images/comment.png" alt="Chat Icon" class="chat-icon-img">
      <span>Tanya Apik</span>
    </div>
    
    <!-- Chat Widget -->
    <ChatWidget v-if="showChat" @close="closeChat" />
  </div>
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.home-page {
  width: 100%;
  min-height: 100vh;
  background: #E8E8E8;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Logo badges top left */
.logo-badges {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 20;
}

.logo-badges img {
  height: 60px;
  width: auto;
  object-fit: contain;
}

/* Decorative boxes in corners */
.deco-box-top-right {
  position: absolute;
  top: 0;
  right: 0;
  z-index: 5;
}

.deco-box-top-right img {
  width: auto;
  height: auto;
  max-width: 250px;
  display: block;
}

.deco-box-bottom-left {
  position: absolute;
  bottom: 0;
  left: 0;
  z-index: 5;
}

.deco-box-bottom-left img {
  width: auto;
  height: auto;
  max-width: 250px;
  display: block;
}

/* Main content */
.main-content {
  text-align: center;
  z-index: 10;
  padding: 20px;
}

.logo-main {
  width: 400px;
  height: 400px;
  margin: 0 auto 30px;
}

.logo-main img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.tagline {
  font-family: 'Poppins', sans-serif;
  font-size: 20px;
  font-weight: 500;
  color: #000000;
  margin-bottom: 40px;
  line-height: 1.5;
}

/* Buttons */
.button-group {
  display: flex;
  gap: 30px;
  justify-content: center;
  align-items: center;
}

.btn {
  width: 232px;
  height: 51px;
  background: #1678F3;
  border: 2px solid #959191;
  border-radius: 8px;
  box-shadow: 0px 5px 7px rgba(0, 0, 0, 0.25);
  font-family: 'K2D', sans-serif;
  font-size: 24px;
  color: #000000;
  text-decoration: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  cursor: pointer;
  border-radius: 20px;
}

.btn:hover {
  background: #0d5ec4;
  color: #ffffff;
  box-shadow: 0px 7px 10px rgba(0, 0, 0, 0.35);
  transform: translateY(-2px);
}

/* Chat button */
.chat-button {
  position: fixed;
  bottom: 80px;
  right: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  z-index: 100;
  transition: all 0.3s ease;
  pointer-events: auto;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.chat-button:hover {
  transform: scale(1.1) translateY(0);
  animation: none;
}

.chat-icon-img {
  width: 74px;
  height: 74px;
  object-fit: contain;
  margin-bottom: 10px;
  pointer-events: none;
}

.chat-button span {
  font-family: 'Inter', sans-serif;
  font-size: 20px;
  font-weight: 600;
  color: #000000;
  pointer-events: none;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .logo-main {
    width: 350px;
    height: 350px;
  }
  
  .tagline {
    font-size: 18px;
  }
  
  .btn {
    width: 200px;
    font-size: 22px;
  }
  
  .button-group {
    gap: 25px;
  }
  
  .deco-box-top-right img,
  .deco-box-bottom-left img {
    max-width: 200px;
  }
}

@media (max-width: 768px) {
  .home-page {
    overflow-x: hidden !important;
    max-width: 100vw !important;
  }

  .logo-badges {
    top: 12px !important;
    left: 12px !important;
  }

  .logo-badges img {
    height: 48px !important;
  }
  
  .deco-box-top-right img,
  .deco-box-bottom-left img {
    max-width: 150px !important;
  }

  .main-content {
    padding: 12px !important;
    max-width: 100% !important;
  }
  
  .logo-main {
    width: 280px !important;
    height: 280px !important;
    margin-bottom: 20px !important;
  }
  
  .tagline {
    font-size: 17px !important;
    margin-bottom: 30px !important;
    padding: 0 20px !important;
    line-height: 1.4 !important;
  }
  
  .button-group {
    flex-direction: column !important;
    gap: 18px !important;
  }
  
  .btn {
    width: 200px !important;
    height: 48px !important;
    font-size: 18px !important;
    padding: 12px !important;
    min-height: 48px !important;
  }
  
  .chat-button {
    bottom: 24px !important;
    right: 24px !important;
  }
  
  .chat-icon-img {
    width: 56px !important;
    height: 56px !important;
    margin-bottom: 6px !important;
  }
  
  .chat-button span {
    font-size: 14px !important;
  }
}

@media (max-width: 480px) {
  .logo-badges {
    top: 10px !important;
    left: 10px !important;
  }

  .logo-badges img {
    height: 40px !important;
  }
  
  .deco-box-top-right img,
  .deco-box-bottom-left img {
    max-width: 100px !important;
  }

  .main-content {
    padding: 10px !important;
  }
  
  .logo-main {
    width: 220px !important;
    height: 220px !important;
  }
  
  .tagline {
    font-size: 15px !important;
    line-height: 1.4 !important;
    padding: 0 16px !important;
  }
  
  .btn {
    width: 180px !important;
    height: 48px !important;
    font-size: 16px !important;
    padding: 12px !important;
    min-height: 48px !important;
  }
  
  .chat-button {
    bottom: 20px !important;
    right: 20px !important;
  }
  
  .chat-icon-img {
    width: 52px !important;
    height: 52px !important;
    margin-bottom: 4px !important;
  }
  
  .chat-button span {
    font-size: 13px !important;
  }
}
</style>
