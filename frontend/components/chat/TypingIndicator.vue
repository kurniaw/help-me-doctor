<template>
  <div class="typing-indicator">
    <div class="avatar">🤖</div>
    <div class="dots-container">
      <span class="dot" />
      <span class="dot" />
      <span class="dot" />
    </div>
  </div>
</template>

<style scoped>
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
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
}

.dots-container {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 0.625rem 1rem;
  display: flex;
  gap: 0.375rem;
  align-items: center;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #94a3b8;
  animation: bounce 1.2s infinite;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%,
  60%,
  100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-6px);
  }
}
</style>
