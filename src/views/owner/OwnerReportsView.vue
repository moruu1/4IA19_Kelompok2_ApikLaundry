<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/authStore'
import { useFinancialStore } from '../../stores/financialStore'
import Breadcrumbs from '../../components/Breadcrumbs.vue'
import ToastNotification from '@/components/ToastNotification.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import EmptyState from '@/components/EmptyState.vue'
import ProfileModal from '@/components/ProfileModal.vue'
import ChangePasswordModal from '@/components/ChangePasswordModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const financialStore = useFinancialStore()

const breadcrumbItems = ref([
  { label: 'Dashboard', path: '/owner/dashboard' },
  { label: 'Laporan Keuangan' }
])

const showProfileMenu = ref(false)
const startDate = ref('')
const endDate = ref('')
const showProfileModal = ref(false)
const showPasswordModal = ref(false)
const showAddModal = ref(false)
const addForm = ref({
  tanggal: '',
  tipe: 'Pengeluaran',
  keterangan: '',
  jumlah: 0,
  metode_pembayaran: 'Tunai'
})
const toast = ref({
  show: false,
  message: '',
  type: 'success'
})

// Pagination
const currentPage = ref(1)
const itemsPerPage = ref(10)

// Type Filter
const typeFilter = ref('Semua')

// Fetch financial data on mount
onMounted(async () => {
  await financialStore.fetchFinancials()
})

const filteredTransactions = computed(() => {
  let transactions = []
  
  if (!startDate.value || !endDate.value) {
    transactions = [...financialStore.financials]
  } else {
    const start = new Date(startDate.value)
    start.setHours(0, 0, 0, 0)
    
    const end = new Date(endDate.value)
    end.setHours(23, 59, 59, 999)
    
    transactions = financialStore.financials.filter(transaction => {
      const transDate = new Date(transaction.tanggal)
      return transDate >= start && transDate <= end
    })
  }
  
  // Filter by type (Pemasukan/Pengeluaran/Semua)
  if (typeFilter.value !== 'Semua') {
    transactions = transactions.filter(t => t.tipe === typeFilter.value)
  }
  
  // Sort by date descending (newest first), then by id descending for same date
  return transactions.sort((a, b) => {
    const dateCompare = new Date(b.tanggal) - new Date(a.tanggal)
    if (dateCompare !== 0) return dateCompare
    // If dates are the same, sort by id (newest entry first)
    return (b.id_financial || 0) - (a.id_financial || 0)
  })
})

// Pagination computed properties
const totalPages = computed(() => {
  return Math.ceil(filteredTransactions.value.length / itemsPerPage.value)
})

const paginatedTransactions = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredTransactions.value.slice(start, end)
})

const pageNumbers = computed(() => {
  const pages = []
  const maxVisible = 5
  let startPage = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let endPage = Math.min(totalPages.value, startPage + maxVisible - 1)
  
  if (endPage - startPage + 1 < maxVisible) {
    startPage = Math.max(1, endPage - maxVisible + 1)
  }
  
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i)
  }
  
  return pages
})

// Calculate summary
const summary = computed(() => {
  const pemasukan = filteredTransactions.value
    .filter(t => t.tipe === 'Pemasukan')
    .reduce((sum, t) => sum + t.jumlah, 0)
  
  const pengeluaran = filteredTransactions.value
    .filter(t => t.tipe === 'Pengeluaran')
    .reduce((sum, t) => sum + t.jumlah, 0)
  
  return {
    pemasukan,
    pengeluaran,
    selisih: pemasukan - pengeluaran
  }
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
    month: '2-digit',
    year: 'numeric'
  })
}

function toggleProfileMenu() {
  showProfileMenu.value = !showProfileMenu.value
}

async function filterByDate() {
  currentPage.value = 1 // Reset to first page when filtering
  if (startDate.value && endDate.value) {
    await financialStore.fetchFinancials(startDate.value, endDate.value)
  } else {
    await financialStore.fetchFinancials()
  }
}

function clearFilter() {
  startDate.value = ''
  endDate.value = ''
  typeFilter.value = 'Semua'
  currentPage.value = 1
  financialStore.fetchFinancials()
}

function setTypeFilter(type) {
  typeFilter.value = type
  currentPage.value = 1
}

// Pagination functions
function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

function previousPage() {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
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
  financialStore.loading = true
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
    financialStore.loading = false
  }
}

async function handlePasswordSave(passwordData) {
  financialStore.loading = true
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
    financialStore.loading = false
  }
}

function openAddModal() {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  
  addForm.value = {
    tanggal: `${year}-${month}-${day}`,
    tipe: 'Pengeluaran',
    keterangan: '',
    jumlah: 0,
    metode_pembayaran: 'Tunai'
  }
  showAddModal.value = true
}

function closeAddModal() {
  showAddModal.value = false
  addForm.value = {
    tanggal: '',
    tipe: 'Pengeluaran',
    keterangan: '',
    jumlah: 0,
    metode_pembayaran: 'Tunai'
  }
}

async function saveAdd() {
  if (!addForm.value.tanggal || !addForm.value.keterangan || !addForm.value.jumlah) {
    toast.value = {
      show: true,
      message: 'Harap lengkapi semua field!',
      type: 'warning'
    }
    return
  }
  
  financialStore.loading = true
  try {
    const result = await financialStore.createFinancial({
      transaction_id: null,
      tanggal: addForm.value.tanggal,
      tipe: addForm.value.tipe,
      keterangan: addForm.value.keterangan,
      jumlah: Number(addForm.value.jumlah),
      metode_pembayaran: addForm.value.metode_pembayaran
    })
    
    if (result.success) {
      toast.value = {
        show: true,
        message: 'Data keuangan berhasil ditambahkan!',
        type: 'success'
      }
      await financialStore.fetchFinancials()
      closeAddModal()
    } else {
      toast.value = {
        show: true,
        message: result.message || 'Gagal menambahkan data',
        type: 'error'
      }
    }
  } catch (error) {
    console.error('Error adding financial data:', error)
    toast.value = {
      show: true,
      message: 'Terjadi kesalahan saat menambahkan data',
      type: 'error'
    }
  } finally {
    financialStore.loading = false
  }
}
</script>

<template>
  <div class="financial-container">
    <!-- Sidebar -->
    <div class="sidebar">
      <!-- Menu Icons -->
      <router-link to="/owner/dashboard" class="sidebar-icon menu-icon">
        <i class="fas fa-th"></i>
      </router-link>
      
      <router-link to="/owner/reports" class="sidebar-icon active">
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
      <div class="financial-header">
        <h1 class="page-title">Laporan Keuangan</h1>
        
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

      <!-- Content Section -->
      <div class="content-section">
        <!-- Action Buttons -->
        <div class="action-buttons">
          <button class="btn-add" @click="openAddModal">
            <i class="fas fa-plus"></i>
            Tambah Data Keuangan
          </button>
        </div>

        <!-- Date Range Filter -->
        <div class="date-filter">
          <div class="date-input-group">
            <i class="fas fa-calendar"></i>
            <label>Tanggal Awal</label>
            <input v-model="startDate" type="date" />
          </div>
          
          <div class="date-input-group">
            <i class="fas fa-calendar"></i>
            <label>Tanggal Akhir</label>
            <input v-model="endDate" type="date" />
          </div>
          
          <button class="btn-cek" @click="filterByDate">Cek</button>
          <button 
            v-if="startDate || endDate" 
            class="btn-clear" 
            @click="clearFilter"
          >
            Reset
          </button>
        </div>

        <!-- Type Filter Tabs -->
        <div class="type-filter-tabs">
          <button 
            class="filter-tab" 
            :class="{ active: typeFilter === 'Semua' }"
            @click="setTypeFilter('Semua')"
          >
            <i class="fas fa-list"></i>
            <span>Semua</span>
          </button>
          <button 
            class="filter-tab" 
            :class="{ active: typeFilter === 'Pemasukan' }"
            @click="setTypeFilter('Pemasukan')"
          >
            <i class="fas fa-arrow-up"></i>
            <span>Pemasukan</span>
          </button>
          <button 
            class="filter-tab" 
            :class="{ active: typeFilter === 'Pengeluaran' }"
            @click="setTypeFilter('Pengeluaran')"
          >
            <i class="fas fa-arrow-down"></i>
            <span>Pengeluaran</span>
          </button>
        </div>

        <!-- Summary Cards -->
        <div class="summary-cards">
          <div class="summary-card pemasukan">
            <i class="fas fa-arrow-up"></i>
            <div class="summary-info">
              <span class="summary-label">Total Pemasukan</span>
              <span class="summary-amount">{{ formatCurrency(summary.pemasukan) }}</span>
            </div>
          </div>
          <div class="summary-card pengeluaran">
            <i class="fas fa-arrow-down"></i>
            <div class="summary-info">
              <span class="summary-label">Total Pengeluaran</span>
              <span class="summary-amount">{{ formatCurrency(summary.pengeluaran) }}</span>
            </div>
          </div>
          <div class="summary-card selisih" :class="{ negative: summary.selisih < 0 }">
            <i class="fas fa-chart-line"></i>
            <div class="summary-info">
              <span class="summary-label">Selisih</span>
              <span class="summary-amount">{{ formatCurrency(summary.selisih) }}</span>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="financialStore.loading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Memuat data...</p>
        </div>

        <!-- Table -->
        <div v-else class="table-container">
          <!-- Empty State -->
          <EmptyState 
            v-if="filteredTransactions.length === 0"
            icon="fas fa-file-invoice-dollar"
            title="Tidak Ada Transaksi"
            message="Tidak ada transaksi untuk periode yang dipilih"
          />

          <table v-else class="financial-table">
            <thead>
              <tr>
                <th class="col-keterangan">Keterangan</th>
                <th class="col-tipe">Tipe</th>
                <th class="col-jumlah">Jumlah</th>
                <th class="col-tanggal">Tanggal</th>
                <th class="col-transaksi">Metode</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="transaction in paginatedTransactions" 
                :key="transaction.id_financial"
                :class="{ 
                  'row-pemasukan': transaction.tipe === 'Pemasukan',
                  'row-pengeluaran': transaction.tipe === 'Pengeluaran'
                }"
              >
                <td class="col-keterangan">{{ transaction.keterangan }}</td>
                <td class="col-tipe">
                  <span 
                    class="badge" 
                    :class="{ 
                      'badge-success': transaction.tipe === 'Pemasukan',
                      'badge-danger': transaction.tipe === 'Pengeluaran'
                    }"
                  >
                    {{ transaction.tipe }}
                  </span>
                </td>
                <td class="col-jumlah">{{ formatCurrency(transaction.jumlah) }}</td>
                <td class="col-tanggal">{{ formatDate(transaction.tanggal) }}</td>
                <td class="col-transaksi">{{ transaction.metode_pembayaran || '-' }}</td>
              </tr>
            </tbody>
          </table>

          <!-- Pagination Controls -->
          <div v-if="filteredTransactions.length > 0" class="pagination-container">
            <div class="pagination-info">
              Menampilkan {{ (currentPage - 1) * itemsPerPage + 1 }} - 
              {{ Math.min(currentPage * itemsPerPage, filteredTransactions.length) }} 
              dari {{ filteredTransactions.length }} data
            </div>
            
            <div class="pagination-controls">
              <button 
                class="pagination-btn" 
                :disabled="currentPage === 1"
                @click="previousPage"
              >
                <i class="fas fa-chevron-left"></i>
              </button>
              
              <button 
                v-if="pageNumbers[0] > 1"
                class="pagination-btn"
                @click="goToPage(1)"
              >
                1
              </button>
              
              <span v-if="pageNumbers[0] > 2" class="pagination-ellipsis">...</span>
              
              <button 
                v-for="page in pageNumbers" 
                :key="page"
                class="pagination-btn"
                :class="{ active: currentPage === page }"
                @click="goToPage(page)"
              >
                {{ page }}
              </button>
              
              <span v-if="pageNumbers[pageNumbers.length - 1] < totalPages - 1" class="pagination-ellipsis">...</span>
              
              <button 
                v-if="pageNumbers[pageNumbers.length - 1] < totalPages"
                class="pagination-btn"
                @click="goToPage(totalPages)"
              >
                {{ totalPages }}
              </button>
              
              <button 
                class="pagination-btn" 
                :disabled="currentPage === totalPages"
                @click="nextPage"
              >
                <i class="fas fa-chevron-right"></i>
              </button>
            </div>
            
            <div class="items-per-page">
              <label>Tampilkan:</label>
              <select v-model="itemsPerPage" @change="currentPage = 1">
                <option :value="5">5</option>
                <option :value="10">10</option>
                <option :value="25">25</option>
                <option :value="50">50</option>
              </select>
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
    <LoadingSpinner :show="financialStore.loading" message="Memproses..." />

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

    <!-- Add Financial Data Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click="closeAddModal">
      <div class="modal-content" @click.stop>
        <h2 class="modal-title">Tambah Data Keuangan</h2>
        
        <div class="form-group">
          <label>Tanggal</label>
          <input 
            v-model="addForm.tanggal" 
            type="date" 
            class="form-input" 
          />
        </div>
        
        <div class="form-group">
          <label>Tipe</label>
          <select v-model="addForm.tipe" class="form-input">
            <option value="Pemasukan">Pemasukan</option>
            <option value="Pengeluaran">Pengeluaran</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Keterangan</label>
          <textarea 
            v-model="addForm.keterangan" 
            class="form-input" 
            rows="3"
            placeholder="Contoh: Pembelian Detergen, Gaji Karyawan, dll"
          ></textarea>
        </div>
        
        <div class="form-group">
          <label>Jumlah (Rp)</label>
          <input 
            v-model.number="addForm.jumlah" 
            type="number" 
            class="form-input" 
            placeholder="0"
          />
        </div>
        
        <div class="form-group">
          <label>Metode Pembayaran</label>
          <select v-model="addForm.metode_pembayaran" class="form-input">
            <option value="Tunai">Tunai</option>
            <option value="Transfer">Transfer</option>
            <option value="E-Wallet">E-Wallet</option>
          </select>
        </div>
        
        <div class="modal-actions">
          <button @click="closeAddModal" class="btn-cancel">Batal</button>
          <button @click="saveAdd" class="btn-save">Simpan</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Financial Report Container */
.financial-container {
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

.sidebar-icon i {
  color: #1678F3;
  font-size: 24px;
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
  padding: 30px;
  margin-left: 80px;
  width: calc(100% - 80px);
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
.financial-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
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

/* User Profile */
.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  position: relative;
  padding: 8px 15px;
  border-radius: 8px;
  transition: background 0.3s;
  z-index: 200;
}

.user-profile:hover {
  background: rgba(0, 0, 0, 0.05);
}

.profile-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
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
  color: #666;
}

.profile-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  margin-top: 8px;
  min-width: 180px;
  z-index: 9999;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: #333;
  text-decoration: none;
  transition: background 0.3s;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
}

.dropdown-item:hover {
  background: #f5f5f5;
}

.dropdown-item i {
  font-size: 16px;
  width: 20px;
  text-align: center;
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
    margin-bottom: 0 !important;
  }

  .logout-button {
    position: relative !important;
    bottom: auto !important;
    margin: 0 !important;
    margin-top: 0 !important;
    width: 48px !important;
    height: 48px !important;
  }

  .main-area {
    margin-left: 0 !important;
    margin-bottom: 85px !important;
    padding: 12px !important;
    width: 100% !important;
  }

  .breadcrumbs {
    display: none !important;
  }

  .financial-header {
    flex-direction: row !important;
    justify-content: space-between !important;
    align-items: center !important;
    gap: 8px !important;
    margin-bottom: 16px !important;
    padding: 0 !important;
  }

  .page-title {
    font-size: 18px !important;
    margin-bottom: 0 !important;
    width: auto !important;
    flex: 1 !important;
  }

  .user-profile {
    position: relative !important;
    width: auto !important;
    padding: 4px 8px !important;
    margin-left: 0 !important;
    align-self: center !important;
    flex-shrink: 0 !important;
  }

  .user-avatar {
    width: 32px !important;
    height: 32px !important;
    font-size: 14px !important;
    min-width: 32px !important;
    flex-shrink: 0 !important;
  }

  .user-info {
    display: none !important;
  }
  
  .user-name {
    font-size: 13px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    max-width: 150px !important;
  }

  .dropdown-icon {
    font-size: 10px !important;
    margin-left: 4px !important;
  }

  .content-section {
    padding: 14px !important;
    border-radius: 8px !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    overflow-x: hidden !important;
  }

  .action-buttons {
    margin-bottom: 16px !important;
  }

  .btn-add {
    width: 100% !important;
    padding: 14px 20px !important;
    font-size: 15px !important;
    min-height: 48px !important;
  }

  .date-filter {
    flex-direction: column !important;
    gap: 12px !important;
    margin-bottom: 20px !important;
  }

  .date-input-group {
    width: 100% !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 8px !important;
  }

  .date-input-group label {
    font-size: 13px !important;
    min-width: 90px !important;
  }

  .date-input-group input {
    flex: 1 !important;
    font-size: 14px !important;
    padding: 10px !important;
  }

  .btn-cek,
  .btn-clear {
    width: 100% !important;
    min-height: 44px !important;
    font-size: 15px !important;
    padding: 12px !important;
  }

  .type-filter-tabs {
    display: flex !important;
    gap: 8px !important;
    margin-bottom: 20px !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    width: 100% !important;
    max-width: 100% !important;
  }

  .filter-tab {
    flex: 0 0 auto !important;
    min-width: 110px !important;
    padding: 10px 12px !important;
    font-size: 13px !important;
  }

  .filter-tab i {
    font-size: 16px !important;
  }

  .summary-cards {
    display: flex !important;
    flex-direction: column !important;
    grid-template-columns: none !important;
    gap: 12px !important;
    margin-bottom: 20px !important;
    width: 100% !important;
    max-width: 100% !important;
  }

  .summary-card {
    padding: 14px !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    flex-shrink: 0 !important;
  }

  .summary-card i {
    font-size: 24px !important;
    width: 45px !important;
    height: 45px !important;
    min-width: 45px !important;
    padding: 10px !important;
  }

  .summary-info {
    flex: 1 !important;
    min-width: 0 !important;
  }

  .summary-label {
    font-size: 13px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
  }

  .summary-amount {
    font-size: 17px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
  }

  /* Table Mobile Styles */
  .table-container {
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    margin: 0 -14px 20px !important;
    padding: 0 14px !important;
    border-radius: 8px !important;
  }

  .financial-table {
    min-width: 800px !important;
    font-size: 13px !important;
  }

  .financial-table th,
  .financial-table td {
    font-size: 13px !important;
    padding: 10px 8px !important;
    white-space: nowrap !important;
  }

  /* Pagination Mobile Styles */
  .pagination-container {
    flex-direction: column !important;
    align-items: stretch !important;
    gap: 14px !important;
    padding: 14px !important;
  }

  .pagination-info {
    text-align: center !important;
    font-size: 13px !important;
  }

  .pagination-controls {
    justify-content: center !important;
    flex-wrap: wrap !important;
    gap: 6px !important;
  }

  .pagination-btn {
    min-width: 40px !important;
    height: 40px !important;
    font-size: 14px !important;
    padding: 8px !important;
  }

  .items-per-page {
    justify-content: center !important;
  }

  .items-per-page label {
    font-size: 13px !important;
  }

  .items-per-page select {
    min-height: 40px !important;
    font-size: 14px !important;
    padding: 10px 32px 10px 12px !important;
  }
}

/* Content Section */
.content-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.3s ease;
  animation: slideUp 0.5s ease-out;
}

.content-section:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.btn-add {
  padding: 12px 24px;
  background: linear-gradient(135deg, #1678F3 0%, #1565C0 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(22, 120, 243, 0.3);
}

.btn-add:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(22, 120, 243, 0.4);
}

/* Type Filter Tabs */
.type-filter-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  padding: 6px;
  background: #F5F5F5;
  border-radius: 10px;
  width: fit-content;
}

.filter-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  background: transparent;
  color: #666;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.filter-tab i {
  font-size: 16px;
  transition: transform 0.3s ease;
}

.filter-tab:hover {
  color: #1678F3;
  background: rgba(22, 120, 243, 0.08);
}

.filter-tab:hover i {
  transform: scale(1.1);
}

.filter-tab.active {
  background: white;
  color: #1678F3;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.filter-tab.active i {
  color: #1678F3;
}

/* Date Filter */
.date-filter {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.date-input-group {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #F5F5F5;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #E0E0E0;
  transition: all 0.3s ease;
}

.date-input-group:focus-within {
  border-color: #1678F3;
  background: white;
  box-shadow: 0 0 0 3px rgba(22, 120, 243, 0.1);
  transform: translateY(-2px);
}

.date-input-group i {
  color: #666;
  font-size: 16px;
}

.date-input-group label {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
}

.date-input-group input {
  border: none;
  background: transparent;
  outline: none;
  font-size: 14px;
  color: #333;
  font-weight: 500;
  width: 120px;
}

.btn-cek {
  background: linear-gradient(135deg, #1678F3 0%, #1565C0 100%);
  color: white;
  border: none;
  padding: 12px 40px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(22, 120, 243, 0.2);
}

.btn-clear {
  background: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
  padding: 12px 32px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-clear:hover {
  background: #e0e0e0;
  transform: translateY(-2px);
}

/* Summary Cards */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.summary-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.summary-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.summary-card i {
  font-size: 32px;
  padding: 16px;
  border-radius: 12px;
}

.summary-card.pemasukan i {
  background: rgba(34, 197, 94, 0.1);
  color: #22C55E;
}

.summary-card.pengeluaran i {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.summary-card.selisih i {
  background: rgba(22, 120, 243, 0.1);
  color: #1678F3;
}

.summary-card.selisih.negative i {
  background: rgba(245, 158, 11, 0.1);
  color: #F59E0B;
}

.summary-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.summary-amount {
  font-size: 24px;
  font-weight: 700;
  color: #333;
}

.summary-card.selisih.negative .summary-amount {
  color: #F59E0B;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #666;
}

.loading-state i {
  font-size: 48px;
  color: #1678F3;
  margin-bottom: 16px;
}

.loading-state p {
  font-size: 16px;
  font-weight: 500;
}

.btn-cek::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.btn-cek:active::before {
  width: 300px;
  height: 300px;
}

.btn-cek:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(22, 120, 243, 0.4);
}

.btn-cek:active {
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(22, 120, 243, 0.3);
}

/* Table */
.table-container {
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  margin-bottom: 30px;
  border-radius: 12px;
  border: 1px solid #E0E0E0;
}

.financial-table {
  width: 100%;
  min-width: 900px;
  border-collapse: collapse;
  background: white;
  table-layout: fixed;
}

.financial-table thead {
  background: #F5F5F5;
}

.financial-table th {
  padding: 16px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
  color: #333;
  border-bottom: 2px solid #E0E0E0;
}

.financial-table tbody tr {
  border-bottom: 1px solid #F0F0F0;
  transition: background-color 0.2s;
  animation: fadeInRow 0.5s ease-out;
}

.financial-table tbody tr:hover {
  background: #F9FAFB;
  transform: translateX(2px);
  box-shadow: -2px 0 0 #1678F3;
}

.financial-table tbody tr.row-pemasukan {
  border-left: 3px solid #22C55E;
}

.financial-table tbody tr.row-pengeluaran {
  border-left: 3px solid #EF4444;
}

.financial-table td {
  padding: 16px;
  font-size: 14px;
  color: #666;
}

/* Badge Styles */
.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-success {
  background: rgba(34, 197, 94, 0.1);
  color: #22C55E;
}

.badge-danger {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

@keyframes fadeInRow {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInRow {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.financial-table td {
  padding: 15px;
  font-size: 14px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.col-keterangan {
  width: 200px;
}

.col-tipe {
  width: 150px;
}

.col-jumlah {
  width: 150px;
}

.col-tanggal {
  width: 150px;
}

.col-transaksi {
  width: 150px;
}

/* Action Footer */
.action-footer {
  display: flex;
  justify-content: flex-end;
}

.btn-inventaris {
  background: #1678F3;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-inventaris:hover {
  background: #0d5bbf;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(22, 120, 243, 0.3);
}

.btn-inventaris i {
  font-size: 16px;
}

/* Pagination */
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: white;
  border-top: 1px solid #E0E0E0;
  gap: 20px;
  flex-wrap: wrap;
}

.pagination-info {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
}

.pagination-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.pagination-btn {
  min-width: 36px;
  height: 36px;
  border: 1px solid #E0E0E0;
  background: white;
  color: #333;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  font-weight: 500;
  padding: 0 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pagination-btn:hover:not(:disabled) {
  background: #F5F5F5;
  border-color: #1678F3;
  color: #1678F3;
}

.pagination-btn.active {
  background: #1678F3;
  color: white;
  border-color: #1678F3;
}

.pagination-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pagination-ellipsis {
  color: #999;
  padding: 0 4px;
  font-size: 14px;
}

.items-per-page {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.items-per-page label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.items-per-page select {
  padding: 8px 32px 8px 12px;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
  background: white;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23333' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
}

.items-per-page select:hover {
  border-color: #1678F3;
}

.items-per-page select:focus {
  outline: none;
  border-color: #1678F3;
  box-shadow: 0 0 0 3px rgba(22, 120, 243, 0.1);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 32px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-title {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin-bottom: 24px;
  text-align: center;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #1678F3;
  box-shadow: 0 0 0 3px rgba(22, 120, 243, 0.1);
}

.form-input:disabled {
  background: #F5F5F5;
  cursor: not-allowed;
}

textarea.form-input {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

select.form-input {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23333' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 40px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
}

.btn-cancel,
.btn-save {
  flex: 1;
  padding: 14px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel {
  background: #F5F5F5;
  color: #666;
}

.btn-cancel:hover {
  background: #E0E0E0;
}

.btn-save {
  background: linear-gradient(135deg, #1678F3 0%, #1565C0 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(22, 120, 243, 0.3);
}

.btn-save:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(22, 120, 243, 0.4);
}

.btn-save:active {
  transform: translateY(0);
}
</style>
