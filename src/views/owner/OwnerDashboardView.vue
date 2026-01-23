<template>
  <div class="dashboard-container">
    <!-- Sidebar -->
    <div class="sidebar">
      <!-- Grid Icon - Center -->
      <router-link to="/owner/dashboard" class="sidebar-icon menu-icon active">
        <i class="fas fa-th"></i>
      </router-link>

      <router-link to="/owner/reports" class="sidebar-icon">
        <i class="fas fa-file-invoice-dollar"></i>
      </router-link>

      <router-link to="/owner/inventory" class="sidebar-icon">
        <i class="fas fa-boxes"></i>
      </router-link>

      <router-link to="/owner/prediction" class="sidebar-icon">
        <i class="fas fa-chart-line"></i>
      </router-link>
      
      <!-- Logout Button - Bottom -->
      <div class="logout-button" @click="handleLogout">
        <i class="fas fa-sign-out-alt"></i>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="main-area">
      <!-- Breadcrumbs -->
      <Breadcrumbs :items="breadcrumbItems" />
      
      <!-- Header -->
      <div class="dashboard-header">
        <h1 class="page-title">Dashboard</h1>
        
        <!-- User Profile (Top Right) -->
        <div class="user-profile" @click="toggleProfileMenu">
          <div class="user-avatar">
            <i class="fas fa-user"></i>
          </div>
          <div class="user-info">
            <p class="user-name">{{ authStore.user?.name || 'Owner' }}</p>
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
      <div class="main-content">
        <!-- Info Cards -->
        <div class="info-cards">
          <div class="info-card">
            <div class="card-icon">
              <i class="fas fa-money-bill-wave"></i>
            </div>
            <div class="card-content">
              <p class="card-label">Total Pendapatan</p>
              <p class="card-value">Rp {{ stats.totalPendapatan.toLocaleString('id-ID') }}</p>
            </div>
          </div>

          <div class="info-card">
            <div class="card-icon">
              <i class="fas fa-shopping-cart"></i>
            </div>
            <div class="card-content">
              <p class="card-label">Jumlah Order</p>
              <p class="card-value">{{ stats.jumlahOrder }}</p>
            </div>
          </div>

          <div class="info-card">
            <div class="card-icon">
              <i class="fas fa-users"></i>
            </div>
            <div class="card-content">
              <p class="card-label">Pelanggan Aktif</p>
              <p class="card-value">{{ stats.pelangganAktif }}</p>
            </div>
          </div>
        </div>

        <!-- Chart Section -->
        <div class="chart-section">
          <div class="chart-header">
            <div style="display: flex; align-items: center; gap: 10px;">
              <i class="fas fa-chart-bar chart-icon"></i>
              <h2 class="chart-title">Pendapatan per Minggu</h2>
            </div>
          </div>

          <div class="chart-container">
            <!-- Y-Axis Labels -->
            <div class="y-axis">
              <span class="y-label">12.5 Jt</span>
              <span class="y-label">10 Jt</span>
              <span class="y-label">7.5 Jt</span>
              <span class="y-label">5 Jt</span>
              <span class="y-label">2.5 Jt</span>
              <span class="y-label">0</span>
            </div>

            <!-- Chart Bars with Grid Lines -->
            <div class="chart-bars">
              <!-- Horizontal Grid Lines -->
              <div class="grid-lines">
                <div class="grid-line"></div>
                <div class="grid-line"></div>
                <div class="grid-line"></div>
                <div class="grid-line"></div>
                <div class="grid-line"></div>
              </div>

              <!-- Bars -->
              <div 
                v-for="(data, index) in pendapatanData" 
                :key="index"
                class="bar-wrapper"
              >
                <div 
                  class="bar" 
                  :style="{ height: (data.value / maxValue * 100) + '%' }"
                  @mouseenter="showTooltip($event, data)"
                  @mouseleave="hideTooltip"
                ></div>
                <span class="bar-label">{{ data.week }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Tooltip -->
        <div v-if="tooltip.show" class="chart-tooltip" :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
          <div class="tooltip-content">
            <div class="tooltip-week">{{ tooltip.week }}</div>
            <div class="tooltip-value">{{ formatCurrency(tooltip.value) }}</div>
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

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useTransactionStore } from '@/stores/transactionStore'
import { useFinancialStore } from '@/stores/financialStore'
import { useCustomerStore } from '@/stores/customerStore'
import Breadcrumbs from '../../components/Breadcrumbs.vue'
import ProfileModal from '@/components/ProfileModal.vue'
import ChangePasswordModal from '@/components/ChangePasswordModal.vue'
import ToastNotification from '@/components/ToastNotification.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

const router = useRouter()
const authStore = useAuthStore()
const transactionStore = useTransactionStore()
const financialStore = useFinancialStore()
const customerStore = useCustomerStore()

const breadcrumbItems = ref([
  { label: 'Dashboard' }
])

const loading = ref(false)

// Tooltip state
const tooltip = ref({
  show: false,
  x: 0,
  y: 0,
  week: '',
  value: 0
})

// Fetch data on mount
onMounted(async () => {
  loading.value = true
  await Promise.all([
    transactionStore.fetchTransactions(),
    financialStore.fetchFinancials(),
    customerStore.fetchCustomers()
  ])
  calculateStats()
  loading.value = false
})

// Computed statistics dari Supabase data
const stats = computed(() => {
  const totalPendapatan = financialStore.financials
    .filter(f => f.tipe === 'Pemasukan')
    .reduce((sum, f) => sum + (f.jumlah || 0), 0)
  
  const jumlahOrder = transactionStore.transactions.length
  
  const pelangganAktif = customerStore.customers.length
  
  return {
    totalPendapatan,
    jumlahOrder,
    pelangganAktif
  }
})

// Data pendapatan per minggu dari financials
const pendapatanData = ref([
  { week: 'Minggu 1', value: 0 },
  { week: 'Minggu 2', value: 0 },
  { week: 'Minggu 3', value: 0 },
  { week: 'Minggu 4', value: 0 }
])

function calculateStats() {
  // Group financial data by week
  const now = new Date()
  const currentMonth = now.getMonth()
  const currentYear = now.getFullYear()
  
  const weeklyData = [0, 0, 0, 0]
  
  financialStore.financials
    .filter(f => f.tipe === 'Pemasukan')
    .forEach(financial => {
      const date = new Date(financial.tanggal)
      if (date.getMonth() === currentMonth && date.getFullYear() === currentYear) {
        const dayOfMonth = date.getDate()
        const weekIndex = Math.min(Math.floor((dayOfMonth - 1) / 7), 3)
        weeklyData[weekIndex] += financial.jumlah || 0
      }
    })
  
  pendapatanData.value = [
    { week: 'Minggu 1', value: weeklyData[0] / 1000000 },
    { week: 'Minggu 2', value: weeklyData[1] / 1000000 },
    { week: 'Minggu 3', value: weeklyData[2] / 1000000 },
    { week: 'Minggu 4', value: weeklyData[3] / 1000000 }
  ]
}

// Tooltip functions
const showTooltip = (event, data) => {
  const rect = event.target.getBoundingClientRect()
  tooltip.value = {
    show: true,
    x: rect.left + rect.width / 2,
    y: rect.top - 10,
    week: data.week,
    value: data.value * 1000000 // Convert back to full value
  }
}

const hideTooltip = () => {
  tooltip.value.show = false
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(value)
}

// Max value untuk chart (dalam juta)
const maxValue = computed(() => {
  const max = Math.max(...pendapatanData.value.map(d => d.value))
  return Math.ceil(max * 1.2) || 12.5
})

// Profile menu
const showProfileMenu = ref(false)
const showProfileModal = ref(false)
const showPasswordModal = ref(false)
const toast = ref({
  show: false,
  message: '',
  type: 'success'
})

const toggleProfileMenu = () => {
  showProfileMenu.value = !showProfileMenu.value
}

async function handleLogout() {
  await authStore.logout()
  router.replace('/login')
}

function openProfileModal() {
  showProfileMenu.value = false
  showProfileModal.value = true
}

function openPasswordModal() {
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
</script>

<style scoped>
.dashboard-container {
  display: flex;
  min-height: 100vh;
  background: #F5F5F5;
  overflow-x: hidden;
  width: 100%;
  max-width: 100vw;
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

.menu-icon {
  margin-top: 0;
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

/* Main Area */
.main-area {
  flex: 1;
  padding: 30px;
  margin-left: 80px;
  width: calc(100% - 80px);
  overflow-y: auto;
  background: linear-gradient(135deg, #E8F4FD 0%, #F5F5F5 100%);
  min-height: 100vh;
  position: relative;
}

.main-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: radial-gradient(circle, rgba(22, 120, 243, 0.03) 1px, transparent 1px);
  background-size: 20px 20px;
  pointer-events: none;
  z-index: 0;
}

.main-area > * {
  position: relative;
  z-index: 1;
}

/* Header */
.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 40px;
  position: relative;
  overflow: visible;
  z-index: 100;
}

.page-title {
  font-family: 'Inter', sans-serif;
  font-size: 32px;
  font-weight: 700;
  color: #1678F3;
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
  z-index: 200;
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
  z-index: 9999;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #333333;
  text-decoration: none;
  background: white;
  border: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: all 0.3s;
}

.dropdown-item:hover {
  background: rgba(22, 120, 243, 0.05);
  color: #1678F3;
}

.dropdown-item i {
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.logout-item {
  border-top: 1px solid #E0E0E0;
  color: #FF4444;
}

.logout-item:hover {
  background: rgba(255, 68, 68, 0.05);
  color: #FF4444;
}

.main-content {
  width: 100%;
  overflow-x: hidden;
}

/* Info Cards */
.info-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.info-card {
  flex: 1;
  background: linear-gradient(135deg, #1678F3 0%, #6BB6FF 100%);
  border-radius: 20px;
  padding: 25px 30px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 4px 15px rgba(22, 120, 243, 0.3);
}

.card-icon {
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
}

.card-content {
  flex: 1;
}

.card-label {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 5px;
}

.card-value {
  font-family: 'Inter', sans-serif;
  font-size: 24px;
  font-weight: 700;
  color: white;
}

/* Chart Section */
.chart-section {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.chart-header {
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-icon {
  font-size: 24px;
  color: #1678F3;
}

.chart-title {
  font-family: 'Inter', sans-serif;
  font-size: 20px;
  font-weight: 600;
  color: #1678F3;
}

.chart-container {
  display: flex;
  align-items: flex-end;
  gap: 20px;
  height: 350px;
  position: relative;
  padding-left: 60px;
}

.y-axis {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 40px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
}

.y-label {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  color: #666666;
  padding-right: 10px;
}

.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 40px;
  height: 100%;
  flex: 1;
  border-left: 2px solid #E0E0E0;
  border-bottom: 2px solid #E0E0E0;
  padding: 20px 20px 40px 20px;
  position: relative;
}

.grid-lines {
  position: absolute;
  left: 0;
  right: 0;
  top: 20px;
  bottom: 40px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  pointer-events: none;
}

.grid-line {
  width: 100%;
  height: 1px;
  background: #F0F0F0;
  border-top: 1px dashed #D0D0D0;
}

.bar-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  z-index: 1;
}

.bar {
  width: 100%;
  max-width: 80px;
  background: #1678F3;
  border-radius: 6px 6px 0 0;
  transition: all 0.3s;
  margin-top: auto;
}

.bar:hover {
  background: #0d5ec4;
}

.bar-label {
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  color: #333333;
  margin-top: 10px;
  position: absolute;
  bottom: -30px;
}

/* Tooltip Styles */
.chart-tooltip {
  position: fixed;
  transform: translate(-50%, -100%);
  z-index: 10000;
  pointer-events: none;
  animation: tooltipFadeIn 0.2s ease-in;
}

@keyframes tooltipFadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, -90%);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -100%);
  }
}

.tooltip-content {
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 120px;
  text-align: center;
}

.tooltip-week {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #ffffff;
}

.tooltip-value {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 700;
  color: #4CAF50;
}

.export-icon {
  position: absolute;
  bottom: 10px;
  left: 10px;
  color: #1678F3;
  font-size: 20px;
  cursor: pointer;
  transition: color 0.3s;
}

.export-icon:hover {
  color: #0d5ec4;
}

/* Responsive */
@media (max-width: 1024px) {
  .user-profile {
    position: static;
    margin-bottom: 20px;
    justify-content: center;
  }

  .info-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  /* Bottom Navigation Bar for Mobile */
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
    margin-bottom: 0 !important;
    margin: 0 !important;
  }

  .logout-button {
    position: relative !important;
    bottom: auto !important;
    margin: 0 !important;
    width: 48px !important;
    height: 48px !important;
  }

  /* Main Content Adjust */
  .main-area {
    margin-left: 0 !important;
    margin-bottom: 85px !important;
    padding: 8px !important;
    width: 100% !important;
    max-width: 100vw !important;
    overflow-x: hidden !important;
    box-sizing: border-box !important;
  }

  .breadcrumbs {
    display: none !important;
  }

  .dashboard-header {
    flex-direction: row !important;
    justify-content: space-between !important;
    align-items: center !important;
    gap: 8px !important;
    margin-bottom: 16px !important;
    width: 100% !important;
    overflow: visible !important;
  }

  .page-title {
    font-size: 20px !important;
    flex: 1 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
  }

  .user-profile {
    width: auto !important;
    justify-content: flex-end !important;
    margin-bottom: 0 !important;
    padding: 4px 8px !important;
    flex-shrink: 0 !important;
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
    margin-left: 4px !important;
  }

  .user-name {
    font-size: 14px !important;
  }

  .profile-dropdown {
    right: 0 !important;
    left: auto !important;
  }

  .main-content {
    width: 100% !important;
    max-width: 100% !important;
    overflow-x: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
  }

  .info-cards {
    flex-direction: column !important;
    gap: 10px !important;
    width: 100% !important;
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
  }

  .info-card {
    padding: 12px 14px !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    margin: 0 !important;
    border-radius: 12px !important;
    box-shadow: none !important;
    transform: none !important;
  }

  .card-icon {
    width: 48px !important;
    height: 48px !important;
    font-size: 22px !important;
  }

  .card-label {
    font-size: 13px !important;
  }

  .card-value {
    font-size: 20px !important;
  }

  .chart-section {
    padding: 12px !important;
    margin-top: 16px !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    overflow-x: hidden !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
  }

  .chart-container {
    padding-left: 35px !important;
    height: 280px !important;
    overflow-x: hidden !important;
    width: 100% !important;
    max-width: 100% !important;
  }

  .chart-bars {
    gap: 12px !important;
    padding: 15px 10px 30px 10px !important;
  }

  .bar {
    max-width: 35px !important;
    min-width: 30px !important;
  }

  .y-axis {
    bottom: 30px !important;
  }

  .y-label {
    font-size: 10px !important;
  }

  .bar-label {
    font-size: 10px !important;
  }

  .main-content {
    padding: 0 !important;
  }
}
</style>
