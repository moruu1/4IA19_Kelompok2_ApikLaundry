<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  username: '',
  email: '',
  name: '',
  address: '',
  phone: '',
  password: '',
  role: 'customer' // default role
})

const errorMessage = ref('')
const showPassword = ref(false)

async function handleRegister() {
  errorMessage.value = ''
  
  // Validation
  if (!formData.value.username || !formData.value.email || !formData.value.name || !formData.value.password) {
    errorMessage.value = 'Username, email, nama, dan password harus diisi'
    return
  }
  
  // Validate email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(formData.value.email)) {
    errorMessage.value = 'Format email tidak valid'
    return
  }
  
  if (formData.value.password.length < 10 || formData.value.password.length > 32) {
    errorMessage.value = 'Password harus antara 10-32 karakter'
    return
  }

  const result = await authStore.register({
    username: formData.value.username,
    email: formData.value.email,
    name: formData.value.name,
    password: formData.value.password,
    phone: formData.value.phone,
    address: formData.value.address,
    role: formData.value.role
  })
  
  if (result.success) {
    // Redirect based on role
    if (authStore.isCustomer) {
      router.push('/customer/home')
    } else if (authStore.isAdmin) {
      router.push('/admin/dashboard')
    } else if (authStore.isOwner) {
      router.push('/owner/dashboard')
    }
  } else {
    errorMessage.value = result.error || 'Registrasi gagal'
  }
}
</script>

<template>
  <div class="register-page">
    <!-- Left side - Form -->
    <div class="register-form-section">
      <div class="form-container">
        <!-- Back to Home Button -->
        <router-link to="/" class="back-to-home">
          <i class="fas fa-arrow-left"></i>
          <span>Kembali ke Home</span>
        </router-link>

        <!-- Logo -->
        <div class="logo-section">
          <img src="@/assets/images/logo_apik.png" alt="Apik Laundry" class="form-logo">
        </div>

        <h2 class="form-title">Register Form</h2>
        
        <div class="form-header">
          <span class="account-question">Sudah punya akun?</span>
          <router-link to="/login" class="login-link">Masuk</router-link>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <form @submit.prevent="handleRegister">
          <!-- Username Field -->
          <div class="form-group">
            <label class="form-label">Username</label>
            <div class="input-wrapper">
              <i class="fas fa-user input-icon"></i>
              <input
                v-model="formData.username"
                type="text"
                placeholder="Masukkan username"
                class="form-input"
                required
              />
            </div>
          </div>

          <!-- Email Field -->
          <div class="form-group">
            <label class="form-label">Email</label>
            <div class="input-wrapper">
              <i class="fas fa-envelope input-icon"></i>
              <input
                v-model="formData.email"
                type="email"
                placeholder="Masukkan email"
                class="form-input"
                required
              />
            </div>
          </div>

          <!-- Name Field -->
          <div class="form-group">
            <label class="form-label">Nama Lengkap</label>
            <div class="input-wrapper">
              <i class="fas fa-id-card input-icon"></i>
              <input
                v-model="formData.name"
                type="text"
                placeholder="Masukkan nama lengkap"
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
                placeholder="Masukkan alamat lengkap"
                class="form-input"
              />
            </div>
          </div>

          <!-- Phone Number Field -->
          <div class="form-group">
            <label class="form-label">Nomor Telepon</label>
            <div class="input-wrapper">
              <i class="fas fa-phone input-icon"></i>
              <input
                v-model="formData.phone"
                type="tel"
                placeholder="Masukkan nomor telepon"
                class="form-input"
              />
            </div>
          </div>

          <!-- Password Field -->
          <div class="form-group">
            <label class="form-label">Kata Sandi</label>
            <div class="input-wrapper">
              <i class="fas fa-lock input-icon"></i>
              <input
                v-model="formData.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Masukkan kata sandi (10-32 karakter)"
                class="form-input"
                required
              />
              <button 
                type="button" 
                @click="showPassword = !showPassword"
                class="toggle-password"
              >
                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
          </div>

          <!-- Register Button -->
          <button 
            type="submit" 
            class="register-button"
            :disabled="authStore.loading"
          >
            {{ authStore.loading ? 'Loading...' : 'Daftar' }}
          </button>
        </form>
      </div>
    </div>

    <!-- Right side - Blue background with decoration -->
    <div class="register-decoration">
      <div class="decoration-shape"></div>
    </div>
  </div>
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.register-page {
  display: flex;
  min-height: 100vh;
  background: #E8E8E8;
}

/* Left Side - Form Section */
.register-form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
}

.register-form-section::before {
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
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  max-height: 90vh;
  overflow-y: auto;
}

.back-to-home {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #666666;
  text-decoration: none;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  margin-bottom: 15px;
  transition: color 0.3s;
}

.back-to-home:hover {
  color: #1678F3;
}

.back-to-home i {
  font-size: 14px;
}

.logo-section {
  display: flex;
  justify-content: center;
  margin-bottom: 15px;
}

.form-logo {
  width: 100px;
  height: 100px;
  object-fit: contain;
}

.form-title {
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  font-weight: 400;
  color: #999999;
  margin-bottom: 15px;
  text-align: center;
}

.form-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.account-question {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #666666;
}

.login-link {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #1678F3;
  text-decoration: none;
  font-weight: 500;
}

.login-link:hover {
  text-decoration: underline;
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

.register-button {
  width: 150px;
  height: 42px;
  background: #1678F3;
  border: none;
  border-radius: 21px;
  font-family: 'Inter', sans-serif;
  font-size: 15px;
  font-weight: 500;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 8px;
}

.register-button:hover:not(:disabled) {
  background: #0d5ec4;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(22, 120, 243, 0.3);
}

.register-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Right Side - Decoration */
.register-decoration {
  flex: 1;
  background: #1678F3;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
  border-radius: 60px 0 0 60px;
}

.decoration-shape {
  width: 500px;
  height: 500px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  position: absolute;
  bottom: -250px;
  right: -250px;
}

/* Responsive */
@media (max-width: 968px) {
  .register-page {
    flex-direction: column !important;
  }
  
  .register-decoration {
    min-height: 200px !important;
    flex: 0 !important;
  }
  
  .decoration-shape {
    width: 300px !important;
    height: 300px !important;
    bottom: -150px !important;
    right: -150px !important;
  }

  .form-title {
    font-size: 26px !important;
  }
}

@media (max-width: 768px) {
  .register-page {
    overflow-x: hidden !important;
    max-width: 100vw !important;
  }

  .register-form-section {
    padding: 16px !important;
    width: 100% !important;
    box-sizing: border-box !important;
    overflow-x: hidden !important;
    max-height: 100vh !important;
    overflow-y: auto !important;
  }
  
  .form-container {
    padding: 24px 16px !important;
    width: 100% !important;
    box-sizing: border-box !important;
  }

  .back-to-home {
    font-size: 14px !important;
    padding: 10px 18px !important;
    min-width: 48px !important;
    min-height: 44px !important;
  }

  .form-logo {
    width: 90px !important;
    height: 90px !important;
    margin-bottom: 16px !important;
  }

  .form-title {
    font-size: 22px !important;
    margin-bottom: 20px !important;
  }

  .account-question,
  .login-link {
    font-size: 14px !important;
  }

  .form-label {
    font-size: 14px !important;
    margin-bottom: 6px !important;
  }

  .form-group {
    margin-bottom: 14px !important;
  }

  .form-input {
    font-size: 16px !important;
    padding: 12px 16px 12px 50px !important;
    min-height: 48px !important;
    width: 100% !important;
    box-sizing: border-box !important;
  }

  .form-input[type="password"],
  .form-input[type="text"] {
    padding-right: 52px !important;
  }

  .input-icon {
    width: 48px !important;
    height: 48px !important;
    font-size: 18px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    left: 0 !important;
  }

  .toggle-password {
    width: 48px !important;
    height: 48px !important;
    font-size: 18px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    right: 0 !important;
  }

  .register-button {
    width: 100% !important;
    min-height: 48px !important;
    font-size: 16px !important;
    padding: 14px !important;
  }

  .error-message {
    font-size: 13px !important;
    padding: 12px !important;
    margin-bottom: 14px !important;
  }
}

</style>