<template>
  <div class="typing-row">
    <div class="ai-avatar">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
      </svg>
    </div>
    <div class="typing-bubble">
      <span class="dot" />
      <span class="dot" />
      <span class="dot" />
      <span class="typing-label">Analysing your situation…</span>
    </div>
  </div>
</template>

<style scoped>
.typing-row {
  display: flex;
  align-items: flex-end;
  gap: 0.625rem;
}

.ai-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--hmd-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.typing-bubble {
  background: var(--hmd-surface);
  border: 1px solid var(--hmd-border);
  border-radius: var(--radius-lg);
  border-bottom-left-radius: 4px;
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  box-shadow: var(--shadow-xs);
}

.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--hmd-primary-light);
  border: 1.5px solid var(--hmd-primary);
  animation: pulse 1.4s ease-in-out infinite;
}

.dot:nth-child(2) { animation-delay: 0.18s; }
.dot:nth-child(3) { animation-delay: 0.36s; }

.typing-label {
  font-size: 0.8125rem;
  color: var(--hmd-text-muted);
  font-weight: 500;
  margin-left: 0.375rem;
  font-style: italic;
}

@keyframes pulse {
  0%, 60%, 100% { transform: scale(1);    opacity: 0.5; }
  30%            { transform: scale(1.35); opacity: 1;   }
}
</style>
