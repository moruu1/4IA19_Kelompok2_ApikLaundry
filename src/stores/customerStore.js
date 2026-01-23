import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '@/lib/supabase'

export const useCustomerStore = defineStore('customers', () => {
  const customers = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchCustomers() {
    loading.value = true
    error.value = null
    try {
      const { data, error: fetchError } = await supabase
        .from('customers')
        .select('*')
        .order('id_customer', { ascending: false })

      if (fetchError) throw fetchError
      
      customers.value = data || []
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error fetching customers:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  async function getCustomerById(id) {
    loading.value = true
    error.value = null
    try {
      const { data, error: fetchError } = await supabase
        .from('customers')
        .select('*')
        .eq('id_customer', id)
        .single()

      if (fetchError) throw fetchError
      
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error fetching customer:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  async function createCustomer(customerData) {
    loading.value = true
    error.value = null
    try {
      console.log('Creating customer with data:', { ...customerData, password: '***' })
      
      // 1. Create auth user first
      const { data: authData, error: authError } = await supabase.auth.signUp({
        email: customerData.email,
        password: customerData.password,
        options: {
          data: {
            name: customerData.nama,
            role: 'customer'
          },
          emailRedirectTo: undefined // Disable email confirmation for admin-created accounts
        }
      })

      if (authError) {
        console.error('Auth signup error:', authError)
        
        // Provide more specific error messages
        let errorMessage = authError.message
        if (authError.message.includes('already registered') || authError.message.includes('already exists')) {
          errorMessage = 'Email sudah terdaftar. Gunakan email lain.'
        } else if (authError.message.includes('invalid')) {
          errorMessage = 'Format email tidak valid. Gunakan email yang berbeda.'
        }
        
        throw new Error(errorMessage)
      }
      
      if (!authData.user) {
        throw new Error('Failed to create user account')
      }

      console.log('Auth user created:', authData.user.id)

      // Generate username from email (part before @)
      const emailPart = customerData.email.split('@')[0]
      const generatedUsername = emailPart.toLowerCase().replace(/[^a-z0-9]/g, '') || 'customer'
      
      console.log('Email part:', emailPart, 'Generated base username:', generatedUsername)
      
      // Check if username exists, add number if needed
      let username = generatedUsername
      let counter = 1
      let usernameExists = true
      
      while (usernameExists) {
        const { data: existingUser } = await supabase
          .from('users')
          .select('username')
          .eq('username', username)
          .maybeSingle()
        
        console.log('Checking username:', username, 'Exists:', !!existingUser)
        
        if (!existingUser) {
          usernameExists = false
        } else {
          username = `${generatedUsername}${counter}`
          counter++
        }
      }
      
      console.log('Final username to insert:', username)
      
      if (!username) {
        throw new Error('Failed to generate username')
      }

      // 2. Insert into users table
      const userInsertData = {
        id: authData.user.id,
        email: customerData.email,
        username: username,
        name: customerData.nama,
        role: 'customer',
        phone: customerData.no_hp,
        address: customerData.alamat
      }
      
      console.log('Inserting user data:', { ...userInsertData, id: '***' })
      
      const { error: userInsertError } = await supabase
        .from('users')
        .insert([userInsertData])

      if (userInsertError) {
        console.error('Users table insert error:', userInsertError)
        // Cleanup: Delete auth user if users table insert fails
        try {
          await supabase.auth.admin.deleteUser(authData.user.id)
        } catch (cleanupError) {
          console.error('Failed to cleanup auth user:', cleanupError)
        }
        throw userInsertError
      }

      console.log('User record created in users table')

      // 3. Create customer record with user_id (NO email/password here)
      const customerRecord = {
        user_id: authData.user.id,
        nama: customerData.nama,
        no_hp: customerData.no_hp,
        alamat: customerData.alamat
      }
      
      console.log('Inserting customer record:', customerRecord)
      
      const { data, error: insertError } = await supabase
        .from('customers')
        .insert([customerRecord])
        .select(`
          id_customer,
          user_id,
          nama,
          no_hp,
          alamat
        `)
        .single()

      if (insertError) {
        console.error('Customers table insert error:', insertError)
        // Cleanup: Delete users table and auth user if customers table insert fails
        try {
          await supabase.from('users').delete().eq('id', authData.user.id)
          await supabase.auth.admin.deleteUser(authData.user.id)
        } catch (cleanupError) {
          console.error('Failed to cleanup user and auth:', cleanupError)
        }
        throw insertError
      }

      console.log('Customer record created:', data)
      
      // Fetch the complete customer data with email from users table
      const { data: completeData, error: fetchError } = await supabase
        .from('customers')
        .select(`
          id_customer,
          user_id,
          nama,
          no_hp,
          alamat,
          users:user_id (
            email
          )
        `)
        .eq('id_customer', data.id_customer)
        .single()
      
      if (fetchError) {
        console.error('Error fetching complete customer data:', fetchError)
        // Still add basic data even if fetch fails
        customers.value.unshift(data)
        return { success: true, data }
      }
      
      // Transform and add to store
      const transformedData = {
        ...completeData,
        email: completeData.users?.email || ''
      }
      
      customers.value.unshift(transformedData)
      return { success: true, data: transformedData }
    } catch (err) {
      error.value = err.message
      console.error('Error creating customer:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  async function updateCustomer(id, customerData) {
    loading.value = true
    error.value = null
    try {
      const { data, error: updateError } = await supabase
        .from('customers')
        .update(customerData)
        .eq('id_customer', id)
        .select()
        .single()

      if (updateError) throw updateError
      
      const index = customers.value.findIndex(c => c.id_customer === id)
      if (index !== -1) {
        customers.value[index] = data
      }
      
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error updating customer:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  async function deleteCustomer(id) {
    loading.value = true
    error.value = null
    try {
      const { error: deleteError } = await supabase
        .from('customers')
        .delete()
        .eq('id_customer', id)

      if (deleteError) throw deleteError
      
      customers.value = customers.value.filter(c => c.id_customer !== id)
      
      return { success: true }
    } catch (err) {
      error.value = err.message
      console.error('Error deleting customer:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  async function searchCustomers(searchTerm) {
    loading.value = true
    error.value = null
    try {
      const { data, error: searchError } = await supabase
        .from('customers')
        .select('*')
        .or(`nama.ilike.%${searchTerm}%,no_hp.ilike.%${searchTerm}%,alamat.ilike.%${searchTerm}%`)
        .order('id_customer', { ascending: false })

      if (searchError) throw searchError
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error searching customers:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  return {
    customers,
    loading,
    error,
    fetchCustomers,
    getCustomerById,
    createCustomer,
    updateCustomer,
    deleteCustomer,
    searchCustomers
  }
})