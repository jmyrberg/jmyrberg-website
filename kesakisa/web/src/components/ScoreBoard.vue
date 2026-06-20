<template>
  <section class="section-block" aria-label="Pisteet">
    <div class="score-grid">
      <article
        v-for="row in scoreRows"
        :key="row.team.id"
        class="score-team"
        :class="{ 'score-team--own': playerTeamId === row.team.id }"
        :style="{ '--team-accent': row.team.accent }"
      >
        <div class="score-team__title" :style="{ '--team-accent': row.team.accent }">
          <span class="score-team__rank">#{{ row.rank }}</span>
          <span class="score-team__name">
            <h2>{{ row.team.name }}</h2>
            <small v-if="row.memberNames">{{ row.memberNames }}</small>
          </span>
          <strong>{{ row.total }}p</strong>
        </div>

        <div class="score-list">
          <div
            v-for="event in row.events"
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
              <span class="score-row__text">
                <strong>{{ event.title }}</strong>
                <small>{{ scoreCategoryLabel(event.category) }} · {{ formatDate(event.createdAt) }}</small>
              </span>
              <b>{{ event.points }}p</b>
            </button>

            <transition name="expand">
              <div v-if="expandedEventId === event.id" class="score-detail">
                <small>Kirjattu {{ formatDate(event.createdAt) }}</small>
                <p v-if="event.description">{{ event.description }}</p>
              </div>
            </transition>
          </div>
          <p v-if="!row.events.length" class="score-empty">Ei kirjauksia vielä.</p>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Player, ScoreEvent, Team, TeamId } from '../types'
import { formatShortDateTime as formatDate } from '../utils/dateFormat'
import { scoreCategoryLabel } from '../utils/score'

const props = defineProps<{
  teams: Team[]
  players: Player[]
  events: ScoreEvent[]
  playerTeamId?: TeamId
}>()

const expandedEventId = ref<string | null>(null)

const scoreRows = computed(() => {
  const rows = props.teams.map((team, index) => ({
    team,
    originalIndex: index,
    total: props.events
      .filter(event => event.teamId === team.id)
      .reduce((total, event) => total + event.points, 0),
    events: props.events
      .filter(event => event.teamId === team.id)
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()),
    memberNames: props.players
      .filter(player => player.teamId === team.id)
      .map(player => player.name)
      .join(', '),
    rank: 1
  }))
    .sort((a, b) => b.total - a.total || a.originalIndex - b.originalIndex)

  rows.forEach((row, index) => {
    const previousRow = rows[index - 1]
    row.rank = previousRow && previousRow.total === row.total ? previousRow.rank : index + 1
  })

  return rows
})

function toggle (eventId: string): void {
  expandedEventId.value = expandedEventId.value === eventId ? null : eventId
}

</script>
