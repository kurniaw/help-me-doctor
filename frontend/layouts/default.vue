<template>
  <div class="app-shell">
    <header class="app-header">
      <div class="header-inner">
        <div class="brand">
          <span class="brand-icon">🏥</span>
          <span class="brand-name">HelpMeDoctor</span>
          <span class="brand-sub">Singapore Medical Triage</span>
        </div>
        <nav class="header-nav">
          <Button
            v-if="authStore.isAuthenticated"
            label="Logout"
            icon="pi pi-sign-out"
            severity="secondary"
            text
            size="small"
            @click="authStore.logout()"
          />
        </nav>
      </div>
    </header>

    <main class="app-main">
      <slot />
    </main>

    <Toast position="top-right" />
  </div>
</template>

<script setup lang="ts">
const authStore = useAuthStore()
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--hmd-bg);
}

.app-header {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.brand-icon {
  font-size: 1.5rem;
}

.brand-name {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--hmd-text);
}

.brand-sub {
  font-size: 0.75rem;
  color: var(--hmd-text-muted);
  display: none;
}

@media (min-width: 640px) {
  .brand-sub {
    display: inline;
  }
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
