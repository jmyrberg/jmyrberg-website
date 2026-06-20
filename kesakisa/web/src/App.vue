<template>
  <div class="app-shell" :class="{ 'app-shell--locked': !accessSession }" :style="patternStyle">
    <main class="phone-frame">
      <KesakisaHeader
        :task="participantDailyTask"
        :status="participantTaskStatus"
        :player-label="isAdminMode ? undefined : accessSession?.label"
        :player-accent="playerAccent"
        :show-countdown-label="activeTab !== 'host'"
        :show-countdown="false"
        :free-time="isFreeTime"
        @open-task="activeTab = 'tehtava'"
      />

      <section v-if="isCheckingAccess" class="login-panel section-block" aria-labelledby="login-check-heading">
        <div class="ribbon">
          <span id="login-check-heading">Tarkistetaan</span>
        </div>
        <p class="login-panel__help login-panel__help--standalone">
          Tarkistetaan voimassa oleva kirjautuminen.
        </p>
      </section>

      <LoginGate
        v-else-if="!accessSession"
        :required-role="requiredRole"
        @unlock="unlockApp"
      />

      <button
        v-if="accessSession && isAdminMode"
        type="button"
        class="host-corner-button"
        :class="{ 'host-corner-button--active': activeTab === 'host' }"
        aria-label="Avaa järjestäjänäkymä"
        @click="activeTab = 'host'"
      >
        Järjestäjä
      </button>

      <button
        v-if="accessSession && !isCheckingAccess && !isAdminMode"
        type="button"
        class="inbox-corner-button"
        :class="{ 'inbox-corner-button--active': activeTab === 'viestit' }"
        :aria-label="hasUnreadUserMessages ? 'Avaa viestit, uusi viesti' : 'Avaa viestit'"
        @click="openInbox"
      >
        <span v-if="hasUnreadUserMessages" class="inbox-corner-button__notification" aria-hidden="true" />
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M4 6h16v12H4z" />
          <path d="m4 7 8 6 8-6" />
        </svg>
      </button>

      <div
        v-if="accessSession && !isCheckingAccess"
        class="view-stack"
        :class="{ 'view-stack--host-status-dock': hostStatusDockVisible }"
      >
        <HomePanel
          v-if="activeTab === 'etusivu'"
          :teams="state.teams"
          :events="state.scoreEvents"
          :task="participantDailyTask"
          :status="participantTaskStatus"
          :free-time="isFreeTime"
          :scoring-in-progress="isScoringInProgress"
          :found-mice="state.foundMice"
          :player-team-id="currentPlayerTeamId"
          @navigate="activeTab = $event"
        />

        <DailyTaskPanel
          v-else-if="activeTab === 'tehtava'"
          :task="participantDailyTask"
          :status="participantTaskStatus"
          :has-task="hasParticipantDailyTask"
          :next-task="nextPreviewDailyTask"
          :daily-tips="participantDailyTips"
        />

        <ScoreBoard
          v-else-if="activeTab === 'pisteet'"
          :teams="state.teams"
          :players="state.players"
          :events="state.scoreEvents"
          :player-team-id="currentPlayerTeamId"
        />

        <MouseHunt
          v-else-if="activeTab === 'hiiret'"
          :found-mice="state.foundMice"
          :mouse-tips="state.mouseTips"
          @view-tips="markMouseTipsSeen"
        />

        <MessageInbox
          v-else-if="activeTab === 'viestit'"
          :messages="playerUserMessages"
        />

        <HostPanel
          v-else-if="activeTab === 'host' && isAdminMode"
          :teams="state.teams"
          :players="state.players"
          :access-token="accessSession?.token"
          :daily-task="activeDailyTask"
          :daily-tasks="state.dailyTasks"
          :active-daily-task-id="state.activeDailyTaskId"
          :mouse-tips="state.mouseTips"
          :daily-tips="state.dailyTips"
          :user-messages="state.userMessages"
          :found-mice="state.foundMice"
          :score-events="state.scoreEvents"
          :status-dock-visible="hostStatusDockVisible"
          @add-score="addScoreEvent"
          @update-score="updateScoreEvent"
          @remove-score="removeScoreEvent"
          @add-team="addTeam"
          @update-team="updateTeam"
          @remove-team="removeTeam"
          @add-player="addPlayer"
          @update-player="updatePlayer"
          @remove-player="removePlayer"
          @add-mouse-tip="addMouseTip"
          @update-mouse-tip="updateMouseTip"
          @remove-mouse-tip="removeMouseTip"
          @add-daily-tip="addDailyTip"
          @update-daily-tip="updateDailyTip"
          @remove-daily-tip="removeDailyTip"
          @add-user-message="addUserMessage"
          @update-user-message="updateUserMessage"
          @remove-user-message="removeUserMessage"
          @create-daily-task="createDailyTask"
          @update-daily-task="updateDailyTask"
          @remove-daily-task="removeDailyTask"
          @set-active-daily-task="setActiveDailyTask"
          @set-mouse-found="setMouseFound"
          @set-mouse-hidden="setMouseHidden"
          @start-task-now="startTaskNow"
          @end-task-now="endTaskNow"
          @host-feedback-change="hostFeedback = $event"
        />

        <section v-else class="section-block" aria-label="Säännöt">
          <ol class="rules-list">
            <li v-for="rule in rules" :key="rule">{{ rule }}</li>
          </ol>
        </section>

        <footer v-if="activeTab === 'host' && isAdminMode" class="local-footer">
          <button type="button" class="text-button" @click="resetLocalState">
            Nollaa kisadata kaikilta
          </button>
          <button type="button" class="text-button" @click="lockApp">
            Kirjaudu ulos
          </button>
        </footer>
      </div>
    </main>

    <HostStatusDock
      v-if="hostStatusDockVisible"
      :host-feedback="hostFeedback"
      :remote-save-status="remoteSaveStatus"
      :remote-save-message="remoteSaveStatusLabel"
      :remote-sync-error="remoteSyncError"
      @retry-remote-save="retryRemoteStateSave"
    />

    <nav v-if="accessSession && !isCheckingAccess && !isAdminMode" class="bottom-nav" aria-label="Kesäkisan näkymät">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        type="button"
        :aria-label="tab.id === 'hiiret' && hasUnreadMouseTips ? 'Hiiret, uusi vihje' : tab.label"
        :class="{ 'bottom-nav__button--active': activeTab === tab.id }"
        class="bottom-nav__button"
        @click="activeTab = tab.id"
      >
        <span
          v-if="tab.id === 'hiiret' && hasUnreadMouseTips"
          class="bottom-nav__notification"
          aria-hidden="true"
        >
          !
        </span>
        <span class="bottom-nav__icon">
          <img :src="tab.icon" alt="" />
        </span>
        <span class="bottom-nav__label">{{ tab.label }}</span>
      </button>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import DailyTaskPanel from './components/DailyTaskPanel.vue'
import HomePanel from './components/HomePanel.vue'
import HostPanel from './components/HostPanel.vue'
import HostStatusDock from './components/HostStatusDock.vue'
import KesakisaHeader from './components/KesakisaHeader.vue'
import LoginGate from './components/LoginGate.vue'
import MessageInbox from './components/MessageInbox.vue'
import MouseHunt from './components/MouseHunt.vue'
import ScoreBoard from './components/ScoreBoard.vue'
import backgroundPattern from './assets/background.svg'
import bucketBlack from './assets/bucket-black.svg'
import bucketBlue from './assets/bucket-blue.svg'
import bucketGreen from './assets/bucket-green.svg'
import bucketPurple from './assets/bucket-purple.svg'
import bucketRed from './assets/bucket-red.svg'
import { rules } from './data/seed'
import { clearAccessSession, loadAccessSession, saveAccessSession, validateAccessSession, type AccessRole, type AccessSession } from './services/accessGate'
import { loadRemoteState, saveRemoteState } from './services/gameStateApi'
import { loadState, resetState, saveState, STORAGE_KEY } from './services/localStore'
import type { AppState, DailyTask, DailyTip, MouseId, MouseTip, Player, ScoreEvent, TaskStatus, Team, TeamId, UserMessage } from './types'
import { dailyTaskScoreKey, normalizeScoreEvent } from './utils/score'

type TabId = 'etusivu' | 'tehtava' | 'pisteet' | 'hiiret' | 'saannot' | 'viestit' | 'host'
type RemoteSaveStatus = 'idle' | 'saving' | 'saved' | 'error'
type HostFeedbackStatus = 'pending' | 'success' | 'error'
type HostFeedback = {
  status: HostFeedbackStatus
  message: string
}

const EMPTY_DAILY_TASK_ID = 'empty-daily-task'
const tabs: { id: TabId, label: string, icon: string }[] = [
  { id: 'etusivu', label: 'Etusivu', icon: bucketBlack },
  { id: 'tehtava', label: 'Tehtävä', icon: bucketRed },
  { id: 'hiiret', label: 'Hiiret', icon: bucketGreen },
  { id: 'pisteet', label: 'Pisteet', icon: bucketBlue },
  { id: 'saannot', label: 'Säännöt', icon: bucketPurple }
]

const normalizedPath = window.location.pathname.replace(/\/+$/, '')
const isAdminMode = normalizedPath === '/kesakisa/admin' || normalizedPath.startsWith('/kesakisa/admin/')
const requiredRole: AccessRole = isAdminMode ? 'admin' : 'player'
const activeTab = ref<TabId>(isAdminMode ? 'host' : 'etusivu')
const accessSession = ref<AccessSession | null>(loadAccessSession(requiredRole))
const isCheckingAccess = ref(!!accessSession.value)
const state = ref<AppState>(loadState())
const now = ref(Date.now())
const STATE_POLL_MS = Number(import.meta.env.VITE_KESAKISA_STATE_POLL_MS ?? 10000)
const remoteSaveStatus = ref<RemoteSaveStatus>('idle')
const remoteSaveError = ref('')
const remoteSyncError = ref('')
const lastRemoteSavedAt = ref<string | null>(null)
const hostFeedback = ref<HostFeedback | null>(null)
let timer: number | undefined
let statePollTimer: number | undefined
let remoteSaveTimer: number | undefined
let remoteSaveStatusTimer: number | undefined
let skipNextLocalSave = false
let isApplyingRemoteState = false
let hasUnsavedRemoteState = false
let pendingRemoteState: AppState | null = null
let isRemoteSaveInFlight = false
let isRemoteStateSyncing = false

const patternStyle = computed(() => ({
  '--background-pattern': `url(${backgroundPattern})`
}))

const activeDailyTask = computed(() => {
  return state.value.dailyTasks.find(task => task.id === state.value.activeDailyTaskId) ??
    pickFallbackDailyTask(state.value.dailyTasks)
})

const sortedDailyTasks = computed(() => {
  return [...state.value.dailyTasks].sort((a, b) => new Date(a.startsAt).getTime() - new Date(b.startsAt).getTime())
})

const liveDailyTask = computed(() => {
  return sortedDailyTasks.value.find(task => taskStatusFor(task) === 'live')
})

const upcomingDailyTasks = computed(() => {
  return sortedDailyTasks.value.filter(task => taskStatusFor(task) === 'upcoming')
})

const latestEndedDailyTask = computed(() => {
  return [...sortedDailyTasks.value].reverse().find(task => taskStatusFor(task) === 'ended')
})

const participantDailyTask = computed(() => {
  return activeDailyTask.value
})

const hasParticipantDailyTask = computed(() => {
  const task = participantDailyTask.value
  const isActiveSelection = state.value.activeDailyTaskId === task.id
  const isCurrentOrPlanned = taskStatusFor(task) !== 'ended'

  return task.id !== EMPTY_DAILY_TASK_ID &&
    hasValidDailyTaskTiming(task) &&
    state.value.dailyTasks.some(item => item.id === task.id) &&
    (isActiveSelection || isCurrentOrPlanned)
})

const participantTaskStatus = computed<TaskStatus>(() => taskStatusFor(participantDailyTask.value))

const taskStatus = computed<TaskStatus>(() => taskStatusFor(activeDailyTask.value))

const nextPreviewDailyTask = computed<DailyTask | undefined>(() => {
  return undefined
})

const isScoringInProgress = computed(() => {
  if (!hasParticipantDailyTask.value || participantTaskStatus.value !== 'ended' || state.value.teams.length === 0) {
    return false
  }

  return scoredTeamsForTask(participantDailyTask.value).size < state.value.teams.length
})

const isFreeTime = computed(() => {
  if (!hasParticipantDailyTask.value) {
    return true
  }

  return participantTaskStatus.value === 'ended' && !isScoringInProgress.value
})

const currentPlayer = computed(() => {
  if (accessSession.value?.playerId) {
    const player = state.value.players.find(item => item.id === accessSession.value?.playerId)

    if (player) {
      return player
    }
  }

  if (!accessSession.value?.label) {
    return undefined
  }

  return state.value.players.find(item => normalizePlayerName(item.name) === normalizePlayerName(accessSession.value?.label ?? ''))
})

const currentPlayerTeamId = computed(() => currentPlayer.value?.teamId ?? undefined)

const playerAccent = computed(() => {
  const team = state.value.teams.find(item => item.id === currentPlayerTeamId.value)

  return team?.accent
})

const playerUserMessages = computed(() => {
  if (!currentPlayer.value) {
    return []
  }

  return state.value.userMessages.filter(message => message.recipientPlayerId === currentPlayer.value?.id)
})

const participantDailyTips = computed(() => {
  if (!hasParticipantDailyTask.value) {
    return []
  }

  return state.value.dailyTips.filter(tip => tip.dailyTaskId === participantDailyTask.value.id)
})

const remoteSaveStatusLabel = computed(() => {
  if (remoteSaveStatus.value === 'saving') {
    return 'Julkaistaan muutoksia osallistujille'
  }

  if (remoteSaveStatus.value === 'saved') {
    return lastRemoteSavedAt.value
      ? `Näkyy osallistujille klo ${formatStatusTime(lastRemoteSavedAt.value)}`
      : 'Näkyy osallistujille'
  }

  if (remoteSaveStatus.value === 'error') {
    return remoteSaveError.value || 'Julkaisu epäonnistui'
  }

  return ''
})

const hostStatusDockVisible = computed(() => {
  if (!isAdminMode || activeTab.value !== 'host') {
    return false
  }

  return !!hostFeedback.value || remoteSaveStatus.value !== 'idle' || !!remoteSyncError.value
})

const latestMouseTipCreatedAt = computed(() => {
  return state.value.mouseTips.reduce<string | null>((latestTipCreatedAt, tip) => {
    if (!latestTipCreatedAt) {
      return tip.createdAt
    }

    return new Date(tip.createdAt).getTime() > new Date(latestTipCreatedAt).getTime()
      ? tip.createdAt
      : latestTipCreatedAt
  }, null)
})

const hasUnreadMouseTips = computed(() => {
  if (!latestMouseTipCreatedAt.value) {
    return false
  }

  if (!state.value.mouseTipsSeenAt) {
    return true
  }

  return new Date(latestMouseTipCreatedAt.value).getTime() > new Date(state.value.mouseTipsSeenAt).getTime()
})

const latestUserMessageCreatedAt = computed(() => {
  return playerUserMessages.value.reduce<string | null>((latestMessageCreatedAt, message) => {
    if (!latestMessageCreatedAt) {
      return message.createdAt
    }

    return new Date(message.createdAt).getTime() > new Date(latestMessageCreatedAt).getTime()
      ? message.createdAt
      : latestMessageCreatedAt
  }, null)
})

const hasUnreadUserMessages = computed(() => {
  if (!latestUserMessageCreatedAt.value) {
    return false
  }

  const seenAt = currentPlayerUserMessagesSeenAt.value

  if (!seenAt) {
    return true
  }

  return new Date(latestUserMessageCreatedAt.value).getTime() > new Date(seenAt).getTime()
})

const currentPlayerUserMessagesSeenAt = computed(() => {
  const playerId = currentPlayer.value?.id

  if (!playerId) {
    return null
  }

  return state.value.userMessagesSeenAtByPlayerId[playerId] ?? state.value.userMessagesSeenAt
})

function scoredTeamsForTask (task: DailyTask): Set<TeamId> {
  const scoredTeams = new Set(
    state.value.scoreEvents
      .filter(event => event.category === 'paivatehtava' && event.dailyTaskId === task.id)
      .map(event => event.teamId)
  )

  return scoredTeams
}

function markMouseTipsSeen (seenAt: string): void {
  if (
    state.value.mouseTipsSeenAt &&
    new Date(state.value.mouseTipsSeenAt).getTime() >= new Date(seenAt).getTime()
  ) {
    return
  }

  state.value.mouseTipsSeenAt = seenAt
}

function markUserMessagesSeen (seenAt: string): void {
  const playerId = currentPlayer.value?.id

  if (!playerId) {
    return
  }

  const previousSeenAt = currentPlayerUserMessagesSeenAt.value

  if (
    previousSeenAt &&
    new Date(previousSeenAt).getTime() >= new Date(seenAt).getTime()
  ) {
    return
  }

  state.value.userMessagesSeenAtByPlayerId = {
    ...state.value.userMessagesSeenAtByPlayerId,
    [playerId]: seenAt
  }
}

function openInbox (): void {
  activeTab.value = 'viestit'

  if (latestUserMessageCreatedAt.value) {
    markUserMessagesSeen(latestUserMessageCreatedAt.value)
  }
}

function taskStatusFor (task: DailyTask): TaskStatus {
  const startsAt = new Date(task.startsAt).getTime()
  const endsAt = new Date(task.endsAt).getTime()

  if (now.value < startsAt) {
    return 'upcoming'
  }

  if (now.value <= endsAt) {
    return 'live'
  }

  return 'ended'
}

function hasValidDailyTaskTiming (task: DailyTask): boolean {
  const startsAt = new Date(task.startsAt).getTime()
  const endsAt = new Date(task.endsAt).getTime()

  return Number.isFinite(startsAt) && Number.isFinite(endsAt) && startsAt < endsAt
}

watch(state, nextState => {
  if (skipNextLocalSave) {
    skipNextLocalSave = false
    return
  }

  saveState(nextState)

  if (isAdminMode && accessSession.value && !isApplyingRemoteState) {
    scheduleRemoteStateSave(nextState)
  }
}, { deep: true })

watch(() => activeTab.value === 'viestit' ? latestUserMessageCreatedAt.value : null, seenAt => {
  if (seenAt) {
    markUserMessagesSeen(seenAt)
  }
})

onMounted(() => {
  timer = window.setInterval(() => {
    now.value = Date.now()
  }, 1000)

  statePollTimer = window.setInterval(() => {
    if (!document.hidden) {
      void syncRemoteState()
    }
  }, STATE_POLL_MS)

  window.addEventListener('focus', handleWindowFocus)
  window.addEventListener('visibilitychange', handleVisibilityChange)
  window.addEventListener('storage', syncStateFromStorage)
  window.addEventListener('beforeunload', handleBeforeUnload)
  void verifyStoredAccess()
})

onBeforeUnmount(() => {
  if (timer) {
    window.clearInterval(timer)
  }

  if (statePollTimer) {
    window.clearInterval(statePollTimer)
  }

  if (remoteSaveTimer) {
    window.clearTimeout(remoteSaveTimer)
  }

  if (remoteSaveStatusTimer) {
    window.clearTimeout(remoteSaveStatusTimer)
  }

  window.removeEventListener('focus', handleWindowFocus)
  window.removeEventListener('visibilitychange', handleVisibilityChange)
  window.removeEventListener('storage', syncStateFromStorage)
  window.removeEventListener('beforeunload', handleBeforeUnload)
})

function syncStateFromStorage (event: StorageEvent): void {
  if (event.key !== STORAGE_KEY) {
    return
  }

  if (isAdminMode && hasUnsavedRemoteState) {
    return
  }

  skipNextLocalSave = true
  state.value = loadState()
}

function handleWindowFocus (): void {
  void syncRemoteState()
}

function handleVisibilityChange (): void {
  if (document.hidden) {
    if (isAdminMode) {
      void flushRemoteStateSave()
    }
    return
  }

  void syncRemoteState()
}

function handleBeforeUnload (event: BeforeUnloadEvent): void {
  if (!isAdminMode || !accessSession.value || !hasUnsavedRemoteState) {
    return
  }

  event.preventDefault()
  event.returnValue = ''
}

async function syncRemoteState (): Promise<void> {
  const session = accessSession.value

  if (!session || isRemoteStateSyncing) {
    return
  }

  if (isAdminMode && (hasUnsavedRemoteState || isRemoteSaveInFlight || remoteSaveTimer)) {
    return
  }

  isRemoteStateSyncing = true

  try {
    const result = await loadRemoteState(session.token)

    if (result.error) {
      remoteSyncError.value = result.error
      return
    }

    remoteSyncError.value = ''

    if (result.state) {
      applyRemoteState(result.state)
      return
    }

    if (isAdminMode && !result.error) {
      const saveError = await saveRemoteState(state.value, session.token)

      if (saveError) {
        pendingRemoteState = cloneState(state.value)
        hasUnsavedRemoteState = true
        remoteSaveStatus.value = 'error'
        remoteSaveError.value = saveError
      } else {
        remoteSaveStatus.value = 'saved'
        remoteSaveError.value = ''
        remoteSyncError.value = ''
        lastRemoteSavedAt.value = new Date().toISOString()
        scheduleRemoteSaveStatusClear()
      }
    }
  } finally {
    isRemoteStateSyncing = false
  }
}

function applyRemoteState (remoteState: AppState): void {
  if (isAdminMode && hasUnsavedRemoteState) {
    return
  }

  const localMouseTipsSeenAt = state.value.mouseTipsSeenAt
  const localUserMessagesSeenAt = state.value.userMessagesSeenAt
  const localUserMessagesSeenAtByPlayerId = state.value.userMessagesSeenAtByPlayerId
  isApplyingRemoteState = true
  state.value = {
    ...remoteState,
    mouseTipsSeenAt: localMouseTipsSeenAt,
    userMessagesSeenAt: localUserMessagesSeenAt,
    userMessagesSeenAtByPlayerId: localUserMessagesSeenAtByPlayerId
  }

  window.setTimeout(() => {
    isApplyingRemoteState = false
  }, 0)
}

function scheduleRemoteStateSave (nextState: AppState): void {
  const session = accessSession.value

  if (!session) {
    return
  }

  hasUnsavedRemoteState = true
  pendingRemoteState = cloneState(nextState)
  remoteSaveStatus.value = 'saving'
  remoteSaveError.value = ''
  clearRemoteSaveStatusTimer()

  if (isRemoteSaveInFlight) {
    return
  }

  if (remoteSaveTimer) {
    window.clearTimeout(remoteSaveTimer)
  }

  remoteSaveTimer = window.setTimeout(() => {
    void flushRemoteStateSave()
  }, 450)
}

async function flushRemoteStateSave (): Promise<boolean> {
  const session = accessSession.value

  if (!session || isRemoteSaveInFlight || !pendingRemoteState) {
    return false
  }

  if (remoteSaveTimer) {
    window.clearTimeout(remoteSaveTimer)
    remoteSaveTimer = undefined
  }

  const stateToSave = pendingRemoteState
  pendingRemoteState = null
  isRemoteSaveInFlight = true
  remoteSaveStatus.value = 'saving'
  remoteSaveError.value = ''
  clearRemoteSaveStatusTimer()

  const saveError = await saveRemoteState(stateToSave, session.token)
  isRemoteSaveInFlight = false

  if (saveError) {
    pendingRemoteState = pendingRemoteState ?? stateToSave
    hasUnsavedRemoteState = true
    remoteSaveStatus.value = 'error'
    remoteSaveError.value = saveError
    return false
  }

  if (pendingRemoteState) {
    scheduleRemoteStateSave(pendingRemoteState)
  } else {
    hasUnsavedRemoteState = false
    remoteSaveStatus.value = 'saved'
    remoteSaveError.value = ''
    remoteSyncError.value = ''
    lastRemoteSavedAt.value = new Date().toISOString()
    scheduleRemoteSaveStatusClear()
  }

  return true
}

function retryRemoteStateSave (): void {
  void flushRemoteStateSave()
}

function cloneState (nextState: AppState): AppState {
  return JSON.parse(JSON.stringify(nextState)) as AppState
}

function scheduleRemoteSaveStatusClear (): void {
  clearRemoteSaveStatusTimer()
  remoteSaveStatusTimer = window.setTimeout(() => {
    if (remoteSaveStatus.value === 'saved' && !hasUnsavedRemoteState) {
      remoteSaveStatus.value = 'idle'
    }

    remoteSaveStatusTimer = undefined
  }, 4500)
}

function clearRemoteSaveStatusTimer (): void {
  if (remoteSaveStatusTimer) {
    window.clearTimeout(remoteSaveStatusTimer)
    remoteSaveStatusTimer = undefined
  }
}

function formatStatusTime (value: string): string {
  return new Date(value).toLocaleTimeString('fi-FI', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

function addScoreEvent (event: ScoreEvent): void {
  const scoreEvent = normalizeScoreEvent(event, state.value.teams, state.value.dailyTasks, state.value.activeDailyTaskId)

  if (!scoreEvent) {
    return
  }

  const duplicate = findDuplicateDailyScore(scoreEvent)

  if (duplicate) {
    updateScoreEvent({
      ...duplicate,
      teamId: scoreEvent.teamId,
      category: scoreEvent.category,
      dailyTaskId: scoreEvent.dailyTaskId,
      title: scoreEvent.title,
      points: scoreEvent.points,
      description: scoreEvent.description
    })
    return
  }

  state.value.scoreEvents = [scoreEvent, ...state.value.scoreEvents]
  openPlayerTab('pisteet')
}

function updateScoreEvent (event: ScoreEvent): void {
  const scoreEvent = normalizeScoreEvent(event, state.value.teams, state.value.dailyTasks, state.value.activeDailyTaskId)

  if (!scoreEvent) {
    return
  }

  state.value.scoreEvents = state.value.scoreEvents.map(existingEvent => existingEvent.id === scoreEvent.id ? scoreEvent : existingEvent)
}

function removeScoreEvent (eventId: string): void {
  state.value.scoreEvents = state.value.scoreEvents.filter(event => event.id !== eventId)
}

function findDuplicateDailyScore (event: ScoreEvent): ScoreEvent | undefined {
  const key = dailyTaskScoreKey(event)

  if (!key) {
    return undefined
  }

  return state.value.scoreEvents.find(scoreEvent => scoreEvent.id !== event.id && dailyTaskScoreKey(scoreEvent) === key)
}

function addTeam (team: Team): void {
  state.value.teams = [...state.value.teams, team]
}

function updateTeam (team: Team): void {
  state.value.teams = state.value.teams.map(existingTeam => existingTeam.id === team.id ? team : existingTeam)
}

function removeTeam (teamId: TeamId): void {
  if (state.value.teams.length <= 1) {
    return
  }

  state.value.teams = state.value.teams.filter(team => team.id !== teamId)
  state.value.players = state.value.players.map(player => player.teamId === teamId ? { ...player, teamId: null } : player)
  state.value.scoreEvents = state.value.scoreEvents.filter(event => event.teamId !== teamId)
  state.value.foundMice = state.value.foundMice.filter(found => found.teamId !== teamId)
}

function addPlayer (player: Player): void {
  const existingPlayer = state.value.players.find(existing => {
    return existing.id === player.id || normalizePlayerName(existing.name) === normalizePlayerName(player.name)
  })

  if (existingPlayer) {
    updatePlayer({
      ...existingPlayer,
      name: player.name,
      inviteCode: player.inviteCode ?? existingPlayer.inviteCode,
      teamId: existingPlayer.teamId ?? player.teamId
    })
    return
  }

  state.value.players = [...state.value.players, player]
}

function updatePlayer (player: Player): void {
  state.value.players = state.value.players.map(existingPlayer => existingPlayer.id === player.id ? player : existingPlayer)
}

function removePlayer (playerId: string): void {
  state.value.players = state.value.players.filter(player => player.id !== playerId)
  state.value.userMessages = state.value.userMessages.filter(message => message.recipientPlayerId !== playerId)

  const remainingSeenAt = { ...state.value.userMessagesSeenAtByPlayerId }
  delete remainingSeenAt[playerId]
  state.value.userMessagesSeenAtByPlayerId = remainingSeenAt
}

function addMouseTip (tip: MouseTip): void {
  state.value.mouseTips = [tip, ...state.value.mouseTips]
  openPlayerTab('hiiret')
}

function updateMouseTip (tip: MouseTip): void {
  state.value.mouseTips = state.value.mouseTips.map(existingTip => existingTip.id === tip.id ? tip : existingTip)
}

function removeMouseTip (tipId: string): void {
  state.value.mouseTips = state.value.mouseTips.filter(tip => tip.id !== tipId)
}

function addDailyTip (tip: DailyTip): void {
  state.value.dailyTips = [tip, ...state.value.dailyTips]
  openPlayerTab('tehtava')
}

function updateDailyTip (tip: DailyTip): void {
  state.value.dailyTips = state.value.dailyTips.map(existingTip => existingTip.id === tip.id ? tip : existingTip)
}

function removeDailyTip (tipId: string): void {
  state.value.dailyTips = state.value.dailyTips.filter(tip => tip.id !== tipId)
}

function addUserMessage (message: UserMessage): void {
  state.value.userMessages = [message, ...state.value.userMessages]
}

function updateUserMessage (message: UserMessage): void {
  state.value.userMessages = state.value.userMessages.map(existingMessage => existingMessage.id === message.id ? message : existingMessage)
}

function removeUserMessage (messageId: string): void {
  state.value.userMessages = state.value.userMessages.filter(message => message.id !== messageId)
}

function createDailyTask (task: DailyTask): void {
  const hasActiveTask = state.value.dailyTasks.some(existingTask => existingTask.id === state.value.activeDailyTaskId)

  state.value.dailyTasks = [task, ...state.value.dailyTasks]

  if (!hasActiveTask) {
    state.value.activeDailyTaskId = task.id
    state.value.dailyTask = task
  }

  openPlayerTab('tehtava')
}

function updateDailyTask (task: DailyTask): void {
  state.value.dailyTasks = state.value.dailyTasks.map(existingTask => existingTask.id === task.id ? task : existingTask)
  if (state.value.activeDailyTaskId === task.id) {
    state.value.dailyTask = task
  }
  openPlayerTab('tehtava')
}

function removeDailyTask (taskId: string): void {
  const task = state.value.dailyTasks.find(item => item.id === taskId)

  if (!task) {
    return
  }

  const nextDailyTasks = state.value.dailyTasks.filter(item => item.id !== taskId)
  state.value.dailyTasks = nextDailyTasks
  state.value.scoreEvents = state.value.scoreEvents.filter(event => event.dailyTaskId !== taskId)
  state.value.dailyTips = state.value.dailyTips.filter(tip => tip.dailyTaskId !== taskId)

  if (state.value.activeDailyTaskId === taskId) {
    const fallbackTask = pickReplacementDailyTask(nextDailyTasks) ?? createEmptyDailyTask()
    state.value.activeDailyTaskId = fallbackTask.id
    state.value.dailyTask = fallbackTask
  } else {
    const activeTask = nextDailyTasks.find(item => item.id === state.value.activeDailyTaskId) ?? state.value.dailyTask
    state.value.dailyTask = activeTask
  }
  openPlayerTab('tehtava')
}

function setActiveDailyTask (taskId: string): void {
  const task = state.value.dailyTasks.find(item => item.id === taskId)

  if (!task) {
    return
  }

  state.value.activeDailyTaskId = taskId
  state.value.dailyTask = task
}

function pickFallbackDailyTask (tasks: DailyTask[]): DailyTask {
  const sortedTasks = [...tasks].sort((a, b) => new Date(a.startsAt).getTime() - new Date(b.startsAt).getTime())
  const upcomingTask = sortedTasks.find(task => taskStatusFor(task) === 'upcoming')
  const endedTask = [...sortedTasks].reverse().find(task => taskStatusFor(task) === 'ended')
  const liveTask = sortedTasks.find(task => taskStatusFor(task) === 'live')

  return liveTask ?? upcomingTask ?? endedTask ?? state.value.dailyTask
}

function pickReplacementDailyTask (tasks: DailyTask[]): DailyTask | undefined {
  const sortedTasks = [...tasks].sort((a, b) => new Date(a.startsAt).getTime() - new Date(b.startsAt).getTime())
  const liveTask = sortedTasks.find(task => taskStatusFor(task) === 'live')
  const upcomingTask = sortedTasks.find(task => taskStatusFor(task) === 'upcoming')

  return liveTask ?? upcomingTask
}

function createEmptyDailyTask (): DailyTask {
  const timestamp = new Date(Date.now() - 1000).toISOString()

  return {
    id: EMPTY_DAILY_TASK_ID,
    title: 'Ei päivätehtävää',
    location: 'Ei paikkaa',
    startsAt: timestamp,
    endsAt: timestamp,
    preparationText: 'Lisää uusi päivätehtävä järjestäjänäkymässä.',
    instructions: 'Päivätehtävää ei ole vielä lisätty.',
    guidanceVisible: false
  }
}

function setMouseFound (mouseId: MouseId, teamId: TeamId): void {
  const foundMouse = {
    mouseId,
    teamId,
    foundAt: new Date().toISOString()
  }

  state.value.foundMice = [
    ...state.value.foundMice.filter(found => found.mouseId !== mouseId),
    foundMouse
  ]
}

function setMouseHidden (mouseId: MouseId): void {
  state.value.foundMice = state.value.foundMice.filter(found => found.mouseId !== mouseId)
}

function resetLocalState (): void {
  const confirmation = window.prompt('Tämä nollaa kisadatan kaikilta osallistujilta. Kirjoita NOLLAA, jos haluat jatkaa.')

  if (confirmation !== 'NOLLAA') {
    return
  }

  state.value = resetState()
  activeTab.value = isAdminMode ? 'host' : 'etusivu'
}

function unlockApp (session: AccessSession): void {
  saveAccessSession(session)
  accessSession.value = session
  void syncRemoteState()
}

async function lockApp (): Promise<void> {
  if (isAdminMode && accessSession.value && hasUnsavedRemoteState) {
    const didSave = await flushRemoteStateSave()

    if (!didSave) {
      window.alert('Muutoksia ei saatu julkaistua. Yritä uudelleen ennen uloskirjautumista.')
      return
    }
  }

  clearAccessSession()
  accessSession.value = null
  activeTab.value = isAdminMode ? 'host' : 'etusivu'
}

async function verifyStoredAccess (): Promise<void> {
  if (!accessSession.value) {
    return
  }

  const session = await validateAccessSession(accessSession.value, requiredRole)
  isCheckingAccess.value = false

  if (!session) {
    await lockApp()
    return
  }

  saveAccessSession(session)
  accessSession.value = session
  await syncRemoteState()
}

function openPlayerTab (tab: Exclude<TabId, 'host'>): void {
  if (!isAdminMode) {
    activeTab.value = tab
  }
}

function normalizePlayerName (name: string): string {
  return name.trim().toLocaleLowerCase('fi-FI')
}

function startTaskNow (taskId?: string): void {
  const task = taskId
    ? state.value.dailyTasks.find(item => item.id === taskId) ?? activeDailyTask.value
    : activeDailyTask.value
  const startsAt = new Date(Date.now() - 1000)
  const endsAt = new Date(Date.now() + 57 * 60 * 1000)

  updateDailyTask({
    ...task,
    startsAt: startsAt.toISOString(),
    endsAt: endsAt.toISOString()
  })
  setActiveDailyTask(task.id)
}

function endTaskNow (taskId?: string): void {
  const task = taskId
    ? state.value.dailyTasks.find(item => item.id === taskId) ?? activeDailyTask.value
    : activeDailyTask.value

  updateDailyTask({
    ...task,
    endsAt: new Date(Date.now() - 1000).toISOString()
  })
  setActiveDailyTask(task.id)
}
</script>
