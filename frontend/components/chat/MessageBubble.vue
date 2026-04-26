<template>
  <div class="message-row" :class="{ 'is-user': message.role === 'user' }">
    <!-- AI avatar -->
    <div v-if="message.role === 'assistant'" class="avatar ai-avatar">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
      </svg>
    </div>

    <div class="bubble-wrapper">
      <!-- Urgency alert header (CRITICAL / HIGH only) -->
      <div
        v-if="message.role === 'assistant' && message.urgency && message.urgency !== 'MEDIUM'"
        class="urgency-alert"
        :class="`urgency-alert-${message.urgency.toLowerCase()}`"
      >
        <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
        {{ urgencyLabel }}
      </div>

      <!-- Meta row (badge + pathway) -->
      <div v-if="message.role === 'assistant' && (message.urgency || message.pathway)" class="meta-row">
        <ChatUrgencyBadge v-if="message.urgency" :urgency="message.urgency" />
        <span v-if="message.pathway" class="pathway-tag">{{ message.pathway }}</span>
      </div>

      <!-- Bubble -->
      <div
        class="bubble"
        :class="{
          'bubble-user': message.role === 'user',
          'bubble-assistant': message.role === 'assistant',
          [`bubble-${message.urgency?.toLowerCase()}`]: message.role === 'assistant' && message.urgency,
        }"
      >
        <!-- Assistant: rendered markdown -->
        <div
          v-if="message.role === 'assistant'"
          class="message-content"
          v-html="renderedContent"
        />
        <!-- User: plain text -->
        <div v-else class="user-text">{{ message.content }}</div>
      </div>

      <!-- Timestamp -->
      <time class="timestamp">{{ formattedTime }}</time>
    </div>

    <!-- User avatar -->
    <div v-if="message.role === 'user'" class="avatar user-avatar">
      {{ userInitials }}
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Message } from '~/types/chat'

const props = defineProps<{ message: Message }>()

const authStore = useAuthStore()

const userInitials = computed(() => {
  const name = authStore.user?.name ?? 'U'
  return name.split(' ').slice(0, 2).map((n) => n[0]?.toUpperCase() ?? '').join('')
})

const urgencyLabel = computed(() => {
  switch (props.message.urgency) {
    case 'CRITICAL': return 'Critical — Seek emergency care immediately'
    case 'HIGH':     return 'High urgency — Visit a hospital or specialist soon'
    default:         return ''
  }
})

function simpleMarkdown(text: string): string {
  let content = text.replace(/^URGENCY:\w+\n+/, '')

  // Escape HTML
  content = content.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

  // Headers
  content = content.replace(/^### (.+)$/gm, '<h3>$1</h3>')
  content = content.replace(/^## (.+)$/gm, '<h2>$1</h2>')
  content = content.replace(/^# (.+)$/gm, '<h1>$1</h1>')

  // Bold + italic
  content = content.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
  content = content.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  content = content.replace(/\*(.+?)\*/g, '<em>$1</em>')

  // Ordered lists
  content = content.replace(/^\d+\. (.+)$/gm, '<li>$1</li>')

  // Unordered lists — group consecutive <li> lines into <ul> blocks
  content = content.replace(/^- (.+)$/gm, '<li>$1</li>')
  content = content.replace(/(<li>[^]*?<\/li>)(\n<li>[^]*?<\/li>)*/g, (match) => `<ul>${match}</ul>`)

  // Paragraph wrapping
  const blocks = content.split(/\n{2,}/).map((p) => {
    const t = p.trim()
    if (!t) return ''
    if (/^<(h[123]|ul|ol|li)/.test(t)) return t
    return `<p>${t.replace(/\n/g, '<br>')}</p>`
  }).filter(Boolean)

  return blocks.join('\n')
}

const renderedContent = computed(() => simpleMarkdown(props.message.content))

const formattedTime = computed(() =>
  new Intl.DateTimeFormat('en-SG', { hour: '2-digit', minute: '2-digit' }).format(props.message.timestamp)
)
</script>

<style scoped>
.message-row {
  display: flex;
  align-items: flex-start;
  gap: 0.625rem;
}

.message-row.is-user {
  flex-direction: row-reverse;
}

/* ── Avatars ── */
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;
}

.ai-avatar {
  background: var(--hmd-primary);
  color: white;
}

.user-avatar {
  background: var(--hmd-primary-light);
  color: var(--hmd-primary-dark);
  font-size: 0.625rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

/* ── Bubble wrapper ── */
.bubble-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  max-width: 78%;
}

/* ── Urgency alert header ── */
.urgency-alert {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.375rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.01em;
}

.urgency-alert-critical {
  background: var(--hmd-critical-bg);
  border: 1px solid var(--hmd-critical-border);
  color: var(--hmd-critical-text);
}

.urgency-alert-high {
  background: var(--hmd-high-bg);
  border: 1px solid var(--hmd-high-border);
  color: var(--hmd-high-text);
}

/* ── Meta row ── */
.meta-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0 0.25rem;
}

.pathway-tag {
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--hmd-text-subtle);
  background: var(--hmd-border);
  padding: 0.125rem 0.4rem;
  border-radius: 4px;
}

/* ── Bubble ── */
.bubble {
  border-radius: var(--radius-lg);
  line-height: 1.65;
  font-size: 0.9375rem;
  word-break: break-word;
}

.bubble-user {
  background: var(--hmd-primary);
  color: white;
  padding: 0.625rem 1rem;
  border-bottom-right-radius: 4px;
}

.bubble-assistant {
  background: var(--hmd-surface);
  border: 1px solid var(--hmd-border);
  padding: 0.875rem 1rem;
  border-bottom-left-radius: 4px;
  box-shadow: var(--shadow-xs);
}

/* Urgency left border on assistant bubble */
.bubble-critical { border-left: 3px solid var(--hmd-critical); }
.bubble-high     { border-left: 3px solid var(--hmd-high); }
.bubble-medium   { border-left: 3px solid var(--hmd-medium); }

/* ── Text ── */
.user-text {
  white-space: pre-wrap;
  word-break: break-word;
  padding: 0.625rem 1rem;
}

/* ── Timestamp ── */
.timestamp {
  font-size: 0.6875rem;
  color: var(--hmd-text-subtle);
  padding: 0 0.25rem;
}

.message-row.is-user .timestamp {
  text-align: right;
}

@media (max-width: 480px) {
  .bubble-wrapper { max-width: 88%; }
}
</style>
