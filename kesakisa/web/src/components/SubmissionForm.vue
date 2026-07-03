<template>
  <form class="submission-form" @submit.prevent="submit">
    <div class="choice-field submission-form__wide">
      <span>Joukkue</span>
      <div class="choice-group choice-group--teams">
        <button
          v-for="team in teams"
          :key="team.id"
          type="button"
          class="choice-button"
          :class="{ 'choice-button--active': teamId === team.id }"
          :style="{ '--choice-accent': team.accent }"
          @click="teamId = team.id"
        >
          {{ team.name }}
        </button>
      </div>
    </div>

    <div class="choice-field submission-form__wide">
      <span>Laji</span>
      <div class="choice-group">
        <button
          v-for="option in categoryOptions"
          :key="option.value"
          type="button"
          class="choice-button"
          :class="{ 'choice-button--active': category === option.value }"
          @click="selectCategory(option.value)"
        >
          {{ option.label }}
        </button>
      </div>
    </div>

    <div v-if="category === 'paivatehtava'" class="choice-field submission-form__wide">
      <span>Päivätehtävä</span>
      <div class="task-choice-list">
        <button
          v-for="task in dailyTasks"
          :key="task.id"
          type="button"
          class="task-choice"
          :class="{ 'task-choice--active': selectedDailyTaskId === task.id }"
          @click="selectDailyTask(task)"
        >
          <strong>{{ task.title }}</strong>
          <span>{{ formatDate(task.startsAt) }}</span>
        </button>
      </div>
    </div>

    <label>
      Otsikko
      <input v-model.trim="title" maxlength="48" required />
    </label>

    <label class="points-input">
      Pisteet
      <input v-model.number="points" type="number" min="-100" max="100" required />
    </label>

    <div class="choice-field submission-form__wide">
      <span>Pikapisteet</span>
      <div class="points-chips">
        <button
          v-for="value in pointOptions"
          :key="value"
          type="button"
          class="point-chip"
          :class="{ 'point-chip--active': points === value }"
          @click="points = value"
        >
          {{ value }}p
        </button>
      </div>
    </div>

    <label class="submission-form__wide">
      Lisätiedot (valinnainen)
      <textarea v-model.trim="description" rows="4" />
    </label>

    <p v-if="formError" class="form-error submission-form__wide" role="alert">
      {{ formError }}
    </p>

    <button type="submit" class="primary-button" :disabled="disabled">
      Tallenna suoritus
    </button>
  </form>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { DailyTask, ScoreCategory, ScoreEvent, Team, TeamId } from '../types'
import { defaultDailyTaskId, pointOptions, scoreCategoryOptions, scoreDefaultsForCategory, validateScoreEvent } from '../utils/score'
import { formatShortDateTime as formatDate } from '../utils/dateFormat'

const props = defineProps<{
  teams: Team[]
  dailyTasks: DailyTask[]
  activeDailyTaskId: string
  disabled?: boolean
}>()

const emit = defineEmits<{
  add: [event: ScoreEvent, accept: (accepted: boolean) => void]
}>()

const categoryOptions = scoreCategoryOptions
const teamId = ref<TeamId>(props.teams[0]?.id ?? 'joukkue-1')
const category = ref<ScoreCategory>('paivatehtava')
const selectedDailyTaskId = ref(defaultDailyTaskId(props.dailyTasks, props.activeDailyTaskId))
const selectedDailyTask = computed(() => props.dailyTasks.find(task => task.id === selectedDailyTaskId.value))
const initialDefaults = scoreDefaultsForCategory(category.value, selectedDailyTask.value)
const title = ref(initialDefaults.title)
const points = ref(initialDefaults.points)
const description = ref('')
const formError = ref('')

watch(
  () => props.activeDailyTaskId,
  () => {
    if (category.value !== 'paivatehtava') {
      return
    }

    selectedDailyTaskId.value = defaultDailyTaskId(props.dailyTasks, props.activeDailyTaskId)
    applyCategoryDefaults()
  }
)

watch(
  () => props.dailyTasks.map(task => task.id).join('|'),
  () => {
    if (!props.dailyTasks.some(task => task.id === selectedDailyTaskId.value)) {
      selectedDailyTaskId.value = defaultDailyTaskId(props.dailyTasks, props.activeDailyTaskId)
      applyCategoryDefaults()
    }
  }
)

watch(
  () => props.teams.map(team => team.id).join('|'),
  () => {
    if (!props.teams.some(team => team.id === teamId.value)) {
      teamId.value = props.teams[0]?.id ?? ''
    }
  }
)

function submit (): void {
  const event: ScoreEvent = {
    id: window.crypto?.randomUUID?.() ?? `event-${Date.now()}`,
    teamId: teamId.value,
    category: category.value,
    dailyTaskId: category.value === 'paivatehtava' ? selectedDailyTaskId.value : undefined,
    title: title.value,
    points: Number(points.value),
    description: description.value,
    createdAt: new Date().toISOString()
  }

  const validationError = validateScoreEvent(event, props.teams, props.dailyTasks)

  if (validationError) {
    formError.value = validationError
    return
  }

  let wasAccepted = false
  formError.value = ''
  emit('add', event, accepted => {
    wasAccepted = accepted
  })

  if (!wasAccepted) {
    return
  }

  applyCategoryDefaults()
  description.value = ''
}

function selectCategory (nextCategory: ScoreCategory): void {
  category.value = nextCategory
  const option = categoryOptions.find(item => item.value === nextCategory)

  if (!option) {
    return
  }

  applyCategoryDefaults()
}

function selectDailyTask (task: DailyTask): void {
  selectedDailyTaskId.value = task.id
  if (category.value === 'paivatehtava') {
    applyCategoryDefaults()
  }
}

function applyCategoryDefaults (): void {
  const defaults = scoreDefaultsForCategory(category.value, selectedDailyTask.value)
  title.value = defaults.title
  points.value = defaults.points
  formError.value = ''
}

</script>
