import { ref, onMounted } from 'vue'

const isDark = ref(true)

export function useTheme() {
  const toggleTheme = () => {
    isDark.value = !isDark.value
    updateTheme()
  }

  const updateTheme = () => {
    const html = document.documentElement
    if (isDark.value) {
      html.classList.remove('light')
      html.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      html.classList.remove('dark')
      html.classList.add('light')
      localStorage.setItem('theme', 'light')
    }
  }

  const initTheme = () => {
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme === 'light') {
      isDark.value = false
    } else {
      isDark.value = true
    }
    updateTheme()
  }

  onMounted(() => {
    // Only init if not already done (optional, but good for SSR safety in other contexts)
    // Here we can just call updateTheme based on current state, 
    // but usually we want to read from storage once.
    // Since this composable might be used in multiple places, we rely on the state 
    // being synced or just init in App.vue once. 
    // For simplicity, let's expose initTheme to be called in App.vue
  })

  return {
    isDark,
    toggleTheme,
    initTheme
  }
}
