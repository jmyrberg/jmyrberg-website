import { createInitialState } from '../data/seed'
import type { AppState } from '../types'

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

  return {
    ...fallback,
    ...state,
    teams: Array.isArray(state.teams) && state.teams.length > 0 ? state.teams : fallback.teams,
    players: Array.isArray(state.players) ? state.players : fallback.players,
    dailyTask: activeDailyTask,
    dailyTasks,
    activeDailyTaskId,
    scoreEvents: Array.isArray(state.scoreEvents) ? state.scoreEvents : fallback.scoreEvents,
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

export function saveState (state: AppState): void {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
}

export function resetState (): AppState {
  const nextState = createInitialState()
  saveState(nextState)
  return nextState
}
