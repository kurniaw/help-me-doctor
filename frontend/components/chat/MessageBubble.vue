<template>
  <div class="message-row" :class="{ 'is-user': message.role === 'user' }">
    <!-- Avatar -->
    <div v-if="message.role === 'assistant'" class="avatar">🤖</div>

    <div class="bubble-wrapper">
      <!-- Urgency badge (assistant only) -->
      <div v-if="message.role === 'assistant' && message.urgency" class="badge-row">
        <ChatUrgencyBadge :urgency="message.urgency" />
        <span v-if="message.pathway" class="pathway-label">{{ message.pathway }}</span>
      </div>

      <!-- Message bubble -->
      <div
        class="bubble"
        :class="{
          'bubble-user': message.role === 'user',
          'bubble-assistant': message.role === 'assistant',
          [`urgency-border-${message.urgency?.toLowerCase()}`]: message.role === 'assistant' && message.urgency,
        }"
      >
        <div
          v-if="message.role === 'assistant'"
          class="message-content"
          v-html="renderedContent"
        />
        <div v-else class="message-content user-text">{{ message.content }}</div>
      </div>

      <!-- Timestamp -->
      <div class="timestamp">{{ formattedTime }}</div>
    </div>

    <!-- User avatar -->
    <div v-if="message.role === 'user'" class="avatar user-avatar">👤</div>
  </div>
</template>

<script setup lang="ts">
import type { Message } from '~/types/chat'

const props = defineProps<{
  message: Message
}>()

// Simple markdown-to-HTML renderer (no external dependency)
function simpleMarkdown(text: string): string {
  // Strip URGENCY: prefix if present
  let content = text.replace(/^URGENCY:\w+\n+/, '')

  // Escape HTML
  content = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // Headers
  content = content.replace(/^### (.+)$/gm, '<h3>$1</h3>')
  content = content.replace(/^## (.+)$/gm, '<h2>$1</h2>')
  content = content.replace(/^# (.+)$/gm, '<h1>$1</h1>')

  // Bold + italic
  content = content.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
  content = content.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  content = content.replace(/\*(.+?)\*/g, '<em>$1</em>')

  // Unordered lists
  content = content.replace(/^\- (.+)$/gm, '<li>$1</li>')
  content = content.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')

  // Line breaks → paragraphs
  const paragraphs = content
    .split(/\n{2,}/)
    .map((p) => {
      const trimmed = p.trim()
      if (!trimmed) return ''
      if (trimmed.startsWith('<h') || trimmed.startsWith('<ul') || trimmed.startsWith('<li')) {
        return trimmed
      }
      return `<p>${trimmed.replace(/\n/g, '<br>')}</p>`
    })
    .filter(Boolean)

  return paragraphs.join('\n')
}

const renderedContent = computed(() => simpleMarkdown(props.message.content))

const formattedTime = computed(() => {
  return new Intl.DateTimeFormat('en-SG', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(props.message.timestamp)
})
</script>

<style scoped>
.message-row {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.25rem 0;
}

.message-row.is-user {
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
  flex-shrink: 0;
  margin-top: 4px;
}

.user-avatar {
  background: #e0e7ff;
}

.bubble-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  max-width: 80%;
}

.badge-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pathway-label {
  font-size: 0.6875rem;
  color: var(--hmd-text-muted);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.bubble {
  padding: 0.75rem 1rem;
  border-radius: 16px;
  line-height: 1.6;
  font-size: 0.9375rem;
}

.bubble-user {
  background: #667eea;
  color: white;
  border-bottom-right-radius: 4px;
}

.bubble-assistant {
  background: white;
  border: 1px solid #e2e8f0;
  border-bottom-left-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.urgency-border-critical {
  border-left: 4px solid var(--hmd-critical);
}

.urgency-border-high {
  border-left: 4px solid var(--hmd-high);
}

.urgency-border-medium {
  border-left: 4px solid var(--hmd-medium);
}

.user-text {
  white-space: pre-wrap;
  word-break: break-word;
}

.timestamp {
  font-size: 0.6875rem;
  color: var(--hmd-text-muted);
  padding: 0 0.25rem;
}

.message-row.is-user .timestamp {
  text-align: right;
}
</style>
