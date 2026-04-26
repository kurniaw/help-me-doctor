<template>
  <div class="chat-window">
    <!-- Messages area -->
    <div ref="scrollContainer" class="messages-area">
      <div class="chat-container">
        <!-- Empty state -->
        <div v-if="chatStore.messages.length === 0" class="empty-state">
          <div class="empty-icon">🏥</div>
          <h2 class="empty-title">How can I help you today?</h2>
          <p class="empty-sub">
            Describe your symptoms, medical condition, or legal situation. I'll connect you with
            the right healthcare providers in Singapore.
          </p>
          <div class="example-prompts">
            <button
              v-for="prompt in examplePrompts"
              :key="prompt"
              class="prompt-chip"
              :disabled="chatStore.streaming"
              @click="chatStore.sendMessage(prompt)"
            >
              {{ prompt }}
            </button>
          </div>
        </div>

        <!-- Message list -->
        <div v-else class="messages-list">
          <ChatMessageBubble
            v-for="message in chatStore.messages"
            :key="message.id"
            :message="message"
          />
          <ChatTypingIndicator v-if="chatStore.streaming" />
        </div>
      </div>
    </div>

    <!-- Input -->
    <ChatChatInput :streaming="chatStore.streaming" @send="chatStore.sendMessage" />
  </div>
</template>

<script setup lang="ts">
const chatStore = useChatStore()
const scrollContainer = ref<HTMLElement | null>(null)

const examplePrompts = [
  'I have chest pain and difficulty breathing',
  'I was assaulted and need help',
  'My child has a high fever for 3 days',
  'I fell at work and injured my back',
]

// Auto-scroll to bottom when messages change
watch(
  () => chatStore.messages.length,
  async () => {
    await nextTick()
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
    }
  },
)

// Also scroll during streaming
watch(
  () => chatStore.streaming,
  async () => {
    await nextTick()
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
    }
  },
)
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 1rem;
  scroll-behavior: smooth;
}

.chat-container {
  max-width: 900px;
  margin: 0 auto;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 3rem 1rem;
  min-height: 50vh;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--hmd-text);
  margin: 0 0 0.5rem;
}

.empty-sub {
  color: var(--hmd-text-muted);
  font-size: 0.9375rem;
  max-width: 480px;
  line-height: 1.6;
  margin: 0 0 2rem;
}

.example-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  max-width: 560px;
}

.prompt-chip {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  color: var(--hmd-text);
  cursor: pointer;
  transition: all 0.15s;
}

.prompt-chip:hover:not(:disabled) {
  border-color: #667eea;
  color: #667eea;
  background: #f0f0ff;
}

.prompt-chip:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-bottom: 1rem;
}
</style>
