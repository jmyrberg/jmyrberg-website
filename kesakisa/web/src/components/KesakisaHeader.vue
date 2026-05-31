<template>
  <header class="hero">
    <div class="hero__banner-wrap">
      <img class="hero__banner" :src="banner" alt="" aria-hidden="true" />
      <h1 class="sr-only">Kesäkisa 2026</h1>
      <svg class="hero__title-svg" viewBox="0 0 402.92 126.17" aria-hidden="true">
        <defs>
          <path id="kesakisa-title-curve" d="M 85 64 C 142 47, 260 47, 318 64" />
        </defs>
        <text>
          <textPath href="#kesakisa-title-curve" startOffset="50%" text-anchor="middle">
            Kesäkisa 2026
          </textPath>
        </text>
      </svg>
    </div>
    <div
      v-if="playerLabel"
      class="hero__player-label"
      :style="{ '--player-accent': playerAccent ?? 'rgba(255, 253, 247, .94)' }"
    >
      {{ playerLabel }}
    </div>
    <div
      v-if="showCountdown && freeTime"
      class="countdown countdown--free-time"
      role="status"
      aria-label="Vapaa-aika"
    >
      <strong>
        <span>Vapaa-aika</span>
        <span class="free-time-emojis">🎉 🎣 🥏 🏊</span>
      </strong>
    </div>
    <CountdownTimer
      v-else-if="showCountdown"
      :target-at="targetAt"
      :label="countdownLabel"
      :finished-label="finishedLabel"
      :show-label="showCountdownLabel"
      aria-label="Avaa päivätehtävä"
      @click="emit('openTask')"
    />
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import banner from '../assets/banner.svg'
import CountdownTimer from './CountdownTimer.vue'
import type { DailyTask, TaskStatus } from '../types'

const props = withDefaults(defineProps<{
  task: DailyTask
  status: TaskStatus
  playerLabel?: string
  playerAccent?: string
  freeTime?: boolean
  showCountdown?: boolean
  showCountdownLabel?: boolean
}>(), {
  freeTime: false,
  showCountdown: true,
  showCountdownLabel: true
})

const emit = defineEmits<{
  openTask: []
}>()

const targetAt = computed(() => props.status === 'upcoming' ? props.task.startsAt : props.task.endsAt)
const countdownLabel = computed(() => props.status === 'upcoming' ? 'Päivätehtävä alkaa' : 'Päivätehtävä käynnissä')
const finishedLabel = computed(() => props.status === 'upcoming' ? 'Tehtävä alkaa nyt' : 'Päivätehtävä päättyi')
</script>
