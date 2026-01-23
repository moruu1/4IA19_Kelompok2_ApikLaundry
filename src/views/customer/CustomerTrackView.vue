<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/authStore'
import { useTransactionStore } from '../../stores/transactionStore'
import { supabase } from '../../lib/supabase'
import Breadcrumbs from '../../components/Breadcrumbs.vue'
import ToastNotification from '../../components/ToastNotification.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import ProfileModal from '../../components/ProfileModal.vue'
import ChangePasswordModal from '../../components/ChangePasswordModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const transactionStore = useTransactionStore()

const currentCustomerId = ref(null)

// Fetch transactions on mount
onMounted(async () => {
  loading.value = true
  
  // Get customer ID from user_id
  const { data, error } = await supabase
    .from('customers')
    .select('id_customer')
    .eq('user_id', authStore.user?.id)
    .single()
  
  if (!error && data) {
    currentCustomerId.value = data.id_customer
  }
  
  await transactionStore.fetchTransactions()
  loading.value = false
})

// Search and filter
const searchQuery = ref('')
const searchedOrder = ref(null)

// Format date to readable format
function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  const day = date.getDate().toString().padStart(2, '0')
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const year = date.getFullYear()
  return `${day}/${month}/${year}`
}

// Get order stages based on status
const orderStages = computed(() => {
  if (!searchedOrder.value) return []
  
  const status = searchedOrder.value.status_pesanan?.toLowerCase()
  
  return [
    {
      icon: '📝',
      title: 'Pesanan Diterima',
      description: `Pesanan diterima pada ${formatDate(searchedOrder.value.tanggal_masuk)}`,
      completed: true
    },
    {
      icon: '🧺',
      title: 'Sedang Diproses',
      description: 'Pesanan Anda sedang dikerjakan',
      completed: status === 'diproses' || status === 'selesai' || status === 'diambil'
    },
    {
      icon: '✅',
      title: 'Selesai',
      description: searchedOrder.value.tanggal_selesai 
        ? `Selesai pada ${formatDate(searchedOrder.value.tanggal_selesai)}`
        : 'Pesanan sedang dalam proses penyelesaian',
      completed: status === 'selesai' || status === 'diambil'
    },
    {
      icon: '🚚',
      title: 'Siap Diambil',
      description: status === 'diambil' 
        ? 'Pesanan sudah diambil'
        : status === 'selesai'
        ? 'Pesanan siap untuk diambil'
        : 'Menunggu proses selesai',
      completed: status === 'selesai' || status === 'diambil'
    }
  ]
})

async function searchOrder() {
  if (!searchQuery.value) {
    toast.value = {
      show: true,
      message: 'Masukkan nomor nota untuk melacak pesanan',
      type: 'warning'
    }
    return
  }
  
  loading.value = true
  
  // Fetch latest data from database
  await transactionStore.fetchTransactions()
  
  // Search for order by nomor_nota and customer_id
  const order = transactionStore.transactions.find(
    t => t.nomor_nota?.toLowerCase() === searchQuery.value.toLowerCase() &&
         t.customer_id === currentCustomerId.value
  )
  
  if (order) {
    searchedOrder.value = order
  } else {
    searchedOrder.value = null
    toast.value = {
      show: true,
      message: 'Pesanan tidak ditemukan atau bukan milik Anda',
      type: 'error'
    }
  }
  
  loading.value = false
}

const breadcrumbItems = ref([
  { label: 'Home', path: '/customer/home' },
  { label: 'Lacak Pesanan' }
])

const showProfileMenu = ref(false)
const showProfileModal = ref(false)
const showPasswordModal = ref(false)

const toast = ref({
  show: false,
  message: '',
  type: 'success'
})
const loading = ref(false)

const toggleProfileMenu = () => {
  showProfileMenu.value = !showProfileMenu.value
}

const openProfileModal = () => {
  showProfileMenu.value = false
  showProfileModal.value = true
}

const openPasswordModal = () => {
  showProfileMenu.value = false
  showPasswordModal.value = true
}

async function handleProfileSave(profileData) {
  loading.value = true
  try {
    const result = await authStore.updateProfile(profileData)
    if (result.success) {
      showProfileModal.value = false
      toast.value = {
        show: true,
        message: 'Profil berhasil diperbarui!',
        type: 'success'
      }
    } else {
      toast.value = {
        show: true,
        message: result.error || 'Gagal memperbarui profil',
        type: 'error'
      }
    }
  } catch (error) {
    console.error('Error updating profile:', error)
    toast.value = {
      show: true,
      message: 'Terjadi kesalahan saat memperbarui profil',
      type: 'error'
    }
  } finally {
    loading.value = false
  }
}

async function handlePasswordSave(passwordData) {
  loading.value = true
  try {
    const result = await authStore.changePassword(
      passwordData.currentPassword,
      passwordData.newPassword
    )
    if (result.success) {
      showPasswordModal.value = false
      toast.value = {
        show: true,
        message: 'Password berhasil diubah!',
        type: 'success'
      }
    } else {
      toast.value = {
        show: true,
        message: result.error || 'Gagal mengubah password',
        type: 'error'
      }
    }
  } catch (error) {
    console.error('Error changing password:', error)
    toast.value = {
      show: true,
      message: 'Terjadi kesalahan saat mengubah password',
      type: 'error'
    }
  } finally {
    loading.value = false
  }
}

async function handleLogout() {
  await authStore.logout()
  router.replace('/login')
}

</script>

<template>
  <div class="customer-track">
    <!-- Sidebar -->
    <div class="sidebar">
      <router-link to="/customer/home" class="sidebar-icon">
        <i class="fas fa-home"></i>
      </router-link>
      
      <router-link to="/customer/services" class="sidebar-icon">
        <i class="fas fa-concierge-bell"></i>
      </router-link>
      
      <router-link to="/customer/track" class="sidebar-icon active">
        <i class="fas fa-map-marker-alt"></i>
      </router-link>
      
      <router-link to="/customer/orders" class="sidebar-icon">
        <i class="fas fa-history"></i>
      </router-link>
      
      <!-- Logout Button - Bottom -->
      <div class="logout-button" @click="handleLogout">
        <i class="fas fa-sign-out-alt"></i>
      </div>
    </div>

    <div class="customer-track-page">
      <!-- Breadcrumbs -->
      <Breadcrumbs :items="breadcrumbItems" />
      
      <!-- Header with User Profile -->
      <div class="header">
        <h1 class="page-title">Lacak Pesanan</h1>
        
        <div class="user-profile" @click="toggleProfileMenu">
          <div class="user-avatar">
            <i class="fas fa-user"></i>
          </div>
          <div class="user-info">
            <p class="user-name">{{ authStore.user?.name || 'Steven' }}</p>
          </div>
          <i class="fas fa-chevron-down dropdown-icon"></i>
          
          <!-- Dropdown Menu -->
          <div v-if="showProfileMenu" class="profile-dropdown">
            <button @click="openProfileModal" class="dropdown-item">
              <i class="fas fa-user-edit"></i>
              <span>Edit Profil</span>
            </button>
            <button @click="openPasswordModal" class="dropdown-item">
              <i class="fas fa-key"></i>
              <span>Ubah Password</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="track-content">
        <!-- Left Section - Title and Search -->
        <div class="track-title-section">
          <h2 class="track-main-title">Lacak Pesanan</h2>
          <div class="search-container">
            <input 
              v-model="searchQuery"
              type="text" 
              class="search-input"
              placeholder="Masukkan nomor nota pesanan"
              @keyup.enter="searchOrder"
            />
            <button @click="searchOrder" class="search-button">
              <i class="fas fa-search"></i>
              Lacak
            </button>
          </div>
        </div>

        <!-- Right Section - Timeline -->
        <div class="track-timeline-section">
          <!-- Show message if no order searched -->
          <div v-if="!searchedOrder" class="no-order-message">
            <i class="fas fa-search"></i>
            <p>Masukkan nomor nota untuk melacak pesanan</p>
          </div>
          
          <!-- Show timeline if order found -->
          <div v-else class="timeline">
            <div 
              v-for="(stage, index) in orderStages" 
              :key="index"
              class="timeline-item"
            >
              <!-- Timeline Line -->
              <div class="timeline-line-container">
                <div class="timeline-dot" :class="{ completed: stage.completed }">
                  <i v-if="stage.completed" class="fas fa-check"></i>
                </div>
                <div 
                  v-if="index < orderStages.length - 1" 
                  class="timeline-line"
                  :class="{ completed: stage.completed }"
                ></div>
              </div>

              <!-- Timeline Content -->
              <div class="timeline-card">
                <div class="card-icon">{{ stage.icon }}</div>
                <div class="card-content">
                  <h3 class="card-title">{{ stage.title }}</h3>
                  <p class="card-description">{{ stage.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <ToastNotification 
      :show="toast.show" 
      :message="toast.message" 
      :type="toast.type"
      @close="toast.show = false" 
    />

    <!-- Loading Spinner -->
    <LoadingSpinner :show="loading" message="Memproses..." />

    <!-- Profile Modal -->
    <ProfileModal 
      :show="showProfileModal"
      :user="authStore.user"
      :userRole="authStore.role"
      @close="showProfileModal = false"
      @save="handleProfileSave"
    />

    <!-- Change Password Modal -->
    <ChangePasswordModal 
      :show="showPasswordModal"
      @close="showPasswordModal = false"
      @save="handlePasswordSave"
    />
  </div>
</template>

<style scoped>
.customer-track {
  display: flex;
  min-height: 100vh;
  background: #E8E8E8;
}

/* Sidebar */
.sidebar {
  width: 80px;
  height: 100vh;
  background: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 0;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
  position: fixed;
  left: 0;
  top: 0;
}

.sidebar-icon {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 12px;
  transition: all 0.3s;
  color: #1678F3;
  font-size: 24px;
  margin-bottom: 20px;
  text-decoration: none;
}

.sidebar-icon.active {
  background: rgba(22, 120, 243, 0.15);
}

.sidebar-icon:hover {
  background: rgba(22, 120, 243, 0.1);
}

.logout-button {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 12px;
  transition: all 0.3s;
  color: #1678F3;
  font-size: 20px;
  margin-top: auto;
  position: absolute;
  bottom: 30px;
}

.logout-button:hover {
  background: rgba(22, 120, 243, 0.1);
}

.customer-track-page {
  flex: 1;
  margin-left: 80px;
  padding: 30px;
  min-height: 100vh;
  background: linear-gradient(135deg, #E8F4FD 0%, #F5F5F5 100%);
  position: relative;
}

.customer-track-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: radial-gradient(circle, #00000005 1px, transparent 1px);
  background-size: 20px 20px;
  pointer-events: none;
}

/* Header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  gap: 16px;
}

.page-title {
  font-family: 'Inter', sans-serif;
  font-size: 32px;
  font-weight: 700;
  color: #1678F3;
  margin: 0;
  flex: 1;
}

.user-profile {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 12px;
  transition: background 0.3s;
  flex-shrink: 0;
}

.user-profile:hover {
  background: rgba(22, 120, 243, 0.05);
}

.user-avatar {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #1678F3 0%, #6BB6FF 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  font-weight: 600;
  color: #1678F3;
  margin: 0;
}

.dropdown-icon {
  font-size: 12px;
  color: #1678F3;
  margin-left: 5px;
  transition: transform 0.3s;
}

.user-profile:hover .dropdown-icon {
  transform: rotate(180deg);
}

.profile-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 10px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-width: 200px;
  overflow: hidden;
  z-index: 1000;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px 20px;
  cursor: pointer;
  transition: background 0.2s;
  text-decoration: none;
  color: #333333;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
}

.dropdown-item:hover {
  background: #F5F5F5;
}

.dropdown-item i {
  font-size: 16px;
  width: 20px;
  text-align: center;
}

/* Track Content */
.track-content {
  display: flex;
  gap: 60px;
  align-items: flex-start;
  padding: 40px 60px;
}

.track-title-section {
  flex: 0 0 auto;
}

.track-main-title {
  font-family: 'Inter', sans-serif;
  font-size: 64px;
  font-weight: 700;
  color: #1678F3;
  margin: 0 0 30px 0;
  line-height: 1.1;
}

.search-container {
  display: flex;
  gap: 15px;
  align-items: center;
}

.search-input {
  flex: 1;
  max-width: 400px;
  padding: 12px 20px;
  border: 2px solid #E0E0E0;
  border-radius: 12px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: #1678F3;
}

.search-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #1678F3;
  color: white;
  border: none;
  border-radius: 12px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.search-button:hover {
  background: #0D5BBF;
}

.search-button i {
  font-size: 16px;
}

.track-timeline-section {
  flex: 1;
  max-width: 600px;
}

.no-order-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.no-order-message i {
  font-size: 48px;
  color: #1678F3;
  margin-bottom: 20px;
}

.no-order-message p {
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  color: #666666;
  margin: 0;
  text-align: center;
}

/* Timeline */
.timeline {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.timeline-item {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.timeline-line-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.timeline-dot {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #E0E0E0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  position: relative;
  z-index: 2;
  flex-shrink: 0;
}

.timeline-dot.completed {
  background: #4CAF50;
}

.timeline-line {
  width: 3px;
  height: 80px;
  background: #E0E0E0;
  margin-top: 5px;
}

.timeline-line.completed {
  background: #4CAF50;
}

.timeline-card {
  flex: 1;
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
}

.timeline-card:hover {
  transform: translateX(8px);
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.15);
}

.card-icon {
  font-size: 40px;
  flex-shrink: 0;
}

.card-content {
  flex: 1;
}

.card-title {
  font-family: 'Inter', sans-serif;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 5px 0;
}

.card-description {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .sidebar {
    width: 100% !important;
    height: 70px !important;
    padding: 0 !important;
    flex-direction: row !important;
    justify-content: space-around !important;
    align-items: center !important;
    position: fixed !important;
    bottom: 0 !important;
    top: auto !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 1000 !important;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1) !important;
  }
  
  .sidebar-icon {
    width: 48px !important;
    height: 48px !important;
    font-size: 22px !important;
    margin: 0 !important;
  }

  .logout-button {
    position: relative !important;
    bottom: auto !important;
    margin: 0 !important;
    width: 48px !important;
    height: 48px !important;
  }

  .main-content {
    margin-left: 0 !important;
    padding: 8px !important;
  }

  .breadcrumbs {
    display: none !important;
  }

  .customer-track-page {
    margin-left: 0 !important;
    margin-bottom: 85px !important;
    padding: 8px !important;
    width: 100% !important;
    max-width: 100vw !important;
    overflow-x: hidden !important;
    box-sizing: border-box !important;
  }

  .header {
    display: flex !important;
    flex-direction: row !important;
    justify-content: space-between !important;
    align-items: center !important;
    gap: 8px !important;
    margin-bottom: 16px !important;
  }

  .page-title {
    font-size: 20px !important;
    flex: 1 !important;
  }

  .user-profile {
    position: relative !important;
    width: auto !important;
    padding: 4px 8px !important;
    margin: 0 !important;
    flex-shrink: 0 !important;
    top: auto !important;
    right: auto !important;
  }

  .user-avatar {
    width: 32px !important;
    height: 32px !important;
    font-size: 14px !important;
  }

  .user-info {
    display: none !important;
  }

  .dropdown-icon {
    font-size: 10px !important;
  }

  .track-content {
    flex-direction: column !important;
    padding: 12px !important;
    gap: 20px !important;
  }

  .search-input {
    width: 100% !important;
    box-sizing: border-box !important;
    font-size: 16px !important;
    min-height: 48px !important;
    padding: 12px 16px !important;
  }

  .search-button {
    min-height: 48px !important;
    padding: 12px 24px !important;
    font-size: 15px !important;
  }

  .track-main-title {
    font-size: 32px !important;
    margin-bottom: 16px !important;
  }

  .track-timeline-section {
    max-width: 100% !important;
  }

  .timeline-step {
    padding: 12px !important;
  }

  .step-title {
    font-size: 15px !important;
  }

  .step-date {
    font-size: 13px !important;
  }
}
</style>
