import { ref } from 'vue'

export function useToast() {
  const toast = ref({
    show: false,
    message: '',
    type: 'success'
  })

  const showToast = (message, type = 'success') => {
    toast.value = {
      show: true,
      message,
      type
    }
  }

  const hideToast = () => {
    toast.value.show = false
  }

  const showSuccess = (message) => showToast(message, 'success')
  const showError = (message) => showToast(message, 'error')
  const showWarning = (message) => showToast(message, 'warning')
  const showInfo = (message) => showToast(message, 'info')

  return {
    toast,
    showToast,
    hideToast,
    showSuccess,
    showError,
    showWarning,
    showInfo
  }
}
