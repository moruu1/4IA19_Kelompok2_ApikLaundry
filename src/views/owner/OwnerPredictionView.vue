<template>
  <div class="prediction-container">
    <!-- Sidebar -->
    <div class="sidebar">
      <!-- Grid Icon - Center -->
      <router-link to="/owner/dashboard" class="sidebar-icon menu-icon">
        <i class="fas fa-th"></i>
      </router-link>

      <router-link to="/owner/reports" class="sidebar-icon">
        <i class="fas fa-file-invoice-dollar"></i>
      </router-link>

      <router-link to="/owner/inventory" class="sidebar-icon">
        <i class="fas fa-boxes"></i>
      </router-link>

      <router-link to="/owner/prediction" class="sidebar-icon active">
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
      <div class="prediction-header">
        <h1 class="page-title">Prediksi</h1>
        
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

      <!-- Content -->
      <div class="content-wrapper">
        <!-- Left Section - Pendapatan -->
        <div class="revenue-section">
          <h2 class="section-title">Pendapatan</h2>
          
          <!-- Chart -->
          <div class="chart-container">
            <!-- Loading State -->
            <div v-if="loadingPrediction" class="chart-loading">
              <i class="fas fa-spinner fa-spin"></i>
              <p>Memuat prediksi...</p>
            </div>

            <!-- Error State -->
            <div v-else-if="predictionError" class="chart-error">
              <i class="fas fa-exclamation-circle"></i>
              <p>{{ predictionError }}</p>
              <button @click="fetchPredictions" class="retry-btn">Coba Lagi</button>
            </div>

            <!-- Chart.js Canvas -->
            <div v-else class="chart-wrapper">
              <canvas ref="revenueChart"></canvas>
            </div>
          </div>

                    <!-- Prediction Summary -->
          <div class="prediction-summary">
            <p v-if="predictionData">
              Berdasarkan analisis <strong>{{ predictionData.model_info?.trained_with_data_size || 0 }} hari</strong> data historis 
              (dari {{ getOldestDate() }}), 
              total pendapatan untuk <strong>30 hari ke depan</strong> diprediksi mencapai 
              <strong>{{ formatCurrency(predictionData.summary?.total_predicted || 0) }}</strong> 
              dengan rata-rata <strong>{{ formatCurrency(predictionData.summary?.average_daily || 0) }}/hari</strong>.
            </p>
            <p v-else>
              Memuat prediksi pendapatan...
            </p>
            
            <!-- Model Info -->
            <div v-if="predictionData?.model_info" class="model-info">
              <small>
                Akurasi Model: MAPE {{ predictionData.model_info.mape?.toFixed(2) || 0 }}% 
                | MAE ± {{ formatCurrency(predictionData.model_info.mae) }} 
                | Data Training: {{ predictionData.model_info.trained_with_data_size }} hari
              </small>
            </div>
          </div>
        </div>

        <!-- Right Section - Stok Inventaris -->
        <div class="inventory-section">
          <h2 class="section-title">Prediksi Stok Inventaris</h2>

          <!-- Loading State -->
          <div v-if="loadingInventory" class="inventory-loading">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Memuat prediksi inventaris...</p>
          </div>

          <!-- Error State -->
          <div v-else-if="inventoryError" class="inventory-error">
            <i class="fas fa-exclamation-circle"></i>
            <p>{{ inventoryError }}</p>
            <button @click="fetchInventoryPrediction" class="retry-btn">Coba Lagi</button>
          </div>

          <!-- Inventory Cards -->
          <div v-else class="inventory-cards">
            <div 
              v-for="item in inventoryPrediction" 
              :key="item.nama_barang"
              :class="['inventory-card', getStatusClass(item.status)]"
            >
              <h3 class="item-name">{{ item.nama_barang }}</h3>
              <p class="stock-info">Sisa Stok: <strong>{{ item.stok_sekarang }} {{ item.satuan }}</strong></p>
              <p class="usage-info">Pemakaian: {{ item.pemakaian_harian_rata2 }} {{ item.satuan }}/hari</p>
              <p :class="['prediction-status', getStatusClass(item.status)]">
                {{ item.estimasi_habis }} - {{ item.status }}
              </p>
              <p v-if="item.status.includes('KRITIS') || item.status.includes('Warning')" class="action-text">
                Segera lakukan pemesanan ulang.
              </p>
            </div>

            <!-- Empty State -->
            <div v-if="!inventoryPrediction || inventoryPrediction.length === 0" class="empty-state">
              <i class="fas fa-box-open"></i>
              <p>Belum ada data prediksi inventaris</p>
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
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { Chart, registerables } from 'chart.js'
import Breadcrumbs from '../../components/Breadcrumbs.vue'
import ProfileModal from '@/components/ProfileModal.vue'
import ChangePasswordModal from '@/components/ChangePasswordModal.vue'
import ToastNotification from '@/components/ToastNotification.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

// Register Chart.js components
Chart.register(...registerables)

const router = useRouter()
const authStore = useAuthStore()

const breadcrumbItems = ref([
  { label: 'Dashboard', path: '/owner/dashboard' },
  { label: 'Prediksi' }
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

// Chart.js instance
const revenueChart = ref(null)
let chartInstance = null

// ML Prediction States - Declare before any functions that use them
const loadingPrediction = ref(false)
const predictionError = ref(null)
const predictionData = ref(null)
const historicalData = ref(null)
const predictionDays = ref(30)
const ML_API_URL = import.meta.env.VITE_ML_API_URL || '/api'

// Inventory Prediction States
const loadingInventory = ref(false)
const inventoryError = ref(null)
const inventoryPrediction = ref([])

// Create or update Chart.js
function renderChart() {
  if (!historicalData.value?.data || !predictionData.value?.predictions) return
  if (!revenueChart.value) return // Wait for canvas to be mounted
  
  const historical = historicalData.value.data.slice(-30) // Last 15 days
  const predictions = predictionData.value.predictions.slice(0, 30) // Next 15 days
  
  // Month names in Indonesian
  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
  
  // Prepare labels (dates) with better format - include year when it changes
  const historicalLabels = historical.map((item, index) => {
    const date = new Date(item.date)
    const day = date.getDate()
    const month = monthNames[date.getMonth()]
    const year = date.getFullYear()
    
    // Show year on first item or when year changes
    if (index === 0 || (index > 0 && new Date(historical[index - 1].date).getFullYear() !== year)) {
      return `${day} ${month} '${year.toString().slice(-2)}`
    }
    return `${day} ${month}`
  })
  
  const predictionLabels = predictions.map((item, index) => {
    const date = new Date(item.date)
    const day = date.getDate()
    const month = monthNames[date.getMonth()]
    const year = date.getFullYear()
    
    // Show year on first prediction item or when year changes
    const lastHistoricalDate = new Date(historical[historical.length - 1].date)
    if (index === 0 && lastHistoricalDate.getFullYear() !== year) {
      return `${day} ${month} '${year.toString().slice(-2)}`
    } else if (index > 0 && new Date(predictions[index - 1].date).getFullYear() !== year) {
      return `${day} ${month} '${year.toString().slice(-2)}`
    }
    return `${day} ${month}`
  })
  
  const allLabels = [...historicalLabels, ...predictionLabels]
  
  // Prepare datasets
  const historicalRevenue = historical.map(item => item.revenue)
  const lastActualRevenue = historicalRevenue[historicalRevenue.length - 1]
  
  // Actual data - extend one more point to overlap with prediction start
  const actualData = [...historicalRevenue, lastActualRevenue, ...Array(predictions.length - 1).fill(null)]
  
  // Model Learning + Prediksi - Gunakan FITTED VALUES dari backend
  const fittedValues = predictionData.value.fitted_values || []
  
  // Get fitted revenue values matching historical dates
  let fittedRevenue = []
  if (fittedValues.length > 0) {
    // Match fitted values with historical dates - use historical as fallback per item
    fittedRevenue = historical.map((item, index) => {
      const fit = fittedValues.find(f => f.date === item.date)
      if (fit && fit.fitted_revenue) {
        return fit.fitted_revenue
      }
      // Fallback to historical value for this specific date
      return item.revenue
    })
  }
  
  // Fallback jika fitted values tidak ada
  if (fittedRevenue.length === 0) {
    fittedRevenue = historicalRevenue
  }
  
  const lastFittedRevenue = fittedRevenue[fittedRevenue.length - 1] || lastActualRevenue
  
  const predictionValues = predictions.map(item => item.predicted_revenue)
  const predictionChartData = [
    ...fittedRevenue,     // OVERLAY: Fitted values dari model
    lastFittedRevenue,    // Titik transisi
    ...predictionValues   // Prediksi masa depan
  ]
  
  // Get MAE from prediction data
  const mae = predictionData.value.model_info?.mae || 0
  
  // Upper bound - untuk SEMUA data (historis + prediksi) dengan MAE
  const fittedUpperBounds = fittedRevenue.map(val => val + mae)
  const predictionUpperBounds = predictions.map(item => item.upper_bound)
  const upperBoundData = [
    ...fittedUpperBounds,        // Upper bound untuk fitted values (historis)
    lastFittedRevenue + mae,     // Titik transisi
    ...predictionUpperBounds     // Upper bound untuk prediksi
  ]
  
  // Lower bound - untuk SEMUA data (historis + prediksi) dengan MAE
  const fittedLowerBounds = fittedRevenue.map(val => Math.max(0, val - mae))
  const predictionLowerBounds = predictions.map(item => item.lower_bound)
  const lowerBoundData = [
    ...fittedLowerBounds,                 // Lower bound untuk fitted values (historis)
    Math.max(0, lastFittedRevenue - mae), // Titik transisi
    ...predictionLowerBounds              // Lower bound untuk prediksi
  ]
  
  // Destroy existing chart
  if (chartInstance) {
    chartInstance.destroy()
  }
  
  // Create new chart
  const ctx = revenueChart.value.getContext('2d')
  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: allLabels,
      datasets: [
        // 1. Confidence Interval Upper Bound (invisible line for fill)
        {
          label: 'Upper Bound',
          data: upperBoundData,
          borderColor: 'transparent',
          backgroundColor: 'transparent',
          pointRadius: 0,
          fill: false,
          spanGaps: true,
          order: 3
        },
        // 2. Confidence Interval Lower Bound (fills between upper and lower)
        {
          label: 'Rentang Error (±MAE)',
          data: lowerBoundData,
          borderColor: 'transparent',
          backgroundColor: 'rgba(255, 152, 0, 0.15)',
          pointRadius: 0,
          fill: '-1', // Fill to previous dataset (upper bound)
          spanGaps: true,
          order: 3
        },
        // 3. Actual Revenue (Blue Solid Line)
        {
          label: 'Data Aktual (Fakta)',
          data: actualData,
          borderColor: '#1678F3',
          backgroundColor: '#1678F3',
          borderWidth: 2.5,
          pointRadius: 4,
          pointHoverRadius: 6,
          tension: 0.4,
          fill: false,
          spanGaps: false,
          order: 1
        },
        // 4. Model Learning + Prediction (Orange Line) - overlaps with actual then continues
        {
          label: 'Model Learning + Prediksi',
          data: predictionChartData,
          borderColor: '#FF9800',
          backgroundColor: '#FF9800',
          borderWidth: 2.5,
          pointRadius: 4,
          pointHoverRadius: 6,
          tension: 0.4,
          fill: false,
          spanGaps: false,
          segment: {
            borderDash: ctx => {
              // Dashed hanya untuk bagian prediksi (setelah fitted values)
              return ctx.p0DataIndex >= fittedRevenue.length ? [8, 4] : []
            }
          },
          order: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            usePointStyle: true,
            padding: 20,
            font: {
              family: 'Inter',
              size: 12
            },
            filter: (item) => {
              // Hide Upper Bound from legend
              return item.text !== 'Upper Bound'
            }
          }
        },
        tooltip: {
          enabled: true,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleFont: {
            family: 'Inter',
            size: 13
          },
          bodyFont: {
            family: 'Inter',
            size: 12
          },
          padding: 12,
          callbacks: {
            label: function(context) {
              if (context.dataset.label === 'Upper Bound') return null
              let label = context.dataset.label || ''
              if (label) {
                label += ': '
              }
              if (context.parsed.y !== null) {
                label += new Intl.NumberFormat('id-ID', {
                  style: 'currency',
                  currency: 'IDR',
                  minimumFractionDigits: 0,
                  maximumFractionDigits: 0
                }).format(context.parsed.y)
              }
              return label
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            display: true,
            color: (context) => {
              // Highlight boundary between actual and prediction
              if (context.index === historical.length) {
                return 'rgba(255, 152, 0, 0.3)'
              }
              return 'rgba(0, 0, 0, 0.05)'
            },
            lineWidth: (context) => {
              if (context.index === historical.length) {
                return 2
              }
              return 1
            }
          },
          ticks: {
            font: {
              family: 'Inter',
              size: 10
            },
            color: '#666666',
            maxRotation: 45,
            minRotation: 45
          }
        },
        y: {
          beginAtZero: true,
          grid: {
            display: true,
            color: 'rgba(0, 0, 0, 0.05)'
          },
          ticks: {
            font: {
              family: 'Inter',
              size: 11
            },
            color: '#666666',
            callback: function(value) {
              if (value >= 1000000) {
                return 'Rp ' + (value / 1000000).toFixed(1) + 'jt'
              } else if (value >= 1000) {
                return 'Rp ' + (value / 1000).toFixed(0) + 'k'
              }
              return 'Rp ' + value
            }
          }
        }
      }
    }
  })
}

// Fetch Predictions from ML API
async function fetchPredictions() {
  loadingPrediction.value = true
  predictionError.value = null
  
  try {
    // Fetch predictions
    const predictionResponse = await fetch(`${ML_API_URL}/api/predict?days=${predictionDays.value}`)
    if (!predictionResponse.ok) throw new Error('Gagal mengambil data prediksi')
    
    predictionData.value = await predictionResponse.json()
    
    // Fetch historical data
    const historicalResponse = await fetch(`${ML_API_URL}/api/historical`)
    if (!historicalResponse.ok) throw new Error('Gagal mengambil data historis')
    
    const historicalResult = await historicalResponse.json()
    
    // Extract data from response - backend returns {success: true, data: [...]}
    if (historicalResult.success && historicalResult.data) {
      historicalData.value = { data: historicalResult.data }
    } else {
      throw new Error('Data historis tidak tersedia')
    }
    
  } catch (error) {
    console.error('Error fetching predictions:', error)
    predictionError.value = error.message || `Tidak dapat terhubung ke server prediksi. Silakan coba lagi.`
  } finally {
    loadingPrediction.value = false
    
    // Render chart after loading is done and canvas is visible
    await nextTick()
    renderChart()
  }
}

function formatCurrency(value) {
  if (!value) return 'Rp 0'
  
  // Format large numbers
  if (value >= 1000000) {
    return `Rp ${(value / 1000000).toFixed(1)} jt`
  } else if (value >= 1000) {
    return `Rp ${(value / 1000).toFixed(0)}k`
  }
  
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

function getOldestDate() {
  if (!historicalData.value?.data || historicalData.value.data.length === 0) return '-'
  
  const oldestDate = new Date(historicalData.value.data[0].date)
  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
  
  return `${oldestDate.getDate()} ${monthNames[oldestDate.getMonth()]} ${oldestDate.getFullYear()}`
}

// Lifecycle
onMounted(() => {
  fetchPredictions()
  fetchInventoryPrediction()
})

// Fetch Inventory Prediction from ML API
async function fetchInventoryPrediction() {
  loadingInventory.value = true
  inventoryError.value = null
  
  try {
    const response = await fetch(`${ML_API_URL}/api/inventory-prediction`)
    if (!response.ok) throw new Error('Gagal mengambil data prediksi inventaris')
    
    const result = await response.json()
    
    if (result.success) {
      inventoryPrediction.value = result.predictions || []
    } else {
      throw new Error(result.error || 'Gagal memuat prediksi inventaris')
    }
    
  } catch (error) {
    console.error('Error fetching inventory prediction:', error)
    inventoryError.value = error.message || `Tidak dapat terhubung ke server prediksi. Silakan coba lagi.`
  } finally {
    loadingInventory.value = false
  }
}

// Get status class for styling
function getStatusClass(status) {
  if (status.includes('KRITIS')) return 'critical'
  if (status.includes('Warning')) return 'warning'
  return 'safe'
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

function handleProfileSave(profileData) {
  loading.value = true
  setTimeout(() => {
    authStore.user = { ...authStore.user, ...profileData }
    showProfileModal.value = false
    loading.value = false
    toast.value = {
      show: true,
      message: 'Profil berhasil diperbarui!',
      type: 'success'
    }
  }, 800)
}

function handlePasswordSave(passwordData) {
  loading.value = true
  setTimeout(() => {
    showPasswordModal.value = false
    loading.value = false
    toast.value = {
      show: true,
      message: 'Password berhasil diubah!',
      type: 'success'
    }
  }, 800)
}

function goToDashboard() {
  router.push('/owner/dashboard')
}
</script>

<style scoped>
.prediction-container {
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
.prediction-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
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

/* Profile Dropdown */
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

/* Content Wrapper */
.content-wrapper {
  display: flex;
  gap: 30px;
}

/* Section Title */
.section-title {
  font-family: 'Inter', sans-serif;
  font-size: 20px;
  font-weight: 600;
  color: #1678F3;
  margin-bottom: 20px;
}

/* Revenue Section */
.revenue-section {
  flex: 1;
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.chart-container {
  position: relative;
  margin-top: 20px;
}

.chart-wrapper {
  position: relative;
  height: 400px;
  padding: 20px;
}

/* Loading & Error States */
.inventory-loading,
.inventory-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.inventory-loading i {
  font-size: 32px;
  color: #1678F3;
  margin-bottom: 12px;
}

.inventory-loading p {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #666666;
}

.inventory-error i {
  font-size: 32px;
  color: #FF4444;
  margin-bottom: 12px;
}

.inventory-error p {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #666666;
  margin-bottom: 16px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: #999999;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
}

.chart-wrapper canvas {
  max-height: 100%;
}

.prediction-summary {
  background: #F5F5F5;
  padding: 20px;
  border-radius: 12px;
  margin-top: 20px;
}

.prediction-summary p {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #555555;
  line-height: 1.6;
  margin: 0;
}

.prediction-summary strong {
  color: #1678F3;
  font-weight: 600;
}

.model-info {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.model-info small {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  color: #666666;
}

/* Chart Loading & Error States */
.chart-loading,
.chart-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: 15px;
}

.chart-loading i {
  font-size: 48px;
  color: #1678F3;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.chart-loading p,
.chart-error p {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #666666;
  margin: 0;
}

.chart-error i {
  font-size: 48px;
  color: #FF4444;
}

.retry-btn {
  margin-top: 10px;
  padding: 10px 24px;
  background: #1678F3;
  color: white;
  border: none;
  border-radius: 8px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.retry-btn:hover {
  background: #0d5fc7;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(22, 120, 243, 0.3);
}

/* Inventory Section */
.inventory-section {
  width: 350px;
}

.inventory-cards {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.inventory-card {
  background: white;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  border-left: 4px solid #FF9800;
  transition: transform 0.2s, box-shadow 0.2s;
}

.inventory-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.12);
}

.inventory-card.critical {
  border-left-color: #FF4444;
  background: linear-gradient(135deg, #FFF5F5 0%, #FFFFFF 100%);
}

.inventory-card.warning {
  border-left-color: #FF9800;
  background: linear-gradient(135deg, #FFF8F0 0%, #FFFFFF 100%);
}

.inventory-card.safe {
  border-left-color: #4CAF50;
  background: linear-gradient(135deg, #F1F8F4 0%, #FFFFFF 100%);
}

.item-name {
  font-family: 'Inter', sans-serif;
  font-size: 18px;
  font-weight: 600;
  color: #333333;
  margin: 0 0 12px 0;
}

.stock-info {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #666666;
  margin: 8px 0;
}

.stock-info strong {
  color: #333333;
  font-weight: 600;
}

.usage-info {
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  color: #888888;
  margin: 6px 0;
}

.prediction-status {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  margin: 10px 0;
  font-weight: 500;
  padding: 8px 12px;
  border-radius: 8px;
  display: inline-block;
}

.prediction-status.critical {
  color: #FF4444;
  background: rgba(255, 68, 68, 0.1);
}

.prediction-status.warning {
  color: #FF9800;
  background: rgba(255, 152, 0, 0.1);
}

.prediction-status.safe {
  color: #4CAF50;
  background: rgba(76, 175, 80, 0.1);
}

.prediction-warning {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #FF4444;
  margin: 8px 0;
  font-weight: 500;
}

.prediction-warning strong {
  font-weight: 700;
}

.prediction-safe {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #4CAF50;
  margin: 8px 0;
  font-weight: 500;
}

.prediction-safe strong {
  font-weight: 700;
}

.action-text {
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  color: #666666;
  margin: 12px 0 0 0;
  line-height: 1.5;
}

/* Responsive */
@media (max-width: 1024px) {
  .content-wrapper {
    flex-direction: column;
  }

  .inventory-section {
    width: 100%;
  }

  .inventory-cards {
    flex-direction: row;
  }

  .inventory-card {
    flex: 1;
  }
}

@media (max-width: 768px) {
  .prediction-container {
    flex-direction: column !important;
    overflow-x: hidden !important;
    width: 100% !important;
    max-width: 100vw !important;
  }

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

  .prediction-header {
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

  .content-wrapper {
    flex-direction: column !important;
    gap: 16px !important;
    width: 100% !important;
    max-width: 100% !important;
    overflow-x: hidden !important;
  }

  .revenue-section,
  .chat-section {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    padding: 16px !important;
  }

  .section-title {
    font-size: 18px !important;
    margin-bottom: 12px !important;
  }

  .chart-container {
    width: 100% !important;
    max-width: 100% !important;
    overflow-x: hidden !important;
    padding: 12px !important;
    box-sizing: border-box !important;
  }

  .chart-area {
    margin-left: 0 !important;
    padding: 12px !important;
  }

  .chart-title {
    font-size: 18px !important;
  }

  .y-label {
    font-size: 11px !important;
  }

  .inventory-cards {
    flex-direction: column !important;
  }

  .inventory-card {
    padding: 18px !important;
  }

  .card-label {
    font-size: 13px !important;
  }

  .card-value {
    font-size: 20px !important;
  }
}
</style>
