<template>
  <div v-if="show" class="modal-overlay" @click.self="handleClose">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>Ubah Password</h2>
        <button class="close-btn" @click="handleClose">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="modal-body">
        <form @submit.prevent="handleSave">
          <div class="form-group">
            <label>Password Lama</label>
            <div class="password-input">
              <input 
                v-model="formData.currentPassword"
                :type="showCurrentPassword ? 'text' : 'password'"
                placeholder="Masukkan password lama"
                required
              />
              <button 
                type="button" 
                @click="showCurrentPassword = !showCurrentPassword"
                class="toggle-password"
              >
                <i :class="showCurrentPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
          </div>
          
          <div class="form-group">
            <label>Password Baru</label>
            <div class="password-input">
              <input 
                v-model="formData.newPassword"
                :type="showNewPassword ? 'text' : 'password'"
                placeholder="Masukkan password baru"
                required
                minlength="6"
              />
              <button 
                type="button" 
                @click="showNewPassword = !showNewPassword"
                class="toggle-password"
              >
                <i :class="showNewPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
            <small class="hint">Minimal 6 karakter</small>
          </div>
          
          <div class="form-group">
            <label>Konfirmasi Password Baru</label>
            <div class="password-input">
              <input 
                v-model="formData.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                placeholder="Konfirmasi password baru"
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
            <small v-if="formData.confirmPassword && formData.newPassword !== formData.confirmPassword" class="error">
              Password tidak cocok
            </small>
          </div>
          
          <div class="modal-actions">
            <button type="button" @click="handleClose" class="btn-cancel">
              Batal
            </button>
            <button 
              type="submit" 
              class="btn-save"
              :disabled="formData.newPassword !== formData.confirmPassword"
            >
              <i class="fas fa-key"></i>
              Ubah Password
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'save'])

const formData = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

watch(() => props.show, (newVal) => {
  if (newVal) {
    // Reset form when modal opens
    formData.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
    showCurrentPassword.value = false
    showNewPassword.value = false
    showConfirmPassword.value = false
  }
})

function handleClose() {
  emit('close')
}

function handleSave() {
  if (formData.value.newPassword !== formData.value.confirmPassword) {
    return
  }
  emit('save', {
    currentPassword: formData.value.currentPassword,
    newPassword: formData.value.newPassword
  })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 30px;
  border-bottom: 1px solid #E0E0E0;
}

.modal-header h2 {
  font-family: 'Inter', sans-serif;
  font-size: 22px;
  font-weight: 700;
  color: #1678F3;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #F5F5F5;
  color: #333;
}

.modal-body {
  padding: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #555;
  margin-bottom: 8px;
}

.password-input {
  position: relative;
}

.password-input input {
  width: 100%;
  padding: 12px 45px 12px 16px;
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
  transition: all 0.3s ease;
}

.password-input input:focus {
  outline: none;
  border-color: #1678F3;
  box-shadow: 0 0 0 3px rgba(22, 120, 243, 0.1);
}

.toggle-password {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  font-size: 16px;
  padding: 8px;
  transition: color 0.3s ease;
}

.toggle-password:hover {
  color: #1678F3;
}

.hint {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: #999;
}

.error {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: #EF5350;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 30px;
}

.btn-cancel,
.btn-save {
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel {
  background: #F5F5F5;
  color: #666;
}

.btn-cancel:hover {
  background: #E0E0E0;
}

.btn-save {
  background: linear-gradient(135deg, #1678F3 0%, #1565C0 100%);
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 2px 8px rgba(22, 120, 243, 0.2);
}

.btn-save:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(22, 120, 243, 0.4);
}

.btn-save:active:not(:disabled) {
  transform: translateY(0);
}

.btn-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Mobile Responsive */
@media (max-width: 640px) {
  .modal-content {
    width: 95% !important;
    max-width: 95% !important;
    margin: 10px !important;
  }

  .modal-header {
    padding: 20px !important;
  }

  .modal-header h2 {
    font-size: 20px !important;
  }

  .close-btn {
    width: 40px !important;
    height: 40px !important;
    font-size: 20px !important;
  }

  .modal-body {
    padding: 20px !important;
  }

  .form-group label {
    font-size: 14px !important;
  }

  .password-input input {
    font-size: 16px !important;
    padding: 12px 45px 12px 12px !important;
    min-height: 48px !important;
  }

  .toggle-password {
    width: 44px !important;
    height: 44px !important;
    font-size: 16px !important;
  }

  .modal-actions {
    flex-direction: column !important;
    gap: 10px !important;
  }

  .btn-cancel,
  .btn-save {
    width: 100% !important;
    min-height: 48px !important;
    font-size: 16px !important;
    padding: 14px !important;
  }

  .error-message {
    font-size: 13px !important;
    padding: 10px !important;
  }
}
</style>
