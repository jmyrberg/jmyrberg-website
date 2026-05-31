<template>
  <section class="section-block task-panel" aria-labelledby="tehtava-heading">
    <div class="ribbon">
      <span id="tehtava-heading">Päivätehtävä</span>
    </div>

    <section class="task-panel__section task-panel__section--status" aria-label="Päivätehtävän tilanne">
      <p class="section-summary task-panel__summary">{{ statusSummary }}</p>

      <CountdownTimer
        v-if="status !== 'ended'"
        class="task-panel__countdown"
        :target-at="targetAt"
        :label="countdownLabel"
        :finished-label="finishedLabel"
        :as-button="false"
        :show-label="false"
      />
    </section>

    <section class="task-panel__section" aria-labelledby="tehtava-aika-paikka-heading">
      <h2 id="tehtava-aika-paikka-heading" class="task-panel__subtitle">{{ taskMetaHeading }}</h2>
      <div class="task-panel__meta">
        <div>
          <small>Paikka</small>
          <strong>{{ task.location }}</strong>
        </div>
        <div>
          <small>Aika</small>
          <strong>{{ formatTime(task.startsAt) }}-{{ formatTime(task.endsAt) }}</strong>
        </div>
      </div>
    </section>

    <section class="task-panel__section" aria-labelledby="tehtava-valmistautuminen-heading">
      <h2 id="tehtava-valmistautuminen-heading" class="task-panel__subtitle">Valmistautuminen</h2>
      <div class="task-panel__prep">
        <span>{{ task.preparationText }}</span>
      </div>
    </section>

    <section class="task-panel__section" aria-labelledby="tehtava-ohjeet-heading">
      <h2 id="tehtava-ohjeet-heading" class="task-panel__subtitle">Tehtävän ohje</h2>
      <transition name="expand" mode="out-in">
        <div v-if="status === 'upcoming'" key="locked" class="task-lock">
          <strong>Ohjeet ovat vielä lukossa.</strong>
          <span>Ne avautuvat automaattisesti, kun päivätehtävä alkaa.</span>
        </div>
        <div v-else-if="status === 'live'" key="live" class="task-instructions">
          <p>{{ task.instructions }}</p>
        </div>
        <div v-else key="ended" class="task-instructions task-instructions--ended">
          <strong>Aika on päättynyt.</strong>
          <p>{{ task.instructions }}</p>
          <p>Tehtävään ei tehdä enää muutoksia. Järjestäjä lisää pisteet pistetaulukkoon.</p>
        </div>
      </transition>
    </section>

    <section v-if="dailyTips.length" class="task-panel__section" aria-labelledby="tehtava-vinkit-heading">
      <h2 id="tehtava-vinkit-heading" class="task-panel__subtitle">Päivävinkit</h2>
      <div class="task-tips">
        <ol>
          <li v-for="tip in sortedDailyTips" :key="tip.id">
            {{ tip.text }}
          </li>
        </ol>
      </div>
    </section>

    <section v-if="nextTask" class="task-panel__section" aria-labelledby="tehtava-seuraava-heading">
      <h2 id="tehtava-seuraava-heading" class="task-panel__subtitle">Seuraavaksi</h2>
      <div class="next-task-preview">
        <span>{{ nextTask.title }}</span>
        <small>{{ formatDate(nextTask.startsAt) }} · {{ nextTask.location }}</small>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DailyTask, DailyTip, TaskStatus } from '../types'
import { formatClock as formatTime, formatWeekdayDateTime as formatDate, isToday, isTomorrow } from '../utils/dateFormat'
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
const taskMetaHeading = computed(() => {
  if (props.status === 'upcoming') {
    return 'Seuraava tehtävä'
  }

  if (props.status === 'live') {
    return 'Nykyinen tehtävä'
  }

  return 'Päättynyt tehtävä'
})

const statusSummary = computed(() => {
  if (props.status === 'upcoming') {
    if (isTomorrow(props.task.startsAt)) {
      return 'Huomisen päivätehtävä - ennakkotiedot alla.'
    }

    if (!isToday(props.task.startsAt)) {
      return 'Seuraavan päivän päivätehtävä - ennakkotiedot alla.'
    }

    return 'Kerää joukkue kasaan ennen lähtölaukausta.'
  }

  if (props.status === 'live') {
    return 'Nyt mennään - ohjeet on avattu.'
  }

  return props.nextTask
    ? 'Tämä tehtävä on päättynyt. Seuraavan tehtävän tiedot näkyvät alempana.'
    : 'Päättynyt tehtävä on paketissa.'
})

</script>
