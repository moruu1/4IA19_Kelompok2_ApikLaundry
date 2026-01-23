<template>
  <div class="customers-container">
    <!-- Sidebar -->
    <div class="sidebar">
      <!-- Menu Icons -->
      <router-link to="/admin/dashboard" class="sidebar-icon">
        <i class="fas fa-th"></i>
      </router-link>
      
      <router-link to="/admin/customers" class="sidebar-icon active">
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
      <div class="customers-header">
        <h1 class="page-title">Pelanggan</h1>
        
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
        <!-- Search and Action Buttons Row -->
        <div class="top-actions">
          <!-- Search Bar -->
          <div class="search-container">
            <input 
              v-model="searchQuery"
              type="text" 
              placeholder="Cari pelanggan..."
              class="search-input"
            />
          </div>

          <!-- Action Buttons -->
          <div class="action-buttons">
            <button 
              class="btn-edit ripple-container" 
              @click="handleEdit"
              @mousedown="addRipple"
              data-tooltip="Edit data pelanggan terpilih"
            >
              <i class="fas fa-edit"></i>
              Edit Data
            </button>
            <button 
              class="btn-delete ripple-container" 
              @click="handleDelete"
              @mousedown="addRipple"
              data-tooltip="Hapus data pelanggan terpilih"
            >
              <i class="fas fa-trash"></i>
              Hapus Data
            </button>
            <button 
              class="btn-add ripple-container" 
              @click="handleAdd"
              @mousedown="addRipple"
              data-tooltip="Tambah pelanggan baru"
            >
              <i class="fas fa-plus"></i>
              Tambah Data
            </button>
          </div>
        </div>

        <!-- Table -->
        <div class="table-container">
          <!-- Loading Skeleton -->
          <div v-if="customerStore.loading">
            <table class="customers-table">
              <thead>
                <tr>
                  <th class="col-select"></th>
                  <th class="col-nama">Nama</th>
                  <th class="col-hp">No Hp</th>
                  <th class="col-alamat">Alamat</th>
                </tr>
              </thead>
            </table>
            <LoadingSkeleton :rows="5" :columns="skeletonColumns" />
          </div>

          <!-- Empty State -->
          <EmptyState 
            v-else-if="filteredCustomers.length === 0 && !searchQuery"
            icon="fas fa-users"
            title="Belum Ada Pelanggan"
            message="Mulai tambahkan pelanggan pertama Anda untuk mengelola data customer"
            actionText="Tambah Pelanggan"
            actionIcon="fas fa-plus"
            @action="handleAdd"
          />

          <!-- Search Empty State -->
          <EmptyState 
            v-else-if="filteredCustomers.length === 0 && searchQuery"
            icon="fas fa-search"
            title="Tidak Ada Hasil"
            :message="`Tidak ditemukan pelanggan dengan kata kunci '${searchQuery}'`"
          />

          <!-- Table with data -->
          <table v-else class="customers-table">
            <thead>
              <tr>
                <th class="col-select"></th>
                <th class="col-nama">Nama</th>
                <th class="col-hp">No Hp</th>
                <th class="col-alamat">Alamat</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="customer in paginatedCustomers" 
                :key="customer.id_customer"
                :class="{ 'selected': selectedCustomer === customer.id_customer }"
                @click="selectCustomer(customer.id_customer)"
              >
                <td class="col-select">
                  <div class="select-circle" :class="{ 'active': selectedCustomer === customer.id_customer }">
                    <i v-if="selectedCustomer === customer.id_customer" class="fas fa-check"></i>
                  </div>
                </td>
                <td class="col-nama">{{ customer.nama }}</td>
                <td class="col-hp">{{ customer.no_hp }}</td>
                <td class="col-alamat">{{ customer.alamat }}</td>
              </tr>
            </tbody>
          </table>

          <!-- Pagination Controls -->
          <div v-if="filteredCustomers.length > 0" class="pagination-container">
            <div class="pagination-info">
              Menampilkan {{ (currentPage - 1) * itemsPerPage + 1 }} - 
              {{ Math.min(currentPage * itemsPerPage, filteredCustomers.length) }} 
              dari {{ filteredCustomers.length }} data
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

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal modal-add" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">Edit Data Pelanggan</h2>
          <button class="close-button" @click="closeEditModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body modal-body-add">
          <div class="form-section">
            <div class="section-title">Edit Informasi Pelanggan</div>
            <div class="form-group">
              <label>Nama</label>
              <input v-model="editForm.nama" type="text" placeholder="Masukkan nama pelanggan" />
            </div>
            <div class="form-group">
              <label>No. HP</label>
              <input v-model="editForm.no_hp" type="text" placeholder="Masukkan nomor HP" />
            </div>
            <div class="form-group">
              <label>Alamat</label>
              <textarea v-model="editForm.alamat" rows="3" placeholder="Masukkan alamat lengkap"></textarea>
            </div>
            <button class="btn-submit" @click="saveEdit">Simpan</button>
          </div>
          <div class="image-section">
            <img src="@/assets/images/admindecor.png" alt="Customer Illustration" class="illustration-img">
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">Hapus Data Pelanggan</h2>
          <button class="close-button" @click="closeDeleteModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p>Apakah Anda yakin ingin menghapus data pelanggan ini?</p>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeDeleteModal">Batal</button>
          <button class="btn-confirm" @click="confirmDelete">Hapus</button>
        </div>
      </div>
    </div>

    <!-- Add Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click="closeAddModal">
      <div class="modal modal-add" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">Tambah Pelanggan</h2>
          <button class="close-button" @click="closeAddModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body modal-body-add">
          <div class="form-section">
            <div class="section-title">Daftarkan Pelanggan Baru</div>
            <div class="form-group">
              <label>Nama</label>
              <input v-model="addForm.nama" type="text" placeholder="Masukkan nama pelanggan" />
            </div>
            <div class="form-group">
              <label>Email</label>
              <input v-model="addForm.email" type="email" placeholder="Masukkan email" />
            </div>
            <div class="form-group">
              <label>No. HP</label>
              <input v-model="addForm.no_hp" type="text" placeholder="Masukkan nomor HP" />
            </div>
            <div class="form-group">
              <label>Alamat</label>
              <textarea v-model="addForm.alamat" rows="3" placeholder="Masukkan alamat lengkap"></textarea>
            </div>
            <div class="form-group">
              <label>Password</label>
              <input v-model="addForm.password" type="password" placeholder="Masukkan password untuk login" />
            </div>
            <button class="btn-submit" @click="saveAdd">Terima</button>
          </div>
          <div class="image-section">
            <img src="@/assets/images/admindecor.png" alt="Customer Illustration" class="illustration-img">
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
    <LoadingSpinner :show="loading" message="Memuat data..." />

    <!-- Confirm Dialog -->
    <ConfirmDialog 
      :show="showDeleteConfirm"
      title="Hapus Pelanggan"
      message="Apakah Anda yakin ingin menghapus pelanggan ini? Tindakan ini tidak dapat dibatalkan."
      confirmText="Hapus"
      cancelText="Batal"
      type="danger"
      @confirm="confirmDelete"
      @cancel="showDeleteConfirm = false"
      @close="showDeleteConfirm = false"
    />

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
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useCustomerStore } from '@/stores/customerStore'
import Breadcrumbs from '../../components/Breadcrumbs.vue'
import ToastNotification from '@/components/ToastNotification.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import LoadingSkeleton from '@/components/LoadingSkeleton.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import EmptyState from '@/components/EmptyState.vue'
import ProfileModal from '@/components/ProfileModal.vue'
import ChangePasswordModal from '@/components/ChangePasswordModal.vue'
import { useRipple } from '@/composables/useRipple'
import { useAnimations } from '@/composables/useAnimations'

const router = useRouter()
const authStore = useAuthStore()
const customerStore = useCustomerStore()
const addRipple = useRipple()
const { triggerSuccess, triggerError } = useAnimations()

const breadcrumbItems = ref([
  { label: 'Dashboard', path: '/admin/dashboard' },
  { label: 'Pelanggan' }
])

// State
const showProfileMenu = ref(false)
const searchQuery = ref('')
const selectedCustomer = ref(null)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const showAddModal = ref(false)
const loading = ref(false)
const dataLoading = ref(false)
const showDeleteConfirm = ref(false)
const showProfileModal = ref(false)
const showPasswordModal = ref(false)
const toast = ref({
  show: false,
  message: '',
  type: 'success'
})

// Pagination
const currentPage = ref(1)
const itemsPerPage = ref(10)

// Fetch data on mount
onMounted(async () => {
  await customerStore.fetchCustomers()
})

// Watch search query and reset to first page
watch(searchQuery, () => {
  currentPage.value = 1
})

// Skeleton columns configuration
const skeletonColumns = [
  { width: '5%' },
  { width: '25%' },
  { width: '20%' },
  { width: '50%' }
]

// Forms
const editForm = ref({
  id_customer: null,
  nama: '',
  no_hp: '',
  alamat: ''
})

const addForm = ref({
  nama: '',
  no_hp: '',
  alamat: ''
})

// Computed
const filteredCustomers = computed(() => {
  let filtered = customerStore.customers
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(customer => 
      customer.nama.toLowerCase().includes(query) ||
      customer.no_hp.includes(query) ||
      customer.alamat.toLowerCase().includes(query)
    )
  }
  
  return filtered
})

// Pagination computed properties
const totalPages = computed(() => {
  return Math.ceil(filteredCustomers.value.length / itemsPerPage.value)
})

const paginatedCustomers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredCustomers.value.slice(start, end)
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

// Methods
function toggleProfileMenu() {
  showProfileMenu.value = !showProfileMenu.value
}

function selectCustomer(id) {
  selectedCustomer.value = selectedCustomer.value === id ? null : id
}

function handleEdit() {
  if (!selectedCustomer.value) {
    toast.value = {
      show: true,
      message: 'Pilih pelanggan terlebih dahulu!',
      type: 'warning'
    }
    return
  }
  
  const customer = customerStore.customers.find(c => c.id_customer === selectedCustomer.value)
  if (customer) {
    editForm.value = { ...customer }
    showEditModal.value = true
  }
}

function handleDelete() {
  if (!selectedCustomer.value) {
    toast.value = {
      show: true,
      message: 'Pilih pelanggan terlebih dahulu!',
      type: 'warning'
    }
    return
  }
  showDeleteConfirm.value = true
}

async function confirmDelete() {
  loading.value = true
  showDeleteConfirm.value = false
  
  const result = await customerStore.deleteCustomer(selectedCustomer.value)
  
  if (result.success) {
    selectedCustomer.value = null
    toast.value = {
      show: true,
      message: 'Pelanggan berhasil dihapus!',
      type: 'success'
    }
    triggerSuccess()
  } else {
    toast.value = {
      show: true,
      message: `Gagal menghapus pelanggan: ${result.error}`,
      type: 'error'
    }
    triggerError()
  }
  
  loading.value = false
}

function handleAdd() {
  addForm.value = {
    nama: '',
    email: '',
    no_hp: '',
    alamat: '',
    password: ''
  }
  showAddModal.value = true
}

function closeEditModal() {
  showEditModal.value = false
}

function closeDeleteModal() {
  showDeleteModal.value = false
}

function closeAddModal() {
  showAddModal.value = false
}

async function saveEdit() {
  // Validation
  if (!editForm.value.nama || !editForm.value.no_hp || !editForm.value.alamat) {
    toast.value = {
      show: true,
      message: 'Semua field harus diisi!',
      type: 'warning'
    }
    return
  }
  
  loading.value = true
  
  const customerData = {
    nama: editForm.value.nama,
    no_hp: editForm.value.no_hp,
    alamat: editForm.value.alamat
  }
  
  const result = await customerStore.updateCustomer(editForm.value.id_customer, customerData)
  
  if (result.success) {
    showEditModal.value = false
    selectedCustomer.value = null
    toast.value = {
      show: true,
      message: 'Data pelanggan berhasil diperbarui!',
      type: 'success'
    }
    triggerSuccess()
  } else {
    toast.value = {
      show: true,
      message: `Gagal memperbarui pelanggan: ${result.error}`,
      type: 'error'
    }
    triggerError()
  }
  
  loading.value = false
}

async function saveAdd() {
  // Validation
  if (!addForm.value.nama || !addForm.value.email || !addForm.value.no_hp || !addForm.value.alamat || !addForm.value.password) {
    toast.value = {
      show: true,
      message: 'Semua field harus diisi!',
      type: 'warning'
    }
    return
  }
  
  // Validate email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(addForm.value.email)) {
    toast.value = {
      show: true,
      message: 'Format email tidak valid!',
      type: 'warning'
    }
    return
  }
  
  // Validate password length
  if (addForm.value.password.length < 6) {
    toast.value = {
      show: true,
      message: 'Password minimal 6 karakter!',
      type: 'warning'
    }
    return
  }
  
  loading.value = true
  
  const customerData = {
    nama: addForm.value.nama,
    email: addForm.value.email,
    no_hp: addForm.value.no_hp,
    alamat: addForm.value.alamat,
    password: addForm.value.password
  }
  
  const result = await customerStore.createCustomer(customerData)
  
  if (result.success) {
    showAddModal.value = false
    toast.value = {
      show: true,
      message: 'Pelanggan baru berhasil ditambahkan!',
      type: 'success'
    }
    triggerSuccess()
  } else {
    toast.value = {
      show: true,
      message: `Gagal menambahkan pelanggan: ${result.error}`,
      type: 'error'
    }
    triggerError()
  }
  
  loading.value = false
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

async function handleLogout() {
  await authStore.logout()
  router.replace('/login')
}
</script>

<style scoped>
/* Page Container */
.customers-container {
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
.customers-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30px;
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

/* User Profile */
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

/* Content Section */
.content-section {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  animation: slideUp 0.5s ease-out;
  transition: box-shadow 0.3s ease;
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

/* Top Actions Row */
.top-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 20px;
}

/* Search Container */
.search-container {
  flex: 1;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 12px 20px 12px 45px;
  border: 2px solid #E0E0E0;
  border-radius: 12px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  transition: all 0.3s ease;
  background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23999" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>') no-repeat 15px center;
  background-size: 18px;
}

.search-input:focus {
  outline: none;
  border-color: #1678F3;
  box-shadow: 0 0 0 4px rgba(22, 120, 243, 0.1);
  transform: translateY(-2px);
}

.search-input::placeholder {
  color: #999;
  font-style: italic;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 12px;
}

.action-buttons button {
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.action-buttons button::before {
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

.action-buttons button:hover::before {
  width: 300px;
  height: 300px;
}

.btn-edit {
  background: linear-gradient(135deg, #FFA726 0%, #FB8C00 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(255, 167, 38, 0.2);
}

.btn-edit:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(255, 167, 38, 0.4);
}

.btn-edit:active {
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(255, 167, 38, 0.3);
}

.btn-delete {
  background: linear-gradient(135deg, #EF5350 0%, #E53935 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(239, 83, 80, 0.2);
}

.btn-delete:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(239, 83, 80, 0.4);
}

.btn-delete:active {
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(239, 83, 80, 0.3);
}

.btn-add {
  background: linear-gradient(135deg, #1678F3 0%, #1565C0 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(22, 120, 243, 0.2);
  animation: pulse-add 2s infinite;
}

.btn-add:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 6px 16px rgba(22, 120, 243, 0.4);
  animation: none;
}

.btn-add:active {
  transform: translateY(-1px) scale(1.02);
  box-shadow: 0 3px 10px rgba(22, 120, 243, 0.3);
}

@keyframes pulse-add {
  0%, 100% {
    box-shadow: 0 2px 8px rgba(22, 120, 243, 0.2);
  }
  50% {
    box-shadow: 0 2px 12px rgba(22, 120, 243, 0.4);
  }
}

/* Table Container */
.table-container {
  border-radius: 16px;
  border: 1px solid #E0E0E0;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  background: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.table-container:hover {
  box-shadow: 0 8px 30px rgba(22, 120, 243, 0.12);
}

/* Table */
.customers-table {
  width: 100%;
  min-width: 900px;
  border-collapse: collapse;
  font-family: 'Inter', sans-serif;
  table-layout: fixed;
}

.customers-table thead {
  background: #F5F5F5;
}

.customers-table th {
  padding: 15px 12px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: #666666;
  border-bottom: 2px solid #E0E0E0;
}

.customers-table td {
  padding: 15px 12px;
  font-size: 13px;
  color: #333333;
  border-bottom: 1px solid #F0F0F0;
}

.customers-table tbody tr {
  cursor: pointer;
  transition: all 0.3s ease;
  animation: fadeInRow 0.5s ease-out;
}

.customers-table tbody tr:hover {
  background: #F8F9FA;
  transform: translateX(4px);
  box-shadow: -4px 0 0 #1678F3;
}

.customers-table tbody tr.selected {
  background: linear-gradient(90deg, #E3F2FD 0%, #F8FBFF 100%);
  border-left: 4px solid #1678F3;
}

@keyframes fadeInRow {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.col-select {
  width: 80px;
  text-align: center;
}

.col-nama {
  width: 25%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.col-hp {
  width: 20%;
}

.col-alamat {
  width: auto;
  max-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Selection Checkbox */
.select-circle {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #E0E0E0;
  position: relative;
}

.select-circle::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 8px;
  background: #1678F3;
  transform: scale(0);
  transition: transform 0.3s ease;
}

.select-circle i {
  position: relative;
  z-index: 1;
  color: white;
  font-size: 16px;
  opacity: 0;
  transform: scale(0) rotate(-180deg);
  transition: all 0.3s ease;
}

.select-circle.active {
  background: #1678F3;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(22, 120, 243, 0.4);
}

.select-circle.active::before {
  transform: scale(1);
}

.select-circle.active i {
  opacity: 1;
  transform: scale(1) rotate(0deg);
}

.select-circle i {
  color: white;
  font-size: 18px;
}

.select-circle:not(.active) i {
  display: none;
}

.col-nama {
  width: 25%;
}

.col-hp {
  width: 20%;
}

.col-alamat {
  width: auto;
}

/* Modal Overlay */
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
  z-index: 2000;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Modal */
.modal {
  background: white;
  border-radius: 20px;
  padding: 30px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.3s;
}

.modal.modal-add {
  max-width: 1000px !important;
  width: 85% !important;
  padding: 35px 50px !important;
}

@keyframes slideUp {
  from {
    transform: translateY(50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Modal Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #F0F0F0;
}

.modal-title {
  font-family: 'Inter', sans-serif;
  font-size: 22px;
  font-weight: 700;
  color: #000000;
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  color: #999999;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s;
}

.close-button:hover {
  background: #F5F5F5;
  color: #333333;
}

/* Modal Body */
.modal-body {
  margin-bottom: 25px;
}

.modal-body-add {
  display: flex;
  gap: 50px;
  margin-bottom: 0;
  align-items: stretch;
}

.form-section {
  flex: 0 0 45%;
  background: #F5F5F5;
  padding: 25px 30px;
  border-radius: 15px;
  display: flex;
  flex-direction: column;
}

.section-title {
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  font-weight: 600;
  color: #1678F3;
  margin-bottom: 15px;
}

.image-section {
  flex: 0 0 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
}

.illustration-img {
  width: 100%;
  max-width: 450px;
  height: auto;
  object-fit: contain;
}

.btn-submit {
  width: 100%;
  padding: 12px;
  background: #1678F3;
  color: white;
  border: none;
  border-radius: 8px;
  font-family: 'Inter', sans-serif;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 5px;
}

.btn-submit:hover {
  background: #1565C0;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(22, 120, 243, 0.3);
}

.form-group {
  margin-bottom: 12px;
}

.form-group label {
  display: block;
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  font-weight: 600;
  color: #333333;
  margin-bottom: 5px;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  transition: all 0.3s;
  box-sizing: border-box;
  background: white;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #1678F3;
  box-shadow: 0 0 0 3px rgba(22, 120, 243, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

/* Modal Footer */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 15px;
  border-top: 2px solid #F0F0F0;
}

.modal-footer button {
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-cancel {
  background: #F5F5F5;
  color: #666666;
}

.btn-cancel:hover {
  background: #E0E0E0;
  color: #333333;
}

.btn-save {
  background: #1678F3;
  color: white;
}

.btn-save:hover {
  background: #1565C0;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(22, 120, 243, 0.3);
}

.btn-confirm {
  background: #EF5350;
  color: white;
}

.btn-confirm:hover {
  background: #E53935;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 83, 80, 0.3);
}

/* Delete Modal Text */
.modal-body p {
  font-family: 'Inter', sans-serif;
  font-size: 15px;
  color: #333333;
  line-height: 1.6;
  margin: 0;
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

  .customers-header {
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

  .content-section {
    padding: 14px !important;
    width: 100% !important;
    box-sizing: border-box !important;
    overflow-x: hidden !important;
  }

  .action-buttons {
    display: flex !important;
    flex-direction: column !important;
    gap: 10px !important;
    margin-bottom: 16px !important;
  }

  .action-buttons button {
    width: 100% !important;
    min-height: 48px !important;
    font-size: 15px !important;
    box-sizing: border-box !important;
  }

  .search-container {
    width: 100% !important;
    margin-bottom: 16px !important;
  }

  .search-input {
    width: 100% !important;
    box-sizing: border-box !important;
    font-size: 16px !important;
    min-height: 48px !important;
  }

  .modal {
    width: 95% !important;
    max-width: 95vw !important;
    padding: 20px !important;
    box-sizing: border-box !important;
  }

  .table-container {
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    margin: 0 -14px !important;
    padding: 0 14px !important;
  }

  .customers-table {
    font-size: 13px !important;
    min-width: 800px !important;
  }

  .customers-table th,
  .customers-table td {
    padding: 10px 8px !important;
  }
  
  .pagination-container {
    flex-direction: column !important;
    align-items: stretch !important;
    gap: 16px !important;
  }
  
  .pagination-info {
    text-align: center !important;
    font-size: 14px !important;
  }
  
  .pagination-controls {
    justify-content: center !important;
    flex-wrap: wrap !important;
  }

  .pagination-button {
    min-width: 44px !important;
    height: 44px !important;
    font-size: 15px !important;
  }
  
  .items-per-page {
    justify-content: center !important;
  }

  .items-per-page select {
    min-height: 44px !important;
    font-size: 14px !important;
  }
}
</style>
