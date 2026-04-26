<template>
  <Card class="auth-card">
    <template #title>
      <div class="card-title">Create Account</div>
    </template>
    <template #content>
      <form class="auth-form" @submit.prevent="handleSubmit">
        <div class="field">
          <label for="name">Full Name</label>
          <InputText
            id="name"
            v-model="form.name"
            placeholder="Enter your name"
            :disabled="loading"
            :invalid="!!errors.name"
            fluid
          />
          <Message v-if="errors.name" severity="error" size="small">{{ errors.name }}</Message>
        </div>

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
            placeholder="Min. 8 characters"
            :disabled="loading"
            :invalid="!!errors.password"
            :feedback="true"
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
          label="Create Account"
          icon="pi pi-user-plus"
          :loading="loading"
          :disabled="loading"
          fluid
          class="submit-btn"
        />

        <div class="form-footer">
          Already have an account?
          <NuxtLink to="/login">Sign in</NuxtLink>
        </div>
      </form>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

const authStore = useAuthStore()
const toast = useToast()
const router = useRouter()

const loading = ref(false)
const serverError = ref('')

const form = reactive({
  name: '',
  email: '',
  password: '',
})

const errors = reactive({
  name: '',
  email: '',
  password: '',
})

function validate(): boolean {
  errors.name = ''
  errors.email = ''
  errors.password = ''

  let valid = true
  if (!form.name.trim()) {
    errors.name = 'Name is required'
    valid = false
  }
  if (!form.email.includes('@')) {
    errors.email = 'Enter a valid email address'
    valid = false
  }
  if (form.password.length < 8) {
    errors.password = 'Password must be at least 8 characters'
    valid = false
  }
  return valid
}

async function handleSubmit(): Promise<void> {
  serverError.value = ''
  if (!validate()) return

  loading.value = true
  try {
    await authStore.register(form)
    toast.add({ severity: 'success', summary: 'Welcome!', detail: 'Account created.', life: 3000 })
    await router.push('/chat')
  } catch (err: unknown) {
    const msg =
      err instanceof Error ? err.message : 'Registration failed. Please try again.'
    serverError.value = msg
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
  color: var(--hmd-text);
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
