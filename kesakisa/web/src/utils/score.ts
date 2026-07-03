import type { DailyTask, ScoreCategory, ScoreEvent, Team, TeamId } from '../types'

export interface ScoreCategoryOption {
  value: ScoreCategory
  label: string
  defaultTitle: string
  defaultPoints: number
}

export const scoreCategoryOptions: ScoreCategoryOption[] = [
  { value: 'paivatehtava', label: 'Päivätehtävä', defaultTitle: 'Päivätehtävä', defaultPoints: 10 },
  { value: 'hiiritehtava', label: 'Hiiritehtävä', defaultTitle: 'Hiiritehtävä', defaultPoints: 16 },
  { value: 'bonus', label: 'Bonus', defaultTitle: 'Bonus', defaultPoints: 5 }
]

export const pointOptions = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

export function defaultDailyTaskId (dailyTasks: DailyTask[], activeDailyTaskId: string): string {
  return dailyTasks.some(task => task.id === activeDailyTaskId)
    ? activeDailyTaskId
    : dailyTasks[0]?.id ?? ''
}

export function scoreCategoryLabel (category: ScoreCategory): string {
  return scoreCategoryOptions.find(option => option.value === category)?.label ?? ''
}

export function scoreDefaultsForCategory (category: ScoreCategory, task?: DailyTask): Pick<ScoreEvent, 'title' | 'points'> {
  const option = scoreCategoryOptions.find(item => item.value === category) ?? scoreCategoryOptions[0]

  return {
    title: category === 'paivatehtava' ? task?.title ?? option.defaultTitle : option.defaultTitle,
    points: option.defaultPoints
  }
}

export function normalizeScoreEvent (
  event: ScoreEvent,
  teams: Team[],
  dailyTasks: DailyTask[],
  activeDailyTaskId: string
): ScoreEvent | null {
  const dailyTaskId = event.category === 'paivatehtava'
    ? event.dailyTaskId ?? defaultDailyTaskId(dailyTasks, activeDailyTaskId)
    : undefined
  const nextEvent = {
    ...event,
    dailyTaskId
  }
  const validationError = validateScoreEvent(nextEvent, teams, dailyTasks)

  if (validationError) {
    return null
  }

  return {
    ...nextEvent,
    dailyTaskId,
    title: event.title.trim(),
    points: Number(event.points),
    description: event.description.trim(),
    createdAt: Number.isNaN(new Date(event.createdAt).getTime()) ? new Date().toISOString() : event.createdAt
  }
}

export function validateScoreEvent (event: ScoreEvent, teams: Team[], dailyTasks: DailyTask[]): string | null {
  if (!teams.some(team => team.id === event.teamId)) {
    return 'Valitse joukkue pistekirjaukselle.'
  }

  if (!scoreCategoryOptions.some(option => option.value === event.category)) {
    return 'Valitse pistekirjauksen laji.'
  }

  if (event.category === 'paivatehtava' && !dailyTasks.some(task => task.id === event.dailyTaskId)) {
    return 'Valitse päivätehtävä pistekirjaukselle.'
  }

  if (!event.title.trim()) {
    return 'Pistekirjauksen otsikko puuttuu.'
  }

  const points = Number(event.points)

  if (!Number.isFinite(points) || points < -100 || points > 100) {
    return 'Pisteiden pitää olla väliltä -100 ja 100.'
  }

  return null
}

export function dailyTaskScoreKey (event: Pick<ScoreEvent, 'category' | 'teamId' | 'dailyTaskId'>): string | null {
  if (event.category !== 'paivatehtava' || !event.dailyTaskId) {
    return null
  }

  return `${event.teamId}:${event.dailyTaskId}`
}

export function teamNameForScore (teamId: TeamId, teams: Team[]): string {
  return teams.find(team => team.id === teamId)?.name ?? 'Tuntematon joukkue'
}
