<template>
  <transition name="toast">
    <div v-if="visible" :class="['toast-notification', type]">
      <i :class="iconClass"></i>
      <span class="toast-message">{{ message }}</span>
      <button class="toast-close" @click="close">
        <i class="fas fa-times"></i>
      </button>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  message: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'success', // success, error, warning, info
    validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
  },
  duration: {
    type: Number,
    default: 3000
  },
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const visible = ref(props.show)
let timeoutId = null

const iconClass = computed(() => {
  const icons = {
    success: 'fas fa-check-circle',
    error: 'fas fa-exclamation-circle',
    warning: 'fas fa-exclamation-triangle',
    info: 'fas fa-info-circle'
  }
  return icons[props.type]
})

watch(() => props.show, (newVal) => {
  visible.value = newVal
  if (newVal && props.duration > 0) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => {
      close()
    }, props.duration)
  }
})

const close = () => {
  visible.value = false
  emit('close')
}
</script>

<style scoped>
.toast-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  min-width: 300px;
  max-width: 500px;
  padding: 16px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 9999;
  font-family: 'Inter', sans-serif;
  border-left: 4px solid;
}

.toast-notification.success {
  border-left-color: #28a745;
}

.toast-notification.success i:first-child {
  color: #28a745;
}

.toast-notification.error {
  border-left-color: #dc3545;
}

.toast-notification.error i:first-child {
  color: #dc3545;
}

.toast-notification.warning {
  border-left-color: #ffc107;
}

.toast-notification.warning i:first-child {
  color: #ffc107;
}

.toast-notification.info {
  border-left-color: #1678F3;
}

.toast-notification.info i:first-child {
  color: #1678F3;
}

.toast-notification i:first-child {
  font-size: 20px;
  flex-shrink: 0;
}

.toast-message {
  flex: 1;
  font-size: 14px;
  color: #333;
  line-height: 1.5;
}

.toast-close {
  background: none;
  border: none;
  color: #999;
  font-size: 16px;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.3s;
  flex-shrink: 0;
}

.toast-close:hover {
  color: #333;
}

/* Animation */
.toast-enter-active {
  animation: toast-in 0.3s ease-out;
}

.toast-leave-active {
  animation: toast-out 0.3s ease-in;
}

@keyframes toast-in {
  from {
    transform: translateX(400px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes toast-out {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(400px);
    opacity: 0;
  }
}

@media (max-width: 768px) {
  .toast-notification {
    top: 10px;
    right: 10px;
    left: 10px;
    min-width: auto;
    max-width: none;
  }

  @keyframes toast-in {
    from {
      transform: translateY(-100px);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  @keyframes toast-out {
    from {
      transform: translateY(0);
      opacity: 1;
    }
    to {
      transform: translateY(-100px);
      opacity: 0;
    }
  }
}
</style>
