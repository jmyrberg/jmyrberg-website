<template>
  <section class="section-block task-panel" aria-label="Päivätehtävä">
    <section class="task-panel__section" aria-label="Tehtävän aika ja paikka">
      <div class="task-panel__meta">
        <strong class="task-panel__box-title">{{ taskMetaHeading }}</strong>
        <div>
          <small>Paikka</small>
          <strong>{{ task.location }}</strong>
        </div>
        <div>
          <small>Aika</small>
          <strong>{{ formatTime(task.startsAt) }} - {{ formatTime(task.endsAt) }}</strong>
        </div>
        <div v-if="status !== 'ended'" class="task-panel__time-left">
          <small>{{ timeLeftLabel }}</small>
          <CountdownTimer
            class="task-panel__countdown"
            :target-at="targetAt"
            :label="countdownLabel"
            :finished-label="finishedLabel"
            :as-button="false"
            :show-label="false"
          />
        </div>
      </div>
    </section>

    <section v-if="status !== 'live'" class="task-panel__section" aria-label="Valmistautuminen">
      <div class="task-panel__prep">
        <strong class="task-panel__box-title">Valmistautuminen</strong>
        <span>{{ task.preparationText }}</span>
      </div>
    </section>

    <section class="task-panel__section" aria-label="Tehtävän ohje">
      <transition name="expand" mode="out-in">
        <div v-if="status === 'upcoming'" key="locked" class="task-lock">
          <strong class="task-panel__box-title">Tehtävän ohje</strong>
          <strong>Ohjeet ovat vielä lukossa.</strong>
          <span>Ne avautuvat automaattisesti, kun päivätehtävä alkaa.</span>
        </div>
        <div v-else-if="status === 'live'" key="live" class="task-instructions">
          <strong class="task-panel__box-title">Tehtävän ohje</strong>
          <p>{{ task.instructions }}</p>
        </div>
        <div v-else key="ended" class="task-instructions task-instructions--ended">
          <strong class="task-panel__box-title">Tehtävän ohje</strong>
          <strong>Aika on päättynyt.</strong>
          <p>{{ task.instructions }}</p>
          <p>Tehtävään ei tehdä enää muutoksia. Järjestäjä lisää pisteet pistetaulukkoon.</p>
        </div>
      </transition>
    </section>

    <section v-if="dailyTips.length" class="task-panel__section" aria-label="Päivävinkit">
      <div class="task-tips">
        <strong class="task-panel__box-title">Päivävinkit</strong>
        <ol>
          <li v-for="tip in sortedDailyTips" :key="tip.id">
            {{ tip.text }}
          </li>
        </ol>
      </div>
    </section>

    <section v-if="nextTask" class="task-panel__section" aria-label="Seuraava tehtävä">
      <div class="next-task-preview">
        <strong class="task-panel__box-title">Seuraavaksi</strong>
        <span>{{ nextTask.title }}</span>
        <small>{{ formatDate(nextTask.startsAt) }} · {{ nextTask.location }}</small>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DailyTask, DailyTip, TaskStatus } from '../types'
import { formatClock as formatTime, formatWeekdayDateTime as formatDate } from '../utils/dateFormat'
import CountdownTimer from './CountdownTimer.vue'

const props = defineProps<{
  task: DailyTask
  status: TaskStatus
  nextTask?: DailyTask
  dailyTips: DailyTip[]
}>()

const sortedDailyTips = computed(() => {
  return [...props.dailyTips].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
})

const targetAt = computed(() => props.status === 'upcoming' ? props.task.startsAt : props.task.endsAt)
const countdownLabel = computed(() => props.status === 'upcoming' ? 'Päivätehtävä alkaa' : 'Päivätehtävä käynnissä')
const finishedLabel = computed(() => props.status === 'upcoming' ? 'Tehtävä alkaa nyt' : 'Päivätehtävä päättyi')
const timeLeftLabel = computed(() => props.status === 'upcoming' ? 'Seuraavan tehtävän alkuun' : 'Aikaa jäljellä')
const taskMetaHeading = computed(() => {
  if (props.status === 'upcoming') {
    return 'Seuraava tehtävä'
  }

  if (props.status === 'live') {
    return 'Nykyinen tehtävä'
  }

  return 'Tehtävä päättynyt'
})

</script>
