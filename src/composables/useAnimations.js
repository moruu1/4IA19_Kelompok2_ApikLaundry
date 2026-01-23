import { ref } from 'vue'

/**
 * Composable for managing UI animations
 * Provides success, error, and loading states with animations
 */

export function useAnimations() {
  const isAnimating = ref(false)
  
  /**
   * Trigger success animation on an element
   * @param {HTMLElement} element - The element to animate
   */
  const triggerSuccess = (element) => {
    if (!element) return
    
    isAnimating.value = true
    element.classList.add('success-animation')
    
    setTimeout(() => {
      element.classList.remove('success-animation')
      isAnimating.value = false
    }, 500)
  }
  
  /**
   * Trigger error shake animation on an element
   * @param {HTMLElement} element - The element to animate
   */
  const triggerError = (element) => {
    if (!element) return
    
    isAnimating.value = true
    element.classList.add('error-animation')
    
    setTimeout(() => {
      element.classList.remove('error-animation')
      isAnimating.value = false
    }, 400)
  }
  
  /**
   * Add loading state to a button
   * @param {HTMLElement} button - The button element
   */
  const setButtonLoading = (button, loading = true) => {
    if (!button) return
    
    if (loading) {
      button.classList.add('btn-loading')
      button.disabled = true
    } else {
      button.classList.remove('btn-loading')
      button.disabled = false
    }
  }
  
  /**
   * Trigger pulse animation for badges
   * @param {HTMLElement} element - The element to pulse
   */
  const triggerPulse = (element) => {
    if (!element) return
    
    element.classList.add('badge-pulse')
    
    setTimeout(() => {
      element.classList.remove('badge-pulse')
    }, 2000)
  }
  
  /**
   * Add shimmer effect to cards during loading
   * @param {HTMLElement} element - The card element
   */
  const addShimmer = (element, active = true) => {
    if (!element) return
    
    if (active) {
      element.classList.add('card-shimmer')
    } else {
      element.classList.remove('card-shimmer')
    }
  }
  
  return {
    isAnimating,
    triggerSuccess,
    triggerError,
    setButtonLoading,
    triggerPulse,
    addShimmer
  }
}
