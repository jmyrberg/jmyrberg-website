<template>
  <section class="section-block" aria-labelledby="pisteet-heading">
    <div class="ribbon">
      <span id="pisteet-heading">Pisteet</span>
    </div>

    <p v-if="ownTeamRankSummary" class="section-summary">{{ ownTeamRankSummary }}</p>

    <div class="score-grid">
      <article
        v-for="team in teams"
        :key="team.id"
        class="score-team"
        :class="{ 'score-team--own': playerTeamId === team.id }"
        :style="{ '--team-accent': team.accent }"
      >
        <div class="score-team__title" :style="{ '--team-accent': team.accent }">
          <h2>{{ team.name }}</h2>
          <strong>{{ totalForTeam(team.id) }}p</strong>
        </div>

        <div class="score-list">
          <div
            v-for="event in eventsForTeam(team.id)"
            :key="event.id"
            class="score-entry"
          >
            <button
              type="button"
              class="score-row"
              :class="{ 'score-row--open': expandedEventId === event.id }"
              :aria-expanded="expandedEventId === event.id"
              @click="toggle(event.id)"
            >
              <strong>{{ event.title }}</strong>
              <b>{{ event.points }}p</b>
            </button>

            <transition name="expand">
              <div v-if="expandedEventId === event.id" class="score-detail">
                <small>Kirjattu {{ formatDate(event.createdAt) }}</small>
                <p v-if="event.description">{{ event.description }}</p>
              </div>
            </transition>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ScoreEvent, Team, TeamId } from '../types'
import { formatShortDateTime as formatDate } from '../utils/dateFormat'

const props = defineProps<{
  teams: Team[]
  events: ScoreEvent[]
  playerTeamId?: TeamId
}>()

const expandedEventId = ref<string | null>(null)
const ownTeamRankSummary = computed(() => props.playerTeamId ? teamStandingSummary(props.playerTeamId) : '')

function eventsForTeam (teamId: TeamId): ScoreEvent[] {
  return props.events
    .filter(event => event.teamId === teamId)
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
}

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

function toggle (eventId: string): void {
  expandedEventId.value = expandedEventId.value === eventId ? null : eventId
}

</script>
