<template>
  <div class="skeleton-container">
    <div v-for="n in rows" :key="n" class="skeleton-row">
      <div 
        v-for="(col, index) in columns" 
        :key="index" 
        class="skeleton-cell"
        :style="{ width: col.width || '100%' }"
      ></div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  rows: {
    type: Number,
    default: 5
  },
  columns: {
    type: Array,
    default: () => [
      { width: '15%' },
      { width: '25%' },
      { width: '20%' },
      { width: '30%' },
      { width: '10%' }
    ]
  }
})
</script>

<style scoped>
.skeleton-container {
  width: 100%;
}

.skeleton-row {
  display: flex;
  gap: 15px;
  padding: 15px 12px;
  border-bottom: 1px solid #f0f0f0;
  align-items: center;
}

.skeleton-cell {
  height: 20px;
  border-radius: 4px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Variations */
.skeleton-row:nth-child(odd) .skeleton-cell {
  animation-delay: 0.1s;
}

.skeleton-row:nth-child(even) .skeleton-cell {
  animation-delay: 0.2s;
}
</style>
