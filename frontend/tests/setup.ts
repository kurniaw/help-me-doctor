import { ref, computed, reactive, readonly, watch, watchEffect } from 'vue'
import { config } from '@vue/test-utils'
import PrimeVue from 'primevue/config'
import Textarea from 'primevue/textarea'
import { vi } from 'vitest'
import ChatUrgencyBadge from '~/components/chat/UrgencyBadge.vue'

// Vue reactivity globals (Nuxt auto-imports these; plain TS store files need them as globals)
vi.stubGlobal('ref', ref)
vi.stubGlobal('computed', computed)
vi.stubGlobal('reactive', reactive)
vi.stubGlobal('readonly', readonly)
vi.stubGlobal('watch', watch)
vi.stubGlobal('watchEffect', watchEffect)

// Nuxt composable globals
vi.stubGlobal('useCookie', vi.fn(() => ref<string | null>(null)))
vi.stubGlobal('navigateTo', vi.fn())
vi.stubGlobal('useRuntimeConfig', vi.fn(() => ({
  public: { apiBase: 'http://localhost:8000' },
})))
vi.stubGlobal('useAuthStore', vi.fn(() => ({
  token: 'test-token',
  user: ref(null),
  isAuthenticated: true,
})))
vi.stubGlobal('useRouter', vi.fn(() => ({ push: vi.fn() })))
vi.stubGlobal('$fetch', vi.fn())

vi.mock('#app', () => ({
  useRuntimeConfig: () => ({
    public: { apiBase: 'http://localhost:8000' },
  }),
  useRouter: () => ({ push: vi.fn() }),
  navigateTo: vi.fn(),
  useCookie: () => ref(null),
  definePageMeta: vi.fn(),
  defineNuxtRouteMiddleware: vi.fn(),
  useNuxtApp: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useRoute: () => ({ params: {}, query: {} }),
}))

// Register PrimeVue and Nuxt auto-imported components globally for component tests
config.global.plugins = [PrimeVue]
config.global.components = { Textarea, ChatUrgencyBadge }
