<template>
  <component
    :is="asButton ? 'button' : 'div'"
    :type="asButton ? 'button' : undefined"
    class="countdown"
    :class="{ 'countdown--ended': remainingMs <= 0 }"
  >
    <span v-if="showLabel" class="countdown__label">{{ remainingMs > 0 ? label : finishedLabel }}</span>
    <strong>{{ formatted }}</strong>
  </component>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = withDefaults(defineProps<{
  targetAt: string
  label: string
  finishedLabel: string
  asButton?: boolean
  showLabel?: boolean
}>(), {
  asButton: true,
  showLabel: true
})

const now = ref(Date.now())
let timer: number | undefined

const remainingMs = computed(() => Math.max(0, new Date(props.targetAt).getTime() - now.value))

const formatted = computed(() => {
  if (remainingMs.value <= 0) {
    return '00:00'
  }

  const totalSeconds = Math.ceil(remainingMs.value / 1000)
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60

  if (hours > 0) {
    return `${hours}h ${minutes.toString().padStart(2, '0')}min ${seconds.toString().padStart(2, '0')}s`
  }

  return `${minutes}min ${seconds.toString().padStart(2, '0')}s`
})

onMounted(() => {
  timer = window.setInterval(() => {
    now.value = Date.now()
  }, 1000)
})

onBeforeUnmount(() => {
  if (timer) {
    window.clearInterval(timer)
  }
})
</script>
