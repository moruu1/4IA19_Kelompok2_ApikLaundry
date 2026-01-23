import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '@/lib/supabase'

export const useTransactionStore = defineStore('transaction', () => {
  const transactions = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Fetch all transactions with related data
  async function fetchTransactions() {
    loading.value = true
    error.value = null
    try {
      const { data, error: fetchError } = await supabase
        .from('transactions')
        .select(`
          *,
          customers (
            id_customer,
            nama,
            no_hp,
            alamat
          ),
          services (
            id_service,
            nama_layanan,
            harga_per_unit
          )
        `)
        .order('tanggal_masuk', { ascending: false })

      if (fetchError) throw fetchError
      transactions.value = data || []
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error fetching transactions:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Get transaction by ID
  async function getTransactionById(id) {
    loading.value = true
    error.value = null
    try {
      const { data, error: fetchError } = await supabase
        .from('transactions')
        .select(`
          *,
          customers (
            id_customer,
            nama,
            no_hp,
            alamat
          ),
          services (
            id_service,
            nama_layanan,
            harga_per_unit
          )
        `)
        .eq('id_transaction', id)
        .single()

      if (fetchError) throw fetchError
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error fetching transaction:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Get transactions by customer ID
  async function getTransactionsByCustomer(customerId) {
    loading.value = true
    error.value = null
    try {
      const { data, error: fetchError } = await supabase
        .from('transactions')
        .select(`
          *,
          services (
            id_service,
            nama_layanan,
            harga_per_unit
          )
        `)
        .eq('customer_id', customerId)
        .order('tanggal_masuk', { ascending: false })

      if (fetchError) throw fetchError
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error fetching customer transactions:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Helper function to reduce inventory stock based on service BOM (Bill of Materials)
  // Following inventory.py prediction logic
  async function reduceInventoryStock(serviceId, quantity) {
    try {
      console.log(`Reducing inventory for service ${serviceId}, quantity: ${quantity}`)
      
      // Query service_bom to get material requirements
      const { data: bomData, error: bomError } = await supabase
        .from('service_bom')
        .select(`
          jumlah_dipakai_per_unit,
          inventory_items (
            id_inventory_item,
            nama_barang,
            stok_sisa,
            unit
          )
        `)
        .eq('service_id', serviceId)
      
      if (bomError) {
        console.error('Error fetching BOM data:', bomError)
        return
      }
      
      if (!bomData || bomData.length === 0) {
        console.log('No BOM data found for service:', serviceId)
        return
      }
      
      // Loop through each material and reduce stock
      for (const bomEntry of bomData) {
        const usagePerUnit = bomEntry.jumlah_dipakai_per_unit
        const inventoryItem = bomEntry.inventory_items
        
        if (!inventoryItem) continue
        
        // Calculate total material usage: order_quantity × usage_per_unit
        const totalUsage = quantity * usagePerUnit
        const newStock = inventoryItem.stok_sisa - totalUsage
        
        console.log(`Material: ${inventoryItem.nama_barang}`)
        console.log(`  Current stock: ${inventoryItem.stok_sisa} ${inventoryItem.unit}`)
        console.log(`  Usage rate: ${usagePerUnit} ${inventoryItem.unit}/unit`)
        console.log(`  Total usage: ${totalUsage} ${inventoryItem.unit}`)
        console.log(`  New stock: ${newStock} ${inventoryItem.unit}`)
        
        // Update inventory_items with new stock
        const { error: updateError } = await supabase
          .from('inventory_items')
          .update({ stok_sisa: newStock })
          .eq('id_inventory_item', inventoryItem.id_inventory_item)
        
        if (updateError) {
          console.error(`Error updating inventory ${inventoryItem.nama_barang}:`, updateError)
        } else {
          console.log(`✅ Successfully updated ${inventoryItem.nama_barang} stock`)
        }
      }
    } catch (err) {
      console.error('Error reducing inventory stock:', err)
    }
  }

  // Create new transaction
  async function createTransaction(transactionData) {
    loading.value = true
    error.value = null
    try {
      const { data, error: insertError } = await supabase
        .from('transactions')
        .insert([transactionData])
        .select(`
          *,
          customers (
            id_customer,
            nama,
            no_hp,
            alamat
          ),
          services (
            id_service,
            nama_layanan,
            harga_per_unit
          )
        `)
        .single()

      if (insertError) throw insertError
      
      // AUTO-REDUCE INVENTORY STOCK based on service BOM
      await reduceInventoryStock(data.service_id, data.jumlah_unit)
      
      // If status_pembayaran is 'Lunas', create financial record
      if (transactionData.status_pembayaran === 'Lunas') {
        console.log('Creating financial record for transaction:', data.id_transaction)
        const { data: financialData, error: financialError } = await supabase
          .from('financials')
          .insert([{
            transaction_id: data.id_transaction,
            tanggal: data.tanggal_masuk,
            tipe: 'Pemasukan',
            keterangan: `Pembayaran ${data.nomor_nota} - ${data.customers?.nama || ''}`,
            jumlah: data.total_harga,
            metode_pembayaran: transactionData.metode_pembayaran
          }])
          .select()
        
        if (financialError) {
          console.error('Error creating financial record:', financialError)
        } else {
          console.log('Financial record created:', financialData)
        }
      }
      
      transactions.value.unshift(data)
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error creating transaction:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Update transaction
  async function updateTransaction(id, transactionData) {
    loading.value = true
    error.value = null
    try {
      const { data, error: updateError } = await supabase
        .from('transactions')
        .update(transactionData)
        .eq('id_transaction', id)
        .select(`
          *,
          customers (
            id_customer,
            nama,
            no_hp,
            alamat
          ),
          services (
            id_service,
            nama_layanan,
            harga_per_unit
          )
        `)
        .single()

      if (updateError) throw updateError
      
      // If status_pembayaran changed to 'Lunas', create financial record
      if (transactionData.status_pembayaran === 'Lunas') {
        console.log('Checking financial record for transaction:', id)
        // Check if financial record already exists
        const { data: existingFinancial } = await supabase
          .from('financials')
          .select('id_financial')
          .eq('transaction_id', id)
          .maybeSingle()
        
        if (!existingFinancial) {
          console.log('Creating new financial record for transaction:', id)
          // Create financial record
          const { data: financialData, error: financialError } = await supabase
            .from('financials')
            .insert([{
              transaction_id: id,
              tanggal: data.tanggal_masuk,
              tipe: 'Pemasukan',
              keterangan: `Pembayaran ${data.nomor_nota} - ${data.customers?.nama || ''}`,
              jumlah: data.total_harga,
              metode_pembayaran: data.metode_pembayaran
            }])
            .select()
          
          if (financialError) {
            console.error('Error creating financial record:', financialError)
          } else {
            console.log('Financial record created:', financialData)
          }
        } else {
          console.log('Financial record already exists for transaction:', id)
        }
      }
      
      // Update local state
      const index = transactions.value.findIndex(t => t.id_transaction === id)
      if (index !== -1) {
        transactions.value[index] = data
      }
      
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error updating transaction:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Update transaction status
  async function updateTransactionStatus(id, status) {
    return await updateTransaction(id, { status_pesanan: status })
  }

  // Update payment status
  async function updatePaymentStatus(id, status) {
    return await updateTransaction(id, { status_pembayaran: status })
  }

  // Delete transaction
  async function deleteTransaction(id) {
    loading.value = true
    error.value = null
    try {
      const { error: deleteError } = await supabase
        .from('transactions')
        .delete()
        .eq('id_transaction', id)

      if (deleteError) throw deleteError
      
      // Remove from local state
      transactions.value = transactions.value.filter(t => t.id_transaction !== id)
      
      return { success: true }
    } catch (err) {
      error.value = err.message
      console.error('Error deleting transaction:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Search transactions
  async function searchTransactions(searchTerm) {
    loading.value = true
    error.value = null
    try {
      const { data, error: searchError } = await supabase
        .from('transactions')
        .select(`
          *,
          customers (
            id_customer,
            nama,
            no_hp,
            alamat
          ),
          services (
            id_service,
            nama_layanan,
            harga_per_unit
          )
        `)
        .or(`nomor_nota.ilike.%${searchTerm}%`)
        .order('tanggal_masuk', { ascending: false })

      if (searchError) throw searchError
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error searching transactions:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  return {
    transactions,
    loading,
    error,
    fetchTransactions,
    getTransactionById,
    getTransactionsByCustomer,
    createTransaction,
    updateTransaction,
    updateTransactionStatus,
    updatePaymentStatus,
    deleteTransaction,
    searchTransactions
  }
})
