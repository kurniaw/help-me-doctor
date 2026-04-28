import { defineStore } from 'pinia'
import type { Message, StreamChunk, UrgencyLevel } from '~/types/chat'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<Message[]>([])
  const streaming = ref(false)
  const currentStreamContent = ref('')
  const currentUrgency = ref<UrgencyLevel | undefined>()
  const currentPathway = ref<string | undefined>()
  const sessionId = ref<string | undefined>()
  const promptsRemaining = ref<number | null>(null)
  const promptsLimit = ref<number>(3)

  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase
  const authStore = useAuthStore()

  function _generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
  }

  function _parseSseLines(raw: string): StreamChunk[] {
    const chunks: StreamChunk[] = []
    const lines = raw.split('\n')
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const json = line.slice(6)
          const chunk = JSON.parse(json) as StreamChunk
          chunks.push(chunk)
        } catch {
          // Ignore malformed SSE lines
        }
      }
    }
    return chunks
  }

  async function sendMessage(text: string): Promise<void> {
    if (!text.trim() || streaming.value) return

    const token = authStore.token
    if (!token) {
      navigateTo('/login')
      return
    }

    // Append user message
    messages.value.push({
      id: _generateId(),
      role: 'user',
      content: text.trim(),
      timestamp: new Date(),
    })

    // Start streaming state
    streaming.value = true
    currentStreamContent.value = ''
    currentUrgency.value = undefined
    currentPathway.value = undefined

    // Add placeholder assistant message
    const assistantId = _generateId()
    messages.value.push({
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
    })

    try {
      const response = await fetch(`${apiBase}/api/v1/chat/stream`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: text.trim(),
          session_id: sessionId.value,
        }),
      })

      if (response.status === 429) {
        const limit = promptsLimit.value
        const msgIdx = messages.value.findIndex((m) => m.id === assistantId)
        if (msgIdx !== -1) {
          messages.value[msgIdx] = {
            ...messages.value[msgIdx]!,
            content: `You've reached your daily limit of ${limit} prompts. Try again tomorrow.`,
          }
        }
        promptsRemaining.value = 0
        return
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const remaining = response.headers.get('X-RateLimit-Remaining')
      const limit = response.headers.get('X-RateLimit-Limit')
      if (remaining !== null) promptsRemaining.value = parseInt(remaining, 10)
      if (limit !== null) promptsLimit.value = parseInt(limit, 10)

      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const chunks = _parseSseLines(buffer)
        // Keep any partial line in the buffer
        const lastNewline = buffer.lastIndexOf('\n')
        buffer = lastNewline >= 0 ? buffer.slice(lastNewline + 1) : buffer

        for (const chunk of chunks) {
          if (chunk.type === 'chunk') {
            currentStreamContent.value += chunk.content
            if (chunk.urgency) currentUrgency.value = chunk.urgency as UrgencyLevel
            if (chunk.pathway) currentPathway.value = chunk.pathway

            // Update the placeholder message in place
            const msgIdx = messages.value.findIndex((m) => m.id === assistantId)
            if (msgIdx !== -1) {
              messages.value[msgIdx] = {
                ...messages.value[msgIdx]!,
                content: currentStreamContent.value,
                urgency: currentUrgency.value,
                pathway: currentPathway.value,
              }
            }
          } else if (chunk.type === 'done') {
            if (chunk.urgency) currentUrgency.value = chunk.urgency as UrgencyLevel
            if (chunk.pathway) currentPathway.value = chunk.pathway
            // Finalize assistant message
            const msgIdx = messages.value.findIndex((m) => m.id === assistantId)
            if (msgIdx !== -1) {
              messages.value[msgIdx] = {
                ...messages.value[msgIdx]!,
                content: currentStreamContent.value,
                urgency: currentUrgency.value,
                pathway: currentPathway.value,
              }
            }
          } else if (chunk.type === 'error') {
            const msgIdx = messages.value.findIndex((m) => m.id === assistantId)
            if (msgIdx !== -1) {
              messages.value[msgIdx] = {
                ...messages.value[msgIdx]!,
                content: chunk.content || 'An error occurred. Please try again.',
              }
            }
          }
        }
      }
    } catch (err) {
      const msgIdx = messages.value.findIndex((m) => m.id === assistantId)
      if (msgIdx !== -1) {
        messages.value[msgIdx] = {
          ...messages.value[msgIdx]!,
          content: 'Connection error. Please check your network and try again.',
        }
      }
      console.error('Chat stream error:', err)
    } finally {
      streaming.value = false
      currentStreamContent.value = ''
      await fetchUsage()
    }
  }

  async function fetchUsage(): Promise<void> {
    const token = authStore.token
    if (!token) return
    try {
      const data = await $fetch<{ prompts_remaining: number; prompts_limit: number }>(
        `${apiBase}/api/v1/usage`,
        { headers: { Authorization: `Bearer ${token}` } },
      )
      promptsRemaining.value = data.prompts_remaining
      promptsLimit.value = data.prompts_limit
    } catch {
      // Non-fatal — usage counter stays hidden until first send
    }
  }

  function clearMessages(): void {
    messages.value = []
    sessionId.value = undefined
  }

  return {
    messages: readonly(messages),
    streaming: readonly(streaming),
    currentUrgency: readonly(currentUrgency),
    promptsRemaining: readonly(promptsRemaining),
    promptsLimit: readonly(promptsLimit),
    sendMessage,
    fetchUsage,
    clearMessages,
  }
})
