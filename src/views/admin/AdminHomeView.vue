<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/authStore'
import { useCustomerStore } from '../../stores/customerStore'
import { useTransactionStore } from '../../stores/transactionStore'
import { useFinancialStore } from '../../stores/financialStore'
import { useInventoryStore } from '../../stores/inventoryStore'
import Breadcrumbs from '../../components/Breadcrumbs.vue'
import ToastNotification from '@/components/ToastNotification.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ProfileModal from '@/components/ProfileModal.vue'
import ChangePasswordModal from '@/components/ChangePasswordModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const customerStore = useCustomerStore()
const transactionStore = useTransactionStore()
const financialStore = useFinancialStore()
const inventoryStore = useInventoryStore()

const breadcrumbItems = ref([
  { label: 'Dashboard' }
])

const showProfileMenu = ref(false)
const showProfileModal = ref(false)
const showPasswordModal = ref(false)
const loading = ref(false)
const toast = ref({
  show: false,
  message: '',
  type: 'success'
})

// Fetch all data on mount
onMounted(async () => {
  await Promise.all([
    customerStore.fetchCustomers(),
    transactionStore.fetchTransactions(),
    financialStore.fetchFinancials(),
    inventoryStore.fetchInventoryItems()
  ])
})

// Dashboard Statistics
const totalCustomers = computed(() => customerStore.customers.length)

const todayTransactions = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)
  
  return transactionStore.transactions.filter(t => {
    if (!t.tanggal_masuk) return false
    const transDate = new Date(t.tanggal_masuk)
    return transDate >= today && transDate < tomorrow
  })
})

const todayRevenue = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)
  
  // Hitung dari transaksi yang sudah lunas hari ini
  return transactionStore.transactions
    .filter(t => {
      if (!t.tanggal_masuk || t.status_pembayaran !== 'Lunas') return false
      const transDate = new Date(t.tanggal_masuk)
      return transDate >= today && transDate < tomorrow
    })
    .reduce((sum, t) => sum + (t.total_harga || 0), 0)
})

const lowStockItems = computed(() => {
  return inventoryStore.inventoryItems.filter(item => item.stok_sisa <= 10)
})

const recentTransactions = computed(() => {
  return transactionStore.transactions.slice(0, 5)
})

const monthlyRevenue = computed(() => {
  const currentMonth = new Date().getMonth()
  const currentYear = new Date().getFullYear()
  
  const pemasukan = financialStore.financials
    .filter(f => {
      const date = new Date(f.tanggal)
      return date.getMonth() === currentMonth && 
             date.getFullYear() === currentYear && 
             f.tipe === 'Pemasukan'
    })
    .reduce((sum, f) => sum + f.jumlah, 0)
  
  const pengeluaran = financialStore.financials
    .filter(f => {
      const date = new Date(f.tanggal)
      return date.getMonth() === currentMonth && 
             date.getFullYear() === currentYear && 
             f.tipe === 'Pengeluaran'
    })
    .reduce((sum, f) => sum + f.jumlah, 0)
  
  return { pemasukan, pengeluaran, selisih: pemasukan - pengeluaran }
})

function formatCurrency(amount) {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(amount)
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('id-ID', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  })
}

function getStatusBadgeClass(status) {
  const statusMap = {
    'Diproses': 'badge-warning',
    'Selesai': 'badge-success',
    'Diambil': 'badge-info'
  }
  return statusMap[status] || 'badge-default'
}

function toggleProfileMenu() {
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

<template>
  <div class="admin-home-container">
    <!-- Sidebar -->
    <div class="sidebar">
      <!-- Menu Icons -->
      <router-link to="/admin/dashboard" class="sidebar-icon active">
        <i class="fas fa-th"></i>
      </router-link>
      
      <router-link to="/admin/customers" class="sidebar-icon">
        <i class="fas fa-user"></i>
      </router-link>
      
      <router-link to="/admin/orders" class="sidebar-icon">
        <i class="fas fa-shopping-cart"></i>
      </router-link>

      <router-link to="/admin/financial-report" class="sidebar-icon">
        <i class="fas fa-file-invoice-dollar"></i>
      </router-link>

      <router-link to="/admin/inventory" class="sidebar-icon">
        <i class="fas fa-boxes"></i>
      </router-link>

      <router-link to="/admin/services" class="sidebar-icon">
        <i class="fas fa-concierge-bell"></i>
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
      <div class="admin-header">
        <h1 class="page-title">Dashboard Admin</h1>
        
        <!-- User Profile (Top Right) -->
        <div class="user-profile" @click="toggleProfileMenu">
          <div class="user-avatar">
            <i class="fas fa-user"></i>
          </div>
          <div class="user-info">
            <p class="user-name">{{ authStore.user?.name || 'Admin Apik' }}</p>
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

      <!-- Dashboard Content -->
      <div class="dashboard-content">
        <!-- Statistics Cards -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon customers">
              <i class="fas fa-users"></i>
            </div>
            <div class="stat-info">
              <h3 class="stat-value">{{ totalCustomers }}</h3>
              <p class="stat-label">Total Pelanggan</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon orders">
              <i class="fas fa-shopping-cart"></i>
            </div>
            <div class="stat-info">
              <h3 class="stat-value">{{ todayTransactions.length }}</h3>
              <p class="stat-label">Pesanan Hari Ini</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon revenue">
              <i class="fas fa-money-bill-wave"></i>
            </div>
            <div class="stat-info">
              <h3 class="stat-value">{{ formatCurrency(todayRevenue) }}</h3>
              <p class="stat-label">Pendapatan Hari Ini</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon inventory">
              <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div class="stat-info">
              <h3 class="stat-value">{{ lowStockItems.length }}</h3>
              <p class="stat-label">Stok Menipis</p>
            </div>
          </div>
        </div>

        <!-- Revenue Chart -->
        <div class="chart-card">
          <h3 class="card-title">Pendapatan Bulan Ini</h3>
          <div class="revenue-bars">
            <div class="revenue-item">
              <div class="revenue-label">
                <i class="fas fa-arrow-up" style="color: #4CAF50"></i>
                <span>Pemasukan</span>
              </div>
              <div class="revenue-bar-container">
                <div class="revenue-bar pemasukan" :style="{ width: monthlyRevenue.pemasukan > 0 ? '100%' : '0%' }"></div>
              </div>
              <span class="revenue-value">{{ formatCurrency(monthlyRevenue.pemasukan) }}</span>
            </div>
            <div class="revenue-item">
              <div class="revenue-label">
                <i class="fas fa-arrow-down" style="color: #EF5350"></i>
                <span>Pengeluaran</span>
              </div>
              <div class="revenue-bar-container">
                <div class="revenue-bar pengeluaran" :style="{ width: monthlyRevenue.pengeluaran > 0 ? (monthlyRevenue.pengeluaran / monthlyRevenue.pemasukan * 100) + '%' : '0%' }"></div>
              </div>
              <span class="revenue-value">{{ formatCurrency(monthlyRevenue.pengeluaran) }}</span>
            </div>
            <div class="revenue-item selisih">
              <div class="revenue-label">
                <i class="fas fa-chart-line" :style="{ color: monthlyRevenue.selisih >= 0 ? '#1678F3' : '#EF5350' }"></i>
                <span>Selisih</span>
              </div>
              <span class="revenue-value" :class="{ negative: monthlyRevenue.selisih < 0 }">{{ formatCurrency(monthlyRevenue.selisih) }}</span>
            </div>
          </div>
        </div>

        <!-- Two Column Layout -->
        <div class="two-column">
          <!-- Recent Transactions -->
          <div class="table-card">
            <div class="card-header">
              <h3 class="card-title">Pesanan Terbaru</h3>
              <router-link to="/admin/orders" class="view-all">Lihat Semua</router-link>
            </div>
            <div class="table-container">
              <table v-if="recentTransactions.length > 0" class="dashboard-table">
                <thead>
                  <tr>
                    <th>No. Nota</th>
                    <th>Pelanggan</th>
                    <th>Status</th>
                    <th>Tanggal</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="trans in recentTransactions" :key="trans.id_transaction">
                    <td>{{ trans.nomor_nota }}</td>
                    <td>{{ trans.customers?.nama || '-' }}</td>
                    <td>
                      <span class="badge" :class="getStatusBadgeClass(trans.status_pesanan)">
                        {{ trans.status_pesanan }}
                      </span>
                    </td>
                    <td>{{ formatDate(trans.tanggal_masuk) }}</td>
                  </tr>
                </tbody>
              </table>
              <div v-else class="empty-state-small">
                <i class="fas fa-inbox"></i>
                <p>Belum ada transaksi</p>
              </div>
            </div>
          </div>

          <!-- Low Stock Alert -->
          <div class="table-card">
            <div class="card-header">
              <h3 class="card-title">Stok Menipis</h3>
              <router-link to="/admin/inventory" class="view-all">Lihat Semua</router-link>
            </div>
            <div class="table-container">
              <table v-if="lowStockItems.length > 0" class="dashboard-table">
                <thead>
                  <tr>
                    <th>Nama Barang</th>
                    <th>Stok</th>
                    <th>Unit</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in lowStockItems" :key="item.id_inventory_item" class="low-stock-row">
                    <td>{{ item.nama_barang }}</td>
                    <td><span class="stock-alert">{{ item.stok_sisa }}</span></td>
                    <td>{{ item.unit }}</td>
                  </tr>
                </tbody>
              </table>
              <div v-else class="empty-state-small success">
                <i class="fas fa-check-circle"></i>
                <p>Semua stok aman</p>
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
/* Page Container */
.admin-home-container {
  display: flex;
  min-height: 100vh;
  background: #E8E8E8;
  font-family: 'Inter', sans-serif;
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
  z-index: 100;
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

/* Main Area */
.main-area {
  flex: 1;
  margin-left: 80px;
  padding: 40px;
  display: flex;
  flex-direction: column;
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
.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 40px;
  width: 100%;
  position: relative;
  overflow: visible;
  z-index: 100;
}

.page-title {
  font-family: 'Inter', sans-serif;
  font-size: 32px;
  font-weight: 700;
  color: #1678F3;
  margin: 0;
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
  margin-left: auto;
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

/* Dashboard Content */
.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Statistics Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.customers {
  background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
}

.stat-icon.orders {
  background: linear-gradient(135deg, #F093FB 0%, #F5576C 100%);
}

.stat-icon.revenue {
  background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
}

.stat-icon.inventory {
  background: linear-gradient(135deg, #FF9800 0%, #FF5722 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin: 0 0 4px 0;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* Chart Card */
.chart-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 20px 0;
}

.revenue-bars {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.revenue-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.revenue-item.selisih {
  padding-top: 16px;
  border-top: 2px dashed #E0E0E0;
  justify-content: space-between;
}

.revenue-label {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 140px;
  font-size: 14px;
  font-weight: 500;
  color: #666;
}

.revenue-bar-container {
  flex: 1;
  height: 32px;
  background: #F5F5F5;
  border-radius: 8px;
  overflow: hidden;
}

.revenue-bar {
  height: 100%;
  transition: width 1s ease;
  border-radius: 8px;
}

.revenue-bar.pemasukan {
  background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
}

.revenue-bar.pengeluaran {
  background: linear-gradient(90deg, #EF5350 0%, #F44336 100%);
}

.revenue-value {
  min-width: 140px;
  text-align: right;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.revenue-value.negative {
  color: #EF5350;
}

/* Two Column Layout */
.two-column {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.table-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.view-all {
  font-size: 14px;
  color: #1678F3;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.view-all:hover {
  color: #0d5bbf;
  text-decoration: underline;
}

.table-container {
  overflow-x: auto;
}

.dashboard-table {
  width: 100%;
  border-collapse: collapse;
}

.dashboard-table thead th {
  text-align: left;
  padding: 12px;
  font-size: 13px;
  font-weight: 600;
  color: #666;
  border-bottom: 2px solid #F0F0F0;
}

.dashboard-table tbody td {
  padding: 12px;
  font-size: 14px;
  color: #333;
  border-bottom: 1px solid #F5F5F5;
}

.dashboard-table tbody tr:hover {
  background: #FAFAFA;
}

.badge {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  display: inline-block;
}

.badge-warning {
  background: rgba(255, 152, 0, 0.1);
  color: #FF9800;
}

.badge-success {
  background: rgba(76, 175, 80, 0.1);
  color: #4CAF50;
}

.badge-info {
  background: rgba(22, 120, 243, 0.1);
  color: #1678F3;
}

.badge-default {
  background: rgba(158, 158, 158, 0.1);
  color: #9E9E9E;
}

.low-stock-row td {
  color: #FF5722 !important;
}

.stock-alert {
  background: rgba(255, 87, 34, 0.1);
  color: #FF5722;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.empty-state-small {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.empty-state-small i {
  font-size: 48px;
  margin-bottom: 12px;
  color: #E0E0E0;
}

.empty-state-small.success i {
  color: #4CAF50;
}

.empty-state-small p {
  margin: 0;
  font-size: 14px;
}

/* Responsive */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .two-column {
    grid-template-columns: 1fr;
  }
}

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
  }

  .page-title {
    font-size: 20px !important;
    flex: 1 !important;
  }

  .user-profile {
    width: auto !important;
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
  }

  .user-name {
    font-size: 14px !important;
  }
  
  .stats-grid {
    grid-template-columns: 1fr !important;
    gap: 12px !important;
  }
  
  .stat-card {
    padding: 16px !important;
    width: 100% !important;
    box-sizing: border-box !important;
  }
  
  .stat-icon {
    width: 48px !important;
    height: 48px !important;
    font-size: 22px !important;
  }

  .stat-label {
    font-size: 13px !important;
  }
  
  .stat-value {
    font-size: 24px !important;
  }
}
</style>
