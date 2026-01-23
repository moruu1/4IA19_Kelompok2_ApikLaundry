<template>
  <div class="profile-page">
    <!-- Left side - Form -->
    <div class="profile-form-section">
      <div class="form-container">
        <h2 class="form-title">Edit Profile</h2>

        <!-- Success Message -->
        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <form @submit.prevent="handleSubmit">
          <!-- Username Field -->
          <div class="form-group">
            <label class="form-label">Username</label>
            <div class="input-wrapper">
              <i class="fas fa-user input-icon"></i>
              <input
                v-model="formData.username"
                type="text"
                placeholder="Username"
                class="form-input"
                required
              />
            </div>
          </div>

          <!-- Name Field -->
          <div class="form-group">
            <label class="form-label">Nama</label>
            <div class="input-wrapper">
              <i class="fas fa-id-card input-icon"></i>
              <input
                v-model="formData.fullName"
                type="text"
                placeholder="Name"
                class="form-input"
                required
              />
            </div>
          </div>

          <!-- Address Field -->
          <div class="form-group">
            <label class="form-label">Alamat</label>
            <div class="input-wrapper">
              <i class="fas fa-map-marker-alt input-icon"></i>
              <input
                v-model="formData.address"
                type="text"
                placeholder="Alamat"
                class="form-input"
              />
            </div>
          </div>

          <!-- Phone Number Field -->
          <div class="form-group">
            <label class="form-label">Phone Number</label>
            <div class="input-wrapper">
              <i class="fas fa-phone input-icon"></i>
              <input
                v-model="formData.phone"
                type="tel"
                placeholder="Phone Number"
                class="form-input"
              />
            </div>
          </div>

          <!-- Buttons -->
          <div class="button-group">
            <button 
              type="submit" 
              class="save-button"
            >
              Simpan
            </button>
            <button 
              type="button" 
              class="change-password-button"
              @click="goToChangePassword"
            >
              Ganti Password
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Right side - Blue background with decoration -->
    <div class="profile-decoration">
      <div class="decoration-shape"></div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  username: 'owner',
  fullName: 'Owner Laundry',
  address: 'Jl. Margonda Raya No. 100',
  phone: '081234567890'
})

const errorMessage = ref('')
const successMessage = ref('')

const handleSubmit = () => {
  errorMessage.value = ''
  successMessage.value = ''
  
  // TODO: Implement profile update logic
  console.log('Profile updated:', formData.value)
  successMessage.value = 'Profil berhasil diperbarui'
  
  // Redirect to owner dashboard after 1 second
  setTimeout(() => {
    router.push('/owner/dashboard')
  }, 1000)
}

const goToChangePassword = () => {
  router.push('/owner/change-password')
}
</script>

<style scoped>
.profile-page {
  display: flex;
  min-height: 100vh;
}

/* Left Side - Form */
.profile-form-section {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  background: #F9F9F9;
  position: relative;
}

.profile-form-section::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 5px;
  background: #1678F3;
}

.form-container {
  width: 100%;
  max-width: 480px;
  background: white;
  padding: 30px 40px;
  border-radius: 0;
  max-height: 90vh;
  overflow-y: auto;
}

.form-title {
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  font-weight: 400;
  color: #999999;
  margin-bottom: 20px;
}

.success-message {
  background: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 13px;
}

.error-message {
  background: #fee;
  border: 1px solid #fcc;
  color: #c33;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 13px;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  color: #333333;
  margin-bottom: 6px;
  font-weight: 500;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 15px;
  color: #999999;
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 10px 15px 10px 40px;
  border: 1px solid #DDDDDD;
  border-radius: 4px;
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  color: #333333;
  outline: none;
  transition: border-color 0.3s;
}

.form-input::placeholder {
  color: #AAAAAA;
}

.form-input:focus {
  border-color: #1678F3;
}

.button-group {
  display: flex;
  gap: 15px;
  margin-top: 25px;
}

.save-button,
.change-password-button {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 4px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.save-button {
  background: #1678F3;
  color: white;
}

.save-button:hover {
  background: #0d5ec4;
}

.change-password-button {
  background: white;
  color: #1678F3;
  border: 1px solid #1678F3;
}

.change-password-button:hover {
  background: #1678F3;
  color: white;
}

/* Right Side - Decoration */
.profile-decoration {
  flex: 1;
  background: linear-gradient(135deg, #1678F3 0%, #6BB6FF 100%);
  position: relative;
  overflow: hidden;
  border-radius: 60px 0 0 60px;
}

.decoration-shape {
  position: absolute;
  width: 200%;
  height: 200%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(45deg);
  background: rgba(255, 255, 255, 0.05);
}

/* Responsive */
@media (max-width: 768px) {
  .profile-page {
    flex-direction: column !important;
  }

  .profile-decoration {
    display: none !important;
  }

  .profile-form-section {
    padding: 20px !important;
  }

  .form-title {
    font-size: 24px !important;
  }

  .form-label {
    font-size: 14px !important;
  }

  .form-input {
    font-size: 16px !important;
    padding: 12px !important;
  }

  .button-group {
    flex-direction: column !important;
    gap: 12px !important;
  }

  .save-button,
  .change-password-button {
    width: 100% !important;
    min-height: 48px !important;
    font-size: 16px !important;
    padding: 14px !important;
  }
}
</style>
