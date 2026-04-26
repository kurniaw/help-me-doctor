<template>
  <div class="auth-shell">
    <div class="auth-header">
      <span class="brand-icon">🏥</span>
      <h1 class="brand-name">HelpMeDoctor</h1>
      <p class="brand-sub">Singapore Medical & Legal Triage Assistant</p>
    </div>
    <div class="auth-card-wrapper">
      <slot />
    </div>
    <Toast position="top-right" />
  </div>
</template>

<style scoped>
.auth-shell {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.auth-header {
  text-align: center;
  color: white;
  margin-bottom: 1.5rem;
}

.brand-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 0.5rem;
}

.brand-name {
  font-size: 1.875rem;
  font-weight: 700;
  margin: 0 0 0.25rem;
}

.brand-sub {
  font-size: 0.875rem;
  opacity: 0.85;
  margin: 0;
}

.auth-card-wrapper {
  width: 100%;
  max-width: 420px;
}
</style>
