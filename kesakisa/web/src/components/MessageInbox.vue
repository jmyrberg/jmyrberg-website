<template>
  <section class="section-block inbox-panel" aria-label="Viestit">
    <div class="inbox-card">
      <header class="inbox-card__header">
        <h2>Viestit</h2>
        <span>{{ messages.length }} kpl</span>
      </header>

      <div v-if="messages.length" class="inbox-list">
        <article v-for="message in sortedMessages" :key="message.id" class="inbox-message">
          <small>{{ formatDate(message.createdAt) }}</small>
          <p>{{ message.text }}</p>
        </article>
      </div>

      <p v-else class="inbox-empty">
        Ei viestejä.
      </p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { UserMessage } from '../types'
import { formatShortDateTime as formatDate } from '../utils/dateFormat'

const props = defineProps<{
  messages: UserMessage[]
}>()

const sortedMessages = computed(() => {
  return [...props.messages].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
})
</script>
