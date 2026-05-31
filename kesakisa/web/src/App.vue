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

      <div v-if="accessSession && !isCheckingAccess" class="view-stack">
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
          :next-task="nextPreviewDailyTask"
          :daily-tips="state.dailyTips"
        />

        <ScoreBoard
          v-else-if="activeTab === 'pisteet'"
          :teams="state.teams"
          :events="state.scoreEvents"
          :player-team-id="currentPlayerTeamId"
        />

        <MouseHunt
          v-else-if="activeTab === 'hiiret'"
          :found-mice="state.foundMice"
          :mouse-tips="state.mouseTips"
          @view-tips="markMouseTipsSeen"
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
          :found-mice="state.foundMice"
          :score-events="state.scoreEvents"
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
          @create-daily-task="createDailyTask"
          @update-daily-task="updateDailyTask"
          @remove-daily-task="removeDailyTask"
          @set-active-daily-task="setActiveDailyTask"
          @set-mouse-found="setMouseFound"
          @set-mouse-hidden="setMouseHidden"
          @start-task-now="startTaskNow"
          @end-task-now="endTaskNow"
        />

        <section v-else class="section-block" aria-label="Säännöt">
          <ol class="rules-list">
            <li v-for="rule in rules" :key="rule">{{ rule }}</li>
          </ol>
        </section>

        <footer v-if="activeTab === 'host' && isAdminMode" class="local-footer">
          <button type="button" class="text-button" @click="resetLocalState">
            Nollaa paikallinen data
          </button>
          <button type="button" class="text-button" @click="lockApp">
            Kirjaudu ulos
          </button>
        </footer>
      </div>
    </main>

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
import KesakisaHeader from './components/KesakisaHeader.vue'
import LoginGate from './components/LoginGate.vue'
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
import type { AppState, DailyTask, DailyTip, MouseId, MouseTip, Player, ScoreEvent, TaskStatus, Team, TeamId } from './types'

type TabId = 'etusivu' | 'tehtava' | 'pisteet' | 'hiiret' | 'saannot' | 'host'

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
const STATE_POLL_MS = Number(import.meta.env.VITE_KESAKISA_STATE_POLL_MS ?? 30000)
let timer: number | undefined
let statePollTimer: number | undefined
let remoteSaveTimer: number | undefined
let skipNextLocalSave = false
let isApplyingRemoteState = false
let hasPendingRemoteSave = false

const patternStyle = computed(() => ({
  '--background-pattern': `url(${backgroundPattern})`
}))

const activeDailyTask = computed(() => {
  return state.value.dailyTasks.find(task => task.id === state.value.activeDailyTaskId) ?? state.value.dailyTask
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
  return liveDailyTask.value ?? upcomingDailyTasks.value[0] ?? latestEndedDailyTask.value ?? activeDailyTask.value
})

const participantTaskStatus = computed<TaskStatus>(() => taskStatusFor(participantDailyTask.value))

const taskStatus = computed<TaskStatus>(() => taskStatusFor(activeDailyTask.value))

const nextPreviewDailyTask = computed(() => {
  return upcomingDailyTasks.value.find(task => task.id !== participantDailyTask.value.id)
})

const isScoringInProgress = computed(() => {
  const taskToScore = latestEndedDailyTask.value

  if (!taskToScore) {
    return false
  }

  return scoredTeamsForTask(taskToScore).size < state.value.teams.length
})

const isFreeTime = computed(() => {
  return !liveDailyTask.value && !upcomingDailyTasks.value.length && !!latestEndedDailyTask.value && !isScoringInProgress.value
})

const currentPlayer = computed(() => {
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

onMounted(() => {
  timer = window.setInterval(() => {
    now.value = Date.now()
  }, 1000)

  statePollTimer = window.setInterval(() => {
    if (!document.hidden) {
      void syncRemoteState()
    }
  }, STATE_POLL_MS)

  window.addEventListener('storage', syncStateFromStorage)
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

  window.removeEventListener('storage', syncStateFromStorage)
})

function syncStateFromStorage (event: StorageEvent): void {
  if (event.key !== STORAGE_KEY) {
    return
  }

  skipNextLocalSave = true
  state.value = loadState()
}

async function syncRemoteState (): Promise<void> {
  const session = accessSession.value

  if (!session || hasPendingRemoteSave) {
    return
  }

  const result = await loadRemoteState(session.token)

  if (result.state) {
    applyRemoteState(result.state)
    return
  }

  if (isAdminMode && !result.error) {
    await saveRemoteState(state.value, session.token)
  }
}

function applyRemoteState (remoteState: AppState): void {
  const localMouseTipsSeenAt = state.value.mouseTipsSeenAt
  isApplyingRemoteState = true
  state.value = {
    ...remoteState,
    mouseTipsSeenAt: localMouseTipsSeenAt
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

  if (remoteSaveTimer) {
    window.clearTimeout(remoteSaveTimer)
  }

  hasPendingRemoteSave = true
  remoteSaveTimer = window.setTimeout(() => {
    void saveRemoteState(nextState, session.token).finally(() => {
      hasPendingRemoteSave = false
      remoteSaveTimer = undefined
    })
  }, 450)
}

function addScoreEvent (event: ScoreEvent): void {
  state.value.scoreEvents = [event, ...state.value.scoreEvents]
  openPlayerTab('pisteet')
}

function updateScoreEvent (event: ScoreEvent): void {
  state.value.scoreEvents = state.value.scoreEvents.map(existingEvent => existingEvent.id === event.id ? event : existingEvent)
}

function removeScoreEvent (eventId: string): void {
  state.value.scoreEvents = state.value.scoreEvents.filter(event => event.id !== eventId)
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

function createDailyTask (task: DailyTask): void {
  state.value.dailyTasks = [task, ...state.value.dailyTasks]
  state.value.activeDailyTaskId = task.id
  state.value.dailyTask = task
  openPlayerTab('tehtava')
}

function updateDailyTask (task: DailyTask): void {
  state.value.dailyTasks = state.value.dailyTasks.map(existingTask => existingTask.id === task.id ? task : existingTask)
  state.value.activeDailyTaskId = task.id
  state.value.dailyTask = task
  openPlayerTab('tehtava')
}

function removeDailyTask (taskId: string): void {
  const task = state.value.dailyTasks.find(item => item.id === taskId)

  if (!task || state.value.dailyTasks.length <= 1 || taskStatusFor(task) !== 'upcoming') {
    return
  }

  state.value.dailyTasks = state.value.dailyTasks.filter(item => item.id !== taskId)
  const fallbackTask = pickFallbackDailyTask(state.value.dailyTasks)
  state.value.activeDailyTaskId = fallbackTask.id
  state.value.dailyTask = fallbackTask
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
  const liveTask = sortedTasks.find(task => taskStatusFor(task) === 'live')
  const upcomingTask = sortedTasks.find(task => taskStatusFor(task) === 'upcoming')
  const endedTask = [...sortedTasks].reverse().find(task => taskStatusFor(task) === 'ended')

  return liveTask ?? upcomingTask ?? endedTask ?? state.value.dailyTask
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
  state.value = resetState()
  activeTab.value = isAdminMode ? 'host' : 'etusivu'
}

function unlockApp (session: AccessSession): void {
  saveAccessSession(session)
  accessSession.value = session
  void syncRemoteState()
}

function lockApp (): void {
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
    lockApp()
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

function startTaskNow (): void {
  const startsAt = new Date(Date.now() - 1000)
  const endsAt = new Date(Date.now() + 57 * 60 * 1000)

  updateDailyTask({
    ...activeDailyTask.value,
    startsAt: startsAt.toISOString(),
    endsAt: endsAt.toISOString()
  })
}

function endTaskNow (): void {
  updateDailyTask({
    ...activeDailyTask.value,
    endsAt: new Date(Date.now() - 1000).toISOString()
  })
}
</script>
