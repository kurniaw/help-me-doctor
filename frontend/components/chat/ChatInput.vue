<template>
  <div class="input-bar">
    <div class="input-bar-inner">
      <div class="input-row" :class="{ 'is-streaming': streaming, 'is-limited': limitReached }">
        <Textarea
          ref="textareaRef"
          v-model="inputText"
          :placeholder="limitReached ? 'Daily limit reached. Try again tomorrow.' : streaming ? 'Analysing your situation…' : 'Describe your symptoms or situation…'"
          :disabled="streaming || limitReached"
          rows="1"
          auto-resize
          class="chat-textarea"
          @keydown.enter.exact.prevent="handleSend"
        />
        <button
          class="send-btn"
          :disabled="!inputText.trim() || streaming || limitReached"
          :aria-label="streaming ? 'Sending…' : 'Send message'"
          @click="handleSend"
        >
          <svg v-if="!streaming" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
          <span v-else class="spinner" />
        </button>
      </div>
      <div class="input-footer">
        <p class="input-hint">
          <kbd>Enter</kbd> to send &nbsp;·&nbsp; <kbd>Shift+Enter</kbd> for new line
        </p>
        <p v-if="promptsRemaining !== null" class="usage-hint" :class="{ 'is-warning': promptsRemaining <= 1, 'is-exhausted': limitReached }">
          {{ limitReached ? 'Daily limit reached' : `${promptsRemaining} of ${promptsLimit} prompts left today` }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{ send: [text: string] }>()

const props = defineProps<{
  streaming: boolean
  promptsRemaining: number | null
  promptsLimit: number
}>()

const inputText = ref('')

const limitReached = computed(() => props.promptsRemaining === 0)

function handleSend(): void {
  const text = inputText.value.trim()
  if (!text || props.streaming || limitReached.value) return
  emit('send', text)
  inputText.value = ''
}
</script>

<style scoped>
.input-bar {
  background: var(--hmd-surface);
  border-top: 1px solid var(--hmd-border);
  padding: 0.875rem 1rem 0.75rem;
  box-shadow: 0 -1px 8px rgba(15,23,42,0.04);
}

.input-bar-inner {
  max-width: 780px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

/* Input row */
.input-row {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
  background: var(--hmd-surface-2);
  border: 1.5px solid var(--hmd-border);
  border-radius: var(--radius-lg);
  padding: 0.5rem 0.5rem 0.5rem 1rem;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.input-row:focus-within {
  border-color: var(--hmd-primary);
  box-shadow: 0 0 0 3px rgba(37,99,235,0.1);
  background: var(--hmd-surface);
}

.input-row.is-streaming {
  opacity: 0.7;
}

/* PrimeVue Textarea */
.chat-textarea {
  flex: 1;
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  outline: none;
  padding: 0.25rem 0 !important;
  resize: none;
}

:deep(.chat-textarea) {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  padding: 0.25rem 0 !important;
  font-family: inherit;
  font-size: 0.9375rem;
  color: var(--hmd-text);
  max-height: 140px;
  overflow-y: auto;
  line-height: 1.55;
  resize: none;
}

:deep(.chat-textarea::placeholder) {
  color: var(--hmd-text-subtle);
}

/* Send button */
.send-btn {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: none;
  background: var(--hmd-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s;
  padding: 0;
}

.send-btn:hover:not(:disabled) {
  background: var(--hmd-primary-dark);
}

.send-btn:active:not(:disabled) {
  transform: scale(0.93);
}

.send-btn:disabled {
  background: var(--hmd-border);
  color: var(--hmd-text-subtle);
  cursor: not-allowed;
}

/* Spinner */
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: block;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Footer row */
.input-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

/* Hint */
.input-hint {
  font-size: 0.6875rem;
  color: var(--hmd-text-subtle);
  margin: 0;
}

.input-hint kbd {
  font-family: inherit;
  font-size: 0.6875rem;
  background: var(--hmd-border);
  border-radius: 3px;
  padding: 0.05rem 0.3rem;
  font-weight: 600;
  color: var(--hmd-text-muted);
}

/* Usage pill */
.usage-hint {
  font-size: 0.6875rem;
  color: var(--hmd-text-subtle);
  margin: 0;
  white-space: nowrap;
  font-weight: 500;
}

.usage-hint.is-warning {
  color: #d97706;
}

.usage-hint.is-exhausted {
  color: #dc2626;
}

.input-row.is-limited {
  opacity: 0.6;
}

@media (max-width: 480px) {
  .input-hint { display: none; }
}
</style>
