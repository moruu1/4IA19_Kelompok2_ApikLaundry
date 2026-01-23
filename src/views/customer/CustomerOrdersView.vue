<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/authStore'
import { useTransactionStore } from '../../stores/transactionStore'
import { useCustomerStore } from '../../stores/customerStore'
import { supabase } from '../../lib/supabase'
import Breadcrumbs from '../../components/Breadcrumbs.vue'
import ToastNotification from '../../components/ToastNotification.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import ProfileModal from '../../components/ProfileModal.vue'
import ChangePasswordModal from '../../components/ChangePasswordModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const transactionStore = useTransactionStore()
const customerStore = useCustomerStore()

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

// Format date to readable format
function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  const day = date.getDate().toString().padStart(2, '0')
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const year = date.getFullYear()
  return `${day}/${month}/${year}`
}

// Get orders for current customer
const orders = computed(() => {
  if (!currentCustomerId.value) return []
  const filtered = transactionStore.transactions.filter(t => t.customer_id === currentCustomerId.value) || []
  
  // Map database fields to template format
  return filtered.map(transaction => ({
    noNota: transaction.nomor_nota,
    nama: transaction.customers?.nama || '-',
    layanan: transaction.services?.nama_layanan || '-',
    berat: transaction.jumlah_unit,
    statusPesanan: transaction.status_pesanan,
    statusPembayaran: transaction.status_pembayaran,
    tanggalMasuk: formatDate(transaction.tanggal_masuk),
    tanggalSelesai: formatDate(transaction.tanggal_selesai),
    metodePembayaran: transaction.metode_pembayaran
  }))
})

const breadcrumbItems = ref([
  { label: 'Home', path: '/customer/home' },
  { label: 'Riwayat Pemesanan' }
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
  <div class="customer-orders">
    <!-- Sidebar -->
    <div class="sidebar">
      <router-link to="/customer/home" class="sidebar-icon">
        <i class="fas fa-home"></i>
      </router-link>
      
      <router-link to="/customer/services" class="sidebar-icon">
        <i class="fas fa-concierge-bell"></i>
      </router-link>
      
      <router-link to="/customer/track" class="sidebar-icon">
        <i class="fas fa-map-marker-alt"></i>
      </router-link>
      
      <router-link to="/customer/orders" class="sidebar-icon active">
        <i class="fas fa-history"></i>
      </router-link>
      
      <!-- Logout Button - Bottom -->
      <div class="logout-button" @click="handleLogout">
        <i class="fas fa-sign-out-alt"></i>
      </div>
    </div>

    <div class="customer-orders-page">
      <!-- Breadcrumbs -->
      <Breadcrumbs :items="breadcrumbItems" />
      
      <!-- Header with User Profile -->
      <div class="header">
        <h1 class="page-title">Riwayat Pemesanan</h1>
        
        <div class="user-profile" @click="toggleProfileMenu">
          <div class="user-avatar">
            <i class="fas fa-user"></i>
          </div>
          <div class="user-info">
            <p class="user-name">{{ authStore.user?.name || 'Customer' }}</p>
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

      <!-- Orders Table -->
      <div class="orders-table-container">
      <table class="orders-table">
        <thead>
          <tr>
            <th>No Nota</th>
            <th>Nama</th>
            <th>Layanan</th>
            <th>Berat(kg)</th>
            <th>Status Pesanan</th>
            <th>Status Pembayaran</th>
            <th>Tanggal Masuk</th>
            <th>Tanggal Selesai</th>
            <th>Metode Pembayaran</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.noNota">
            <td>{{ order.noNota }}</td>
            <td>{{ order.nama }}</td>
            <td>{{ order.layanan }}</td>
            <td>{{ order.berat }}</td>
            <td>
              <span 
                class="status-badge"
                :class="{
                  'status-selesai': order.statusPesanan === 'Selesai',
                  'status-proses': order.statusPesanan === 'Proses',
                  'status-pending': order.statusPesanan === 'Pending'
                }"
              >
                {{ order.statusPesanan }}
              </span>
            </td>
            <td>{{ order.statusPembayaran }}</td>
            <td>{{ order.tanggalMasuk }}</td>
            <td>{{ order.tanggalSelesai || '-' }}</td>
            <td>{{ order.metodePembayaran }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="orders.length === 0" class="empty-state">
      <div class="empty-icon">📦</div>
      <h3 class="empty-title">Belum ada pesanan</h3>
      <p class="empty-text">Riwayat pesanan Anda akan ditampilkan di sini.</p>
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
  </div>
</template>

<style scoped>
.customer-orders {
  display: flex;
  min-height: 100vh;
  background: #f5f5f5;
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

.customer-orders-page {
  flex: 1;
  margin-left: 80px;
  padding: 30px;
  min-height: 100vh;
  background: linear-gradient(135deg, #E8F4FD 0%, #F5F5F5 100%);
  position: relative;
}

.customer-orders-page::before {
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

.orders-table-container {
  background: white;
  border-radius: 16px;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
}

.orders-table-container:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.orders-table {
  width: 100%;
  min-width: 800px;
  border-collapse: collapse;
}

.orders-table thead {
  background: #f8f9fa;
}

.orders-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.875rem;
  color: #666;
  border-bottom: 2px solid #e9ecef;
}

.orders-table tbody tr {
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.orders-table tbody tr:hover {
  background: #f8f9fa;
}

.orders-table td {
  padding: 1rem;
  font-size: 0.875rem;
  color: #333;
}

.status-badge {
  display: inline-block;
  padding: 0.375rem 0.875rem;
  border-radius: 20px;
  font-size: 0.813rem;
  font-weight: 500;
}

.status-selesai {
  background: #d4edda;
  color: #155724;
}

.status-proses {
  background: #fff3cd;
  color: #856404;
}

.status-pending {
  background: #f8d7da;
  color: #721c24;
}

.empty-state {
  background: white;
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.empty-text {
  color: #666;
  margin-bottom: 1.5rem;
}

.btn-primary {
  display: inline-block;
  background: linear-gradient(135deg, #1678F3 0%, #6BB6FF 100%);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(22, 120, 243, 0.3);
}

/* Mobile Responsive */
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

  .customer-orders-page {
    margin-left: 0 !important;
    margin-bottom: 85px !important;
    padding: 8px !important;
    width: 100% !important;
    max-width: 100vw !important;
    overflow-x: hidden !important;
    box-sizing: border-box !important;
  }

  .header {
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

  .user-name {
    font-size: 14px !important;
  }

  .order-card {
    padding: 16px !important;
    box-sizing: border-box !important;
    width: 100% !important;
  }

  .order-id {
    font-size: 14px !important;
    font-weight: 600 !important;
  }

  .order-details {
    font-size: 13px !important;
    line-height: 1.6 !important;
  }

  .order-status {
    font-size: 12px !important;
    padding: 6px 12px !important;
    margin-top: 8px !important;
  }

  .table-container {
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    margin: 0 -8px !important;
    padding: 0 8px !important;
  }

  .orders-table {
    min-width: 800px !important;
    font-size: 13px !important;
  }

  .orders-table th,
  .orders-table td {
    padding: 10px 8px !important;
  }
}
</style>
