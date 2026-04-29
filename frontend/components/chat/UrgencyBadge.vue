<template>
  <span v-if="urgency" class="urgency-pill" :class="`urgency-pill-${urgency.toLowerCase()}`">
    <span class="urgency-dot" />
    {{ urgency }}
  </span>
</template>

<script setup lang="ts">
import type { UrgencyLevel } from '~/types/chat'

defineProps<{ urgency?: UrgencyLevel }>()
</script>

<style scoped>
.urgency-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.1875rem 0.5rem;
  border-radius: 99px;
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  white-space: nowrap;
}

.urgency-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
  flex-shrink: 0;
}

.urgency-pill-critical {
  background: var(--hmd-critical-bg);
  color: var(--hmd-critical);
  border: 1px solid var(--hmd-critical-border);
}

.urgency-pill-high {
  background: var(--hmd-high-bg);
  color: var(--hmd-high);
  border: 1px solid var(--hmd-high-border);
}

.urgency-pill-medium {
  background: var(--hmd-medium-bg);
  color: var(--hmd-medium);
  border: 1px solid var(--hmd-medium-border);
}

.urgency-pill-low {
  background: var(--hmd-low-bg);
  color: var(--hmd-low);
  border: 1px solid var(--hmd-low-border);
}
</style>
