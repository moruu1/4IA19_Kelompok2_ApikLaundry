import { ref } from 'vue'

export function useConfirm() {
  const confirm = ref({
    show: false,
    title: 'Konfirmasi',
    message: 'Apakah Anda yakin?',
    confirmText: 'Ya',
    cancelText: 'Batal',
    type: 'danger',
    onConfirm: () => {},
    onCancel: () => {}
  })

  const showConfirm = (options) => {
    confirm.value = {
      show: true,
      title: options.title || 'Konfirmasi',
      message: options.message || 'Apakah Anda yakin?',
      confirmText: options.confirmText || 'Ya',
      cancelText: options.cancelText || 'Batal',
      type: options.type || 'danger',
      onConfirm: options.onConfirm || (() => {}),
      onCancel: options.onCancel || (() => {})
    }
  }

  const hideConfirm = () => {
    confirm.value.show = false
  }

  const handleConfirm = () => {
    if (confirm.value.onConfirm) {
      confirm.value.onConfirm()
    }
    hideConfirm()
  }

  const handleCancel = () => {
    if (confirm.value.onCancel) {
      confirm.value.onCancel()
    }
    hideConfirm()
  }

  return {
    confirm,
    showConfirm,
    hideConfirm,
    handleConfirm,
    handleCancel
  }
}
