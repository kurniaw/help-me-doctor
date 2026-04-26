<template>
  <Card class="auth-card">
    <template #title>
      <div class="card-title">Sign In</div>
    </template>
    <template #content>
      <form class="auth-form" @submit.prevent="handleSubmit">
        <div class="field">
          <label for="email">Email</label>
          <InputText
            id="email"
            v-model="form.email"
            type="email"
            placeholder="Enter your email"
            :disabled="loading"
            :invalid="!!errors.email"
            fluid
          />
          <Message v-if="errors.email" severity="error" size="small">{{ errors.email }}</Message>
        </div>

        <div class="field">
          <label for="password">Password</label>
          <Password
            id="password"
            v-model="form.password"
            placeholder="Enter your password"
            :disabled="loading"
            :feedback="false"
            toggle-mask
            fluid
          />
          <Message v-if="errors.password" severity="error" size="small">{{
            errors.password
          }}</Message>
        </div>

        <Message v-if="serverError" severity="error">{{ serverError }}</Message>

        <Button
          type="submit"
          label="Sign In"
          icon="pi pi-sign-in"
          :loading="loading"
          :disabled="loading"
          fluid
          class="submit-btn"
        />

        <div class="form-footer">
          Don't have an account?
          <NuxtLink to="/register">Create one</NuxtLink>
        </div>
      </form>
    </template>
  </Card>
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
    serverError.value =
      err instanceof Error ? err.message : 'Invalid email or password'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-card {
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.card-title {
  font-size: 1.375rem;
  font-weight: 700;
  text-align: center;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.field label {
  font-size: 0.875rem;
  font-weight: 500;
}

.submit-btn {
  margin-top: 0.5rem;
}

.form-footer {
  text-align: center;
  font-size: 0.875rem;
  color: var(--hmd-text-muted);
}

.form-footer a {
  color: #667eea;
  font-weight: 500;
  text-decoration: none;
}
</style>
