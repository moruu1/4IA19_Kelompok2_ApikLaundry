<template>
  <div v-if="show" class="modal-overlay" @click.self="handleClose">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>Edit Profil</h2>
        <button class="close-btn" @click="handleClose">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="modal-body">
        <form @submit.prevent="handleSave">
          <div class="form-group">
            <label>Nama Lengkap</label>
            <input 
              v-model="formData.name" 
              type="text" 
              placeholder="Masukkan nama lengkap"
              required
            />
          </div>
          
          <div class="form-group">
            <label>Email</label>
            <input 
              v-model="formData.email" 
              type="email" 
              placeholder="Masukkan email"
              required
            />
          </div>
          
          <div class="form-group">
            <label>No. Telepon</label>
            <input 
              v-model="formData.phone" 
              type="tel" 
              placeholder="Masukkan nomor telepon"
              required
            />
          </div>
          
          <!-- Alamat hanya untuk customer -->
          <div v-if="userRole === 'customer'" class="form-group">
            <label>Alamat</label>
            <textarea 
              v-model="formData.address" 
              rows="3" 
              placeholder="Masukkan alamat lengkap"
              required
            ></textarea>
          </div>
          
          <div class="modal-actions">
            <button type="button" @click="handleClose" class="btn-cancel">
              Batal
            </button>
            <button type="submit" class="btn-save">
              <i class="fas fa-save"></i>
              Simpan Perubahan
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
  },
  user: {
    type: Object,
    default: () => ({})
  },
  userRole: {
    type: String,
    default: 'customer'
  }
})

const emit = defineEmits(['close', 'save'])

const formData = ref({
  name: '',
  email: '',
  phone: '',
  address: ''
})

watch(() => props.show, (newVal) => {
  if (newVal && props.user) {
    formData.value = {
      name: props.user.name || '',
      email: props.user.email || '',
      phone: props.user.phone || '',
      address: props.user.address || ''
    }
  }
})

function handleClose() {
  emit('close')
}

function handleSave() {
  emit('save', formData.value)
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
  max-width: 600px;
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

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #1678F3;
  box-shadow: 0 0 0 3px rgba(22, 120, 243, 0.1);
}

.form-group textarea {
  resize: vertical;
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

.btn-save:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(22, 120, 243, 0.4);
}

.btn-save:active {
  transform: translateY(0);
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

  .form-group input,
  .form-group textarea {
    font-size: 16px !important;
    padding: 12px !important;
    min-height: 48px !important;
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
}
</style>
