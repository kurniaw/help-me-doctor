import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

// Mock $fetch
vi.stubGlobal('$fetch', vi.fn())

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('initialises with no user and no token', async () => {
    const { useAuthStore } = await import('~/stores/auth')
    const store = useAuthStore()
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })

  it('sets token on successful login', async () => {
    const mockFetch = vi.mocked($fetch as ReturnType<typeof vi.fn>)
    // JWT with payload { sub: "user1", name: "Alice", email: "alice@test.com" }
    const fakeJwt =
      'eyJhbGciOiJIUzI1NiJ9.' +
      btoa(JSON.stringify({ sub: 'user1', name: 'Alice', email: 'alice@test.com' })) +
      '.signature'
    mockFetch.mockResolvedValueOnce({
      access_token: fakeJwt,
      token_type: 'bearer',
      expires_in: 3600,
    })

    const { useAuthStore } = await import('~/stores/auth')
    const store = useAuthStore()
    await store.login({ email: 'alice@test.com', password: 'password123' })

    expect(store.isAuthenticated).toBe(true)
  })

  it('clears state on logout', async () => {
    const { useAuthStore } = await import('~/stores/auth')
    const store = useAuthStore()
    store.logout()
    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
  })
})
