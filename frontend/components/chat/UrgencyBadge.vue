<template>
  <Badge
    v-if="urgency"
    :value="urgency"
    :severity="badgeSeverity"
    class="urgency-badge"
  />
</template>

<script setup lang="ts">
import type { UrgencyLevel } from '~/types/chat'

const props = defineProps<{
  urgency?: UrgencyLevel
}>()

const badgeSeverity = computed(() => {
  switch (props.urgency) {
    case 'CRITICAL':
      return 'danger'
    case 'HIGH':
      return 'warn'
    case 'MEDIUM':
      return 'info'
    default:
      return 'secondary'
  }
})
</script>

<style scoped>
.urgency-badge {
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}
</style>
