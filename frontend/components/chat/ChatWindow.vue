<template>
  <div class="chat-window">
    <!-- Messages area -->
    <div ref="scrollContainer" class="messages-area">
      <div class="messages-container">

        <!-- Empty / welcome state -->
        <div v-if="chatStore.messages.length === 0" class="empty-state">
          <div class="welcome-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          </div>
          <h2 class="welcome-title">{{ greeting }}, {{ firstName }}</h2>
          <p class="welcome-sub">
            Describe your symptoms, medical condition, or legal-medical situation.<br>
            Our AI will route you to the right Singapore healthcare provider.
          </p>

          <!-- Category cards -->
          <div class="category-grid">
            <button
              v-for="cat in categories"
              :key="cat.label"
              class="category-card"
              :disabled="chatStore.streaming || limitReached"
              @click="chatStore.sendMessage(cat.prompt)"
            >
              <span class="category-icon">{{ cat.icon }}</span>
              <span class="category-label">{{ cat.label }}</span>
              <span class="category-desc">{{ cat.desc }}</span>
            </button>
          </div>

          <!-- Suggested prompts -->
          <p class="prompts-label">Or try one of these</p>
          <div class="prompt-chips">
            <button
              v-for="prompt in examplePrompts"
              :key="prompt"
              class="prompt-chip"
              :disabled="chatStore.streaming || limitReached"
              @click="chatStore.sendMessage(prompt)"
            >
              {{ prompt }}
            </button>
          </div>
        </div>

        <!-- Message list -->
        <template v-else>
          <ChatMessageBubble
            v-for="message in chatStore.messages"
            :key="message.id"
            :message="message"
          />
          <ChatTypingIndicator v-if="chatStore.streaming" />
        </template>
      </div>
    </div>
    
    <!-- Input bar -->
    <ChatInput
      :streaming="chatStore.streaming"
      :prompts-remaining="chatStore.promptsRemaining"
      :prompts-limit="chatStore.promptsLimit"
      @send="chatStore.sendMessage"
    />
  </div>
</template>

<script setup lang="ts">
const chatStore = useChatStore()
const authStore = useAuthStore()
const scrollContainer = ref<HTMLElement | null>(null)
const limitReached = computed(() => chatStore.promptsRemaining === 0)

const firstName = computed(() => {
  const name = authStore.user?.name ?? 'there'
  return name.split(' ')[0] ?? name
})

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 18) return 'Good afternoon'
  return 'Good evening'
})

const categories = [
  { icon: '🩺', label: 'Symptoms', desc: 'Describe what you feel', prompt: 'I have chest pain and difficulty breathing' },
  { icon: '🚨', label: 'Emergency', desc: 'Urgent medical help', prompt: 'I need emergency medical assistance' },
  { icon: '⚖️', label: 'Legal-Medical', desc: 'Assault, workplace injury', prompt: 'I was assaulted and need medical and legal help' },
  { icon: '🏢', label: 'Workplace', desc: 'Work injury or illness', prompt: 'I fell at work and injured my back' },
]

const examplePrompts = [
  'My child has a high fever for 3 days',
  'I need a routine medical checkup',
  'I have a mild headache and dizziness',
]

function scrollToBottom(): void {
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
  }
}

watch(() => chatStore.messages.length, async () => { await nextTick(); scrollToBottom() })
watch(() => chatStore.streaming, async () => { await nextTick(); scrollToBottom() })
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: var(--hmd-bg);
}

/* ── Messages area ── */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 1rem 0.5rem;
}

.messages-container {
  max-width: 780px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-bottom: 1rem;
}

/* ── Empty / welcome state ── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 2.5rem 1rem 1rem;
}

.welcome-icon {
  width: 60px;
  height: 60px;
  background: var(--hmd-primary);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 1.25rem;
  box-shadow: 0 8px 20px rgba(37,99,235,0.3);
}

.welcome-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--hmd-text);
  letter-spacing: -0.025em;
  margin: 0 0 0.625rem;
}

.welcome-sub {
  font-size: 0.9rem;
  color: var(--hmd-text-muted);
  line-height: 1.65;
  max-width: 480px;
  margin: 0 0 2rem;
}

/* Category cards */
.category-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.625rem;
  width: 100%;
  max-width: 540px;
  margin-bottom: 1.75rem;
}

.category-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.25rem;
  padding: 1rem;
  background: var(--hmd-surface);
  border: 1px solid var(--hmd-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.15s;
  text-align: left;
  font-family: inherit;
}

.category-card:hover:not(:disabled) {
  border-color: var(--hmd-primary-light);
  background: var(--hmd-primary-faint);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.category-card:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.category-icon {
  font-size: 1.25rem;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.category-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--hmd-text);
}

.category-desc {
  font-size: 0.75rem;
  color: var(--hmd-text-muted);
  line-height: 1.3;
}

/* Prompt chips */
.prompts-label {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--hmd-text-subtle);
  margin: 0 0 0.75rem;
}

.prompt-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  max-width: 560px;
}

.prompt-chip {
  background: var(--hmd-surface);
  border: 1px solid var(--hmd-border);
  border-radius: 99px;
  padding: 0.4375rem 0.875rem;
  font-size: 0.8125rem;
  color: var(--hmd-text-muted);
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
  font-weight: 500;
}

.prompt-chip:hover:not(:disabled) {
  border-color: var(--hmd-primary);
  color: var(--hmd-primary);
  background: var(--hmd-primary-faint);
}

.prompt-chip:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

@media (min-width: 640px) {
  .category-grid { grid-template-columns: repeat(4, 1fr); }
}
</style>
