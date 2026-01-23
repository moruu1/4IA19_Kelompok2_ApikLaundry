<template>
  <transition name="modal">
    <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
      <div class="confirmation-modal" @click.stop>
        <div class="modal-header">
          <i :class="iconClass"></i>
          <h3>{{ title }}</h3>
        </div>
        <div class="modal-body">
          <p>{{ message }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="cancel">{{ cancelText }}</button>
          <button :class="['btn-confirm', type]" @click="confirm">{{ confirmText }}</button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Konfirmasi'
  },
  message: {
    type: String,
    default: 'Apakah Anda yakin?'
  },
  confirmText: {
    type: String,
    default: 'Ya'
  },
  cancelText: {
    type: String,
    default: 'Batal'
  },
  type: {
    type: String,
    default: 'danger', // danger, warning, info
    validator: (value) => ['danger', 'warning', 'info'].includes(value)
  }
})

const emit = defineEmits(['confirm', 'cancel', 'close'])

const iconClass = computed(() => {
  const icons = {
    danger: 'fas fa-exclamation-circle icon-danger',
    warning: 'fas fa-exclamation-triangle icon-warning',
    info: 'fas fa-info-circle icon-info'
  }
  return icons[props.type]
})

const confirm = () => {
  emit('confirm')
  emit('close')
}

const cancel = () => {
  emit('cancel')
  emit('close')
}

const handleOverlayClick = () => {
  cancel()
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.confirmation-modal {
  background: white;
  border-radius: 16px;
  max-width: 450px;
  width: 100%;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.modal-header {
  padding: 24px 24px 16px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.modal-header i {
  font-size: 32px;
}

.icon-danger {
  color: #dc3545;
}

.icon-warning {
  color: #ffc107;
}

.icon-info {
  color: #1678F3;
}

.modal-header h3 {
  font-family: 'Inter', sans-serif;
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.modal-body {
  padding: 0 24px 24px 24px;
}

.modal-body p {
  font-family: 'Inter', sans-serif;
  font-size: 15px;
  color: #666;
  line-height: 1.6;
  margin: 0;
  padding-left: 44px;
}

.modal-footer {
  padding: 16px 24px;
  background: #f8f9fa;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-cancel,
.btn-confirm {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-cancel {
  background: white;
  color: #666;
  border: 1px solid #ddd;
}

.btn-cancel:hover {
  background: #f8f9fa;
  border-color: #999;
}

.btn-confirm {
  color: white;
}

.btn-confirm.danger {
  background: #dc3545;
}

.btn-confirm.danger:hover {
  background: #c82333;
}

.btn-confirm.warning {
  background: #ffc107;
  color: #333;
}

.btn-confirm.warning:hover {
  background: #e0a800;
}

.btn-confirm.info {
  background: #1678F3;
}

.btn-confirm.info:hover {
  background: #0d5ec4;
}

/* Animation */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s;
}

.modal-enter-active .confirmation-modal,
.modal-leave-active .confirmation-modal {
  transition: transform 0.3s;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .confirmation-modal,
.modal-leave-to .confirmation-modal {
  transform: scale(0.9);
}

@media (max-width: 768px) {
  .modal-footer {
    flex-direction: column-reverse;
  }

  .btn-cancel,
  .btn-confirm {
    width: 100%;
  }
}
</style>
