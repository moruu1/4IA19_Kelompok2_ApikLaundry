<script setup>
import { computed } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    required: true,
    // Format: [{ label: 'Home', path: '/home' }, { label: 'Orders' }]
  }
})
</script>

<template>
  <nav class="breadcrumbs">
    <div class="breadcrumb-items">
      <template v-for="(item, index) in items" :key="index">
        <router-link 
          v-if="item.path" 
          :to="item.path" 
          class="breadcrumb-item breadcrumb-link"
        >
          {{ item.label }}
        </router-link>
        <span v-else class="breadcrumb-item breadcrumb-current">
          {{ item.label }}
        </span>
        <span v-if="index < items.length - 1" class="breadcrumb-separator">
          <i class="fas fa-chevron-right"></i>
        </span>
      </template>
    </div>
  </nav>
</template>

<style scoped>
.breadcrumbs {
  margin-bottom: 20px;
}

.breadcrumb-items {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.breadcrumb-item {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #666;
  text-decoration: none;
  transition: all 0.3s;
}

.breadcrumb-link:hover {
  color: #1678F3;
}

.breadcrumb-current {
  color: #1678F3;
  font-weight: 600;
}

.breadcrumb-separator {
  color: #999;
  font-size: 10px;
}
</style>
