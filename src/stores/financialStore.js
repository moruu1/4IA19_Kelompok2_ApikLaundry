import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '@/lib/supabase'

export const useFinancialStore = defineStore('financial', () => {
  const financials = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Fetch all financial records
  async function fetchFinancials(startDate = null, endDate = null) {
    loading.value = true
    error.value = null
    try {
      let query = supabase
        .from('financials')
        .select(`
          *,
          transactions (
            id_transaction,
            nomor_nota,
            customers (
              id_customer,
              nama
            )
          )
        `)
        .order('tanggal', { ascending: false })

      // Filter by date range if provided
      if (startDate && endDate) {
        query = query.gte('tanggal', startDate).lte('tanggal', endDate)
      }

      const { data, error: fetchError } = await query

      if (fetchError) throw fetchError
      financials.value = data || []
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error fetching financials:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Get financial by ID
  async function getFinancialById(id) {
    loading.value = true
    error.value = null
    try {
      const { data, error: fetchError } = await supabase
        .from('financials')
        .select(`
          *,
          transactions (
            id_transaction,
            nomor_nota,
            customers (
              id_customer,
              nama
            )
          )
        `)
        .eq('id_financial', id)
        .single()

      if (fetchError) throw fetchError
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error fetching financial:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Create new financial record
  async function createFinancial(financialData) {
    loading.value = true
    error.value = null
    try {
      const { data, error: insertError } = await supabase
        .from('financials')
        .insert([financialData])
        .select()
        .single()

      if (insertError) throw insertError
      financials.value.unshift(data)
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error creating financial record:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Update financial record
  async function updateFinancial(id, financialData) {
    loading.value = true
    error.value = null
    try {
      const { data, error: updateError } = await supabase
        .from('financials')
        .update(financialData)
        .eq('id_financial', id)
        .select()
        .single()

      if (updateError) throw updateError
      
      const index = financials.value.findIndex(f => f.id_financial === id)
      if (index !== -1) {
        financials.value[index] = data
      }
      
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error updating financial record:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Delete financial record
  async function deleteFinancial(id) {
    loading.value = true
    error.value = null
    try {
      const { error: deleteError } = await supabase
        .from('financials')
        .delete()
        .eq('id_financial', id)

      if (deleteError) throw deleteError
      
      financials.value = financials.value.filter(f => f.id_financial !== id)
      
      return { success: true }
    } catch (err) {
      error.value = err.message
      console.error('Error deleting financial record:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Get financial summary
  async function getFinancialSummary(startDate = null, endDate = null) {
    loading.value = true
    error.value = null
    try {
      let query = supabase
        .from('financials')
        .select('tipe, jumlah')

      if (startDate && endDate) {
        query = query.gte('tanggal', startDate).lte('tanggal', endDate)
      }

      const { data, error: fetchError } = await query

      if (fetchError) throw fetchError

      // Calculate summary
      const summary = {
        totalPemasukan: 0,
        totalPengeluaran: 0,
        selisih: 0
      }

      data.forEach(item => {
        if (item.tipe === 'Pemasukan') {
          summary.totalPemasukan += item.jumlah
        } else if (item.tipe === 'Pengeluaran') {
          summary.totalPengeluaran += item.jumlah
        }
      })

      summary.selisih = summary.totalPemasukan - summary.totalPengeluaran

      return { success: true, data: summary }
    } catch (err) {
      error.value = err.message
      console.error('Error fetching financial summary:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Get financial by type
  async function getFinancialByType(tipe, startDate = null, endDate = null) {
    loading.value = true
    error.value = null
    try {
      let query = supabase
        .from('financials')
        .select('*')
        .eq('tipe', tipe)
        .order('tanggal', { ascending: false })

      if (startDate && endDate) {
        query = query.gte('tanggal', startDate).lte('tanggal', endDate)
      }

      const { data, error: fetchError } = await query

      if (fetchError) throw fetchError
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error fetching financials by type:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  return {
    financials,
    loading,
    error,
    fetchFinancials,
    getFinancialById,
    createFinancial,
    updateFinancial,
    deleteFinancial,
    getFinancialSummary,
    getFinancialByType
  }
})
