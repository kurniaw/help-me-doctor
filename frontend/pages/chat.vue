<template>
  <div class="chat-page">
    <ChatWindow />
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  ssr: false,
  middleware: 'auth',
})

const chatStore = useChatStore()
onMounted(() => { chatStore.fetchUsage() })
</script>

<style scoped>
.chat-page {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  overflow: hidden;
}
</style>
