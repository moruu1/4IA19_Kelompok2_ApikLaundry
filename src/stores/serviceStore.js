import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '@/lib/supabase'

export const useServiceStore = defineStore('service', () => {
  const services = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Fetch all services
  async function fetchServices() {
    loading.value = true
    error.value = null
    try {
      const { data, error: fetchError } = await supabase
        .from('services')
        .select('*')
        .order('id_service', { ascending: true })

      if (fetchError) throw fetchError
      services.value = data || []
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error fetching services:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Get service by ID
  async function getServiceById(id) {
    loading.value = true
    error.value = null
    try {
      const { data, error: fetchError } = await supabase
        .from('services')
        .select('*')
        .eq('id_service', id)
        .single()

      if (fetchError) throw fetchError
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error fetching service:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Get service with BOM (Bill of Materials)
  async function getServiceWithBOM(id) {
    loading.value = true
    error.value = null
    try {
      const { data, error: fetchError } = await supabase
        .from('services')
        .select(`
          *,
          service_bom (
            id_bom,
            jumlah_dipakai_per_unit,
            inventory_items (
              id_inventory_item,
              nama_barang,
              stok_sisa,
              unit
            )
          )
        `)
        .eq('id_service', id)
        .single()

      if (fetchError) throw fetchError
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error fetching service with BOM:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Create new service
  async function createService(serviceData) {
    loading.value = true
    error.value = null
    try {
      const { data, error: insertError } = await supabase
        .from('services')
        .insert([serviceData])
        .select()
        .single()

      if (insertError) throw insertError
      services.value.push(data)
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error creating service:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Update service
  async function updateService(id, serviceData) {
    loading.value = true
    error.value = null
    try {
      const { data, error: updateError } = await supabase
        .from('services')
        .update(serviceData)
        .eq('id_service', id)
        .select()
        .single()

      if (updateError) throw updateError
      
      const index = services.value.findIndex(s => s.id_service === id)
      if (index !== -1) {
        services.value[index] = data
      }
      
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error updating service:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Delete service
  async function deleteService(id) {
    loading.value = true
    error.value = null
    try {
      const { error: deleteError } = await supabase
        .from('services')
        .delete()
        .eq('id_service', id)

      if (deleteError) throw deleteError
      
      services.value = services.value.filter(s => s.id_service !== id)
      
      return { success: true }
    } catch (err) {
      error.value = err.message
      console.error('Error deleting service:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  return {
    services,
    loading,
    error,
    fetchServices,
    getServiceById,
    getServiceWithBOM,
    createService,
    updateService,
    deleteService
  }
})
