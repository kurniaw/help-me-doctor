<template>
  <div class="app-shell">
    <header class="app-header">
      <div class="header-inner">
        <!-- Brand -->
        <NuxtLink to="/chat" class="brand">
          <div class="brand-mark">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          </div>
          <span class="brand-name">Help Me Doctor</span>
          <span class="brand-divider" />
          <span class="brand-sub">Singapore</span>
        </NuxtLink>

        <!-- Right: user + logout -->
        <div class="header-right">
          <div v-if="authStore.user" class="user-info">
            <div class="user-avatar">{{ initials }}</div>
            <span class="user-name">{{ authStore.user.name }}</span>
          </div>
          <button
            v-if="authStore.isAuthenticated"
            class="logout-btn"
            @click="authStore.logout()"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            <span>Sign out</span>
          </button>
        </div>
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

const initials = computed(() => {
  const name = authStore.user?.name ?? ''
  return name
    .split(' ')
    .slice(0, 2)
    .map((n) => n[0]?.toUpperCase() ?? '')
    .join('')
})
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--hmd-bg);
}

/* ── Header ── */
.app-header {
  background: var(--hmd-surface);
  border-bottom: 1px solid var(--hmd-border);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow-sm);
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 62px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

/* Brand */
.brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: inherit;
}

.brand-mark {
  width: 32px;
  height: 32px;
  background: var(--hmd-primary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.brand-name {
  font-size: 1rem;
  font-weight: 700;
  color: var(--hmd-text);
  letter-spacing: -0.02em;
}

.brand-divider {
  width: 1px;
  height: 14px;
  background: var(--hmd-border);
  display: none;
}

.brand-sub {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--hmd-text-muted);
  display: none;
}

@media (min-width: 520px) {
  .brand-divider,
  .brand-sub { display: block; }
}

/* Right section */
.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--hmd-primary-light);
  color: var(--hmd-primary-dark);
  font-size: 0.6875rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  letter-spacing: 0.02em;
  flex-shrink: 0;
}

.user-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--hmd-text);
  display: none;
}

@media (min-width: 640px) {
  .user-name { display: block; }
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  border: 1px solid var(--hmd-border);
  background: transparent;
  border-radius: 7px;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--hmd-text-muted);
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}

.logout-btn:hover {
  background: var(--hmd-bg);
  color: var(--hmd-text);
  border-color: #cbd5e1;
}

.logout-btn span { display: none; }

@media (min-width: 480px) {
  .logout-btn span { display: block; }
}

/* ── Main ── */
.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
