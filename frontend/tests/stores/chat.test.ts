import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.stubGlobal('fetch', vi.fn())

describe('chat store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('initialises with empty messages', async () => {
    const { useChatStore } = await import('~/stores/chat')
    const store = useChatStore()
    expect(store.messages).toHaveLength(0)
  })

  it('appends user message when sendMessage called', async () => {
    const mockAuthStore = { token: { value: 'test-token' }, isAuthenticated: true }
    vi.mock('~/stores/auth', () => ({ useAuthStore: () => mockAuthStore }))

    // Mock SSE response
    const encoder = new TextEncoder()
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(
          encoder.encode('data: {"type":"chunk","content":"Test response","urgency":"MEDIUM","pathway":"MEDICAL"}\n\n')
        )
        controller.enqueue(
          encoder.encode('data: {"type":"done","content":"","urgency":"MEDIUM","pathway":"MEDICAL"}\n\n')
        )
        controller.close()
      },
    })

    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      body: stream,
    } as Response)

    const { useChatStore } = await import('~/stores/chat')
    const store = useChatStore()

    await store.sendMessage('I have chest pain')

    // First message is user
    expect(store.messages[0]?.role).toBe('user')
    expect(store.messages[0]?.content).toBe('I have chest pain')
  })

  it('clears messages on clearMessages', async () => {
    const { useChatStore } = await import('~/stores/chat')
    const store = useChatStore()
    store.clearMessages()
    expect(store.messages).toHaveLength(0)
  })

  it('starts and ends streaming flag correctly', async () => {
    const { useChatStore } = await import('~/stores/chat')
    const store = useChatStore()
    expect(store.streaming).toBe(false)
  })
})
