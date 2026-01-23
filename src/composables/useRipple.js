/**
 * Composable for adding ripple effect to elements
 * Usage: const addRipple = useRipple()
 * Then: @click="addRipple($event)"
 */

export function useRipple() {
  const addRipple = (event) => {
    const button = event.currentTarget
    
    // Create ripple element
    const ripple = document.createElement('span')
    const diameter = Math.max(button.clientWidth, button.clientHeight)
    const radius = diameter / 2
    
    // Calculate position
    const rect = button.getBoundingClientRect()
    ripple.style.width = ripple.style.height = `${diameter}px`
    ripple.style.left = `${event.clientX - rect.left - radius}px`
    ripple.style.top = `${event.clientY - rect.top - radius}px`
    ripple.classList.add('ripple-effect')
    
    // Remove existing ripples
    const existingRipple = button.querySelector('.ripple-effect')
    if (existingRipple) {
      existingRipple.remove()
    }
    
    // Add ripple
    button.appendChild(ripple)
    
    // Remove after animation
    setTimeout(() => {
      ripple.remove()
    }, 600)
  }
  
  return addRipple
}
