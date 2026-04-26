import { vi } from 'vitest'

// Mock Nuxt auto-imports for tests
vi.mock('#app', () => ({
  useRuntimeConfig: () => ({
    public: { apiBase: 'http://localhost:8000' },
  }),
  useRouter: () => ({ push: vi.fn() }),
  navigateTo: vi.fn(),
  useCookie: () => ({ value: null }),
  definePageMeta: vi.fn(),
  defineNuxtRouteMiddleware: vi.fn(),
  useNuxtApp: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useRoute: () => ({ params: {}, query: {} }),
}))
