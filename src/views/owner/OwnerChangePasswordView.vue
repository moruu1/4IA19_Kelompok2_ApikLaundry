<template>
  <div class="change-password-page">
    <!-- Left side - Form -->
    <div class="password-form-section">
      <div class="form-container">
        <h2 class="form-title">Ubah Password</h2>

        <!-- Success Message -->
        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <form @submit.prevent="handleSubmit">
          <!-- Old Password Field -->
          <div class="form-group">
            <label class="form-label">Masukkan Password Lama</label>
            <div class="input-wrapper">
              <i class="fas fa-lock input-icon"></i>
              <input
                v-model="formData.oldPassword"
                :type="showOldPassword ? 'text' : 'password'"
                placeholder="*Password length (10-32)"
                class="form-input"
                required
              />
              <button 
                type="button" 
                @click="showOldPassword = !showOldPassword"
                class="toggle-password"
              >
                <i :class="showOldPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
          </div>

          <!-- New Password Field -->
          <div class="form-group">
            <label class="form-label">Masukkan Password Baru</label>
            <div class="input-wrapper">
              <i class="fas fa-lock input-icon"></i>
              <input
                v-model="formData.newPassword"
                :type="showNewPassword ? 'text' : 'password'"
                placeholder="*Password length (10-32)"
                class="form-input"
                required
              />
              <button 
                type="button" 
                @click="showNewPassword = !showNewPassword"
                class="toggle-password"
              >
                <i :class="showNewPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
          </div>

          <!-- Confirm Password Field -->
          <div class="form-group">
            <label class="form-label">Masukkan Password Baru</label>
            <div class="input-wrapper">
              <i class="fas fa-lock input-icon"></i>
              <input
                v-model="formData.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                placeholder="*Password length (10-32)"
                class="form-input"
                required
              />
              <button 
                type="button" 
                @click="showConfirmPassword = !showConfirmPassword"
                class="toggle-password"
              >
                <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
          </div>

          <!-- Submit Button -->
          <button 
            type="submit" 
            class="save-button"
          >
            Simpan
          </button>
        </form>
      </div>
    </div>

    <!-- Right side - Blue background with decoration -->
    <div class="password-decoration">
      <div class="decoration-shape"></div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const formData = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const errorMessage = ref('')
const successMessage = ref('')
const showOldPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

async function handleSubmit() {
  errorMessage.value = ''
  successMessage.value = ''
  
  // Validation
  if (!formData.value.oldPassword || !formData.value.newPassword || !formData.value.confirmPassword) {
    errorMessage.value = 'Semua field harus diisi'
    return
  }
  
  // Validate new password length
  if (formData.value.newPassword.length < 10 || formData.value.newPassword.length > 32) {
    errorMessage.value = 'Password baru harus antara 10-32 karakter'
    return
  }
  
  // Check if new password and confirm password match
  if (formData.value.newPassword !== formData.value.confirmPassword) {
    errorMessage.value = 'Password baru dan konfirmasi password tidak cocok'
    return
  }

  // TODO: Implement password change
  successMessage.value = 'Password berhasil diubah'
  
  // Clear form
  formData.value.oldPassword = ''
  formData.value.newPassword = ''
  formData.value.confirmPassword = ''
  
  // Redirect to owner dashboard after 1.5 seconds
  setTimeout(() => {
    router.push('/owner/dashboard')
  }, 1500)
}
</script>

<style scoped>
.change-password-page {
  display: flex;
  min-height: 100vh;
}

/* Left Side - Form */
.password-form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
}

.password-form-section::before {
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
}

.form-title {
  font-family: 'Inter', sans-serif;
  font-size: 18px;
  font-weight: 500;
  color: #1678F3;
  margin-bottom: 30px;
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
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  color: #333333;
  margin-bottom: 8px;
  font-weight: 400;
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
  padding: 10px 50px 10px 40px;
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

.toggle-password {
  position: absolute;
  right: 15px;
  background: none;
  border: none;
  color: #999999;
  cursor: pointer;
  padding: 5px;
  font-size: 16px;
}

.toggle-password:hover {
  color: #1678F3;
}

.save-button {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 4px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  background: #1678F3;
  color: white;
  margin-top: 10px;
}

.save-button:hover {
  background: #0d5ec4;
}

/* Right Side - Decoration */
.password-decoration {
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
  .change-password-page {
    flex-direction: column;
  }

  .password-decoration {
    display: none;
  }

  .password-form-section {
    padding: 20px;
  }
}
</style>
