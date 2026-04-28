<template>
  <div class="auth-form-wrap">
    <!-- Header -->
    <div class="form-header">
      <div class="form-logo">
        <div class="logo-mark">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
          </svg>
        </div>
      </div>
      <h1 class="form-title">Welcome back</h1>
      <p class="form-subtitle">Sign in to your account</p>
    </div>

    <!-- Form -->
    <form class="auth-form" @submit.prevent="handleSubmit">
      <div class="field">
        <label for="email" class="field-label">Email address</label>
        <InputText
          id="email"
          v-model="form.email"
          type="email"
          :disabled="loading"
          :invalid="!!errors.email"
          fluid
          class="field-input"
        />
        <span v-if="errors.email" class="field-error">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
          {{ errors.email }}
        </span>
      </div>

      <div class="field">
        <label for="password" class="field-label">Password</label>
        <Password
          id="password"
          v-model="form.password"
          :disabled="loading"
          :invalid="!!errors.password"
          :feedback="false"
          toggle-mask
          fluid
          class="field-password"
        />
        <span v-if="errors.password" class="field-error">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
          {{ errors.password }}
        </span>
      </div>

      <div v-if="serverError" class="server-error">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
        {{ serverError }}
      </div>

      <Button
        type="submit"
        label="Sign in"
        :loading="loading"
        :disabled="loading"
        fluid
        class="submit-btn"
      />
    </form>

    <div class="form-footer">
      Don't have an account?
      <NuxtLink to="/register">Create account</NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const authStore = useAuthStore()
const router = useRouter()

const loading = ref(false)
const serverError = ref('')

const form = reactive({ email: '', password: '' })
const errors = reactive({ email: '', password: '' })

function validate(): boolean {
  errors.email = ''
  errors.password = ''
  let valid = true
  if (!form.email.includes('@')) {
    errors.email = 'Enter a valid email address'
    valid = false
  }
  if (!form.password) {
    errors.password = 'Password is required'
    valid = false
  }
  return valid
}

async function handleSubmit(): Promise<void> {
  serverError.value = ''
  if (!validate()) return
  loading.value = true
  try {
    await authStore.login(form)
    await router.push('/chat')
  } catch (err: unknown) {
    serverError.value = err instanceof Error ? err.message : 'Invalid email or password'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-form-wrap {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
  background: var(--hmd-surface);
  border: 1px solid var(--hmd-border);
  border-radius: var(--radius-lg);
  padding: 2rem;
}

/* Header */
.form-header {
  text-align: center;
}

.form-logo {
  display: flex;
  justify-content: center;
  margin-bottom: 1.25rem;
}

.logo-mark {
  width: 60px;
  height: 60px;
  background: var(--hmd-primary);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 8px 20px rgba(37,99,235,0.3);
}

.form-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--hmd-text);
  margin: 0 0 0.375rem;
  letter-spacing: -0.025em;
}

.form-subtitle {
  font-size: 0.9rem;
  color: var(--hmd-text-muted);
  line-height: 1.65;
  margin: 0;
}

/* Form */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.125rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.field-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--hmd-text);
  letter-spacing: 0.01em;
}

/* ── InputText ── */
:deep(.field-input) {
  height: 42px;
  background: var(--hmd-surface-2) !important;
  border: 1.5px solid var(--hmd-border) !important;
  border-radius: var(--radius) !important;
  font-family: inherit !important;
  font-size: 0.9375rem !important;
  color: var(--hmd-text) !important;
  box-shadow: none !important;
  transition: border-color 0.15s, box-shadow 0.15s, background 0.15s !important;
}

:deep(.field-input:enabled:hover) {
  border-color: var(--hmd-primary-light) !important;
  background: var(--hmd-surface-2) !important;
}

:deep(.field-input:enabled:focus) {
  border-color: var(--hmd-primary) !important;
  box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
  background: var(--hmd-surface) !important;
  outline: none !important;
}

:deep(.field-input.p-invalid) {
  border-color: var(--hmd-critical) !important;
}

/* ── Password: style the wrapper as the field, strip the inner input ── */
:deep(.field-password) {
  position: relative;
  width: 100%;
  height: 42px;
  background: var(--hmd-surface-2);
  border: 1.5px solid var(--hmd-border);
  border-radius: var(--radius);
  transition: border-color 0.15s, box-shadow 0.15s, background 0.15s;
}

:deep(.field-password:hover) {
  border-color: var(--hmd-primary-light);
}

:deep(.field-password:focus-within) {
  border-color: var(--hmd-primary);
  box-shadow: 0 0 0 3px rgba(37,99,235,0.1);
  background: var(--hmd-surface);
}

:deep(.field-password.p-invalid) {
  border-color: var(--hmd-critical);
}

:deep(.field-password .p-inputtext) {
  height: 100% !important;
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  outline: none !important;
  font-family: inherit !important;
  font-size: 0.9375rem !important;
  color: var(--hmd-text) !important;
}

:deep(.field-password .p-inputtext:focus) {
  box-shadow: none !important;
  outline: none !important;
}

:deep(.field-password .p-password-toggle-mask-icon) {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--hmd-text-muted);
  cursor: pointer;
}

.field-error {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.8rem;
  color: var(--hmd-critical);
  font-weight: 500;
}

.server-error {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: var(--hmd-critical-bg);
  border: 1px solid var(--hmd-critical-border);
  border-radius: var(--radius-lg);
  color: var(--hmd-critical-text);
  font-size: 0.875rem;
  font-weight: 500;
}

/* ── Button ── */
:deep(.submit-btn) {
  margin-top: 0.25rem;
  height: 42px;
  background: var(--hmd-primary) !important;
  border-color: var(--hmd-primary) !important;
  border-radius: var(--radius) !important;
  font-family: inherit !important;
  font-size: 0.9375rem !important;
  font-weight: 600 !important;
  color: white !important;
  transition: background 0.15s, transform 0.1s, box-shadow 0.15s !important;
}

:deep(.submit-btn:not(:disabled):hover) {
  background: var(--hmd-primary-dark) !important;
  border-color: var(--hmd-primary-dark) !important;
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

:deep(.submit-btn:not(:disabled):active) {
  transform: scale(0.99);
}

:deep(.submit-btn:disabled) {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Footer */
.form-footer {
  text-align: center;
  font-size: 0.875rem;
  color: var(--hmd-text-muted);
  padding-top: 0.25rem;
  border-top: 1px solid var(--hmd-border);
}

.form-footer a {
  color: var(--hmd-primary);
  font-weight: 600;
  text-decoration: none;
  margin-left: 0.25rem;
  transition: all 0.15s;
}

.form-footer a:hover {
  color: var(--hmd-primary-dark);
  text-decoration: underline;
}
</style>
