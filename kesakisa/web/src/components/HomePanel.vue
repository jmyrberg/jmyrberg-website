<template>
  <section class="section-block home-panel" aria-label="Etusivu">
    <div class="home-stack">
      <article class="home-card home-card--task">
        <span class="home-card__title">Päivätehtävä</span>
        <span class="home-card__summary">{{ dailyTaskSummary }}</span>
        <div class="home-card__body">
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
            <strong>Pisteiden kirjaus käynnissä.</strong>
          </button>
          <button
            v-else-if="isOpenEndedLiveTask"
            type="button"
            class="countdown countdown--scoring"
            aria-label="Avaa päivätehtävä"
            @click="$emit('navigate', 'tehtava')"
          >
            <strong>Päivätehtävä käynnissä.</strong>
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
              <strong>{{ taskTimeLabel }}</strong>
            </span>
          </span>
        </div>
      </article>

      <button
        type="button"
        class="home-card home-card--mice"
        aria-label="Hiiret"
        @click="$emit('navigate', 'hiiret')"
      >
        <span class="home-card__title">Hiiret</span>
        <span class="home-card__summary">{{ mouseSummary }}</span>
        <span class="home-card__body">
          <span class="home-mice-grid">
            <img
              v-for="mouse in mice"
              :key="mouse.id"
              :src="isFound(mouse.id) ? mouse.foundImage : mouse.image"
              :alt="mouse.label"
            />
          </span>
        </span>
      </button>

      <button type="button" class="home-card home-card--scores" @click="$emit('navigate', 'pisteet')">
        <span class="home-card__title">Pisteet</span>
        <span v-if="scoreSummary" class="home-card__summary">{{ scoreSummary }}</span>
        <span class="home-card__body">
          <span class="home-score-grid">
            <span
              v-for="row in scoreRows"
              :key="row.team.id"
              class="home-score-team"
              :class="{ 'home-score-team--own': playerTeamId === row.team.id }"
              :style="{ '--team-accent': row.team.accent }"
            >
              <strong>{{ row.team.name }}</strong>
              <b>{{ row.total }}p</b>
            </span>
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

const hasEndTime = computed(() => Boolean(props.task.endsAt))
const isOpenEndedLiveTask = computed(() => props.status === 'live' && !hasEndTime.value)
const targetAt = computed(() => props.status === 'upcoming' ? props.task.startsAt : props.task.endsAt ?? props.task.startsAt)
const countdownLabel = computed(() => props.status === 'upcoming' ? 'Päivätehtävä alkaa.' : 'Päivätehtävä käynnissä.')
const finishedLabel = computed(() => props.status === 'upcoming' ? 'Tehtävä alkaa nyt.' : 'Päivätehtävä päättyi.')
const taskTimeLabel = computed(() => props.task.endsAt
  ? `${formatTime(props.task.startsAt)} - ${formatTime(props.task.endsAt)}`
  : `${formatTime(props.task.startsAt)} alkaen`
)
const dailyTaskSummary = computed(() => {
  if (props.scoringInProgress) {
    return 'Tuomaristo laskee, hengitä hetki.'
  }

  if (props.freeTime) {
    return freeTimeMessage
  }

  const summaryByStatus: Record<TaskStatus, string> = {
    upcoming: upcomingTaskSummary.value,
    live: liveTaskSummary.value,
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
const liveTaskSummary = computed(() => props.task.guidanceVisible
  ? 'Nyt mennään - ohjeet on avattu.'
  : 'Kokoonnutaan paikalle - ohjeet avataan järjestäjän merkistä.'
)
const mouseSummary = computed(() => hiddenMouseCount.value > 0 ? 'Hiiriä on piilossa.' : 'Kaikki hiiret on löydetty.')
const hiddenMouseCount = computed(() => mice.length - props.foundMice.length)
const scoreRows = computed(() => {
  const rows = props.teams.map((team, index) => ({
    team,
    originalIndex: index,
    total: totalForTeam(team.id),
    rank: 1
  }))
    .sort((a, b) => b.total - a.total || a.originalIndex - b.originalIndex)

  rows.forEach((row, index) => {
    const previousRow = rows[index - 1]
    row.rank = previousRow && previousRow.total === row.total ? previousRow.rank : index + 1
  })

  return rows
})
const scoreSummary = computed(() => {
  if (!props.events.length) {
    return 'Pisteitä ei ole vielä kirjattu.'
  }

  if (props.scoringInProgress) {
    return 'Pisteitä kirjataan parhaillaan.'
  }

  return props.playerTeamId ? teamStandingSummary(props.playerTeamId) : 'Tilanne päivittyy pisteiden mukana.'
})

function totalForTeam (teamId: TeamId): number {
  return props.events
    .filter(event => event.teamId === teamId)
    .reduce((total, event) => total + event.points, 0)
}

function teamRank (teamId: TeamId): number {
  return scoreRows.value.find(row => row.team.id === teamId)?.rank ?? props.teams.length
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
