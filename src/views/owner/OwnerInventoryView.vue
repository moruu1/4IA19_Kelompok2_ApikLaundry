<template>
  <div class="inventory-container">
    <!-- Sidebar -->
    <div class="sidebar">
      <!-- Menu Icons -->
      <router-link to="/owner/dashboard" class="sidebar-icon">
        <i class="fas fa-th"></i>
      </router-link>
      
      <router-link to="/owner/reports" class="sidebar-icon">
        <i class="fas fa-file-invoice-dollar"></i>
      </router-link>

      <router-link to="/owner/inventory" class="sidebar-icon active">
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
      <div class="inventory-header">
        <h1 class="page-title">Inventaris</h1>
        
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
            Edit Inventaris
          </button>
          <button class="btn-delete" @click="handleDelete">
            <i class="fas fa-trash"></i>
            Hapus Inventaris
          </button>
          <button class="btn-add" @click="handleAdd">
            <i class="fas fa-plus"></i>
            Tambah Inventaris
          </button>
        </div>

        <!-- Search Bar -->
        <div class="search-container">
          <i class="fas fa-search search-icon"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Cari nama barang atau unit..."
            class="search-input"
          />
        </div>

        <!-- Table -->
        <div class="table-container">
          <!-- Loading State -->
          <div v-if="inventoryStore.loading" class="loading-state">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Memuat data...</p>
          </div>

          <!-- Empty State -->
          <EmptyState 
            v-else-if="inventoryStore.inventoryItems.length === 0"
            icon="fas fa-boxes"
            title="Belum Ada Inventaris"
            message="Inventaris akan muncul di sini setelah ditambahkan"
            actionText="Tambah Inventaris"
            actionIcon="fas fa-plus"
            @action="handleAdd"
          />

          <table v-else class="inventory-table">
            <thead>
              <tr>
                <th class="col-select"></th>
                <th class="col-nama">Nama Barang</th>
                <th class="col-stok">Stok Sisa</th>
                <th class="col-unit">Unit</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="item in paginatedItems" 
                :key="item.id_inventory_item"
                :class="{ 'selected': selectedItem === item.id_inventory_item, 'low-stock': item.stok_sisa <= 10 }"
                @click="selectItem(item.id_inventory_item)"
              >
                <td class="col-select">
                  <div class="select-circle" :class="{ 'active': selectedItem === item.id_inventory_item }">
                    <i v-if="selectedItem === item.id_inventory_item" class="fas fa-check"></i>
                  </div>
                </td>
                <td class="col-nama">
                  {{ item.nama_barang }}
                  <span v-if="item.stok_sisa <= 10" class="stock-alert">
                    <i class="fas fa-exclamation-triangle"></i> Stok Menipis
                  </span>
                </td>
                <td class="col-stok">{{ item.stok_sisa }}</td>
                <td class="col-unit">{{ item.unit }}</td>
              </tr>
            </tbody>
          </table>

          <!-- Pagination Controls -->
          <div v-if="inventoryStore.inventoryItems.length > 0" class="pagination-container">
            <div class="pagination-info">
              Menampilkan {{ (currentPage - 1) * itemsPerPage + 1 }}-{{ Math.min(currentPage * itemsPerPage, filteredItems.length) }} dari {{ filteredItems.length }} data
            </div>

            <div class="pagination-controls">
              <div class="items-per-page">
                <label>Tampilkan:</label>
                <select v-model.number="itemsPerPage">
                  <option :value="5">5</option>
                  <option :value="10">10</option>
                  <option :value="25">25</option>
                  <option :value="50">50</option>
                </select>
              </div>

              <div class="page-buttons">
                <button 
                  @click="previousPage" 
                  :disabled="currentPage === 1"
                  class="page-btn"
                >
                  <i class="fas fa-chevron-left"></i>
                </button>

                <button
                  v-for="page in pageNumbers"
                  :key="page"
                  @click="goToPage(page)"
                  class="page-btn"
                  :class="{ active: currentPage === page }"
                >
                  {{ page }}
                </button>

                <button 
                  @click="nextPage" 
                  :disabled="currentPage === totalPages"
                  class="page-btn"
                >
                  <i class="fas fa-chevron-right"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Edit Inventaris</h2>
          <button class="close-btn" @click="showEditModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="modal-left">
            <div class="form-group">
              <label>Nama Barang</label>
              <input v-model="editForm.nama_barang" type="text" placeholder="Masukkan nama barang" required />
            </div>
            
            <div class="form-group">
              <label>Stok Sisa</label>
              <input v-model.number="editForm.stok_sisa" type="number" min="0" placeholder="Masukkan jumlah stok" required />
            </div>
            
            <div class="form-group">
              <label>Unit</label>
              <input v-model="editForm.unit" type="text" placeholder="Masukkan unit (Liter/Pack/dll)" required />
            </div>
            
            <button type="button" @click="saveEdit" class="submit-btn">Simpan Perubahan</button>
          </div>
          
          <div class="modal-right">
            <div class="decor-placeholder">
              <i class="fas fa-box-open"></i>
              <p>Inventaris</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Tambah Inventaris</h2>
          <button class="close-btn" @click="showAddModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="modal-left">
            <div class="form-group">
              <label>Nama Barang</label>
              <input v-model="addForm.nama_barang" type="text" placeholder="Masukkan nama barang" required />
            </div>
            
            <div class="form-group">
              <label>Stok Sisa</label>
              <input v-model.number="addForm.stok_sisa" type="number" min="0" placeholder="Masukkan jumlah stok" required />
            </div>
            
            <div class="form-group">
              <label>Unit</label>
              <input v-model="addForm.unit" type="text" placeholder="Masukkan unit (Liter/Pack/dll)" required />
            </div>
            
            <button type="button" @click="saveAdd" class="submit-btn">Tambah Inventaris</button>
          </div>
          
          <div class="modal-right">
            <div class="decor-placeholder">
              <i class="fas fa-box-open"></i>
              <p>Inventaris</p>
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

    <!-- Confirm Dialog -->
    <ConfirmDialog 
      :show="showDeleteConfirm"
      title="Hapus Inventaris"
      message="Apakah Anda yakin ingin menghapus inventaris ini?"
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
import { useInventoryStore } from '@/stores/inventoryStore'
import Breadcrumbs from '../../components/Breadcrumbs.vue'
import ToastNotification from '@/components/ToastNotification.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import EmptyState from '@/components/EmptyState.vue'
import ProfileModal from '@/components/ProfileModal.vue'
import ChangePasswordModal from '@/components/ChangePasswordModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const inventoryStore = useInventoryStore()

// Search and pagination
const searchQuery = ref('')
const currentPage = ref(1)
const itemsPerPage = ref(10)

const breadcrumbItems = ref([
  { label: 'Dashboard', path: '/owner/dashboard' },
  { label: 'Inventaris' }
])

const showProfileMenu = ref(false)
const selectedItem = ref(null)
const showEditModal = ref(false)
const showAddModal = ref(false)
const loading = ref(false)
const showDeleteConfirm = ref(false)
const showProfileModal = ref(false)
const showPasswordModal = ref(false)
const toast = ref({
  show: false,
  message: '',
  type: 'success'
})

// Fetch data on mount
onMounted(async () => {
  await inventoryStore.fetchInventoryItems()
})

// Watch search to reset pagination
watch(searchQuery, () => {
  currentPage.value = 1
})

// Filtered and paginated items
const filteredItems = computed(() => {
  let filtered = inventoryStore.inventoryItems
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(item => 
      item.nama_barang.toLowerCase().includes(query) ||
      item.unit.toLowerCase().includes(query)
    )
  }
  
  return filtered
})

const totalPages = computed(() => {
  return Math.ceil(filteredItems.value.length / itemsPerPage.value)
})

const paginatedItems = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredItems.value.slice(start, end)
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

const editForm = ref({
  id_inventory_item: null,
  nama_barang: '',
  stok_sisa: 0,
  unit: ''
})

const addForm = ref({
  nama_barang: '',
  stok_sisa: 0,
  unit: ''
})

function toggleProfileMenu() {
  showProfileMenu.value = !showProfileMenu.value
}

function selectItem(id) {
  selectedItem.value = selectedItem.value === id ? null : id
}

function handleEdit() {
  if (!selectedItem.value) {
    toast.value = {
      show: true,
      message: 'Pilih inventaris terlebih dahulu',
      type: 'warning'
    }
    return
  }
  
  const item = inventoryStore.inventoryItems.find(i => i.id_inventory_item === selectedItem.value)
  if (item) {
    editForm.value = {
      id_inventory_item: item.id_inventory_item,
      nama_barang: item.nama_barang,
      stok_sisa: item.stok_sisa,
      unit: item.unit
    }
    showEditModal.value = true
  }
}

function handleDelete() {
  if (!selectedItem.value) {
    toast.value = {
      show: true,
      message: 'Pilih inventaris terlebih dahulu',
      type: 'warning'
    }
    return
  }
  showDeleteConfirm.value = true
}

function handleAdd() {
  addForm.value = {
    nama_barang: '',
    stok_sisa: 0,
    unit: ''
  }
  showAddModal.value = true
}

async function saveEdit() {
  if (!editForm.value.nama_barang || !editForm.value.unit) {
    toast.value = {
      show: true,
      message: 'Harap lengkapi semua field!',
      type: 'warning'
    }
    return
  }
  
  loading.value = true
  
  const result = await inventoryStore.updateInventoryItem(
    editForm.value.id_inventory_item,
    {
      nama_barang: editForm.value.nama_barang,
      stok_sisa: editForm.value.stok_sisa,
      unit: editForm.value.unit
    }
  )
  
  if (result.success) {
    toast.value = {
      show: true,
      message: 'Inventaris berhasil diperbarui!',
      type: 'success'
    }
    await inventoryStore.fetchInventoryItems()
    selectedItem.value = null
  } else {
    toast.value = {
      show: true,
      message: result.error || 'Gagal memperbarui inventaris',
      type: 'error'
    }
  }
  
  loading.value = false
  showEditModal.value = false
}

async function saveAdd() {
  if (!addForm.value.nama_barang || !addForm.value.unit) {
    toast.value = {
      show: true,
      message: 'Harap lengkapi semua field!',
      type: 'warning'
    }
    return
  }
  
  loading.value = true
  
  const result = await inventoryStore.createInventoryItem({
    nama_barang: addForm.value.nama_barang,
    stok_sisa: addForm.value.stok_sisa,
    unit: addForm.value.unit
  })
  
  if (result.success) {
    toast.value = {
      show: true,
      message: 'Inventaris berhasil ditambahkan!',
      type: 'success'
    }
    await inventoryStore.fetchInventoryItems()
  } else {
    toast.value = {
      show: true,
      message: result.error || 'Gagal menambahkan inventaris',
      type: 'error'
    }
  }
  
  loading.value = false
  showAddModal.value = false
}

async function confirmDelete() {
  loading.value = true
  
  const result = await inventoryStore.deleteInventoryItem(selectedItem.value)
  
  if (result.success) {
    toast.value = {
      show: true,
      message: 'Inventaris berhasil dihapus!',
      type: 'success'
    }
    await inventoryStore.fetchInventoryItems()
    selectedItem.value = null
  } else {
    toast.value = {
      show: true,
      message: result.error || 'Gagal menghapus inventaris',
      type: 'error'
    }
  }
  
  loading.value = false
  showDeleteConfirm.value = false
}

function convertDateToInput(dateStr) {
  // Convert DD-MM-YYYY to YYYY-MM-DD
  const parts = dateStr.split('-')
  if (parts.length === 3) {
    return `${parts[2]}-${parts[1]}-${parts[0]}`
  }
  return dateStr
}

function formatDate(dateStr) {
  // Convert YYYY-MM-DD to DD-MM-YYYY
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  return `${day}-${month}-${year}`
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
/* Page Container */
.inventory-container {
  display: flex;
  min-height: 100vh;
  background: #E8E8E8;
  font-family: 'Inter', sans-serif;
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
.inventory-header {
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
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
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
  margin-bottom: 20px;
  justify-content: flex-end;
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

.action-buttons button:active::before {
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
    padding: 8px !important;
    width: 100% !important;
    max-width: 100vw !important;
    overflow-x: hidden !important;
    box-sizing: border-box !important;
  }

  .breadcrumbs {
    display: none !important;
  }

  .inventory-header {
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
    max-width: 100% !important;
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
    padding: 12px 20px !important;
    box-sizing: border-box !important;
  }

  .search-container {
    width: 100% !important;
    max-width: 100% !important;
    margin-bottom: 16px !important;
  }

  .search-input {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    font-size: 16px !important;
    min-height: 48px !important;
    padding: 12px 16px 12px 44px !important;
  }

  .table-container {
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
  }

  .inventory-table {
    width: 100% !important;
    font-size: 12px !important;
    table-layout: fixed !important;
  }

  .inventory-table th,
  .inventory-table td {
    padding: 8px 4px !important;
    white-space: normal !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
  }

  .col-select {
    width: 50px !important;
  }

  .col-nama {
    width: 30% !important;
  }

  .col-jumlah {
    width: 20% !important;
  }

  .col-satuan {
    width: 20% !important;
  }

  .col-keterangan {
    width: 30% !important;
  }

  .modal-content {
    width: 90% !important;
    max-width: 500px !important;
    padding: 20px !important;
    box-sizing: border-box !important;
    margin: 10px !important;
    overflow-x: hidden !important;
  }

  .modal-header {
    padding: 0 0 16px 0 !important;
    margin: 0 !important;
  }

  .modal-body {
    padding: 16px 0 !important;
    margin: 0 !important;
    width: 100% !important;
    box-sizing: border-box !important;
  }

  .modal-footer {
    padding: 16px 0 0 0 !important;
    flex-direction: column !important;
    gap: 10px !important;
    margin: 0 !important;
  }

  .modal-footer button {
    width: 100% !important;
    min-height: 48px !important;
    font-size: 15px !important;
    box-sizing: border-box !important;
  }

  .form-group {
    width: 100% !important;
    margin-bottom: 12px !important;
  }

  .form-group input,
  .form-group select {
    width: 100% !important;
    box-sizing: border-box !important;
    font-size: 16px !important;
    min-height: 48px !important;
    padding: 12px 16px !important;
  }

  .submit-btn {
    width: 100% !important;
    min-height: 48px !important;
    box-sizing: border-box !important;
  }

  .pagination-container {
    flex-direction: column !important;
    gap: 12px !important;
    align-items: stretch !important;
  }

  .pagination-info {
    text-align: center !important;
    font-size: 12px !important;
  }

  .pagination-controls {
    flex-direction: column !important;
    gap: 12px !important;
    align-items: stretch !important;
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

  .page-buttons {
    display: flex !important;
    justify-content: center !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
  }

  .page-btn {
    min-width: 44px !important;
    min-height: 44px !important;
    padding: 10px !important;
    font-size: 14px !important;
  }
}

/* Search Bar */
.search-container {
  position: relative;
  margin-bottom: 20px;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
  font-size: 16px;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 45px;
  border: 2px solid #E0E0E0;
  border-radius: 12px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #1678F3;
  box-shadow: 0 0 0 3px rgba(22, 120, 243, 0.1);
}

.search-input::placeholder {
  color: #999;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #1678F3;
}

.loading-state i {
  font-size: 48px;
  margin-bottom: 16px;
}

.loading-state p {
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

/* Table Container */
.table-container {
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  border-radius: 16px;
  border: 1px solid #E0E0E0;
  background: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.table-container:hover {
  box-shadow: 0 8px 30px rgba(22, 120, 243, 0.12);
}

/* Pagination Container */
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-top: 1px solid #E0E0E0;
  background: #F9F9F9;
}

.pagination-info {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #666;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.items-per-page {
  display: flex;
  align-items: center;
  gap: 10px;
}

.items-per-page label {
  font-size: 14px;
  font-weight: 500;
  color: #555;
}

.items-per-page select {
  padding: 8px 32px 8px 12px;
  border: 2px solid #E0E0E0;
  border-radius: 8px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white url('data:image/svg+xml;utf8,<svg fill="%23555" height="20" viewBox="0 0 24 24" width="20" xmlns="http://www.w3.org/2000/svg"><path d="M7 10l5 5 5-5z"/></svg>') no-repeat;
  background-position: right 8px center;
  background-size: 16px;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
}

.items-per-page select:focus {
  outline: none;
  border-color: #1678F3;
}

.page-buttons {
  display: flex;
  gap: 8px;
}

.page-btn {
  padding: 8px 12px;
  border: 2px solid #E0E0E0;
  border-radius: 8px;
  background: white;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: #666;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-btn:hover:not(:disabled) {
  border-color: #1678F3;
  color: #1678F3;
  background: rgba(22, 120, 243, 0.05);
}

.page-btn.active {
  background: linear-gradient(135deg, #1678F3 0%, #1565C0 100%);
  color: white;
  border-color: #1678F3;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Table */
.inventory-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'Inter', sans-serif;
  table-layout: fixed;
}

.inventory-table thead {
  background: #F5F5F5;
}

.inventory-table th {
  padding: 15px 12px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: #666666;
  border-bottom: 2px solid #E0E0E0;
}

.inventory-table td {
  padding: 15px 12px;
  font-size: 13px;
  color: #333333;
  border-bottom: 1px solid #F0F0F0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.inventory-table tbody tr {
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
  animation: fadeInRow 0.5s ease-out;
}

.inventory-table tbody tr:hover {
  background: #f9f9f9;
  transform: translateX(2px);
  box-shadow: -2px 0 0 #1678F3;
  transition: all 0.2s ease;
}

.inventory-table tbody tr.selected {
  background: linear-gradient(90deg, #E3F2FD 0%, #F8FBFF 100%);
  border-left-color: #1678F3;
  box-shadow: 0 2px 12px rgba(22, 120, 243, 0.1);
}

.inventory-table tbody tr.low-stock {
  background: linear-gradient(90deg, #FFF3E0 0%, #FFFBF5 100%);
  border-left-color: #FF9800;
}

.inventory-table tbody tr.low-stock.selected {
  background: linear-gradient(90deg, #FFE0B2 0%, #FFF8E1 100%);
  border-left-color: #FF9800;
}

.stock-alert {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-left: 8px;
  padding: 2px 8px;
  background: #FF9800;
  color: white;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.stock-alert i {
  font-size: 10px;
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

.col-select {
  width: 80px;
  text-align: center;
}

/* Selection Checkbox */
.select-circle {
  width: 40px;
  height: 40px;
  border: 2px solid #E0E0E0;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.select-circle:hover {
  border-color: #1678F3;
  transform: scale(1.05);
}

.select-circle.active {
  background: #1678F3;
  border-color: #1678F3;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(22, 120, 243, 0.3);
}

.select-circle i {
  color: white;
  font-size: 18px;
  transition: transform 0.3s ease;
}

.select-circle.active i {
  transform: rotate(360deg);
}

.select-circle:not(.active) i {
  display: none;
}

.col-nama {
  width: 30%;
}

.col-jumlah {
  width: 20%;
}

.col-satuan {
  width: 20%;
}

.col-keterangan {
  width: 30%;
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
  z-index: 10000;
  backdrop-filter: blur(4px);
  padding: 20px;
  box-sizing: border-box;
  overflow-y: auto;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  animation: modalSlideIn 0.3s ease-out;
  margin: auto;
  box-sizing: border-box;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 30px;
  border-bottom: 1px solid #E0E0E0;
}

.modal-header h2 {
  font-family: 'Inter', sans-serif;
  font-size: 22px;
  font-weight: 700;
  color: #1678F3;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #F5F5F5;
  color: #333;
}

.modal-body {
  display: flex;
  gap: 30px;
  padding: 30px;
}

.modal-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.modal-right {
  flex: 0 0 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.decor-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 180px;
  height: 180px;
  background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
  border-radius: 16px;
  color: #1678F3;
}

.decor-placeholder i {
  font-size: 60px;
  margin-bottom: 12px;
}

.decor-placeholder p {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: #555;
}

.form-group input {
  padding: 12px 16px;
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
  transition: all 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #1678F3;
  box-shadow: 0 0 0 3px rgba(22, 120, 243, 0.1);
}

.submit-btn {
  background: linear-gradient(135deg, #1678F3 0%, #1565C0 100%);
  color: white;
  border: none;
  padding: 14px 24px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 10px;
  box-shadow: 0 2px 8px rgba(22, 120, 243, 0.2);
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(22, 120, 243, 0.4);
}

.submit-btn:active {
  transform: translateY(0);
}

</style>
