<template>
  <div class="chat-input-bar">
    <div class="input-wrapper">
      <Textarea
        ref="textareaRef"
        v-model="inputText"
        :placeholder="streaming ? 'Waiting for response…' : 'Describe your symptoms or situation…'"
        :disabled="streaming"
        rows="1"
        auto-resize
        class="chat-textarea"
        @keydown.enter.exact.prevent="handleSend"
      />
      <Button
        icon="pi pi-send"
        :disabled="!inputText.trim() || streaming"
        :loading="streaming"
        class="send-btn"
        rounded
        aria-label="Send message"
        @click="handleSend"
      />
    </div>
    <div class="input-hint">Press Enter to send · Shift+Enter for new line</div>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{
  send: [text: string]
}>()

const props = defineProps<{
  streaming: boolean
}>()

const inputText = ref('')
const textareaRef = ref()

function handleSend(): void {
  const text = inputText.value.trim()
  if (!text || props.streaming) return
  emit('send', text)
  inputText.value = ''
}
</script>

<style scoped>
.chat-input-bar {
  border-top: 1px solid #e2e8f0;
  background: white;
  padding: 0.875rem 1rem 0.625rem;
}

.input-wrapper {
  display: flex;
  gap: 0.625rem;
  align-items: flex-end;
  max-width: 900px;
  margin: 0 auto;
}

.chat-textarea {
  flex: 1;
  resize: none;
  border-radius: 22px;
  font-size: 0.9375rem;
  max-height: 160px;
  overflow-y: auto;
}

.send-btn {
  flex-shrink: 0;
  width: 42px;
  height: 42px;
}

.input-hint {
  max-width: 900px;
  margin: 0.375rem auto 0;
  font-size: 0.6875rem;
  color: var(--hmd-text-muted);
  text-align: center;
}

@media (max-width: 640px) {
  .input-hint {
    display: none;
  }
}
</style>
