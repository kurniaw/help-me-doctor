import { defineStore } from 'pinia'
import type { LoginPayload, RegisterPayload, TokenResponse, User } from '~/types/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = useCookie<string | null>('hmd_token', {
    maxAge: 3600,
    secure: true,
    sameSite: 'strict',
    httpOnly: false, // Must be false so JS can read it for SSE requests
  })

  const user = ref<User | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  async function register(payload: RegisterPayload): Promise<void> {
    loading.value = true
    try {
      const data = await $fetch<TokenResponse>(`${apiBase}/api/v1/auth/register`, {
        method: 'POST',
        body: payload,
      })
      token.value = data.access_token
      // Decode user info from token payload (base64)
      _decodeToken(data.access_token)
    } finally {
      loading.value = false
    }
  }

  async function login(payload: LoginPayload): Promise<void> {
    loading.value = true
    try {
      const data = await $fetch<TokenResponse>(`${apiBase}/api/v1/auth/login`, {
        method: 'POST',
        body: payload,
      })
      token.value = data.access_token
      _decodeToken(data.access_token)
    } finally {
      loading.value = false
    }
  }

  function logout(): void {
    token.value = null
    user.value = null
    navigateTo('/login')
  }

  function _decodeToken(jwt: string): void {
    try {
      const parts = jwt.split('.')
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1]!))
        user.value = {
          id: payload.sub ?? '',
          name: payload.name ?? 'User',
          email: payload.email ?? '',
        }
      }
    } catch {
      // Token decode failure is non-fatal; user info is cosmetic
    }
  }

  return {
    token: readonly(token),
    user: readonly(user),
    loading: readonly(loading),
    isAuthenticated,
    register,
    login,
    logout,
  }
})
