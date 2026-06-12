<template>
  <section class="section-block host-panel" aria-label="Järjestäjä">
    <div v-if="isHostBusy" class="host-saving-pill" role="status" aria-live="polite">
      <span class="host-saving-pill__spinner" aria-hidden="true" />
      <span>Tallennetaan</span>
    </div>

    <div class="host-stack">
      <span class="host-tab-label">Aihe</span>
      <div class="host-domain-tabs">
        <button
          v-for="domain in domains"
          :key="domain.id"
          type="button"
          :class="{ 'host-domain-tabs__button--active': activeDomain === domain.id }"
          class="host-domain-tabs__button"
          @click="selectDomain(domain.id)"
        >
          {{ domain.label }}
        </button>
      </div>

      <div class="host-divider" role="presentation" />

      <span class="host-tab-label">Toiminto</span>
      <div class="host-action-tabs">
        <button
          v-for="action in currentActions"
          :key="action.id"
          type="button"
          :class="{ 'host-action-tabs__button--active': activeAction === action.id }"
          class="host-action-tabs__button"
          @click="activeAction = action.id"
        >
          {{ action.label }}
        </button>
      </div>

      <form
        v-if="activeDomain === 'paivatehtava' && activeAction === 'luo'"
        class="host-card tip-form"
        @submit.prevent="createDailyTaskSetup"
      >
        <h2>Lisää päivätehtävä</h2>
        <p class="host-help">Syötä tehtävän sisältö ja aikataulu yhdessä paikassa. Ohjeet avautuvat osallistujille vasta aloitushetkellä.</p>
        <label>
          Otsikko
          <input v-model.trim="dailyTaskDraft.title" required maxlength="48" />
        </label>
        <label>
          Paikka
          <input v-model.trim="dailyTaskDraft.location" required maxlength="60" />
        </label>
        <label>
          Aloitusaika
          <input v-model="dailyTaskStartDraft" type="datetime-local" required />
        </label>
        <label>
          Lopetusaika
          <input v-model="dailyTaskEndDraft" type="datetime-local" required />
        </label>
        <label>
          Ennen aloitusta näkyvä ohje
          <textarea v-model.trim="dailyTaskDraft.preparationText" rows="3" required />
        </label>
        <label>
          Aloituksessa avautuvat ohjeet
          <textarea v-model.trim="dailyTaskDraft.instructions" rows="5" required />
        </label>
        <button type="submit" class="primary-button" :disabled="isHostBusy">
          Lisää päivätehtävä
        </button>
      </form>

      <div v-else-if="activeDomain === 'paivatehtava' && activeAction === 'hallinta'" class="host-card">
        <h2>Muokkaa päivätehtävää</h2>
        <div class="choice-field">
          <span>Valitse päivätehtävä</span>
          <div class="task-choice-list">
            <button
              v-for="task in dailyTasks"
              :key="task.id"
              type="button"
              class="task-choice"
              :class="{ 'task-choice--active': activeDailyTaskId === task.id }"
              @click="selectDailyTask(task)"
            >
              <strong>{{ task.title }}</strong>
              <span>{{ formatDate(task.startsAt) }}</span>
            </button>
          </div>
        </div>
        <div class="task-summary">
          <strong>{{ dailyTask.title }}</strong>
          <span>{{ dailyTask.location }} · {{ formatDate(dailyTask.startsAt) }} - {{ formatClock(dailyTask.endsAt) }}</span>
        </div>
        <div v-if="canRemoveDailyTask(dailyTask)" class="host-subsection">
          <h3>Poista tehtävä</h3>
          <p class="host-help">Voit poistaa valitun tehtävän myös silloin, kun se on käynnissä. Vähintään yksi tehtävä pitää jäädä jäljelle.</p>
          <button type="button" class="pill-button pill-button--danger" :disabled="isHostBusy" @click="removeDailyTask(dailyTask.id)">
            Poista tehtävä
          </button>
        </div>

        <div class="host-subsection">
          <h3>Käsiohjaus</h3>
          <p class="host-help">Aloita tehtävä käsin tai päätä se ennen ajastinta.</p>
          <div class="quick-actions">
            <button type="button" class="pill-button" :disabled="isHostBusy" @click="startTaskNow">
              Aloita nyt
            </button>
            <button type="button" class="pill-button pill-button--danger" :disabled="isHostBusy" @click="endTaskNow">
              Lopeta nyt
            </button>
          </div>
        </div>

        <details class="host-subsection">
          <summary>Muokkaa tehtävää</summary>
          <form class="tip-form" @submit.prevent="submitDailyTaskSetup">
            <label>
              Otsikko
              <input v-model.trim="dailyTaskDraft.title" required maxlength="48" />
            </label>
            <label>
              Paikka
              <input v-model.trim="dailyTaskDraft.location" required maxlength="60" />
            </label>
            <label>
              Aloitusaika
              <input v-model="dailyTaskStartDraft" type="datetime-local" required />
            </label>
            <label>
              Lopetusaika
              <input v-model="dailyTaskEndDraft" type="datetime-local" required />
            </label>
            <label>
              Ennen aloitusta näkyvä ohje
              <textarea v-model.trim="dailyTaskDraft.preparationText" rows="3" required />
            </label>
            <label>
              Aloituksessa avautuvat ohjeet
              <textarea v-model.trim="dailyTaskDraft.instructions" rows="5" required />
            </label>
            <button type="submit" class="primary-button" :disabled="isHostBusy">
              Tallenna muutokset
            </button>
          </form>
        </details>

        <div class="host-subsection">
          <h3>Lisävinkit</h3>
          <form class="tip-form" @submit.prevent="submitDailyTip">
            <label>
              Uusi vinkki
              <textarea v-model.trim="dailyTipText" rows="3" required />
            </label>
            <button type="submit" class="primary-button" :disabled="isHostBusy">
              Julkaise päivävinkki
            </button>
          </form>
          <div v-if="sortedDailyTips.length" class="host-list">
            <article v-for="tip in sortedDailyTips" :key="tip.id" class="host-list-item">
              <small>{{ formatDate(tip.createdAt) }}</small>
              <textarea
                :value="dailyDrafts[tip.id] ?? tip.text"
                rows="3"
                @input="dailyDrafts[tip.id] = inputValue($event)"
              />
              <div class="quick-actions">
                <button type="button" class="pill-button" :disabled="isHostBusy" @click="saveDailyTip(tip)">
                  Tallenna
                </button>
                <button type="button" class="pill-button pill-button--danger" :disabled="isHostBusy" @click="removeDailyTip(tip.id)">
                  Poista
                </button>
              </div>
            </article>
          </div>
          <p v-else class="empty-note">Ei päivävinkkejä.</p>
        </div>
      </div>

      <div v-else-if="activeDomain === 'hiiret' && activeAction === 'tila'" class="host-card">
        <h2>Muokkaa hiiriä</h2>
        <div class="mouse-toggle-grid">
          <button
            v-for="mouse in mice"
            :key="mouse.id"
            type="button"
            class="mouse-toggle"
            :class="{ 'mouse-toggle--found': foundMouse(mouse.id) }"
            :aria-pressed="!!foundMouse(mouse.id)"
            :disabled="isHostBusy"
            @click="toggleMouse(mouse.id)"
          >
            <img :src="foundMouse(mouse.id) ? mouse.foundImage : mouse.image" :alt="mouse.label" />
            <strong>{{ mouse.label }}</strong>
            <span>{{ foundMouse(mouse.id) ? teamName(foundMouse(mouse.id)?.teamId) : 'Piilossa' }}</span>
          </button>
        </div>
        <div class="choice-field">
          <span>Löytänyt joukkue</span>
          <div class="choice-group">
            <button
              type="button"
              class="choice-button"
              :class="{ 'choice-button--active': selectedMouseTeam === null }"
              @click="selectedMouseTeam = null"
            >
              Ei löydetty
            </button>
            <button
              v-for="team in teams"
              :key="team.id"
              type="button"
              class="choice-button"
              :class="{ 'choice-button--active': selectedMouseTeam === team.id }"
              :style="{ '--choice-accent': team.accent }"
              @click="selectedMouseTeam = team.id"
            >
              {{ team.name }}
            </button>
          </div>
        </div>
      </div>

      <div v-else-if="activeDomain === 'hiiret' && activeAction === 'vinkit'" class="host-card">
        <h2>Lisää hiirivinkki</h2>
        <form class="tip-form" @submit.prevent="submitTip">
          <div class="mouse-choice-group" role="radiogroup" aria-label="Valitse hiiri">
            <button
              v-for="mouse in mice"
              :key="mouse.id"
              type="button"
              class="mouse-choice"
              :class="{ 'mouse-choice--active': mouseId === mouse.id }"
              :aria-checked="mouseId === mouse.id"
              role="radio"
              @click="mouseId = mouse.id"
            >
              <img :src="mouse.image" :alt="mouse.label" />
              <span>{{ mouse.label }}</span>
            </button>
          </div>
          <label>
            Uusi vinkki
            <textarea v-model.trim="tipText" rows="3" required />
          </label>
          <button type="submit" class="primary-button" :disabled="isHostBusy">
            Lisää vinkki
          </button>
        </form>
        <div v-if="mouseTips.length" class="host-list">
          <article v-for="tip in sortedMouseTips" :key="tip.id" class="host-list-item">
            <small>{{ mouseLabel(tip.mouseId) }} · {{ formatDate(tip.createdAt) }}</small>
            <div class="mouse-choice-group mouse-choice-group--compact" role="radiogroup" aria-label="Vaihda hiiri">
              <button
                v-for="mouse in mice"
                :key="mouse.id"
                type="button"
                class="mouse-choice"
                :class="{ 'mouse-choice--active': selectedTipMouse(tip) === mouse.id }"
                :aria-checked="selectedTipMouse(tip) === mouse.id"
                role="radio"
                @click="mouseTipSelections[tip.id] = mouse.id"
              >
                <img :src="mouse.image" :alt="mouse.label" />
                <span>{{ mouse.label }}</span>
              </button>
            </div>
            <textarea
              :value="mouseDrafts[tip.id] ?? tip.text"
              rows="3"
              @input="mouseDrafts[tip.id] = inputValue($event)"
            />
            <div class="quick-actions">
              <button type="button" class="pill-button" :disabled="isHostBusy" @click="saveMouseTip(tip)">
                Tallenna
              </button>
              <button type="button" class="pill-button pill-button--danger" :disabled="isHostBusy" @click="removeMouseTip(tip.id)">
                Poista
              </button>
            </div>
          </article>
        </div>
        <p v-else class="empty-note">Ei hiirivinkkejä.</p>
      </div>

      <div v-else-if="activeDomain === 'pisteet' && activeAction === 'lisaa'" class="host-card">
        <h2>Lisää pisteet</h2>
        <SubmissionForm
          :teams="teams"
          :daily-tasks="dailyTasks"
          :disabled="isHostBusy"
          @add="submitScore"
        />
      </div>

      <div v-else-if="activeDomain === 'pisteet' && activeAction === 'muokkaa'" class="host-card">
        <h2>Muokkaa pisteitä</h2>
        <div v-if="scoreEvents.length" class="host-list">
          <article v-for="scoreEvent in sortedScoreEvents" :key="scoreEvent.id" class="host-list-item score-editor">
            <header class="score-editor__header">
              <strong>{{ scoreHeader(scoreEvent) }}</strong>
              <small>{{ teamName(scoreTeam(scoreEvent)) }} · {{ formatDate(scoreEvent.createdAt) }}</small>
            </header>

            <div class="choice-field">
              <span>Joukkue</span>
              <div class="choice-group choice-group--teams">
                <button
                  v-for="team in teams"
                  :key="team.id"
                  type="button"
                  class="choice-button"
                  :class="{ 'choice-button--active': scoreTeam(scoreEvent) === team.id }"
                  :style="{ '--choice-accent': team.accent }"
                  @click="updateScoreDraft(scoreEvent, { teamId: team.id })"
                >
                  {{ team.name }}
                </button>
              </div>
            </div>

            <div class="choice-field">
              <span>Laji</span>
              <div class="choice-group">
                <button
                  v-for="option in scoreCategoryOptions"
                  :key="option.value"
                  type="button"
                  class="choice-button"
                  :class="{ 'choice-button--active': scoreCategory(scoreEvent) === option.value }"
                  @click="updateScoreCategory(scoreEvent, option.value)"
                >
                  {{ option.label }}
                </button>
              </div>
            </div>

            <div v-if="scoreCategory(scoreEvent) === 'paivatehtava'" class="choice-field">
              <span>Päivätehtävä</span>
              <div class="task-choice-list">
                <button
                  v-for="task in dailyTasks"
                  :key="task.id"
                  type="button"
                  class="task-choice"
                  :class="{ 'task-choice--active': scoreDailyTaskId(scoreEvent) === task.id }"
                  @click="updateScoreTask(scoreEvent, task)"
                >
                  <strong>{{ task.title }}</strong>
                  <span>{{ formatDate(task.startsAt) }}</span>
                </button>
              </div>
            </div>

            <div class="score-editor__fields">
              <label>
                Otsikko
                <input
                  :value="scoreTitle(scoreEvent)"
                  maxlength="48"
                  required
                  @input="updateScoreDraft(scoreEvent, { title: inputValue($event) })"
                />
              </label>

              <label>
                Pisteet
                <input
                  :value="scorePoints(scoreEvent)"
                  type="number"
                  min="-100"
                  max="100"
                  required
                  @input="updateScoreDraft(scoreEvent, { points: Number(inputValue($event)) })"
                />
              </label>
            </div>

            <div class="choice-field">
              <span>Pikapisteet</span>
              <div class="points-chips">
                <button
                  v-for="value in pointOptions"
                  :key="value"
                  type="button"
                  class="point-chip"
                  :class="{ 'point-chip--active': scorePoints(scoreEvent) === value }"
                  @click="updateScoreDraft(scoreEvent, { points: value })"
                >
                  {{ value }}p
                </button>
              </div>
            </div>

            <label>
              Lisätiedot
              <textarea
                :value="scoreDescription(scoreEvent)"
                rows="3"
                @input="updateScoreDraft(scoreEvent, { description: inputValue($event) })"
              />
            </label>

            <div class="quick-actions">
              <button type="button" class="pill-button" :disabled="isHostBusy" @click="saveScore(scoreEvent)">
                Tallenna
              </button>
              <button type="button" class="pill-button pill-button--danger" :disabled="isHostBusy" @click="removeScore(scoreEvent.id)">
                Poista
              </button>
            </div>
          </article>
        </div>
        <p v-else class="empty-note">Ei pistekirjauksia.</p>
      </div>

      <div v-else-if="activeDomain === 'viestit' && activeAction === 'laheta'" class="host-card">
        <h2>Viestit</h2>
        <form class="tip-form" @submit.prevent="submitUserMessage">
          <label>
            Vastaanottaja
            <select v-model="userMessageRecipientId" required>
              <option value="" disabled>Valitse pelaaja</option>
              <option v-for="player in players" :key="player.id" :value="player.id">
                {{ player.name }}
              </option>
            </select>
          </label>
          <label>
            Uusi viesti
            <textarea v-model.trim="userMessageText" rows="4" required maxlength="500" />
          </label>
          <button type="submit" class="primary-button" :disabled="isHostBusy || !userMessageRecipientId">
            Lähetä viesti
          </button>
        </form>

        <div v-if="userMessages.length" class="host-list">
          <article v-for="message in sortedUserMessages" :key="message.id" class="host-list-item">
            <small>{{ playerName(message.recipientPlayerId) }} · {{ formatDate(message.createdAt) }}</small>
            <textarea
              :value="userMessageDrafts[message.id] ?? message.text"
              rows="3"
              maxlength="500"
              @input="userMessageDrafts[message.id] = inputValue($event)"
            />
            <div class="quick-actions">
              <button type="button" class="pill-button" :disabled="isHostBusy" @click="saveUserMessage(message)">
                Tallenna
              </button>
              <button type="button" class="pill-button pill-button--danger" :disabled="isHostBusy" @click="removeUserMessage(message.id)">
                Poista
              </button>
            </div>
          </article>
        </div>
        <p v-else class="empty-note">Ei lähetettyjä viestejä.</p>
      </div>

      <div v-else-if="activeDomain === 'joukkueet' && activeAction === 'hallinta'" class="host-card">
        <h2>Joukkueet</h2>
        <form class="tip-form" @submit.prevent="submitTeam">
          <label>
            Joukkueen nimi
            <input v-model.trim="teamNameDraft" required maxlength="32" />
          </label>
          <div class="choice-field">
            <span>Väri</span>
            <div class="color-choice-row">
              <button
                v-for="color in teamColorOptions"
                :key="color"
                type="button"
                class="color-choice"
                :class="{ 'color-choice--active': teamAccentDraft === color }"
                :style="{ '--team-accent': color }"
                :aria-label="`Valitse väri ${color}`"
                @click="teamAccentDraft = color"
              />
            </div>
          </div>
          <label>
            Oma väri
            <input v-model="teamAccentDraft" type="color" required />
          </label>
          <button type="submit" class="primary-button" :disabled="isHostBusy">
            Lisää joukkue
          </button>
        </form>

        <div v-if="teams.length" class="host-list">
          <article v-for="team in teams" :key="team.id" class="host-list-item team-editor">
            <small>Joukkue</small>
            <label>
              Nimi
              <input
                :value="teamDraftName(team)"
                maxlength="32"
                required
                @input="updateTeamDraft(team, { name: inputValue($event) })"
              />
            </label>
            <div class="choice-field">
              <span>Väri</span>
              <div class="color-choice-row">
                <button
                  v-for="color in teamColorOptions"
                  :key="color"
                  type="button"
                  class="color-choice"
                  :class="{ 'color-choice--active': teamDraftAccent(team) === color }"
                  :style="{ '--team-accent': color }"
                  :aria-label="`Valitse väri ${color}`"
                  @click="updateTeamDraft(team, { accent: color })"
                />
              </div>
            </div>
            <label>
              Oma väri
              <input
                :value="teamDraftAccent(team)"
                type="color"
                required
                @input="updateTeamDraft(team, { accent: inputValue($event) })"
              />
            </label>
            <div class="quick-actions">
              <button type="button" class="pill-button" :disabled="isHostBusy" @click="saveTeam(team)">
                Tallenna
              </button>
              <button
                type="button"
                class="pill-button pill-button--danger"
                :disabled="teams.length <= 1 || isHostBusy"
                @click="removeTeam(team.id)"
              >
                Poista
              </button>
            </div>
          </article>
        </div>
      </div>

      <div v-else-if="activeDomain === 'pelaajat' && activeAction === 'hallinta'" class="host-card">
        <h2>Pelaajat</h2>
        <form class="tip-form" @submit.prevent="submitPlayer">
          <label>
            Pelaajan nimi
            <input v-model.trim="playerNameDraft" required maxlength="32" />
          </label>
          <button type="submit" class="primary-button" :disabled="isHostBusy || !accessToken">
            Lisää pelaajakoodi
          </button>
          <p v-if="playerInviteError" class="login-panel__error">{{ playerInviteError }}</p>
        </form>

        <div v-if="latestPlayerInvite" class="host-code-box">
          <small>Uusin pelaajakoodi</small>
          <strong>{{ latestPlayerInvite.label }}</strong>
          <code>{{ latestPlayerInvite.code }}</code>
        </div>

        <div v-if="players.length" class="host-list">
          <article v-for="player in players" :key="player.id" class="host-list-item player-editor">
            <small>Pelaaja</small>
            <label>
              Nimi
              <input
                :value="playerDraftName(player)"
                maxlength="32"
                required
                @input="updatePlayerDraft(player, { name: inputValue($event) })"
              />
            </label>
            <label>
              Joukkue
              <select
                :value="playerDraftTeamId(player) ?? ''"
                :disabled="isHostBusy"
                @change="updatePlayerDraft(player, { teamId: selectedNullableTeamId($event) })"
              >
                <option value="">Ei joukkuetta</option>
                <option v-for="team in teams" :key="team.id" :value="team.id">
                  {{ team.name }}
                </option>
              </select>
            </label>
            <div v-if="playerDraftInviteCode(player)" class="player-code-line">
              <span>Pelaajakoodi</span>
              <code>{{ playerDraftInviteCode(player) }}</code>
            </div>
            <div class="quick-actions">
              <button type="button" class="pill-button" :disabled="isHostBusy" @click="savePlayer(player)">
                Tallenna
              </button>
              <button type="button" class="pill-button" :disabled="isHostBusy || !accessToken" @click="regeneratePlayerInvite(player)">
                Uusi koodi
              </button>
              <button type="button" class="pill-button pill-button--danger" :disabled="isHostBusy" @click="removePlayer(player.id)">
                Poista
              </button>
            </div>
          </article>
        </div>
        <p v-else class="empty-note">Ei pelaajia.</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, reactive, ref, watch } from 'vue'
import type { DailyTask, DailyTip, FoundMouse, MouseId, MouseTip, Player, ScoreCategory, ScoreEvent, Team, TeamId, UserMessage } from '../types'
import { createPlayerInvite, type PlayerInvite } from '../services/accessGate'
import { formatClock, formatShortDateTime as formatDate } from '../utils/dateFormat'
import mouseBlack from '../assets/mouse-black.svg'
import mouseBlackFound from '../assets/mouse-black-found.svg'
import mousePink from '../assets/mouse-pink.svg'
import mousePinkFound from '../assets/mouse-pink-found.svg'
import mouseWhite from '../assets/mouse-white.svg'
import mouseWhiteFound from '../assets/mouse-white-found.svg'
import SubmissionForm from './SubmissionForm.vue'

type HostDomain = 'paivatehtava' | 'hiiret' | 'pisteet' | 'viestit' | 'joukkueet' | 'pelaajat'
type HostAction = 'luo' | 'hallinta' | 'tila' | 'vinkit' | 'lisaa' | 'muokkaa' | 'laheta'

type ScoreDraft = Partial<Pick<ScoreEvent, 'teamId' | 'category' | 'dailyTaskId' | 'title' | 'points' | 'description'>>
type TeamDraft = Partial<Pick<Team, 'name' | 'accent'>>
type PlayerDraft = Partial<Pick<Player, 'name' | 'teamId' | 'inviteCode'>>

const props = defineProps<{
  teams: Team[]
  players: Player[]
  accessToken?: string
  dailyTask: DailyTask
  dailyTasks: DailyTask[]
  activeDailyTaskId: string
  mouseTips: MouseTip[]
  dailyTips: DailyTip[]
  userMessages: UserMessage[]
  foundMice: FoundMouse[]
  scoreEvents: ScoreEvent[]
}>()

const emit = defineEmits<{
  addScore: [event: ScoreEvent]
  updateScore: [event: ScoreEvent]
  removeScore: [eventId: string]
  addTeam: [team: Team]
  updateTeam: [team: Team]
  removeTeam: [teamId: TeamId]
  addPlayer: [player: Player]
  updatePlayer: [player: Player]
  removePlayer: [playerId: string]
  addMouseTip: [tip: MouseTip]
  updateMouseTip: [tip: MouseTip]
  removeMouseTip: [tipId: string]
  addDailyTip: [tip: DailyTip]
  updateDailyTip: [tip: DailyTip]
  removeDailyTip: [tipId: string]
  addUserMessage: [message: UserMessage]
  updateUserMessage: [message: UserMessage]
  removeUserMessage: [messageId: string]
  createDailyTask: [task: DailyTask]
  updateDailyTask: [task: DailyTask]
  removeDailyTask: [taskId: string]
  setActiveDailyTask: [taskId: string]
  setMouseFound: [mouseId: MouseId, teamId: TeamId]
  setMouseHidden: [mouseId: MouseId]
  startTaskNow: []
  endTaskNow: []
}>()

const mouseId = ref<MouseId>('white')
const tipText = ref('')
const dailyTipText = ref('')
const userMessageText = ref('')
const userMessageRecipientId = ref(props.players[0]?.id ?? '')
const selectedMouseTeam = ref<TeamId | null>(null)
const teamNameDraft = ref('')
const teamAccentDraft = ref('#f7e87a')
const playerNameDraft = ref('')
const latestPlayerInvite = ref<PlayerInvite | null>(null)
const playerInviteError = ref('')
const activeDomain = ref<HostDomain>('paivatehtava')
const activeAction = ref<HostAction>('luo')
const dailyTaskDraft = reactive({
  title: props.dailyTask.title,
  location: props.dailyTask.location,
  preparationText: props.dailyTask.preparationText,
  instructions: props.dailyTask.instructions
})
const dailyTaskStartDraft = ref(toDateTimeLocalValue(props.dailyTask.startsAt))
const dailyTaskEndDraft = ref(toDateTimeLocalValue(props.dailyTask.endsAt))
const dailyDrafts = reactive<Record<string, string>>({})
const mouseDrafts = reactive<Record<string, string>>({})
const userMessageDrafts = reactive<Record<string, string>>({})
const mouseTipSelections = reactive<Record<string, MouseId>>({})
const scoreDrafts = reactive<Record<string, ScoreDraft>>({})
const teamDrafts = reactive<Record<string, TeamDraft>>({})
const playerDrafts = reactive<Record<string, PlayerDraft>>({})
const activeHostActivity = ref('')
let activityTimeout: number | undefined

const domains: { id: HostDomain, label: string }[] = [
  { id: 'paivatehtava', label: 'Päivätehtävä' },
  { id: 'hiiret', label: 'Hiiret' },
  { id: 'pisteet', label: 'Pisteet' },
  { id: 'viestit', label: 'Viestit' },
  { id: 'joukkueet', label: 'Joukkueet' },
  { id: 'pelaajat', label: 'Pelaajat' }
]

const actionsByDomain: Record<HostDomain, { id: HostAction, label: string }[]> = {
  paivatehtava: [
    { id: 'luo', label: 'Lisää' },
    { id: 'hallinta', label: 'Muokkaa' }
  ],
  hiiret: [
    { id: 'tila', label: 'Muokkaa' },
    { id: 'vinkit', label: 'Lisää vinkki' }
  ],
  pisteet: [
    { id: 'lisaa', label: 'Lisää' },
    { id: 'muokkaa', label: 'Muokkaa' }
  ],
  viestit: [
    { id: 'laheta', label: 'Lähetä' }
  ],
  joukkueet: [
    { id: 'hallinta', label: 'Lisää / muokkaa' }
  ],
  pelaajat: [
    { id: 'hallinta', label: 'Lisää / muokkaa' }
  ]
}

const teamColorOptions = ['#f7e87a', '#8bd3f7', '#7ecf9a', '#f59aa5', '#f7c0c8', '#fff8dc']
const scoreCategoryOptions: { value: ScoreCategory, label: string, defaultTitle: string, defaultPoints: number }[] = [
  { value: 'paivatehtava', label: 'Päivätehtävä', defaultTitle: 'Päivätehtävä', defaultPoints: 10 },
  { value: 'hiiritehtava', label: 'Hiiritehtävä', defaultTitle: 'Hiiritehtävä', defaultPoints: 16 },
  { value: 'bonus', label: 'Bonus', defaultTitle: 'Bonus', defaultPoints: 5 }
]

const pointOptions = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

const mice: { id: MouseId, label: string, image: string, foundImage: string }[] = [
  { id: 'white', label: 'Valkoinen hiiri', image: mouseWhite, foundImage: mouseWhiteFound },
  { id: 'pink', label: 'Pinkki hiiri', image: mousePink, foundImage: mousePinkFound },
  { id: 'black', label: 'Musta hiiri', image: mouseBlack, foundImage: mouseBlackFound }
]

const sortedMouseTips = computed(() => {
  return [...props.mouseTips].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
})

const sortedDailyTips = computed(() => {
  return props.dailyTips
    .filter(tip => tip.dailyTaskId === props.dailyTask.id)
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
})

const sortedUserMessages = computed(() => {
  return [...props.userMessages].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
})

const sortedScoreEvents = computed(() => {
  return [...props.scoreEvents].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
})

const currentActions = computed(() => actionsByDomain[activeDomain.value])
const isHostBusy = computed(() => activeHostActivity.value !== '')

onBeforeUnmount(() => {
  if (activityTimeout) {
    window.clearTimeout(activityTimeout)
  }
})

watch(() => props.players.map(player => player.id).join('|'), () => {
  if (!props.players.some(player => player.id === userMessageRecipientId.value)) {
    userMessageRecipientId.value = props.players[0]?.id ?? ''
  }
})

watch(
  () => [
    props.dailyTask.id,
    props.dailyTask.title,
    props.dailyTask.location,
    props.dailyTask.preparationText,
    props.dailyTask.instructions,
    props.dailyTask.startsAt,
    props.dailyTask.endsAt
  ],
  () => {
    syncDailyTaskDraft(props.dailyTask)
  }
)

function selectDomain (domain: HostDomain): void {
  activeDomain.value = domain
  activeAction.value = actionsByDomain[domain][0].id
}

function submitTip (): void {
  runHostActivity('Julkaistaan hiirivinkkiä', () => {
    emit('addMouseTip', {
      id: window.crypto?.randomUUID?.() ?? `tip-${Date.now()}`,
      mouseId: mouseId.value,
      text: tipText.value,
      createdAt: new Date().toISOString()
    })

    tipText.value = ''
  })
}

function submitDailyTip (): void {
  runHostActivity('Julkaistaan päivävinkkiä', () => {
    emit('addDailyTip', {
      id: window.crypto?.randomUUID?.() ?? `daily-tip-${Date.now()}`,
      dailyTaskId: props.dailyTask.id,
      text: dailyTipText.value,
      createdAt: new Date().toISOString()
    })

    dailyTipText.value = ''
  })
}

function submitUserMessage (): void {
  if (!userMessageRecipientId.value) {
    return
  }

  runHostActivity('Lähetetään viestiä', () => {
    emit('addUserMessage', {
      id: window.crypto?.randomUUID?.() ?? `message-${Date.now()}`,
      recipientPlayerId: userMessageRecipientId.value,
      text: userMessageText.value,
      createdAt: new Date().toISOString()
    })

    userMessageText.value = ''
  })
}

function createDailyTaskSetup (): void {
  runHostActivity('Tallennetaan päivätehtävää', () => {
    const task = dailyTaskFromDraft()
    emit('createDailyTask', {
      ...task,
      id: window.crypto?.randomUUID?.() ?? `daily-task-${Date.now()}`
    })
  })
}

function submitDailyTaskSetup (): void {
  runHostActivity('Tallennetaan muutoksia', () => {
    emit('updateDailyTask', dailyTaskFromDraft())
  })
}

function canRemoveDailyTask (task: DailyTask): boolean {
  return props.dailyTasks.length > 1 && props.dailyTasks.some(item => item.id === task.id)
}

function dailyTaskFromDraft (): DailyTask {
  return {
    ...props.dailyTask,
    title: dailyTaskDraft.title,
    location: dailyTaskDraft.location,
    preparationText: dailyTaskDraft.preparationText,
    instructions: dailyTaskDraft.instructions,
    startsAt: fromDateTimeLocalValue(dailyTaskStartDraft.value),
    endsAt: fromDateTimeLocalValue(dailyTaskEndDraft.value)
  }
}

function selectDailyTask (task: DailyTask): void {
  runHostActivity('Vaihdetaan päivätehtävää', () => {
    emit('setActiveDailyTask', task.id)
    syncDailyTaskDraft(task)
  })
}

function syncDailyTaskDraft (task: DailyTask): void {
  dailyTaskDraft.title = task.title
  dailyTaskDraft.location = task.location
  dailyTaskDraft.preparationText = task.preparationText
  dailyTaskDraft.instructions = task.instructions
  dailyTaskStartDraft.value = toDateTimeLocalValue(task.startsAt)
  dailyTaskEndDraft.value = toDateTimeLocalValue(task.endsAt)
}

function saveDailyTip (tip: DailyTip): void {
  runHostActivity('Tallennetaan päivävinkkiä', () => {
    emit('updateDailyTip', {
      ...tip,
      text: dailyDrafts[tip.id] ?? tip.text
    })
  })
}

function removeDailyTip (tipId: string): void {
  if (!confirmAction('Poistetaanko tämä päivävinkki? Tätä ei voi kumota.')) {
    return
  }

  runHostActivity('Poistetaan päivävinkkiä', () => {
    emit('removeDailyTip', tipId)
    delete dailyDrafts[tipId]
  })
}

function saveUserMessage (message: UserMessage): void {
  runHostActivity('Tallennetaan viestiä', () => {
    emit('updateUserMessage', {
      ...message,
      text: userMessageDrafts[message.id] ?? message.text
    })

    delete userMessageDrafts[message.id]
  })
}

function removeUserMessage (messageId: string): void {
  if (!confirmAction('Poistetaanko tämä viesti? Pelaaja ei näe sitä enää.')) {
    return
  }

  runHostActivity('Poistetaan viestiä', () => {
    emit('removeUserMessage', messageId)
    delete userMessageDrafts[messageId]
  })
}

function removeDailyTask (taskId: string): void {
  if (!confirmAction(`Poistetaanko tehtävä "${props.dailyTask.title}"? Tehtävän pisteet ja päivävinkit poistuvat samalla.`)) {
    return
  }

  runHostActivity('Poistetaan päivätehtävää', () => {
    emit('removeDailyTask', taskId)
  })
}

function saveMouseTip (tip: MouseTip): void {
  runHostActivity('Tallennetaan hiirivinkkiä', () => {
    emit('updateMouseTip', {
      ...tip,
      mouseId: selectedTipMouse(tip),
      text: mouseDrafts[tip.id] ?? tip.text
    })
  })
}

function removeMouseTip (tipId: string): void {
  if (!confirmAction('Poistetaanko tämä hiirivinkki? Tätä ei voi kumota.')) {
    return
  }

  runHostActivity('Poistetaan hiirivinkkiä', () => {
    emit('removeMouseTip', tipId)
    delete mouseDrafts[tipId]
    delete mouseTipSelections[tipId]
  })
}

function updateScoreDraft (event: ScoreEvent, draft: ScoreDraft): void {
  scoreDrafts[event.id] = {
    ...scoreDrafts[event.id],
    ...draft
  }
}

function updateScoreCategory (event: ScoreEvent, category: ScoreCategory): void {
  const option = scoreCategoryOptions.find(item => item.value === category)
  const dailyTaskId = category === 'paivatehtava' ? scoreDailyTaskId(event) || props.dailyTasks[0]?.id : undefined
  const selectedTask = props.dailyTasks.find(task => task.id === dailyTaskId)

  updateScoreDraft(event, {
    category,
    dailyTaskId,
    title: category === 'paivatehtava' ? selectedTask?.title ?? option?.defaultTitle : option?.defaultTitle,
    points: option?.defaultPoints
  })
}

function updateScoreTask (event: ScoreEvent, task: DailyTask): void {
  updateScoreDraft(event, {
    dailyTaskId: task.id,
    title: task.title
  })
}

function saveScore (event: ScoreEvent): void {
  runHostActivity('Tallennetaan pisteitä', () => {
    const category = scoreCategory(event)

    emit('updateScore', {
      ...event,
      teamId: scoreTeam(event),
      category,
      dailyTaskId: category === 'paivatehtava' ? scoreDailyTaskId(event) : undefined,
      title: scoreTitle(event),
      points: scorePoints(event),
      description: scoreDescription(event)
    })

    delete scoreDrafts[event.id]
  })
}

function submitScore (event: ScoreEvent): void {
  runHostActivity('Tallennetaan pisteitä', () => {
    emit('addScore', event)
  })
}

function removeScore (eventId: string): void {
  if (!confirmAction('Poistetaanko tämä pistekirjaus? Pisteet poistuvat taulukosta heti.')) {
    return
  }

  runHostActivity('Poistetaan pistekirjausta', () => {
    emit('removeScore', eventId)
    delete scoreDrafts[eventId]
  })
}

function submitTeam (): void {
  runHostActivity('Lisätään joukkuetta', () => {
    emit('addTeam', {
      id: window.crypto?.randomUUID?.() ?? `team-${Date.now()}`,
      name: teamNameDraft.value,
      accent: teamAccentDraft.value
    })

    teamNameDraft.value = ''
    teamAccentDraft.value = teamColorOptions[props.teams.length % teamColorOptions.length]
  })
}

function submitPlayer (): void {
  const nextPlayerName = playerNameDraft.value.trim()
  playerInviteError.value = ''

  if (!nextPlayerName) {
    playerInviteError.value = 'Pelaajan nimi puuttuu.'
    return
  }

  if (props.players.some(player => normalizePlayerName(player.name) === normalizePlayerName(nextPlayerName))) {
    playerInviteError.value = 'Pelaaja on jo listalla.'
    return
  }

  runHostActivity('Luodaan pelaajakoodia', async () => {
    if (!props.accessToken) {
      playerInviteError.value = 'Järjestäjän kirjautuminen puuttuu.'
      return
    }

    const result = await createPlayerInvite(nextPlayerName, props.accessToken)

    if (!result.invite) {
      playerInviteError.value = result.error ?? 'Pelaajakoodia ei voitu luoda.'
      return
    }

    latestPlayerInvite.value = result.invite
    emit('addPlayer', {
      id: result.invite.playerId,
      name: result.invite.label,
      teamId: null,
      inviteCode: result.invite.code
    })
    playerNameDraft.value = ''
  })
}

function updateTeamDraft (team: Team, draft: TeamDraft): void {
  teamDrafts[team.id] = {
    ...teamDrafts[team.id],
    ...draft
  }
}

function updatePlayerDraft (player: Player, draft: PlayerDraft): void {
  playerDrafts[player.id] = {
    ...playerDrafts[player.id],
    ...draft
  }
}

function saveTeam (team: Team): void {
  runHostActivity('Tallennetaan joukkuetta', () => {
    emit('updateTeam', {
      ...team,
      name: teamDraftName(team),
      accent: teamDraftAccent(team)
    })

    delete teamDrafts[team.id]
  })
}

function savePlayer (player: Player): void {
  const nextName = playerDraftName(player).trim()

  playerInviteError.value = ''

  if (!nextName) {
    playerInviteError.value = 'Pelaajan nimi puuttuu.'
    return
  }

  if (hasDuplicatePlayerName(player, nextName)) {
    playerInviteError.value = 'Pelaaja on jo listalla.'
    return
  }

  runHostActivity('Tallennetaan pelaajaa', () => {
    emit('updatePlayer', {
      ...player,
      name: nextName,
      teamId: playerDraftTeamId(player),
      inviteCode: playerDraftInviteCode(player)
    })

    delete playerDrafts[player.id]
  })
}

function regeneratePlayerInvite (player: Player): void {
  const nextName = playerDraftName(player).trim()

  playerInviteError.value = ''

  if (!nextName) {
    playerInviteError.value = 'Pelaajan nimi puuttuu.'
    return
  }

  if (hasDuplicatePlayerName(player, nextName)) {
    playerInviteError.value = 'Pelaaja on jo listalla.'
    return
  }

  runHostActivity('Luodaan pelaajakoodia', async () => {
    if (!props.accessToken) {
      playerInviteError.value = 'Järjestäjän kirjautuminen puuttuu.'
      return
    }

    const result = await createPlayerInvite(nextName, props.accessToken, player.id)

    if (!result.invite) {
      playerInviteError.value = result.error ?? 'Pelaajakoodia ei voitu luoda.'
      return
    }

    latestPlayerInvite.value = result.invite
    emit('updatePlayer', {
      ...player,
      name: result.invite.label,
      teamId: playerDraftTeamId(player),
      inviteCode: result.invite.code
    })

    delete playerDrafts[player.id]
  })
}

function removePlayer (playerId: string): void {
  const player = props.players.find(item => item.id === playerId)

  if (!confirmAction(`Poistetaanko pelaaja "${player?.name ?? 'Pelaaja'}"? Myös pelaajan viestit poistuvat.`)) {
    return
  }

  runHostActivity('Poistetaan pelaajaa', () => {
    emit('removePlayer', playerId)
    delete playerDrafts[playerId]
  })
}

function removeTeam (teamId: TeamId): void {
  if (!confirmAction(`Poistetaanko joukkue "${teamName(teamId)}"? Joukkueen pisteet, hiirilöydöt ja pelaajien joukkuevalinnat poistuvat samalla.`)) {
    return
  }

  runHostActivity('Poistetaan joukkuetta', () => {
    emit('removeTeam', teamId)
    delete teamDrafts[teamId]
  })
}

function selectedNullableTeamId (event: Event): TeamId | null {
  const value = inputValue(event)
  return value ? value : null
}

function playerDraftName (player: Player): string {
  return hasPlayerDraftField(player, 'name') ? playerDrafts[player.id].name ?? '' : player.name
}

function playerDraftTeamId (player: Player): TeamId | null {
  return hasPlayerDraftField(player, 'teamId') ? playerDrafts[player.id].teamId ?? null : player.teamId
}

function playerDraftInviteCode (player: Player): string | undefined {
  return hasPlayerDraftField(player, 'inviteCode') ? playerDrafts[player.id].inviteCode : player.inviteCode
}

function hasPlayerDraftField (player: Player, field: keyof PlayerDraft): boolean {
  return Object.prototype.hasOwnProperty.call(playerDrafts[player.id] ?? {}, field)
}

function hasDuplicatePlayerName (player: Player, name: string): boolean {
  return props.players.some(item => item.id !== player.id && normalizePlayerName(item.name) === normalizePlayerName(name))
}

function normalizePlayerName (name: string): string {
  return name.trim().toLocaleLowerCase('fi-FI')
}

function teamDraftName (team: Team): string {
  return teamDrafts[team.id]?.name ?? team.name
}

function teamDraftAccent (team: Team): string {
  return teamDrafts[team.id]?.accent ?? team.accent
}

function scoreTeam (event: ScoreEvent): TeamId {
  return scoreDrafts[event.id]?.teamId ?? event.teamId
}

function scoreCategory (event: ScoreEvent): ScoreCategory {
  return scoreDrafts[event.id]?.category ?? event.category
}

function scoreDailyTaskId (event: ScoreEvent): string {
  return scoreDrafts[event.id]?.dailyTaskId ?? event.dailyTaskId ?? props.dailyTasks[0]?.id ?? ''
}

function scoreTitle (event: ScoreEvent): string {
  return scoreDrafts[event.id]?.title ?? event.title
}

function scorePoints (event: ScoreEvent): number {
  return scoreDrafts[event.id]?.points ?? event.points
}

function scoreDescription (event: ScoreEvent): string {
  return scoreDrafts[event.id]?.description ?? event.description
}

function scoreHeader (event: ScoreEvent): string {
  const category = scoreCategory(event)

  if (category !== 'paivatehtava') {
    return scoreCategoryLabel(category)
  }

  const selectedTask = props.dailyTasks.find(task => task.id === scoreDailyTaskId(event))
  return selectedTask?.title ?? scoreTitle(event) ?? scoreCategoryLabel(category)
}

function scoreCategoryLabel (category: ScoreCategory): string {
  return scoreCategoryOptions.find(option => option.value === category)?.label ?? ''
}

function selectedTipMouse (tip: MouseTip): MouseId {
  return mouseTipSelections[tip.id] ?? tip.mouseId
}

function foundMouse (mouseId: MouseId): FoundMouse | undefined {
  return props.foundMice.find(found => found.mouseId === mouseId)
}

function toggleMouse (mouseId: MouseId): void {
  runHostActivity('Tallennetaan hiiren tilaa', () => {
    if (foundMouse(mouseId) || selectedMouseTeam.value === null) {
      emit('setMouseHidden', mouseId)
    } else {
      emit('setMouseFound', mouseId, selectedMouseTeam.value)
    }
  })
}

function startTaskNow (): void {
  if (!confirmAction(`Aloitetaanko tehtävä "${props.dailyTask.title}" nyt? Ajastettu aloitus muuttuu.`)) {
    return
  }

  runHostActivity('Aloitetaan tehtävää', () => {
    emit('startTaskNow')
  })
}

function endTaskNow (): void {
  if (!confirmAction(`Lopetetaanko tehtävä "${props.dailyTask.title}" nyt? Tämä siirtää tehtävän päättyneeksi.`)) {
    return
  }

  runHostActivity('Päätetään tehtävää', () => {
    emit('endTaskNow')
  })
}

function confirmAction (message: string): boolean {
  return window.confirm(message)
}

function runHostActivity (label: string, activity: () => void | Promise<void>): void {
  if (isHostBusy.value) {
    return
  }

  if (activityTimeout) {
    window.clearTimeout(activityTimeout)
  }

  activeHostActivity.value = label
  const startedAt = Date.now()

  void Promise.resolve()
    .then(activity)
    .finally(() => {
      const remainingMs = Math.max(0, 520 - (Date.now() - startedAt))

      activityTimeout = window.setTimeout(() => {
        activeHostActivity.value = ''
      }, remainingMs)
    })
}

function teamName (teamId: TeamId | undefined): string {
  return props.teams.find(team => team.id === teamId)?.name ?? ''
}

function playerName (playerId: string): string {
  return props.players.find(player => player.id === playerId)?.name ?? 'Poistettu pelaaja'
}

function mouseLabel (mouseId: MouseId): string {
  return mice.find(mouse => mouse.id === mouseId)?.label ?? ''
}

function inputValue (event: Event): string {
  return (event.target as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement).value
}

function toDateTimeLocalValue (value: string): string {
  const date = new Date(value)
  const offsetMs = date.getTimezoneOffset() * 60 * 1000
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16)
}

function fromDateTimeLocalValue (value: string): string {
  return new Date(value).toISOString()
}
</script>
