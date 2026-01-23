<script setup>
import { RouterView } from 'vue-router'
import { onErrorCaptured, ref } from 'vue'

const error = ref(null)

onErrorCaptured((err) => {
  console.error('App Error:', err)
  error.value = err
  return false
})
</script>

<template>
  <div v-if="error" class="min-h-screen bg-red-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-lg shadow-lg p-8 max-w-2xl">
      <h1 class="text-2xl font-bold text-red-600 mb-4">⚠️ Error Occurred</h1>
      <pre class="bg-gray-100 p-4 rounded overflow-auto text-sm">{{ error }}</pre>
      <button 
        @click="error = null; window.location.reload()" 
        class="mt-4 bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
      >
        Reload Page
      </button>
    </div>
  </div>
  <div v-else id="app" class="min-h-screen bg-gray-50">
    <RouterView v-slot="{ Component }">
      <Transition name="fade" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </div>
</template>

<style>
/* Page Transition Animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-to,
.fade-leave-from {
  opacity: 1;
}
</style>

<style scoped>
/* Global app styles */
</style>
