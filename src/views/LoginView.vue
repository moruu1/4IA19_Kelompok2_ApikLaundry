<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  email: '',
  password: ''
})

const errorMessage = ref('')
const showPassword = ref(false)

async function handleLogin() {
  errorMessage.value = ''
  
  if (!formData.value.email || !formData.value.password) {
    errorMessage.value = 'Username dan password harus diisi'
    return
  }

  console.log('Attempting login with:', formData.value.email)
  const result = await authStore.login(formData.value.email, formData.value.password)
  console.log('Login result:', result)
  console.log('Auth role:', authStore.role)
  console.log('Is admin:', authStore.isAdmin)
  
  if (result.success) {
    // Redirect based on role
    if (authStore.isCustomer) {
      console.log('Redirecting to customer home')
      router.push('/customer/home')
    } else if (authStore.isAdmin) {
      console.log('Redirecting to admin dashboard')
      router.push('/admin/dashboard')
    } else if (authStore.isOwner) {
      console.log('Redirecting to owner dashboard')
      router.push('/owner/dashboard')
    }
  } else {
    errorMessage.value = result.error || 'Login gagal'
  }
}
</script>

<template>
  <div class="login-page">
    <!-- Left side - Form -->
    <div class="login-form-section">
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

        <h2 class="form-title">Login Form</h2>
        
        <div class="form-header">
          <span class="account-question">Belum punya akun?</span>
          <router-link to="/register" class="register-link">Daftar</router-link>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <form @submit.prevent="handleLogin">
          <!-- Username or Email Field -->
          <div class="form-group">
            <label class="form-label">Username atau Email</label>
            <div class="input-wrapper">
              <i class="fas fa-user input-icon"></i>
              <input
                v-model="formData.email"
                type="text"
                placeholder="Masukkan username atau email"
                class="form-input"
                required
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
                placeholder="Masukkan kata sandi"
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

          <!-- Login Button -->
          <button 
            type="submit" 
            class="login-button"
            :disabled="authStore.loading"
          >
            <span v-if="!authStore.loading">Login</span>
            <span v-else class="loading-content">
              <i class="fas fa-spinner fa-spin"></i>
              Loading...
            </span>
          </button>
        </form>
      </div>
    </div>

    <!-- Right side - Blue background with decoration -->
    <div class="login-decoration">
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

.login-page {
  display: flex;
  min-height: 100vh;
  background: #E8E8E8;
}

/* Left Side - Form Section */
.login-form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
}

.login-form-section::before {
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
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.back-to-home {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #666666;
  text-decoration: none;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  margin-bottom: 20px;
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
  margin-bottom: 20px;
}

.form-logo {
  width: 120px;
  height: 120px;
  object-fit: contain;
}

.form-title {
  font-family: 'Inter', sans-serif;
  font-size: 18px;
  font-weight: 400;
  color: #999999;
  margin-bottom: 20px;
  text-align: center;
}

.form-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 30px;
}

.account-question {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #666666;
}

.register-link {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #1678F3;
  text-decoration: none;
  font-weight: 500;
}

.register-link:hover {
  text-decoration: underline;
}

.error-message {
  background: #fee;
  border: 1px solid #fcc;
  color: #c33;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 14px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #333333;
  margin-bottom: 8px;
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
  font-size: 16px;
}

.form-input {
  width: 100%;
  padding: 12px 15px 12px 45px;
  border: 1px solid #DDDDDD;
  border-radius: 4px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
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

.login-button {
  width: 180px;
  height: 48px;
  background: #1678F3;
  border: none;
  border-radius: 24px;
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  font-weight: 500;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 10px;
}

.login-button:hover:not(:disabled) {
  background: #0d5ec4;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(22, 120, 243, 0.3);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.loading-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.loading-content i {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Right Side - Decoration */
.login-decoration {
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
  .login-page {
    flex-direction: column !important;
  }
  
  .login-decoration {
    min-height: 200px !important;
    flex: 0 !important;
  }
  
  .decoration-shape {
    width: 300px !important;
    height: 300px !important;
    bottom: -150px !important;
    right: -150px !important;
  }
}

@media (max-width: 768px) {
  .login-page {
    overflow-x: hidden !important;
    max-width: 100vw !important;
  }

  .login-form-section {
    padding: 16px !important;
    width: 100% !important;
    box-sizing: border-box !important;
    overflow-x: hidden !important;
  }
  
  .form-container {
    padding: 24px 16px !important;
    width: 100% !important;
    box-sizing: border-box !important;
  }

  .back-to-home {
    min-width: 48px !important;
    min-height: 48px !important;
    font-size: 15px !important;
    padding: 12px 20px !important;
  }

  .form-logo {
    width: 100px !important;
    height: 100px !important;
    margin-bottom: 16px !important;
  }
  
  .form-title {
    font-size: 22px !important;
    margin-bottom: 24px !important;
  }
  
  .form-label {
    font-size: 14px !important;
    margin-bottom: 6px !important;
  }

  .form-group {
    margin-bottom: 16px !important;
  }
  
  .form-input {
    font-size: 16px !important;
    padding: 14px 14px 14px 50px !important;
    min-height: 48px !important;
    width: 100% !important;
    box-sizing: border-box !important;
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
  }
  
  .login-button {
    width: 100% !important;
    font-size: 16px !important;
    padding: 14px !important;
    min-height: 48px !important;
  }
  
  .register-link,
  .account-question {
    font-size: 14px !important;
  }

  .error-message {
    font-size: 14px !important;
    padding: 12px !important;
    margin-bottom: 16px !important;
  }
}
</style>