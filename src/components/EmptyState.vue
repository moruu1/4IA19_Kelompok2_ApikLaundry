<template>
  <div class="empty-state">
    <i :class="iconClass"></i>
    <h3>{{ title }}</h3>
    <p>{{ message }}</p>
    <button v-if="actionText" class="btn-action" @click="$emit('action')">
      <i v-if="actionIcon" :class="actionIcon"></i>
      {{ actionText }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  icon: {
    type: String,
    default: 'fas fa-inbox'
  },
  title: {
    type: String,
    default: 'Tidak ada data'
  },
  message: {
    type: String,
    default: ''
  },
  actionText: {
    type: String,
    default: ''
  },
  actionIcon: {
    type: String,
    default: ''
  }
})

defineEmits(['action'])

const iconClass = (icon) => {
  return `${icon} fa-3x`
}
</script>

<script>
export default {
  computed: {
    iconClass() {
      return `${this.icon} fa-3x`
    }
  }
}
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-state i {
  color: #ccc;
  margin-bottom: 20px;
}

.empty-state h3 {
  font-family: 'Inter', sans-serif;
  font-size: 20px;
  font-weight: 600;
  color: #666;
  margin: 0 0 10px 0;
}

.empty-state p {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #999;
  margin: 0 0 24px 0;
  max-width: 400px;
}

.btn-action {
  padding: 12px 24px;
  background: #1678F3;
  color: white;
  border: none;
  border-radius: 8px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background 0.3s;
}

.btn-action:hover {
  background: #0d5ec4;
}

.btn-action i {
  font-size: 16px;
  color: white;
  margin: 0;
}
</style>
