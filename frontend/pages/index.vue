<template>
  <div />
</template>

<script setup lang="ts">
const authStore = useAuthStore()
await navigateTo(authStore.isAuthenticated ? '/chat' : '/login')
</script>
