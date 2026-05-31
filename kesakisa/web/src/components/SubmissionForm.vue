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

    <button type="submit" class="primary-button" :disabled="disabled">
      Tallenna suoritus
    </button>
  </form>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { DailyTask, ScoreCategory, ScoreEvent, Team, TeamId } from '../types'
import { formatShortDateTime as formatDate } from '../utils/dateFormat'

const props = defineProps<{
  teams: Team[]
  dailyTasks: DailyTask[]
  disabled?: boolean
}>()

const emit = defineEmits<{
  add: [event: ScoreEvent]
}>()

const categoryOptions: { value: ScoreCategory, label: string, defaultTitle: string, defaultPoints: number }[] = [
  { value: 'paivatehtava', label: 'Päivätehtävä', defaultTitle: 'Päivätehtävä', defaultPoints: 10 },
  { value: 'hiiritehtava', label: 'Hiiritehtävä', defaultTitle: 'Hiiritehtävä', defaultPoints: 16 },
  { value: 'bonus', label: 'Bonus', defaultTitle: 'Bonus', defaultPoints: 5 }
]

const pointOptions = [1, 2, 3, 5, 10, 16, 20]
const teamId = ref<TeamId>(props.teams[0]?.id ?? 'joukkue-1')
const category = ref<ScoreCategory>('paivatehtava')
const selectedDailyTaskId = ref(props.dailyTasks[0]?.id ?? '')
const selectedDailyTask = computed(() => props.dailyTasks.find(task => task.id === selectedDailyTaskId.value))
const title = ref(selectedDailyTask.value?.title ?? 'Päivätehtävä')
const points = ref(10)
const description = ref('')

function submit (): void {
  emit('add', {
    id: window.crypto?.randomUUID?.() ?? `event-${Date.now()}`,
    teamId: teamId.value,
    category: category.value,
    dailyTaskId: category.value === 'paivatehtava' ? selectedDailyTaskId.value : undefined,
    title: title.value,
    points: Number(points.value),
    description: description.value,
    createdAt: new Date().toISOString()
  })

  title.value = category.value === 'hiiritehtava' ? 'Hiiritehtävä' : selectedDailyTask.value?.title ?? 'Päivätehtävä'
  points.value = category.value === 'hiiritehtava' ? 16 : 10
  description.value = ''
}

function selectCategory (nextCategory: ScoreCategory): void {
  category.value = nextCategory
  const option = categoryOptions.find(item => item.value === nextCategory)

  if (!option) {
    return
  }

  title.value = nextCategory === 'paivatehtava' ? selectedDailyTask.value?.title ?? option.defaultTitle : option.defaultTitle
  points.value = option.defaultPoints
}

function selectDailyTask (task: DailyTask): void {
  selectedDailyTaskId.value = task.id
  title.value = task.title
}

</script>
