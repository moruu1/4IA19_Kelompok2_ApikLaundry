import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Public Routes
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },

    // Customer Routes
    {
      path: '/customer/home',
      name: 'customer-home',
      component: () => import('../views/customer/CustomerHomeView.vue'),
      meta: { requiresAuth: true, role: 'customer' }
    },
    {
      path: '/customer/orders',
      name: 'customer-orders',
      component: () => import('../views/customer/CustomerOrdersView.vue'),
      meta: { requiresAuth: true, role: 'customer' }
    },
    {
      path: '/customer/services',
      name: 'customer-services',
      component: () => import('../views/customer/CustomerServicesView.vue'),
      meta: { requiresAuth: true, role: 'customer' }
    },
    {
      path: '/customer/track',
      name: 'customer-track',
      component: () => import('../views/customer/CustomerTrackView.vue'),
      meta: { requiresAuth: true, role: 'customer' }
    },
    {
      path: '/customer/history',
      name: 'customer-history',
      component: () => import('../views/customer/CustomerOrdersView.vue'),
      meta: { requiresAuth: true, role: 'customer' }
    },
    {
      path: '/customer/profile',
      name: 'customer-profile',
      component: () => import('../views/customer/CustomerProfileView.vue'),
      meta: { requiresAuth: true, role: 'customer' }
    },
    {
      path: '/customer/change-password',
      name: 'customer-change-password',
      component: () => import('../views/customer/ChangePasswordView.vue'),
      meta: { requiresAuth: true, role: 'customer' }
    },

    // Admin Routes
    {
      path: '/admin/dashboard',
      name: 'admin-dashboard',
      component: () => import('../views/admin/AdminHomeView.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/orders',
      name: 'admin-orders',
      component: () => import('../views/admin/AdminOrdersView.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/customers',
      name: 'admin-customers',
      component: () => import('../views/admin/AdminCustomersView.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/profile',
      name: 'admin-profile',
      component: () => import('../views/admin/AdminProfileView.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/change-password',
      name: 'admin-change-password',
      component: () => import('../views/admin/AdminChangePasswordView.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/financial-report',
      name: 'admin-financial-report',
      component: () => import('../views/admin/AdminFinancialReportView.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/inventory',
      name: 'admin-inventory',
      component: () => import('../views/admin/AdminInventoryView.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/services',
      name: 'admin-services',
      component: () => import('../views/admin/AdminServicesView.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },

    // Owner Routes
    {
      path: '/owner/dashboard',
      name: 'owner-dashboard',
      component: () => import('../views/owner/OwnerDashboardView.vue'),
      meta: { requiresAuth: true, role: 'owner' }
    },
    {
      path: '/owner/profile',
      name: 'owner-profile',
      component: () => import('../views/owner/OwnerProfileView.vue'),
      meta: { requiresAuth: true, role: 'owner' }
    },
    {
      path: '/owner/change-password',
      name: 'owner-change-password',
      component: () => import('../views/owner/OwnerChangePasswordView.vue'),
      meta: { requiresAuth: true, role: 'owner' }
    },
    {
      path: '/owner/analytics',
      name: 'owner-analytics',
      component: () => import('../views/owner/OwnerReportsView.vue'),
      meta: { requiresAuth: true, role: 'owner' }
    },
    {
      path: '/owner/reports',
      name: 'owner-reports',
      component: () => import('../views/owner/OwnerReportsView.vue'),
      meta: { requiresAuth: true, role: 'owner' }
    },
    {
      path: '/owner/finance',
      name: 'owner-finance',
      component: () => import('../views/owner/OwnerReportsView.vue'),
      meta: { requiresAuth: true, role: 'owner' }
    },
    {
      path: '/owner/inventory',
      name: 'owner-inventory',
      component: () => import('../views/owner/OwnerInventoryView.vue'),
      meta: { requiresAuth: true, role: 'owner' }
    },
    {
      path: '/owner/prediction',
      name: 'owner-prediction',
      component: () => import('../views/owner/OwnerPredictionView.vue'),
      meta: { requiresAuth: true, role: 'owner' }
    },
    {
      path: '/owner/staff',
      name: 'owner-staff',
      redirect: '/owner/dashboard',
      meta: { requiresAuth: true, role: 'owner' }
    },
    {
      path: '/owner/settings',
      name: 'owner-settings',
      redirect: '/owner/dashboard',
      meta: { requiresAuth: true, role: 'owner' }
    },

    // Legacy Routes (redirect to new structure)
    {
      path: '/dashboard',
      redirect: to => {
        const authStore = useAuthStore()
        if (authStore.isCustomer) return '/customer/orders'
        if (authStore.isAdmin) return '/admin/dashboard'
        if (authStore.isOwner) return '/owner/dashboard'
        return '/login'
      }
    },
    {
      path: '/orders',
      name: 'orders',
      redirect: '/customer/orders'
    },
    {
      path: '/orders/:id',
      name: 'order-detail',
      redirect: to => `/customer/orders/${to.params.id}`
    },
    {
      path: '/customers',
      name: 'customers',
      redirect: '/admin/customers'
    },
    {
      path: '/services',
      name: 'services',
      redirect: '/customer/services'
    },
    {
      path: '/reports',
      name: 'reports',
      redirect: '/owner/reports'
    }
  ]
})

// Navigation Guard
router.beforeEach(async (to, from, next) => {
  // Lazy load authStore to avoid initialization issues
  const { useAuthStore } = await import('../stores/authStore.js')
  const authStore = useAuthStore()
  
  console.log('Navigation guard - To:', to.path, 'Authenticated:', authStore.isAuthenticated, 'Role:', authStore.role)
  
  // If going to login/register and already authenticated, redirect to dashboard
  if ((to.path === '/login' || to.path === '/register') && authStore.isAuthenticated) {
    console.log('Already authenticated, redirecting to dashboard')
    if (authStore.isCustomer) {
      next('/customer/home')
    } else if (authStore.isAdmin) {
      next('/admin/dashboard')
    } else if (authStore.isOwner) {
      next('/owner/dashboard')
    } else {
      next()
    }
    return
  }
  
  // Allow access to public routes
  if (!to.meta.requiresAuth) {
    next()
    return
  }
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    console.log('Not authenticated, redirecting to login')
    // Clear any stale data
    authStore.user = null
    authStore.role = null
    localStorage.removeItem('user')
    localStorage.removeItem('role')
    
    next('/login')
    return
  }
  
  // Check role-based access
  if (to.meta.role && authStore.role !== to.meta.role) {
    console.log('Wrong role, redirecting. Required:', to.meta.role, 'Current:', authStore.role)
    // Redirect to appropriate dashboard
    if (authStore.isCustomer) {
      next('/customer/orders')
    } else if (authStore.isAdmin) {
      next('/admin/dashboard')
    } else if (authStore.isOwner) {
      next('/owner/dashboard')
    } else {
      next('/login')
    }
    return
  }
  
  next()
})

export default router
