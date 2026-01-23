import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '@/lib/supabase'

export const useInventoryStore = defineStore('inventory', () => {
  const inventoryItems = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Fetch all inventory items
  async function fetchInventoryItems() {
    loading.value = true
    error.value = null
    try {
      const { data, error: fetchError } = await supabase
        .from('inventory_items')
        .select('*')
        .order('id_inventory_item', { ascending: true })

      if (fetchError) throw fetchError
      inventoryItems.value = data || []
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error fetching inventory:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Get inventory item by ID
  async function getInventoryItemById(id) {
    loading.value = true
    error.value = null
    try {
      const { data, error: fetchError } = await supabase
        .from('inventory_items')
        .select('*')
        .eq('id_inventory_item', id)
        .single()

      if (fetchError) throw fetchError
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error fetching inventory item:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Create new inventory item
  async function createInventoryItem(itemData) {
    loading.value = true
    error.value = null
    try {
      const { data, error: insertError } = await supabase
        .from('inventory_items')
        .insert([itemData])
        .select()
        .single()

      if (insertError) throw insertError
      inventoryItems.value.push(data)
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error creating inventory item:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Update inventory item
  async function updateInventoryItem(id, itemData) {
    loading.value = true
    error.value = null
    try {
      const { data, error: updateError } = await supabase
        .from('inventory_items')
        .update(itemData)
        .eq('id_inventory_item', id)
        .select()
        .single()

      if (updateError) throw updateError
      
      const index = inventoryItems.value.findIndex(i => i.id_inventory_item === id)
      if (index !== -1) {
        inventoryItems.value[index] = data
      }
      
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error updating inventory item:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Update stock
  async function updateStock(id, newStock) {
    return await updateInventoryItem(id, { stok_sisa: newStock })
  }

  // Decrease stock (for usage)
  async function decreaseStock(id, amount) {
    loading.value = true
    error.value = null
    try {
      // Get current stock first
      const { data: currentItem, error: fetchError } = await supabase
        .from('inventory_items')
        .select('stok_sisa')
        .eq('id_inventory_item', id)
        .single()

      if (fetchError) throw fetchError

      const newStock = currentItem.stok_sisa - amount
      if (newStock < 0) {
        throw new Error('Stok tidak mencukupi')
      }

      return await updateStock(id, newStock)
    } catch (err) {
      error.value = err.message
      console.error('Error decreasing stock:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Increase stock (for restock)
  async function increaseStock(id, amount) {
    loading.value = true
    error.value = null
    try {
      const { data: currentItem, error: fetchError } = await supabase
        .from('inventory_items')
        .select('stok_sisa')
        .eq('id_inventory_item', id)
        .single()

      if (fetchError) throw fetchError

      const newStock = currentItem.stok_sisa + amount
      return await updateStock(id, newStock)
    } catch (err) {
      error.value = err.message
      console.error('Error increasing stock:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Delete inventory item
  async function deleteInventoryItem(id) {
    loading.value = true
    error.value = null
    try {
      const { error: deleteError } = await supabase
        .from('inventory_items')
        .delete()
        .eq('id_inventory_item', id)

      if (deleteError) throw deleteError
      
      inventoryItems.value = inventoryItems.value.filter(i => i.id_inventory_item !== id)
      
      return { success: true }
    } catch (err) {
      error.value = err.message
      console.error('Error deleting inventory item:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Get low stock items
  async function getLowStockItems(threshold = 10) {
    loading.value = true
    error.value = null
    try {
      const { data, error: fetchError } = await supabase
        .from('inventory_items')
        .select('*')
        .lte('stok_sisa', threshold)
        .order('stok_sisa', { ascending: true })

      if (fetchError) throw fetchError
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error fetching low stock items:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  return {
    inventoryItems,
    loading,
    error,
    fetchInventoryItems,
    getInventoryItemById,
    createInventoryItem,
    updateInventoryItem,
    updateStock,
    decreaseStock,
    increaseStock,
    deleteInventoryItem,
    getLowStockItems
  }
})
