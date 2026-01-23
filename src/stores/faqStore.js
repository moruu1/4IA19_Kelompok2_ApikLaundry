import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '@/lib/supabase'

export const useFAQStore = defineStore('faq', () => {
  const faqs = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Fetch all FAQs
  async function fetchFAQs() {
    loading.value = true
    error.value = null
    try {
      const { data, error: fetchError } = await supabase
        .from('faq')
        .select('*')
        .order('id_faq', { ascending: true })

      if (fetchError) throw fetchError
      faqs.value = data || []
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error fetching FAQs:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Search FAQs (for chatbot)
  async function searchFAQ(searchTerm) {
    loading.value = true
    error.value = null
    try {
      const { data, error: searchError } = await supabase
        .from('faq')
        .select('*')
        .or(`pertanyaan.ilike.%${searchTerm}%,jawaban.ilike.%${searchTerm}%`)

      if (searchError) throw searchError
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error searching FAQs:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Get FAQ by ID
  async function getFAQById(id) {
    loading.value = true
    error.value = null
    try {
      const { data, error: fetchError } = await supabase
        .from('faq')
        .select('*')
        .eq('id_faq', id)
        .single()

      if (fetchError) throw fetchError
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error fetching FAQ:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Create new FAQ
  async function createFAQ(faqData) {
    loading.value = true
    error.value = null
    try {
      const { data, error: insertError } = await supabase
        .from('faq')
        .insert([faqData])
        .select()
        .single()

      if (insertError) throw insertError
      faqs.value.push(data)
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error creating FAQ:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Update FAQ
  async function updateFAQ(id, faqData) {
    loading.value = true
    error.value = null
    try {
      const { data, error: updateError } = await supabase
        .from('faq')
        .update(faqData)
        .eq('id_faq', id)
        .select()
        .single()

      if (updateError) throw updateError
      
      const index = faqs.value.findIndex(f => f.id_faq === id)
      if (index !== -1) {
        faqs.value[index] = data
      }
      
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      console.error('Error updating FAQ:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Delete FAQ
  async function deleteFAQ(id) {
    loading.value = true
    error.value = null
    try {
      const { error: deleteError } = await supabase
        .from('faq')
        .delete()
        .eq('id_faq', id)

      if (deleteError) throw deleteError
      
      faqs.value = faqs.value.filter(f => f.id_faq !== id)
      
      return { success: true }
    } catch (err) {
      error.value = err.message
      console.error('Error deleting FAQ:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  return {
    faqs,
    loading,
    error,
    fetchFAQs,
    searchFAQ,
    getFAQById,
    createFAQ,
    updateFAQ,
    deleteFAQ
  }
})
