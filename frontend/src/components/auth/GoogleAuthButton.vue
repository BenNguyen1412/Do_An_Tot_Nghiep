<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/auth'

type GoogleButtonText = 'signin_with' | 'signup_with' | 'continue_with'

const props = withDefaults(
  defineProps<{
    label: string
    redirectTo?: string
    buttonText?: GoogleButtonText
  }>(),
  {
    redirectTo: '/user/home',
    buttonText: 'continue_with',
  },
)

const authStore = useAuthStore()
const router = useRouter()
const toast = useToast()

const buttonContainer = ref<HTMLDivElement | null>(null)
const isProcessing = ref(false)
const scriptError = ref('')

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID?.trim() || ''

let googleScriptPromise: Promise<void> | null = null

const loadGoogleScript = () => {
  if ((window as Window & { google?: unknown }).google) {
    return Promise.resolve()
  }

  if (googleScriptPromise) {
    return googleScriptPromise
  }

  googleScriptPromise = new Promise<void>((resolve, reject) => {
    const existingScript = document.querySelector<HTMLScriptElement>(
      'script[data-google-identity-script="true"]',
    )

    if (existingScript) {
      existingScript.addEventListener('load', () => resolve(), { once: true })
      existingScript.addEventListener(
        'error',
        () => reject(new Error('Failed to load Google script')),
        {
          once: true,
        },
      )
      return
    }

    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    script.dataset.googleIdentityScript = 'true'
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('Failed to load Google script'))
    document.head.appendChild(script)
  })

  return googleScriptPromise
}

const renderButton = async () => {
  scriptError.value = ''

  if (!googleClientId) {
    scriptError.value = 'Set VITE_GOOGLE_CLIENT_ID in frontend .env to enable Google sign-in.'
    return
  }

  if (!buttonContainer.value) {
    return
  }

  try {
    await loadGoogleScript()

    const google = (window as Window & { google?: any }).google
    if (!google?.accounts?.id) {
      throw new Error('Google Identity Services is unavailable')
    }

    google.accounts.id.initialize({
      client_id: googleClientId,
      callback: async (response: { credential?: string }) => {
        if (!response.credential) {
          return
        }

        isProcessing.value = true

        try {
          const result = await authStore.loginWithGoogle(response.credential)

          if (result.success) {
            toast.success(`✅ ${props.label} successful!`, { timeout: 2000 })
            await router.push(props.redirectTo)
            return
          }

          const errorMessage = result.error || 'Google sign-in failed. Please try again.'
          toast.error(`❌ ${errorMessage}`, { timeout: 4000 })
        } catch {
          toast.error('❌ Google sign-in failed. Please try again.', { timeout: 4000 })
        } finally {
          isProcessing.value = false
        }
      },
    })

    google.accounts.id.renderButton(buttonContainer.value, {
      theme: 'outline',
      size: 'large',
      text: props.buttonText,
      shape: 'pill',
      width: buttonContainer.value.clientWidth || 360,
    })
  } catch (error) {
    console.error('Google sign-in initialization failed:', error)
    scriptError.value = 'Google sign-in is unavailable right now.'
  }
}

onMounted(() => {
  void renderButton()
})
</script>

<template>
  <div class="google-auth-section">
    <div class="or-divider">
      <span>OR</span>
    </div>

    <div v-if="googleClientId" class="google-button-wrap">
      <div ref="buttonContainer" class="google-button-container"></div>
      <p v-if="isProcessing" class="google-loading">Processing Google sign-in...</p>
    </div>

    <p v-else class="google-config-hint">
      Set <strong>VITE_GOOGLE_CLIENT_ID</strong> in frontend .env to enable Google sign-in.
    </p>

    <p v-if="scriptError" class="google-config-hint">{{ scriptError }}</p>
  </div>
</template>

<style scoped>
.google-auth-section {
  margin-top: 18px;
}

.or-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
  color: #7a7a7a;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.12em;
}

.or-divider::before,
.or-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(45, 80, 22, 0.25), transparent);
}

.google-button-wrap {
  display: grid;
  gap: 10px;
}

.google-button-container {
  min-height: 44px;
}

.google-loading,
.google-config-hint {
  margin: 0;
  font-size: 0.88rem;
  color: #5f6a5f;
  line-height: 1.45;
}

.google-config-hint strong {
  color: #2d5016;
}
</style>
