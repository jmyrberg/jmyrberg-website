<template>
  <section class="section-block home-panel" aria-label="Etusivu">
    <div class="home-stack">
      <article class="home-card home-card--task">
        <span class="home-card__title">Päivätehtävä</span>
        <span class="home-card__summary">{{ dailyTaskSummary }}</span>
        <div
          v-if="freeTime"
          class="countdown countdown--free-time"
          role="status"
          aria-label="Vapaa-aika"
        >
          <strong>
            <span>Vapaa-aika</span>
            <span class="free-time-emojis">🎉 🎣 🥏 🏊</span>
          </strong>
        </div>
        <button
          v-else-if="scoringInProgress"
          type="button"
          class="countdown countdown--scoring"
          aria-label="Avaa pisteet"
          @click="$emit('navigate', 'pisteet')"
        >
          <strong>Pisteiden kirjaus käynnissä</strong>
        </button>
        <CountdownTimer
          v-else
          :target-at="targetAt"
          :label="countdownLabel"
          :finished-label="finishedLabel"
          aria-label="Avaa päivätehtävä"
          @click="$emit('navigate', 'tehtava')"
        />
        <span v-if="status !== 'ended' && !freeTime" class="home-task-meta">
          <span>
            <small>Paikka</small>
            <strong>{{ task.location }}</strong>
          </span>
          <span>
            <small>Aika</small>
            <strong>{{ formatTime(task.startsAt) }} - {{ formatTime(task.endsAt) }}</strong>
          </span>
        </span>
      </article>

      <button
        type="button"
        class="home-card home-card--mice"
        aria-label="Hiiret"
        @click="$emit('navigate', 'hiiret')"
      >
        <span class="home-card__title">Hiiret</span>
        <span class="home-card__summary">{{ mouseSummary }}</span>
        <span class="home-mice-grid">
          <img
            v-for="mouse in mice"
            :key="mouse.id"
            :src="isFound(mouse.id) ? mouse.foundImage : mouse.image"
            :alt="mouse.label"
          />
        </span>
      </button>

      <button type="button" class="home-card home-card--scores" @click="$emit('navigate', 'pisteet')">
        <span class="home-card__title">Pisteet</span>
        <span v-if="ownTeamRankSummary" class="home-card__summary">{{ ownTeamRankSummary }}</span>
        <span class="home-score-grid">
          <span
            v-for="team in teams"
            :key="team.id"
            class="home-score-team"
            :class="{ 'home-score-team--own': playerTeamId === team.id }"
            :style="{ '--team-accent': team.accent }"
          >
            <strong>{{ team.name }}</strong>
            <b>{{ totalForTeam(team.id) }}p</b>
          </span>
        </span>
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DailyTask, FoundMouse, MouseAsset, MouseId, ScoreEvent, TaskStatus, Team, TeamId } from '../types'
import mouseBlack from '../assets/mouse-black.svg'
import mouseBlackFound from '../assets/mouse-black-found.svg'
import mousePink from '../assets/mouse-pink.svg'
import mousePinkFound from '../assets/mouse-pink-found.svg'
import mouseWhite from '../assets/mouse-white.svg'
import mouseWhiteFound from '../assets/mouse-white-found.svg'
import { formatClock as formatTime, isToday, isTomorrow } from '../utils/dateFormat'
import CountdownTimer from './CountdownTimer.vue'

type NavigateTarget = 'tehtava' | 'pisteet' | 'hiiret'

const props = defineProps<{
  teams: Team[]
  events: ScoreEvent[]
  task: DailyTask
  status: TaskStatus
  freeTime: boolean
  scoringInProgress: boolean
  foundMice: FoundMouse[]
  playerTeamId?: TeamId
}>()

defineEmits<{
  navigate: [target: NavigateTarget]
}>()

const mice: MouseAsset[] = [
  {
    id: 'white',
    label: 'Valkoinen hiiri',
    image: mouseWhite,
    foundImage: mouseWhiteFound
  },
  {
    id: 'pink',
    label: 'Pinkki hiiri',
    image: mousePink,
    foundImage: mousePinkFound
  },
  {
    id: 'black',
    label: 'Musta hiiri',
    image: mouseBlack,
    foundImage: mouseBlackFound
  }
]

const targetAt = computed(() => props.status === 'upcoming' ? props.task.startsAt : props.task.endsAt)
const countdownLabel = computed(() => props.status === 'upcoming' ? 'Päivätehtävä alkaa' : 'Päivätehtävä käynnissä')
const finishedLabel = computed(() => props.status === 'upcoming' ? 'Tehtävä alkaa nyt' : 'Päivätehtävä päättyi')
const dailyTaskSummary = computed(() => {
  if (props.scoringInProgress) {
    return 'Tuomaristo laskee, hengitä hetki.'
  }

  if (props.freeTime) {
    return freeTimeMessage
  }

  const summaryByStatus: Record<TaskStatus, string> = {
    upcoming: upcomingTaskSummary.value,
    live: 'Nyt mennään - ohjeet on avattu',
    ended: 'Päättynyt tehtävä on paketissa.'
  }

  return summaryByStatus[props.status]
})
const upcomingTaskSummary = computed(() => {
  if (isTomorrow(props.task.startsAt)) {
    return 'Seuraava päivätehtävä on huomenna.'
  }

  if (!isToday(props.task.startsAt)) {
    return 'Seuraava päivätehtävä odottaa tulevana päivänä.'
  }

  return 'Kerää joukkue kasaan ennen lähtölaukausta.'
})
const freeTimeMessage = 'Ei tehtävää käynnissä - nauti mökkiajasta ja pidä silmät auki.'
const mouseSummary = computed(() => hiddenMouseCount.value > 0 ? 'Hiiriä on piilossa' : 'Kaikki hiiret on löydetty')
const hiddenMouseCount = computed(() => mice.length - props.foundMice.length)
const ownTeamRankSummary = computed(() => props.playerTeamId ? teamStandingSummary(props.playerTeamId) : '')

function totalForTeam (teamId: TeamId): number {
  return props.events
    .filter(event => event.teamId === teamId)
    .reduce((total, event) => total + event.points, 0)
}

function teamRank (teamId: TeamId): number {
  const totals = props.teams
    .map(team => totalForTeam(team.id))
    .sort((a, b) => b - a)
  const teamTotal = totalForTeam(teamId)

  return totals.findIndex(total => total === teamTotal) + 1
}

function teamStandingSummary (teamId: TeamId): string {
  const ownTotal = totalForTeam(teamId)
  const otherTotals = props.teams
    .filter(team => team.id !== teamId)
    .map(team => totalForTeam(team.id))

  if (!otherTotals.length) {
    return 'Joukkueesi on johdossa.'
  }

  const bestOtherTotal = Math.max(...otherTotals)

  if (ownTotal > bestOtherTotal) {
    return `Joukkueesi on johdossa ${ownTotal - bestOtherTotal} pisteellä.`
  }

  if (ownTotal === bestOtherTotal) {
    return 'Joukkueesi on tasapisteissä kärjessä.'
  }

  const rank = teamRank(teamId)
  const topTotal = Math.max(...otherTotals, ownTotal)
  const trailingBy = topTotal - ownTotal

  if (rank === 2) {
    return `Joukkueesi on tappiolla ${trailingBy} pisteellä.`
  }

  return `Joukkueesi on sijalla ${rank}, tappiolla ${trailingBy} pisteellä.`
}

function isFound (mouseId: MouseId): boolean {
  return props.foundMice.some(mouse => mouse.mouseId === mouseId)
}

</script>
