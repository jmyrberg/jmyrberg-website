import { createInitialState } from '../data/seed'
import type { AppState, ScoreCategory, ScoreEvent, Team, DailyTask } from '../types'
import { normalizeScoreEvent, scoreCategoryOptions } from '../utils/score'

export const STORAGE_KEY = 'kesakisa-2026-local-state-v1'

export function loadState (): AppState {
  const fallback = createInitialState()
  const stored = window.localStorage.getItem(STORAGE_KEY)

  if (!stored) {
    return fallback
  }

  try {
    return normalizeState(JSON.parse(stored) as Partial<AppState>, fallback)
  } catch {
    return fallback
  }
}

export function normalizeState (state: Partial<AppState>, fallback = createInitialState()): AppState {
  const parsedDailyTask = state.dailyTask ? { ...fallback.dailyTask, ...state.dailyTask } : fallback.dailyTask
  const dailyTasks = Array.isArray(state.dailyTasks)
    ? state.dailyTasks
    : [parsedDailyTask]
  const activeDailyTaskId = state.activeDailyTaskId && dailyTasks.some(task => task.id === state.activeDailyTaskId)
    ? state.activeDailyTaskId
    : dailyTasks[0]?.id ?? parsedDailyTask.id
  const activeDailyTask = dailyTasks.find(task => task.id === activeDailyTaskId) ?? dailyTasks[0] ?? parsedDailyTask
  const teams = Array.isArray(state.teams) && state.teams.length > 0 ? state.teams : fallback.teams

  return {
    ...fallback,
    ...state,
    teams,
    players: Array.isArray(state.players) ? state.players : fallback.players,
    dailyTask: activeDailyTask,
    dailyTasks,
    activeDailyTaskId,
    scoreEvents: normalizeScoreEvents(state.scoreEvents, teams, dailyTasks, activeDailyTaskId, fallback.scoreEvents),
    foundMice: Array.isArray(state.foundMice) ? state.foundMice : fallback.foundMice,
    mouseTips: Array.isArray(state.mouseTips) ? state.mouseTips : fallback.mouseTips,
    mouseTipsSeenAt: typeof state.mouseTipsSeenAt === 'string' ? state.mouseTipsSeenAt : fallback.mouseTipsSeenAt,
    dailyTips: Array.isArray(state.dailyTips)
      ? state.dailyTips.map(tip => ({
        ...tip,
        dailyTaskId: typeof tip.dailyTaskId === 'string' ? tip.dailyTaskId : activeDailyTaskId
      }))
      : fallback.dailyTips,
    userMessages: Array.isArray(state.userMessages) ? state.userMessages : fallback.userMessages,
    userMessagesSeenAt: typeof state.userMessagesSeenAt === 'string' ? state.userMessagesSeenAt : fallback.userMessagesSeenAt,
    userMessagesSeenAtByPlayerId: isStringRecord(state.userMessagesSeenAtByPlayerId)
      ? state.userMessagesSeenAtByPlayerId
      : fallback.userMessagesSeenAtByPlayerId
  }
}

export function remoteStatePayload (state: AppState): AppState {
  return {
    ...state,
    mouseTipsSeenAt: null,
    userMessagesSeenAt: null,
    userMessagesSeenAtByPlayerId: {}
  }
}

function isStringRecord (value: unknown): value is Record<string, string> {
  return !!value &&
    typeof value === 'object' &&
    !Array.isArray(value) &&
    Object.values(value).every(item => typeof item === 'string')
}

function normalizeScoreEvents (
  value: unknown,
  teams: Team[],
  dailyTasks: DailyTask[],
  activeDailyTaskId: string,
  fallback: ScoreEvent[]
): ScoreEvent[] {
  if (!Array.isArray(value)) {
    return fallback
  }

  const seenIds = new Set<string>()
  const normalizedEvents: ScoreEvent[] = []

  value.forEach((item, index) => {
    const event = parseScoreEvent(item, index)

    if (!event || seenIds.has(event.id)) {
      return
    }

    const normalizedEvent = normalizeScoreEvent(event, teams, dailyTasks, activeDailyTaskId)

    if (!normalizedEvent) {
      return
    }

    seenIds.add(normalizedEvent.id)
    normalizedEvents.push(normalizedEvent)
  })

  return normalizedEvents
}

function parseScoreEvent (value: unknown, index: number): ScoreEvent | null {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return null
  }

  const candidate = value as Partial<ScoreEvent>
  const category = isScoreCategory(candidate.category) ? candidate.category : null

  if (!category) {
    return null
  }

  return {
    id: typeof candidate.id === 'string' && candidate.id ? candidate.id : `score-${index}`,
    teamId: typeof candidate.teamId === 'string' ? candidate.teamId : '',
    category,
    dailyTaskId: typeof candidate.dailyTaskId === 'string' ? candidate.dailyTaskId : undefined,
    title: typeof candidate.title === 'string' ? candidate.title : '',
    points: Number(candidate.points),
    description: typeof candidate.description === 'string' ? candidate.description : '',
    createdAt: typeof candidate.createdAt === 'string' ? candidate.createdAt : new Date().toISOString()
  }
}

function isScoreCategory (value: unknown): value is ScoreCategory {
  return scoreCategoryOptions.some(option => option.value === value)
}

export function saveState (state: AppState): void {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
}

export function resetState (): AppState {
  const nextState = createInitialState()
  saveState(nextState)
  return nextState
}
