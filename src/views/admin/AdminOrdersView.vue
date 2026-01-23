<template>
  <div class="orders-container">
    <!-- Sidebar -->
    <div class="sidebar">
      <!-- Menu Icons -->
      <router-link to="/admin/dashboard" class="sidebar-icon">
        <i class="fas fa-th"></i>
      </router-link>
      
      <router-link to="/admin/customers" class="sidebar-icon">
        <i class="fas fa-user"></i>
      </router-link>
      
      <router-link to="/admin/orders" class="sidebar-icon active">
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
      <div class="orders-header">
        <h1 class="page-title">Pesanan</h1>
        
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
            Edit Pesanan
          </button>
          <button class="btn-add" @click="handleAdd">
            <i class="fas fa-plus"></i>
            Tambah Pesanan
          </button>
        </div>

        <!-- Search Bar -->
        <div class="search-container">
          <i class="fas fa-search search-icon"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Cari nomor nota atau nama pelanggan..."
            class="search-input"
          />
        </div>

        <!-- Status Filter Tabs -->
        <div class="filter-tabs">
          <button 
            class="filter-tab" 
            :class="{ active: statusFilter === 'Semua' }"
            @click="setStatusFilter('Semua')"
          >
            Semua
          </button>
          <button 
            class="filter-tab" 
            :class="{ active: statusFilter === 'Diproses' }"
            @click="setStatusFilter('Diproses')"
          >
            Diproses
          </button>
          <button 
            class="filter-tab" 
            :class="{ active: statusFilter === 'Selesai' }"
            @click="setStatusFilter('Selesai')"
          >
            Selesai
          </button>
          <button 
            class="filter-tab" 
            :class="{ active: statusFilter === 'Diambil' }"
            @click="setStatusFilter('Diambil')"
          >
            Diambil
          </button>
        </div>

        <!-- Table -->
        <div class="table-container">
          <!-- Loading State -->
          <div v-if="transactionStore.loading" class="loading-state">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Memuat data...</p>
          </div>

          <!-- Empty State -->
          <EmptyState 
            v-else-if="transactionStore.transactions.length === 0"
            icon="fas fa-shopping-cart"
            title="Belum Ada Pesanan"
            message="Pesanan akan muncul di sini setelah ditambahkan"
            actionText="Tambah Pesanan"
            actionIcon="fas fa-plus"
            @action="handleAdd"
          />

          <table v-else class="orders-table">
            <thead>
              <tr>
                <th class="col-select"></th>
                <th class="col-nota">No Nota</th>
                <th class="col-nama">Nama</th>
                <th class="col-layanan">Layanan</th>
                <th class="col-unit">Jumlah Unit</th>
                <th class="col-total">Total Harga</th>
                <th class="col-status-pesanan">Status Pesanan</th>
                <th class="col-status-bayar">Status Pembayaran</th>
                <th class="col-tanggal-masuk">Tanggal Masuk</th>
                <th class="col-tanggal-selesai">Tanggal Selesai</th>
                <th class="col-metode">Metode Pembayaran</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="transaction in paginatedTransactions" 
                :key="transaction.id_transaction"
                :class="{ 'selected': selectedOrder === transaction.id_transaction }"
                @click="selectOrder(transaction.id_transaction)"
              >
                <td class="col-select">
                  <div class="select-circle" :class="{ 'active': selectedOrder === transaction.id_transaction }">
                    <i v-if="selectedOrder === transaction.id_transaction" class="fas fa-check"></i>
                  </div>
                </td>
                <td class="col-nota">{{ transaction.nomor_nota }}</td>
                <td class="col-nama">{{ transaction.customers?.nama || '-' }}</td>
                <td class="col-layanan">{{ transaction.services?.nama_layanan || '-' }}</td>
                <td class="col-unit">{{ transaction.jumlah_unit }}</td>
                <td class="col-total">{{ formatCurrency(transaction.total_harga) }}</td>
                <td class="col-status-pesanan">
                  <span class="status-badge" :class="getStatusClass(transaction.status_pesanan)">
                    {{ transaction.status_pesanan }}
                  </span>
                </td>
                <td class="col-status-bayar">
                  <span class="status-badge" :class="getPaymentStatusClass(transaction.status_pembayaran)">
                    {{ transaction.status_pembayaran }}
                  </span>
                </td>
                <td class="col-tanggal-masuk">{{ formatDate(transaction.tanggal_masuk) }}</td>
                <td class="col-tanggal-selesai">{{ formatDate(transaction.tanggal_selesai) }}</td>
                <td class="col-metode">{{ transaction.metode_pembayaran }}</td>
              </tr>
            </tbody>
          </table>

          <!-- Pagination Controls -->
          <div v-if="transactionStore.transactions.length > 0" class="pagination-container">
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
              <select v-model.number="itemsPerPage" @change="currentPage = 1">
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
      <div class="modal-content edit-modal" @click.stop>
        <h2 class="edit-modal-title">Edit Pesanan</h2>
        
        <div class="edit-modal-layout">
          <!-- Left Side - Form -->
          <div class="edit-form-section">
            
            <form @submit.prevent="saveEdit">
              <div class="edit-form-group">
                <label>Pelanggan</label>
                <select v-model="editForm.customer_id" required>
                  <option :value="null">Pilih Pelanggan</option>
                  <option 
                    v-for="customer in customerStore.customers" 
                    :key="customer.id_customer"
                    :value="customer.id_customer"
                  >
                    {{ customer.nama }}
                  </option>
                </select>
              </div>
              
              <div class="edit-form-group">
                <label>Layanan</label>
                <select v-model="editForm.service_id" required>
                  <option :value="null">Pilih Layanan</option>
                  <option 
                    v-for="service in serviceStore.services" 
                    :key="service.id_service"
                    :value="service.id_service"
                  >
                    {{ service.nama_layanan }} - {{ formatCurrency(service.harga_per_unit) }}/unit
                  </option>
                </select>
              </div>
              
              <div class="edit-form-group">
                <label>Jumlah Unit</label>
                <input v-model.number="editForm.jumlah_unit" type="number" min="0" step="0.01" placeholder="Jumlah Unit" required />
              </div>
              
              <div class="edit-form-group">
                <label>Status Pembayaran</label>
                <select v-model="editForm.status_pembayaran" required>
                  <option value="">Pilih Status</option>
                  <option value="Lunas">Lunas</option>
                  <option value="Belum Lunas">Belum Lunas</option>
                </select>
              </div>
              
              <div class="edit-form-group">
                <label>Status Pesanan</label>
                <select v-model="editForm.status_pesanan" required>
                  <option value="">Pilih Status</option>
                  <option value="Diproses">Diproses</option>
                  <option value="Selesai">Selesai</option>
                  <option value="Diambil">Diambil</option>
                </select>
              </div>
            </form>
          </div>
          
          <!-- Right Side - Form -->
          <div class="edit-form-section-right">
            <div class="edit-form-group">
              <label>Tanggal Masuk</label>
              <input v-model="editForm.tanggal_masuk" type="date" required />
            </div>
            
            <div class="edit-form-group">
              <label>Tanggal Selesai</label>
              <input v-model="editForm.tanggal_selesai" type="date" />
            </div>
            
            <div class="edit-form-group">
              <label>Metode Pembayaran</label>
              <select v-model="editForm.metode_pembayaran" required>
                <option value="">Pilih Metode</option>
                <option value="Tunai">Tunai</option>
                <option value="Transfer">Transfer</option>
              </select>
            </div>
            
            <button type="button" @click="saveEdit" class="edit-submit-btn">Simpan</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click="closeAddModal">
      <div class="modal-content add-modal" @click.stop>
        <h2 class="add-modal-title">Tambah Pesanan</h2>
        
        <div class="add-modal-layout">
          <!-- Left Side - Form -->
          <div class="add-form-section">
            
            <form @submit.prevent="saveAdd">
              <div class="add-form-group">
                <label>Pelanggan</label>
                <select v-model="addForm.customer_id" required>
                  <option :value="null">Pilih Pelanggan</option>
                  <option 
                    v-for="customer in customerStore.customers" 
                    :key="customer.id_customer"
                    :value="customer.id_customer"
                  >
                    {{ customer.nama }}
                  </option>
                </select>
              </div>
              
              <div class="add-form-group">
                <label>Layanan</label>
                <select v-model="addForm.service_id" required>
                  <option :value="null">Pilih Layanan</option>
                  <option 
                    v-for="service in serviceStore.services" 
                    :key="service.id_service"
                    :value="service.id_service"
                  >
                    {{ service.nama_layanan }} - {{ formatCurrency(service.harga_per_unit) }}/unit
                  </option>
                </select>
              </div>
              
              <div class="add-form-group">
                <label>Jumlah Unit</label>
                <input v-model.number="addForm.jumlah_unit" type="number" min="0" step="0.01" placeholder="Jumlah Unit" required />
              </div>
              
              <div class="add-form-group">
                <label>Status Pembayaran</label>
                <select v-model="addForm.status_pembayaran" required>
                  <option value="">Pilih Status</option>
                  <option value="Lunas">Lunas</option>
                  <option value="Belum Lunas">Belum Lunas</option>
                </select>
              </div>
              
              <div class="add-form-group">
                <label>Status Pesanan</label>
                <select v-model="addForm.status_pesanan" required>
                  <option value="">Pilih Status</option>
                  <option value="Diproses">Diproses</option>
                  <option value="Selesai">Selesai</option>
                  <option value="Diambil">Diambil</option>
                </select>
              </div>
            </form>
          </div>
          
          <!-- Right Side - Form -->
          <div class="add-form-section-right">
            <div class="add-form-group">
              <label>Tanggal Masuk</label>
              <input v-model="addForm.tanggal_masuk" type="date" required />
            </div>
            
            <div class="add-form-group">
              <label>Tanggal Selesai</label>
              <input v-model="addForm.tanggal_selesai" type="date" />
            </div>
            
            <div class="add-form-group">
              <label>Metode Pembayaran</label>
              <select v-model="addForm.metode_pembayaran" required>
                <option value="">Pilih Metode</option>
                <option value="Tunai">Tunai</option>
                <option value="Transfer">Transfer</option>
              </select>
            </div>
            
            <button type="button" @click="saveAdd" class="add-submit-btn">Masukkan keranjang</button>
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
      title="Hapus Pesanan"
      message="Apakah Anda yakin ingin menghapus pesanan ini?"
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
import { useTransactionStore } from '@/stores/transactionStore'
import { useCustomerStore } from '@/stores/customerStore'
import { useServiceStore } from '@/stores/serviceStore'
import Breadcrumbs from '../../components/Breadcrumbs.vue'
import ToastNotification from '@/components/ToastNotification.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import EmptyState from '@/components/EmptyState.vue'
import ProfileModal from '@/components/ProfileModal.vue'
import ChangePasswordModal from '@/components/ChangePasswordModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const transactionStore = useTransactionStore()
const customerStore = useCustomerStore()
const serviceStore = useServiceStore()

const breadcrumbItems = ref([
  { label: 'Dashboard', path: '/admin/dashboard' },
  { label: 'Pesanan' }
])

const showProfileMenu = ref(false)
const selectedOrder = ref(null)
const showEditModal = ref(false)
const showAddModal = ref(false)
const loading = ref(false)
const showDeleteConfirm = ref(false)
const showProfileModal = ref(false)
const showPasswordModal = ref(false)
const searchQuery = ref('')
const statusFilter = ref('Semua')
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
  await Promise.all([
    transactionStore.fetchTransactions(),
    customerStore.fetchCustomers(),
    serviceStore.fetchServices()
  ])
})

// Watch search and reset page
watch([searchQuery, statusFilter], () => {
  currentPage.value = 1
})

const editForm = ref({
  id_transaction: null,
  customer_id: null,
  service_id: null,
  jumlah_unit: 0,
  status_pesanan: '',
  status_pembayaran: '',
  tanggal_masuk: '',
  tanggal_selesai: '',
  metode_pembayaran: ''
})

const addForm = ref({
  customer_id: null,
  service_id: null,
  jumlah_unit: 0,
  status_pesanan: 'Diproses',
  status_pembayaran: 'Belum Lunas',
  tanggal_masuk: '',
  tanggal_selesai: '',
  metode_pembayaran: 'Tunai'
})

const filteredTransactions = computed(() => {
  let filtered = transactionStore.transactions
  
  // Filter by status
  if (statusFilter.value !== 'Semua') {
    filtered = filtered.filter(t => t.status_pesanan === statusFilter.value)
  }
  
  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(t => 
      t.nomor_nota.toLowerCase().includes(query) ||
      t.customers?.nama.toLowerCase().includes(query)
    )
  }
  
  return filtered
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

function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('id-ID', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(amount)
}

function toggleProfileMenu() {
  showProfileMenu.value = !showProfileMenu.value
}

function selectOrder(id) {
  selectedOrder.value = selectedOrder.value === id ? null : id
}

function getStatusClass(status) {
  if (status === 'Selesai') return 'status-selesai'
  if (status === 'Diproses') return 'status-proses'
  if (status === 'Diambil') return 'status-diambil'
  return 'status-pending'
}

function getPaymentStatusClass(status) {
  if (status === 'Lunas') return 'status-lunas'
  return 'status-belum'
}

function setStatusFilter(status) {
  statusFilter.value = status
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

function handleEdit() {
  if (!selectedOrder.value) {
    toast.value = {
      show: true,
      message: 'Pilih pesanan terlebih dahulu!',
      type: 'warning'
    }
    return
  }
  
  const transaction = transactionStore.transactions.find(t => t.id_transaction === selectedOrder.value)
  if (!transaction) return
  
  // Convert date format to YYYY-MM-DD for input[type="date"]
  const convertDate = (dateStr) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  
  editForm.value = {
    id_transaction: transaction.id_transaction,
    customer_id: transaction.customer_id,
    service_id: transaction.service_id,
    jumlah_unit: transaction.jumlah_unit,
    status_pesanan: transaction.status_pesanan,
    status_pembayaran: transaction.status_pembayaran,
    tanggal_masuk: convertDate(transaction.tanggal_masuk),
    tanggal_selesai: convertDate(transaction.tanggal_selesai),
    metode_pembayaran: transaction.metode_pembayaran
  }
  showEditModal.value = true
}

function handleAdd() {
  // Get today's date
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  const todayFormatted = `${year}-${month}-${day}`
  
  addForm.value = {
    customer_id: null,
    service_id: null,
    jumlah_unit: 0,
    status_pesanan: 'Diproses',
    status_pembayaran: 'Belum Lunas',
    tanggal_masuk: todayFormatted,
    tanggal_selesai: '',
    metode_pembayaran: 'Tunai'
  }
  showAddModal.value = true
}

function closeEditModal() {
  showEditModal.value = false
}

function closeAddModal() {
  showAddModal.value = false
}

async function saveEdit() {
  // Validate
  if (!editForm.value.customer_id || !editForm.value.service_id || !editForm.value.jumlah_unit) {
    toast.value = {
      show: true,
      message: 'Harap lengkapi semua field!',
      type: 'warning'
    }
    return
  }
  
  loading.value = true
  
  // Get service price and calculate total
  const service = serviceStore.services.find(s => s.id_service === editForm.value.service_id)
  const hargaPerUnit = service?.harga_per_unit || 0
  const totalHarga = hargaPerUnit * editForm.value.jumlah_unit
  
  // Auto set tanggal_selesai if status is Selesai and date is empty
  if (editForm.value.status_pesanan === 'Selesai' && !editForm.value.tanggal_selesai) {
    const today = new Date()
    const year = today.getFullYear()
    const month = String(today.getMonth() + 1).padStart(2, '0')
    const day = String(today.getDate()).padStart(2, '0')
    editForm.value.tanggal_selesai = `${year}-${month}-${day}`
  }
  
  const result = await transactionStore.updateTransaction(
    editForm.value.id_transaction,
    {
      customer_id: editForm.value.customer_id,
      service_id: editForm.value.service_id,
      jumlah_unit: editForm.value.jumlah_unit,
      total_harga: totalHarga,
      status_pesanan: editForm.value.status_pesanan,
      status_pembayaran: editForm.value.status_pembayaran,
      tanggal_masuk: editForm.value.tanggal_masuk,
      tanggal_selesai: editForm.value.tanggal_selesai || null,
      metode_pembayaran: editForm.value.metode_pembayaran,
      sumber_pesanan: 'Offline'
    }
  )
  
  if (result.success) {
    toast.value = {
      show: true,
      message: 'Pesanan berhasil diperbarui!',
      type: 'success'
    }
    await transactionStore.fetchTransactions()
    selectedOrder.value = null
  } else {
    toast.value = {
      show: true,
      message: result.error || 'Gagal memperbarui pesanan',
      type: 'error'
    }
  }
  
  loading.value = false
  closeEditModal()
}

async function saveAdd() {
  // Validate
  if (!addForm.value.customer_id || !addForm.value.service_id || !addForm.value.jumlah_unit) {
    toast.value = {
      show: true,
      message: 'Harap lengkapi semua field!',
      type: 'warning'
    }
    return
  }
  
  loading.value = true
  
  // Get service price
  const service = serviceStore.services.find(s => s.id_service === addForm.value.service_id)
  const hargaPerUnit = service?.harga_per_unit || 0
  const totalHarga = hargaPerUnit * addForm.value.jumlah_unit
  
  // Generate nomor nota (format: TRX-YYYYMMDD-XXXX)
  const today = new Date()
  const dateStr = today.getFullYear().toString() + 
                  (today.getMonth() + 1).toString().padStart(2, '0') + 
                  today.getDate().toString().padStart(2, '0')
  const randomNum = Math.floor(1000 + Math.random() * 9000)
  const nomorNota = `TRX-${dateStr}-${randomNum}`
  
  const result = await transactionStore.createTransaction({
    nomor_nota: nomorNota,
    customer_id: addForm.value.customer_id,
    service_id: addForm.value.service_id,
    jumlah_unit: addForm.value.jumlah_unit,
    total_harga: totalHarga,
    status_pesanan: addForm.value.status_pesanan,
    status_pembayaran: addForm.value.status_pembayaran,
    tanggal_masuk: addForm.value.tanggal_masuk,
    tanggal_selesai: addForm.value.tanggal_selesai || null,
    metode_pembayaran: addForm.value.metode_pembayaran,
    sumber_pesanan: 'Offline'
  })
  
  if (result.success) {
    toast.value = {
      show: true,
      message: 'Pesanan baru berhasil ditambahkan!',
      type: 'success'
    }
    await transactionStore.fetchTransactions()
  } else {
    toast.value = {
      show: true,
      message: result.error || 'Gagal menambahkan pesanan',
      type: 'error'
    }
  }
  
  loading.value = false
  closeAddModal()
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
.orders-container {
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
.orders-header {
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

/* Filter Tabs */
.filter-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  border-bottom: 2px solid #E0E0E0;
  padding-bottom: 2px;
}

.filter-tab {
  padding: 10px 20px;
  background: none;
  border: none;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: #666;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
}

.filter-tab:hover {
  color: #1678F3;
}

.filter-tab.active {
  color: #1678F3;
  border-bottom-color: #1678F3;
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
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23666' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
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

/* Table */
.orders-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'Inter', sans-serif;
}

.orders-table thead {
  background: #F5F5F5;
}

.orders-table th {
  padding: 15px 8px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: #666666;
  border-bottom: 2px solid #E0E0E0;
  white-space: normal;
  line-height: 1.3;
}

.orders-table td {
  padding: 12px 8px;
  font-size: 12px;
  color: #333333;
  border-bottom: 1px solid #F0F0F0;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}

.orders-table tbody tr {
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
  animation: fadeInRow 0.5s ease-out;
}

.orders-table tbody tr:hover {
  background: #f9f9f9;
  transform: translateX(2px);
  box-shadow: -2px 0 0 #1678F3;
  transition: all 0.2s ease;
}

.orders-table tbody tr.selected {
  background: linear-gradient(90deg, #E3F2FD 0%, #F8FBFF 100%);
  border-left-color: #1678F3;
  box-shadow: 0 2px 12px rgba(22, 120, 243, 0.1);
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
  width: 60px;
  text-align: center;
}

.col-nota {
  width: 10%;
  font-weight: 600;
  color: #1678F3;
  white-space: nowrap;
}

.col-nama {
  width: 10%;
  white-space: nowrap;
}

.col-layanan {
  width: 12%;
}

.col-unit {
  width: 7%;
  text-align: center;
  white-space: nowrap;
}

.col-total {
  width: 10%;
  text-align: right;
  font-weight: 600;
  color: #2E7D32;
  white-space: nowrap;
}

.col-status-pesanan {
  width: 10%;
  text-align: center;
}

.col-status-bayar {
  width: 10%;
  text-align: center;
}

.col-tanggal-masuk {
  width: 9%;
  text-align: center;
  font-size: 11px;
  white-space: nowrap;
}

.col-tanggal-selesai {
  width: 9%;
  text-align: center;
  font-size: 11px;
  white-space: nowrap;
}

.col-metode {
  width: 10%;
  text-align: center;
  white-space: nowrap;
}

/* Selection Checkbox */
.select-circle {
  width: 32px;
  height: 32px;
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

/* Status Badges */
.status-badge {
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 11px;
  font-weight: 600;
  text-align: center;
  display: inline-block;
  white-space: nowrap;
}

.status-diproses {
  background: #FFF3E0;
  color: #F57C00;
}

.status-selesai {
  background: #E8F5E9;
  color: #388E3C;
}

.status-diambil {
  background: #E3F2FD;
  color: #1976D2;
}

.status-pending {
  background: #FFF9C4;
  color: #F9A825;
}

.status-lunas {
  background: #E8F5E9;
  color: #388E3C;
}

.status-belum {
  background: #FFEBEE;
  color: #D32F2F;
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
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 30px;
  width: 90%;
  max-width: 800px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  animation: modalSlideIn 0.3s ease-out;
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

/* Edit Modal */
.edit-modal-title,
.add-modal-title {
  font-family: 'Inter', sans-serif;
  font-size: 24px;
  font-weight: 700;
  color: #1678F3;
  margin: 0 0 25px 0;
  text-align: center;
}

.edit-modal-layout,
.add-modal-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.section-label {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 15px 0;
}

.edit-form-section,
.edit-form-section-right,
.add-form-section,
.add-form-section-right {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.edit-form-group,
.add-form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.edit-form-group label,
.add-form-group label {
  font-size: 14px;
  font-weight: 600;
  color: #555;
}

.edit-form-group input,
.edit-form-group select,
.add-form-group input,
.add-form-group select {
  padding: 12px 16px;
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
  transition: all 0.3s ease;
  background: white;
}

.edit-form-group input:focus,
.edit-form-group select:focus,
.add-form-group input:focus,
.add-form-group select:focus {
  outline: none;
  border-color: #1678F3;
  box-shadow: 0 0 0 3px rgba(22, 120, 243, 0.1);
}

.edit-form-group input:disabled,
.add-form-group input:disabled {
  background: #F5F5F5;
  cursor: not-allowed;
}

.edit-submit-btn,
.add-submit-btn {
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

.edit-submit-btn:hover,
.add-submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(22, 120, 243, 0.4);
}

.edit-submit-btn:active,
.add-submit-btn:active {
  transform: translateY(0);
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

  .orders-header {
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

  .table-container {
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    margin: 0 -14px !important;
    padding: 0 14px !important;
  }

  .orders-table {
    font-size: 13px !important;
    min-width: 1000px !important;
  }

  .orders-table th,
  .orders-table td {
    padding: 10px 8px !important;
  }

  .edit-modal-layout,
  .add-modal-layout {
    grid-template-columns: 1fr !important;
  }

  .modal-content {
    width: 95% !important;
    padding: 20px !important;
  }

  .modal-footer button {
    min-height: 44px !important;
    font-size: 15px !important;
  }
}
</style>
