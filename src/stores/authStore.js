import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { supabase } from '../lib/supabase'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const role = ref(null) // 'customer', 'admin', 'owner'
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!user.value)
  const isCustomer = computed(() => role.value === 'customer')
  const isAdmin = computed(() => role.value === 'admin')
  const isOwner = computed(() => role.value === 'owner')
  const isStaff = computed(() => role.value === 'admin' || role.value === 'owner')

  // Timeout wrapper to prevent stuck loading
  function withTimeout(promise, timeoutMs = 10000) {
    return Promise.race([
      promise,
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Request timeout. Silakan coba lagi.')), timeoutMs)
      )
    ])
  }

  async function login(emailOrUsername, password) {
    loading.value = true
    error.value = null
    try {
      let userEmail = emailOrUsername
      
      // Check if input is email or username
      const isEmail = emailOrUsername.includes('@')
      
      if (!isEmail) {
        // If username, get email from database with timeout
        const result = await withTimeout(
          supabase
            .from('users')
            .select('email')
            .eq('username', emailOrUsername)
            .single()
        )
        
        if (result.error || !result.data) {
          throw new Error('Username tidak ditemukan')
        }
        
        userEmail = result.data.email
      }
      
      // Supabase authentication with email and timeout
      const authResult = await withTimeout(
        supabase.auth.signInWithPassword({
          email: userEmail,
          password
        })
      )
      
      if (authResult.error) {
        if (authResult.error.message.includes('Invalid login credentials')) {
          throw new Error('Username/Email atau password salah')
        }
        throw authResult.error
      }

      // Get user role from users table with timeout
      const userResult = await withTimeout(
        supabase
          .from('users')
          .select('*')
          .eq('id', authResult.data.user.id)
          .single()
      )
      
      if (userResult.error) throw userResult.error

      user.value = {
        id: userResult.data.id,
        email: userResult.data.email,
        username: userResult.data.username,
        name: userResult.data.name,
        phone: userResult.data.phone,
        address: userResult.data.address
      }
      role.value = userResult.data.role
      
      localStorage.setItem('user', JSON.stringify(user.value))
      localStorage.setItem('role', role.value)
      
      return { success: true, data: user.value }
    } catch (err) {
      error.value = err.message
      console.error('Login error:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  async function register(userData) {
    loading.value = true
    error.value = null
    try {
      // Check if username already exists in users table
      const { data: existingUser, error: checkError } = await supabase
        .from('users')
        .select('username, id')
        .eq('username', userData.username)
        .maybeSingle()
      
      if (existingUser) {
        throw new Error('Username sudah digunakan')
      }
      
      // Check if email already exists in auth
      const { data: authCheck } = await supabase.auth.signInWithPassword({
        email: userData.email,
        password: 'dummy-check-12345'
      })
      // If we can attempt login, email exists (even if password wrong)
      // Note: This is not perfect but helps catch some cases
      
      // Create auth user
      const { data: authData, error: signUpError } = await supabase.auth.signUp({
        email: userData.email,
        password: userData.password
      })
      
      if (signUpError) {
        // Check if error is due to email already registered
        if (signUpError.message.includes('already registered') || 
            signUpError.message.includes('already exists') ||
            signUpError.message.includes('User already registered')) {
          throw new Error('Email sudah terdaftar. Silakan gunakan email lain atau login.')
        }
        throw signUpError
      }

      // Insert user data with role into users table
      const { error: insertError } = await supabase
        .from('users')
        .insert([{
          id: authData.user.id,
          email: userData.email,
          username: userData.username,
          name: userData.name,
          phone: userData.phone,
          role: userData.role || 'customer',
          address: userData.address || null
        }])
      
      if (insertError) throw insertError

      // If role is customer, also create entry in customers table
      if (userData.role === 'customer' || !userData.role) {
        const { error: customerError } = await supabase
          .from('customers')
          .insert([{
            user_id: authData.user.id,
            nama: userData.name,
            no_hp: userData.phone || '',
            alamat: userData.address || ''
          }])
        
        if (customerError) {
          console.error('Error creating customer entry:', customerError)
          // Don't throw error here, user is already created
        }
      }

      user.value = { 
        id: authData.user.id,
        email: userData.email,
        username: userData.username,
        name: userData.name,
        phone: userData.phone,
        address: userData.address
      }
      role.value = userData.role || 'customer'
      
      localStorage.setItem('user', JSON.stringify(user.value))
      localStorage.setItem('role', role.value)
      
      return { success: true, data: user.value }
    } catch (err) {
      error.value = err.message
      console.error('Register error:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  async function updateProfile(profileData) {
    loading.value = true
    error.value = null
    try {
      if (!user.value) throw new Error('User not authenticated')
      
      // Prepare update data (address only for customer)
      const updateData = {
        name: profileData.name,
        email: profileData.email,
        phone: profileData.phone,
        updated_at: new Date().toISOString()
      }
      
      // Only include address for customer role
      if (role.value === 'customer' && profileData.address !== undefined) {
        updateData.address = profileData.address
      }
      
      // Update users table with timeout
      const updateResult = await withTimeout(
        supabase
          .from('users')
          .update(updateData)
          .eq('id', user.value.id)
          .select()
          .single()
      )
      
      if (updateResult.error) throw updateResult.error

      // Update auth email if changed
      if (profileData.email !== user.value.email) {
        const emailResult = await withTimeout(
          supabase.auth.updateUser({
            email: profileData.email
          })
        )
        if (emailResult.error) throw emailResult.error
      }

      // Update local user data
      user.value = {
        id: updateResult.data.id,
        email: updateResult.data.email,
        username: updateResult.data.username,
        name: updateResult.data.name,
        phone: updateResult.data.phone,
        address: updateResult.data.address
      }
      
      localStorage.setItem('user', JSON.stringify(user.value))
      
      return { success: true, data: user.value }
    } catch (err) {
      error.value = err.message
      console.error('Update profile error:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  async function changePassword(currentPassword, newPassword) {
    loading.value = true
    error.value = null
    try {
      if (!user.value) throw new Error('User not authenticated')
      
      // Verify current password by attempting to sign in with timeout
      const verifyResult = await withTimeout(
        supabase.auth.signInWithPassword({
          email: user.value.email,
          password: currentPassword
        })
      )
      
      if (verifyResult.error) throw new Error('Password lama tidak sesuai')
      
      // Update password with timeout
      const updateResult = await withTimeout(
        supabase.auth.updateUser({
          password: newPassword
        })
      )
      
      if (updateResult.error) throw updateResult.error
      
      return { success: true, message: 'Password berhasil diubah' }
    } catch (err) {
      error.value = err.message
      console.error('Change password error:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    try {
      // Clear local state FIRST (synchronous)
      user.value = null
      role.value = null
      localStorage.removeItem('user')
      localStorage.removeItem('role')
      
      // Then sign out from Supabase (async) with timeout
      const signOutResult = await withTimeout(
        supabase.auth.signOut(),
        5000 // 5 second timeout for logout
      )
      
      if (signOutResult.error) {
        console.error('Supabase signOut error:', signOutResult.error)
        // Don't throw - local state already cleared
      }
      
      return { success: true }
    } catch (err) {
      error.value = err.message
      console.error('Logout error:', err)
      // Even if error, local state is cleared
      return { success: true } // Return success because local logout succeeded
    } finally {
      loading.value = false
    }
  }

  let isCheckingAuth = false

  async function checkAuth() {
    // Prevent multiple simultaneous checks
    if (isCheckingAuth) return
    
    isCheckingAuth = true
    try {
      // First, try to restore from localStorage
      const storedUser = localStorage.getItem('user')
      const storedRole = localStorage.getItem('role')
      
      if (storedUser && storedRole) {
        user.value = JSON.parse(storedUser)
        role.value = storedRole
      }
      
      // Then check Supabase session
      const { data: { session }, error: sessionError } = await supabase.auth.getSession()
      
      if (sessionError) throw sessionError
      
      if (session?.user) {
        // Get user data from users table
        const { data: userData, error: userError } = await supabase
          .from('users')
          .select('*')
          .eq('id', session.user.id)
          .single()
        
        if (userError) throw userError
        
        user.value = {
          id: userData.id,
          email: userData.email,
          username: userData.username,
          name: userData.name,
          phone: userData.phone,
          address: userData.address
        }
        role.value = userData.role
        
        localStorage.setItem('user', JSON.stringify(user.value))
        localStorage.setItem('role', role.value)
      } else if (!storedUser || !storedRole) {
        // No session and no localStorage, clear everything
        user.value = null
        role.value = null
        localStorage.removeItem('user')
        localStorage.removeItem('role')
      }
    } catch (err) {
      console.error('Error checking auth:', err)
      // Don't clear if we have valid localStorage data
      if (!user.value) {
        user.value = null
        role.value = null
        localStorage.removeItem('user')
        localStorage.removeItem('role')
      }
    } finally {
      isCheckingAuth = false
    }
  }

  // Listen to auth state changes
  supabase.auth.onAuthStateChange(async (event, session) => {
    console.log('Auth state changed:', event)
    if (event === 'SIGNED_OUT') {
      user.value = null
      role.value = null
      localStorage.removeItem('user')
      localStorage.removeItem('role')
    }
    // Note: SIGNED_IN will be handled by login function directly
  })

  // Check auth on store initialization (only once)
  checkAuth()

  return {
    user,
    role,
    loading,
    error,
    isAuthenticated,
    isCustomer,
    isAdmin,
    isOwner,
    isStaff,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    checkAuth
  }
})
