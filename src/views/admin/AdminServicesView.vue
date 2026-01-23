<template>
  <div class="services-container">
    <!-- Sidebar -->
    <div class="sidebar">
      <!-- Menu Icons -->
      <router-link to="/admin/dashboard" class="sidebar-icon">
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

      <router-link to="/admin/services" class="sidebar-icon active">
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
      <div class="services-header">
        <h1 class="page-title">Layanan</h1>
        
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
          <button class="btn-edit" @click="handleEdit">
            <i class="fas fa-edit"></i>
            Edit Layanan
          </button>
          <button class="btn-delete" @click="handleDelete">
            <i class="fas fa-trash"></i>
            Hapus Layanan
          </button>
          <button class="btn-add" @click="handleAdd">
            <i class="fas fa-plus"></i>
            Tambah Layanan
          </button>
        </div>

        <!-- Search Bar -->
        <div class="search-container">
          <i class="fas fa-search search-icon"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Cari nama layanan..."
            class="search-input"
          />
        </div>

        <!-- Table -->
        <div class="table-container">
          <!-- Loading State -->
          <div v-if="serviceStore.loading" class="loading-state">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Memuat data...</p>
          </div>

          <!-- Empty State -->
          <EmptyState 
            v-else-if="serviceStore.services.length === 0"
            icon="fas fa-concierge-bell"
            title="Belum Ada Layanan"
            message="Layanan akan muncul di sini setelah ditambahkan"
            actionText="Tambah Layanan"
            actionIcon="fas fa-plus"
            @action="handleAdd"
          />

          <table v-else class="services-table">
            <thead>
              <tr>
                <th class="col-select"></th>
                <th class="col-nama">Nama Layanan</th>
                <th class="col-harga">Harga</th>
                <th class="col-deskripsi">Deskripsi</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="service in paginatedServices" 
                :key="service.id_service"
                :class="{ 'selected': selectedService === service.id_service }"
                @click="selectService(service.id_service)"
              >
                <td class="col-select">
                  <div class="select-circle" :class="{ 'active': selectedService === service.id_service }">
                    <i v-if="selectedService === service.id_service" class="fas fa-check"></i>
                  </div>
                </td>
                <td class="col-nama">{{ service.nama_layanan }}</td>
                <td class="col-harga">Rp {{ service.harga_per_unit?.toLocaleString('id-ID') || 0 }}</td>
                <td class="col-deskripsi">{{ service.deskripsi || '-' }}</td>
              </tr>
            </tbody>
          </table>

          <!-- Pagination Controls -->
          <div v-if="serviceStore.services.length > 0" class="pagination-container">
            <div class="pagination-info">
              Menampilkan {{ (currentPage - 1) * itemsPerPage + 1 }} - 
              {{ Math.min(currentPage * itemsPerPage, filteredServices.length) }} 
              dari {{ filteredServices.length }} data
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
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Edit Layanan</h2>
          <button class="modal-close" @click="closeEditModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <form @submit.prevent="submitEdit" class="modal-form">
          <div class="form-group">
            <label>Nama Layanan <span class="required">*</span></label>
            <input v-model="editForm.nama_layanan" type="text" placeholder="Contoh: Cuci Kering" required />
          </div>
          <div class="form-group">
            <label>Harga (Rp) <span class="required">*</span></label>
            <input v-model.number="editForm.harga_per_unit" type="number" min="0" placeholder="Contoh: 5000" required />
          </div>
          <div class="form-group">
            <label>Deskripsi</label>
            <textarea v-model="editForm.deskripsi" rows="3" placeholder="Deskripsi layanan (opsional)"></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeEditModal" class="btn-cancel">Batal</button>
            <button type="submit" class="btn-submit">Simpan Perubahan</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Add Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="closeAddModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Tambah Layanan Baru</h2>
          <button class="modal-close" @click="closeAddModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <form @submit.prevent="submitAdd" class="modal-form">
          <div class="form-group">
            <label>Nama Layanan <span class="required">*</span></label>
            <input v-model="addForm.nama_layanan" type="text" placeholder="Contoh: Cuci Kering" required />
          </div>
          <div class="form-group">
            <label>Harga (Rp) <span class="required">*</span></label>
            <input v-model.number="addForm.harga_per_unit" type="number" min="0" placeholder="Contoh: 5000" required />
          </div>
          <div class="form-group">
            <label>Deskripsi</label>
            <textarea v-model="addForm.deskripsi" rows="3" placeholder="Deskripsi layanan (opsional)"></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeAddModal" class="btn-cancel">Batal</button>
            <button type="submit" class="btn-submit">Tambah Layanan</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="modal-content modal-small">
        <div class="modal-header">
          <h2>Konfirmasi Hapus</h2>
          <button class="modal-close" @click="closeDeleteModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p>Apakah Anda yakin ingin menghapus layanan ini?</p>
          <p class="warning-text">Tindakan ini tidak dapat dibatalkan.</p>
        </div>
        <div class="modal-actions">
          <button type="button" @click="closeDeleteModal" class="btn-cancel">Batal</button>
          <button type="button" @click="confirmDelete" class="btn-delete-confirm">Hapus</button>
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
import { useServiceStore } from '@/stores/serviceStore'
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import ToastNotification from '@/components/ToastNotification.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ProfileModal from '@/components/ProfileModal.vue'
import ChangePasswordModal from '@/components/ChangePasswordModal.vue'
import EmptyState from '@/components/EmptyState.vue'

const router = useRouter()
const authStore = useAuthStore()
const serviceStore = useServiceStore()

// Breadcrumbs
const breadcrumbItems = ref([
  { label: 'Dashboard', path: '/admin/dashboard' },
  { label: 'Layanan' }
])

// Fetch services on mount
onMounted(async () => {
  await serviceStore.fetchServices()
})

// UI State
const showProfileMenu = ref(false)
const showProfileModal = ref(false)
const showPasswordModal = ref(false)
const showEditModal = ref(false)
const showAddModal = ref(false)
const showDeleteModal = ref(false)
const toast = ref({ show: false, message: '', type: 'success' })
const loading = ref(false)

// Search & Pagination
const searchQuery = ref('')
const currentPage = ref(1)
const itemsPerPage = ref(10)
const selectedService = ref(null)

// Forms
const editForm = ref({
  nama_layanan: '',
  harga_per_unit: 0,
  deskripsi: ''
})

const addForm = ref({
  nama_layanan: '',
  harga_per_unit: 0,
  deskripsi: ''
})

// Computed
const filteredServices = computed(() => {
  if (!searchQuery.value) return serviceStore.services
  
  const query = searchQuery.value.toLowerCase()
  return serviceStore.services.filter(service => 
    service.nama_layanan?.toLowerCase().includes(query)
  )
})

const totalPages = computed(() => Math.ceil(filteredServices.value.length / itemsPerPage.value))

const paginatedServices = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredServices.value.slice(start, end)
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

// Functions
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

// Functions
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

const selectService = (id) => {
  selectedService.value = selectedService.value === id ? null : id
}

// Edit Functions
const handleEdit = () => {
  if (!selectedService.value) {
    toast.value = {
      show: true,
      message: 'Pilih layanan yang ingin diedit',
      type: 'warning'
    }
    return
  }
  
  const service = serviceStore.services.find(s => s.id_service === selectedService.value)
  if (service) {
    editForm.value = {
      nama_layanan: service.nama_layanan,
      harga_per_unit: service.harga_per_unit,
      deskripsi: service.deskripsi || ''
    }
    showEditModal.value = true
  }
}

const closeEditModal = () => {
  showEditModal.value = false
  editForm.value = {
    nama_layanan: '',
    harga_per_unit: 0,
    deskripsi: ''
  }
}

const submitEdit = async () => {
  loading.value = true
  try {
    const serviceData = {
      nama_layanan: editForm.value.nama_layanan,
      harga_per_unit: editForm.value.harga_per_unit,
      deskripsi: editForm.value.deskripsi || null
    }
    
    const result = await serviceStore.updateService(selectedService.value, serviceData)
    
    if (result.success) {
      closeEditModal()
      selectedService.value = null
      toast.value = {
        show: true,
        message: 'Layanan berhasil diperbarui!',
        type: 'success'
      }
    } else {
      toast.value = {
        show: true,
        message: result.error || 'Gagal memperbarui layanan',
        type: 'error'
      }
    }
  } catch (error) {
    console.error('Error updating service:', error)
    toast.value = {
      show: true,
      message: 'Terjadi kesalahan saat memperbarui layanan',
      type: 'error'
    }
  } finally {
    loading.value = false
  }
}

// Add Functions
const handleAdd = () => {
  showAddModal.value = true
}

const closeAddModal = () => {
  showAddModal.value = false
  addForm.value = {
    nama_layanan: '',
    harga_per_unit: 0,
    deskripsi: ''
  }
}

const submitAdd = async () => {
  loading.value = true
  try {
    const serviceData = {
      nama_layanan: addForm.value.nama_layanan,
      harga_per_unit: addForm.value.harga_per_unit,
      deskripsi: addForm.value.deskripsi || null
    }
    
    const result = await serviceStore.createService(serviceData)
    
    if (result.success) {
      closeAddModal()
      toast.value = {
        show: true,
        message: 'Layanan berhasil ditambahkan!',
        type: 'success'
      }
    } else {
      toast.value = {
        show: true,
        message: result.error || 'Gagal menambahkan layanan',
        type: 'error'
      }
    }
  } catch (error) {
    console.error('Error adding service:', error)
    toast.value = {
      show: true,
      message: 'Terjadi kesalahan saat menambahkan layanan',
      type: 'error'
    }
  } finally {
    loading.value = false
  }
}

// Delete Functions
const handleDelete = () => {
  if (!selectedService.value) {
    toast.value = {
      show: true,
      message: 'Pilih layanan yang ingin dihapus',
      type: 'warning'
    }
    return
  }
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
}

const confirmDelete = async () => {
  loading.value = true
  try {
    const result = await serviceStore.deleteService(selectedService.value)
    
    if (result.success) {
      closeDeleteModal()
      selectedService.value = null
      toast.value = {
        show: true,
        message: 'Layanan berhasil dihapus!',
        type: 'success'
      }
    } else {
      toast.value = {
        show: true,
        message: result.error || 'Gagal menghapus layanan',
        type: 'error'
      }
    }
  } catch (error) {
    console.error('Error deleting service:', error)
    toast.value = {
      show: true,
      message: 'Terjadi kesalahan saat menghapus layanan',
      type: 'error'
    }
  } finally {
    loading.value = false
  }
}

// Pagination
const goToNextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const goToPreviousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}
</script>

<style scoped>
/* Use same styles as AdminInventoryView.vue */
.services-container {
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
  margin: 10px 0;
  color: #999999;
  text-decoration: none;
  border-radius: 12px;
  transition: all 0.3s;
}

.sidebar-icon:hover {
  background: #F0F7FF;
  color: #1678F3;
}

.sidebar-icon.active {
  background: #1678F3;
  color: white;
}

.sidebar-icon i {
  font-size: 22px;
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
  margin-left: 80px;
  flex: 1;
  padding: 30px 40px;
}

/* Header */
.services-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-title {
  font-family: 'Inter', sans-serif;
  font-size: 32px;
  font-weight: 700;
  color: #1678F3;
  margin: 0;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 15px;
  cursor: pointer;
  padding: 10px 20px;
  border-radius: 12px;
  transition: background 0.3s;
  position: relative;
}

.user-profile:hover {
  background: #F5F5F5;
}

.user-avatar {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
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

/* Content Section */
.content-section {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
}

.action-buttons button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-edit {
  background: #FFA500;
  color: white;
}

.btn-edit:hover {
  background: #FF8C00;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 165, 0, 0.3);
}

.btn-delete {
  background: #FF4757;
  color: white;
}

.btn-delete:hover {
  background: #E63946;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 71, 87, 0.3);
}

.btn-add {
  background: #1678F3;
  color: white;
}

.btn-add:hover {
  background: #0D5BBF;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(22, 120, 243, 0.3);
}

/* Search */
.search-container {
  position: relative;
  margin-bottom: 25px;
}

.search-icon {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  color: #999999;
  font-size: 16px;
}

.search-input {
  width: 100%;
  padding: 14px 20px 14px 50px;
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

/* Table */
.table-container {
  overflow-x: auto;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #999999;
}

.loading-state i {
  font-size: 48px;
  margin-bottom: 15px;
  color: #1678F3;
}

.loading-state p {
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  margin: 0;
}

.services-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'Inter', sans-serif;
}

.services-table thead {
  background: #F8F9FA;
}

.services-table th {
  text-align: left;
  padding: 15px 20px;
  font-size: 14px;
  font-weight: 600;
  color: #666666;
  border-bottom: 2px solid #E0E0E0;
}

.services-table tbody tr {
  border-bottom: 1px solid #F0F0F0;
  transition: all 0.3s;
  cursor: pointer;
}

.services-table tbody tr:hover {
  background: #F8F9FA;
}

.services-table tbody tr.selected {
  background: #E8F4FF;
}

.services-table td {
  padding: 18px 20px;
  font-size: 14px;
  color: #333333;
}

.col-select {
  width: 60px;
}

.select-circle {
  width: 24px;
  height: 24px;
  border: 2px solid #D0D0D0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.select-circle.active {
  background: #1678F3;
  border-color: #1678F3;
}

.select-circle i {
  color: white;
  font-size: 12px;
}

.col-nama {
  width: 30%;
  font-weight: 500;
}

.col-harga {
  width: 20%;
  font-weight: 600;
  color: #1678F3;
}

.col-deskripsi {
  width: 40%;
  color: #666666;
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

.pagination-btn i {
  font-size: 12px;
  display: inline-block;
}

.pagination-btn .fa-chevron-left,
.pagination-btn .fa-chevron-right {
  font-size: 12px !important;
  line-height: 1;
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

.pagination-text {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #333333;
  font-weight: 500;
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
  outline: none;
  transition: border-color 0.2s;
}

.items-per-page select:focus {
  border-color: #1678F3;
}

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-content.modal-small {
  max-width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 30px;
  border-bottom: 2px solid #F0F0F0;
}

.modal-header h2 {
  font-family: 'Inter', sans-serif;
  font-size: 20px;
  font-weight: 700;
  color: #333333;
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #F5F5F5;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  color: #666666;
}

.modal-close:hover {
  background: #E0E0E0;
  color: #333333;
}

.modal-body {
  padding: 25px 30px;
}

.modal-body p {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #666666;
  margin: 0 0 10px 0;
}

.warning-text {
  color: #FF4757;
  font-weight: 600;
}

.modal-form {
  padding: 25px 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: #333333;
  margin-bottom: 8px;
}

.required {
  color: #FF4757;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #E0E0E0;
  border-radius: 10px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #1678F3;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  padding: 20px 30px;
  border-top: 2px solid #F0F0F0;
}

.btn-cancel,
.btn-submit,
.btn-delete-confirm {
  flex: 1;
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
}

.btn-submit {
  background: #1678F3;
  color: white;
}

.btn-submit:hover {
  background: #0D5BBF;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(22, 120, 243, 0.3);
}

.btn-delete-confirm {
  background: #FF4757;
  color: white;
}

.btn-delete-confirm:hover {
  background: #E63946;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 71, 87, 0.3);
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

  .services-header {
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

  .table-container {
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    margin: 0 -14px !important;
    padding: 0 14px !important;
  }

  .services-table {
    font-size: 13px !important;
    min-width: 700px !important;
  }

  .services-table th,
  .services-table td {
    padding: 10px 8px !important;
  }

  .modal {
    width: 95% !important;
    padding: 20px !important;
  }

  .btn-cancel,
  .btn-submit,
  .btn-delete-confirm {
    min-height: 44px !important;
    font-size: 15px !important;
  }
}

</style>
